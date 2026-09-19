from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from wikidict import constants
from wikidict.converters.dictfile import ConverterFromDictFile


class MobiFormat(ConverterFromDictFile):
    """Save the data into a MobiPocket file."""

    target_format = "mobi"
    target_suffix = "mobi"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"
    zip_glob_files = ""  # Will be set in `_compress()`
    glossary_options: ClassVar[dict[str, bool | str]] = {
        "cover_path": str(constants.COVER_FILE),
        "keep": True,
        "kindlegen_path": str(constants.MOBIPOCKET_TOOL),
    }

    def _compress(self) -> Path:
        # Move the relevant file at the top-level data folder, and rename it for more accuracy
        src = self.output_dir_tmp / f"dict-data.{self.target_suffix}" / "OEBPS" / f"content.{self.target_suffix}"
        file = src.rename(self.dictionary_file(self.final_file.removesuffix(".zip")))
        self.zip_glob_files = f"../{file.name}"
        return super()._compress()
