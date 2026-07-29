"""Spanish language."""

import re

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
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
    "conjugación",
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

variant_templates = (
    "{{enclítico",
    "{{forma ",
    "{{f.",
    "{{gerundio",
    "{{infinitivo",
    "{{participio",
)

reverse_variant_titles = (
    "{{es.v",
    "{{inflect.",
)
reverse_variant_templates = ("{{rev-flexion",)

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
    ['[t̪ãmˈbjẽn]']

    >>> context.new_word("hala")
    >>> find_pronunciations("{{pron-graf|acentuación=grave|audio=LL-Q1321_(spa)-Rodelar-ala.wav|división=ha - la|fone=ˈa.la|homófono=ala|longitud_silábica=2|número_letras=4}}", "es")
    ['[ˈala]']
    """
    from ... import context

    res: set[str] = set()
    for tpl in pattern.findall(code):
        table = context.expand(tpl, "es")
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
    r"""
    >>> from ... import context
    >>> _ = context.reset("es")

    >>> context.new_word("autocompletar")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{es.v}}", "es", word="autocompletar")
    '== {{lengua|es}} ==\n;1: {{rev-flexion|autocompleta}}\n;1: {{rev-flexion|autocompletaba}}\n;1: {{rev-flexion|autocompletabais}}\n;1: {{rev-flexion|autocompletaban}}\n;1: {{rev-flexion|autocompletabas}}\n;1: {{rev-flexion|autocompletad}}\n;1: {{rev-flexion|autocompletado}}\n;1: {{rev-flexion|autocompletamos}}\n;1: {{rev-flexion|autocompletan}}\n;1: {{rev-flexion|autocompletando}}\n;1: {{rev-flexion|autocompletara}}\n;1: {{rev-flexion|autocompletarais}}\n;1: {{rev-flexion|autocompletaran}}\n;1: {{rev-flexion|autocompletaras}}\n;1: {{rev-flexion|autocompletare}}\n;1: {{rev-flexion|autocompletareis}}\n;1: {{rev-flexion|autocompletaremos}}\n;1: {{rev-flexion|autocompletaren}}\n;1: {{rev-flexion|autocompletares}}\n;1: {{rev-flexion|autocompletaron}}\n;1: {{rev-flexion|autocompletará}}\n;1: {{rev-flexion|autocompletarán}}\n;1: {{rev-flexion|autocompletarás}}\n;1: {{rev-flexion|autocompletaré}}\n;1: {{rev-flexion|autocompletaréis}}\n;1: {{rev-flexion|autocompletaría}}\n;1: {{rev-flexion|autocompletaríais}}\n;1: {{rev-flexion|autocompletaríamos}}\n;1: {{rev-flexion|autocompletarían}}\n;1: {{rev-flexion|autocompletarías}}\n;1: {{rev-flexion|autocompletas}}\n;1: {{rev-flexion|autocompletase}}\n;1: {{rev-flexion|autocompletaseis}}\n;1: {{rev-flexion|autocompletasen}}\n;1: {{rev-flexion|autocompletases}}\n;1: {{rev-flexion|autocompletaste}}\n;1: {{rev-flexion|autocompletasteis}}\n;1: {{rev-flexion|autocomplete}}\n;1: {{rev-flexion|autocompletemos}}\n;1: {{rev-flexion|autocompleten}}\n;1: {{rev-flexion|autocompletes}}\n;1: {{rev-flexion|autocompleto}}\n;1: {{rev-flexion|autocompletá}}\n;1: {{rev-flexion|autocompletábamos}}\n;1: {{rev-flexion|autocompletáis}}\n;1: {{rev-flexion|autocompletáramos}}\n;1: {{rev-flexion|autocompletáremos}}\n;1: {{rev-flexion|autocompletás}}\n;1: {{rev-flexion|autocompletásemos}}\n;1: {{rev-flexion|autocompleté}}\n;1: {{rev-flexion|autocompletéis}}\n;1: {{rev-flexion|autocompletés}}\n;1: {{rev-flexion|autocompletó}}'

    >>> context.new_word("superscribir")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{es.v}}", "es", word="superscribir")
    '== {{lengua|es}} ==\n;1: {{rev-flexion|superscriba}}\n;1: {{rev-flexion|superscribamos}}\n;1: {{rev-flexion|superscriban}}\n;1: {{rev-flexion|superscribas}}\n;1: {{rev-flexion|superscribe}}\n;1: {{rev-flexion|superscriben}}\n;1: {{rev-flexion|superscribes}}\n;1: {{rev-flexion|superscribid}}\n;1: {{rev-flexion|superscribiendo}}\n;1: {{rev-flexion|superscribiera}}\n;1: {{rev-flexion|superscribierais}}\n;1: {{rev-flexion|superscribieran}}\n;1: {{rev-flexion|superscribieras}}\n;1: {{rev-flexion|superscribiere}}\n;1: {{rev-flexion|superscribiereis}}\n;1: {{rev-flexion|superscribieren}}\n;1: {{rev-flexion|superscribieres}}\n;1: {{rev-flexion|superscribieron}}\n;1: {{rev-flexion|superscribiese}}\n;1: {{rev-flexion|superscribieseis}}\n;1: {{rev-flexion|superscribiesen}}\n;1: {{rev-flexion|superscribieses}}\n;1: {{rev-flexion|superscribimos}}\n;1: {{rev-flexion|superscribiremos}}\n;1: {{rev-flexion|superscribirá}}\n;1: {{rev-flexion|superscribirán}}\n;1: {{rev-flexion|superscribirás}}\n;1: {{rev-flexion|superscribiré}}\n;1: {{rev-flexion|superscribiréis}}\n;1: {{rev-flexion|superscribiría}}\n;1: {{rev-flexion|superscribiríais}}\n;1: {{rev-flexion|superscribiríamos}}\n;1: {{rev-flexion|superscribirían}}\n;1: {{rev-flexion|superscribirías}}\n;1: {{rev-flexion|superscribiste}}\n;1: {{rev-flexion|superscribisteis}}\n;1: {{rev-flexion|superscribiéramos}}\n;1: {{rev-flexion|superscribiéremos}}\n;1: {{rev-flexion|superscribiésemos}}\n;1: {{rev-flexion|superscribió}}\n;1: {{rev-flexion|superscribo}}\n;1: {{rev-flexion|superscribáis}}\n;1: {{rev-flexion|superscribás}}\n;1: {{rev-flexion|superscribí}}\n;1: {{rev-flexion|superscribía}}\n;1: {{rev-flexion|superscribíais}}\n;1: {{rev-flexion|superscribíamos}}\n;1: {{rev-flexion|superscribían}}\n;1: {{rev-flexion|superscribías}}\n;1: {{rev-flexion|superscribís}}\n;1: {{rev-flexion|superscripto}}\n;1: {{rev-flexion|superscrito}}'
    """
    # Synonyms
    code = code.replace("{{sinónimo", ":;a: {{sinónimo")

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code = tpl_code.rsplit("}}", 1)[0]
                    tpl_code += "}}"
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip()
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)
                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    cleaned.extend(f";1: {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
