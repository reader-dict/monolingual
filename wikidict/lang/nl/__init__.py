"""Dutch language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://nl.wiktionary.org/wiki/Speciaal:WillekeurigeUitCategorie/Woorden_in_het_Nederlands"

template_trans = "Sjabloon"

float_separator = ","
thousands_separator = " "

section_patterns = ("#", r"\*")
sublist_patterns = ("#", r"\*")
section_sublevels = (3, 4)
head_sections = ("{{nld}}", "{{qtu}}")
etyl_section = ("{{etym}}",)
sections = (
    *etyl_section,
    "{{abbr",
    "{{adjc",
    "{{decl",
    "{{expr",
    "{{interj",
    "{{name",
    "{{note",
    "{{noun",
    "{{pref",
    "{{prep",
    "{{pronom",
    "{{prov",
    "{{symbool",
    "{{syn",
    "{{verb",
)

variant_templates = (
    "{{flexion",
    "{{noun-dim",
    "{{noun-dim-pl",
    "{{noun-pl",
)

reverse_variant_titles = ("{{adjcomp", "{{-nlnoun-", "{{-nlverb-")
reverse_variant_templates = ("{{rev-flexion",)

# https://nl.wiktionary.org/wiki/WikiWoordenboek:Genus#Nederlands
GENDERS = {
    "c": "g",
    "f": "v",
    "g": "g",
    "m": "m",
    "n": "o",
    "o": "o",
    "p": "mv",
    "v": "v",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "nl")
    []
    >>> find_genders("{{-l-|0}}", "nl")
    []
    >>> find_genders("{{-l-|f}}", "nl")
    ['v']
    >>> find_genders("{{-l-|mf}}", "nl")
    ['m', 'v']
    """
    pattern = re.compile(r"\{\{-l-\|(\w+)\}\}")
    for match in pattern.findall(code):
        return utils.unique(utils.flatten(sorted(GENDERS[m] for m in match if m != "0")))
    return []


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "nl")
    []

    >>> find_pronunciations("{{IPA|/ɑː/|ang}}", "nl")
    ['/ɑː/']

    >>> _ = context.reset("nl")

    >>> context.new_word("isolatiebedrijven")
    >>> find_pronunciations("{{IPA-nl-standaard|izoˈla(t)sibəˌdrɛivə(n)}}", "nl")
    ['/izoˈla(t)sibəˌdrɛivə(n)/']

    >>> context.new_word("turflucifer")
    >>> find_pronunciations("{{IPA-nl-standaard|plaatshouder taxonomie}}", "nl")
    []
    """
    res: list[str] = []
    for pattern in [
        r"\{\{IPA\|([^|}]+)",
        r"\{\{IPA-nl-standaard\|[^}]+\}\}",
    ]:
        for match in re.findall(pattern, code):
            if "IPA-nl-standaard" in match:
                expanded = context.expand(match, "nl")
                if "&#x202F;" in expanded:
                    res.append(f"/{expanded.split('&#x202F;')[-2]}/")
            else:
                res.append(match)
    return res


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> _ = context.reset("nl")

    >>> context.new_word("pover")
    >>> adjust_wikicode("{{adjcomp|p=1|{{pn}}|[[{{pn}}e]]|[[{{pn}}der]]|[[{{pn}}dere]]|[[{{pn}}st]]|[[{{pn}}ste]]|part=[[{{pn}}s]]|partcomp=[[{{pn}}ders]]}}", "nl", word="pover")
    '==={{noun}}===\n# {{rev-flexion|poverder}}\n# {{rev-flexion|poverdere}}\n# {{rev-flexion|poverders}}\n# {{rev-flexion|povere}}\n# {{rev-flexion|povers}}\n# {{rev-flexion|poverst}}\n# {{rev-flexion|poverste}}'

    >>> context.new_word("B")
    >>> adjust_wikicode("{{-nlnoun-|{{QZ|{{pn}}|nld}}|[[{{pn}}'s]]|[[{{pn}}'tje]]|[[{{pn}}'tjes]]}}", "nl", word="B")
    "==={{noun}}===\n# {{rev-flexion|B's}}\n# {{rev-flexion|B'tje}}\n# {{rev-flexion|B'tjes}}"

    >>> context.new_word("nikkel")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|-|[[nikkeltje]](2)|[[nikkeltjes]](2)}}", "nl", word="nikkel")
    '==={{noun}}===\n# {{rev-flexion|nikkeltje}}\n# {{rev-flexion|nikkeltjes}}'

    >>> context.new_word("canzone")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[canzones]]<br/>[[canzonen]] ''(verouderd)''<br/>[[canzone's]] ''(meer Italiaans)''|-|-}}", "nl", word="canzone")
    "==={{noun}}===\n# {{rev-flexion|canzone's}}\n# {{rev-flexion|canzonen}}\n# {{rev-flexion|canzones}}"

    >>> context.new_word("get")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[gitien]] (Hebreeuws),<br />[[getten]] (Jiddisj)|-|-|2.|[A]}}", "nl", word="get")
    '==={{noun}}===\n# {{rev-flexion|getten}}\n# {{rev-flexion|gitien}}'

    >>> context.new_word("Aborigine")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|''(lang)'' [[Aborigine's]]<br>''(verkort)'' [[Aborigines]]|||}}", "nl", word="Aborigine")
    "==={{noun}}===\n# {{rev-flexion|Aborigine's}}\n# {{rev-flexion|Aborigines}}"

    >>> context.new_word("ijzer(III)fosfaat")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[ijzer(III)fosfaten]]}}", "nl", word="ijzer(III)fosfaat")
    '==={{noun}}===\n# {{rev-flexion|ijzer(III)fosfaten}}'

    >>> context.new_word("butin")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[burins]]|([[burintje]]) [[#Opmerkingen|*]]|([[burintjes]]) [[#Opmerkingen|*]]}}", "nl", word="butin")
    '==={{noun}}===\n# {{rev-flexion|burins}}\n# {{rev-flexion|burintje}}\n# {{rev-flexion|burintjes}}'

    >>> context.new_word("stichter")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}s]]|\n''([[{{pn}}tje]])''|''([[{{pn}}tjes]])''}}", "nl", word="stichter")
    '==={{noun}}===\n# {{rev-flexion|stichters}}\n# {{rev-flexion|stichtertje}}\n# {{rev-flexion|stichtertjes}}'

    >>> context.new_word("rekenmachine")
    >>> adjust_wikicode("{{-nlverb-|{{pn}}|[[{{pn}}s]]|([[{{pn}}tje]])<br/>[[rekenmachientje]]|([[{{pn}}tjes]])|vd=[[rekenmachientjes]]}}", "nl", word="rekenmachine")
    '==={{noun}}===\n# {{rev-flexion|rekenmachientje}}\n# {{rev-flexion|rekenmachientjes}}\n# {{rev-flexion|rekenmachines}}\n# {{rev-flexion|rekenmachinetje}}\n# {{rev-flexion|rekenmachinetjes}}'

    >>> context.new_word("blad")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}en]]<br>[[{{pn}}eren]]<br>[[blaren]]|[[blaadje]]|[[blaadjes]], ([[{{pn}}ertjes]])|1.}}", "nl", word="blad")
    '==={{noun}}===\n# {{rev-flexion|blaadje}}\n# {{rev-flexion|blaadjes}}\n# {{rev-flexion|bladen}}\n# {{rev-flexion|bladeren}}\n# {{rev-flexion|bladertjes}}\n# {{rev-flexion|blaren}}'

    >>> context.new_word("binnenbarbecue")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[binnenbarbecues]]|([[binnenbarbecuetje]]) [1]|([[binnenbarbecuetjes]]) [1]}}", "nl", word="binnenbarbecue")
    '==={{noun}}===\n# {{rev-flexion|binnenbarbecues}}\n# {{rev-flexion|binnenbarbecuetje}}\n# {{rev-flexion|binnenbarbecuetjes}}'
    """
    # Special handling for genders (`{{-l-|m}}`)
    code = code.replace("{{-l-|", "::: {{-l-|")

    # Replace all word occurrences
    code = code.replace("{{pn}}", word)

    # {{=nld=}} → == {{nld}} ==
    code = re.sub(r"^\{\{=(.+)=\}\}", r"== {{\1}} ==", code, flags=re.MULTILINE)

    # {{-etym-}} → === {{etym}} ===
    code = re.sub(r"^\{\{-(\w+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # {{-noun-|0}} → === {{noun}} ===
    code = re.sub(r"^\{\{-(\w+)-\|\d+\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # {{-noun-|ANY}} → === {{noun|ANY}} ===
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

    #
    # Variants
    #

    # {{noun-pl|isolatiebedrijf}} → # {{noun-pl|isolatiebedrijf}}
    if "noun-pl" in code:
        code = re.sub(r"^(\{\{noun-pl\|[^}]+\}\})", r"# \1", code, flags=re.MULTILINE)

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
                cleaned.append("==={{noun}}===")

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip().replace("''", "")
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
