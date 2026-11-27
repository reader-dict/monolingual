"""Dutch language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]  # the folder name, on any OS

random_word_url = "https://nl.wiktionary.org/wiki/Speciaal:WillekeurigeUitCategorie/Woorden_in_het_Nederlands"

template_trans = "Sjabloon"

section_patterns = ("#", r"\*")
sublist_patterns = ("#", r"\*")
section_sublevels = (3, 4)
head_sections = ("{{nld}}", "{{qtu}}")
etyl_section = ("{{etym}}",)
sections = (
    *etyl_section,
    "{{abbr",
    "{{adjc",
    "{{adverb",
    "{{art",
    "{{conj",
    "{{cont",
    "{{decl",
    "{{expr",
    "{{inter",
    "{{name",
    "{{note",
    "{{noun",
    "{{num",
    "{{ordn",
    "{{pref",
    "{{prep",
    "{{phrase",
    "{{post",
    "{{pron-adv",
    "{{pronom",
    "{{prov",
    "{{suff",
    "{{symbool",
    "{{syn",
    "{{verb",
)

variant_templates = (
    "{{1ps",
    "{{2ps",
    "{{flexion",
    "{{nl-adjc-form",
    "{{noun-dim",
    "{{noun-dim-pl",
    "{{noun-pl",
    "{{ovt-enk",
    "{{ovt-mv",
    "{{tps",
    "{{volt-d",
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
    "p": ["m", "v"],
    "v": "v",
}


RE_GENDERS = re.compile(r"\{\{-l-\|(\w++)\}\}")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", LANG)
    []
    >>> find_genders("{{-l-|0}}", LANG)
    []
    >>> find_genders("{{-l-|f}}", LANG)
    ['v']
    >>> find_genders("{{-l-|mf}}", LANG)
    ['m', 'v']
    >>> find_genders("{{-l-|mfn}}", LANG)
    ['m', 'o', 'v']
    """
    res: set[str] = set()
    for gender in RE_GENDERS.findall(code):
        if gender == "0":
            continue
        if "".join(sgen := sorted(gender)) in {"fm", "fmn", "mv"}:
            res.update(GENDERS[g] for g in sgen)  # type: ignore[misc]
        else:
            if gender == "p":
                res.update(GENDERS[gender])
            else:
                res.add(GENDERS[gender])  # type: ignore[arg-type]
    return utils.unique(sorted(res))


RE_FIND_PRONS_PATTERNS = [
    re.compile(r"\{\{IPA-nl-standaard\|[^}]++\}\}"),
    re.compile(r"\{\{IPA\|([^|}]++)"),
]
RE_PARENS = re.compile(r"[()]")


def find_pronunciations(code: str, locale: str) -> list[str]:
    r"""
    >>> find_pronunciations("", LANG)
    []

    >>> find_pronunciations("{{IPA|/ ɑː /|ang}}", LANG)
    ['/ɑː/']

    >>> _ = context.reset(LANG)

    >>> context.new_word("isolatiebedrijven")
    >>> find_pronunciations("{{IPA-nl-standaard| izoˈlatsibəˌdrɛivən }}", LANG)
    ['/izoˈlatsibəˌdrɛivən/']

    >>> context.new_word("turflucifer")
    >>> find_pronunciations("{{IPA-nl-standaard|plaatshouder taxonomie}}", LANG)
    []

    >>> context.new_word("era")
    >>> find_pronunciations("{{-pron-}}\n*{{WikiW|IPA}}: {{IPA-nl-standaard|ˈera}}\n**{{pron-reg|N=a}} {{IPA|/ɪːra/|nld}}\n**{{pron-reg|V=a|l=a}} {{IPA|/eːra/|nld}}", LANG)
    ['/ˈera/']
    """
    res: list[str] = []
    for pattern in RE_FIND_PRONS_PATTERNS:
        for match in pattern.findall(code):
            if "IPA-nl-standaard" in match:
                expanded = context.expand(match, LANG)
                if "&#x202F;" in expanded:
                    res.append(f"/{expanded.split('&#x202F;')[-2]}/")
            else:
                res.append(match)
        if res:
            break
    return [RE_PARENS.sub("", pron.replace("/ ", "/").replace(" /", "/")) for pron in res]


RE_NUMBERED = re.compile(r"\*\s*+((?:\[[\d\s,+–-]++\][\s,]*+)++):?\s*+(\S.*+)")
RE_FIND_NUMBERS = re.compile(r"(\d++)(?:\s*+[–-]\s*+(\d++))?")


def attach_synonyms(code: str) -> str:
    r"""
    Put the synonyms under their meaning, as a sub-definition, when they give its number: `*[1] [[bijgevolg]]`.
    The list is kept as it is when one of its lines has no number, or a number that is not the one of a meaning:
    `[1.1]` refers to a sub-meaning.

    >>> attach_synonyms("=== {{adverb|nld}} ===\n'''daardoor'''\n#door dat\n#: voorbeeld\n{{bijv-1|Het is warm.}}\n#fysiek\n=== {{syn}} ===\n\n*[1] [[bijgevolg]], [[dientengevolge]]\n=== {{trans}} ===")
    "=== {{adverb|nld}} ===\n'''daardoor'''\n#door dat\n#: voorbeeld\n## ''syn.:'' [[bijgevolg]], [[dientengevolge]]\n{{bijv-1|Het is warm.}}\n#fysiek\n=== {{trans}} ==="
    >>> attach_synonyms("=== {{verb|nld}} ===\n# een\n# twee\n# drie\n=== {{homo}} ===\n*[[x]]\n=== {{syn}} ===\n* [1, 3] [[a]],\n* [2]: [[b]]\n*[2-3] [[c]]")
    "=== {{verb|nld}} ===\n# een\n## ''syn.:'' [[a]]\n# twee\n## ''syn.:'' [[b]], [[c]]\n# drie\n## ''syn.:'' [[a]], [[c]]\n=== {{homo}} ===\n*[[x]]"
    >>> attach_synonyms("=== {{noun|nld}} ===\n# een\n## een.een\n=== {{syn}} ===\n*[1] [[a]]\n*[1.1] [[b]]")
    '=== {{noun|nld}} ===\n# een\n## een.een\n=== {{syn}} ===\n*[1] [[a]]\n*[1.1] [[b]]'
    >>> attach_synonyms("=== {{noun|nld}} ===\n# een\n=== {{syn}} ===\n*[1] [[a]]\n*[[b]]")
    '=== {{noun|nld}} ===\n# een\n=== {{syn}} ===\n*[1] [[a]]\n*[[b]]'
    >>> attach_synonyms("=== {{noun|nld}} ===\n# een\n=== {{syn}} ===\n*[2] [[a]]")
    '=== {{noun|nld}} ===\n# een\n=== {{syn}} ===\n*[2] [[a]]'
    >>> attach_synonyms("=== {{verb|nld}} ===\n# een\n#{{volt-d|bezweten}}\n=== {{syn}} ===\n*[2] [[bezweet]]")
    '=== {{verb|nld}} ===\n# een\n#{{volt-d|bezweten}}\n=== {{syn}} ===\n*[2] [[bezweet]]'
    """
    lines = code.split("\n")
    headers = [n for n, line in enumerate(lines) if line.startswith("=")] + [len(lines)]

    def level(n: int) -> int:
        return len(lines[n]) - len(lines[n].lstrip("="))

    def meanings(start: int, end: int) -> list[int]:
        return [n for n in range(start + 1, end) if lines[n].startswith("#") and lines[n][1:2] not in "#*:"]

    def is_form(n: int) -> bool:
        return lines[n][1:].lstrip().startswith(variant_templates)

    def numbers(text: str) -> list[int]:
        """`[1, 3-4]` gives `[1, 3, 4]`."""
        return [
            number
            for first, last in RE_FIND_NUMBERS.findall(text)
            for number in range(int(first), int(last or first) + 1)
        ]

    drop: set[int] = set()
    insert: dict[int, str] = {}
    for i, start in enumerate(headers[:-1]):
        if lines[start].strip("= ") != "{{syn}}":
            continue
        # The meanings: the "#" items of the nearest section above that has some, as other sections
        # (homophones, notes) can come in between, but not above the section of the language, nor in another
        # list of synonyms: meanings in there lack the header of their part of speech
        items: list[int] = []
        for j in range(i - 1, -1, -1):
            if level(headers[j]) < level(start) or lines[headers[j]].strip("= ") == "{{syn}}":
                break
            if items := meanings(headers[j], headers[j + 1]):
                break
        synonyms: dict[int, list[str]] = {}
        for n in range(start + 1, headers[i + 1]):
            if not (text := lines[n].strip()):
                continue
            if not (match := RE_NUMBERED.fullmatch(text)) or not (found := numbers(match[1])):
                break
            # A meaning that is the form of another word goes to the variants, its synonyms would be lost with it
            if any(not 0 < k <= len(items) or is_form(items[k - 1]) for k in found):
                break
            for k in found:
                synonyms.setdefault(k, []).append(match[2].rstrip(", "))
        else:
            for k, texts in synonyms.items():
                # After the meaning and its own sub-items
                item = items[k - 1]
                after = next(
                    (n for n in range(item + 1, len(lines)) if not lines[n].startswith(("#*", "#:", "##"))), len(lines)
                )
                insert[after - 1] = f"## ''syn.:'' {', '.join(texts)}"
            if synonyms:
                drop.update(range(start, headers[i + 1]))

    out: list[str] = []
    for n, line in enumerate(lines):
        if n not in drop:
            out.append(line)
        if n in insert:
            out.append(insert[n])
    return "\n".join(out)


RE_CLEANUPS = [
    # {{=nld=}} → == {{nld}} ==
    (re.compile(r"(?m)^\{\{=(.+)=\}\}"), r"== {{\1}} ==\n"),
    # {{-etym-}} → === {{etym}} ===
    (re.compile(r"(?m)^\{\{-([\w-]+)(?=-\}\})\-\}\}"), r"=== {{\1}} ===\n"),
    # {{-noun-|0}} → === {{noun}} ===
    (re.compile(r"(?m)^\{\{-([\w-]+)(?=-\|0\}\})\-\|0\}\}"), r"=== {{\1}} ===\n"),
    # {{-noun-|LOCALE}} → === {{noun|LOCALE}} ===
    (re.compile(r"(?m)^\{\{-([\w-]+)-\|(\w{3})\}\}"), r"=== {{\1|\2}} ===\n"),
    # {{-noun-|LOCALE|...}} → === {{noun|LOCALE|...}} ===
    (re.compile(r"(?m)^\{\{-([\w-]+)-\|(\w{3}\|[^}\[\]{}]++)\}\}"), r"=== {{\1|\2}} ===\n"),
]
RE_VARIANTS = re.compile(r"(?m)^(\{\{noun-pl\|[^}]++\}\})")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("{{-prep-nv-}}", LANG)
    '=== {{prep-nv}} ===\n'
    >>> adjust_wikicode("{{-prep-nv-|nld}}", LANG)
    '=== {{prep-nv|nld}} ===\n'
    >>> adjust_wikicode("{{-prep-nv-|nld|dat}}", LANG)
    '=== {{prep-nv|nld|dat}} ===\n'
    >>> adjust_wikicode("{{-prep-nv-|0}}", LANG)
    '=== {{prep-nv}} ===\n'
    >>> adjust_wikicode("{{-noun-|nld}}", LANG)
    '=== {{noun|nld}} ===\n'
    >>> adjust_wikicode("{{-pronom-pers-|deu}}", LANG)
    '=== {{pronom-pers|deu}} ===\n'
    >>> adjust_wikicode("{{-depronom-pers-3-|2}}", LANG)
    '{{-depronom-pers-3-|2}}'

    >>> _ = context.reset(LANG)

    >>> context.new_word("stint")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[stints]]|-|-}}", LANG, word="stint")
    '==={{noun}}===\n# {{rev-flexion|stints}}'

    >>> context.new_word("a")
    >>> adjust_wikicode("{{-nlnoun-|[[a]]|[[a's]]|[[a'tje]]|[[a'tjes]]}}", LANG, word="a")
    "==={{noun}}===\n# {{rev-flexion|a's}}\n# {{rev-flexion|a'tje}}\n# {{rev-flexion|a'tjes}}"

    >>> context.new_word("B")
    >>> adjust_wikicode("{{-nlnoun-|{{QZ|{{pn}}|nld}}|[[{{pn}}'s]]|[[{{pn}}'tje]]|[[{{pn}}'tjes]]}}", LANG, word="B")
    "==={{noun}}===\n# {{rev-flexion|B's}}\n# {{rev-flexion|B'tje}}\n# {{rev-flexion|B'tjes}}"

    >>> _ = context.reset(LANG)

    >>> context.new_word("pover")
    >>> adjust_wikicode("{{adjcomp|p=1|{{pn}}|[[{{pn}}e]]|[[{{pn}}der]]|[[{{pn}}dere]]|[[{{pn}}st]]|[[{{pn}}ste]]|part=[[{{pn}}s]]|partcomp=[[{{pn}}ders]]}}", LANG, word="pover")
    '==={{noun}}===\n# {{rev-flexion|poverder}}\n# {{rev-flexion|poverdere}}\n# {{rev-flexion|poverders}}\n# {{rev-flexion|povere}}\n# {{rev-flexion|povers}}\n# {{rev-flexion|poverst}}\n# {{rev-flexion|poverste}}'

    >>> context.new_word("B")
    >>> adjust_wikicode("{{-nlnoun-|{{QZ|{{pn}}|nld}}|[[{{pn}}'s]]|[[{{pn}}'tje]]|[[{{pn}}'tjes]]}}", LANG, word="B")
    "==={{noun}}===\n# {{rev-flexion|B's}}\n# {{rev-flexion|B'tje}}\n# {{rev-flexion|B'tjes}}"

    >>> context.new_word("nikkel")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|-|[[nikkeltje]](2)|[[nikkeltjes]](2)}}", LANG, word="nikkel")
    '==={{noun}}===\n# {{rev-flexion|nikkeltje}}\n# {{rev-flexion|nikkeltjes}}'

    >>> context.new_word("canzone")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[canzones]]<br/>[[canzonen]] ''(verouderd)''<br/>[[canzone's]] ''(meer Italiaans)''|-|-}}", LANG, word="canzone")
    "==={{noun}}===\n# {{rev-flexion|canzone's}}\n# {{rev-flexion|canzonen}}\n# {{rev-flexion|canzones}}"

    >>> context.new_word("get")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[gitien]] (Hebreeuws),<br />[[getten]] (Jiddisj)|-|-|2.|[A]}}", LANG, word="get")
    '==={{noun}}===\n# {{rev-flexion|getten}}\n# {{rev-flexion|gitien}}'

    >>> context.new_word("Aborigine")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|''(lang)'' [[Aborigine's]]<br>''(verkort)'' [[Aborigines]]|||}}", LANG, word="Aborigine")
    "==={{noun}}===\n# {{rev-flexion|Aborigine's}}\n# {{rev-flexion|Aborigines}}"

    >>> context.new_word("ijzer(III)fosfaat")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[ijzer(III)fosfaten]]}}", LANG, word="ijzer(III)fosfaat")
    '==={{noun}}===\n# {{rev-flexion|ijzer(III)fosfaten}}'

    >>> context.new_word("butin")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[burins]]|([[burintje]]) [[#Opmerkingen|*]]|([[burintjes]]) [[#Opmerkingen|*]]}}", LANG, word="butin")
    '==={{noun}}===\n# {{rev-flexion|burins}}\n# {{rev-flexion|burintje}}\n# {{rev-flexion|burintjes}}'

    >>> context.new_word("stichter")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}s]]|\n''([[{{pn}}tje]])''|''([[{{pn}}tjes]])''}}", LANG, word="stichter")
    '==={{noun}}===\n# {{rev-flexion|stichters}}\n# {{rev-flexion|stichtertje}}\n# {{rev-flexion|stichtertjes}}'

    >>> context.new_word("rekenmachine")
    >>> adjust_wikicode("{{-nlverb-|{{pn}}|[[{{pn}}s]]|([[{{pn}}tje]])<br/>[[rekenmachientje]]|([[{{pn}}tjes]])|vd=[[rekenmachientjes]]}}", LANG, word="rekenmachine")
    '==={{noun}}===\n# {{rev-flexion|rekenmachientje}}\n# {{rev-flexion|rekenmachientjes}}\n# {{rev-flexion|rekenmachines}}\n# {{rev-flexion|rekenmachinetje}}\n# {{rev-flexion|rekenmachinetjes}}'

    >>> context.new_word("blad")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[{{pn}}en]]<br>[[{{pn}}eren]]<br>[[blaren]]|[[blaadje]]|[[blaadjes]], ([[{{pn}}ertjes]])|1.}}", LANG, word="blad")
    '==={{noun}}===\n# {{rev-flexion|blaadje}}\n# {{rev-flexion|blaadjes}}\n# {{rev-flexion|bladen}}\n# {{rev-flexion|bladeren}}\n# {{rev-flexion|bladertjes}}\n# {{rev-flexion|blaren}}'

    >>> context.new_word("binnenbarbecue")
    >>> adjust_wikicode("{{-nlnoun-|{{pn}}|[[binnenbarbecues]]|([[binnenbarbecuetje]]) [1]|([[binnenbarbecuetjes]]) [1]}}", LANG, word="binnenbarbecue")
    '==={{noun}}===\n# {{rev-flexion|binnenbarbecues}}\n# {{rev-flexion|binnenbarbecuetje}}\n# {{rev-flexion|binnenbarbecuetjes}}'
    """
    # Special handling for genders (`{{-l-|m}}`)
    code = code.replace("{{-l-|", "::: {{-l-|")

    # Replace all word occurrences
    code = code.replace("{{pn}}", word)

    # {{=nld=}} → == {{nld}} ==
    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    # Synonyms go under their meaning when they give its number: `*[1] [[bijgevolg]]`
    code = attach_synonyms(code)

    #
    # Variants
    #

    # {{noun-pl|isolatiebedrijf}} → # {{noun-pl|isolatiebedrijf}}
    if "noun-pl" in code:
        code = RE_VARIANTS.sub(r"# \1", code)

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
                    tpl_name = (
                        tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")]
                        .strip()
                        .strip("\u200e")
                        .replace("''", "")
                    )
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
