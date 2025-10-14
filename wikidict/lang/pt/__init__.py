"""Portuguese language."""

import re

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
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
section_sublevels = (2, 3)
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
    "conjugação",
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

reverse_variant_titles = (
    "{{conj/",
    "{{flex.",
)
reverse_variant_templates = ("{{rev-flexion",)

definitions_to_ignore = ("peçodef",)

templates_ignored = (
    "{{?",
    "{{camonismo",  # ? (it is append in https://pt.wiktionary.org/wiki/Calisto)
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
    r"""
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
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=formolado|mp=formolados|fs=formolada|fp=formoladas}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|formolada}}\n# {{rev-flexion|formoladas}}\n# {{rev-flexion|formolado}}\n# {{rev-flexion|formolados}}'

    >>> context.new_word("focinho")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=focinho|mp=focinhos|ms-div=fo.<u>ci</u>.nho{{#if:|<br/>{{{3}}}o}}|mp-div=fo.<u>ci</u>.nhos{{#if:|<br/>{{{3}}}os}}}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|focinho}}\n# {{rev-flexion|focinhos}}'

    >>> context.new_word("che")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.gl|ms=che|mp=ches}} (è)", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|che}}\n# {{rev-flexion|ches}}'

    >>> context.new_word("kelvinometria")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|fs=kelvinometria|fp=kelvinometrias|fs-div={{{2}}}a|fp-div={{{2}}}as}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|kelvinometria}}\n# {{rev-flexion|kelvinometrias}}'

    >>> context.new_word("abaixador")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=abaixador|mp=abaixadores|fs=abaixadora|fp=abaixadoras |ms-div=a.bai.xa.<u>dor</u>|mp-div=a.bai.xa.<u>do</u>.res|fs-div=a.bai.xa.<u>do</u>.ra|fp-div=a.bai.xa.<u>do</u>.ras}}{{oxítona|a|bai|xa|dor}} {{datação|século XIV|pt}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|abaixador}}\n# {{rev-flexion|abaixadora}}\n# {{rev-flexion|abaixadoras}}\n# {{rev-flexion|abaixadores}}'
    """
    # `=={{Substantivo|pt}}<sup>1</sup>==` → `=={{Substantivo 1|pt}}==`
    code = re.sub(r"==\s*\{\{Substantivo\|(\w+)\}\}\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \2|\1}}==", code)

    # `==Substantivo<sup>2</sup>==` → `=={{Substantivo 2}}==`
    code = re.sub(r"==\s*Substantivo\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \1}}==", code)

    # <li value="2"> → ''
    code = re.sub(r"<li [^>]+>", "", code)

    # `={{-pt-}}=\n{{flex.}}` → `={{-pt-}}=\n==Substantivo==\n{{flex.}}`
    code = re.sub(r"=\s*{{-pt-}}\s*=\n{{flex", r"={{-pt-}}=\n==Substantivo==\n{{flex", code)

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

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
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

                    # Apply some clean-up to prevent breaking everything
                    if "#if:" in tpl_code:
                        # `{{flex.pt|ms=focinho|mp=focinhos|ms-div=fo.<u>ci</u>.nho{{#if:|<br/>{{{3}}}o}}|mp-div=fo.<u>ci</u>.nhos{{#if:|<br/>{{{3}}}os}}}}`
                        tpl_code = re.sub(r"\{\{#if:\|<br/>\{\{\{\d\}\}\}[^}]*}}", "", tpl_code)
                    if "{{" in tpl_code:
                        # `{{flex.pt|fs=kelvinometria|fp=kelvinometrias|fs-div={{{2}}}a|fp-div={{{2}}}as}}`
                        tpl_code = re.sub(r"=\{{3}+\d\}{3}", "=", tpl_code)
                    if "-div" in tpl_code:
                        tpl_code = re.sub(r"\s*\|\w+-div=[^|}]+", "", tpl_code)

                    # Remove unrelated templates after a reverse variant one
                    # `{{flex.pt|...}}{{oxítona|a|bai|xa|dor}} {{datação|século XIV|pt}}` → `{{flex.pt|...}}`
                    tpl_code = re.split(r"}}\s*\{\{", tpl_code, maxsplit=1)[0]
                    if not tpl_code.endswith("}}"):
                        tpl_code += "}}"

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
