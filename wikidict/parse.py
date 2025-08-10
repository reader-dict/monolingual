"""Parse and store raw Wiktionary data."""

from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from xml.sax.saxutils import unescape

from . import lang, utils

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator


log = logging.getLogger(__name__)

RE_TEXT = re.compile(r"<text[^>]*>(.*)</text>", flags=re.DOTALL).finditer
RE_TITLE = re.compile(r"<title>([^:]*)</title>").finditer

# To list all words not taken into account with current head sections:
#    DEBUG_PARSE=1 python -m wikidict LOCALE --parse >out.log
DEBUG_PARSE = "DEBUG_PARSE" in os.environ


def xml_iter_parse(file: Path) -> Generator[str]:
    """Efficient XML parsing for big files."""
    element: list[str] = []
    is_element = False

    with file.open(encoding="utf-8") as fh:
        for line in fh:
            if is_element:
                if "/page>" in line:
                    yield "".join(element)
                    element = []
                    is_element = False
                else:
                    element.append(line)
            elif "<page" in line:
                is_element = True


def xml_parse_element(element: str, head_sections_matcher: Callable[[str], Iterator[str]]) -> tuple[str, str]:
    """Parse the XML `element` to retrieve the word and its definitions."""
    if title_match := next(RE_TITLE(element), None):
        for text_match in RE_TEXT(element, pos=element.find("<text", title_match.endpos)):
            if next(head_sections_matcher(wikicode := text_match[1]), None):
                return title_match[1], wikicode

        if DEBUG_PARSE:
            try:
                print(f"{title_match[1]!r}: {wikicode[:200]!r}", flush=True)
            except UnboundLocalError:
                print(f"{title_match[1]!r}: NO TEXT", flush=True)

    # No Wikicode; unfinished page; no interesting head section; a foreign word, etc. Who knows?
    return "", ""


def process(file: Path, locale: str) -> dict[str, str]:
    """Process the big XML file and retain only information we are interested in."""
    words: dict[str, str] = defaultdict(str)
    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)

    log.info("Processing %s for destination lang %r ...", file, lang_dst)

    if lang_src == "de":
        # It is not possible to use a regexp matcher
        def head_sections_matcher(wikicode: str) -> Iterator[str]:
            return (s for s in lang.head_sections[lang_dst] if s in wikicode.lower())
    else:
        head_sections_matcher = re.compile(
            rf"^=*\s*(?:{'|'.join(hs.replace('{', r'\{').replace('|', r'\|') for hs in lang.head_sections[lang_dst])})",
            flags=re.IGNORECASE | re.MULTILINE,
        ).finditer  # type: ignore[assignment]

    for element in xml_iter_parse(file):
        word, code = xml_parse_element(element, head_sections_matcher)
        if word and code:
            if lang_dst == "en" and word[:19] == "Unsupported titles/":
                continue
            words[unescape(word)] = unescape(code)

    return words


def save(output: Path, words: dict[str, str]) -> None:
    """Persist data."""
    if not words:
        log.warning("No words to save.")
        return

    output.parent.mkdir(exist_ok=True, parents=True)
    with output.open(mode="w", encoding="utf-8") as fh:
        json.dump(words, fh, ensure_ascii=False, indent=4, sort_keys=True)

    log.info("Saved %s words into %s", f"{len(words):,}", output)


def get_latest_xml_file(source_dir: Path) -> Path | None:
    """Get the name of the last pages-*.xml file."""
    files = list(source_dir.glob(f"pages-{'[0-9]' * 8}.xml"))
    return sorted(files)[-1] if files else None


def get_source_dir(lang_src: str) -> Path:
    return Path(os.getenv("CWD", "")) / "data" / lang_src


def get_output_file(source_dir: Path, lang_src: str, lang_dst: str, snapshot: str) -> Path:
    return source_dir.parent / lang_dst / lang_src / f"data_wikicode-{snapshot}.json"


def main(locale: str) -> int:
    """Entry point."""

    start = monotonic()
    lang_src, lang_dst = utils.guess_locales(locale)

    source_dir = get_source_dir(lang_src)
    if not (input_file := get_latest_xml_file(source_dir)):
        log.error("No dump found. Run with --download first ... ")
        return 1

    ret = 0
    output = get_output_file(source_dir, lang_src, lang_dst, input_file.stem.split("-")[-1])
    if output.is_file():
        log.info("Already parsed into %s", output)
    else:
        words = process(input_file, locale)
        save(output, words)
        if not words:
            ret = 1

    log.info("Parse done in %s!", timedelta(seconds=monotonic() - start))
    return ret
