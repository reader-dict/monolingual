from __future__ import annotations

from typing import ClassVar

from wikidict.converters.dictfile import ConverterFromDictFile


class DictOrgFormat(ConverterFromDictFile):
    """Save the data into a DICT.org file."""

    target_format = "dict.org"
    target_suffix = "index"
    final_file = "dictorg-{lang_src}-{lang_dst}{etym_suffix}.zip"
    glossary_options: ClassVar[dict[str, bool | str]] = {"dictzip": True, "install": False}
