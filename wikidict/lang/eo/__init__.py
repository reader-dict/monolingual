"""Esperanto language."""

import re
from collections import defaultdict

from ... import lang, utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401
from .variant_handlers import render_reverse_variant

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
    "sinonimoj",
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
    # "{{vortospeco|litero|eo}",  # See #2634
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

variant_templates = ("{{form-eo}}",)

reverse_variant_titles = ("{{Deklinacio-eo}}", "{{Esperanta verbo}}")
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{?",
    "{{bildodek",  # picture
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

    >>> from ... import context
    >>> _ = context.reset("eo")

    >>> context.new_word("ekami")
    >>> adjust_wikicode("{{Esperanta verbo}}", "eo", word="ekami")
    '# {{rev-flexion|ekamanta}}\n# {{rev-flexion|ekamante}}\n# {{rev-flexion|ekamanto}}\n# {{rev-flexion|ekamas}}\n# {{rev-flexion|ekamata}}\n# {{rev-flexion|ekamate}}\n# {{rev-flexion|ekamato}}\n# {{rev-flexion|ekaminta}}\n# {{rev-flexion|ekaminte}}\n# {{rev-flexion|ekaminto}}\n# {{rev-flexion|ekamis}}\n# {{rev-flexion|ekamita}}\n# {{rev-flexion|ekamite}}\n# {{rev-flexion|ekamito}}\n# {{rev-flexion|ekamonta}}\n# {{rev-flexion|ekamonte}}\n# {{rev-flexion|ekamonto}}\n# {{rev-flexion|ekamos}}\n# {{rev-flexion|ekamota}}\n# {{rev-flexion|ekamote}}\n# {{rev-flexion|ekamoto}}\n# {{rev-flexion|ekamu}}\n# {{rev-flexion|ekamus}}'
    """
    # Wipe out unwanted sub-sections
    cleaned: list[str] = []
    in_unwanted_section = False
    unwanted = (
        r"\{\{Anagramoj",
        r"\{\{Ekzemploj",
        r"\{\{Fontoj",
        r"\{\{Derivaĵoj",
        r"\{\{Referencoj",
        r"\{\{Similaĵoj",
        r"\{\{Vortfaradoj",
    )
    for line in code.splitlines():
        if line.startswith(("{{", "=")):
            in_unwanted_section = bool(re.search(rf"^[= ]*(?:{'|'.join(unwanted)})", line, flags=re.MULTILINE))
        if not in_unwanted_section:
            cleaned.append(line)
    code = "\n".join(cleaned)

    # {{Sinonimoj}} → ==== Sinonimoj ====
    # (add handle section content without patterns)
    if "{{Sinonimoj}}" in code:
        cleaned.clear()
        in_section = False
        for line in code.splitlines():
            if line.startswith("{{Sinonimoj"):
                line = "==== Sinonimoj ===="
                in_section = True
            elif in_section:
                if line.startswith(("{{", "=")):
                    in_section = False
                elif not bool(re.search(rf"^(?:{'|'.join(section_patterns)})", line, flags=re.MULTILINE)):
                    line = f"# {line}"
            cleaned.append(line)
        code = "\n".join(cleaned)

    # Variants
    # {{form-eo}} → # {{form-eo}}
    code = code.replace(f"{{{{form-{locale}}}}}", f"# {{{{form-{locale}}}}}")
    for tpl in lang.reverse_variant_titles[locale]:
        code = code.replace(tpl, f"# {tpl}")

    # {{xxx}} → ==== {{xxx}} ====
    # {{xx-x}} → ==== {{xx-x}} ====
    code = re.sub(r"^(\{\{[\w\-]+\}\})", r"==== \1 ====", code, flags=re.MULTILINE)

    # Easier pronunciation
    code = re.sub(r"==== {{Vorterseparo}} ====\s*:(.+)\s*", r"\n{{PRON|`\1`}}\n", code, flags=re.MULTILINE)

    #
    # Reverse variants
    #

    for tpl in lang.reverse_variant_titles[locale]:
        if tpl in code and (forms := render_reverse_variant(tpl.strip("{}"), [], defaultdict(str), word)):
            code = code.replace(tpl, "\n# ".join(f"{{{{rev-flexion|{form}}}}}" for form in forms.split("|")), count=1)

    return code
