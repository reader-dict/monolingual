"""Get and render a word."""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

from . import constants, utils
from .render import parse_word
from .user_functions import int_to_roman

if TYPE_CHECKING:
    from .stubs import Word


def bold(value: str) -> str:
    return value if "NO_COLORS" in os.environ else f"\033[1m{value}\033[22m"


def italic(value: str) -> str:
    return value if "NO_COLORS" in os.environ else f"\033[3m{value}\033[23m"


def get_word(word: str, locale: str, *, all_templates: list[tuple[str, str, str]] | None = None) -> Word:
    """Get a *word* wikicode and parse it."""
    url = f"https://{utils.guess_lang_origin(locale)}.wiktionary.org/w/index.php?title={word}&action=raw"
    with constants.SESSION.get(url) as req:
        req.raise_for_status()
        code = req.text
    return parse_word(word, code, locale, force=True, all_templates=all_templates)


def get_and_parse_word(word: str, locale: str, *, raw: bool = False) -> None:
    """Get a *word* wikicode, parse it and print it."""

    def strip_html(text: str) -> str:
        """Strip HTML chars."""
        if raw:
            return repr(text)
        text = text.replace("<br>", "\n")
        text = text.replace("<br/>", "\n")
        text = re.sub(r"<b>([^<]+)</b>", lambda m: bold(m[1]), text)
        text = re.sub(r"<i>([^<]+)</i>", lambda m: italic(m[1]), text)
        text = re.sub(r"<[^>]+/?>", "", text)
        text = text.replace("&gt;", ">")
        text = text.replace("&lt;", "<")
        text = text.replace("&mdash;", "—")
        text = text.replace("&minus;", "−")
        text = text.replace("&nbsp;", " ")
        text = text.replace("&ndash;", "–")
        text = text.replace("&thinsp;", " ")
        text = text.replace("&times;", "×")
        text = text.replace(" ,", ",")
        text = text.replace(" .", ".")
        return text

    all_templates: list[tuple[str, str, str]] = []
    details = get_word(word, locale, all_templates=all_templates)
    print(
        word,
        utils.convert_pronunciation(details.pronunciations).lstrip(),
        strip_html(utils.convert_gender(details.genders).lstrip()),
    )

    for pos, definitions in sorted(details.definitions.items(), key=lambda kv: kv[0]):
        print("\n", bold(pos))
        index = 1
        for definition in definitions:
            if not isinstance(definition, tuple):
                print(f"{index}.".rjust(4), strip_html(definition))
                index = index + 1
                continue

            for a, subdef in zip("abcdefghijklmopqrstuvwxz", definition):
                if not isinstance(subdef, tuple):
                    print(f"{a}.".rjust(8), strip_html(subdef))
                    continue

                for rn, subsubdef in enumerate(subdef, 1):
                    print(f"{int_to_roman(rn).lower()}.".rjust(12), strip_html(subsubdef))

    if details.etymology:
        print("\n")
        for etymology in details.etymology:
            if not isinstance(etymology, tuple):
                print(strip_html(etymology))
                continue

            for i, sub_etymology in enumerate(etymology, 1):
                print(f"{i}.".rjust(8), strip_html(sub_etymology))  # type: ignore[arg-type]

    if details.variants:
        print("\n[variants]", ", ".join(iter(details.variants)))

    print()
    utils.check_for_missing_templates(all_templates)


def set_output(locale: str, word: str) -> None:
    """It is very specific to GitHub Actions, and will set the job summary with helpful information."""
    if "CI" not in os.environ:
        return

    with open(os.environ["GITHUB_STEP_SUMMARY"], "ab") as fh:
        fh.write(f"[{locale.upper()}] {word!r}\n".encode())


def main(locale: str, word: str, *, raw: bool = False) -> int:
    """Entry point."""

    _, lang_dst = utils.guess_locales(locale, use_log=False)

    # If *word* is empty, get a random word
    word = word or utils.get_random_word(lang_dst)

    set_output(locale, word)
    get_and_parse_word(word, locale, raw=raw)
    return 0
