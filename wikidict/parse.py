"""Parse and store raw Wiktionary data."""

from __future__ import annotations

import json
import logging
import os
import re
from datetime import timedelta
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING
from xml.sax.saxutils import unescape

from rich.progress import (
    BarColumn,
    FileSizeColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TotalFileSizeColumn,
    TransferSpeedColumn,
)

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


def xml_iter_parse(file: Path, locale: str) -> Generator[str]:
    """Efficient XML parsing for big files."""
    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)
    file_size = file.stat().st_size

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TextColumn("•"),
        FileSizeColumn(),
        TextColumn("/"),
        TotalFileSizeColumn(),
        TextColumn("•"),
        TransferSpeedColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(),
    ) as progress:
        task = progress.add_task(f"[cyan][{lang_src.upper()}-{lang_dst.upper()}] Parsing {file.name}", total=file_size)

        with file.open(encoding="utf-8") as fh:
            current_size = fh.buffer.tell  # type: ignore[attr-defined]
            current_page: list[str] = []
            in_page = False
            start_tag = "  <page>\n"
            end_tag = "  </page>\n"
            lines = 0

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

                if (lines := lines + 1) == 100:
                    lines = 0
                    progress.update(task, completed=current_size())

        # Final update to ensure we show 100%
        progress.update(
            task,
            completed=file_size,
            description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Parsed {file.name} [green]✓[/green]",
        )


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
                context.new_page(page, 828, body, redirect_to=redirect_to)

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
                context.new_page(page, 10, body, redirect_to=redirect_to)

    # Appendix
    elif title := next(appendix_matcher(element), None):
        body, redirect_to = "", None
        if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
            redirect_to = redirect[1]
        elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
            body = unescape(text[1], entities=constants.HTML_REPL_BODY)
        if body or redirect_to:
            page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
            context.new_page(page, 100, body, redirect_to=redirect_to)

    # Word
    elif title := next(RE_TITLE_WORD(element), None):
        if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
            redirect_to = redirect[1]
            return title[1], f"{constants.REDIRECT_KEY}{redirect_to}"

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
    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)

    utils.setup_logging(lang_src, lang_dst)

    words: dict[str, str] = {}
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

    if is_monolingual := lang_src == lang_dst:
        context.setup_modules_db(locale, db_already_setup=False)

        module_matcher = re.compile(rf"<title>({lang.module_trans[lang_dst]}:[^<]+)</title>").finditer
        template_matcher = re.compile(rf"<title>({lang.template_trans[lang_dst]}:[^<]+)</title>").finditer
        appendix_matcher = re.compile(rf"<title>({lang.appendix_trans[lang_dst]}:[^<]+)</title>").finditer
    else:

        def module_matcher(*_, **__):  # type: ignore[no-untyped-def]
            yield from ()

        def template_matcher(*_, **__):  # type: ignore[no-untyped-def]
            yield from ()

        def appendix_matcher(*_, **__):  # type: ignore[no-untyped-def]
            yield from ()

    for element in xml_iter_parse(file, locale):
        title, code = xml_parse_element(
            element,
            head_sections_matcher,
            module_matcher,
            template_matcher,
            appendix_matcher,
        )
        if not title or not code or (lang_dst == "en" and title[:19] == "Unsupported titles/"):
            continue
        words[unescape(title, entities=constants.HTML_REPL_TITLE)] = unescape(code, entities=constants.HTML_REPL_BODY)

    if is_monolingual:
        # Check that modules were properly imported
        iterator = context.get_ctx().ctx.get_all_pages(namespace_ids=[10, 828])
        next(iterator)  # special sandbox module
        next(iterator)  # at least one template/module
        del iterator

        context.adapt_templates(lang_dst)
        context.close_ctx()

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


def get_output_file_modules(source_dir: Path, lang_src: str, lang_dst: str, snapshot: str) -> Path:
    return source_dir.parent / lang_dst / lang_src / f"modules-{snapshot}.sqlite"


def main(locale: str) -> int:
    """Entry point."""

    start = monotonic()
    lang_src, lang_dst = utils.guess_locales(locale)

    source_dir = get_source_dir(lang_src)
    if not (input_file := get_latest_xml_file(source_dir)):
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
