"""Swedish language."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://sv.wiktionary.org/wiki/Special:RandomRootpage"

module_trans = "Modul"
template_trans = "Mall"

float_separator = ","
thousands_separator = " "

# https://sv.wiktionary.org/wiki/Wiktionary:Stilguide#Ordklassrubriken
head_sections = ("svenska",)
sections = (
    "adjektiv",
    "adverb",
    "affix",
    "artikel",
    "efterled",
    "förkortning",
    "förled",
    "interjektion",
    "konjunktion",
    "possessivt pronomen",
    "postposition",
    "prefix",
    "preposition",
    "pronomen",
    "substantiv",
    "suffix",
    "verb",
    "verbpartikel",
)

variant_titles = (
    "adjektiv",
    "adverb",
    "substantiv",
    "verb",
)
variant_templates = (
    "{{avledning",
    "{{böjning",
)

templates_ignored = (
    "{{?",
    "{{citat",
    "{{inget uppslag",  # nospread
    "{{fakta",  # facts
    "{{källa-so",  # missing source
    "{{konstr",  # incomplete construction
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "sv")
    []
    >>> find_pronunciations("{{uttal|sv|ipa=eːn/, /ɛn/, /en}}", "sv")
    ['/eːn/, /ɛn/, /en/']
    >>> find_pronunciations("{{uttal|sv|ipa=en|uttalslänk=-|tagg=vissa dialekter}}", "sv")
    ['/en/']
    >>> find_pronunciations("{{uttal|sv|ipa=ɛn|uttalslänk=-}}", "sv")
    ['/ɛn/']
    """
    pattern = re.compile(rf"\{{uttal\|{locale}\|(?:[^\|]+\|)?ipa=([^}}|]+)}}?\|?")
    return [f"/{p}/" for p in utils.unique(pattern.findall(code))]
