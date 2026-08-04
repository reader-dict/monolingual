"""Polish language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://pl.wiktionary.org/wiki/Specjalna:Losowa_strona"

module_trans = "Moduł"
template_trans = "Szablon"

float_separator = ","
thousands_separator = " "

head_sections = ("polski", "międzynarodowe")
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


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "pl")
    []
    >>> find_genders("{{gender|rodzaj żeński}}", "pl")
    ['ż']
    """
    pattern = re.compile(r"\{\{gender\|rodzaj (\w+)\}\}")
    return [gender[0] for gender in utils.unique(pattern.findall(code))]


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "pl")
    []
    >>> find_pronunciations("{{IPA3|ˈpʲjɛ̃ŋknɨ}}", "pl")
    ['[ˈpʲjɛ̃ŋknɨ]']
    >>> find_pronunciations("{{IPA3|ˈ[[a]][[d]][[r]][[ɛ]][[s]]}}", "pl")
    []
    """
    pattern = re.compile(r"\{\{IPA\d*\|([^}]+)")
    return [f"[{pron}]" for pron in utils.unique(pattern.findall(code)) if "[" not in pron]


def pos_and_gender(matches: re.Match[str]) -> str:
    if "," in (match := matches[2]):
        pos, gender = match.split(",", 1)
        return f"==={pos.strip()}===\n{{{{gender|{gender.strip()}}}}}"

    if match.startswith("{"):
        match = context.expand(match, "pl").replace("<i>", "").replace("</i>", "")
    return f"==={match.strip()}==="


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

    # Extract POS, and gender
    code = re.sub("^(''([^']+)'').*$", pos_and_gender, code, flags=re.MULTILINE)

    # {{synonimy}} → ===synonimy===
    code = re.sub(r"^\{\{(\w+)\}\}", r"===\1===", code, flags=re.MULTILINE)

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
                if variant := re.findall(r"\[\[([^\]]+)\]\]$", line):
                    lines.append(f": (0.0) {{{{flexion|{variant[0]}}}}}")
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
                        tpl_name = tpl_sub[2 : max(0, tpl_sub.find("|")) or tpl_sub.find("}")].strip()
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
