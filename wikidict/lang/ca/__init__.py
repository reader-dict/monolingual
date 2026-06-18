"""Catalan language."""

import re

from ... import utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://ca.wiktionary.org/wiki/Especial:RandomRootpage"

module_trans = "Mòdul"
template_trans = "Plantilla"

float_separator = ","
thousands_separator = "."

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

variant_titles = sections
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


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ca")
    []
    >>> find_genders("{{ca-nom|m}}", "ca")
    ['m']
    >>> find_genders("{{ca-nom|m}} {{ca-nom|m}}", "ca")
    ['m']
    """
    pattern = re.compile(rf"\{{{locale}-\w+\|([fm]+)")
    return utils.unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ca")
    []
    >>> find_pronunciations("{{ca-pron|/as/}}", "ca")
    ['/as/']
    >>> find_pronunciations("{{ca-pron|or=/əɫ/}}", "ca")
    ['/əɫ/']
    >>> find_pronunciations("{{ca-pron|or=/əɫ/|occ=/eɫ/}}", "ca")
    ['/əɫ/']
    >>> find_pronunciations("{{ca-pron|q=àton|or=/əɫ/|occ=/eɫ/|rima=}}", "ca")
    ['/əɫ/']
    """
    pattern = re.compile(rf"\{{\{{\s*{locale}-pron\s*\|(?:q=\S*\|)?(?:\s*or\s*=\s*)?(/[^/]+/)")
    return utils.unique(pattern.findall(code))


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("== {{-ca-}} ==\n=== Interjecció ===\n{{-sin-}}\n* [[quina llàstima]]\n* desaprofitat, fallit, malreeixit", "ca")
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
