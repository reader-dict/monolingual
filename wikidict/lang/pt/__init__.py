"""Portuguese language."""

import re

from ...user_functions import unique
from .escopos import escopos

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
section_patterns = ("#", r"\*", ":#")
sublist_patterns = ("#", r"\*")
section_level = 1
section_sublevels = (2,)
head_sections = ("{{-pt-}}", "{{-mult-}}")
etyl_section = ("{{etimologia|pt}}", "{{etimologia|mult}}", "etimologia")
_sections = [
    "abreviação",
    "abreviatura",
    "acrônimo",
    "acrónimo",
    "adjetivo",
    "advérbio",
    "afixo",
    "antepositivo",
    "artigo",
    "caractere",
    "conjunção",
    "contração",
    "elemento de composição",
    "expressão",
    "expressão verbal",
    "expressões",
    "forma adjetivo",
    "forma de adjetivo",
    "forma de advérbio",
    "forma de expressão verbal",
    "forma de locução adjetiva",
    "forma de locução adverbial",
    "forma de locução pronominal",
    "forma de locução substantiva",
    "forma de pronome",
    "forma de sigla",
    "forma de substantiva",
    "forma de substantivo",
    "forma de sufixo",
    "forma de verbo",
    "forma verbal",
    "frase",
    "infixo",
    "interjeição",
    "interfixo",
    "letra",
    "locução",
    "locução adjetiva",
    "locução adverbial",
    "locuçào adverbial",
    "locução conjuntiva",
    "locução interjetiva",
    "locução prepositiva",
    "locução substantiva",
    "locução verbal",
    "numeral",
    "onomatopeia",
    "pepb|",
    "plural",
    "pospositivo",
    "prefixo",
    "preposição",
    "pronome",
    "provérbio",
    "sigla",
    "símbolo",
    "subfijo",
    "substantivo",
    "sufixo",
    "topónimo",
    "verbal",
    "verbo",
]
_sections.extend(f"{{{{{s}" for s in _sections.copy())
_sections.extend(etyl_section)
sections = tuple(_sections)

# Variantes
variant_titles = sections
variant_templates = ("{{flexion",)

# Some definitions are not good to keep
definitions_to_ignore = ("peçodef",)

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "?.",
    "cont",
    "FDSP",
    "ligaçãoPalavraWdic",
    "OESP",
    "#seigual",
    "t",
)

# Templates that will be completed/replaced using italic style.
templates_italic = {**escopos}

# Templates more complex to manage.
templates_multi = {
    # {{AFI|/k/|pt}}
    "AFI": "parts[1]",
    # {{barra de cor|#0000FF|#0000FF}}
    "barra de cor": "color(parts[-1])",
    # {{c}}
    "c": "italic('género comum')",
    # {{c2gb}}
    "c2gb": "italic('comum aos dois gêneros no Brasil')",
    # {{confundir|anacruse}}
    "confundir": "f'{italic(f\"Não confundir com {strong(parts[-1])}\")}'",
    # {{datação|5/4/1810}}
    "datação": "f'[{italic(\"Datação\")}: {parts[-1]}]'",
    # {{escopo2|Informática}}
    # {{escopo2|Brasil|governo}}
    "escopo2": "term(parts[1])",
    # {{escopoCat|Náutica|pt}}
    "escopoCat": "term(lookup_italic(parts[1], 'pt'))",
    # {{escopoCatLang|Verbo auxiliar|pt}}
    "escopoCatLang": "term(lookup_italic(parts[1], 'pt'))",
    # {{escopoClasseMorfo|variação}}
    "escopoClasseMorfo": "small('(' + parts[-1] + ')')",
    # {{escopoObs.|Lê-se <u>formato dois A</u>.}}
    "escopoObs.": "f'{strong(\"Observação\")}: {parts[-1]}'",
    # {{escopoUso|Portugal|pt}}
    "escopoUso": "term(lookup_italic(parts[1], 'pt'))",
    # {{f}}
    "f": "italic('feminino')",
    # {{fb}}
    "fb": "italic('feminino no Brasil')",
    # {{fbmfdemais}}
    "fbmfdemais": "italic('feminino no Brasil, masculino ou feminino em Portugal e demais países')",
    # {{fem|heliostático}}
    "fem": 'f"feminino de {strong(parts[1])}"',
    # {{fl|la|occŭlo}}
    "fl": "parts[-1]",
    # {{fp}}
    "fp": "italic('feminino plural')",
    # {{grafiaPtbr|autocrómico}}
    "grafiaPtbr": "f'{italic(f\"Grafia usada no Brasil. Nos restantes países da CPLP escreve-se {strong(parts[-1])}\")}'",
    # {{grafiaPtpt|a}}
    "grafiaPtpt": "f'{italic(f\"Grafia usada em todos os países falantes de língua portuguesa exceto no Brasil, onde se escreve {strong(parts[-1])}\")}'",
    # {{l|pt|usar|usar}}",
    "l": "parts[-1]",
    # {{l.o.|jurídico|jurídica}}
    "l.o.": "parts[-1]",
    # {{l.s.|uso}}
    # {{l.s.|uso|Verbo}}
    "l.s.": "parts[1]",
    # {{lig|is|hljóð}}
    "lig": "parts[3 if len(parts) >= 4 else 2]",
    # {{link idioma|carro}}
    # {{link idioma|carro|es|vehículo}}
    "link idioma": "parts[3 if len(parts) == 4 else 1]",
    # {{link opcional|arapytãŋa|tpn}}
    "link opcional": "parts[1]",
    # {{link preto|ciconiforme}}
    "link preto": "parts[-1]",
    # {{ll|publicar}}
    "ll": "parts[3 if len(parts) == 4 else 1]",
    # {m|ar|شيشة|tr=šīša}}
    "m": "italic('masculino')",
    # {{mbfp}}
    "mbfp": "italic('masculino no Brasil, feminino em Portugal')",
    # {{mbmfp}}
    "mbmfp": "italic('masculino no Brasil, masculino e feminino em Portugal')",
    # {{mf}}
    "mf": "italic('masculino ou feminino')",
    # {{mfbfdemais}}
    "mfbfdemais": "italic('masculino ou feminino no Brasil, feminino em Portugal e demais países')",
    # {{mp}}
    "mp": "italic('masculino plural')",
    # {{mpfb}}
    "mpfb": "italic('masculino em Portugal, feminino no Brasil')",
    # {{mpmfb}}
    "mpmfb": "italic('masculino em Portugal, masculino e feminino no Brasil')",
    # {{mpteu}}
    "mpteu": "italic('masculino em Portugal')",
    # {{mq|palavra}}
    # {{mq|word|en}}
    "mq": 'f"o mesmo que {strong(parts[1]) if len(parts) == 2 else italic(parts[1])}"',
    # {{n}}
    "n": "italic('neutro')",
    # {{PE|cu}}
    "PE": "f\"{parts[-1]} {superscript('(português de Portugal)')}\"",
    # {{p/a}}
    "p/a": "italic('plural apenas')",
    # {{politônico|κρατία}}
    "politônico": "parts[-1]",
    # {{pr}}
    "pr": "italic('próprio')",
    # {{r|la|basium|basĭum}}
    "r": "parts[-1]",
    # {{r.l|la|utor|ūtor}}
    "r.l": "parts[-1]",
    # {{s/p}}
    "s/p": "italic('sem plural')",
    # {{signBr|a}}
    "signBr": "f'{italic(f\"Este significado é de uso comum no Brasil. Um semelhante pode ser encontrado em: {strong(parts[-1])}\")}'",
    # {{signPt|a}}
    "signPt": "f'{italic(f\"Este significado é de uso comum em Portugal. Um semelhante pode ser encontrado em: {strong(parts[-1])}\")}'",
    # {{varort|tenu-|pt}}
    "varort": 'f"variante ortográfica de {strong(parts[1])}"',
}

# Templates that will be completed/replaced using custom style.
templates_other = {
    "-varort-": "Formas alternativas",
    "escopoGrafiaPort": "(grafia port.)",
    "escopoGrafiaBrasil": "(grafia bras.)",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "pt")
    []
    >>> find_genders("{{oxítona|ca|brum}}, {{mf}}", "pt")
    ['mf']
    >>> find_genders("'''COPOM''', {{m}}", "pt")
    ['m']
    """
    pattern = re.compile(r"{([fm]+)}")
    return unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "pt")
    []
    >>> find_pronunciations("{{AFI|/pɾe.ˈno.me̝/}}", "pt")
    ['/pɾe.ˈno.me̝/']
    >>> find_pronunciations("{{AFI|/pɾe.ˈno.me̝/|lang=pt}}", "pt")
    ['/pɾe.ˈno.me̝/']
    """
    pattern = re.compile(r"{AFI\|(/[^/]+/)")
    return unique(pattern.findall(code))


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be call in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["codelang", "grc"], "pt")
        'grego clássico'

        >>> last_template_handler(["etm", "la", "pt"], "pt")
        'latim'

        >>> last_template_handler(["la"], "pt")
        'Latim'

        >>> last_template_handler(["unknown", "test"], "pt")
        '<i>(Unknown)</i>'

        >>> last_template_handler(["xlatio", "it", "chimica", "f."], "pt")
        'chimica f.'
        >>> last_template_handler(["xlatio", "cu", "крикъ"], "pt")
        'крикъ'
    """
    from .. import defaults
    from .codelangs import codelangs
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

    match tpl:
        case "codelang":
            return codelangs[parts[0]]
        case "etm":
            return langs[parts[0]].lower()
        case "xlatio":
            return " ".join(parts[1:])

    # This is a country in the current locale
    if lang := langs.get(tpl):
        return lang.capitalize()

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://pt.wiktionary.org/wiki/Especial:RandomRootpage"


def adjust_wikicode(code: str, locale: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("=={{Substantivo|pt}}<sup>1</sup>==", "pt")
    '=={{Substantivo 1|pt}}=='
    >>> adjust_wikicode("==Substantivo<sup>2</sup>==", "pt")
    '=={{Substantivo 2}}=='

    >>> adjust_wikicode('#<li value="2"> [[toca]], [[covil]]', "pt")
    '# [[toca]], [[covil]]'

    >>> adjust_wikicode(":# [[plural]] [[de]] '''[[anão]]'''", "pt")
    '# {{flexion|anão}}'
    >>> adjust_wikicode("* [[plural]] [[de]] '''[[anão]]'''", "pt")
    '# {{flexion|anão}}'
    >>> adjust_wikicode("# [[plural]] [[de]] '''[[anão]]'''", "pt")
    '# {{flexion|anão}}'
    >>> adjust_wikicode("# plural de [[anão]]", "pt")
    '# {{flexion|anão}}'

    >>> adjust_wikicode("*{{f}} de [[objetivo]]", "pt")
    '# {{flexion|objetivo}}'

    >>> adjust_wikicode("# plural de [[anão]]", "pt")
    '# {{flexion|anão}}'
    >>> adjust_wikicode("# feminino plural de [[sardenho]]", "pt")
    '# {{flexion|sardenho}}'

    >>> adjust_wikicode("# [[terceira pessoa]] do [[plural]] do [[futuro do pretérito]] do verbo '''[[ensimesmar]]'''", "pt")
    '# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("#[[terceira]] [[pessoa]] do [[singular]]  do [[presente]] [[indicativo]]  do [[verbo]] '''[[ensimesmar]]'''", "pt")
    '# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("#terceira pessoa do singular  do presente indicativo  do verbo [[ensimesmar]]", "pt")
    '# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("# [[infinitivo pessoal]] da [[terceira pessoa]] do [[plural]] do verbo '''[[acarretar]]'''", "pt")
    '# {{flexion|acarretar}}'

    >>> adjust_wikicode("# [[particípio]] do verbo '''[[abotecar]]'''", "pt")
    '# {{flexion|abotecar}}'
    """
    # `=={{Substantivo|pt}}<sup>1</sup>==` → `=={{Substantivo 1|pt}}==`
    code = re.sub(r"==\s*\{\{Substantivo\|(\w+)\}\}\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \2|\1}}==", code)

    # `==Substantivo<sup>2</sup>==` → `=={{Substantivo 2}}==`
    code = re.sub(r"==\s*Substantivo\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \1}}==", code)

    # <li value="2"> → ''
    code = re.sub(r"<li [^>]+>", "", code)

    #
    # Variants
    #

    start = rf"^(?:{'|'.join(section_patterns)})\s*"

    # `# [[plural]] [[de]] '''[[anão]]'''` → `# {{flexion|anão}}`
    # `# plural de [[anão]]` → `# {{flexion|anão}}`
    # `# feminino plural de [[anão]]` → `# {{flexion|anão}}`
    code = re.sub(
        rf"{start}\[*(?:feminino)?\s*plural.+'*\[\[([^\]]+)+\].*",
        r"# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    # `# {{f}} de [[objetivo]]` → `# {{flexion|objetivo}}`
    code = re.sub(rf"{start}\{{\{{f\}}\}} de \[\[([^\]]+)+\].*", r"# {{flexion|\1}}", code, flags=re.MULTILINE)

    # `# [[terceira pessoa]] do [[plural]] do [[futuro do pretérito]] do verbo '''[[ensimesmar]]'''` → `# {{flexion|ensimesmar}}`
    # `#[[terceira]] [[pessoa]] do [[singular]]  do [[presente]] [[indicativo]]  do [[verbo]] '''[[ensimesmar]]'''` → `# {{flexion|ensimesmar}}`
    code = re.sub(
        rf"{start}\[?\[?.+ (?:da|do) \[?\[?.+ do \[?\[?.+ do \[*verbo\]* '*\[\[([^\]]+)+\].*",
        r"# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    # `# [[particípio]] do verbo '''[[abotecar]]'''` → `# {{flexion|abotecar}}`
    code = re.sub(
        rf"{start}\[?\[?(?:gerúndio|particípio)\]?\]? do \[*verbo\]* '*\[\[([^\]]+)+\].*",
        r"# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    return code
