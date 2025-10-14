"""DEBUG: generate the dictionary for specific words."""

import os
from datetime import UTC, datetime
from pathlib import Path

from .convert import convert, get_formatters, make_variants
from .get_word import get_word
from .stubs import Variants


def main(locale: str, words: str, output: Path | str, *, format: str = "kobo") -> int:
    """Entry point."""

    if isinstance(output, str):
        output_dir = Path(os.getenv("CWD", "")) / output
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = output

    words_stripped = [word_stripped for word in words.split(",") if (word_stripped := word.strip())]
    all_words = {word: get_word(word, locale) for word in words_stripped}
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
