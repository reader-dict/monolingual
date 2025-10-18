"""Esperanto language."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://eo.wiktionary.org/wiki/Speciala%C4%B5o:RandomRootpage"

module_trans = "Modulo"
template_trans = "Ŝablono"

float_separator = ","
thousands_separator = " "

section_patterns = ("#", r":\[\d+\]", r"\*")
section_sublevels = (3, 4)
head_sections = ("{{lingvo|eo}}", "{{lingvo|mul}}", "esperanto", "multldingva", "translingva")
etyl_section = ("{{deveno}}", "{{etimologio}}")
sections = (
    *etyl_section,
    "adjektivo",
    "adverbo",
    "difinoj",
    "infikso",
    "interjekcio",
    "konjunkcio",
    "malllongigo",
    "mallongigoj",
    "numeralo",
    "prefikso",
    "prepozicio",
    "pronomo",
    "radiko",
    "signifo",
    "signo",
    "subjunkcio",
    "substantivo",
    "sufikso",
    "verba formo",
    "verbo",
    "{{signifoj}",
    "{{vortospeco|adjektiva formo|eo}",
    "{{vortospeco|adjektivo|eo}",
    "{{vortospeco|adverbo|eo}",
    "{{vortospeco|antaŭfiksaĵo|eo}",
    "{{vortospeco|artikolo|eo}",
    "{{vortospeco|demanda adverbo|eo}",
    "{{vortospeco|esprimo|eo}",
    "{{vortospeco|finaĵo|eo}",
    "{{vortospeco|frazo|eo}",
    "{{vortospeco|interjekcio|eo}",
    "{{vortospeco|konjunkcio|eo}",
    "{{vortospeco|liternomo|eo}",
    "{{vortospeco|litero|eo}",
    "{{vortospeco|literoparo|eo}",
    "{{vortospeco|loknomo|eo}",
    "{{vortospeco|mallongigo|eo}",
    "{{vortospeco|mallongigo|mul}",
    "{{vortospeco|mona nomo|eo}",
    "{{vortospeco|nombro|eo}",
    "{{vortospeco|nomo|eo}",
    "{{vortospeco|numeralo|eo}",
    "{{vortospeco|partikulo|eo}",
    "{{vortospeco|persona nomo|eo}",
    "{{vortospeco|persona pronomo|eo}",
    "{{vortospeco|poseda pronomo|eo}",
    "{{vortospeco|postfiksaĵo|eo}",
    "{{vortospeco|prepozicio|eo}",
    "{{vortospeco|pronomo|eo}",
    "{{vortospeco|scienca nomo|mul}",
    "{{vortospeco|signo|mul}",
    "{{vortospeco|simbolo|eo}",
    "{{vortospeco|simbolo|mul}",
    "{{vortospeco|subjunkcio|eo}",
    "{{vortospeco|substantiva formo|eo}",
    "{{vortospeco|substantivo|eo}",
    "{{vortospeco|substantivo|mul}",
    "{{vortospeco|sufikso|eo}",
    "{{vortospeco|verbo ambaŭtransitiva|eo}",
    "{{vortospeco|verba formo|eo}",
    "{{vortospeco|verbo|eo}",
    "{{vortospeco|verbo netransitiva|eo}",
    "{{vortospeco|verbo transitiva|eo}",
    "{{vortospeco|vortgrupo|eo}",
)

variant_titles = sections
variant_templates = ("{{form-eo}}",)

templates_ignored = (
    "{{?",
    "{{aŭdo",  # audio
    "{{PRON",  # audio
    "{{quote-",
    "{{ref-",
    "{{Vd",  # see also
    "{{Vidu ankaŭ",  # see also
    "{{W",
    "{{X",
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "eo")
    []
    >>> find_genders("{{g|m}}", "eo")
    ['m']
    """
    pattern = re.compile(r"{g\|(\w+)")
    return utils.unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from ... import context
    >>> _ = context.reset("eo")
    >>> context.new_word("word")

    >>> find_pronunciations("", "eo")
    []
    >>> find_pronunciations("{{PRON|`luk/o.`}}", "eo")
    ['luk/o']
    >>> find_pronunciations("{{PRON|`[[advent]]•[[o]]`}}", "eo")
    ['advent•o']
    >>> find_pronunciations("{{PRON|`{{radi|vultur}} + o`}}", "eo")
    ['vultur + o']
    >>> find_pronunciations("{{PRON|` {{radi|dekstr}} + {{fina|a}}`}}", "eo")
    ['dekstr + a']
    >>> find_pronunciations("{{IFA|/vitpunkto/}}", "eo")
    ['/vitpunkto/']
    >>> find_pronunciations("{{IFA|nenk=1|ˈbɛʁɡŋ̩}}", "eo")
    ['ˈbɛʁɡŋ̩']
    """
    if prons := [
        utils.process_templates("", match.rstrip("."), locale) for match in re.findall(r"\{\{PRON\|`([^`]+)`", code)
    ]:
        return prons

    return [
        utils.process_templates("", match.rstrip(".").split("|")[-1], locale)
        for match in re.findall(r"\{\{IFA\|([^}]+)}}", code)
    ]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{Deklinacio-eo}}", "eo")
    ''

    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{form-eo}}", "eo")
    '=={{Lingvo|eo}}==\n# {{form-eo}}'

    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{xxx}}", "eo")
    '=={{Lingvo|eo}}==\n==== {{xxx}} ===='
    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{xx-x}}", "eo")
    '=={{Lingvo|eo}}==\n==== {{xx-x}} ===='

    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{Vorterseparo}}:{{radi|tret}} + {{fina|i}}", "eo")
    '=={{Lingvo|eo}}==\n\n{{PRON|`{{radi|tret}} + {{fina|i}}`}}\n'
    >>> adjust_wikicode("=={{Lingvo|eo}}==\n{{Vorterseparo}}\n:{{radi|tret}} + {{fina|i}}", "eo")
    '=={{Lingvo|eo}}==\n\n{{PRON|`{{radi|tret}} + {{fina|i}}`}}\n'
    """

    # Wipe out {{Deklinacio-eo}}
    code = code.replace(f"{{{{Deklinacio-{locale}}}}}", "")

    # Keep interesting sections only
    if not (code := utils.extract_relevant_sections(code, locale)):
        return ""

    # Wipe out unwanted sub-sections
    cleaned: list[str] = []
    in_unwanted_section = False
    unwanted = (
        "{{Anagramoj",
        "{{Ekzemploj",
        "{{Derivaĵoj",
        "{{Referencoj",
        "{{Sinonimoj",
        "{{Tradukoj",
        "{{Vortfaradoj",
        "{{trad-",
    )
    for line in code.splitlines():
        if line.startswith(("{{", "=")):
            in_unwanted_section = line.startswith(unwanted)
        if not in_unwanted_section:
            cleaned.append(line)
    code = "\n".join(cleaned)

    # Variants
    # {{form-eo}} → # {{form-eo}}
    code = code.replace(f"{{{{form-{locale}}}}}", f"# {{{{form-{locale}}}}}")

    # {{xxx}} → ==== {{xxx}} ====
    # {{xx-x}} → ==== {{xx-x}} ====
    code = re.sub(r"^(\{\{[\w\-]+\}\})", r"==== \1 ====", code, flags=re.MULTILINE)

    # Easier pronunciation
    code = re.sub(r"==== {{Vorterseparo}} ====\s*:(.+)\s*", r"\n{{PRON|`\1`}}\n", code, flags=re.MULTILINE)

    return code
