"""Polish language."""

import re
from collections.abc import Callable

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://pl.wiktionary.org/wiki/Specjalna:Losowa_strona"

module_trans = "Moduł"
template_trans = "Szablon"

head_sections = (
    "polski",  # Polish
    "międzynarodowe",  # international
)
section_patterns = (
    r":[ ]*\(\d+\.\d+\)",  # `: (1.1) ...`
    r":[ ]*\(\d+\.\d+-\d+\)",  # `: (1.1–2) ...`
)
subsection_patterns = (r"::[ ]*\(\d+\.\d+\.\d+\)",)  # `:: (1.1.1) ...`
etyl_section = ("etymologia",)
sections = (
    *etyl_section,
    "czasownik",  # verb
    "fraza",  # sentence
    "końcówka",  # ending
    # "litera",  # letter, see #2634
    "morfem",
    "odmiana",  # conjugation
    "partykuła",  # particle
    "przedimek",  # definite article
    # "przykłady",  # examples
    "przyimek",  # preposition
    "przymiotnik",  # adjective
    "przysłówek",  # adverb
    "przysłowie",  # proverb
    "rodzajnik",  # definite article
    "rzeczownik",  # noun
    "skrót",  # abbreviation
    "spójnik",  # conjunction
    "symbol",
    "synonimy",
    # "uwagi",  # notes
    "wykrzyknik",  # exclamation mark
    "zaimek",  # pronoun
)

variant_templates = ("{{flexion",)

reverse_variant_titles = ("{{alternatywna", "{{nieodm-", "{{odmiana-")
reverse_variant_templates = ("{{rev-flexion",)


RE_GENDERS = re.compile(r"\{\{gender\|rodzaj (\w+)\}\}")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "pl")
    []
    >>> find_genders("{{gender|rodzaj żeński}}", "pl")
    ['ż']
    """
    return [gender[0] for gender in utils.unique(RE_GENDERS.findall(code))]


RE_PRONS = re.compile(r"\{\{IPA\d*\|([^}]++)")


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "pl")
    []
    >>> find_pronunciations("{{IPA3|ˈpʲjɛ̃ŋknɨ}}", "pl")
    ['[ˈpʲjɛ̃ŋknɨ]']
    >>> find_pronunciations("{{IPA3|ˈ[[a]][[d]][[r]][[ɛ]][[s]]}}", "pl")
    []
    """
    return [f"[{pron}]" for pron in RE_PRONS.findall(code) if "[" not in pron]


def pos_and_gender(matches: re.Match[str]) -> str:
    if "," in (match := matches[2]):
        pos, gender = match.split(",", 1)
        return f"==={pos.strip()}===\n{{{{gender|{gender.strip()}}}}}"

    if match.startswith("{"):
        match = context.expand(match, "pl").replace("<i>", "").replace("</i>", "")
    return f"==={match.strip()}==="


RE_HEADER = re.compile(r"\{\{(\w++)\}\}")
RE_POS = re.compile(r"''([^',]++)")
RE_DEFINITION = re.compile(r":\s*+\((\d++\.\d++)\)")
RE_SYNONYMS = re.compile(r":\s*+((?:\([\d.,\s–-]++\)[\s,]*+)++)(\S.*+)")
RE_NUMBERS = re.compile(r"(?:(\d++)\.)?(\d++)(?:[–-](?:(\d++)\.)?(\d++))?")


def meaning_numbers(text: str) -> list[str]:
    """
    The meanings that synonyms refer to, or nothing when one of them can't be read.

    >>> meaning_numbers("(1.1-2, 2.1)")
    ['1.1', '1.2', '2.1']
    >>> meaning_numbers("(1.4-5,7)")
    ['1.4', '1.5', '1.7']
    >>> meaning_numbers("(1.1) (2.1)")
    ['1.1', '2.1']
    >>> meaning_numbers("(1.1-1.2)")
    ['1.1', '1.2']
    >>> meaning_numbers("(1.1-3.1)")
    []
    >>> meaning_numbers("(1-2)")
    []
    """
    numbers: list[str] = []
    pos = ""
    for token in filter(None, re.split(r"[\s,()]++", text)):
        if not (match := RE_NUMBERS.fullmatch(token)):
            return []
        # `1.1,3` is `1.1` and `1.3`
        pos = match[1] or pos
        first, last = int(match[2]), int(match[4] or match[2])
        if not pos or match[3] not in {None, pos} or last < first:
            return []
        numbers.extend(f"{pos}.{number}" for number in range(first, last + 1))
    return numbers


def attach_synonyms(code: str) -> str:
    r"""
    Put the synonyms under their meaning, as a sub-definition: `: (1.1) [[trusia]]`.
    The list of a language is kept as it is when one of its lines doesn't give the number of a meaning,
    or gives the one of a meaning that isn't shown: a form of another word goes to the variants, and a part of
    speech like a suffix is left out, so its synonyms would be lost with it.

    >>> attach_synonyms("==polski==\n{{znaczenia}}\n''rzeczownik''\n: (1.1) zwierzę\n''rzeczownik''\n: (2.1) władca\n: (2.2) mężczyzna\n{{synonimy}}\n: (1.1) [[trusia]]\n: (2.1-2) [[kacyk]]\n: (2.1) [[władyka]]\n{{antonimy}}")
    "==polski==\n{{znaczenia}}\n''rzeczownik''\n: (1.1) zwierzę\n: (1.1)# ''syn.:'' [[trusia]]\n''rzeczownik''\n: (2.1) władca\n: (2.1)# ''syn.:'' [[kacyk]]; [[władyka]]\n: (2.2) mężczyzna\n: (2.2)# ''syn.:'' [[kacyk]]\n{{synonimy}}\n{{antonimy}}"
    >>> attach_synonyms("==międzynarodowe==\n{{znaczenia}}\n''symbol''\n: (1.1) litera\n==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n{{synonimy}}\n: (1.1) [[oraz]]")
    "==międzynarodowe==\n{{znaczenia}}\n''symbol''\n: (1.1) litera\n==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n: (1.1)# ''syn.:'' [[oraz]]\n{{synonimy}}"
    >>> attach_synonyms("==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n{{synonimy}}\n: (1.1) [[oraz]]\n: {{gwara}} [[ä]]")
    "==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n{{synonimy}}\n: (1.1) [[oraz]]\n: {{gwara}} [[ä]]"
    >>> attach_synonyms("==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n{{synonimy}}\n: (1.2) [[oraz]]")
    "==polski==\n{{znaczenia}}\n''spójnik''\n: (1.1) i\n{{synonimy}}\n: (1.2) [[oraz]]"
    >>> attach_synonyms("==polski==\n{{znaczenia}}\n''{{forma rzeczownika}}''\n: (1.1) {{lm|pies}}\n{{synonimy}}\n: (1.1) [[kundle]]")
    "==polski==\n{{znaczenia}}\n''{{forma rzeczownika}}''\n: (1.1) {{lm|pies}}\n{{synonimy}}\n: (1.1) [[kundle]]"
    >>> attach_synonyms("==polski==\n{{znaczenia}}\n''przyrostek''\n: (1.1) tworzy nazwy\n{{synonimy}}\n: (1.1) [[-ok]]")
    "==polski==\n{{znaczenia}}\n''przyrostek''\n: (1.1) tworzy nazwy\n{{synonimy}}\n: (1.1) [[-ok]]"
    """
    lines = code.split("\n")
    insert: dict[int, str] = {}
    drop: set[int] = set()

    def attach(definitions: dict[str, int], synonyms: list[int]) -> None:
        texts: dict[str, list[str]] = {}
        for n in synonyms:
            if not (match := RE_SYNONYMS.fullmatch(lines[n])) or not (numbers := meaning_numbers(match[1])):
                return
            if any(number not in definitions for number in numbers):
                return
            for number in numbers:
                texts.setdefault(number, []).append(match[2])
        for number, synonym_texts in texts.items():
            # The `#` after the number makes it a sub-list of the meaning
            insert[definitions[number]] = f": ({number})# ''syn.:'' {'; '.join(synonym_texts)}"
        drop.update(synonyms)

    # Number of a shown meaning: its line
    definitions: dict[str, int] = {}
    synonyms: list[int] = []
    section = ""
    is_shown = False
    for n, line in enumerate(lines):
        if line.startswith("==") and not line.startswith("==="):
            # Each language numbers its own meanings
            attach(definitions, synonyms)
            definitions, synonyms, section, is_shown = {}, [], "", False
        elif header := RE_HEADER.match(line):
            section = header[1]
        elif section == "znaczenia":
            if pos := RE_POS.match(line):
                is_shown = pos[1].strip().lower().startswith(sections)
            elif is_shown and (definition := RE_DEFINITION.match(line)) and definition[1] not in definitions:
                definitions[definition[1]] = n
        elif section == "synonimy" and line.strip():
            synonyms.append(n)
    attach(definitions, synonyms)

    out: list[str] = []
    for n, line in enumerate(lines):
        if n not in drop:
            out.append(line)
        if n in insert:
            out.append(insert[n])
    return "\n".join(out)


RE_CLEANUPS: list[tuple[re.Pattern[str], str | Callable[[re.Match[str]], str]]] = [
    # Extract POS, and gender
    (re.compile(r"(?m)^(''([^']++)'').*$"), pos_and_gender),
    # {{synonimy}} → ===synonimy===
    (re.compile(r"(?m)^\{\{(\w+)\}\}"), "===\\1==="),
]
RE_VARIANT = re.compile(r"\[\[([^\]]++)\]\]$")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("{{znaczenia}}\n''przymiotnik jakościowy''", "pl")
    '===znaczenia===\n===przymiotnik jakościowy==='
    >>> adjust_wikicode("{{znaczenia}}\n''rzeczownik, rodzaj żeński''", "pl")
    '===znaczenia===\n===rzeczownik===\n{{gender|rodzaj żeński}}'
    >>> adjust_wikicode("{{synonimy}}", "pl")
    '===synonimy==='
    """
    has_variants = "''{{forma " in code

    # Synonyms go under their meaning: `: (1.1) [[trusia]]`
    code = attach_synonyms(code)

    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    #
    # Variants
    #

    lines: list[str] = []
    if has_variants:
        in_tpl = False
        for line in code.splitlines():
            if line.startswith("="):
                in_tpl = "forma " in line
                lines.append(line)
            elif in_tpl:
                if variant := RE_VARIANT.search(line):
                    lines.append(f": (0.0) {{{{flexion|{variant[1]}}}}}")
            else:
                lines.append(line)
        code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        lines.clear()
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if any(irvt in line for irvt in interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    for tpl_sub in extract_templates(tpl_code):
                        tpl_name = tpl_sub[2 : max(0, tpl_sub.find("|")) or tpl_sub.find("}")].strip().strip("\u200e")
                        variant_handlers_mod.append_to_reverse_variants(tpl_name)
                        forms = utils.process_templates(
                            word,
                            tpl_sub,
                            locale,
                            templates_status=templates_status,
                            variant_only=True,
                        )
                        lines.extend(f": (0.0) {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                lines.append(line)

        code = "\n".join(lines)

    return code


def extract_templates(templates: str) -> list[str]:
    r"""
    >>> extract_templates(": (1.1-3) {{odmiana-rzeczownik-polski\n|Mianownik lp = książka\n|Dopełniacz lp = książki\n|Celownik lp = książce\n|Biernik lp = książkę\n|Narzędnik lp = książką\n|Miejscownik lp = książce\n|Wołacz lp = książko\n|Mianownik lm = książki\n|Dopełniacz lm = książek\n|Celownik lm = książkom\n|Biernik lm = książki\n|Narzędnik lm = książkami\n|Miejscownik lm = książkach\n|Wołacz lm = książki\n}}")
    ['{{odmiana-rzeczownik-polski|Mianownik lp = książka|Dopełniacz lp = książki|Celownik lp = książce|Biernik lp = książkę|Narzędnik lp = książką|Miejscownik lp = książce|Wołacz lp = książko|Mianownik lm = książki|Dopełniacz lm = książek|Celownik lm = książkom|Biernik lm = książki|Narzędnik lm = książkami|Miejscownik lm = książkach|Wołacz lm = książki}}']
    >>> extract_templates(": (1.4) {{blm}}; {{odmiana-rzeczownik-polski\n|Mianownik lp = książka\n|Dopełniacz lp = książki\n|Celownik lp = książce\n|Biernik lp = książkę\n|Narzędnik lp = książką\n|Miejscownik lp = książce\n|Wołacz lp = książko\n}}")
    ['{{blm}}', '{{odmiana-rzeczownik-polski|Mianownik lp = książka|Dopełniacz lp = książki|Celownik lp = książce|Biernik lp = książkę|Narzędnik lp = książką|Miejscownik lp = książce|Wołacz lp = książko}}']
    """
    res: list[str] = []

    in_tpl = False
    current_template = ""

    for char in list(templates):
        if not in_tpl and char == "{":
            in_tpl = True
        if in_tpl and char != "\n":
            current_template += char
        if char != "}" or len(current_template) <= 4 or current_template.count("{") != current_template.count("}"):
            continue

        res.append(current_template)
        current_template = ""
        in_tpl = False

    return res
