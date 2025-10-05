"""Spanish language."""

import re

from ... import utils
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
    "{{pron-graf",  # TODO: remove with #2542
    "{{referencia",
    "{{relacionado",
    "{{revisar línea",
    "{{revisión",
    "{{sin referencias",
    "{{uso",
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    r"""
    Expected docstring + function content is as follow after #2542 will be fixed (replace ">>" with ">>>"):

    >>> find_pronunciations("", "es")
    []

    >> from ... import context
    >> _ = context.reset("es")
    >> context.new_word("también")

    >> find_pronunciations("{{pron-graf}}", "es")
    ['[t̪amˈbjen]']
    \"""
    from ... import context

    pattern = re.compile(r"(\{\{pron-graf[^\}]*\}\})")
    res: set[str] = set()
    for tpl in pattern.findall(code):
        res.add(context.expand(tpl, locale))
    return sorted(f"[{pron}]" for pron in res)
    """
    """
    >>> find_pronunciations("{{pron-graf|fone=ˈa.t͡ʃo}}", "es")
    ['[ˈa.t͡ʃo]']
    >>> find_pronunciations("{{pron-graf|pron=seseo|altpron=No seseante|fone=ˈgɾa.θjas|2pron=seseo|alt2pron=Seseante|2fone=ˈgɾa.sjas|audio=Gracias (español).ogg}}", "es")
    ['[ˈgɾa.θjas]', '[ˈgɾa.sjas]']
    """
    pattern = re.compile(r"fone=([^}\|\s]+)")
    return [f"[{p}]" for p in utils.unique(utils.flatten(pattern.findall(code)))]


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
