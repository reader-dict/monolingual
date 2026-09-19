from __future__ import annotations

import bz2
import gc
import logging
import os
import shutil
from pathlib import Path
from typing import ClassVar
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Template
from pyglossary.glossary_v2 import ConvertArgs, Glossary

from wikidict.converters import BaseFormat, Summary

# DictFile-related dictionaries
# Source: https://pgaskin.net/dictutil/dictgen/#dictfile-format
# Source: https://github.com/hunspell/hunspell/blob/ecc6dbb52025bdf3a766429988e64190d912765f/man/hunspell.1#L93-L139 (for later, in case of issues with other sub-formats)
WORD_TPL_DICTFILE = Template(
    """\
@ {{ word }}
{%- if pronunciation %}
:{{ pronunciation }}
{%- endif %}
{%- for variant in variants %}
& {{ variant }}
{%- endfor %}
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
    <br/>
{%- endif %}


"""
)

log = logging.getLogger(__name__)


class CustomLogFilter(logging.Filter):
    """Filter out noisy PyGlossary messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not msg.startswith(("duplicate language", "Module 'lxml' not found"))


class DictFileFormat(Summary, BaseFormat):
    """Save the data into a *.df* DictFile."""

    output_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.df"
    template = WORD_TPL_DICTFILE

    def process(self) -> None:
        file = self.dictionary_file(self.output_file)
        words = self.words
        data = "".join(formatted_word for word in words for formatted_word in self.handle_word(word, words))
        file.write_text(data, encoding="utf-8")

        self.summary(file)


class ConverterFromDictFile(DictFileFormat):
    target_format = ""
    target_suffix = ""
    final_file = ""
    zip_glob_files = "dict-data.*"
    glossary_options: ClassVar[dict[str, bool | str]] = {}

    def _patch_gc(self) -> None:
        """Bypass performances issues when calling PyGlossary from Python."""

        def noop_gc_collect() -> None:
            pass

        gc.collect = noop_gc_collect  # type: ignore[assignment]

    def _cleanup(self) -> None:
        shutil.rmtree(self.output_dir_tmp, ignore_errors=True)

    @property
    def output_dir_tmp(self) -> Path:
        return self.output_dir / self.target_format

    @property
    def glos_input_fname(self) -> Path:
        return self.dictionary_file(DictFileFormat.output_file)

    @property
    def glos_output_fname(self) -> Path:
        return self.output_dir_tmp / f"dict-data.{self.target_suffix}"

    def _convert(self) -> None:
        """Convert the DictFile to the target format."""
        if pyglossary_logger := logging.getLogger("pyglossary"):
            pyglossary_logger.addFilter(CustomLogFilter())

        # We do not want to use temporary SQLite databases. Without them:
        #   - that's faster;
        #   - it prevents concurrent access issues from secondary formatters;
        #   - and it reduces I/O on the machine.
        os.environ["NO_SQLITE"] = "1"

        Glossary.init()
        glos = Glossary()
        glos.config = {
            "auto_sqlite": False,
            "cleanup": False,  # Prevent deleting temporary image files (~/.cache/pyglossary/DICT/FILE.gif)
        }

        if self.format == "StarDict":
            writer_cls = glos.plugins["Stardict"].writerClass

            # Do not append extra data to the book name
            def get_bookname(cls, partNumber: int | None = None) -> str:  # type: ignore[no-untyped-def]
                bookname = str(cls._glos.getInfo("name"))
                log.info("bookname: %s", bookname)
                return bookname

            writer_cls.getBookname = get_bookname

        glos.setInfo("description", self.description)
        glos.setInfo("title", self.title())
        glos.setInfo("website", self.website)
        glos.setInfo("date", f"{self.snapshot[:4]}-{self.snapshot[4:6]}-{self.snapshot[6:8]}")

        glos.sourceLangName = self.effective_lang_src()
        glos.targetLangName = self.effective_lang_dst()

        if self.format == "Mobi":
            # Alter the generated word title to fix this Kindling warning:
            # [warning R6.1] section 6.1 (p.22): Content is not well-formed XHTML. Kindle requires well-formed HTML documents for reliable conversion. Parse error: ill-formed document: expected `</br>`, but `</idx:orth>` was found (g000002.xhtml)
            wordTitleStr_original = glos.wordTitleStr

            def wordTitleStr(word: str, **kwargs: str) -> str:
                # Do not end with `<br>` but `<br/>`
                return str(wordTitleStr_original(word, **kwargs)).replace("<br>", "<br/>")

            glos.wordTitleStr = wordTitleStr

        self.output_dir_tmp.mkdir()
        glos.convert(
            ConvertArgs(
                inputFilename=str(self.glos_input_fname),
                outputFilename=str(self.glos_output_fname),
                writeOptions=self.glossary_options,
            )
        )

    def _compress(self) -> Path:
        final_file = self.dictionary_file(self.final_file)
        with ZipFile(final_file, mode="w", compression=ZIP_DEFLATED) as fh:
            for file in self.output_dir_tmp.glob(self.zip_glob_files):
                fh.write(file, arcname=file.name)

            for entry in (self.output_dir / self.target_format).glob("res/*"):
                fh.write(entry, arcname=f"res/{entry.name}")

            # Check the ZIP validity
            # testzip() returns the name of the first corrupt file, or None
            assert fh.testzip() is None, fh.testzip()

        return final_file

    def process(self) -> None:
        self._cleanup()
        self._patch_gc()
        self._convert()
        final_file = self._compress()
        BaseFormat.summary(self, final_file)
        self._cleanup()


class BZ2DictFileFormat(BaseFormat):
    def process(self) -> None:
        df_file = self.dictionary_file(DictFileFormat.output_file)
        bz2_file = df_file.with_suffix(".df.bz2")
        bz2_file.write_bytes(bz2.compress(df_file.read_bytes()))
        return self.summary(bz2_file)
