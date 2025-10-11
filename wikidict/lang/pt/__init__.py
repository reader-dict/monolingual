"""Portuguese language."""

import re

from ... import utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://pt.wiktionary.org/wiki/Especial:RandomRootpage"

module_trans = "Módulo"
template_trans = "Predefinição"

float_separator = ","
thousands_separator = " "

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

variant_titles = sections
variant_templates = ("{{flexion",)

reverse_variant_titles = ("{{flex.pt",)
reverse_variant_templates = ("{{rev-flexion",)

definitions_to_ignore = ("peçodef",)

templates_ignored = (
    "{{?",
    "{{cont",  # incomplete
)


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
    return utils.unique(pattern.findall(code))


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
    return utils.unique(pattern.findall(code))


START = rf"^(?:{'|'.join(section_patterns)})\s*"
PATTERNS = [
    # [[plural]] [[de]] '''[[anão]]'''
    # plural de [[anão]]
    # feminino plural de [[anão]]
    r"\[*(?:feminino)?\s*plural.+'*\[\[([^\]]+)+\].*",
    # {{f}} de [[objetivo]]
    r"\{\{f\}\} de \[\[([^\]]+)+\]",
    # [[terceira pessoa]] do [[plural]] do [[futuro do pretérito]] do verbo '''[[ensimesmar]]'''
    # [[terceira]] [[pessoa]] do [[singular]]  do [[presente]] [[indicativo]]  do [[verbo]] '''[[ensimesmar]]'''
    r"\[?\[?.+ (?:da|do).+do.+do \[*verbo\]* '*\[\[([^\]]+)+\]",
    # [[particípio]] do verbo '''[[abotecar]]'''
    r"\[?\[?(?:gerúndio|particípio)\]?\]? do \[*verbo\]* '*\[\[([^\]]+)+\]",
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
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

    >>> from ... import context
    >>> _ = context.reset("pt")
    >>> context.new_word("formolado")
    >>> adjust_wikicode("{{flex.pt|ms=formolado|mp=formolados|fs=formolada|fp=formoladas}}", "pt")
    ''
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

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(START, line):
            for pattern in PATTERNS:
                line, count = re.subn(rf"{START}{pattern}.*", r"# {{flexion|\1}}", line, count=1, flags=re.IGNORECASE)  # noqa: PLW2901
                if count:
                    break
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    if any(tpl in code for tpl in reverse_variant_titles):
        cleaned: list[str] = []
        in_expected_section = False
        expected_section = (f"= {{{{-{locale}-}}", f"={{{{-{locale}-}}")
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
