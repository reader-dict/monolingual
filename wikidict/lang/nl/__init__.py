"""Dutch language."""

import re

from ... import context, utils
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

variant_titles = sections
variant_templates = (
    "{{flexion",
    "{{noun-dim",
    "{{noun-dim-pl",
    "{{noun-pl",
)

reverse_variant_titles = "{{-nlnoun-"
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{audio",
    "{{sound",
)

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


IGNORED_VARIANTS = {"#Opmerkingen", "alternatief:"}


def cleanup_rev_variant(matches: re.Match[str]) -> str:
    variants = re.sub(r"<br\s*/?>", "|", matches[1])
    return "\n".join(
        f"# {{{{rev-flexion|{sm}}}}}"
        for variant in variants.split("|")
        if (
            (
                sm := variant.strip()
                .split("=", 1)[-1]
                .replace("(lang)", "")
                .replace("(verkort)", "")
                .split(" (", 1)[0]
                .split(" ''(", 1)[0]
                .split(") ", 1)[0]
                .replace("]", "")
                .strip(" []()'-,")
            )
            and (sm := re.sub(r"\s*\(?\d[).]?\s*", "", sm))
            and len(sm) > 1
            and sm not in IGNORED_VARIANTS
        )
    )


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("{{adjcomp|p=1|{{pn}}|[[{{pn}}e]]|[[{{pn}}der]]|[[{{pn}}dere]]|[[{{pn}}st]]|[[{{pn}}ste]]|part=[[{{pn}}s]]|partcomp=[[{{pn}}ders]]}}", "nl", word="pover")
    '==={{adjc}}===\n# {{rev-flexion|pover}}\n# {{rev-flexion|povere}}\n# {{rev-flexion|poverder}}\n# {{rev-flexion|poverdere}}\n# {{rev-flexion|poverst}}\n# {{rev-flexion|poverste}}\n# {{rev-flexion|povers}}\n# {{rev-flexion|poverders}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|-|[[nikkeltje]](2)|[[nikkeltjes]](2)}}", "nl", word="nikkel")
    '==={{noun}}===\n# {{rev-flexion|nikkel}}\n# {{rev-flexion|nikkeltje}}\n# {{rev-flexion|nikkeltjes}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[canzones]]<br/>[[canzonen]] ''(verouderd)''<br/>[[canzone's]] ''(meer Italiaans)''|-|-}}", "nl", word="canzone")
    "==={{noun}}===\n# {{rev-flexion|canzone}}\n# {{rev-flexion|canzones}}\n# {{rev-flexion|canzonen}}\n# {{rev-flexion|canzone's}}"

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[gitien]] (Hebreeuws),<br />[[getten]] (Jiddisj)|-|-|2.|[A]}}", "nl", word="get")
    '==={{noun}}===\n# {{rev-flexion|get}}\n# {{rev-flexion|gitien}}\n# {{rev-flexion|getten}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|''(lang)'' [[Aborigine's]]<br>''(verkort)'' [[Aborigines]]|||}}", "nl", word="Aborigine")
    "==={{noun}}===\n# {{rev-flexion|Aborigine}}\n# {{rev-flexion|Aborigine's}}\n# {{rev-flexion|Aborigines}}"

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[ijzer(III)fosfaten]]}}", "nl", word="ijzer(III)fosfaat")
    '==={{noun}}===\n# {{rev-flexion|ijzer(III)fosfaat}}\n# {{rev-flexion|ijzer(III)fosfaten}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[burins]]|([[burintje]]) [[#Opmerkingen|*]]|([[burintjes]]) [[#Opmerkingen|*]]}}", "nl", word="butin")
    '==={{noun}}===\n# {{rev-flexion|butin}}\n# {{rev-flexion|burins}}\n# {{rev-flexion|burintje}}\n# {{rev-flexion|burintjes}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}s]]|''([[{{pn}}tje]])''|''([[{{pn}}tjes]])''}}", "nl", word="stichter")
    '==={{noun}}===\n# {{rev-flexion|stichter}}\n# {{rev-flexion|stichters}}\n# {{rev-flexion|stichtertje}}\n# {{rev-flexion|stichtertjes}}'

    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}s]]|\n''([[{{pn}}tje]])''|\n''([[{{pn}}tjes]])''\n}}", "nl", word="stichter")
    '==={{noun}}===\n# {{rev-flexion|stichter}}\n# {{rev-flexion|stichters}}\n# {{rev-flexion|stichtertje}}\n# {{rev-flexion|stichtertjes}}'

    >>> adjust_wikicode("{{-nlverb-|{{pn}}|[[{{pn}}s]]|([[{{pn}}tje]])<br/>[[rekenmachientje]]|([[{{pn}}tjes]])|vd=[[rekenmachientjes]]}}", "nl", word="rekenmachine")
    '==={{verb}}===\n# {{rev-flexion|rekenmachine}}\n# {{rev-flexion|rekenmachines}}\n# {{rev-flexion|rekenmachinetje}}\n# {{rev-flexion|rekenmachientje}}\n# {{rev-flexion|rekenmachinetjes}}\n# {{rev-flexion|rekenmachientjes}}'
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

    # {{adjcomp|...}}
    if "{{adjcomp" in code:
        code = code.replace("{{adjcomp", "==={{adjc}}===\n{{adjcomp")
        code = re.sub(r"^\{\{adjcomp\|([^}]+)\}\}", cleanup_rev_variant, code, flags=re.MULTILINE)

    # {{-nlnoun-|...}}
    if f"-{locale}noun-" in code:
        code = code.replace(f"{{{{-{locale}noun-", f"==={{{{noun}}}}===\n{{{{-{locale}noun-")
        code = re.sub(rf"^\{{\{{-{locale}noun-\|([^}}]+)\}}\}}", cleanup_rev_variant, code, flags=re.MULTILINE)

    # {{-nlverb-|...}}
    if f"-{locale}verb-" in code:
        code = code.replace(f"{{{{-{locale}verb-", f"==={{{{verb}}}}===\n{{{{-{locale}verb-")
        code = re.sub(rf"^\{{\{{-{locale}verb-\|([^}}]+)\}}\}}", cleanup_rev_variant, code, flags=re.MULTILINE)

    return code
