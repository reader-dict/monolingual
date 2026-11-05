from __future__ import annotations

import html
import shutil
import struct
import zipfile
from itertools import groupby
from logging import getLogger
from operator import itemgetter
from typing import Any

from jinja2 import Template

from wikidict import constants
from wikidict.converters import BaseFormat, dictzip

log = getLogger(__name__)

TEMPLATE = Template(
    """\
{% if pronunciation %}
{{ pronunciation }}
{% endif %}
{%- for pos, pos_definitions in definitions -%}
    <p>
    {%- if pos.find("|") > -1 -%}
    <b>{{ pos.split("|", 1)[0] }}</b> <i>{{ pos.split("|", 1)[1] }}</i>
    {%- else -%}
    <b>{{ pos }}</b>
    {%- endif -%}
    </p><ol>
    {%- for definition in pos_definitions -%}
        {%- if definition is string -%}
            <li>{{ definition }}</li>
        {%- else -%}
            <ol style="list-style-type:lower-alpha">
                {%- for sub_def in definition -%}
                    {%- if sub_def is string -%}
                        <li>{{ sub_def }}</li>
                    {%- else -%}
                        <ol style="list-style-type:lower-roman">
                            {%- for sub_sub_def in sub_def -%}
                                <li>{{ sub_sub_def }}</li>
                            {%- endfor -%}
                        </ol>
                    {%- endif -%}
                {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
    </ol>
{%- endfor -%}
{%- if etymologies -%}
    {%- for etymology in etymologies -%}
        {%- if etymology is string -%}
            {%- if etymology.startswith("<table") -%}
                {{ etymology }}
            {%- else -%}
                <p>{{ etymology }}</p>
            {%- endif -%}
        {%- else -%}
            <ol>
                {%- for sub_etymology in etymology -%}
                    <li>{{ sub_etymology }}</li>
                {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
{%- endif -%}
"""
)


class StarDictFormat(BaseFormat):
    """Save the data into a StarDict file."""

    target_format = "stardict"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"
    template = TEMPLATE

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.tmp_dir = self.output_dir / self.target_format
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir()

        stem = self.title().lower().replace(" ", "-")
        self.dict_file = self.tmp_dir / f"{stem}.dict"
        self.idx_file = self.dict_file.with_suffix(".idx")
        self.ifo_file = self.dict_file.with_suffix(".ifo")
        self.syn_file = self.dict_file.with_suffix(".syn")
        self.dict_file_h = self.dict_file.open(mode="wb")
        self.idx_file_h = self.idx_file.open(mode="wb")

        self.variants_index: list[tuple[bytes, int]] = []

    def render_word(self, template: Template, **kwargs: Any) -> str:
        self.add_entry(kwargs["word"], super().render_word(template, **kwargs).strip(), kwargs["variants"])
        return ""

    def add_entry(self, word: str, article: str, variants: list[str]) -> None:
        offset = self.dict_file_h.tell()
        size = self.dict_file_h.write(article.encode("utf-8"))
        self.idx_file_h.write(word.encode("utf-8") + b"\0" + struct.pack(">I", offset) + struct.pack(">I", size))
        self.variants_index.extend((variant.encode("utf-8"), self.words_count - 1) for variant in variants)

    def write_index(self) -> tuple[int, int]:
        """Write the variants into the .syn file, the words are already in the .idx one.
        Return the number of words, and of variants."""
        if self.variants_count:
            with self.syn_file.open(mode="wb") as fh:
                variants = self.variants_index
                variants.sort(key=lambda s: (s[0].lower(), s[0]))  # stardict_strcmp()
                pack = struct.pack
                fh.writelines(variant + b"\0" + pack(">I", entry_index) for variant, entry_index in variants)
        return self.words_count, self.variants_count

    def process(self) -> None:
        words = self.words
        entries = sorted(words, key=lambda s: (s.encode("utf-8").lower(), s.encode("utf-8")))  # stardict_strcmp()
        for word in entries:
            # Exhaust the generator
            for _ in self.handle_word(word, words):
                pass

        words_count, variants_count = self.write_index()

        idx_file_size = self.idx_file_h.tell()
        self.idx_file_h.close()

        self.dict_file_h.close()
        self.dict_file = dictzip(self.dict_file)

        # https://github.com/huzheng001/stardict-3/blob/master/dict/doc/StarDictFileFormat
        description = "<br>".join(
            [
                "Clean, optimized dictionary generated from Wiktionary data.",
                f"Contains {words_count + variants_count:,} entries with{'' if self.include_etymology else 'out'} etymologies.<br>",
                self.description,
            ]
        )
        ifo_data = {
            "version": "3.0.0",
            "bookname": self.title(),
            "wordcount": str(words_count),
            "idxfilesize": str(idx_file_size),
            "author": constants.PROJECT,
            "website": self.website,
            "description": description,
            "date": f"{self.snapshot[:4]}-{self.snapshot[4:6]}-{self.snapshot[6:8]}",
            "sametypesequence": "h",
        }
        if variants_count:
            ifo_data["synwordcount"] = str(variants_count)
        with self.ifo_file.open(encoding="utf-8", mode="w") as fh:
            fh.write("StarDict's dict ifo file\n")
            fh.writelines(f"{key}={value}\n" for key, value in ifo_data.items())

        file = self.dictionary_file(self.final_file)
        with zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED) as fh:
            fh.write(self.dict_file, arcname=self.dict_file.name)
            fh.write(self.ifo_file, arcname=self.ifo_file.name)
            fh.write(self.idx_file, arcname=self.idx_file.name)
            if variants_count:
                fh.write(self.syn_file, arcname=self.syn_file.name)
            assert fh.testzip() is None, fh.testzip()

        self.summary(file)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)


class StarDictNoSynFormat(StarDictFormat):
    """Save the data into a StarDict file without a .syn file.

    Some readers ignore the .syn file (the dictionary app of Boox devices, for instance),
    so they find words, but none of their variants.
    Here, every variant is an entry of the .idx file, pointing to the article of its word.
    A variant of several words points to all their articles, one after the other.
    And each article starts with its word, to tell which word a variant belongs to.
    """

    target_format = "stardict-nosyn"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}-nosyn.zip"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        # The position and size of each article, written first into a temporary file
        self.articles: list[tuple[int, int]] = []
        # The .idx entries: (spelling, 0 for the word itself or 1 for a variant, article number)
        self.entries: list[tuple[bytes, int, int]] = []

    def add_entry(self, word: str, article: str, variants: list[str]) -> None:
        offset = self.dict_file_h.tell()
        size = self.dict_file_h.write(f"<b>{html.escape(word, quote=False)}</b> {article}".encode())
        number = len(self.articles)
        self.articles.append((offset, size))
        self.entries.append((word.encode("utf-8"), 0, number))
        self.entries.extend((variant.encode("utf-8"), 1, number) for variant in variants)

    def write_index(self) -> tuple[int, int]:
        """Write the .idx file, with one entry per spelling, and the .dict file, with the articles each entry shows.
        Return the number of entries, and of variants (none)."""
        # Same spellings next to each other, the word first, then the words it is a variant of
        self.entries.sort(key=lambda s: (s[0].lower(), s[0], s[1], s[2]))  # stardict_strcmp()

        self.dict_file_h.close()
        articles_file = self.dict_file.with_suffix(".articles")
        self.dict_file.replace(articles_file)
        self.dict_file_h = self.dict_file.open(mode="wb")

        # Each group of articles is written once, even when several spellings show it
        blocks: dict[tuple[int, ...], tuple[int, int]] = {}
        count = 0
        pack = struct.pack
        with articles_file.open(mode="rb") as fh:
            for spelling, group in groupby(self.entries, key=itemgetter(0)):
                numbers = tuple(dict.fromkeys(number for _, _, number in group))
                if not (block := blocks.get(numbers)):
                    parts = []
                    for number in numbers:
                        offset, size = self.articles[number]
                        fh.seek(offset)
                        parts.append(fh.read(size))
                    block = blocks[numbers] = self.dict_file_h.tell(), self.dict_file_h.write(b"<hr>".join(parts))
                self.idx_file_h.write(spelling + b"\0" + pack(">II", *block))
                count += 1
        articles_file.unlink()
        return count, 0
