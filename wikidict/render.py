"""Render templates from raw data."""

from __future__ import annotations

import dataclasses
import json
import logging
import multiprocessing
import os
import re
import sys
import warnings
from collections import defaultdict
from contextlib import suppress
from datetime import timedelta
from functools import partial
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING, Any, cast

import wikitextparser as wtp
import wikitextparser._spans
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from . import context, lang, utils
from .stubs import Definition, Definitions, Word, Words

if TYPE_CHECKING:
    from collections.abc import Callable

    from .stubs import Definitions, SubDefinition


# As stated in wikitextparser._spans.parse_pm_pf_tl():
#   If the byte_array passed to parse_to_spans contains n WikiLinks, then
#   this function will be called n + 1 times. One time for the whole byte_array
#   and n times for each of the n WikiLinks.
#
# We do not care about links, let's speed-up the all process by skipping the n times call.
# Doing that is a ~30% optimization.
wikitextparser._spans.WIKILINK_PARAM_FINDITER = lambda *_: ()


Sections = dict[str, list[wtp.Section]]

# To list all unhandled sections:
#    DEBUG_SECTIONS=1 python -m wikidict LOCALE --render | sort -u >out.log
#
# To make words using a given section to fail:
#    DEBUG_SECTIONS="SECTION" python -m wikidict LOCALE --render
# Example with the RO dict, and the "{{unități}}" section:
#    DEBUG_SECTIONS="{{unități}}" python -m wikidict ro --render
DEBUG_SECTIONS = os.environ.get("DEBUG_SECTIONS", "0")

# To list all unhandled words:
#    DEBUG_EMPTY_WORDS=1 python -m wikidict LOCALE --render >out.log 2>&1
DEBUG_EMPTY_WORDS = "DEBUG_EMPTY_WORDS" in os.environ

# To log all words for each process in order to be able to catch problematic words in a second time:
#    DEBUG_LUA=1 python -m wikidict LOCALE --render > LOG_FILE 2>&1
#    tail -f LOG_FILE
#    (and when the ouput hangs, hit CTRL+C, multiple times if needed)
#    python log-analyzer.py LOG_FILE
DEBUG_LUA = int(os.getenv("DEBUG_LUA", "0")) > 0

log = logging.getLogger(__name__)


def get_ignored_terms(lang_src: str, lang_dst: str) -> set[str]:
    ignored_terms = set(lang.definitions_to_ignore[lang_dst])
    ignored_terms.update(lang.variant_templates[lang_dst])
    return {term.lower() for term in ignored_terms}


def find_definitions(
    word: str,
    parsed_sections: Sections,
    lang_src: str,
    lang_dst: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
) -> Definitions:
    """Find all definitions, without eventual subtext."""
    definitions: Definitions = defaultdict(list)

    for pos, sections in parsed_sections.items():
        for section in sections:
            if pos_defs := find_section_definitions(
                word, section, lang_src, lang_dst, templates_status=templates_status
            ):
                target_pos = definitions[pos]
                for pos_def in pos_defs:
                    if pos_def not in target_pos:
                        target_pos.append(pos_def)

    # Move notes below definitions
    if lang_src == "en" and "Usage Note" in definitions:
        definitions["Usage Note"] = definitions.pop("Usage Note")
    elif lang_src == "nl" and "Opmerkingen" in definitions:
        definitions["Opmerkingen"] = definitions.pop("Opmerkingen")

    return dict(definitions)


def es_replace_defs_list_with_numbered_lists(
    lst: wtp.WikiList,
    *,
    regex_item: re.Pattern[str] = re.compile(
        r"(^|\\n);\d+[ |:]+",  # `;1:`
        flags=re.MULTILINE,
    ),
    regex_subitem: re.Pattern[str] = re.compile(
        r"(^|\\n):;\s*[a-z]:+\s+",  # `:;a:`
        flags=re.MULTILINE,
    ),
) -> str:
    """
    ES uses definition lists, not well supported by the parser...
    replace them by numbered lists.
    """
    res = regex_item.sub(r"\1# ", lst.string)
    return regex_subitem.sub(r"\1## ", res)


def find_section_definitions(
    word: str,
    section: wtp.Section,
    lang_src: str,
    lang_dst: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
) -> list[Definition]:
    """Find definitions from the given *section*, with eventual sub-definitions."""
    definitions: list[Definition] = []

    if lang_src == "es":
        if section.title.lstrip().lower().startswith("forma"):
            return []
        if lists := section.get_lists(pattern="[:;]"):
            section.contents = "".join(es_replace_defs_list_with_numbered_lists(lst) for lst in lists)

    ignored_terms = get_ignored_terms(lang_src, lang_dst)

    if lists := section.get_lists(pattern=lang.section_patterns[lang_dst]):
        for a_list in lists:
            for idx, code in enumerate(a_list.items):
                # Ignore some patterns
                if any(ignore_me in code.lower() for ignore_me in ignored_terms):
                    continue

                # Transform and clean the Wikicode
                definition = utils.process_templates(word, code, lang_dst, templates_status=templates_status)

                # Skip empty definitions
                if not definition:
                    continue

                # Keep the definition ...
                if definition not in definitions:
                    definitions.append(definition)

                # ... And its eventual sub-definitions
                subdefinitions: list[SubDefinition] = []
                for sublist in a_list.sublists(i=idx, pattern=lang.sublist_patterns[lang_dst]):
                    if not (items := [item for item in sublist.items if item]):
                        continue

                    if lang_src == "el":
                        # Only keep sublists specific to synonyms
                        if sublist.pattern == "#:":
                            items = [item for item in items if "{{συνων}}" in item]
                        elif sublist.pattern.endswith(":"):
                            continue

                    if lang_src in {"en", "sv"}:
                        # Only keep sublists specific to synonyms
                        if sublist.pattern == "#:":
                            items = [
                                item.replace("Thesaurus:", "")
                                for item in items
                                if "{{syn|" in item or "{{synonym" in item
                            ]
                        elif sublist.pattern.endswith(":"):
                            continue

                    if lang_src == "pt" and sublist.pattern == r"#\*":
                        # We want to keep sublists like "## ..." and "** ...", but not "#* ..."
                        continue

                    for idx2, subcode in enumerate(items):
                        subdefinition = utils.process_templates(
                            word, subcode, lang_dst, templates_status=templates_status
                        )
                        if not subdefinition:
                            continue

                        if subdefinition not in subdefinitions:
                            subdefinitions.append(subdefinition)

                        subsubdefinitions: list[str] = []
                        for subsublist in sublist.sublists(i=idx2, pattern=lang.sublist_patterns[lang_dst]):
                            if lang_src in {"en", "sv"} and subsublist.pattern.endswith(":"):
                                # Only keep sublists specific to synonyms, we do not yet check for them at the lower level
                                continue

                            for subsubcode in subsublist.items:
                                if (
                                    subsubdefinition := utils.process_templates(
                                        word,
                                        subsubcode,
                                        lang_dst,
                                        templates_status=templates_status,
                                    )
                                ) and subsubdefinition not in subsubdefinitions:
                                    subsubdefinitions.append(subsubdefinition)

                        if subsubdefinitions:
                            subdefinitions.append(tuple(subsubdefinitions))

                if subdefinitions:
                    definitions.append(tuple(subdefinitions))

    return definitions


def find_etymology(
    word: str,
    lang_src: str,
    lang_dst: str,
    parsed_section: wtp.Section,
    *,
    templates_status: list[tuple[str, str]] | None = None,
) -> list[Definition]:
    """Find the etymology.

    >>> _ = context.reset("sv")
    >>> context.new_word("word")

    >>> find_etymology("Artur", "sv", "sv", wtp.Section("==Svenska==\\n===Substantiv===\\n#:{{etymologi|Denna namnform kom till Sverige som namn via {{härledning|sv|la|Arthurus, Arturus}}, möjligen av kymriska ''[[arth]]'' (\\"björn\\"), av {{härledning|sv|cel-uce|*artos|björn}}.\\nParallellt med det keltiska ursprunget har två andra teorier framförts: antingen av ett romerskt släktnamn (Artorius), och/eller ett nordiskt mansnamn, ''[[Arnþor]]'' (\\"Arntor\\"), sammansatt av ''Ar(i)n-'' (\\"örn\\") och ''‑tor'' (\\"dunder, åska\\").}}"))
    ['Denna namnform kom till Sverige som namn via latinska&nbsp;<i>Arthurus, Arturus</i>, möjligen av kymriska <i>arth</i> ("björn"), av urkeltiska&nbsp;<i>*artos</i>&nbsp;(”björn”).Parallellt med det keltiska ursprunget har två andra teorier framförts: antingen av ett romerskt släktnamn (Artorius), och/eller ett nordiskt mansnamn, <i>Arnþor</i> ("Arntor"), sammansatt av <i>Ar(i)n-</i> ("örn") och <i>‑tor</i> ("dunder, åska").']
    """

    def get_items(patterns: tuple[str, ...], *, skip: tuple[str, ...] | None = None) -> list[str]:
        items: list[str]
        try:
            items = parsed_section.get_lists(pattern=patterns)[0].items
        except IndexError:
            items = [parsed_section.contents]
        else:
            if skip:
                items = [item for item in items if not item.lstrip().lower().startswith(skip)]
        if items:
            ignored_terms = {term.lower() for term in lang.definitions_to_ignore[lang_dst]}
            items = [item for item in items if all(ignore_me not in item.lower() for ignore_me in ignored_terms)]
        return items

    match lang_src:
        case "cs":
            items = []
            for line in parsed_section.contents.splitlines():
                if not line.startswith(("{{", "}}")):
                    items.append(line.lstrip(":;#*"))
        case "da":
            items = get_items(("#", ":"))
        case "de":
            items = get_items(("#", ":"))
        case "el":
            items = get_items((": ", "#"))
        case "en":
            items = []
            for item in get_items(("",), skip=("===etymology", "{{pie root")):
                if "{{zh-x" in item or "{{zh-q" in item:
                    item = item.replace("collapsed=y", "collapsed=n")
                    item = utils.clean(context.expand(item, "en"))
                items.append(item)
        case "eo":
            items = get_items((":", "#"))
        case "es":
            items = get_items((r";\d",), skip=("=== etimología",))
        case "fr":
            definitions: list[Definition] = []
            tables = parsed_section.tables
            tableindex = 0
            ignored_terms = get_ignored_terms(lang_src, lang_dst)
            for section in parsed_section.get_lists():
                for idx, section_item in enumerate(section.items):
                    if any(ignore_me in section_item.lower() for ignore_me in ignored_terms):
                        continue
                    if section_item == ' {| class="wikitable"':
                        phrase = utils.table2html(word, lang_dst, tables[tableindex])
                        definitions.append(phrase)
                        tableindex += 1
                    else:
                        definitions.append(
                            utils.process_templates(word, section_item, lang_dst, templates_status=templates_status)
                        )
                        subdefinitions: list[SubDefinition] = []
                        for sublist in section.sublists(i=idx):
                            subdefinitions.extend(
                                utils.process_templates(word, subcode, lang_dst, templates_status=templates_status)
                                for subcode in sublist.items
                            )
                        if subdefinitions:
                            definitions.append(tuple(subdefinitions))
            return definitions
        case "it":
            items = get_items(("",), skip=("=== {{etim",))
        case "ja":
            items = get_items(("#", r"\*"))
        case "jbo":
            items = get_items(("",), skip=("===vlakra", "=== vlakra"))
        case "nl":
            items = get_items((r"\*",))
        case "no":
            items = get_items(("#", ":", r"\*"))
        case "pl":
            items = get_items((r":[ ]*\(\d+\.\d+\)", r":[ ]*\(\d+\.\d+-\d+\)", ":"))
        case "pt":
            items = get_items(("#", r"[:]", r"\*"))
        case "ro":
            items = get_items(("#", r"\*"))
        case "sv":
            # Remove the leading template name, and trailing `}}`
            items = [
                tpl.__str__()[len("{{etymologi|") : -2] for tpl in parsed_section.templates if tpl.name == "etymologi"
            ]
        case "th":
            items = []
            for line in parsed_section.contents.splitlines():
                if line.startswith("#:"):
                    continue
                items.append(line.lstrip("#"))
        case "tr":
            items = get_items(("#", ":"))
        case "uk":
            items = []
            for line in parsed_section.contents.splitlines():
                items.append(line.lstrip(":;#*"))
        case "zh":
            items = []
            for line_ in parsed_section.contents.splitlines():
                line = line_.lstrip(":;#*")
                if "{{zh-x" in line or "{{zh-q" in line:
                    item = line.replace("collapsed=y", "collapsed=n")
                    item = utils.clean(context.expand(item, "zh"))
                items.append(line)
        case _:
            items = [parsed_section.contents]

    etyms = [
        etyl.replace("<br/>", "") if lang_src == "jbo" else etyl
        for item in items
        if (etyl := utils.process_templates(word, item, lang_dst, templates_status=templates_status)) and len(etyl) > 1
    ]

    # Do not keep incomplete etymologies
    if lang_src in {"el", "en", "es", "ru", "uk"}:
        useless = {
            "el": {f"<b>{word}</b> &lt;"},
            "en": {
                "Abbreviations.",
                "See",
                "See.",
                "See further at etymology 1.",
                "Variant forms.",
                "Unknown",
            },
            "es": {
                "<i>Si puedes, incorpórala: ver cómo</i>.",
            },
            "ru": {"??", "Из ??", "От", "От ??", "Происходит от", "Происходит от ??", "Происходит от&nbsp;??"},
            "uk": {"Від ?", "Від ??"},
        }.get(lang_src, set())
        etyms = [etym for etym in etyms if etym not in useless]

    return etyms  # type: ignore[return-value]


def _find_pronunciations(top_sections: list[wtp.Section], lang_src: str, lang_dst: str) -> list[str]:
    """Find pronunciations."""
    results = []
    func = lang.find_pronunciations[lang_src]
    for top_section in top_sections:
        if result := func(top_section.contents, lang_dst):
            results.extend(result)
    return utils.unique(results)


def section_title(section: wtp.Section) -> str:
    title = section.title
    return title.replace(" ", "").lower().strip() if title else ""


def find_all_sections(
    code: str, lang_src: str, lang_dst: str
) -> tuple[list[wtp.Section], list[tuple[str, wtp.Section]]]:
    """Find all sections holding definitions."""
    parsed = wtp.parse(code)
    all_sections: list[tuple[str, wtp.Section]] = []
    level = lang.section_level[lang_dst]
    head_sections = tuple(hs.replace(" ", "") for hs in lang.head_sections[lang_dst])

    # Add fake section for etymology if in the leading part
    if lang_src == "ca":
        etyl_l_sections = lang.etyl_section[lang_dst]
        for leading_part in parsed.get_sections(include_subsections=False, level=level):
            if section_title(leading_part) not in head_sections:
                continue

            all_sections.extend(
                (
                    etyl_l_sections[0],
                    wtp.Section(f"=== {etyl_l_sections[0]} ===\n{line}"),
                )
                for line in leading_part.contents.split("\n")
                if line.startswith(etyl_l_sections)
            )

    # Get interesting top sections
    top_sections = [section for section in parsed.get_sections(level=level) if section_title(section) in head_sections]

    # Get all sections without any filtering
    all_sections.extend(
        (section.title.strip(), section)
        for top_section in top_sections
        for sublevel in lang.section_sublevels[lang_dst]
        for section in top_section.get_sections(include_subsections=False, level=sublevel)
    )

    return top_sections, all_sections


def prettify_pos(section: wtp.Section, lang_src: str, lang_dst: str) -> str:
    section_pos = str(section.title).strip().lower()

    if lang_src == "en" and section_pos.startswith("etymology"):
        # Most of the time, definitions are symbols outside a subsection, like in the "wa" word
        section_pos = "symbol"
    elif lang_src == "es" and section_pos.startswith("etimología"):
        # Well, lets just put those elsewhere
        section_pos = "sustantivo"
    elif lang_src == "lt":
        section_pos = section_pos.strip("'")
    elif lang_src == "pt" and "etimologia" in section_pos:
        # Well, lets just put those elsewhere
        section_pos = "substantivo"

    pretty_pos = utils.format_pos(lang_src, section_pos)

    # A potential gender, specified in the section content, is merged into the current POS ("Noun" becomes "Noun f.")
    if pretty_pos != "Trans" and (genders := lang.find_genders[lang_src](section.contents, lang_dst)):
        pretty_pos += f"|{', '.join(f'{g}.' for g in genders)}"

    return pretty_pos


def find_sections(word: str, code: str, lang_src: str, lang_dst: str) -> tuple[list[wtp.Section], Sections]:
    """Find the correct section(s) holding the current locale definition(s)."""
    ret = defaultdict(list)
    wanted = lang.sections[lang_dst]
    etyl_section = lang.etyl_section[lang_dst]
    top_sections, all_sections = find_all_sections(code, lang_src, lang_dst)
    current_genders: list[str] = []
    current_pos = ""

    if lang_src == "de":
        # DE sets the eventual gender in the top-level section
        current_genders = lang.find_genders[lang_src](top_sections[0].contents, lang_src)
    elif lang_src in {"ru", "uk"}:
        # Genders are found in inflections
        current_genders = lang.find_genders[lang_src](top_sections[0].contents, lang_src)

    for title, section in all_sections:
        title = title.lower()
        if lang_src == "lt":
            title = title.strip("'")

        if lang_src == "de" and section.level == 3:
            current_pos = "/".join(re.findall(r"\{\{\w+\|([^|]+)\|\w+\}\}", title))
            continue

        # Filter on interesting sections
        if title.startswith(wanted):
            if lang_src == "de":
                if title in etyl_section:
                    pos = title
                else:
                    current_pos = current_pos or title
                    if "synonyme" in title:
                        current_pos = "synonyme"
                    pos = utils.format_pos("de", current_pos)
                    if current_genders:
                        pos += f"|{', '.join(f'{g}.' for g in current_genders)}"
            elif title in etyl_section:
                pos = title
            else:
                pos = prettify_pos(section, lang_src, lang_dst)
                if lang_src in {"ru", "uk"} and current_genders and "|" not in pos:
                    pos += f"|{', '.join(f'{g}.' for g in current_genders)}"
            ret[pos].append(section)
        elif DEBUG_SECTIONS == "1":
            print(f"Title section rejected: {title!r} {word=}", flush=True)
        elif DEBUG_SECTIONS == title:
            assert 0  # Break the rendering to report the word as an error and be able to look into it

    return top_sections, ret


def add_potential_variant(
    word: str,
    tpl: str,
    locale: str,
    variants: list[str],
    *,
    repl: Callable[[str, str], str] = re.compile(r"(</?[^>]+>)").sub,
    is_reverse_variant: bool = False,
) -> None:
    """
    >>> _ = context.reset("fr")
    >>> context.new_word("word")

    Ensure a variant identical to the word is not taken into account:
    >>> variants_lst = []
    >>> add_potential_variant("19e", "{{fr-rég|diz.nœ.vjɛm|s=19{{e}}|p=19{{e|es}}}}", "fr", variants_lst)
    >>> variants_lst
    []

    Ensure HTML tags are stripped from variants:
    >>> variants_lst = []
    >>> add_potential_variant("19es", "{{fr-rég|diz.nœ.vjɛm|s=19{{e}}|p=19{{e|es}}}}", "fr", variants_lst)
    >>> variants_lst
    ['19e']

    Ensure false positives are taken into account:
    >>> variants_lst = []
    >>> add_potential_variant("401(k)s", "{{fr-rég|401(k)s}}", "fr", variants_lst)
    >>> variants_lst
    ['401(k)']

    Ensure variants with special templates are properly taken into account:
    >>> variants_lst = []
    >>> add_potential_variant("Ires", "{{fr-accord-mixte|ms=Ier{{!}}I{{er}}}}", "fr", variants_lst)
    >>> variants_lst
    ['Ier']

    [NL] We do allow some special parenthesis
    >>> variants_lst = []
    >>> add_potential_variant("ijzerIIIfosfaten", "{{noun-pl|ijzer(III)fosfaat}}", "nl", variants_lst)
    >>> variants_lst
    ['ijzer(III)fosfaat']
    """
    if (variant := utils.process_templates(word, tpl, locale, variant_only=True)) and (
        variant_cleaned := repl("", variant)
    ) != word:
        # Example of false positive we try to prevent in the condition:
        #    [DE] word="Halles (Saale)" variant="Halle (Saale)"
        #    [EN] word="401(k)s"        variant="401(k)"
        if (
            any(char in variant_cleaned for char in "<>|={}")
            or any(char in variant_cleaned for char in "()")
            and all(char not in word for char in "()")
            and not (locale == "nl" and re.findall(r"\b\(I*\)\b", variant_cleaned))
        ):
            kind = "variant"
            if is_reverse_variant:
                kind = f"reverse {kind}"
            log.warning("Potential %s issue: %r → %r for word=%r", kind, variant, variant_cleaned, word)
            return
        variants.append(variant_cleaned)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # Keep interesting sections only
    if not (code := utils.extract_relevant_sections(code, locale)):
        return ""

    code = context.clean_html_input(code, locale)
    return lang.adjust_wikicode[locale](code, locale, templates_status=templates_status, word=word)  # type: ignore[no-any-return]


def parse_word(
    word: str,
    code: str,
    locale: str,
    *,
    force: bool = False,
    templates_status: list[tuple[str, str]] | None = None,
) -> Word | None:
    """Parse *code* Wikicode to find word details.
    *force* can be set to True to force the pronunciation guessing.
    It is disabled by default to speed-up the overall process, but enabled when
    called from `get_word.get_and_parse_word()`.
    """
    # Init the Lua interpreter for this word
    if DEBUG_LUA:
        log.info(word)
    context.new_word(word)

    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)

    # Fast path: stop right now when nothing interesting is found for this word
    if not (code := adjust_wikicode(code, lang_dst, templates_status=templates_status, word=word)):
        return None

    top_sections, parsed_sections = find_sections(word, code, lang_src, lang_dst)
    prons = []
    etymology = []
    etymology_sections: list[wtp.Section] = []
    definitions: Definitions = {}
    variants: list[str] = []
    reverse_variants: list[str] = []

    # Etymology (pre-select sections)
    if lang_src != "sv" and parsed_sections:
        for section in lang.etyl_section[lang_dst]:
            etymology_sections.extend(
                wtp.Section(etyl_data.__str__()) for etyl_data in parsed_sections.pop(section, [])
            )

    # Definitions
    if parsed_sections:
        definitions = find_definitions(word, parsed_sections, lang_src, lang_dst, templates_status=templates_status)

    # Variants
    if parsed_sections:
        interesting_templates = lang.variant_templates[lang_dst]
        interesting_templates_reverse = lang.reverse_variant_templates[lang_dst]
        for parsed_section in parsed_sections.values():
            for parsed in parsed_section:
                parsed_title = (parsed.title or "").strip()
                for tpl in parsed.templates:
                    tpl = str(tpl)
                    if lang_src == "es" and tpl in parsed_title:
                        # [ES] `=== {{verbo transitivo|en}} ===` section title seen as a variant template
                        continue
                    if tpl.startswith(interesting_templates):
                        add_potential_variant(word, tpl, lang_dst, variants)
                    elif tpl.startswith(interesting_templates_reverse):
                        add_potential_variant(word, tpl, lang_dst, reverse_variants, is_reverse_variant=True)
        if variants:
            variants = sorted(set(variants))
        if reverse_variants:
            reverse_variants = sorted(set(reverse_variants))

    # Some words have no head sections but only a list of definitions at the root of the "top" section.
    # Sometimes, there will be a section for synonyms, and we still need to check for top-section-less data.
    if (lang_src == "no" and (not definitions or (len(definitions) == 1 and "Synonymer" in definitions))) or (
        lang_src == "pt"
        and (not variants and not reverse_variants)
        and (
            not definitions
            or (
                len(definitions) == 1
                and any(syn in definitions for syn in ("Sinónimo", "Sinónimos", "Sinônimo", "Sinônimos"))
            )
        )
    ):
        top_section = top_sections[0]
        top_section.title = "top"
        section_pos = prettify_pos(top_section, lang_src, lang_dst)
        definitions |= find_definitions(
            word, {section_pos: top_sections}, lang_src, lang_dst, templates_status=templates_status
        )

    if definitions or force:
        for pron in (prons := _find_pronunciations(top_sections, lang_src, lang_dst)).copy():
            if "{{" in pron:
                log.warning("Malformed pronunciation in %r: %r", word, pron)
                prons.remove(pron)
        definitions.pop("Trans", None)

    # Etymology
    if definitions:
        if lang_src == "sv":
            for top in top_sections:
                etymology.extend(find_etymology(word, lang_src, lang_dst, top, templates_status=templates_status))
        elif etymology_sections:
            for etyl_data in etymology_sections:
                etymology.extend(find_etymology(word, lang_src, lang_dst, etyl_data, templates_status=templates_status))

        if etymology:
            # Remove duplicates
            seen = set()
            etymology = [e for e in etymology if not (e in seen or seen.add(e))]  # type: ignore[func-returns-value]

    return Word(prons, [], etymology, definitions, variants, reverse_variants)


def render_word(
    w: tuple[str, str],
    results: Words,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
) -> None:
    word, code = w
    try:
        details = parse_word(word, code, locale, templates_status=templates_status)
    except Exception:
        log.exception("ERROR with %r", word)
    else:
        if details and (details.definitions or details.variants or details.reverse_variants):
            results[word] = details

    if DEBUG_EMPTY_WORDS:
        print(f"Empty {word = }", flush=True)

    if DEBUG_LUA:
        log.info("Job done.")


def init_worker(locale: str) -> None:
    utils.setup_logging(*utils.guess_locales(locale, use_log=False))
    if not context.setup_modules_db(locale):
        sys.exit(1)


def render(
    in_words: list[tuple[str, str]],
    redirections: list[tuple[str, str]],
    locale: str,
    workers: int,
    *,
    parallelism_start_method: str = "spawn",
) -> Words:
    if parallelism_start_method == "fork":
        warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*may lead to deadlocks in the child.*")

    if multiprocessing.get_start_method() != parallelism_start_method:
        multiprocessing.set_start_method(parallelism_start_method, force=True)

    manager = multiprocessing.Manager()
    managed_results = manager.dict()
    results: Words = cast(Words, managed_results)
    managed_template_status = manager.list()
    templates_status: list[tuple[str, str]] = cast(list[tuple[str, str]], managed_template_status)

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        transient=False,
    ) as progress:
        lang_src, lang_dst = utils.guess_locales(locale, use_log=False)
        main_task = progress.add_task(
            f"[cyan][{lang_src.upper()}-{lang_dst.upper()}] Rendering words",
            total=len(in_words),
        )
        with multiprocessing.Pool(processes=workers, initializer=init_worker, initargs=(locale,)) as pool:
            for _ in pool.imap_unordered(
                partial(render_word, results=results, locale=locale, templates_status=templates_status),
                in_words,
                chunksize=1000,
            ):
                progress.advance(main_task)

        # Final update to ensure we show 100%
        progress.update(
            main_task,
            completed=len(in_words),
            description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Rendered words [green]✓[/green]",
        )

        utils.check_for_templates_status(managed_template_status._getvalue())

        results_final: Words = managed_results._getvalue()

        redirection_task = progress.add_task(
            f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Adding redirections",
            total=len(redirections),
        )
        redirection_count = 0
        for word, redirect_to in redirections:
            with suppress(KeyError):
                results_final[redirect_to].reverse_variants.append(word)
                redirection_count += 1
                progress.update(redirection_task, completed=redirection_count)
        progress.update(
            redirection_task,
            total=redirection_count,
            description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Added redirections [green]✓[/green]",
        )

        if lang.reverse_variant_templates[lang_dst]:
            reverse_task = progress.add_task(
                f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Handling reverse variants",
                total=len(results),
            )

            for word, details in results.items():
                if not details.reverse_variants:
                    progress.advance(reverse_task)
                    continue

                for form in details.reverse_variants:
                    if form.startswith("trad:"):
                        continue
                    try:
                        results_final[form].variants = sorted({*results_final[form].variants, word})
                    except KeyError:
                        results_final[form] = Word(variants=[word])
                progress.advance(reverse_task)

            progress.update(
                reverse_task,
                description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Handled reverse variants [green]✓[/green]",
            )

        hook_after(results_final, progress)

    return results_final


def save(output: Path, words: Words) -> None:
    """Persist data."""

    if not words:
        log.warning("No words to save.")
        return

    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o: object) -> Any:
            if dataclasses.is_dataclass(o):
                # Skip falsy values (empty list, `is_variant` being only defined/updated in/for --convert)
                return dataclasses.asdict(o, dict_factory=lambda x: {k: v for (k, v) in x if v})  # type: ignore[arg-type]
            return super().default(o)

    output.parent.mkdir(exist_ok=True, parents=True)
    with output.open(mode="w", encoding="utf-8") as fh:
        json.dump(words, fh, cls=EnhancedJSONEncoder, ensure_ascii=False, indent=2)
    log.info("Saved %s words into %s", f"{len(words):,}", output)


def get_source_dir(lang_src: str, lang_dst: str) -> Path:
    return Path(os.getenv("CWD", "")) / "data" / lang_dst / lang_src


def get_output_file(source_dir: Path, snapshot: str) -> Path:
    return source_dir / f"data-{snapshot}.json"


def load_words(lang_src: str, lang_dst: str) -> tuple[str, list[tuple[str, str]], list[tuple[str, str]]]:
    if lang_src == "de":
        # It is not possible to use a regexp matcher
        def has_interesting_sections(wikicode: str) -> bool:
            wikicode = wikicode.lower()
            return any(hs in wikicode for hs in lang.head_sections[lang_dst])
    else:
        has_interesting_sections = re.compile(
            rf"^={{1,2}}[ ]*({'|'.join(hs.replace('{', r'\{').replace('|', r'\|') for hs in lang.head_sections[lang_dst])})",
            flags=re.IGNORECASE | re.MULTILINE,
        ).search  # type: ignore[assignment]

    ctx = context.get_ctx()

    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"[cyan][{lang_src.upper()}-{lang_dst.upper()}] Loading words", total=None)
        words = [item for item in ctx.fetch_words() if has_interesting_sections(item[1])]

        # Final update to ensure we show 100%
        progress.update(
            task,
            total=100,
            completed=100,
            description=f"[magenta][{lang_src.upper()}-{lang_dst.upper()}] Loaded words [green]✓[/green]",
        )

    redirections = list(ctx.fetch_redirections())
    snapshot = ctx.snapshot
    context.close_ctx()
    return snapshot, words, redirections


def hook_after(words: Words, progress: Progress) -> None:
    pass


def main(locale: str, *, workers: int = multiprocessing.cpu_count(), parallelism_start_method: str = "spawn") -> int:
    """Entry point."""

    start = monotonic()

    if not context.setup_modules_db(locale):
        log.error("No dump found. Run with --parse first ... ")
        return 1

    lang_src, lang_dst = utils.guess_locales(locale)
    snapshot, in_words, redirections = load_words(lang_src, lang_dst)
    if not in_words:
        log.error("No word found!")
        return 1

    log.info("Rendering ...")
    workers = workers or multiprocessing.cpu_count()
    words = render(
        in_words,
        redirections,
        locale,
        workers,
        parallelism_start_method=parallelism_start_method,
    )

    ret = 1
    if words:
        source_dir = get_source_dir(lang_src, lang_dst)
        output = get_output_file(source_dir, snapshot)
        save(output, words)
        ret = 0

    log.info("Render done in %s!", timedelta(seconds=monotonic() - start))
    return ret
