"""Catalan language."""

import re
from functools import lru_cache

from ... import context, utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]  # the folder name, on any OS

random_word_url = "https://ca.wiktionary.org/wiki/Especial:RandomRootpage"

module_trans = "Mòdul"
template_trans = "Plantilla"

head_sections = ("{{-ca-}}", "{{-mul-}}")
etyl_section = ("{{-etimologia-", "{{-etim-", "{{etim-lang")
sections = (
    *etyl_section,
    "abreviatura",
    "acrònim",
    "adjectiu",
    "adverbi",
    "article",
    # "caràcter",  # See #2634
    "conjunció",
    "contracció",
    "desinència",
    "forma verbal",
    "frase feta",
    "infix",
    "interjecció",
    # "lletra",  # See #2634
    "nom",
    "numeral",
    "prefix",
    "preposició",
    "pronom",
    "proverbi",
    "sigles",
    "sinònims",
    "sufix",
    "símbol",
    "verb",
)

variant_templates = (
    "{{ca-forma-conj",
    "{{forma-conj",
    "{{forma-f|",
    "{{forma-p|",
)

definitions_to_ignore = (
    "ex-cit",
    "ex-us",
)

templates_ignored = (
    "{{falten accepcions",
    "{{manquen accepcions",
    "{{sense accepcions",
)


@lru_cache
def cache_gender_pattern(locale: str) -> re.Pattern[str]:
    return re.compile(rf"\{{{locale}-\w++\|([fm]++)")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", LANG)
    []
    >>> find_genders("{{ca-nom|m}}", LANG)
    ['m']
    >>> find_genders("{{ca-nom|m}} {{ca-nom|m}}", LANG)
    ['m']
    """
    res: set[str] = set()
    for gender in cache_gender_pattern(locale).findall(code):
        if gender in ("mf", "fm"):
            res.update(("f", "m"))
        else:
            res.add(gender)
    return utils.unique(sorted(res))


RE_FIND_PRONS = re.compile(r"(/[^/]++/)$")


@lru_cache
def cache_pron_pattern(locale: str) -> re.Pattern[str]:
    return re.compile(rf"(?sm)(\{{\{{{locale}-pron[^}}]*+\}}\}})")


def find_pronunciations(code: str, locale: str) -> list[str]:
    r"""
    >>> _ = context.reset(LANG)

    >>> context.new_word("AFI")
    >>> find_pronunciations("{{ca-pron}}", LANG)
    ['/ˈa.fi/']

    >>> context.new_word("el")
    >>> find_pronunciations("{{ca-pron|q=àton|or=/əɫ/|occ=/eɫ/\n|f-centr=LL-Q7026 (cat)-Unjoanqualsevol-el.wav\n}}", LANG)
    ['/eɫ/']

    >>> context.new_word("miolar")
    >>> find_pronunciations("{{ca-pron|tipus=inf\n|f-centr=LL-Q7026 (cat)-Marvives-miolar.wav\n}}", LANG)
    ['/mi.uˈɫa/']
    """
    if not (templates := cache_pron_pattern(locale).findall(code)):
        return []

    lines = [line.strip() for line in context.expand(templates[0], LANG).splitlines()]

    # Prefer the standard one first
    for line in lines:
        if "|central" in line:
            return RE_FIND_PRONS.findall(line)

    # Fallback to the first AFI available
    for line in lines:
        if "Pronúncia del català" in line:
            return RE_FIND_PRONS.findall(line)

    return []


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("== {{-ca-}} ==\n=== Interjecció ===\n{{-sin-}}\n* [[quina llàstima]]\n* desaprofitat, fallit, malreeixit", LANG)
    '== {{-ca-}} ==\n=== Interjecció ===\n=== Sinònims ===\n# [[quina llàstima]]\n# desaprofitat, fallit, malreeixit'
    """
    # {{-sin-}} → === Sinònims ===
    code = code.replace("{{-sin-}}", "=== Sinònims ===")

    # Change the list type type of synonyms
    cleaned: list[str] = []
    in_section = False
    for line in code.splitlines():
        if line.startswith("=== Sinònims"):
            in_section = True
        elif in_section:
            if line.startswith("*"):
                line = line.replace("*", "#")
            else:
                in_section = False
        cleaned.append(line)
    code = "\n".join(cleaned)

    return code
