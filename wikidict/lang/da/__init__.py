"""Danish language."""

import re
from functools import lru_cache

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://da.wiktionary.org/wiki/Speciel:RandomRootpage"

module_trans = "Modul"
template_trans = "Skabelon"

section_patterns = ("#", r"\*")
section_sublevels = (3, 4)
head_sections = (
    "{{da}}",
    "{{=da=}}",
    "{{-da-}}",
    "dansk",
    "{{mul}}",
    "{{=mul=}}",
    "{{-mul-}}",
    "tværsprogligt",
)
etyl_section = ("{{etym}}", "{{etym2}}", "etymologi", "etymologi 1", "etymologi 2", "etymologi 3", "etymologi 4")
sections = (
    *etyl_section,
    "adjektiv",
    "adverbium",
    "alternativ form",
    # "bogstav",  # letter, see #2634
    "bøjning",
    "fast udtryk",
    "formelt subjekt",
    "interfiks",
    "interjektion",
    "konjugation",
    "lydord",
    "noun",
    "possessivt pronomen",
    "possessivt pronomen (ejestedord)",
    "prefix",
    "pronomen",
    "proposition",
    "proprium",
    "prœposition",
    "substantiv",
    "symbol",
    "synonymer",
    "sætning",
    "ubestemt prononmen",
    "ubestemt pronomen",
    "ubestemt talord",
    "udtryk",
    "verbum",
    "{{abbr}",
    "{{abr}",
    "{{abr|mul}",
    "{{adj}",
    "{{adv}",
    "{{art}",
    "{{car-num}",
    "{{car-num|mul}",
    "{{conj}",
    "{{contr}",
    "{{dem-pronom}",
    "{{decl}",
    "{{end}",
    "{{expr}",
    "{{frase}",
    "{{interj}",
    "{{lyd}",
    "{{noun}",
    "{{noun2}",
    "{{num}",
    "{{part}",
    "{{pers-pronom}",
    "{{phr}",
    "{{pp}",
    "{{pref}",
    "{{prep}",
    "{{pron}",
    "{{prop}",
    "{{prov}",
    "{{seq-num}",
    "{{sætning}",
    "{{suf}",
    "{{symb}",
    "{{symb|mul}",
    "{{syn}",
    "{{ubest-pronon}",
    "{{verb}",
)

variant_templates = ("{{alternativ stavemåde af", "{{form of", "{{flexion", "{{imperativ af", "{{imperativ form af")

reverse_variant_titles = (
    "{{da-noun",
    "{{da-verb",
)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{definition mangler",
    "{{dm",
    "{{rfe",
    "{{wikipedia",
    "{{Wikipedia",
)


@lru_cache
def cache_pattern(locale: str) -> re.Pattern[str]:
    return re.compile(rf"\{{\{{IPA(?:\|(.*?))?\|lang={locale}\}}\}}")


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", LANG)
    []
    >>> find_pronunciations("{{IPA|/bɛ̜ːˀ/|lang=da}}", LANG)
    ['/bɛ̜ːˀ/']
    >>> find_pronunciations("{{IPA|/fuːl/|[fuːˀl]|lang=da}}", LANG)
    ['/fuːl/']
    """
    pron = next(
        (
            item.replace("[", "/").replace("]", "/")
            for sublist in (cache_pattern(locale).findall(code) or [])
            for item in sublist.split("|")
            if item
        ),
        "",
    )
    return [pron] if pron else []


ALL_FORMS = [
    "bestemt ental af",
    "bestemt flertal af",
    "da-adj-1",
    "da-adj-2",
    "da-noun-1",
    "da-noun-2",
    "da-noun-",
    "da-noun-3",
    "da-noun-4",
    "da-noun-5",
    "da-noun-6",
    "da-noun-7",
    "ental af",
    "ental bestemt af",
    "ental flertal af",
    "flertal af",
    "flertal ubestemt af",
    "genitivform af",
    "genitiv bestemt ental af",
    "genitiv bestemt flertal af",
    "genitiv ental ubestemt af",
    "genitiv ubestemt entalsform af",
    "genitiv ubestemt ental af",
    "genitiv ubestemt flertalsform af",
    "genitiv ubestemt flertal af",
    "imperativ af",
    "nutid af",
    "pluralis af",
    "præsens af",
    "præsens participium af",
    "præteritum participium af",
    "præteritum af",
    "ubestemt ental af",
    "ubestemt flertal af",
]
RE_CLEANUPS = [
    # `=== Alternativ form ===\n* {{l|...}}` → `=== Alternativ form ===\n* {{flexion|...}}`
    (
        re.compile(r"(?m)^(={3,}[ ]*+Alternativ form[ ]*+={3,})\n\* \{\{l\|[^|]++\|([^}]++)\}\}"),
        r"\1\n* {{flexion|\2}}",
    ),
    # {{-avv-|ANY}} → === {{avv}} ===
    (re.compile(r"(?m)^\{\{-(.+)-\|(\w++)\}\}"), r"=== {{\1}} ==="),
    # {{-avv-}} → === {{avv}} ===
    (re.compile(r"(?m)^\{\{-(\w++)-\}\}"), r"=== {{\1}} ==="),
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
    forms: str = r"|".join(ALL_FORMS),
    start: str = rf"^(?:{'|'.join(section_patterns)})\s*+",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("== Dansk ==\n=== Alternativ form ===\n* {{l|da|vørme}}", LANG)
    '== Dansk ==\n=== Alternativ form ===\n* {{flexion|vørme}}'

    >>> adjust_wikicode("=={{da}}==\n{{-avv-|da}}", LANG)
    '=={{da}}==\n=== {{avv}} ==='

    >>> adjust_wikicode("=={{da}}==\n{{-avv-|ANY}}", LANG)
    '=={{da}}==\n=== {{avv}} ==='

    >>> adjust_wikicode("=={{da}}==\n{{-avv-}}", LANG)
    '=={{da}}==\n=== {{avv}} ==='

    >>> adjust_wikicode("=={{da}}==\n*Pluralis af [[tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n#Pluralis af [[tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n#Pluralis af [[tale|tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n#Pluralis af [[tale#Substantiv|tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n# Nutid af [[tale#Verbum|tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n# Flertal af [[tale]]: [[ui]].", LANG)
    '=={{da}}==\n# {{flexion|tale}}'

    >>> adjust_wikicode("=={{da}}==\n# {{flertal af}} [[tale]]", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n# {{flertal af}} '''[[tale]]'''", LANG)
    '=={{da}}==\n# {{flexion|tale}}'
    >>> adjust_wikicode("=={{da}}==\n#''præsens participium af'' '''[[abandonnere]]'''.", LANG)
    '=={{da}}==\n# {{flexion|abandonnere}}'
    >>> adjust_wikicode("=={{da}}==\n# {{flertal af}} {{l|da|tale}}", LANG)
    '=={{da}}==\n# {{flexion|{{l|da|tale}}}}'
    >>> adjust_wikicode("=={{da}}==\n# {{flertal af}} {{l|da|tale|taler}}", LANG)
    '=={{da}}==\n# {{flexion|{{l|da|tale|taler}}}}'

    >>> from ... import context
    >>> _ = context.reset(LANG)

    >>> context.new_word("baskyle")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|baskyle|baskylen|baskyler|baskylerne}}", LANG, word="baskyle")
    '=={{da}}==\n# {{rev-flexion|baskylen}}\n# {{rev-flexion|baskyler}}\n# {{rev-flexion|baskylerne}}'

    >>> context.new_word("hav")
    >>> adjust_wikicode("=={{da}}==\n{{da-verb|hav|have|har|havde|har|haft}}", LANG, word="hav")
    '=={{da}}==\n# {{rev-flexion|haft}}\n# {{rev-flexion|har}}\n# {{rev-flexion|havde}}\n# {{rev-flexion|have}}'

    >>> context.new_word("genom")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun-infl|et|er}}", LANG, word="genom")
    '=={{da}}==\n# {{rev-flexion|genomer}}\n# {{rev-flexion|genomerne}}\n# {{rev-flexion|genomernes}}\n# {{rev-flexion|genomers}}\n# {{rev-flexion|genomet}}\n# {{rev-flexion|genomets}}\n# {{rev-flexion|genoms}}'

    >>> context.new_word("atlas")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|et|atlas|atlasset|atlas(ser)|atlasse(r)ne}}", LANG, word="atlas")
    '=={{da}}==\n# {{rev-flexion|atlasser}}\n# {{rev-flexion|atlasserne}}\n# {{rev-flexion|atlasset}}'

    >>> context.new_word("forlige")
    >>> adjust_wikicode("=={{da}}==\n{{da-verb|forlig|forlige|forliger|forligte/forligede|har/er|forlig(e)t}}", LANG, word="forlige")
    '=={{da}}==\n# {{rev-flexion|forlig}}\n# {{rev-flexion|forligede}}\n# {{rev-flexion|forliger}}\n# {{rev-flexion|forliget}}\n# {{rev-flexion|forligte}}'

    >>> context.new_word("magma")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|magma|magmaen|magmaer|magmaerne}} / {{da-noun|et|magma|magmaet|magmaer|magmaerne}}", LANG, word="magma")
    '=={{da}}==\n# {{rev-flexion|magmaen}}\n# {{rev-flexion|magmaer}}\n# {{rev-flexion|magmaerne}}\n# {{rev-flexion|magmaer}}\n# {{rev-flexion|magmaerne}}\n# {{rev-flexion|magmaet}}'

    >>> context.new_word("forhammer")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller\n:{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", LANG, word="forhammer")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", LANG, word="forhammer")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller uofficielt\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", LANG, word="forhammer")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} (''plante'')\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}} (''grøntsag'')", LANG, word="forhammer")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'

    >>> context.new_word("føde")
    >>> adjust_wikicode("=={{da}}==\n{{da-verb|fød|føde|føder|fødede<br />fødte|har|fødet<br />født}}", LANG, word="føde")
    '=={{da}}==\n# {{rev-flexion|fød}}\n# {{rev-flexion|fødede}}\n# {{rev-flexion|føder}}\n# {{rev-flexion|fødet}}\n# {{rev-flexion|født}}\n# {{rev-flexion|fødte}}'
    """
    code = code.replace("----", "")

    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    #
    # Variants
    #

    patterns = [
        # Pluralis af [[tale#Substantiv|tale]]
        re.compile(rf"(?i){start}(?:{forms})\s++\[\[([^\]#|]++)(?:[#|].+)?\]\].*"),
        # {{flertal af}} '''[[tale]]'''
        re.compile(rf"(?i){start}\{{\{{(?:{forms})\}}\}} '*+\[\[([^\]]++).*"),
        #''præsens participium af'' '''[[abandonnere]]'''.
        re.compile(rf"(?i){start}'++(?:{forms})[\s']++\[\[([^\]]++).*"),
        # {{flertal af}} {{l|da|tale}}
        re.compile(rf"(?i){start}.*\{{\{{(?:{forms})\}}\}}\s++(\{{\{{[^}}]++\}}\}}).*"),
    ]

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(start, line):
            for pattern in patterns:
                line, count = pattern.subn(r"# {{flexion|\1}}", line, count=1)
                if count:
                    break
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = re.compile(
            rf"(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]++\}}\}})"
        )
        cleaned: list[str] = []

        for line in code.splitlines():
            if not any(tpl in line for tpl in interesting_reverse_variant_titles):
                cleaned.append(line)
                continue

            for tpl in pattern.findall(line):
                tpl_name = tpl[2 : max(0, tpl.find("|")) or tpl.find("}")].strip(" \u200e")
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(cleaned)

    return code
