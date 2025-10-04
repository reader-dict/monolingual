"""Norwegian language."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://no.wiktionary.org/wiki/Spesial:Tilfeldig_rotside"

module_trans = "Modul"
template_trans = "Mal"

float_separator = ","
thousands_separator = " "

head_sections = ("norsk",)
section_sublevels = (3, 4)
etyl_section = ("etymologi",)
sections = (
    *etyl_section,
    "adjektiv",
    "adverb",
    "artikkel",
    "egennavn",
    "forklaring",
    "forkortelse",
    "frase",
    "idiom",
    "initialord",
    "interjeksjon",
    "konjunksjon",
    "ordklasse",
    "ordtak",
    "prefiks",
    "preposisjon",
    "pronomen",
    "subjektiv",
    "subjunksjon",
    "substantiv",
    "suffiks",
    "tallord",
    "verb",
)

variant_titles = tuple(section for section in sections if section not in etyl_section)
variant_templates = (
    "{{bøyingsform",
    "{{bøyningsform",
    "{{no-adj-bøyningsform",
    "{{no-sub-bøyningsform",
    "{{no-verbform av",
    "{{no-verb-bøyningsform",
)

templates_ignored = (
    "{{?",
    "{{audio",
    "{{definisjon mangler",
    "{{etymologi mangler",
    "{{Etymologi mangler",
    "{{mangler definisjon",
    "{{mangler etymologi",
    "{{o-ennå",  # translation table
    "{{opprydning",  # to clean
    "{{sitat",  # quote
    "{{trenger referanse",  # reference needed
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "no")
    []
    >>> find_genders("{{no-sub|m}}", "no")
    ['m']
    >>> find_genders("{{no-sub|mf}}", "no")
    ['mf']
    >>> find_genders("{{nn-sub|f}}", "no")
    ['f']
    >>> find_genders("{{nb-sub|m}}", "no")
    ['m']
    """
    pattern = re.compile(r"{{n[bon]-sub\|(\w+)}}")
    return utils.unique(utils.flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "no")
    []
    >>> find_pronunciations("{{IPA|/ɡrœn/|[grøn:]|språk=no}}", "no")
    ['/ɡrœn/', '[grøn:]']
    >>> find_pronunciations("{{IPA|[anomali:´]|språk=no}}", "no")
    ['[anomali:´]']
    >>> find_pronunciations("{{IPA|['klɑɾ]||['kɽɑɾ] (tykk ''L'' (østnorsk)|språk=no}}", "no")
    ["['klɑɾ]"]
    """
    pattern = re.compile(r"{{\s*IPA\s*\|[^\}]*}}")
    result: list[str] = []
    for f in pattern.findall(code):
        fsplit = f.split("|")
        for fs in fsplit:
            if not fs:
                continue
            if (fs[0] == "[" and fs[-1] == "]") or (fs[0] == "/" and fs[-1] == "/"):
                result.append(fs)
    return result


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("----", "no")
    ''

    >>> adjust_wikicode("<includeonly>\\n{{rfscript|und|sc=Deva}}, <br /></includeonly>", "no")
    ''
    """
    code = code.replace("----", "")

    # <includeonly>...</includeonly> → ''
    code = re.sub(r"(<includeonly>.+</includeonly>)", "", code, flags=re.DOTALL | re.MULTILINE)

    return code
