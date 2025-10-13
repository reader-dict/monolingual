"""Spanish language."""

import re

from ... import utils
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

variant_titles = sections
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
    ['[t̪amˈbjen]']

    >>> context.new_word("hala")
    >>> find_pronunciations("{{pron-graf|acentuación=grave|audio=LL-Q1321_(spa)-Rodelar-ala.wav|división=ha - la|fone=ˈa.la|homófono=ala|longitud_silábica=2|número_letras=4}}", "es")
    ['[ˈa.la]']
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
    >>> adjust_wikicode("{{ES|xxx|núm=1}}", "es")
    '== {{lengua|es}} =='

    >>> from ... import context
    >>> _ = context.reset("es")

    >>> context.new_word("autocompletar")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{es.v}}", "es", word="autocompletar")
    '== {{lengua|es}} ==\n# {{rev-flexion|autocompleta}}\n# {{rev-flexion|autocompletaba}}\n# {{rev-flexion|autocompletabais}}\n# {{rev-flexion|autocompletaban}}\n# {{rev-flexion|autocompletabas}}\n# {{rev-flexion|autocompletad}}\n# {{rev-flexion|autocompletado}}\n# {{rev-flexion|autocompletamos}}\n# {{rev-flexion|autocompletan}}\n# {{rev-flexion|autocompletando}}\n# {{rev-flexion|autocompletara}}\n# {{rev-flexion|autocompletarais}}\n# {{rev-flexion|autocompletaran}}\n# {{rev-flexion|autocompletaras}}\n# {{rev-flexion|autocompletare}}\n# {{rev-flexion|autocompletareis}}\n# {{rev-flexion|autocompletaremos}}\n# {{rev-flexion|autocompletaren}}\n# {{rev-flexion|autocompletares}}\n# {{rev-flexion|autocompletaron}}\n# {{rev-flexion|autocompletará}}\n# {{rev-flexion|autocompletarán}}\n# {{rev-flexion|autocompletarás}}\n# {{rev-flexion|autocompletaré}}\n# {{rev-flexion|autocompletaréis}}\n# {{rev-flexion|autocompletaría}}\n# {{rev-flexion|autocompletaríais}}\n# {{rev-flexion|autocompletaríamos}}\n# {{rev-flexion|autocompletarían}}\n# {{rev-flexion|autocompletarías}}\n# {{rev-flexion|autocompletas}}\n# {{rev-flexion|autocompletase}}\n# {{rev-flexion|autocompletaseis}}\n# {{rev-flexion|autocompletasen}}\n# {{rev-flexion|autocompletases}}\n# {{rev-flexion|autocompletaste}}\n# {{rev-flexion|autocompletasteis}}\n# {{rev-flexion|autocomplete}}\n# {{rev-flexion|autocompletemos}}\n# {{rev-flexion|autocompleten}}\n# {{rev-flexion|autocompletes}}\n# {{rev-flexion|autocompleto}}\n# {{rev-flexion|autocompletá}}\n# {{rev-flexion|autocompletábamos}}\n# {{rev-flexion|autocompletáis}}\n# {{rev-flexion|autocompletáramos}}\n# {{rev-flexion|autocompletáremos}}\n# {{rev-flexion|autocompletás}}\n# {{rev-flexion|autocompletásemos}}\n# {{rev-flexion|autocompleté}}\n# {{rev-flexion|autocompletéis}}\n# {{rev-flexion|autocompletés}}\n# {{rev-flexion|autocompletó}}'

    >>> context.new_word("flamma")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{inflect.la.sust.1|flamm}}", "es", word="flamma")
    '== {{lengua|es}} ==\n# {{rev-flexion|flammae}}\n# {{rev-flexion|flammam}}\n# {{rev-flexion|flammarum}}\n# {{rev-flexion|flammas}}\n# {{rev-flexion|flammis}}'
    """
    # {{ES|xxx|núm=n}} → == {{lengua|es}} ==
    code = re.sub(rf"^\{{\{{{locale.upper()}\|.+}}}}", rf"== {{{{lengua|{locale}}}}} ==", code, flags=re.MULTILINE)

    #
    # Reverse variants
    #

    if any(tpl in code for tpl in reverse_variant_titles):
        cleaned: list[str] = []
        in_expected_section = False
        expected_section = (f"== {{{{lengua|{locale}}}", f"=={{{{lengua|{locale}}}")
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            line = line.strip()
            if not in_expected_section:
                if line.startswith(expected_section):
                    in_expected_section = True
            elif line.startswith(("= {", "={")):
                in_expected_section = False

            if not in_expected_section:
                continue

            if line.startswith(reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code, rest = tpl_code.rsplit("}}", 1)
                    if not rest:
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
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    if rest:
                        cleaned.append(rest)
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
