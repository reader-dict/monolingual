"""Danish language."""

import re

from ... import lang, utils
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
    "{{ubest-pronon}",
    "{{verb}",
)

variant_titles = sections
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

    >>> adjust_wikicode("{{trans-top|en kødbolle lavet af hakket fars}}\n*{{en}}: {{t|en|meatball}}\n*{{fi}}: {{t|fi|lihapulla}}f}}\n*{{el}}: {{t|el|κεφτές|m|sc=Grek}}\n**{{grc}}: {{t|grc|ἰσίκιον|n}}\n{{trans-mid}}\n*{{it}}: {{t|it|polpetta}}\n*{{es}}: {{t|es|albóndigas}}\n*{{sv}}: {{t|sv|frikadell|c}}\n*{{de}}: {{t|de|Frikadelle|f}}\n{{trans-bottom}}", "da")
    ''

    >>> adjust_wikicode("{{=da=}}", "da")
    '=={{da}}=='

    >>> adjust_wikicode("===dansk===", "da")
    '=={{da}}=='
    >>> adjust_wikicode("===Engelsk===", "da")
    '=={{en}}=='
    >>> adjust_wikicode("===Foo===", "da")
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
    >>> adjust_wikicode("#''præsens participium af'' '''[[abandonnere]]'''.", "da")
    '# {{flexion|abandonnere}}'
    >>> adjust_wikicode("# {{flertal af}} {{l|da|tale}}", "da")
    '# {{flexion|{{l|da|tale}}}}'
    >>> adjust_wikicode("# {{flertal af}} {{l|da|tale|taler}}", "da")
    '# {{flexion|{{l|da|tale|taler}}}}'

    >>> from ... import context
    >>> _ = context.reset("da")

    >>> context.new_word("baskyle")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|baskyle|baskylen|baskyler|baskylerne}}", "da")
    '=={{da}}==\n# {{rev-flexion|baskylen}}\n# {{rev-flexion|baskyler}}\n# {{rev-flexion|baskylerne}}'

    >>> context.new_word("hav")
    >>> adjust_wikicode("=={{da}}==\n{{da-verb|hav|have|har|havde|har|haft}}", "da")
    '=={{da}}==\n# {{rev-flexion|haft}}\n# {{rev-flexion|har}}\n# {{rev-flexion|hav}}\n# {{rev-flexion|havde}}\n# {{rev-flexion|have}}'

    >>> context.new_word("genom")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun-infl|et|er}}", "da")
    '=={{da}}==\n# {{rev-flexion|genom}}\n# {{rev-flexion|genomer}}\n# {{rev-flexion|genomerne}}\n# {{rev-flexion|genomernes}}\n# {{rev-flexion|genomers}}\n# {{rev-flexion|genomet}}\n# {{rev-flexion|genomets}}\n# {{rev-flexion|genoms}}'

    >>> context.new_word("atlas")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|et|atlas|atlasset|atlas(ser)|atlasse(r)ne}}", "da")
    '=={{da}}==\n# {{rev-flexion|atlasser}}\n# {{rev-flexion|atlasserne}}\n# {{rev-flexion|atlasset}}'

    >>> context.new_word("forlige")
    >>> adjust_wikicode("=={{da}}==\n{{da-verb|forlig|forlige|forliger|forligte/forligede|har/er|forlig(e)t}}", "da")
    '=={{da}}==\n# {{rev-flexion|forlig}}\n# {{rev-flexion|forlige}}\n# {{rev-flexion|forligede}}\n# {{rev-flexion|forliger}}\n# {{rev-flexion|forliget}}\n# {{rev-flexion|forligte}}'

    >>> context.new_word("magma")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|magma|magmaen|magmaer|magmaerne}} / {{da-noun|et|magma|magmaet|magmaer|magmaerne}}", "da")
    '=={{da}}==\n# {{rev-flexion|magmaen}}\n# {{rev-flexion|magmaer}}\n# {{rev-flexion|magmaerne}}\n# {{rev-flexion|magmaer}}\n# {{rev-flexion|magmaerne}}\n# {{rev-flexion|magmaet}}'

    >>> context.new_word("forhammer")
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller\n:{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", "da")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", "da")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} eller uofficielt\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}}", "da")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    >>> adjust_wikicode("=={{da}}==\n{{da-noun|en|forhammer|forhammeren|forhamre|forhamrene}} (''plante'')\n{{da-noun|en|forhammer|forhammeren|forhammere|forhammerne}} (''grøntsag'')", "da")
    '=={{da}}==\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhamre}}\n# {{rev-flexion|forhamrene}}\n# {{rev-flexion|forhammere}}\n# {{rev-flexion|forhammeren}}\n# {{rev-flexion|forhammerne}}'
    """
    code = code.replace("----", "")

    # {{(}} .* {{)}}
    code = re.sub(r"\{\{\(\}\}(.+)\{\{\)\}\}", "", code, flags=re.DOTALL | re.MULTILINE)

    # {{trans-top|...}}...{{trans-bottom}}
    code = re.sub(r"\{\{trans-top(.+)\{\{trans-bottom\}\}", "", code, flags=re.DOTALL | re.MULTILINE)

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
        #''præsens participium af'' '''[[abandonnere]]'''.
        rf"'+(?:{forms})[\s']+\[\[([^\]]+)",
        # {{flertal af}} {{l|da|tale}}
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
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]+}}}})"
        cleaned: list[str] = []
        in_expected_section = False

        for line in code.splitlines():
            line = line.strip()
            if not in_expected_section:
                if line.startswith(f"=={{{{{locale}}}"):
                    in_expected_section = True
            elif line.startswith("=={{"):
                in_expected_section = False

            if not in_expected_section or not any(tpl in line for tpl in interesting_reverse_variant_titles):
                cleaned.append(line)
                continue

            for tpl in re.findall(pattern, line):
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(cleaned)

    return code
