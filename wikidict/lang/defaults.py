"""Defaults values for locales without specific needs.
See `wikidict.langs.__init__` for details.
"""

from collections import defaultdict
from collections.abc import Callable

module_trans = "Module"
template_trans = "Template"
appendix_trans = "Appendix"
template_adapters: dict[str, Callable[[str], str]] = {}
template_overrides: dict[str, Callable[[tuple[str, ...]], str]] = {}

float_separator = ""
thousands_separator = ""

section_patterns = ("#", r"\*")
sublist_patterns = ("#", r"\*", ":")
section_level = 2
section_sublevels = (3,)
head_sections = ("",)
etyl_section = ("",)

variant_titles: tuple[str, ...] = ()
variant_templates: tuple[str, ...] = ()
reverse_variant_titles: tuple[str, ...] = ()
reverse_variant_templates: tuple[str, ...] = ()
variant_handlers: dict[str, Callable[[str, list[str], defaultdict[str, str], str], str]] = {}

definitions_to_ignore: tuple[str, ...] = ()
templates_ignored: tuple[str, ...] = ()


def find_genders(code: str, locale: str) -> list[str]:
    return []


def find_pronunciations(code: str, locale: str) -> list[str]:
    return []


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    return code
