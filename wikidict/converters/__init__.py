from __future__ import annotations

import hashlib
import logging
import os
from collections.abc import Generator
from contextlib import suppress
from copy import deepcopy
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from time import monotonic
from typing import Any

from idzip import compressor
from jinja2 import Template

from wikidict import constants, utils
from wikidict.stubs import Variants, Words

log = logging.getLogger(__name__)


def dictzip(ifile: Path) -> Path:
    ofile = ifile.with_suffix(f"{ifile.suffix}.dz")
    with ifile.open(mode="rb") as in_file, ofile.open(mode="wb") as out_file:
        ifile_stat = os.fstat(in_file.fileno())
        compressor.compress(
            in_file,
            ifile_stat.st_size,
            out_file,
            ifile.name,
            int(ifile_stat.st_mtime),
        )
    ifile.unlink()
    return ofile


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
        self.locale = locale
        self._lang_src, self._lang_dst = utils.guess_locales(locale)
        self.format = type(self).__name__.removesuffix("Format")
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

    def dictionary_file(self, output_file: str, *, output_dir: Path | None = None) -> Path:
        return (output_dir or self.output_dir) / output_file.format(
            lang_src=self.effective_lang_src(),
            lang_dst=self.effective_lang_dst(),
            etym_suffix="" if self.include_etymology else constants.NO_ETYMOLOGY_SUFFIX,
        )

    def handle_word(self, word: str, words: Words) -> Generator[str]:
        for_kobo = self.format == "DictHtml"

        # Prevent storing variants definitions in DictFile & co
        if (details := words[word]).is_variant and not details.definitions and not for_kobo:
            return

        lang_src = self.effective_lang_src()

        if for_kobo and details.variants:
            # On Kobo, there is a special file used to handle variants that have a different group prefix: prefix_exceptions.
            # It will be populated with the content of `self.prefix_exceptions` later.
            guess_prefix = partial(utils.guess_prefix, locale=lang_src)
            word_group_prefix = guess_prefix(word)
            for variant in details.variants:
                if lang_src == "ja":
                    self.prefix_exceptions.append(f"{word}\t{guess_prefix(variant)}")  # type: ignore[attr-defined]
                elif (variant_group_prefix := guess_prefix(variant)) != word_group_prefix:
                    self.prefix_exceptions.append(f"{word}\t{variant_group_prefix}")  # type: ignore[attr-defined]

        if not details.definitions:
            return

        all_variants = self.variants
        if variants := deepcopy(all_variants.get(word, set())):
            # Add variants of empty* variant, only 1 redirection:
            #   [ES] gastada* -> gastado* -> gastar --> (gastada, gastado) -> gastar
            # Note: the process works backward: from gastar up to gastado up to gastada.
            for variant in [*variants]:
                if (wv := words.get(variant)) and not wv.definitions and (new_variants := all_variants.get(variant)):
                    variants.update(new_variants)

            # Filter out variants being identical to the word
            variants.discard(word)

            # Nullify variant words to prevent polluting the dictionary with duplicates
            for variant in variants:
                with suppress(KeyError):
                    words[variant].is_variant = True

            if for_kobo:
                # Variants must be normalized by trimming whitespaces, and lowercasing it.
                variants = {variant.lower().strip() for variant in variants}

        # On Kobo, we want to display a variant being the same word lowercased (see #2579):
        #   - [FR] Loches (proper noun) should also take into account "loches" in its variants
        elif for_kobo and word[0].isupper() and (lowercase_word := word.lower()) in words:
            variants.add(lowercase_word)

        # Russian/Ukranian on Kindle must provide a lowercase variant for uppercase-only words (see #2623)
        elif lang_src in {"ru", "uk"} and self.format == "Mobi" and word.isupper():
            variants.add(word.lower())

        # For Japanese hiragana words, the <a name="..."> needs to be the katakana version
        # because Kobo normalizes hiragana to katakana when looking up words.
        # Leaving this out causes the Kobo to completely fail to find entries for hiragana words
        # (see #2750)
        # Inspiration: https://github.com/cessen/kobo_jp_dict/blob/2f14c08dbd6e5dfb7f3bc95bace6ecead3a8ddb5/src/generic_dict.rs#L334-L337
        # e.g. for the hiragana entry "あい", we have to generate
        # <a name="アイ"> with the katakana version, but still display the text as あい
        # アイ.html: <w><p><a name="アイ" /><b>あい</b>...</p></w>
        if lang_src == "ja":
            headword = utils.to_katakana(word)
        else:
            headword = word

        yield self.render_word(
            self.template,
            headword=headword,
            word=word,
            definitions=details.definitions.items(),
            pronunciation=utils.convert_pronunciation(details.pronunciations),
            etymologies=details.etymology if self.include_etymology else [],
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
            file,
            f"{file.stat().st_size:,}",
            timedelta(seconds=monotonic() - self.start),
        )
        self.compute_checksum(file)

        log.info(
            "[%s] Effective words + variants: %s + %s => %s",
            self.id(),
            f"{self.words_count:,}",
            f"{self.variants_count:,}",
            f"{self.words_count + self.variants_count:,}",
        )

        log.info(
            "[%s] Finished the conversion with %s words, and %s variants, as expected.",
            self.id(),
            f"{len(self.words):,}",
            f"{len(self.variants):,}",
        )
