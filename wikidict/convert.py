"""Convert rendered data to working dictionaries."""

from __future__ import annotations

import json
import logging
import threading
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from time import monotonic

from wikidict import render, utils
from wikidict.converters import BaseFormat
from wikidict.converters.dictfile import DictFileFormat
from wikidict.converters.dicthtml import DictHtmlFormat
from wikidict.converters.dictorg import DictOrgFormat
from wikidict.converters.json_volume import JSONVolumeFormat
from wikidict.converters.mobi import MobiFormat
from wikidict.converters.stardict import StarDictFormat
from wikidict.stubs import Variants, Word, Words

log = logging.getLogger(__name__)

FORMATTERS: dict[str, type[BaseFormat]] = {
    "dictfile": DictFileFormat,
    "dicthtml": DictHtmlFormat,
    "dictorg": DictOrgFormat,
    "jsonvolume": JSONVolumeFormat,
    "mobi": MobiFormat,
    "stardict": StarDictFormat,
}


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
    return max(files) if files else None


def get_formatters(formats: str) -> set[type[BaseFormat]]:
    formatters: set[type[BaseFormat]] = set()
    for fmt in (formats or "all").split(","):
        match fmt:
            case _ if fmt in FORMATTERS:
                formatters.add(FORMATTERS[fmt])
            case "all":
                formatters.update(FORMATTERS.values())
                break
            case _:
                print(f"Unknown format: {fmt!r}")
    return formatters


def convert(
    formatters: set[type[BaseFormat]],
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
        distribute_workload(formatters, *args, include_etymology=include_etymology)


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

    formatters = get_formatters(format)
    start = monotonic()
    convert(
        formatters,
        output_dir,
        input_file.stem.split("-")[-1],
        locale,
        words,
        variants,
        with_etym_only=with_etym_only,
    )
    log.info("Convert done in %s!", timedelta(seconds=monotonic() - start))
    return 0
