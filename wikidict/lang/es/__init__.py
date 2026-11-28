"""Spanish language."""

import itertools
import re
from collections import defaultdict

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://es.wiktionary.org/wiki/Especial:Aleatorio_en_categor%C3%ADa/Espa%C3%B1ol"

module_trans = "Módulo"
template_trans = "Plantilla"

head_sections = ("{{lengua|es}}",)
section_sublevels = (3, 4)
etyl_section = ("etimología", "etimología 1")
core_sections = (
    "abreviaturas",
    "adjetivo",
    "abreviatura",
    "adjetivo",
    "adverbio",
    "artículo",
    "conjugación",
    "conjunción",
    "contracción",
    "interjección",
    "locución",
    "onomatopeya",
    "partícula",
    "posposición",
    "postposición",
    "prefijo",
    "preposición",
    "pronombre",
    "sufijo",
    "sustantivo",
    "verbo",
    #
    # Variants, see render.find_section_definitions()
    #
    "forma ",
)
sections = (
    *etyl_section,
    *core_sections,
    *[f"{{{{{section}" for section in core_sections],
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
    "{{es.",
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

RE_FIND_PRONS = re.compile(r"\|(\[[^\[\]]++\])")


def find_pronunciations(
    code: str,
    locale: str,
    *,
    pattern: re.Pattern[str] = re.compile(r"(\{\{pron-graf[^\}]*+\}\})"),
) -> list[str]:
    r"""
    >>> _ = context.reset(LANG)

    >>> find_pronunciations("", LANG)
    []

    >>> context.new_word("también")
    >>> find_pronunciations("{{pron-graf}}", LANG)
    ['[t̪ãmˈbjẽn]']

    >>> context.new_word("hala")
    >>> find_pronunciations("{{pron-graf|1audio1=LL-Q1321_(spa)-Rodelar-ala.wav|h1=ala}}", LANG)
    ['[ˈala]']

    >>> context.new_word("bicicleta")
    >>> find_pronunciations("{{pron-graf|1audio1=LL-Q1321 (spa)-AdrianAbdulBaha-bicicleta.wav|1aunota1=Colombia}}", LANG)
    ['Esp.: [biθiˈklet̪a]', 'Am.: [bisiˈklet̪a]']

    >>> context.new_word("Guyana")
    >>> find_pronunciations("{{pron-graf|1audio1=LL-Q1321 (spa)-Rodelar-Guyana.wav|v1=Guayana|p1=Guyena}}", LANG)
    ['[guˈʝana]']
    """
    pronunciations = defaultdict(set)

    for tpl in pattern.findall(code):
        expanded = context.expand(tpl, LANG).splitlines()
        for line1, line2 in itertools.pairwise(expanded):
            if not (prons := RE_FIND_PRONS.findall(line2)):
                continue

            if "seseante'''" not in line1 or "'''no sheísta'''" in line1:  # No system
                pronunciations[prons[0]].add("")
                break

            if "'''seseante'''" in line1:  # Latin America
                pronunciations[prons[0]].add("Am.")
            elif "'''no seseante'''" in line1:  # Spanish
                pronunciations[prons[0]].add("Esp.")

    # If all pronunciations are the same, merge them without the system prefix
    final: list[str] = []
    for pron, kinds in pronunciations.items():
        kinds.discard("")
        if len(kinds) > 1:
            final.append(pron)
        elif len(kinds) == 1:
            final.append(f"{next(iter(kinds))}: {pron}")
        else:
            final.append(pron)

    # `reverse=True` because we want "Esp." first, then "Am."
    return sorted(final, reverse=True)


RE_LIST = re.compile(r"(?m)^;\d++[ |:]++")  # `;1:`
RE_SUB_LIST = re.compile(r"(?m)^:;\s*+[a-z]:++\s++")  # `:;a:`


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
    >>> _ = context.reset(LANG)

    >>> context.new_word("autocompletar")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{es.v}}", LANG, word="autocompletar")
    '== {{lengua|es}} ==\n# {{rev-flexion|autocompleta}}\n# {{rev-flexion|autocompletaba}}\n# {{rev-flexion|autocompletabais}}\n# {{rev-flexion|autocompletaban}}\n# {{rev-flexion|autocompletabas}}\n# {{rev-flexion|autocompletad}}\n# {{rev-flexion|autocompletado}}\n# {{rev-flexion|autocompletamos}}\n# {{rev-flexion|autocompletan}}\n# {{rev-flexion|autocompletando}}\n# {{rev-flexion|autocompletara}}\n# {{rev-flexion|autocompletarais}}\n# {{rev-flexion|autocompletaran}}\n# {{rev-flexion|autocompletaras}}\n# {{rev-flexion|autocompletare}}\n# {{rev-flexion|autocompletareis}}\n# {{rev-flexion|autocompletaremos}}\n# {{rev-flexion|autocompletaren}}\n# {{rev-flexion|autocompletares}}\n# {{rev-flexion|autocompletaron}}\n# {{rev-flexion|autocompletará}}\n# {{rev-flexion|autocompletarán}}\n# {{rev-flexion|autocompletarás}}\n# {{rev-flexion|autocompletaré}}\n# {{rev-flexion|autocompletaréis}}\n# {{rev-flexion|autocompletaría}}\n# {{rev-flexion|autocompletaríais}}\n# {{rev-flexion|autocompletaríamos}}\n# {{rev-flexion|autocompletarían}}\n# {{rev-flexion|autocompletarías}}\n# {{rev-flexion|autocompletas}}\n# {{rev-flexion|autocompletase}}\n# {{rev-flexion|autocompletaseis}}\n# {{rev-flexion|autocompletasen}}\n# {{rev-flexion|autocompletases}}\n# {{rev-flexion|autocompletaste}}\n# {{rev-flexion|autocompletasteis}}\n# {{rev-flexion|autocomplete}}\n# {{rev-flexion|autocompletemos}}\n# {{rev-flexion|autocompleten}}\n# {{rev-flexion|autocompletes}}\n# {{rev-flexion|autocompleto}}\n# {{rev-flexion|autocompletá}}\n# {{rev-flexion|autocompletábamos}}\n# {{rev-flexion|autocompletáis}}\n# {{rev-flexion|autocompletáramos}}\n# {{rev-flexion|autocompletáremos}}\n# {{rev-flexion|autocompletás}}\n# {{rev-flexion|autocompletásemos}}\n# {{rev-flexion|autocompleté}}\n# {{rev-flexion|autocompletéis}}\n# {{rev-flexion|autocompletés}}\n# {{rev-flexion|autocompletó}}'

    >>> context.new_word("superscribir")
    >>> adjust_wikicode("== {{lengua|es}} ==\n{{es.v}}", LANG, word="superscribir")
    '== {{lengua|es}} ==\n# {{rev-flexion|superscriba}}\n# {{rev-flexion|superscribamos}}\n# {{rev-flexion|superscriban}}\n# {{rev-flexion|superscribas}}\n# {{rev-flexion|superscribe}}\n# {{rev-flexion|superscriben}}\n# {{rev-flexion|superscribes}}\n# {{rev-flexion|superscribid}}\n# {{rev-flexion|superscribiendo}}\n# {{rev-flexion|superscribiera}}\n# {{rev-flexion|superscribierais}}\n# {{rev-flexion|superscribieran}}\n# {{rev-flexion|superscribieras}}\n# {{rev-flexion|superscribiere}}\n# {{rev-flexion|superscribiereis}}\n# {{rev-flexion|superscribieren}}\n# {{rev-flexion|superscribieres}}\n# {{rev-flexion|superscribieron}}\n# {{rev-flexion|superscribiese}}\n# {{rev-flexion|superscribieseis}}\n# {{rev-flexion|superscribiesen}}\n# {{rev-flexion|superscribieses}}\n# {{rev-flexion|superscribimos}}\n# {{rev-flexion|superscribiremos}}\n# {{rev-flexion|superscribirá}}\n# {{rev-flexion|superscribirán}}\n# {{rev-flexion|superscribirás}}\n# {{rev-flexion|superscribiré}}\n# {{rev-flexion|superscribiréis}}\n# {{rev-flexion|superscribiría}}\n# {{rev-flexion|superscribiríais}}\n# {{rev-flexion|superscribiríamos}}\n# {{rev-flexion|superscribirían}}\n# {{rev-flexion|superscribirías}}\n# {{rev-flexion|superscribiste}}\n# {{rev-flexion|superscribisteis}}\n# {{rev-flexion|superscribiéramos}}\n# {{rev-flexion|superscribiéremos}}\n# {{rev-flexion|superscribiésemos}}\n# {{rev-flexion|superscribió}}\n# {{rev-flexion|superscribo}}\n# {{rev-flexion|superscribáis}}\n# {{rev-flexion|superscribás}}\n# {{rev-flexion|superscribí}}\n# {{rev-flexion|superscribía}}\n# {{rev-flexion|superscribíais}}\n# {{rev-flexion|superscribíamos}}\n# {{rev-flexion|superscribían}}\n# {{rev-flexion|superscribías}}\n# {{rev-flexion|superscribís}}\n# {{rev-flexion|superscripto}}\n# {{rev-flexion|superscrito}}'
    """
    # Replace definition lists with numbered lists
    code = RE_LIST.sub("# ", code)
    code = RE_SUB_LIST.sub("## ", code)

    # Synonyms
    code = code.replace("{{sinónimo", "## {{sinónimo")

    # Remove templates used a sublist since they interfer with how list are retreived
    code = re.sub(rf"(?m)^(?:{'|'.join(templates_ignored)})[^\n]++", "", code)
    code = "\n".join(line for line in code.splitlines() if line.strip())

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
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip().strip("\u200e")
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)
                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
