"""Parse and store raw Wiktionary data."""

from __future__ import annotations

import bz2
import json
import logging
import os
import re
from datetime import timedelta
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from xml.sax.saxutils import unescape

from . import constants, context, lang, utils

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterator


log = logging.getLogger(__name__)

RE_REDIRECT = re.compile(r'<redirect title="(.+)" />').finditer
RE_TEXT = re.compile(r"<text[^>]*>(.*)</text>", flags=re.DOTALL).finditer
RE_TITLE_WORD = re.compile(r"<title>([^:]*)</title>").finditer

# To list all words not taken into account with current head sections:
#    DEBUG_PARSE=1 python -m wikidict LOCALE --parse >out.log
DEBUG_PARSE = "DEBUG_PARSE" in os.environ


def xml_iter_parse(file: Path) -> Generator[str]:
    """Efficient XML parsing for big files."""
    with bz2.open(file, "rt", encoding="utf-8") as fh:
        current_page: list[str] = []
        in_page = False

        start_tag = "  <page>\n"
        end_tag = "  </page>\n"

        for line in fh:
            if in_page:
                if line == end_tag:
                    yield "".join(current_page)
                    current_page.clear()
                    in_page = False
                else:
                    current_page.append(line)
            elif line == start_tag:
                in_page = True


def xml_parse_element(
    element: str,
    head_sections_matcher: Callable[[str], Iterator[str]],
    module_matcher: Callable[[str], Iterator[re.Match[str]]],
    template_matcher: Callable[[str], Iterator[re.Match[str]]],
    appendix_matcher: Callable[[str], Iterator[re.Match[str]]],
) -> tuple[str, str]:
    """Parse the XML `element` to retrieve interesting Wiktionary raw data."""

    # Module
    if title := next(module_matcher(element), None):
        if not title[1].lower().endswith(constants.MODULES_TO_IGNORE):
            body, redirect_to = "", None
            if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
                redirect_to = redirect[1]
            elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
                body = unescape(text[1], entities=constants.HTML_REPL_BODY)
            if body or redirect_to:
                page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
                context.CTX.add_page(page, body=body, namespace_id=828, model="Scribunto", redirect_to=redirect_to)

    # Template
    elif title := next(template_matcher(element), None):
        if not title[1].lower().endswith(constants.MODULES_TO_IGNORE):
            body, redirect_to = "", None
            if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
                redirect_to = redirect[1]
            elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
                body = unescape(text[1], entities=constants.HTML_REPL_BODY)
            if body or redirect_to:
                page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
                context.CTX.add_page(page, body=body, namespace_id=10, model="wikitext", redirect_to=redirect_to)

    # Appendix
    elif title := next(appendix_matcher(element), None):
        body, redirect_to = "", None
        if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
            redirect_to = redirect[1]
        elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
            body = unescape(text[1], entities=constants.HTML_REPL_BODY)
        if body or redirect_to:
            page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
            context.CTX.add_page(page, body=body, namespace_id=100, model="wikitext", redirect_to=redirect_to)

    # Word
    elif title := next(RE_TITLE_WORD(element), None):
        text = next(RE_TEXT(element, pos=element.find("<text", title.endpos)), "")
        if text and next(head_sections_matcher(wikicode := text[1]), None):
            return title[1], wikicode

        if DEBUG_PARSE:
            try:
                print(f"{title[1]!r}: {wikicode[:200]!r}", flush=True)
            except UnboundLocalError:
                print(f"{title[1]!r}: NO TEXT", flush=True)

    # No Wikicode; unfinished page; no interesting head section; a foreign word, or a module/template.
    return "", ""


def process(file: Path, locale: str) -> dict[str, str]:
    """Process the big XML file and retain only information we are interested in."""
    words: dict[str, str] = {}
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

    module_matcher = re.compile(rf"<title>({lang.module_trans[lang_dst]}:[^<]+)</title>").finditer
    template_matcher = re.compile(rf"<title>({lang.template_trans[lang_dst]}:[^<]+)</title>").finditer
    appendix_matcher = re.compile(rf"<title>({lang.appendix_trans[lang_dst]}:[^<]+)</title>").finditer

    for element in xml_iter_parse(file):
        title, code = xml_parse_element(
            element,
            head_sections_matcher,
            module_matcher,
            template_matcher,
            appendix_matcher,
        )
        if not title or not code or (lang_dst == "en" and title[:19] == "Unsupported titles/"):
            continue
        words[unescape(title)] = unescape(code)

    context.adapt_templates(lang_dst)

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


def get_latest_file(source_dir: Path) -> Path | None:
    """Get the name of the latest downloaded dump file."""
    files = list(source_dir.glob(f"pages-{'[0-9]' * 8}.xml.bz2"))
    return sorted(files)[-1] if files else None


def get_source_dir(lang_src: str) -> Path:
    return Path(os.getenv("CWD", "")) / "data" / lang_src


def get_output_file(source_dir: Path, lang_src: str, lang_dst: str, snapshot: str) -> Path:
    return source_dir.parent / lang_dst / lang_src / f"data_wikicode-{snapshot}.json"


def get_output_file_modules(source_dir: Path, lang_src: str, lang_dst: str, snapshot: str) -> Path:
    return source_dir.parent / lang_dst / lang_src / f"modules-{snapshot}.sqlite"


def main(locale: str) -> int:
    """Entry point."""

    start = monotonic()
    lang_src, lang_dst = utils.guess_locales(locale)

    source_dir = get_source_dir(lang_src)
    if not (input_file := get_latest_file(source_dir)):
        log.error("No dump found. Run with --download first ... ")
        return 1

    ret = 0
    output = get_output_file(source_dir, lang_src, lang_dst, input_file.stem[6:14])
    if output.is_file():
        log.info("Already parsed into %s", output)
    else:
        words = process(input_file, locale)
        save(output, words)
        if not words:
            ret = 1

    log.info("Parse done in %s!", timedelta(seconds=monotonic() - start))
    return ret
