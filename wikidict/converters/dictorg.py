"""
Source: https://github.com/jgoerzen/dictdlib
"""

import shutil
import string
import zipfile
from typing import Any

from jinja2 import Template

from wikidict.converters import BaseFormat, Summary, dictzip
from wikidict.converters.stardict import TEMPLATE

B64_LIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
VALID_DICT_CHARS = set(string.ascii_letters + string.digits + " \t")
URL_HEADWORD = "00-database-url"
SHORT_HEADWORD = "00-database-short"
INFO_HEADWORD = "00-database-info"


def b64_encode(val: int) -> str:
    start_found = False
    retval = ""
    for i in range(5, -1, -1):
        this_part = (val >> (6 * i)) & ((2**6) - 1)
        if not start_found and not this_part:
            continue
        start_found = True
        retval += B64_LIST[this_part]
    return retval if len(retval) else B64_LIST[0]


def sort_df_key(string: str) -> tuple[str, str]:
    key = "".join(char for char in string if char in VALID_DICT_CHARS).upper()
    return (key, string.upper())


class DictOrgFormat(Summary, BaseFormat):
    """Save the data into a DICT.org file (dictd)."""

    target_format = "dictorg"
    final_file = "dictorg-{lang_src}-{lang_dst}{etym_suffix}.zip"
    template = TEMPLATE

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.tmp_dir = self.output_dir / self.target_format
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

        stem = self.title().lower().replace(" ", "-")
        self.dict_file = self.tmp_dir / f"{stem}.dict"
        self.dict_file_h = self.dict_file.open(mode="wb")

        self.index_entries: list[tuple[str, int, int]] = []

    def _add_meta_entry(self, headword: str, content: str) -> None:
        offset = self.dict_file_h.tell()
        size = self.dict_file_h.write(f"{headword}\n{content}\n".encode())
        self.index_entries.append((headword, offset, size))

    def set_url(self, url: str) -> None:
        self._add_meta_entry(URL_HEADWORD, f"     {url}")

    def set_short_name(self, shortname: str) -> None:
        self._add_meta_entry(SHORT_HEADWORD, f"     {shortname}")

    def set_long_info(self, longinfo: str) -> None:
        self._add_meta_entry(INFO_HEADWORD, longinfo)

    def write_metadata(self) -> None:
        description = "\n".join(
            [
                "Clean, optimized dictionary generated from Wiktionary data.",
                f"Contains {self.words_count + self.variants_count:,} entries with{'' if self.include_etymology else 'out'} etymologies.\n",
                self.description,
            ]
        )
        self.set_short_name(self.title())
        self.set_url(self.website)
        self.set_long_info(description)

    def render_word(self, template: Template, **kwargs: Any) -> str:
        offset = self.dict_file_h.tell()
        size = self.dict_file_h.write(super().render_word(template, **kwargs).strip().encode("utf-8") + b"\n")
        self.index_entries.append((kwargs["word"], offset, size))
        self.index_entries.extend((variant, offset, size) for variant in kwargs["variants"])
        return ""

    def process(self) -> None:
        words = self.words
        for word in sorted(words):
            # Exhaust the generator
            for _ in self.handle_word(word, words):
                pass

        self.write_metadata()

        index_file = self.dict_file.with_suffix(".index")
        self.dict_file_h.close()
        self.dict_file = dictzip(self.dict_file)

        index_lines = [
            f"{headword}\t{b64_encode(offset)}\t{b64_encode(size)}" for headword, offset, size in self.index_entries
        ]
        index_lines.sort(key=sort_df_key)
        with index_file.open(mode="w", encoding="utf-8") as fh:
            for line in index_lines:
                fh.write(f"{line}\n")

        file = self.dictionary_file(self.final_file)
        with zipfile.ZipFile(file, mode="w", compression=zipfile.ZIP_DEFLATED) as fh:
            fh.write(self.dict_file, arcname=self.dict_file.name)
            fh.write(index_file, arcname=index_file.name)
            assert fh.testzip() is None, fh.testzip()

        self.summary(file)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
