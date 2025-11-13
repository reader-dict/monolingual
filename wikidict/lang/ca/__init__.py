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
    "caràcter",
    "conjunció",
    "contracció",
    "desinència",
    "forma verbal",
    "frase feta",
    "infix",
    "interjecció",
    "lletra",
    "nom",
    "numeral",
    "prefix",
    "preposició",
    "pronom",
    "proverbi",
    "sigles",
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
