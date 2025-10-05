"""Danish language."""

import re

from .langs import langs
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://da.wiktionary.org/wiki/Speciel:RandomRootpage"

module_trans = "Modul"
template_trans = "Skabelon"

float_separator = ","
thousands_separator = " "

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
    "bogstav",
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
    "{{ubest-pronon}",
    "{{verb}",
)

variant_titles = sections
variant_templates = ("{{alternativ stavemåde af", "{{form of", "{{flexion", "{{imperativ af", "{{imperativ form af")

templates_ignored = (
    "{{definition mangler",
    "{{dm",
    "{{rfe",
    "{{wikipedia",
    "{{Wikipedia",
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "da")
    []
    >>> find_pronunciations("{{IPA|/bɛ̜ːˀ/|lang=da}}", "da")
    ['/bɛ̜ːˀ/']
    """
    pattern = re.compile(rf"\{{\{{IPA(?:\|(.*?))?\|lang={locale}\}}\}}")
    return [item for sublist in (re.findall(pattern, code) or []) for item in sublist.split("|") if item]


ALL_FORMS = [
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
    "ental bestemt af",
    "flertal af",
    "genitivform af",
    "genitiv ental ubestemt af",
    "genitiv ubestemt entalsform af",
    "nutid af",
    "pluralis af",
    "præteritum participium af",
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
    all_langs_iso: str = "|".join(langs),
    all_langs_name: str = "|".join(langs.values()),
    forms: str = "|".join(ALL_FORMS),
    start: str = rf"^(?:{'|'.join(section_patterns)})\s*",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("{{(}}\n* {{en}}: {{trad|en|limnology}}\n{{)}}", "da")
    ''

    >>> adjust_wikicode("{{=da=}}", "da")
    '=={{da}}=='

    >>> adjust_wikicode("===dansk===", "da")
    '=={{da}}=='
    >>> adjust_wikicode("===Engelsk===", "da")
    '=={{en}}=='
    >>> adjust_wikicode("===Foo===", "fo")
    '===Foo==='

    >>> adjust_wikicode("{{-avv-|da}}", "da")
    '=== {{avv}} ==='

    >>> adjust_wikicode("{{-avv-|ANY}}", "da")
    '=== {{avv|ANY}} ==='

    >>> adjust_wikicode("{{-avv-}}", "da")
    '=== {{avv}} ==='

    >>> adjust_wikicode("*Pluralis af [[tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("#Pluralis af [[tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("#Pluralis af [[tale|tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("#Pluralis af [[tale#Substantiv|tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("# Nutid af [[tale#Verbum|tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("# Flertal af [[tale]]: [[ui]].", "da")
    '# {{flexion|tale}}'

    >>> adjust_wikicode("# {{flertal af}} [[tale]]", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("# {{flertal af}} '''[[tale]]'''", "da")
    '# {{flexion|tale}}'
    >>> adjust_wikicode("# {{flertal af}} {{l|da|tale}}", "da")
    '# {{flexion|{{l|da|tale}}}}'
    >>> adjust_wikicode("# {{flertal af}} {{l|da|tale|taler}}", "da")
    '# {{flexion|{{l|da|tale|taler}}}}'
    """
    code = code.replace("----", "")

    # {{(}} .* {{)}}
    code = re.sub(r"\{\{\(\}\}(.+)\{\{\)\}\}", "", code, flags=re.DOTALL | re.MULTILINE)

    # {{=da=}} → =={{da}}==
    code = re.sub(r"\{\{=(\w+)=\}\}", r"=={{\1}}==", code, flags=re.MULTILINE)

    # ===dansk=== → =={{da}}==
    code = re.sub(
        rf"=+\s*({all_langs_name})\s*=+",
        lambda m: f"=={{{{{next(iso for iso, name in langs.items() if m[1].lower() == name)}}}}}==",
        code,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    # Transform sub-locales into their own section to prevent mixing stuff
    # {{-da-}} → =={{da}}==
    # {{-mul-}} → =={{mul}}==
    code = re.sub(rf"\{{\{{-({all_langs_iso})-\}}\}}", r"=={{\1}}==", code, flags=re.MULTILINE)

    # {{-avv-|da}} → === {{avv}} ===
    code = re.sub(rf"^\{{\{{-(.+)-\|{locale}\}}\}}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # {{-avv-|ANY}} → === {{avv|ANY}} ===
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

    # {{-avv-}} → === {{avv}} ===
    code = re.sub(r"^\{\{-(\w+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    #
    # Variants
    #

    patterns = [
        # Pluralis af [[tale#Substantiv|tale]]
        rf"(?:{forms})\s+\[\[([^\]#|]+)(?:[#|].+)?]]",
        # {{flertal af}} '''[[tale]]'''
        rf"\{{\{{(?:{forms})\}}\}} '*\[\[([^\]]+)",
        # `# {{flertal af}} {{l|da|tale}}
        rf".*\{{\{{(?:{forms})\}}\}}\s+(\{{\{{[^}}]+\}}\}})",
    ]

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(start, line):
            for pattern in patterns:
                line, count = re.subn(rf"{start}{pattern}.*", r"# {{flexion|\1}}", line, count=1, flags=re.IGNORECASE)  # noqa: PLW2901
                if count:
                    break
        lines.append(line)

    return "\n".join(lines)
