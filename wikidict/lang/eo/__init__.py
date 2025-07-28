"""Esperanto language."""

# Float number separator
import re

from ...user_functions import unique

float_separator = ","

# Thousands separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
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

# Variants
variant_titles = sections
variant_templates = ("{{form-eo}}",)

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "?",
    "aŭdo",
    "barileto",
    "fundamenta",
    "IFA",
    "N",
    "PRON",
    "quote-book",
    "quote-magazine",
    "ref-AdE",
    "ref-Grabowski",
    "ref-Kalman",
    "ref-PrV",
    "ref-ReVo",
    "radiofoniaj liternomoj",
    "rima",
    "vian",
    "Vd",
    "Vidu ankaŭ",
    "W",
    "X",
)

# Templates more complex to manage.
templates_multi = {
    # {{fina|o}}
    "fina": "parts[1]",
    # {{lite|ŭ}}
    "lite": "parts[1]",
    # {{inte|o}}
    "inte": "parts[1]",
    # {{mems|du}}
    "mems": "parts[1]",
    # {{pref|mis}}
    "pref": "parts[1]",
    # {{radi|vort}}
    "radi": "parts[1]",
    # {{sufi|il}}
    "sufi": "parts[1]",
    # {{Vortospeco|mona nomo|eo}}
    "Vortospeco": "capitalize(parts[1])",
}

# Templates that will be completed/replaced using custom text.
templates_other = {
    "🏠": "🏠 <i>arkitekturo</i>",
    "🌄": "<i>geografio</i>",
    "🍴": "gastronomia",
    "📖": "📖 <i>(presarto kaj libroj)</i>",
    "📷": "📷 <i>fotografio kaj kinotekniko</i>",
    "⏚": "⏚ <i>elektro kaj elektroteĥniko</i>",
    "✞": "✞ <i>kristanismo</i>",
    "❤": "❤ <i>korpostrukturo kaj histologio:</i>",
    "☆": "☆ <i>belartoj<i>",
    "♉": "♉ <i>bestologio</i>",
    "👥": "👥 <i>komunuza senso</i>",
    "🍁": "🍁 <i>herbiko</i>",
    "✈": "✈ <i>aviado</i>",
    "♠": "♠ <i>ludoj</i>",
    "☼": "☼ <i>terscieco (inkl. mineral- kaj rokoscienco)</i>",
    "⚓": "⚓ <i>marnavigado kaj ŝipoj</i>",
    "⚕": "(⚕ <i>kuracscienco kaj kirurgio</i>)",
    "♜": "♜ <i>historio</i>",
    "Λ": "Λ <i>lingv.</i>",
    "⊕": "⊕ <i>terologio (inkl. mineralogio kaj petrologio):</i>",
    "♧": "♧ <i>beletro</i>",
    "Ⓣ": "Ⓣ <i>(teknikoj [inkl. mekanikon kaj metalurgion])</i>",
    "☇": "☇ <i>forkomunikoj (inkl. radioforsonadon, videaĵojn kaj elektrosonsciencon</i>)",
    "Π": "Π <i>prahistorio</i>",
    "Θ": "(<i>Θ religioj</i>)",
    "𝅘𝅥𝅰": "𝅘𝅥𝅰 <i>muziko</i>",
    "⚔": "<i>militaferoj</i>",
    "AGRHOR": "<i>terkulturo</i>",
    "EKON": "<i>ekon.</i>",
    "HOR": "<i>hortikulturo, arbokulturo, arbarkultivo</i>",
    "KRI": "<i>krist.</i>",
    "TRA": "<i>trafiko</i>",
    "figurs.": "<i>figursenca</i>",
    "hist.": "♜ <i>hist.</i>",
    "ĵar.": "<i>ĵar.</i>",
    "lat. tardío": "malfrua latina",
    "lat. vulg.": "vulgara latina",
    "ling.": "Λ <i>lingv.</i>",
    "mar.": "⚓ <i>maraferoj</i>",
    "poe.": "<i>poetiko, poezio</i>",
}
templates_other["Ĵar."] = templates_other["ĵar."]
templates_other["Ling."] = templates_other["ling."]
templates_other["Mar."] = templates_other["mar."]
templates_other["MUZ"] = templates_other["𝅘𝅥𝅰"]
templates_other["Poe."] = templates_other["poe."]


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "eo")
    []
    >>> find_genders("{{g|m}}", "eo")
    ['m']
    """
    pattern = re.compile(r"{g\|(\w+)")
    return unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
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
    from ...utils import process_templates

    if prons := [
        process_templates("", match.rstrip("."), locale) for match in re.findall(r"\{\{PRON\|`([^`]+)`", code)
    ]:
        return prons

    return [
        process_templates("", match.rstrip(".").split("|")[-1], locale)
        for match in re.findall(r"\{\{IFA\|([^}]+)}}", code)
    ]


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


random_word_url = "https://eo.wiktionary.org/wiki/Speciala%C4%B5o:RandomRootpage"


def adjust_wikicode(code: str, locale: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{Deklinacio-eo}}", "eo")
    ''

    >>> adjust_wikicode("{{form-eo}}", "eo")
    '# {{form-eo}}'

    >>> adjust_wikicode("{{xxx}}", "eo")
    '==== {{xxx}} ===='
    >>> adjust_wikicode("{{xx-x}}", "eo")
    '==== {{xx-x}} ===='
    >>> adjust_wikicode("===={{Tradukoj}}====", "eo")
    '== {{Tradukoj}} =='

    >>> adjust_wikicode("{{Vorterseparo}}:{{radi|tret}} + {{fina|i}}", "eo")
    '\\n{{PRON|`{{radi|tret}} + {{fina|i}}`}}\\n'
    >>> adjust_wikicode("{{Vorterseparo}}\\n:{{radi|tret}} + {{fina|i}}", "eo")
    '\\n{{PRON|`{{radi|tret}} + {{fina|i}}`}}\\n'
    """
    # Wipe out {{Deklinacio-eo}}
    code = code.replace(f"{{{{Deklinacio-{locale}}}}}", "")

    # Variants
    # {{form-eo}} → # {{form-eo}}
    code = code.replace(f"{{{{form-{locale}}}}}", f"# {{{{form-{locale}}}}}")

    # {{xxx}} → ==== {{xxx}} ====
    # {{xx-x}} → ==== {{xx-x}} ====
    code = re.sub(r"^(\{\{[\w\-]+\}\})", r"==== \1 ====", code, flags=re.MULTILINE)

    # ===={{Tradukoj}}==== → == {{Tradukoj}} ==
    code = re.sub(
        r"====\s*(\{\{(?:Ekzemploj|Derivaĵoj|Referencoj|Sinonimoj|Tradukoj|Vortfaradoj|trad-\w+)\}\})\s*====",
        r"== \1 ==",
        code,
        flags=re.MULTILINE,
    )

    # Easier pronunciation
    code = re.sub(r"==== {{Vorterseparo}} ====\s*:(.+)\s*", r"\n{{PRON|`\1`}}\n", code, flags=re.MULTILINE)

    return code
