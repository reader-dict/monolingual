from __future__ import annotations

import os
import shutil
import struct
import zipfile
from collections import deque
from logging import getLogger
from pathlib import Path
from typing import Any

from idzip import compressor
from jinja2 import Template

from wikidict import constants
from wikidict.converters import BaseFormat, Summary

log = getLogger(__name__)


def dictzip(ifile: Path) -> Path:
    ofile = ifile.with_suffix(f"{ifile.suffix}.dz")
    with ifile.open(mode="rb") as in_file, ofile.open(mode="wb") as out_file:
        inputInfo = os.fstat(in_file.fileno())
        compressor.compress(
            in_file,
            inputInfo.st_size,
            out_file,
            ifile.name,
            int(inputInfo.st_mtime),
        )
    ifile.unlink()
    return ofile


WORD_TPL_STARDICT = Template(
    """\
@ {{ word }}
{%- if pronunciation %}
:{{ pronunciation }}
{%- endif %}
<html>
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


class StarDictFormat(Summary, BaseFormat):
    """Save the data into a StarDict file."""

    target_format = "stardict"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"
    template = WORD_TPL_STARDICT

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

        self.entry_index = 0
        self.variants_index: list[tuple[bytes, int]] = []

    def render_word(self, template: Template, **kwargs: Any) -> str:
        offset = self.dict_file_h.tell()
        size = self.dict_file_h.write(super().render_word(template, **kwargs).encode("utf-8"))
        self.idx_file_h.write(
            kwargs["word"].encode("utf-8") + b"\0" + struct.pack(">I", offset) + struct.pack(">I", size)
        )
        self.variants_index.extend((variant.encode("utf-8"), self.entry_index) for variant in kwargs["variants"])

        self.entry_index += 1
        return ""

    def process(self) -> None:
        words = self.words
        entries = sorted(words, key=lambda s: (s.encode("utf-8").lower(), s.encode("utf-8")))  # stardict_strcmp()
        for word in entries:
            deque(self.handle_word(word, words), maxlen=0)  # Exhaust the generator

        idx_file_size = self.idx_file_h.tell()
        self.dict_file_h.close()
        self.idx_file_h.close()

        assert self.entry_index == self.words_count
        assert len(self.variants_index) == self.variants_count

        self.dict_file = dictzip(self.dict_file)

        if self.variants_count:
            pack = struct.pack
            with self.syn_file.open(mode="wb") as fh:
                variants = sorted(self.variants_index, key=lambda s: (s[0].lower(), s[0]))  # stardict_strcmp()
                fh.writelines(variant + b"\0" + pack(">I", entry_index) for variant, entry_index in variants)

        # https://github.com/huzheng001/stardict-3/blob/master/dict/doc/StarDictFileFormat
        description = "<br>".join(
            [
                "Clean, optimized dictionary generated from Wiktionary data.",
                f"Contains {self.words_count + self.variants_count:,} entries with{'' if self.include_etymology else 'out'} etymologies.<br>",
                self.description,
            ]
        )
        ifo_data = {
            "version": "3.0.0",
            "bookname": self.title(),
            "wordcount": str(self.words_count),
            "idxfilesize": str(idx_file_size),
            "author": constants.PROJECT,
            "website": self.website,
            "description": description,
            "date": f"{self.snapshot[:4]}-{self.snapshot[4:6]}-{self.snapshot[6:8]}",
            "sametypesequence": "h",
        }
        if self.variants_count:
            ifo_data["synwordcount"] = str(self.variants_count)
        with self.ifo_file.open(encoding="utf-8", mode="w") as fh:
            fh.write("StarDict's dict ifo file\n")
            fh.writelines(f"{key}={value}\n" for key, value in ifo_data.items())

        file = self.dictionary_file(self.final_file)
        with zipfile.ZipFile(file, "w", zipfile.ZIP_DEFLATED) as fh:
            fh.write(self.dict_file, arcname=self.dict_file.name)
            fh.write(self.ifo_file, arcname=self.ifo_file.name)
            fh.write(self.idx_file, arcname=self.idx_file.name)
            if self.variants_count:
                fh.write(self.syn_file, arcname=self.syn_file.name)
            assert fh.testzip() is None, fh.testzip()

        self.summary(file)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
