"""Portuguese language."""

import re

from ... import lang, utils
from ..pl import extract_templates
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
section_sublevels = (2, 3, 4)
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
    # "caractere",  # See #2634
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
    # "letra",  # See #2634
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
    "plural",
    "pospositivo",
    "prefixo",
    "preposição",
    "pronome",
    "provérbio",
    "sigla",
    "símbolo",
    "sinônimo",
    "sinônimos",
    "sinónimo",
    "sinónimos",
    "subfijo",
    "substantivo",
    "sufixo",
    "topónimo",
    "verbal",
    "verbo",
]
_sections.extend(f"pepb|{s}" for s in _sections.copy())
_sections.extend(f"{{{{{s}" for s in _sections.copy())
_sections.extend(etyl_section)
sections = tuple(_sections)

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
    r"""
    >>> find_genders("", "pt")
    []
    >>> find_genders("{{oxítona|ca|brum}}, {{mf}}", "pt")
    ['mf']
    >>> find_genders("'''COPOM''', {{m}}", "pt")
    ['m']
    >>> find_genders("{{oxítona|ta|tu}}, {{gramática|f}}", "pt")
    ['f']
    >>> find_genders("{{oxítona|ta|tu}}, {{g|f}}", "pt")
    ['f']
    >>> find_genders("{{oxítona|ta|tu}}, {{g|c}}", "pt")
    ['c']
    >>> find_genders("{{paroxítona|pau|lis|ta}}, {{c2g}}", "pt")
    ['mf']
    >>> find_genders("{{paroxítona|pau|lis|ta}}, {{gramática|2g}}", "pt")
    ['mf']
    >>> find_genders("'''ANTT''', {{gramática|f}}\n'''ANTT''', {{gramática|m}}", "pt")
    ['mf']
    >>> find_genders("{{paroxítona|an|go|la}} {{gramática|2g}}\n{{paroxítona|an|go|la}} {{gramática|m}}\n{{paroxítona|an|go|la}} {{gramática|f}}", "pt")
    ['mf']
    """
    pattern = re.compile(r"\{\{(?:(?:g|gramática)\|)?([fmc2g]+)\}")
    res: set[str] = set()
    for gender in pattern.findall(code):
        if gender in ("2g", "c2g"):
            res.update(("f", "m"))
        elif gender == "gc":
            res.add("c")
        else:
            res.add(gender)
    if sorted(res) == ["f", "m"]:
        return ["mf"]
    return utils.unique(sorted(res))


def find_pronunciations(code: str, locale: str) -> list[str]:
    r"""
    >>> find_pronunciations("", "pt")
    []

    >>> find_pronunciations("=={{pronúncia|pt}}==\n===Brasil===\n* [[AFI]]: {{AFI|/bu.'se.ta/}}", "pt")
    ["BR: /bu.'se.ta/"]
    >>> find_pronunciations("=={{pronúncia|pt}}==\n===Brasil===\n* [[AFI]]: /bu.'se.ta/", "pt")
    ["BR: /bu.'se.ta/"]

    >>> find_pronunciations("=={{pronúncia|pt}}==\n===Portugal===\n* AFI: {{AFI|/bɐ.ˈteɾ/}}", "pt")
    ['PT: /bɐ.ˈteɾ/']

    >>> find_pronunciations("=={{Pronúncia|pt}}==\n===Brasil===\n====Paulistana e Caipira====\n* [[AFI]]: {{AFI|[aw.ˈgẽj]}}\n* [[X-SAMPA]]: /aw.\"ge~j/\n===Portugal===\n* AFI: {{AFI|/aɫ.ˈɡɐ̃j̃/}}", "pt")
    ['PT: /aɫ.ˈɡɐ̃j̃/', 'BR: /aw.ˈgẽj/']
    """
    lines: list[str] = []
    in_section = False
    was_in_section = False
    for line in code.splitlines():
        if line.startswith(("=={", "== {")):
            in_section = "pronúncia" in line.lower()
        elif in_section:
            was_in_section = True
            if (line.startswith("=") and not line.startswith("====")) or "AFI" in line:
                lines.append(line.strip())
        elif was_in_section:
            break

    if not lines:
        return []

    pronunciations = {"PT": "", "BR": ""}
    kind = ""
    for line in lines:
        if "=Portugal=" in line:
            kind = "PT"
            continue
        elif "=Brasil=" in line:
            kind = "BR"
            continue

        if (
            kind
            and not pronunciations[kind]
            and (prons := re.findall(r"/([^/]+)/", line) or re.findall(r"\{AFI\|\[([^\]]+)\]", line))
        ):
            pron = prons[0].replace("''", "")
            pronunciations[kind] = f"/{pron}/"

    # `reverse=True` because we want "PT" first, then "BR"
    return sorted((f"{kind}: {pron}" for kind, pron in pronunciations.items() if pron), reverse=True)


START = rf"^(?:{'|'.join(section_patterns)})\s*"
PATTERNS = [
    # [[plural]] [[de]] '''[[anão]]'''
    # plural de [[anão]]
    # feminino plural de [[anão]]
    # plural de '''[[úlcera#{{pt}}|úlcera]]'''
    r"\[*(?:feminino)?\s*plural.+'*\[\[([^#\]]+)",
    # {{f}} de [[objetivo]]
    r"\{\{f\}\} de \[\[([^\]]+)+\]",
    # feminino de '''[[frito#Português|frito]]'''
    r"feminino de '*\[\[([^#\]]+)",
    # [[terceira pessoa]] do [[plural]] do [[futuro do pretérito]] do verbo '''[[ensimesmar]]'''
    # [[terceira]] [[pessoa]] do [[singular]]  do [[presente]] [[indicativo]]  do [[verbo]] '''[[ensimesmar]]'''
    # [[infinitivo pessoal]] da segunda pessoa do plural do verbo '''amar'''
    r"\[?\[?.+ (?:da|do).+do.+do \[*verbo\]* '*\[*([^'#\]]+)",
    # [[particípio]] do verbo '''[[abotecar]]'''
    r"\[?\[?(?:gerúndio|particípio)\]?\]? do \[*verbo\]* '*\[\[([^#\]]+)",
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
    >>> adjust_wikicode("={{-pt-}}=\n=={{Substantivo|pt}}<sup>1</sup>==", "pt")
    '={{-pt-}}=\n=={{Substantivo 1|pt}}=='
    >>> adjust_wikicode("={{-pt-}}=\n==Substantivo<sup>2</sup>==", "pt")
    '={{-pt-}}=\n=={{Substantivo 2}}=='

    >>> adjust_wikicode('={{-pt-}}=\n#<li value="2"> [[toca]], [[covil]]', "pt")
    '={{-pt-}}=\n# [[toca]], [[covil]]'

    >>> adjust_wikicode("={{-pt-}}=\n:# [[plural]] [[de]] '''[[anão]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|anão}}'
    >>> adjust_wikicode("={{-pt-}}=\n* [[plural]] [[de]] '''[[anão]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|anão}}'
    >>> adjust_wikicode("={{-pt-}}=\n# [[plural]] [[de]] '''[[anão]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|anão}}'
    >>> adjust_wikicode("={{-pt-}}=\n# plural de [[anão]]", "pt")
    '={{-pt-}}=\n# {{flexion|anão}}'

    >>> adjust_wikicode("={{-pt-}}=\n*{{f}} de [[objetivo]]", "pt")
    '={{-pt-}}=\n# {{flexion|objetivo}}'

    >>> adjust_wikicode("={{-pt-}}=\n# plural de [[anão]]", "pt")
    '={{-pt-}}=\n# {{flexion|anão}}'
    >>> adjust_wikicode("={{-pt-}}=\n# feminino plural de [[sardenho]]", "pt")
    '={{-pt-}}=\n# {{flexion|sardenho}}'
    >>> adjust_wikicode("={{-pt-}}=\n# feminino de '''[[frito#Português|frito]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|frito}}'

    >>> adjust_wikicode("={{-pt-}}=\n# [[infinitivo pessoal]] da segunda pessoa do plural do verbo '''amar'''", "pt")
    '={{-pt-}}=\n# {{flexion|amar}}'
    >>> adjust_wikicode("={{-pt-}}=\n# [[terceira pessoa]] do [[plural]] do [[futuro do pretérito]] do verbo '''[[ensimesmar]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("={{-pt-}}=\n#[[terceira]] [[pessoa]] do [[singular]]  do [[presente]] [[indicativo]]  do [[verbo]] '''[[ensimesmar]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("={{-pt-}}=\n#terceira pessoa do singular  do presente indicativo  do verbo [[ensimesmar]]", "pt")
    '={{-pt-}}=\n# {{flexion|ensimesmar}}'
    >>> adjust_wikicode("={{-pt-}}=\n# [[infinitivo pessoal]] da [[terceira pessoa]] do [[plural]] do verbo '''[[acarretar]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|acarretar}}'
    >>> adjust_wikicode("={{-pt-}}=\n# [[masculino]] [[singular]] do [[particípio]] [[passado]] do [[verbo]] '''[[achatar#{{pt}}|achatar]]'''.", "pt")
    '={{-pt-}}=\n# {{flexion|achatar}}'

    >>> adjust_wikicode("={{-pt-}}=\n# [[particípio]] do verbo '''[[abotecar]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|abotecar}}'

    >>> adjust_wikicode("={{-pt-}}=\n#plural de '''[[úlcera#{{pt}}|úlcera]]'''", "pt")
    '={{-pt-}}=\n# {{flexion|úlcera}}'

    >>> adjust_wikicode("={{-pt-}}=\n'''anões''' ''masculino ''", "pt")
    "={{-pt-}}=\n'''anões''' '{{m}}"

    >>> from ... import context
    >>> _ = context.reset("pt")

    >>> context.new_word("formolado")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=formolado|mp=formolados|fs=formolada|fp=formoladas}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|formolada}}\n# {{rev-flexion|formoladas}}\n# {{rev-flexion|formolados}}'

    >>> context.new_word("focinho")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=focinho|mp=focinhos|ms-div=fo.<u>ci</u>.nho{{#if:|<br/>{{{3}}}o}}|mp-div=fo.<u>ci</u>.nhos{{#if:|<br/>{{{3}}}os}}}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|focinhos}}'

    >>> context.new_word("che")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.gl|ms=che|mp=ches}} (è)", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|ches}}'

    >>> context.new_word("kelvinometria")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|fs=kelvinometria|fp=kelvinometrias|fs-div={{{2}}}a|fp-div={{{2}}}as}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|kelvinometrias}}'

    >>> context.new_word("abaixador")
    >>> adjust_wikicode("={{-pt-}}=\n{{flex.pt|ms=abaixador|mp=abaixadores|fs=abaixadora|fp=abaixadoras |ms-div=a.bai.xa.<u>dor</u>|mp-div=a.bai.xa.<u>do</u>.res|fs-div=a.bai.xa.<u>do</u>.ra|fp-div=a.bai.xa.<u>do</u>.ras}}{{oxítona|a|bai|xa|dor}} {{datação|século XIV|pt}}", "pt")
    '={{-pt-}}=\n==Substantivo==\n# {{rev-flexion|abaixadora}}\n# {{rev-flexion|abaixadoras}}\n# {{rev-flexion|abaixadores}}\n{{oxítona|a|bai|xa|dor}}\n{{datação|século XIV|pt}}'
    """
    # `=={{Substantivo|pt}}<sup>1</sup>==` → `=={{Substantivo 1|pt}}==`
    code = re.sub(r"==\s*\{\{Substantivo\|(\w+)\}\}\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \2|\1}}==", code)

    # `==Substantivo<sup>2</sup>==` → `=={{Substantivo 2}}==`
    code = re.sub(r"==\s*Substantivo\s*<sup>(\d)</sup>\s*==", r"=={{Substantivo \1}}==", code)

    # <li value="2"> → ''
    code = re.sub(r"<li [^>]+>", "", code)

    # `={{-pt-}}=\n{{flex.}}` → `={{-pt-}}=\n==Substantivo==\n{{flex.}}`
    code = re.sub(r"=\s*{{-pt-}}\s*=\n{{flex", r"={{-pt-}}=\n==Substantivo==\n{{flex", code)

    # Try to find more genders
    # `'''anões''' ''masculino ''` → `'''anões''' {{m}}`
    code = re.sub(
        r"^([{']+.*)[ ']+(feminino|masculino)[ ']+",
        lambda m: f"{m[1]}{{{{{m[2][0]}}}}}",
        code,
        flags=re.MULTILINE,
    )

    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(START, line):
            for pattern in PATTERNS:
                line, count = re.subn(rf"{START}{pattern}.*", r"# {{flexion|\1}}", line, count=1, flags=re.IGNORECASE)
                if count:
                    break
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        lines.clear()
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    for tpl_sub in extract_templates(tpl_code):
                        # Apply some clean-up to prevent breaking everything
                        if "#if:" in tpl_sub:
                            # `{{flex.pt|ms=focinho|mp=focinhos|ms-div=fo.<u>ci</u>.nho{{#if:|<br/>{{{3}}}o}}|mp-div=fo.<u>ci</u>.nhos{{#if:|<br/>{{{3}}}os}}}}`
                            tpl_sub = re.sub(r"\{\{#if:\|<br/>\{\{\{\d\}\}\}[^}]*}}", "", tpl_sub)
                        if tpl_sub.count("{{") > 1:
                            # `{{flex.pt|fs=kelvinometria|fp=kelvinometrias|fs-div={{{2}}}a|fp-div={{{2}}}as}}`
                            tpl_sub = re.sub(r"=\{{3}+\d\}{3}", "=", tpl_sub)
                        if "-div" in tpl_sub and tpl_sub.count("{{") == 1:
                            tpl_sub = re.sub(r"\s*\|\w+-div=[^|}]+", "", tpl_sub)

                        if not tpl_sub.startswith(interesting_reverse_variant_titles):
                            lines.append(tpl_sub)
                            continue

                        tpl_name = tpl_sub[2 : max(0, tpl_sub.find("|")) or tpl_sub.find("}")].strip()
                        variant_handlers_mod.append_to_reverse_variants(tpl_name)
                        forms = utils.process_templates(
                            word,
                            tpl_sub,
                            locale,
                            templates_status=templates_status,
                            variant_only=True,
                        )
                        lines.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

                    tpl_code = ""
                    in_tpl = False
            else:
                lines.append(line)

        code = "\n".join(lines)

    return code
