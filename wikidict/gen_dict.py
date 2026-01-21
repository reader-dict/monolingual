"""DEBUG: generate the dictionary for specific words."""

import os
from datetime import UTC, datetime
from pathlib import Path

from . import context
from .convert import convert, get_formatters, make_variants
from .render import render_word
from .stubs import Variants, Words


def main(locale: str, words: str, output: Path | str, *, format: str = "kobo") -> int:
    """Entry point."""

    if not context.setup_modules_db(locale):
        exit(1)

    if isinstance(output, str):
        output_dir = Path(os.getenv("CWD", "")) / output
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = output

    all_words: Words = {}
    for word in words.split(","):
        if not (word_stripped := word.strip()):
            continue
        render_word((word_stripped, context.get_word(word_stripped)), all_words, locale)

    variants: Variants = make_variants(all_words)
    snapshot = datetime.now(tz=UTC).strftime("%Y%m%d")
    primary_formatters, secondary_formatters, mobi_run = get_formatters(format)
    convert(
        primary_formatters,
        secondary_formatters,
        mobi_run,
        output_dir,
        snapshot,
        locale,
        all_words,
        variants,
        with_etym_only=True,
    )

    return 0
