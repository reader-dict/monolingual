"""Norwegian language."""

import re

from ...user_functions import flatten, unique
from .labels import labels

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
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

# Variants
variant_titles = tuple(section for section in sections if section not in etyl_section)
variant_templates = (
    "{{bøyingsform",
    "{{bøyningsform",
    "{{no-adj-bøyningsform",
    "{{no-sub-bøyningsform",
    "{{no-verbform av",
    "{{no-verb-bøyningsform",
)

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "?",
    "#ifeq",
    "audio",
    "definisjon mangler",
    "etymologi mangler",
    "Etymologi mangler",
    "IPA",
    "lyd",
    "mangler definisjon",
    "mangler etymologi",
    "norm",
    "o-begge/båe",
    "o-nå/nu/no",
    "o-hvem/kven",
    "opprydning",
    "ordbank",
    "R",
    "sitat",
    "suffiks/oversikt",
    "taxlink",
    "trenger referanse",
)

# Templates that will be completed/replaced using italic style.
templates_italic = {
    **labels,
    "anatomi": "anatomi",
    "biologi": "biologi",
    "edb": "edb",
    "ikkekomp": "ingen komparativ eller superlativ",
    "internett": "Internett",
    "Internett": "Internett",
    "klær": "klesplagg",
    "målenhet": "måleenhet",
    "militær": "militært",
}


# Templates more complex to manage.
templates_multi = {
    # {{alternativ skrivemåte|be}}
    "alternativ skrivemåte": "f\"{italic('alternativ skrivemåte av')} {strong(parts[-1])}\"",
    # {{feilstaving av|førstvoterende|språk=no}}
    "feilstaving av": 'f"Feilstaving av {parts[1]}."',
    # {{l|lt|duktė}}
    "l": "parts[-1]",
    # {{m}}
    "m": "italic(parts[0])",
    # {{n}}
    "n": "italic(parts[0])",
    # {{opphav|norrønt|språk=no}
    "opphav": "parts[1]",
    # {{prefiks|a|biotisk|språk=no}}
    "prefiks": 'f"{italic(parts[1])}- + {italic(parts[2])}"',
    # {{qualifier|idiomatisk}}
    "qualifier": "term(parts[1])",
    # {{suffiks|konsentrere|sjon|språk=no}}
    "suffiks": 'f"{italic(parts[1])} + -{italic(parts[2])}"',
    # {{teleskopord|nei|ja|språk=no}}
    "teleskopord": 'f"teleskopord sammensatt av {parts[1]} og {parts[2]}"',
    # {{tidligere bøyningsform|no|sub|jul}}
    "tidligere bøyningsform": "f\"{italic('tidligere bøyningsform av')} {strong(parts[-1])}\"",
    # {{tidligere skriveform|no|kunstnarleg}}
    "tidligere skriveform": "f\"{italic('tidligere skriveform av')} {strong(parts[-1])}\"",
    # {{tidligere skrivemåte|no|naturlig tall}}
    "tidligere skrivemåte": "f\"{italic('tidligere skriveform av')} {strong(parts[-1])}\"",
    # {{vokabular|overført}}
    "vokabular": "term(parts[1])",
}

# Templates that will be completed/replaced using custom text.
templates_other = {
    "it": "italiensk",
    "l.": "latin",
    "L.": "latin",
    "la": "latin",
    "lty.": "nedertysk/lavtysk",
    "nn": "nynorsk",
    "tr": "tyrkisk",
}


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
    return unique(flatten(pattern.findall(code)))


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


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be called in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["jus"], "no")
        '<i>(jus)</i>'
        >>> last_template_handler(["jus", "nb"], "no")
        '<i>(jus)</i>'
        >>> last_template_handler(["jus", "nn"], "no")
        '<i>(jus)</i>'
        >>> last_template_handler(["jus", "no"], "no")
        '<i>(jus)</i>'
        >>> last_template_handler(["jus", "no"], "no")
        '<i>(jus)</i>'

        >>> last_template_handler(["kontekst", "fobi", "utellelig", "kat=no:Fobier", "kat2=no:Masseord"], "no")
        '<i>(fobi, utellelig)</i>'
        >>> last_template_handler(["kontekst", "jus", "utellelig", "kat=no:Jus", "kat2=no:Masseord", "nesten alltid i ubestemt form", "foreldet, nå kun i uttrykket «tort og svie»", "språk=no"], "no")
        '<i>(jus, utellelig, nesten alltid i ubestemt form)</i>'
        >>> last_template_handler(["tema", "matematikk", "fysikk", "språk=no"], "no")
        '<i>(matematikk, fysikk)</i>'

        >>> last_template_handler(["etyl", "non", "no"], "no")
        'norrønt'
        >>> last_template_handler(["etyl", "vulgærlatin", "no"], "no")
        'vulgærlatin'
        >>> last_template_handler(["term", "ord"], "no")
        '<i>ord</i>'

    """
    from ...user_functions import concat, extract_keywords_from, lookup_italic, term
    from .. import defaults
    from .langs import langs
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

    extract_keywords_from(parts)

    match tpl:
        case "etyl":
            return langs.get(parts[0], parts[0])
        case "kontekst" | "tema":
            return term(concat(parts[:3], ", "))

    if italic_tpl := lookup_italic(tpl, locale, empty_default=True):
        return term(italic_tpl)

    if not parts or (len(parts) == 1 and parts[0] in {"nb", "nn", "no", "nrm"}):
        return term(tpl)

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://no.wiktionary.org/wiki/Spesial:Tilfeldig_rotside"


def adjust_wikicode(code: str, locale: str) -> str:
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
