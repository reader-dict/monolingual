"""Render templates from raw data."""

from __future__ import annotations

import logging
import os

from . import convert, render, utils
from .stubs import Words

log = logging.getLogger(__name__)


def show_pos(words: Words) -> None:
    debug = os.getenv("DEBUG_POS", "")
    text = "\nPart Of Speech:"
    all_pos: list[str] = []

    for word, details in words.items():
        all_pos.extend(new_pos := details.definitions.keys())
        if debug and any(debug in pos for pos in new_pos):
            print(f"{word!r}: {', '.join(new_pos)}")

    for count, pos in enumerate(sorted(set(all_pos)), 1):
        text += f"\n  {str(count).rjust(2)}. {pos!r}"

    log.info(text)


def main(locale: str) -> int:
    """Entry point."""

    lang_src, lang_dst = utils.guess_locales(locale)
    utils.setup_logging(lang_src, lang_dst)

    source_dir = render.get_source_dir(lang_src, lang_dst)
    if not (input_file := convert.get_latest_json_file(source_dir)):
        log.error("No dump found. Run with --parse first ... ")
        return 1

    output = render.get_output_file(source_dir, input_file.stem.split("-")[-1])
    words = convert.load(output)
    show_pos(words)
    return 0
