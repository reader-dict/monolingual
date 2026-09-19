from __future__ import annotations

from typing import ClassVar

from wikidict.converters.dictfile import ConverterFromDictFile


class StarDictFormat(ConverterFromDictFile):
    """Save the data into a StarDict file."""

    target_format = "stardict"
    target_suffix = "ifo"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"
    glossary_options: ClassVar[dict[str, bool | str]] = {"dictzip": True, "sametypesequence": "h"}

    def _convert(self) -> None:
        super()._convert()

        # Append missing lang details to the .ifo
        ifo = self.output_dir / self.target_format / "dict-data.ifo"
        content = ifo.read_text()
        if "lang=" in content:
            return
        content += f"lang={self.effective_lang_src()}-{self.effective_lang_dst()}\n"
        ifo.write_text(content)
