"""Parse and store raw Wiktionary data."""

from __future__ import annotations

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
from .lang.da.langs import langs as langs_da

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
    module_matcher: Callable[[str], Iterator[re.Match[str]]],
    template_matcher: Callable[[str], Iterator[re.Match[str]]],
    appendix_matcher: Callable[[str], Iterator[re.Match[str]]],
    *,
    is_monolingual: bool = False,
) -> tuple[str, str]:
    """Parse the XML `element` to retrieve interesting Wiktionary raw data."""
    empty = "", ""

    if is_monolingual:
        # Module
        if title := next(module_matcher(element), None):
            if not title[1].lower().endswith(constants.MODULES_TO_IGNORE):
                body, redirect_to = None, None
                if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
                    redirect_to = redirect[1]
                elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
                    body = unescape(text[1], entities=constants.HTML_REPL_BODY)
                if body or redirect_to:
                    page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
                    context.new_page(page, 828, body, redirect_to)
                    return empty

        # Template
        elif title := next(template_matcher(element), None):
            if not title[1].lower().endswith(constants.MODULES_TO_IGNORE):
                body, redirect_to = None, None
                if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
                    redirect_to = redirect[1]
                elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
                    body = unescape(text[1], entities=constants.HTML_REPL_BODY)
                if body or redirect_to:
                    page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
                    context.new_page(page, 10, body, redirect_to)
                    return empty

        # Appendix
        elif title := next(appendix_matcher(element), None):
            body, redirect_to = None, None
            if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
                redirect_to = redirect[1]
            elif text := next(RE_TEXT(element, pos=element.find("<text")), ""):
                body = unescape(text[1], entities=constants.HTML_REPL_BODY)
            if body or redirect_to:
                page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
                context.new_page(page, 100, body, redirect_to)
                return empty

    # Word
    if title := next(RE_TITLE_WORD(element), None):
        # Redirection
        if redirect := next(RE_REDIRECT(element, endpos=element.find("<revision")), None):
            page = unescape(title[1], entities=constants.HTML_REPL_TITLE)
            redirect_to = unescape(redirect[1], entities=constants.HTML_REPL_TITLE)
            context.new_page(page, 0, None, redirect_to)
            return empty

        # Actual word
        if text := next(RE_TEXT(element, pos=element.find("<text", title.endpos)), ""):
            return title[1], text[1]

    # No Wikicode; unfinished page; no interesting head section; a foreign word, or a module/template.
    return empty


def process(file: Path, locale: str) -> bool:
    """Process the big XML file and retain only information we are interested in."""
    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)

    utils.setup_logging(lang_src, lang_dst)

    word_count = 0
    log.info("Processing %s for destination lang %r ...", file, lang_dst)

    module_matcher = re.compile(rf"<title>({lang.module_trans[lang_dst]}:[^<]+)</title>").finditer
    template_matcher = re.compile(rf"<title>({lang.template_trans[lang_dst]}:[^<]+)</title>").finditer
    appendix_matcher = re.compile(rf"<title>({lang.appendix_trans[lang_dst]}:[^<]+)</title>").finditer

    if is_monolingual := lang_src == lang_dst:
        context.setup_modules_db(locale, db_already_setup=False)

    for element in xml_iter_parse(file, locale):
        title, code = xml_parse_element(
            element,
            module_matcher,
            template_matcher,
            appendix_matcher,
            is_monolingual=is_monolingual,
        )
        if not title or not code or (lang_dst == "en" and title[:19] == "Unsupported titles/"):
            continue

        title = unescape(title, entities=constants.HTML_REPL_TITLE)
        body = unescape(code, entities=constants.HTML_REPL_BODY)

        # Header section adjustments may be required to search for specific locale in --render
        match lang_dst:
            case "da":
                # `{{=da=}}` → `=={{da}}==`
                body = re.sub(r"\{\{=(\w+)=\}\}", r"=={{\1}}==", body, flags=re.MULTILINE)

                # Transform sub-locales into their own section to prevent mixing stuff
                # `{{-da-}}` → `=={{da}}==`
                # `{{-mul-}}` → `=={{mul}}==`
                body = re.sub(rf"\{{\{{-({'|'.join(langs_da)})-\}}\}}", r"=={{\1}}==", body, flags=re.MULTILINE)
            case "de":
                # `== CIA ({{Sprache|Deutsch}}) ==` → `== {{Sprache|Deutsch}} ==`
                body = re.sub(r"^==\s*.*\((\{\{Sprache\|[^}]+\}\})\)\s*==", r"== \1 ==", body, flags=re.MULTILINE)
            case "ja":
                if "{{kanji header" in body:
                    body = f"=={{{{kanji}}}}==\n{body}"

        context.new_page(title, 0, body, None)
        word_count += 1

    if is_monolingual:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(complete_style="green", finished_style="bold green"),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(f"[cyan][{lang_src.upper()}-{lang_dst.upper()}] Adapting templates", total=None)
            context.adapt_templates(lang_dst)

            # Final update to ensure we show 100%
            progress.update(
                task,
                total=100,
                completed=100,
                description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Adapted templates [green]✓[/green]",
            )

    context.close_ctx()
    return word_count > 1


def get_latest_dump_file(source_dir: Path) -> Path | None:
    """Get the name of the last pages-*.xml.bz2 file."""
    files = list(source_dir.glob(f"pages-{'[0-9]' * 8}.xml.bz2"))
    return sorted(files)[-1] if files else None


def get_latest_xml_file(source_dir: Path) -> Path | None:
    """Get the name of the last pages-*.xml file."""
    files = list(source_dir.glob(f"pages-{'[0-9]' * 8}.xml"))
    return sorted(files)[-1] if files else None


def get_source_dir(lang_src: str) -> Path:
    return Path(os.getenv("CWD", "")) / "data" / lang_src


def get_output_file(source_dir: Path, snapshot: str) -> Path:
    return source_dir / f"pages-{snapshot}.sqlite"


def main(locale: str) -> int:
    """Entry point."""

    start = monotonic()
    lang_src, _ = utils.guess_locales(locale)

    source_dir = get_source_dir(lang_src)
    if not (input_file := get_latest_xml_file(source_dir)):
        log.error("No dump found. Run with --download first ... ")
        return 1

    ret = 0
    output = get_output_file(source_dir, input_file.stem[6:14])
    if output.is_file():
        log.info("Already parsed into %s", output)
    elif process(input_file, locale):
        # Do not keep the (big) XML file
        input_file.unlink()
    else:
        ret = 1

    log.info("Parse done in %s!", timedelta(seconds=monotonic() - start))
    return ret
