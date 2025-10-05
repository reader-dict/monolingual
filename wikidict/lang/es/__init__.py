"""Spanish language."""

import re

from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://es.wiktionary.org/wiki/Especial:Aleatorio_en_categor%C3%ADa/Espa%C3%B1ol"

module_trans = "Módulo"
template_trans = "Plantilla"

float_separator = ","
thousands_separator = " "

head_sections = ("{{lengua|es}}",)
section_sublevels = (4, 3)
etyl_section = ("etimología", "etimología 1")
sections = (
    *etyl_section,
    "abreviaturas",
    "adjetivo",
    "{{abreviatura",
    "{{adjetivo",
    "{{adverbio",
    "{{artículo",
    "{{conjunción",
    "{{interjección",
    "{{locución",
    "{{onomatopeya",
    "{{prefijo",
    "{{preposición",
    "{{pronombre",
    "{{sufijo|",
    "{{sustantivo",
    "{{verbo",
    #
    # Variants, see render.find_section_definitions()
    #
    "forma adjetiva",
    "forma adjetiva y de participio",
    "forma verbal",
)

variant_titles = (
    "forma adjetiva",
    "forma verbal",
)
variant_templates = (
    "{{enclítico",
    "{{forma ",
    "{{f.",
    "{{gerundio",
    "{{infinitivo",
    "{{participio",
)

definitions_to_ignore = (
    "definición imprecisa",
    "marcar sin referencias",
)

templates_ignored = (
    "{{ámbito",
    "{{cita requerida",
    "{{citarequerida",
    "{{clear",
    "{{definición",
    "{{dicvis",
    "{{ejemplo",
    "{{elemento químico",
    "{{mapa",
    "{{marcar sin referencias",
    "{{picdic",
    "{{referencia",
    "{{relacionado",
    "{{revisar línea",
    "{{revisión",
    "{{sin referencias",
    "{{uso",
)


def find_pronunciations(
    code: str,
    locale: str,
    *,
    pattern: re.Pattern[str] = re.compile(r"(\{\{pron-graf[^\}]*\}\})"),
    find_prons: re.Pattern[str] = re.compile(r"^\|(\[[^\[\]]+])", flags=re.MULTILINE),
) -> list[str]:
    """
    >>> from ... import context
    >>> _ = context.reset("es")

    >>> find_pronunciations("", "es")
    []

    >>> context.new_word("también")
    >>> find_pronunciations("{{pron-graf}}", "es")
    ['[t̪amˈbjen]']

    >>> context.new_word("hala")
    >>> find_pronunciations("{{pron-graf|acentuación=grave|audio=LL-Q1321_(spa)-Rodelar-ala.wav|división=ha - la|fone=ˈa.la|homófono=ala|longitud_silábica=2|número_letras=4}}", "es")
    ['[ˈa.la]']
    """
    from ... import context

    res: set[str] = set()
    for tpl in pattern.findall(code):
        table = context.expand(tpl, locale)
        res.update(find_prons.findall(table))
    return sorted(res)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{ES|xxx|núm=1}}", "es")
    '== {{lengua|es}} =='
    """
    # {{ES|xxx|núm=n}} → == {{lengua|es}} ==
    code = re.sub(rf"^\{{\{{{locale.upper()}\|.+}}}}", rf"== {{{{lengua|{locale}}}}} ==", code, flags=re.MULTILINE)

    return code
