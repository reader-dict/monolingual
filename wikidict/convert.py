"""Convert rendered data to working dictionaries."""

from __future__ import annotations

import bz2
import gc
import gzip
import hashlib
import json
import logging
import os
import shutil
import threading
from collections import defaultdict
from contextlib import suppress
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Template
from marisa_trie import Trie
from pyglossary.glossary_v2 import ConvertArgs, Glossary

from . import constants, render, utils
from .stubs import Word

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any

    from .stubs import Definition, Definitions, Groups, Variants, Words

#
# Templates for devices/apps
#
# Note: we issue a line break (`<br/>`) at the end of etymologies to workaround a visual glitch when there are multiple results for a word:
#       the next word would'nt be properly visually separated from the previous word's etymology.

# Kobo-related dictionaries
# Note: We cannot remove the space before the slash in `<a name="{{ word }}" />` because
#       the Kobo lookup regexp for Japanese words is `(<a name="WORD" />.*</w>)`.
WORD_TPL_KOBO = Template(
    """\
<w><p><a name="{{ word }}" /><b>{{ current_word }}</b>{{ pronunciation }}{{ gender }}<br/><br/>
{%- for pos, pos_definitions in definitions -%}
    <b>{{ pos }}</b><ol>
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
            <p>{{ etymology }}</p>
        {%- else -%}
            <ol>
            {%- for sub_etymology in etymology -%}
                <li>{{ sub_etymology }}</li>
            {%- endfor -%}
            </ol>
        {%- endif -%}
    {%- endfor -%}
    <br/>
{%- endif -%}
</p>
{%- if variants -%}
    <var>
    {%- for variant in variants -%}
        <variant name="{{ variant }}"/>
    {%- endfor -%}
    </var>
{%- endif -%}
</w>
""",
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)

# DictFile-related dictionaries
# Source: https://pgaskin.net/dictutil/dictgen/#dictfile-format
# Source: https://github.com/hunspell/hunspell/blob/ecc6dbb52025bdf3a766429988e64190d912765f/man/hunspell.1#L93-L139 (for later, in case of issues with other sub-formats)
WORD_TPL_DICTFILE = Template(
    """\
@ {{ word }}
{%- if pronunciation or gender %}
:{{ pronunciation }}{{ gender }}
{%- endif %}
{%- for variant in variants %}
& {{ variant }}
{%- endfor %}
<html>
{%- for pos, pos_definitions in definitions -%}
    <p><b>{{ pos }}</b></p><ol>
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

# Threshold before issuing a warning to catch potentially problematic variants
MAX_VARIANTS = 255

log = logging.getLogger(__name__)


class CustomLogFilter(logging.Filter):
    """Filter out noisy PyGlossary messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return not msg.startswith(("duplicate language", "Module 'lxml' not found"))


class BaseFormat:
    """Base class for all dictionaries."""

    template = Template("")  # To be set by subclasses

    def __init__(
        self,
        locale: str,
        output_dir: Path,
        words: Words,
        variants: Variants,
        snapshot: str,
        *,
        include_etymology: bool = True,
    ) -> None:
        self._lang_src, self._lang_dst = utils.guess_locales(locale)
        self.output_dir = output_dir
        self.words = words
        self.variants = variants
        self.snapshot = snapshot
        self.include_etymology = include_etymology
        self.start = monotonic()
        self.words_count = 0
        self.variants_count = 0

        utils.setup_logging(self.effective_lang_dst(), self.effective_lang_src())
        log.info(
            "[%s] Starting the conversion with %s words, and %s variants ...",
            self.id(),
            f"{len(words):,}",
            f"{len(variants):,}",
        )

    @property
    def description(self) -> str:
        return f"© {constants.PROJECT} {datetime.now(tz=UTC).year}"

    def id(self) -> str:
        return f"{type(self).__name__} {self.effective_lang_src().upper()}-{self.effective_lang_dst().upper()} {'' if self.include_etymology else 'no'}etym"

    def title(self) -> str:
        return constants.TITLE.format(
            project=constants.PROJECT,
            langs=(
                self._lang_src.upper()
                if self._lang_src == self._lang_dst
                else f"{self.effective_lang_src()}-{self.effective_lang_dst()}".upper()
            ),
        )

    @property
    def website(self) -> str:
        return constants.WEBSITE

    def effective_lang_src(self) -> str:
        return self._lang_src

    def effective_lang_dst(self) -> str:
        return self._lang_dst

    def dictionary_file(self, output_file: str) -> Path:
        return self.output_dir / output_file.format(
            lang_src=self.effective_lang_src(),
            lang_dst=self.effective_lang_dst(),
            etym_suffix="" if self.include_etymology else constants.NO_ETYMOLOGY_SUFFIX,
        )

    def handle_word(self, word: str, words: Words) -> Generator[str]:
        """
        Special handling for Japanese on Kobo: variants are not supported as other locales, so we duplicate entries as normal words.
        """

        for_kobo = isinstance(self, KoboFormat)

        # Prevent storing variants definitions in DictFile & co
        if (chosen_word := words[word]).is_variant and not chosen_word.definitions and not for_kobo:
            return

        details = deepcopy(chosen_word)
        current_words = {word: details}
        lang_src = self.effective_lang_src()
        is_russian = lang_src == "ru"

        if for_kobo:
            is_japanese = lang_src == "ja"
            guess_prefix = partial(utils.guess_prefix, locale=lang_src)
            word_group_prefix = guess_prefix(word)

        if details.variants and for_kobo:
            # [***] Variants are more like typos, or misses, and so devices expect word & variants to start with same letters, at least.
            # An example in FR, where "suis" (verb flexion) is a variant of both "être" & "suivre": "suis" & "être" are quite differents.
            # As a workaround, we yield as many words as there are variants but under the word "suis": at the end, we will have 3 words:
            #   - "suis" with the content "suis" (itself)
            #   - "suis" with the content "être"
            #   - "suis" with the content "suivre"
            for variant in details.variants:
                if (is_japanese or guess_prefix(variant) != word_group_prefix) and (root := self.words.get(variant)):
                    current_words[variant] = root

        for current_word, current_details in sorted(current_words.items()):
            if not current_details.definitions:
                continue

            all_variants = self.variants
            if variants := deepcopy(all_variants.get(current_word, set())):
                # Add variants of empty* variant, only 1 redirection:
                #   [ES] gastada* -> gastado* -> gastar --> (gastada, gastado) -> gastar
                # Note: the process works backward: from gastar up to gastado up to gastada.
                for variant in [*variants]:
                    if (
                        (wv := words.get(variant))
                        and not wv.definitions
                        and (new_variants := all_variants.get(variant))
                    ):
                        variants.update(new_variants)

                # Filter out variants being identical to the word (it happens when altering `current_words`, cf [***])
                variants.discard(word)
                variants.discard(current_word)

                # Nullify variant words to prevent polluting the dictionary with duplicates
                for variant in variants:
                    with suppress(KeyError):
                        words[variant].is_variant = True

                if for_kobo:
                    if is_japanese:
                        variants.clear()
                    else:
                        # Filter out variants with a different prefix than their word.
                        # Plus, variants must be normalized by trimming whitespaces, and lowercasing it.
                        current_word_group_prefix = guess_prefix(current_word)
                        variants = {
                            variant.lower().strip()
                            for variant in variants
                            if guess_prefix(variant) == current_word_group_prefix
                        }

                if len(variants) > MAX_VARIANTS:
                    log.warning(
                        "Word %r has too many variants (%d): %r",
                        current_word,
                        len(variants),
                        sorted(variants)[:10],
                    )

            # On Kobo, we want to display a variant being the same word lowercased (see #2579):
            #   - [FR] Loches (proper noun) should also take into account "loches" in its variants
            elif for_kobo and current_word[0].isupper() and (lowercase_word := current_word.lower()) in words:
                variants.add(lowercase_word)

            # Russian on Kindle must provide a lowercase variant for uppercase-only words (see #2623)
            elif is_russian and isinstance(self, MobiFormat) and current_word.isupper():
                variants.add(current_word.lower())

            yield self.render_word(
                self.template,
                word=word,
                current_word=current_word,
                definitions=current_details.definitions.items(),
                pronunciation=utils.convert_pronunciation(current_details.pronunciations),
                gender=utils.convert_gender(current_details.genders),
                etymologies=current_details.etymology if self.include_etymology else [],
                variants=sorted(variants, key=lambda s: (len(s), s)),
            )

    def process(self) -> None:
        raise NotImplementedError()

    def render_word(self, template: Template, **kwargs: Any) -> str:
        self.variants_count += len(kwargs["variants"])
        self.words_count += 1
        return template.render(**kwargs)

    def compute_checksum(self, file: Path) -> None:
        checksum = hashlib.new(constants.ASSET_CHECKSUM_ALGO, file.read_bytes()).hexdigest()
        checksum_file = file.with_suffix(f"{file.suffix}.{constants.ASSET_CHECKSUM_ALGO}")
        checksum_file.write_text(f"{checksum} {file.name}")
        log.info("[%s] Crafted %s (%s)", self.id(), checksum_file.name, checksum)

    def summary(self, file: Path) -> None:
        log.info(
            "[%s] Generated %s (%s bytes) in %s",
            self.id(),
            file.name,
            f"{file.stat().st_size:,}",
            timedelta(seconds=monotonic() - self.start),
        )
        self.compute_checksum(file)

        log.info(
            "[%s] Finished the conversion with %s words, and %s variants, as expected.",
            self.id(),
            f"{len(self.words):,}",
            f"{len(self.variants):,}",
        )


class Summary(BaseFormat):
    """Display words + variants summary for primary formaters."""

    def summary(self, file: Path) -> None:
        log.info(
            "[%s] Effective words + variants: %s + %s => %s",
            self.id(),
            f"{self.words_count:,}",
            f"{self.variants_count:,}",
            f"{self.words_count + self.variants_count:,}",
        )
        super().summary(file)


class KoboFormat(Summary, BaseFormat):
    """Save the data into Kobo-specific ZIP file."""

    output_file = "dicthtml-{lang_src}-{lang_dst}{etym_suffix}.zip"
    template = WORD_TPL_KOBO

    def process(self) -> None:
        self.groups = self.make_groups(self.words)
        self.save()

    @staticmethod
    def craft_index(wordlist: list[str], output_dir: Path) -> Path:
        """Generate the special file "words" that is an index of all words."""
        output = output_dir / "words"
        trie = Trie(wordlist)
        trie.save(output)
        return output

    def make_groups(self, words: Words) -> Groups:
        """Group word by prefix."""
        groups: Groups = defaultdict(dict)
        guess_prefix = partial(utils.guess_prefix, locale=self.effective_lang_src())
        for word, details in words.items():
            groups[guess_prefix(word)][word] = details
        return groups

    def save(self) -> None:  # sourcery skip: extract-method
        """
        Format of resulting dicthtml-LOCALE-LOCALE.zip:

            aa.html
            ab.html
            ..
            words

        Each word must be stored into the file {letter1}{letter2}.html (gzip content).
        """

        # Clean-up before we start
        tmp_dir = self.output_dir / "tmp"
        shutil.rmtree(tmp_dir, ignore_errors=True)
        tmp_dir.mkdir()

        # Files to add to the final archive
        to_compress: list[Path] = []

        # First, create individual HTML files
        wordlist: list[str] = []
        for prefix, words in self.groups.items():
            if html := self.save_html(prefix, words, tmp_dir):
                to_compress.append(html)
            wordlist.extend(words.keys())

        # Then create the special "words" file
        to_compress.append(self.craft_index(wordlist, tmp_dir))

        # Finally, create the ZIP
        final_file = self.dictionary_file(self.output_file)
        with ZipFile(final_file, mode="w", compression=ZIP_DEFLATED) as fh:
            # The ZIP's comment will serve as the dictionary signature
            fh.comment = bytes(self.description, "utf-8")

            # Unrelated files, just for history
            fh.writestr(constants.ZIP_WORDS_COUNT, str(self.words_count + self.variants_count))
            fh.writestr(constants.ZIP_WORDS_SNAPSHOT, self.snapshot)

            for file in to_compress:
                fh.write(file, arcname=file.name)

            # Check the ZIP validity
            # testzip() returns the name of the first corrupt file, or None
            assert fh.testzip() is None, fh.testzip()

        self.summary(final_file)

    def save_html(self, name: str, words: Words, output_dir: Path) -> Path | None:
        """Generate individual HTML files.

        Content of the HTML file:

            <html>
                word 1
                word 2
                ...
            </html>
        """

        # Save to uncompressed HTML
        if not (data := "".join(line for word in words for line in self.handle_word(word, self.words))):
            return None
        raw_output = output_dir / f"{name}.raw.html"
        raw_output.write_text(data, encoding="utf-8")

        # Compress the HTML with gzip
        output = output_dir / f"{name}.html"
        with raw_output.open(mode="rb") as fi, gzip.open(output, mode="wb") as fo:
            fo.write(fi.read())

        return output

    def summary(self, file: Path) -> None:
        log.info("[%s] utils.guess_prefix() %s", self.id(), utils.guess_prefix.cache_info())
        super().summary(file)


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
    glossary_options: dict[str, str | bool] = {}

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

        if isinstance(self, StarDictFormat):
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

        if isinstance(self, MobiFormat):
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
                inputFilename=str(self.dictionary_file(DictFileFormat.output_file)),
                outputFilename=str(self.output_dir_tmp / f"dict-data.{self.target_suffix}"),
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


class BZ2DictFileFormat(BaseFormat):
    def process(self) -> None:
        df_file = self.dictionary_file(DictFileFormat.output_file)
        bz2_file = df_file.with_suffix(".df.bz2")
        bz2_file.write_bytes(bz2.compress(df_file.read_bytes()))
        return self.summary(bz2_file)


class DictOrgFormat(ConverterFromDictFile):
    """Save the data into a DICT.org file."""

    target_format = "dict.org"
    target_suffix = "index"
    final_file = "dictorg-{lang_src}-{lang_dst}{etym_suffix}.zip"
    glossary_options = {"dictzip": True, "install": False}


class MobiFormat(ConverterFromDictFile):
    """Save the data into a MobiPocket file."""

    target_format = "mobi"
    target_suffix = "mobi"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"
    zip_glob_files = ""  # Will be set in `_compress()`
    glossary_options = {
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


class StarDictFormat(ConverterFromDictFile):
    """Save the data into a StarDict file."""

    target_format = "stardict"
    target_suffix = "ifo"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.zip"
    glossary_options = {"dictzip": True, "sametypesequence": "h"}

    def _convert(self) -> None:
        super()._convert()

        # Append missing lang details to the .ifo
        ifo = self.output_dir / self.target_format / "dict-data.ifo"
        content = ifo.read_text()
        if "lang=" in content:
            return
        content += f"lang={self.effective_lang_src()}-{self.effective_lang_dst()}\n"
        ifo.write_text(content)


class JSONVolumeFormat(BaseFormat):
    """Save the data into JSON volumes with range-based splitting."""

    output_file = "jsonvolume-{lang_src}-{lang_dst}{etym_suffix}"
    max_volume_size_kb = 1024  # Target volume size in KB
    max_volume_bytes = max_volume_size_kb * 1024

    KEY_DEFINITION = "d"
    KEY_ETYMOLOGY = "e"
    KEY_GENDER = "g"
    KEY_PRONUNCIATION = "p"
    KEY_REDIRECT = "r"
    KEY_VARIANT = "v"

    def process(self) -> None:
        if not self.include_etymology:
            return

        """Generate the JSON volumes."""
        output_base = self.dictionary_file(self.output_file)
        output_base.mkdir(exist_ok=True, parents=True)

        # Get all words sorted alphabetically
        all_words = sorted(
            (word, details)
            for word, details in self.words.items()
            # Skip variant-only words without definitions
            if not details.is_variant or details.definitions
        )

        log.info(
            "[%s] Processing %s words into volumes (max %dKB each)",
            self.id(),
            f"{len(all_words):,}",
            self.max_volume_size_kb,
        )

        # Split into volumes
        volumes = self._create_volumes(all_words, output_base)

        # Generate and save manifest
        self._save_manifest(volumes, output_base)

        # Summary
        log.info(
            "[%s] Generated %s volumes with %s total words (max size: %dKB)",
            self.id(),
            f"{len(volumes):,}",
            f"{len(all_words):,}",
            self.max_volume_size_kb,
        )

    def _format_word_data(self, word: str, details: Word) -> dict[str, Any]:
        """Format a single word's data for JSON output."""
        if not details.definitions:
            if details.reverse_variants:
                return {self.KEY_REDIRECT: details.reverse_variants[0]}
            return {self.KEY_REDIRECT: details.variants[0]}

        word_data: dict[str, Any] = {}
        if defs := self._format_definitions(details.definitions):
            word_data[self.KEY_DEFINITION] = defs
        if etyms := self._format_etymology(details.etymology):
            word_data[self.KEY_ETYMOLOGY] = etyms
        if genders := utils.convert_gender(details.genders):
            word_data[self.KEY_GENDER] = genders
        if prons := utils.convert_pronunciation(details.pronunciations):
            word_data[self.KEY_PRONUNCIATION] = prons
        if variants := self.variants.get(word):
            word_data[self.KEY_VARIANT] = sorted(variants)

        return word_data

    def _format_definitions(self, definitions: Definitions) -> dict[str, list[Any]]:
        """Format definitions preserving nested structure."""
        return {
            pos: [self._format_definition_item(definition) for definition in pos_definitions]
            for pos, pos_definitions in definitions.items()
        }

    def _format_definition_item(self, definition: Definition) -> str | list[Any]:
        """Recursively format a definition item, preserving nesting."""
        if isinstance(definition, str):
            return definition
        return [self._format_definition_item(sub_def) for sub_def in definition]

    def _format_etymology(self, etymology: list[Definition]) -> str | list[Any]:
        """Format etymology preserving nested structure."""
        if not etymology:
            return ""

        if len(etymology) == 1 and isinstance(etymology[0], str):
            return etymology[0]

        result: list[str | list[Any]] = []
        for etym in etymology:
            if isinstance(etym, str):
                result.append(etym)
            else:
                result.append([self._format_definition_item(sub_etym) for sub_etym in etym])

        return result

    def _estimate_json_size(self, data: dict[str, dict[str, Any]]) -> int:
        """Estimate the size of JSON data in bytes."""
        json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return len(json_str.encode("utf-8"))

    def _create_volumes(self, all_words: list[tuple[str, Word]], output_dir: Path) -> list[dict[str, Any]]:
        """Split words into volumes based on size."""
        volumes = []
        current_volume_words: dict[str, dict[str, Any]] = {}
        current_volume_size = 0
        volume_num = 0
        first_word = ""

        for word, details in all_words:
            word_data = self._format_word_data(word, details)

            # Estimate size of adding this word
            test_entry = {word: word_data}
            word_size = self._estimate_json_size(test_entry)

            # If this is the first word in the volume, track it
            if not current_volume_words:
                first_word = word

            # Check if adding this word would exceed the limit
            if current_volume_size + word_size > self.max_volume_bytes and current_volume_words:
                # Save current volume
                last_word = list(current_volume_words.keys())[-1]
                volume_info = self._save_volume(volume_num, current_volume_words, first_word, last_word, output_dir)
                volumes.append(volume_info)

                # Start new volume
                volume_num += 1
                current_volume_words = {}
                current_volume_size = 0
                first_word = word

            # Add word to current volume
            current_volume_words[word] = word_data
            current_volume_size += word_size
            self.words_count += 1

        # Save the last volume
        if current_volume_words:
            last_word = list(current_volume_words.keys())[-1]
            volume_info = self._save_volume(volume_num, current_volume_words, first_word, last_word, output_dir)
            volumes.append(volume_info)

        return volumes

    def _save_volume(
        self,
        volume_num: int,
        words: dict[str, Any],
        first_word: str,
        last_word: str,
        output_dir: Path,
    ) -> dict[str, Any]:
        """Save a single volume and return its metadata."""
        volume_data = {"words": words}

        filename = f"vol-{volume_num:08d}.json.gz"
        filepath = output_dir / filename

        # Write gzipped JSON
        json_content = json.dumps(volume_data, ensure_ascii=False, separators=(",", ":"))
        with gzip.open(filepath, "wt", encoding="utf-8") as f:
            f.write(json_content)

        file_size = filepath.stat().st_size  # Get actual compressed file size

        log.info(
            "[%s] Volume %s: %s → %s (%s words, %sKB)",
            self.id(),
            f"{volume_num:08d}",
            first_word,
            last_word,
            f"{len(words):,}",
            f"{file_size / 1024:.1f}",
        )

        return {
            "filename": filename,
            "volumeNum": volume_num,
            "firstWord": first_word,
            "lastWord": last_word,
            "wordCount": len(words),
            "sizeBytes": file_size,
        }

    def _save_manifest(self, volumes: list[dict[str, Any]], output_dir: Path) -> None:
        """Generate and save the manifest.json file."""
        manifest = {
            "version": "3.0",
            "totalVolumes": len(volumes),
            "totalWords": self.words_count,
            "maxVolumeSizeKB": self.max_volume_size_kb,
            "volumes": [
                {
                    "file": vol["filename"],
                    "volumeNum": vol["volumeNum"],
                    "firstWord": vol["firstWord"],
                    "lastWord": vol["lastWord"],
                    "wordCount": vol["wordCount"],
                    "sizeBytes": vol["sizeBytes"],
                }
                for vol in volumes
            ],
        }

        manifest_path = output_dir / "manifest.json"
        with manifest_path.open("w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        log.info("[%s] Generated manifest.json with %d volumes", self.id(), len(volumes))
        self.compute_checksum(manifest_path)

    def summary(self, file: Path) -> None:
        """Override summary to handle directory output."""
        log.info(
            "[%s] Generated JSON volumes with %s words in %s",
            self.id(),
            f"{self.words_count:,}",
            timedelta(seconds=monotonic() - self.start),
        )
        log.info(
            "[%s] Finished the conversion with %s words, and %s variants, as expected.",
            self.id(),
            f"{len(self.words):,}",
            f"{len(self.variants):,}",
        )


PRIMARY_FORMATTERS = {KoboFormat, DictFileFormat, JSONVolumeFormat}
SECONDARY_FORMATTERS = {BZ2DictFileFormat, DictOrgFormat, MobiFormat, StarDictFormat}
FORMATTERS: dict[str, tuple[type[BaseFormat], type[BaseFormat] | None]] = {
    # "format": (primary formatter class, secondary formatter class)
    "dictfile": (DictFileFormat, BZ2DictFileFormat),
    "dicthtml": (KoboFormat, None),
    "dictorg": (DictFileFormat, DictOrgFormat),
    "jsonvolume": (JSONVolumeFormat, None),
    "mobi": (DictFileFormat, MobiFormat),
    "stardict": (DictFileFormat, StarDictFormat),
}
FORMATTERS["df"] = FORMATTERS["dictfile"]
FORMATTERS["kindle"] = FORMATTERS["mobi"]
FORMATTERS["kobo"] = FORMATTERS["dicthtml"]


def get_primary_formatters() -> set[type[BaseFormat]]:
    return PRIMARY_FORMATTERS


def get_secondary_formatters() -> set[type[BaseFormat]]:
    """Formatters that require files generated by `get_primary_formatters()`."""
    return SECONDARY_FORMATTERS


def run_formatter(
    cls: type[BaseFormat],
    locale: str,
    output_dir: Path,
    words: Words,
    variants: Variants,
    snapshot: str,
    *,
    include_etymology: bool = True,
) -> None:
    formatter = cls(
        locale,
        output_dir,
        words,
        variants,
        snapshot,
        include_etymology=include_etymology,
    )
    formatter.process()


def load(file: Path) -> Words:
    """Load the big JSON file containing all words and their details."""
    log.info("Loading %s ...", file)
    with file.open(encoding="utf-8") as fh:
        words: Words = {key: Word(**values) for key, values in json.load(fh).items()}
    log.info("Loaded %s words from %s", f"{len(words):,}", file)
    return words


def make_variants(words: Words) -> Variants:
    """Group word by variant."""
    log.info("Creating variants ...")
    variants: Variants = defaultdict(set)
    for word, details in words.items():
        for variant in details.variants:
            variants[variant].add(word)
        for variant in details.reverse_variants:
            variants[word].add(variant)
    log.info("Created %s variants", f"{len(variants):,}")
    return variants


def distribute_workload(
    formatters: set[type[BaseFormat]],
    output_dir: Path,
    snapshot: str,
    locale: str,
    words: Words,
    variants: Variants,
    *,
    include_etymology: bool = True,
    sequential: bool = False,
) -> None:
    """Run formatters in parallel."""
    threads = []

    for formatter in formatters:
        if sequential:
            run_formatter(formatter, locale, output_dir, words, variants, snapshot, include_etymology=include_etymology)
        else:
            th = threading.Thread(
                target=run_formatter,
                args=(formatter, locale, output_dir, words, variants, snapshot),
                kwargs={"include_etymology": include_etymology},
            )
            th.start()
            threads.append(th)

    for th in threads:
        th.join()


def get_latest_json_file(source_dir: Path) -> Path | None:
    """Get the name of the last data-*.json file."""
    files = list(source_dir.glob(f"data-{'[0-9]' * 8}.json"))
    return sorted(files)[-1] if files else None


def get_formatters(formats: str) -> tuple[set[type[BaseFormat]], set[type[BaseFormat]]]:
    primary_formatters: set[type[BaseFormat]] = set()
    secondary_formatters: set[type[BaseFormat]] = set()
    for fmt in (formats or "all").split(","):
        match fmt:
            case _ if fmt in FORMATTERS:
                primary, secondary = FORMATTERS[fmt]
                primary_formatters.add(primary)
                if secondary:
                    secondary_formatters.add(secondary)
            case "all":
                primary_formatters = get_primary_formatters()
                secondary_formatters = get_secondary_formatters()
                break
            case _:
                print(f"Unknown format: {fmt!r}")
    return primary_formatters, secondary_formatters


def convert(
    primary_formatters: set[type[BaseFormat]],
    secondary_formatters: set[type[BaseFormat]],
    output_dir: Path,
    snapshot: str,
    locale: str,
    words: Words,
    variants: Variants,
    *,
    with_etym_only: bool = False,
) -> None:
    args = (output_dir, snapshot, locale, words, variants)
    include_etymologies = [True] if with_etym_only else [False, True]
    for include_etymology in include_etymologies:
        distribute_workload(primary_formatters, *args, include_etymology=include_etymology)
        distribute_workload(secondary_formatters, *args, include_etymology=include_etymology, sequential=True)


def main(locale: str, format: str = "all", with_etym_only: bool = False) -> int:
    """Entry point."""

    lang_src, lang_dst = utils.guess_locales(locale)

    source_dir = render.get_source_dir(lang_src, lang_dst)
    if not (input_file := get_latest_json_file(source_dir)):
        log.error("No dump found. Run with --render first ... ")
        return 1

    # Get all words from the database
    words: Words = load(input_file)
    variants: Variants = make_variants(words)

    # And run formatters, distributing the workload
    output_dir = source_dir / "output"
    output_dir.mkdir(exist_ok=True, parents=True)

    primary_formatters, secondary_formatters = get_formatters(format)
    start = monotonic()
    convert(
        primary_formatters,
        secondary_formatters,
        output_dir,
        input_file.stem.split("-")[-1],
        locale,
        words,
        variants,
        with_etym_only=with_etym_only,
    )
    log.info("Convert done in %s!", timedelta(seconds=monotonic() - start))
    return 0
