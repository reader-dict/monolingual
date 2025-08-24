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
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from zipfile import ZIP_DEFLATED, ZipFile

from jinja2 import Template
from marisa_trie import Trie
from pyglossary.glossary_v2 import ConvertArgs, Glossary

from . import constants, render, user_functions, utils
from .stubs import Word

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any

    from .stubs import Groups, Variants, Words

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
{%- endif -%}</html>


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

        logging.basicConfig(level=logging.INFO)
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
        # Prevent storing variants definitions in DictFile & co
        if (chosen_word := words[word]).is_variant and not chosen_word.definitions and not isinstance(self, KoboFormat):
            return

        details = deepcopy(chosen_word)
        current_words = {word: details}
        guess_prefix = utils.guess_prefix
        word_group_prefix = guess_prefix(word)

        if (
            details.variants
            and isinstance(self, KoboFormat)
            and any(guess_prefix(variant) != word_group_prefix for variant in details.variants)
        ):
            # [***] Variants are more like typos, or misses, and so devices expect word & variants to start with same letters, at least.
            # An example in FR, where "suis" (verb flexion) is a variant of both "être" & "suivre": "suis" & "être" are quite differents.
            # As a workaround, we yield as many words as there are variants but under the word "suis": at the end, we will have 3 words:
            #   - "suis" with the content "suis" (itself)
            #   - "suis" with the content "être"
            #   - "suis" with the content "suivre"
            for variant in details.variants:
                if root := self.words.get(variant):
                    current_words[variant] = root

        for current_word, current_details in sorted(current_words.items()):
            if not current_details.definitions:
                continue

            all_variants = self.variants
            if variants := deepcopy(all_variants.get(current_word, [])):
                # Add variants of empty* variant, only 1 redirection:
                #   [ES] gastada* -> gastado* -> gastar --> (gastada, gastado) -> gastar
                # Note: the process works backward: from gastar up to gastado up to gastada.
                for variant in [*variants]:
                    if (
                        (wv := words.get(variant))
                        and not wv.definitions
                        and (new_variants := all_variants.get(variant))
                    ):
                        variants.extend(new_variants)

                # Filter out variants being identical to the word (it happens when altering `current_words`, cf [***])
                variants = [variant for variant in variants if variant not in {word, current_word}]

                # Nullify variant words to prevent polluting the dictionary with duplicates
                for variant in variants:
                    words[variant].is_variant = True

                if isinstance(self, KoboFormat):
                    # Filter out variants with a different prefix that their word.
                    # Plus, variants must be normalized by trimming whitespaces, and lowercasing it.
                    current_word_group_prefix = guess_prefix(current_word)
                    variants = [
                        variant.lower().strip()
                        for variant in variants
                        if guess_prefix(variant) == current_word_group_prefix
                    ]

                if len(variants := list(set(variants))) > MAX_VARIANTS:
                    log.warning("Word %r has too many variants (%d): %r", current_word, len(variants), variants)

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
        if type(self).__name__ in {KoboFormat.__name__, DictFileFormat.__name__}:
            log.info(
                "[%s] Effective words + variants: %s + %s => %s",
                self.id(),
                f"{self.words_count:,}",
                f"{self.variants_count:,}",
                f"{self.words_count + self.variants_count:,}",
            )
            log.info("[%s] utils.guess_prefix() %s", self.id(), utils.guess_prefix.cache_info())

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


class KoboFormat(BaseFormat):
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

    @staticmethod
    def make_groups(words: Words) -> Groups:
        """Group word by prefix."""
        groups: Groups = defaultdict(dict)
        for word, details in words.items():
            groups[utils.guess_prefix(word)][word] = details
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


class DictFileFormat(BaseFormat):
    """Save the data into a *.df* DictFile."""

    output_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.df"
    template = WORD_TPL_DICTFILE

    def process(self) -> None:
        file = self.dictionary_file(self.output_file)
        words = self.words
        data = "".join(formatted_word for word in words for formatted_word in self.handle_word(word, words))
        file.write_text(data, encoding="utf-8")

        self.summary(file)


class DictFileFormatForMobi(DictFileFormat):
    """Save the data into a *.df* DictFile."""

    output_file = f"altered-{DictFileFormat.output_file}"


class ConverterFromDictFile(DictFileFormat):
    target_format = ""
    target_suffix = ""
    final_file = ""
    zip_glob_files = "dict-data.*"
    dictfile_format_cls = DictFileFormat
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

            # We do not want to compress the `.syn` file as it does not work everywhere (see issue #2407)
            writer_cls.dictzipSynFile = False

            # Do not append extra data to the book name
            def get_bookname(cls) -> str:  # type: ignore[no-untyped-def]
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

        self.output_dir_tmp.mkdir()
        glos.convert(
            ConvertArgs(
                inputFilename=str(self.dictionary_file(self.dictfile_format_cls.output_file)),
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
        self.summary(final_file)


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
    """Save the data into a Mobi file.

    Incompatibility issues:

    1) No support for multiple HTML tags, they will be ignored:

        Warning(inputpreprocessor):W29007: Rejected unknown tag: <bdi>

    2) Most locales are not fully supported:

        Warning(index build):W15008: language not supported. Using default phonetics for spellchecker: english.

    3) Greek (EL), and Russian (RU), locales might be incorrectly displayed:

        Error(core):E1008: Failed conversion to unicode. The resulting string may contain wrong characters.

    """

    target_format = "mobi"
    target_suffix = "mobi"
    final_file = "dict-{lang_src}-{lang_dst}{etym_suffix}.mobi.zip"
    zip_glob_files = ""  # Will be set in `_compress()`
    dictfile_format_cls = DictFileFormatForMobi
    glossary_options = {
        "cover_path": str(constants.COVER_FILE),
        "keep": True,
        "kindlegen_path": str(constants.KINDLEGEN_FILE),
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


def get_primary_formatters() -> list[type[BaseFormat]]:
    return [KoboFormat, DictFileFormat]


def get_secondary_formatters() -> list[type[BaseFormat]]:
    """Formatters that require files generated by `get_primary_formatters()`."""
    return [BZ2DictFileFormat, DictOrgFormat, StarDictFormat]


def run_mobi_formatter(
    output_dir: Path,
    file: Path,
    locale: str,
    words: Words,
    variants: Variants,
    *,
    include_etymology: bool = True,
) -> None:
    """Mobi formatter.

    For multiple languages, we need to delete words if the total number of unique unicode characters is greater than 256.
    To do this, we delete words using the least-used characters until we meet this condition.
    """

    if locale in constants.MOBI_SKIP:
        log.info("[Mobi %s] Skipping as the final file size would be > 650 MiB", locale.upper())
        return

    def all_chars(word: str, details: Word) -> set[str]:
        chars = set(word)
        if definitions := details.definitions:
            if isinstance(definitions, str):
                chars.update(definitions)
            elif isinstance(definitions, tuple):
                chars.update(user_functions.flatten(definitions))
        if etymology := details.etymology:
            if isinstance(etymology, str):
                chars.update(etymology)
            elif isinstance(etymology, tuple):
                chars.update(user_functions.flatten(etymology))
        return chars

    stats = defaultdict(list)
    for word, details in words.copy().items():
        if len(word) > 127:
            log.info("[Mobi %s] Truncated word too long: %r", locale.upper(), word)
            truncated = word[:127]
            words[truncated] = words.pop(word)
            word = truncated
        for char in all_chars(word, details):
            stats[char].append(word)

    if locale in constants.MOBI_CLEANUP and len(stats) > 256:
        new_words = words.copy()
        threshold = 1
        while len(stats) > 256:
            log.info(
                "[Mobi %s] Removing words with unique characters count at %d (total is %d)",
                locale.upper(),
                threshold,
                len(stats),
            )
            for char, related_words in sorted(stats.copy().items(), key=lambda v: (char, len(v[1]))):
                if len(related_words) == threshold:
                    for w in related_words:
                        new_words.pop(w, None)
                    stats.pop(char)
                if len(stats) <= 256:
                    break
            threshold += 1

        log.info(
            "[Mobi %s] Removed %s words from .mobi (total words count is %s, unique characters count is %d)",
            locale.upper(),
            f"{len(words) - len(new_words):,}",
            f"{len(new_words):,}",
            len(stats),
        )
        words = new_words
        variants = make_variants(words)
    else:
        log.info(
            "[Mobi %s] Untouched words for .mobi (total words count is %s, unique characters count is %d)",
            locale.upper(),
            f"{len(words):,}",
            len(stats),
        )

    args = (locale, output_dir, words, variants, file.stem.split("-")[-1])
    run_formatter(DictFileFormatForMobi, *args, include_etymology=include_etymology)
    try:
        run_formatter(MobiFormat, *args, include_etymology=include_etymology)
    except Exception:
        log.exception("[Mobi %s] Error with the Mobi conversion", locale.upper())


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
    variants: Variants = defaultdict(list)
    for word, details in words.items():
        for variant in details.variants:
            variants[variant].append(word)
    log.info("Created %s variants", f"{len(variants):,}")
    return variants


def distribute_workload(
    formatters: list[type[BaseFormat]],
    output_dir: Path,
    file: Path,
    locale: str,
    words: Words,
    variants: Variants,
    *,
    include_etymology: bool = True,
) -> None:
    """Run formatters in parallel."""
    threads = []

    for formatter in formatters:
        th = threading.Thread(
            target=run_formatter,
            args=(formatter, locale, output_dir, words, variants, file.stem.split("-")[-1]),
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


def main(locale: str) -> int:
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
    args = (output_dir, input_file, locale, words, variants)

    start = monotonic()
    for include_etymology in [False, True]:
        distribute_workload(get_primary_formatters(), *args, include_etymology=include_etymology)
        distribute_workload(get_secondary_formatters(), *args, include_etymology=include_etymology)
        run_mobi_formatter(*args, include_etymology=include_etymology)

    log.info("Convert done in %s!", timedelta(seconds=monotonic() - start))
    return 0
