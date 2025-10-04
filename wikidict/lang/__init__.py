"""Internationalization stuff."""

from collections import defaultdict
from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any

from . import defaults

_ALL_LOCALES = {
    locale.name: import_module(f"wikidict.lang.{locale.name}")
    for locale in sorted(Path(__file__).parent.glob("*"))
    if locale.is_dir() and bool(list(locale.glob("*.py", case_sensitive=True)))
}


def _populate(attr: str) -> dict[str, Any]:
    """
    Create a dict for all locales pointing to the appropriate attribute.
    Fallback to `defaults`.
    """
    return {
        locale.__name__.split(".")[-1]: getattr(locale, attr) if hasattr(locale, attr) else getattr(defaults, attr)
        for locale in _ALL_LOCALES.values()
    }


# Name of the "Module" special page in the current locale
module_trans: dict[str, str] = _populate("module_trans")

# Name of the "Template" special page in the current locale
template_trans: dict[str, str] = _populate("template_trans")

# Name of the "Appendix" special page in the current locale
appendix_trans: dict[str, str] = _populate("appendix_trans")

# Wiktionary modules/templates to alter in the database directly
template_adapters: dict[str, dict[str, Callable[[str], str]]] = _populate("template_adapters")

# Wiktionary modules/templates to override
template_overrides: dict[str, dict[str, Callable[[tuple[str, ...]], str]]] = _populate("template_overrides")

# Float number separator
float_separator: dict[str, str] = _populate("float_separator")

# Thousands separator
thousands_separator: dict[str, str] = _populate("thousands_separator")

# Markers for sections that contain interesting text to analyse.
section_patterns: dict[str, tuple[str, ...]] = _populate("section_patterns")
sublist_patterns: dict[str, tuple[str, ...]] = _populate("sublist_patterns")
section_level: dict[str, int] = _populate("section_level")
section_sublevels: dict[str, tuple[int, ...]] = _populate("section_sublevels")
head_sections: dict[str, tuple[str, ...]] = _populate("head_sections")
etyl_section: dict[str, tuple[str]] = _populate("etyl_section")
sections: dict[str, tuple[str, ...]] = _populate("sections")

# Variants
# Section titles considered interesting to look variants into
variant_titles: dict[str, tuple[str, ...]] = _populate("variant_titles")
reverse_variant_titles: dict[str, tuple[str, ...]] = _populate("reverse_variant_titles")

# Template names considered interesting to look variants into
variant_templates: dict[str, tuple[str, ...]] = _populate("variant_templates")
reverse_variant_templates: dict[str, tuple[str, ...]] = _populate("reverse_variant_templates")

# Functions to extract variants from templates
variant_handlers: dict[str, dict[str, Callable[[str, list[str], defaultdict[str, str], str], str]]] = _populate(
    "variant_handlers"
)

# Some definitions are not good to keep
definitions_to_ignore: dict[str, tuple[str, ...]] = _populate("definitions_to_ignore")

# Templates to ignore: the text will be deleted
templates_ignored: dict[str, tuple[str, ...]] = _populate("templates_ignored")

# Function to find gender(s)
find_genders: dict[str, Callable[[str, str], list[str]]] = _populate("find_genders")

# Function to find pronunciation(s)
find_pronunciations: dict[str, Callable[[str, str], list[str]]] = _populate("find_pronunciations")

# URL to fetch a random word (in the current locale preferrably)
random_word_url: dict[str, str] = _populate("random_word_url")

# Function to adapt the word wikicode before rendering
# TODO: typing, but I do not know yet how to set keyword-arguments
adjust_wikicode = _populate("adjust_wikicode")
