"""Romanian language."""

import re

from ...user_functions import flatten, unique
from .langs import langs

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = "."

# Markers for sections that contain interesting text to analyse.
section_patterns = ("#", r"\*")
section_sublevels = (3,)
head_sections = ("{{limba|ron}}", "{{limba|ro}}", "{{limba|conv}}")
etyl_section = ("{{etimologie}}",)
sections = (
    *etyl_section,
    "{{abr}}",
    "{{abreviere}",
    "{{adjectiv}",
    "{{adjective}",
    "{{adverb}",
    "{{articol}",
    "{{conjuncție}",
    "{{cuvânt compus}",
    "{{expr}}",
    "{{expresie}",
    "{{expresie|ro",
    "{{interjecție}",
    "{{locuțiune adjectivală}",
    "{{locuțiune adverbială}",
    "{{locuțiune}",
    "{{numeral colectiv}",
    "{{numeral}",
    "{{nume propriu}",
    "{{nume propriu|ro",
    "{{nume taxonomic|conv}",
    "{{participiu}",
    "{{prefix}",
    "{{prepoziție}",
    "{{pronume}",
    "{{pronume|ro",
    "{{substantiv}",
    "{{sufix}",
    "{{simbol|conv}",
    "{{unități}}",
    "{{verb auxiliar}",
    "{{verb copulativ}",
    "{{verb predicativ}",
    "{{verb tranzitiv}",
    "{{verb}",
)

# Variantes
variant_titles = tuple(section for section in sections if section not in etyl_section)
variant_templates = (
    "{{adj form of",
    "{{flexion",
)

# Templates more complex to manage.
templates_multi = {
    # {{n}}
    "n": "italic('n.')",
    # {{p}}
    "p": "italic('pl.')",
    # {{trad|el|παρα}}
    "trad": "parts[-1]",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ro")
    []
    >>> find_genders("{{substantiv-ron|gen={{m}}|nom-sg=câine|nom-pl=câini", "ro")
    ['m']
    >>> find_genders("{{substantiv-ron|gen={{n}}}}", "ro")
    ['n']
    """
    pattern = re.compile(r"gen={{([fmsingp]+)(?: \?\|)*}")
    return unique(flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ro")
    []
    >>> find_pronunciations("{{AFI|/ka.priˈmulg/}}", "ro")
    ['/ka.priˈmulg/']
    >>> find_pronunciations("{{IPA|ro|[fruˈmoʃʲ]}}", "ro")
    ['[fruˈmoʃʲ]']
    """
    res = []
    for pattern in (
        re.compile(r"\{AFI\|(/[^/]+/)(?:\|(/[^/]+/))*"),
        re.compile(rf"\{{IPA\|{locale}\|([^}}]+)"),
    ):
        res.extend(pattern.findall(code))

    return unique(flatten(res))


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    from .. import defaults
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        return render_template(word, template)

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://ro.wiktionary.org/wiki/Special:RandomRootpage"


def adjust_wikicode(code: str, locale: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{-avv-|ANY|ANY}}", "ro")
    '=== {{avv|ANY|ANY}} ==='

    >>> adjust_wikicode("====Verb tranzitiv====", "ro")
    '=== {{Verb tranzitiv}} ==='

    >>> adjust_wikicode("{{-avv-|ron}}", "ro")
    '=== {{avv}} ==='
    >>> adjust_wikicode("{{-avv-|ro}}", "ro")
    '=== {{avv}} ==='

    >>> adjust_wikicode("{{-avv-|ANY}}", "ro")
    '=== {{avv|ANY}} ==='

    >>> adjust_wikicode("{{-avv-}}", "ro")
    '=== {{avv}} ==='

    >>> adjust_wikicode("{{-nume propriu-}}", "ro")
    '=== {{nume propriu}} ==='

    >>> adjust_wikicode("==Romanian==", "ro")
    '== {{limba|ron}} =='

    >>> adjust_wikicode("==Romanian==\\n===Adjective===", "ro")
    '== {{limba|ron}} ==\\n=== {{Adjective}} ==='

    >>> adjust_wikicode("#''forma de feminin singular pentru'' [[frumos]].", "ro")
    '# {{flexion|frumos}}'
    >>> adjust_wikicode("#''formă alternativă pentru'' [[fântânioară]].", "ro")
    '# {{flexion|fântânioară}}'
    """
    locale_3_chars, lang_name = langs[locale]

    # `{{-avv-|ANY|ANY}}` → === `{{avv|ANY|ANY}} ===`
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\|(\w+)\}\}", r"=== {{\1|\2|\3}} ===", code, flags=re.MULTILINE)

    # `====Verb tranzitiv====` → `=== {{Verb tranzitiv}} ===`
    code = re.sub(r"====([^=]+)====", r"=== {{\1}} ===", code)

    # `{{-avv-|ron}}` → `=== {{avv}} ===`
    code = re.sub(rf"^\{{\{{-(.+)-\|({locale}|{locale_3_chars})\}}\}}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # `{{-avv-|ANY}}` → `=== {{avv|ANY}} ===`
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

    # `{{-avv-}}` → `=== {{avv}} ===`
    # `{{-nume propriu-}}` → `=== {{nume propriu}} ===`
    code = re.sub(r"^\{\{-([\w ]+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # Try to convert old Wikicode
    if f"=={lang_name}==" in code:
        # `==Romanian==` → `== {{limba|ron}} ==`
        code = code.replace(f"=={lang_name}==", f"== {{{{limba|{locale_3_chars}}}}} ==")

        # `===Adjective===` → `=== {{Adjective}} ===`
        code = re.sub(r"===(\w+)===", r"=== {{\1}} ===", code)

    #
    # Variants
    #

    # `#''forma de feminin singular pentru'' [[frumos]].` → `# {{flexion|frumos}}`
    # `#''formă alternativă pentru'' [[fântânioară]].` → `# {{flexion|fântânioară}}`
    code = re.sub(
        r"^#\s*'+(?:forma de|formă) [^']+'+\s*'*\[\[([^\]]+)\]\]'*\.?",
        r"# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    return code
