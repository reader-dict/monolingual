import contextlib
import logging
import math
import re
import unicodedata
from collections import defaultdict
from typing import TypedDict

from num2words import num2words

from ...user_functions import (
    capitalize,
    chinese,
    concat,
    extract_keywords_from,
    italic,
    lookup_italic,
    ruby,
    small,
    strong,
    superscript,
    term,
)
from . import geochronology, si_unit, wikidata
from .form_of import form_of_templates
from .labels import labels, syntaxes
from .langs import langs
from .places import (
    placetypes_aliases,
    recognized_placenames,
    recognized_placetypes,
    recognized_qualifiers,
)
from .scripts import scripts
from .transliterator import transliterate

log = logging.getLogger(__name__)


# Source: https://en.wiktionary.org/w/index.php?title=Module:sem-arb-utilities&oldid=85728127#L-31
AR_RADICALS = {
    "ء": "ʔ",
    "ب": "b",
    "ت": "t",
    "ث": "ṯ",
    "ج": "j",
    "ح": "ḥ",
    "خ": "ḏ",
    "د": "d",
    "ذ": "ḏ",
    "ر": "r",
    "ز": "z",
    "س": "s",
    "ش": "š",
    "ص": "ṣ",
    "ض": "ḍ",
    "ط": "ṭ",
    "ظ": "ẓ",
    "ع": "ʕ",
    "غ": "ḡ",
    "ف": "f",
    "ق": "q",
    "ك": "k",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ه": "h",
    "و": "w",
    "ي": "y",
    "گ": "g",
    "چ": "č",
    "پ": "p",
    "ڭ": "g",
}


def gender_number_specs(parts: str) -> str:
    """
    Source: https://en.wiktionary.org/wiki/Module:gender_and_number

    >>> gender_number_specs("m")
    '<i>m</i>'
    >>> gender_number_specs("m-p")
    '<i>m pl</i>'
    >>> gender_number_specs("m-an-p")
    '<i>m anim pl</i>'
    >>> gender_number_specs("?-p")
    '<i>? pl</i>'
    >>> gender_number_specs("?!-an-s")
    '<i>gender unattested anim sg</i>'
    >>> gender_number_specs("mfbysense-p")
    '<i>m pl or f pl by sense</i>'
    >>> gender_number_specs("mfequiv-s")
    '<i>m sg or f sg same meaning</i>'
    >>> gender_number_specs("mfequiv")
    '<i>m or f same meaning</i>'
    >>> gender_number_specs("biasp-s")
    '<i>impf sg or pf sg</i>'
    >>> gender_number_specs("f,n")
    '<i>f or n</i>'
    """
    specs = {
        # Genders
        "m": "m",
        "n": "n",
        "f": "f",
        "gneut": "gender-neutral",
        "g!": "gender unattested",
        "c": "c",
        # Numbers
        "s": "sg",
        "d": "du",
        "num!": "number unattested",
        "p": "pl",
        # Animacy
        "an": "anim",
        "in": "inan",
        "an!": "animacy unattested",
        "pr": "pers",
        "anml": "animal",
        "np": "npers",
        # Virility
        "vr": "vir",
        "nv": "nvir",
        # Aspect
        "pf": "pf",
        "impf": "impf",
        "asp!": "aspect unattested",
        # Other
        "?": "?",
        "?!": "gender unattested",
    }
    specs_combined = {
        "biasp": [specs["impf"], specs["pf"]],
        "f,n": [specs["f"], specs["n"]],
        "mf": [specs["m"], specs["f"]],
        "mfbysense": [specs["m"], specs["f"]],
        "mfequiv": [specs["m"], specs["f"]],
    }
    result = []

    for part in parts.split("-"):
        if part in specs_combined:
            combinations = specs_combined[parts.split("-")[0]]
            spec = specs[parts.split("-")[1]] if "-" in parts else ""
            res = " or ".join(f"{a} {b}".strip() for a, b in zip(combinations, [spec] * len(combinations), strict=True))
            if "sense" in part:
                res += " by sense"
            elif "equiv" in part:
                res += " same meaning"
            result.append(res)
            return italic(" or ".join(result))
        else:
            result.append(specs[part])

    return italic(" ".join(result))


def join_names(
    data: defaultdict[str, str],
    key: str,
    last_sep: str,
    *,
    include_langname: bool = False,
    key_alias: str = "",
    prefix: str = "",
    suffix: str = "",
) -> str:
    var_a = []
    if data[key] or data[key_alias]:
        for i in range(1, 10):
            var_key = f"{key}{i}" if i != 1 else key
            var_text = data[var_key]
            var_alias_key = ""
            if key_alias:
                var_alias_key = f"{key_alias}{i}" if i != 1 else key_alias
            if not var_text and var_alias_key:
                var_text = data[var_alias_key]
            if var_text:
                for origins in var_text.split(","):
                    if include_langname and ":" in origins:
                        data_split = origins.split(":")
                        text = f"{langs[data_split[0]]} {data_split[1]}"
                        if trans := transliterate(data_split[0], data_split[1]):
                            text += f" ({trans})"
                        var_a.append(text)
                    else:
                        langnametext = "English " if include_langname else ""
                        var_a.append(langnametext + prefix + origins + suffix)
    return concat(var_a, ", ", last_sep=last_sep) if var_a else ""


def gloss_tr_poss(data: defaultdict[str, str], gloss: str, *, trans: str = "") -> str:
    local_phrase = []
    phrase = ""
    trts = ""
    if (tr := data["tr"]) and tr != "-":
        trts += f"{italic(tr)}"
    if data["ts"]:
        if trts:
            trts += " "
        trts += f"{'/' + data['ts'] + '/'}"
    if trts:
        local_phrase.append(trts)
    if trans:
        local_phrase.append(f"{italic(trans)}")
    if gloss:
        local_phrase.append(f"“{gloss}”")
    if data["pos"]:
        local_phrase.append(f"{data['pos']}")
    if data["lit"]:
        local_phrase.append(f"{'literally “' + data['lit'] + '”'}")
    if local_phrase:
        phrase += " ("
        phrase += concat(local_phrase, ", ")
        phrase += ")"
    return phrase


def misc_variant(start: str, tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    if parts:
        parts.pop(0)  # Remove the language
    p = data["alt"] or data["2"] or (parts.pop(0) if parts else "") or ""
    data["t"] = data["t"] or data["3"] or ""
    starter = "" if data["notext"] in ("1", "yes") else start
    if p and starter:
        starter += " of"
    phrase = starter if data["nocap"] else starter.capitalize()
    if p != "-":
        if phrase:
            phrase += " "
        phrase += italic(p.split("#", 1)[0])
    phrase += gloss_tr_poss(data, data["t"] or data["gloss"] or "")
    return phrase


def misc_variant_no_term(title: str, tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    if data["notext"]:
        return ""
    text = data.get("title", title if data["nocap"] else capitalize(title))
    if data["cap"]:
        text = capitalize(text)
    return text


def render_abbreviated(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_abbreviated("a", ["en", "LGAT"], defaultdict(str))
    '(<i>abbreviated</i> <b>LGAT</b>)'
    >>> render_abbreviated("a", ["en", "LGAT", "GATO"], defaultdict(str))
    '(<i>abbreviated</i> <b>LGAT</b>, <b>GATO</b>)'
    """
    text = f"<i>abbreviated</i> <b>{parts[1]}</b>"
    if len(parts) > 2:
        text += f", <b>{parts[2]}</b>"
    return f"({text})"


def render_accent(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_accent("a", ["en", "ethnology"], defaultdict(str))
    '<i>(ethnology)</i>'
    >>> render_accent("a", ["en", "(ethnology)"], defaultdict(str))
    '<i>(ethnology)</i>'
    >>> render_accent("a", ["en", "RP"], defaultdict(str))
    '<i>(Received Pronunciation)</i>'
    """
    text = labels.get(parts[-1], parts[-1])
    return italic(text) if text.startswith("(") else term(text)


def render_aka(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_aka("aka", [], defaultdict(str))
    'a.k.a.'
    >>> render_aka("aka", [], defaultdict(str, {"aka": "1"}))
    'aka'
    >>> render_aka("aka", [], defaultdict(str, {"AKA": "1"}))
    'AKA'
    >>> render_aka("aka", [], defaultdict(str, {"uc": "1"}))
    'AKA'
    """
    if not data:
        return "a.k.a."
    text = "aka"
    if data["AKA"] or data["uc"]:
        text = text.upper()
    return text


def render_ante2(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ante2("ante2", ["1702"], defaultdict(str))
    '<i>ante</i> <b>1702</b>'
    >>> render_ante2("ante2", ["1702"], defaultdict(str, {"short": "yes"}))
    '<i>a.</i> <b>1702</b>'
    """
    init = "a." if data["short"] else "ante"
    return f"{italic(init)} {strong(parts[0])}"


def render_aphetic_form(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_aphetic_form("aphetic form", ["en", "Sabrina"], defaultdict(str))
    'Aphetic form of <i>Sabrina</i>'
    """
    return misc_variant("aphetic form", tpl, parts, data, word=word)


def render_apocopic_form(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_apocopic_form("apocopic form", ["en", "Chicago"], defaultdict(str))
    'Apocopic form of <i>Chicago</i>'
    """
    return misc_variant("apocopic form", tpl, parts, data, word=word)


def render_ar_active_participle(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_active_participle("ar-active participle", [], defaultdict(str))
    'Derived from the active participle'
    >>> render_ar_active_participle("ar-active participle", [], defaultdict(str, {"lc": "1"}))
    'derived from the active participle'
    >>> render_ar_active_participle("ar-active participle", [], defaultdict(str, {"noderived": "1"}))
    'active participle'
    """
    if data["noderived"]:
        return "active participle"
    return f"{'d' if data['lc'] else 'D'}erived from the active participle"


def render_ar_instance_noun(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_instance_noun("ar-instance noun", [], defaultdict(str))
    'Instance noun'
    >>> render_ar_instance_noun("ar-instance noun", [], defaultdict(str, {"lc": "1"}))
    'instance noun'
    """
    return f"{'i' if data['lc'] else 'I'}nstance noun"


def render_ar_passive_participle(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_passive_participle("ar-passive participle", [], defaultdict(str))
    'Derived from the passive participle'
    >>> render_ar_passive_participle("ar-passive participle", [], defaultdict(str, {"lc": "1"}))
    'derived from the passive participle'
    >>> render_ar_passive_participle("ar-passive participle", [], defaultdict(str, {"noderived": "1"}))
    'passive participle'
    """
    if data["noderived"]:
        return "passive participle"
    return f"{'d' if data['lc'] else 'D'}erived from the passive participle"


def render_ar_root(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_root("ar-root", ["ع ل ي"], defaultdict(str))
    'ع ل ي (ʕ l y)'
    >>> render_ar_root("ar-root", ["ع ل ي", "ع ل ي"], defaultdict(str))
    'ع ل ي (ʕ l y), ع ل ي (ʕ l y)'
    >>> render_ar_root("ar-root", ["ع ل ي"], defaultdict(str, {"notext": "1"}))
    ''
    """
    if data["notext"]:
        return ""
    return ", ".join(f"{root} ({' '.join(AR_RADICALS[char] for char in root.split(' '))})" for root in parts)


def render_bce(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_bce("B.C.E.", [], defaultdict(str))
    '<small>B.C.E.</small>'
    >>> render_bce("C.E.", [], defaultdict(str, {"nodot": "1"}))
    '<small>CE</small>'
    >>> render_bce("CE", [], defaultdict(str))
    '<small>CE</small>'
    """
    nodot = data["nodot"] in ("1", "yes") or tpl in {"CE", "BCE"}
    text = "C.E." if tpl in {"C.E.", "CE", "A.D.", "AD"} else "B.C.E."
    return small(text.replace(".", "")) if nodot else small(text)


def render_blockquote(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_blockquote("blockquote", ["text"], defaultdict(str))
    '<blockquote>&nbsp;&nbsp;“&nbsp;text&nbsp;”</blockquote>'
    >>> render_blockquote("blockquote", [], defaultdict(str, {"1": "text"}))
    '<blockquote>&nbsp;&nbsp;“&nbsp;text&nbsp;”</blockquote>'
    """
    return f"<blockquote>&nbsp;&nbsp;“&nbsp;{data['1'] or parts[0]}&nbsp;”</blockquote>"


def render_bond_credit_rating(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_bond_credit_rating("bond credit rating", ["a bond is upper-medium grade with low risk of default"], defaultdict(str, {"lt": "1", "s": "1", "f": "1"}))
    '{{lb|mul|finance}} <i>Long-term bond credit rating by S&P Global Ratings and Fitch Ratings, indicating that a bond is upper-medium grade with low risk of default.</i>'
    """
    text = "{{lb|mul|finance}} <i>"

    if data["lt"]:
        text += "Long-term"
    if data["st"]:
        text += "Short-term"

    text += " bond credit rating by"

    agencies: list[str] = []
    if data["m"]:
        agencies.append("Moody's Investors Service")
    if data["s"]:
        agencies.append("S&P Global Ratings")
    if data["f"]:
        agencies.append("Fitch Ratings")
    text += f" {concat(agencies, ', ', last_sep=' and ')},"

    return f"{text} indicating that {parts[0]}.</i>"


def render_cap(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cap("cap", ["beef"], defaultdict(str))
    'Beef'
    >>> render_cap("cap", ["common cold"], defaultdict(str))
    'Common cold'
    >>> render_cap("cap", ["bracket", "s"], defaultdict(str))
    'Brackets'

    # We need to be able to transcript here
    # >>> render_cap("cap", ["σκύλαξ"], defaultdict(str, {"lang": "grc"}))
    # 'Σκύλαξ (Skúlax)'
    # >>> render_cap("cap", ["кот", "а́"], defaultdict(str, {"lang": "ru"}))
    # 'Кота́ (Kotá)'
    """
    return f"{capitalize(''.join(parts))}"


def render_century(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_century("century", ["17"], defaultdict(str))
    '<small>[from 17th c.]</small>'
    >>> render_century("century", ["1"], defaultdict(str))
    '<small>[from 1st c.]</small>'
    >>> render_century("century", ["2", "3"], defaultdict(str))
    '<small>[2nd–3rd c.]</small>'
    """

    def ordinal(n: str) -> str:
        suffix = "th"
        with contextlib.suppress(ValueError):
            x = int(n)
            mod10 = x % 10
            mod100 = x % 100
            if mod10 == 1 and mod100 != 11:
                suffix = "st"
            elif mod10 == 2 and mod100 != 12:
                suffix = "nd"
            elif mod10 == 3 and mod100 != 13:
                suffix = "rd"
        return f"{n}{suffix}"

    if len(parts) > 1:
        phrase = f"{ordinal(parts[0])}–{ordinal(parts[1])} c."
    else:
        phrase = f"from {ordinal(parts[0])} c."

    return small(f"[{phrase}]")


def render_chemical_symbol(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_chemical_symbol("chemical symbol", ["calcium"], defaultdict(str))
    '<i>(chemistry) Chemical symbol for</i> <b>calcium</b>.'
    >>> render_chemical_symbol("chemical symbol", ["unnilquadium"], defaultdict(str, {"sys": "1"}))
    '<i>(chemistry) Systematic chemical symbol for</i> <b>unnilquadium</b>.'
    >>> render_chemical_symbol("chemical symbol", ["unnilquadium", "rutherfordium"], defaultdict(str, {"sys": "1"}))
    '<i>(chemistry) Systematic chemical symbol for</i> <b>unnilquadium</b>, now named <b>rutherfordium</b>.'
    >>> render_chemical_symbol("chemical symbol", ["copernicium"], defaultdict(str, {"obs": "1"}))
    '<i>(chemistry, obsolete) Obsolete chemical symbol for</i> <b>copernicium</b>.'
    """
    if data["obs"] == "1":
        text = "(chemistry, obsolete) Obsolete chemical symbol for"
    elif data["sys"] == "1":
        text = "(chemistry) Systematic chemical symbol for"
    else:
        text = "(chemistry) Chemical symbol for"
    text = f"{italic(text)} {strong(parts.pop(0))}"
    if parts:
        text += f", now named {strong(parts.pop(0))}"
    return f"{text}."


def render_clipped_compound(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_clipped_compound("clipped compound", ["en", "character set"], defaultdict(str))
    'Clipped compound of <i>character set</i>'
    """
    return misc_variant("clipped compound", tpl, parts, data, word=word)


def render_clipping(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_clipping("clipping", ["en", "automobile"], defaultdict(str))
    'Clipping of <i>automobile</i>'
    >>> render_clipping("clipping", ["en", "-"], defaultdict(str))
    'Clipping of'
    >>> render_clipping("clipping", ["fr", "métropolitain"], defaultdict(str, {"notext": "1"}))
    '<i>métropolitain</i>'
    >>> render_clipping("clipping", ["ru", "ку́бовый краси́тель"], defaultdict(str, {"t": "vat dye", "nocap": "1"}))
    'clipping of <i>ку́бовый краси́тель</i> (“vat dye”)'
    """
    return misc_variant("clipping", tpl, parts, data, word=word)


def render_codepoint(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_codepoint("codepoint", ["U+2010"], defaultdict(str))
    '‐ (U+2010 HYPHEN)'
    >>> render_codepoint("codepoint", ["U+2010"], defaultdict(str, {"display": "0"}))
    'U+2010 HYPHEN'
    >>> render_codepoint("codepoint", [":"], defaultdict(str))
    ': (U+003A COLON)'
    """

    def get_wide_ordinal(char: str) -> str:
        if len(char) == 2:
            res = 0x10000 + (ord(char[0]) - 0xD800) * 0x400 + (ord(char[1]) - 0xDC00)
        else:
            res = ord(char)
        return f"U+{res:>04X}"

    if (char := parts[0]).startswith("U+"):
        codepoint = char
        char = chr(int(char[2:], 16))
    else:
        codepoint = get_wide_ordinal(char)
    name = unicodedata.name(char)

    if data["display"] != "0" and not data["plain"]:
        return f"{char} ({codepoint} {name})"
    return f"{codepoint} {name}"


def render_coinage(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_coinage("coin", ["en", "Josiah Willard Gibbs"], defaultdict(str))
    'Coined by Josiah Willard Gibbs'
    >>> render_coinage("coin", ["en", "Josiah Willard Gibbs"], defaultdict(str, {"in":"1881", "nat":"American", "occ":"scientist"}))
    'Coined by American scientist Josiah Willard Gibbs in 1881'
    >>> render_coinage("coin", ["en", "Josiah Willard Gibbs"], defaultdict(str, {"alt":"Josiah W. Gibbs", "nationality":"American", "occupation":"scientist"}))
    'Coined by American scientist Josiah W. Gibbs'
    >>> render_coinage("coin", [], defaultdict(str, {"1":"en", "2":"Charles Rice", "in": "c. 1000"}))
    'Coined by Charles Rice c. 1000'
    >>> render_coinage("coin", ["mul", "Q1043"], defaultdict(str, {"exnihilo": "1", "in": "in the 1950s"}))
    'Coined <i>ex nihilo</i> by Swedish botanist, physician, and zoologist Carl Linnaeus in the 1950s'
    """
    if parts:
        parts.pop(0)  # Remove the language

    phrase = ""
    if data["notext"] != "1":
        starter = "coined"
        if data["exnihilo"]:
            starter += " <i>ex nihilo</i>"
        starter += " by"
        phrase = starter if data["nocap"] else starter.capitalize()
        if data["nationality"]:
            phrase += f" {data['nationality']}"
        elif data["nat"]:
            phrase += f" {data['nat']}"
        if occ := join_names(data, "occ", " and ", include_langname=False, key_alias="occupation"):
            phrase += f" {occ}"
        phrase += " "

    who = data["alt"] or data["2"] or (parts.pop(0) if parts else "unknown") or "unknown"
    if who.startswith("Q") and who[1:].isdigit():
        who = wikidata.person(who)

    phrase += who

    if date := data["in"]:
        if date.isdigit():
            phrase += " in"
        phrase += f" {date}"

    return phrase


def render_contraction(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    return misc_variant("contraction", tpl, parts, data, word=word)


def render_lang_def(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    def ordinal_to_word(num: str) -> str:
        return str(num2words(num, lang="en", to="ordinal"))

    lang = parts.pop(0)
    alphabet = data["alphabet"]
    dot = data["dot"]
    name = data["name"]
    nodot = data["nodot"]
    sc = data["sc"]
    trans = data["tr"]

    match parts.pop(0):
        case "diacritic":
            letters = " / ".join(parts[2:])
            text = f"A diacritical mark of the {sc} script, called {{{{m-self||{name}|tr={trans}}}}} in {langs[lang]}, and found on {letters}"
            text += dot or "."

        case "letter":
            letter = ""
            if parts:
                if letter := parts.pop(0):
                    letter = ordinal_to_word(letter)
            text = "<i>The " if letter or lang != "mul" else "<i>A "
            if letter:
                text += f"{letter} "
            text += "letter of the "

            if alphabet:
                text += alphabet
            elif lang == "mul":
                text += sc.rstrip("-")
                if not sc.endswith("-"):
                    text += " "
                text += "script"
            else:
                text += f"{langs[lang]} alphabet"

            if parts:
                text += f", called <b>{parts.pop(0)}</b>"
                if parts:
                    text += "," if len(parts) > 1 else " or"
                    text += f" <b>{parts.pop(0)}</b>"
                    if parts:
                        text += "," if len(parts) > 1 else " or"
                        text += f" <b>{parts.pop(0)}</b>"
                        if parts:
                            text += f" or <b>{parts.pop(0)}</b>"

            if lang != "mul":
                text += f", and written in the {sc.rstrip('-')} script"
            text += "</i>"
            if not nodot:
                text += dot or "."

        case "name":
            text = f"<i>The name of the {sc}"
            if not sc.endswith("-"):
                text += " "
            text += f"script letter</i> <b>{parts.pop(0)}</b>"
            if parts:
                text += f" / <b>{parts[0]}</b>"
            if not nodot:
                text += dot or "."

        case "ordinal":
            ord_word = ordinal_to_word(parts.pop(0))
            text = f"<i>The ordinal number <b>{ord_word}</b>, derived from this letter of the {langs[lang]} alphabet"
            if parts:
                text += f", called <b>{parts.pop(0)}</b>"
                if parts:
                    text += f" or '{parts.pop(0)}'"
                    if parts:
                        text += f" or '{parts.pop(0)}'"
            text += f", written in the {sc.rstrip('-')} script</i>"
            text += dot or "."

    return text


def render_cyrl_def(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cyrl_def("Cyrl-def", ["en", "name", "Ԫ", "ԫ"], defaultdict(str, {"sc": "Cyrl"}))
    '<i>The name of the Cyrillic script letter</i> <b>Ԫ</b> / <b>ԫ</b>.'
    >>> render_cyrl_def("Cyrl-def", ["mul", "letter"], defaultdict(str))
    '<i>A letter of the Cyrillic script</i>.'
    >>> render_cyrl_def("Cyrl-def", ["mul", "letter"], defaultdict(str, {"sc": "Cyrl", "nodot": "1"}))
    '<i>A letter of the Cyrillic script</i>'
    >>> render_cyrl_def("Cyrl-def", ["mul", "letter", "", "zemlya", "zemlja", "zemlia"], defaultdict(str, {"sc": "Cyrs"}))
    '<i>A letter of the Old Cyrillic script, called <b>zemlya</b>, <b>zemlja</b> or <b>zemlia</b></i>.'
    """
    sc = data["sc"] or "Cyrillic"
    if sc == "Cyrl":
        sc = "Cyrillic"
    elif sc == "Cyrs":
        sc = "Old Cyrillic"
    data["sc"] = sc
    if data["sc"] not in {"Cyrillic", "Old Cyrillic"}:
        raise ValueError(f"Unhandled Cyrl-def sc: {data['sc']!r}")
    return render_lang_def(tpl, parts, data, word=word)


def render_latn_def(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_latn_def("Latn-def", ["en", "name", "M", "m"], defaultdict(str))
    '<i>The name of the Latin-script letter</i> <b>M</b> / <b>m</b>.'
    >>> render_latn_def("Latn-def", ["en", "letter"], defaultdict(str))
    '<i>The letter of the English alphabet, and written in the Latin script</i>.'
    >>> render_latn_def("Latn-def", ["en", "letter", "1"], defaultdict(str))
    '<i>The first letter of the English alphabet, and written in the Latin script</i>.'
    >>> render_latn_def("Latn-def", ["en", "letter", "1", "a"], defaultdict(str))
    '<i>The first letter of the English alphabet, called <b>a</b>, and written in the Latin script</i>.'
    >>> render_latn_def("Latn-def", ["en", "ordinal", "1"], defaultdict(str))
    '<i>The ordinal number <b>first</b>, derived from this letter of the English alphabet, written in the Latin script</i>.'
    >>> render_latn_def("Latn-def", ["en", "ordinal", "1", "a"], defaultdict(str))
    '<i>The ordinal number <b>first</b>, derived from this letter of the English alphabet, called <b>a</b>, written in the Latin script</i>.'
    """
    data["sc"] = "Latin-"
    return render_lang_def(tpl, parts, data, word=word)


def render_dating(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_dating("ante", ["1880"], defaultdict(str))
    '<i>a.</i> <b>1880</b>,'
    >>> render_dating("ante", ["1880", "1900"], defaultdict(str))
    '<i>a.</i> <b>1880</b> 1900,'
    >>> render_dating("circa", ["1880", "1900"], defaultdict(str))
    '<i>c.</i> <b>1880</b> 1900,'
    """
    init = f"{tpl[0]}."
    start = data["1"] or parts.pop(0) if parts else ""
    end = data["2"] or parts.pop(0) if parts else ""

    return f"{italic(init)} {strong(start)}" + (f" {end}" if end else "") + ","


def render_dating_full_and_short(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_dating_full_and_short("circa2", ["1880"], defaultdict(str))
    '<i>circa</i> 1880'
    >>> render_dating_full_and_short("circa2", ["1880"], defaultdict(str, {"short": "yes"}))
    '<i>c.</i> 1880'
    >>> render_dating_full_and_short("post2", ["1880"], defaultdict(str))
    '<i>post</i> 1880'
    >>> render_dating_full_and_short("post2", ["1880"], defaultdict(str, {"short": "1"}))
    '<i>p.</i> 1880'
    """
    return f"<i>{f'{tpl[0]}.' if data['short'] else tpl.removesuffix('2')}</i> {parts[0]}"


def render_deverbal(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_deverbal("deverbal", [], defaultdict(str))
    'Deverbal'
    >>> render_deverbal("deverbal", ["fr", "accorder"], defaultdict(str))
    'Deverbal from <i>accorder</i>'
    >>> render_deverbal("deverbal", ["it", "sguardare", "", "to look at"], defaultdict(str, {"nocap": "1"}))
    'deverbal from <i>sguardare</i> (“to look at”)'
    """
    text = "deverbal" if data["nocap"] == "1" else "Deverbal"
    if len(parts) > 1:
        text += f" from {italic(parts[1])}"
        if len(parts) > 3:
            text += f" (“{parts[3]}”)"
    return text


def render_el_uk_us(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_el_uk_us("l-UK-US", ["enam", "elled"], defaultdict(str))
    'enamelled (<i>UK</i>), enameled (<i>US</i>)'
    >>> render_el_uk_us("l-UK-US", ["word1", "word2"], defaultdict(str))
    'word1 (<i>UK</i>), word2 (<i>US</i>)'
    """
    match end := parts[1]:
        case "isable":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}izable"
        case "isation":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}ization"
        case "ise":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}ize"
        case "ised":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}ized"
        case "iser":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}izer"
        case "ising":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}izing"
        case "elled":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}eled"
        case "our":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}or"
        case "oured":
            word_uk, word_us = f"{parts[0]}{end}", f"{parts[0]}ored"
        case _:
            word_uk, word_us = parts[0], parts[1]

    return f"{word_uk} (<i>UK</i>), {word_us} (<i>US</i>)"


def render_etydate(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etydate("etydate", ["1880"], defaultdict(str))
    'First attested in 1880'
    >>> render_etydate("etydate", ["1880"], defaultdict(str, {"nocap": "1"}))
    'first attested in 1880'
    >>> render_etydate("etydate", ["first half of the 19th century"], defaultdict(str))
    'First attested in the first half of the 19th century'
    >>> render_etydate("etydate", ["c", "1900"], defaultdict(str))
    'First attested in <i>c.</i> 1900'
    >>> render_etydate("etydate", ["c", "1900", "2000"], defaultdict(str))
    'First attested in <i>c.</i> 1900, but in common usage only as of 2000'
    >>> render_etydate("etydate", ["c", "1900", "first half of the 21st century"], defaultdict(str))
    'First attested in <i>c.</i> 1900, but in common usage only as of the first half of the 21st century'
    >>> render_etydate("etydate", ["r", "1900", "1910"], defaultdict(str))
    'First attested in 1900–1910'
    >>> render_etydate("etydate", ["r", "1900", "1910", "1980"], defaultdict(str))
    'First attested in 1900–1910, but in common usage only as of 1980'
    >>> render_etydate("etydate", ["r", "1900", "1910", "first half of the 19st century"], defaultdict(str))
    'First attested in 1900–1910, but in common usage only as of the first half of the 19st century'
    """

    def render_etydate_l2(parts: list[str]) -> str:
        phrase = ", but in common usage only as of "
        if parts[0] == "c":
            phrase += f"{italic('c.')} "
            phrase += f"{parts[2]}–{parts[3]}" if parts[1] == "r" else parts[1]
        else:
            if parts[0] == "r":
                phrase += f"{parts[1]}–{parts[2]}"
            else:
                phrase += parts[0] if re.match(r"\d+$", parts[0]) else f"the {parts[0]}"
        return phrase

    nocap = data["nocap"] in ("1", "yes")
    phrase = ("f" if nocap else "F") + "irst attested in "
    if parts[0] == "c":
        phrase += f"{italic('c.')} "
        if parts[1] == "r":
            phrase += f"{parts[2]}–{parts[3]}"
            if len(parts) > 4:
                phrase += render_etydate_l2(parts[4:])
        else:
            phrase += parts[1]
            if len(parts) > 2:
                phrase += render_etydate_l2(parts[2:])
    else:
        if parts[0] == "r":
            phrase += f"{parts[1]}–{parts[2]}"
            if len(parts) > 3:
                phrase += render_etydate_l2(parts[3:])
        else:
            phrase += parts[0] if re.match(r"\d+$", parts[0]) else f"the {parts[0]}"
    return phrase


def alter_demonym_parts(parts: list[str]) -> list[str]:
    def rpl(match: re.Match[str]) -> str:
        kind, pos, place = match.groups()

        kind = placetypes_aliases.get(kind, kind)
        prep = recognized_placetypes[kind.lower()]["preposition"] or "of"
        if pos.istitle():
            kind = kind.title()
        as_prefix = pos.lower() == "pref"
        multiple_places = "," in place

        if multiple_places:
            kind += "s"
            place = concat(place.split(","), ", ", last_sep=" and ")

        return f"{kind} {prep} {place}" if as_prefix else f"{place} {kind}"

    for idx, part in enumerate(parts.copy()):
        has_changed = False
        if "<<" in part:
            part = re.sub(r"<<(\w+)(?::also)?:(\w+)(?::also)?/([^>]+)>>", rpl, part)
            has_changed = True

        if "<q:" in part:
            part = re.sub(r"(\w+)<q:([^>]+)>", r"(<i>\2</i>) \1", part)
            has_changed = True
        if "<qq:" in part:
            part = re.sub(r"(\w+)<qq:([^>]+)>", r"\1 (<i>\2</i>)", part)
            has_changed = True
        if "<t:" in part or "<gloss:" in part:
            part = re.sub(r"<(?:t|gloss):([^>]+)>", r" (\1)", part)
            has_changed = True

        if "w:" in part:
            part = part.replace("w:", "")
            has_changed = True

        if "<<" in part:
            part = re.sub(r"<<\w/([^>]+)>>", r"\1", part)
            has_changed = True

        if has_changed:
            parts[idx] = part

    return parts


def render_demonym_adj(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_demonym_adj("demonym-adj", ["en", "Tucson"], defaultdict(str))
    'Of, from or relating to Tucson.'
    >>> render_demonym_adj("demonym-adj", ["en", "Tucson"], defaultdict(str, {"nocap": "1", "nodot": "1"}))
    'of, from or relating to Tucson'
    >>> render_demonym_adj("demonym-adj", ["it", "w:Abatemarco"], defaultdict(str))
    'of, from or relating to Abatemarco'

    >>> render_demonym_adj("demonym-adj", ["en", "Alexandria<t:city in Egypt>", "Alexandria<t:city in Virginia, USA>"], defaultdict(str))
    'Of, from or relating to Alexandria (city in Egypt) or Alexandria (city in Virginia, USA).'
    >>> render_demonym_adj("demonym-adj", ["it", "Alexandria in Egypt"], defaultdict(str, {"t": "Alexandrian", "t2": "Alexandrine"}))
    'Alexandrian, Alexandrine (of, from or relating to Alexandria in Egypt)'
    >>> render_demonym_adj("demonym-adj", ["es", "Linares, Colombia", "w:Linares, Jaén", "w:Linares de la Sierra", "w:Linares de Mora", "w:Linares de Riofrío", "w:Linares, Nuevo León"], defaultdict(str))
    'of, from or relating to Linares, Colombia; Linares, Jaén; Linares de la Sierra; Linares de Mora; Linares de Riofrío; or Linares, Nuevo León'
    >>> render_demonym_adj("demonym-adj", ["en", "the <<r:pref/Karelia>>, politically split between the <<adr:pref/North Karelia,South Karelia,here>>, <<c/Finland>> and the <<rep:Pref:also/Karelia>>, <<c/Russia>>"], defaultdict(str))
    'Of, from or relating to the region of Karelia, politically split between the administrative regions of North Karelia, South Karelia and here, Finland and the Republic of Karelia, Russia.'
    >>> render_demonym_adj("demonym-adj", ["en", "the <<r:pref/Frisia>>: Either West Frisia (the Dutch <<p:also:pref/Friesland>>); North Frisia (in the German <<s:pref:also/Schleswig-Holstein>>, near the Danish border); or East Frisia (in the German <<s:pref:also/Lower Saxony>>, near the Dutch border)"], defaultdict(str))
    'Of, from or relating to the region of Frisia: Either West Frisia (the Dutch province of Friesland); North Frisia (in the German state of Schleswig-Holstein, near the Danish border); or East Frisia (in the German state of Lower Saxony, near the Dutch border).'
    >>> render_demonym_adj("demonym-adj", ["it", "Sanremo<gloss:town in Liguria>"], defaultdict(str))
    'of, from or relating to Sanremo (town in Liguria)'
    """
    is_english = parts[0] == "en"
    has_parenthesis = bool(data["t"])

    phrase = ""
    if t1 := data["t"]:
        phrase += t1
        for idx in range(2, 16):
            if t := data[f"t{idx}"]:
                phrase += f", {t}"
            else:
                break
        phrase += " ("
    phrase += "o" if data["nocap"] or not is_english else "O"
    phrase += "f, from or relating to "
    sep, last_sep = (
        (" or ", " or ")
        if len(parts[1:]) == 2
        else ("; ", "; or ")
        if any("t:" in part or "w:" in part for part in parts[1:])
        else (", ", " or ")
    )
    parts = alter_demonym_parts(parts)
    phrase += concat(parts[1:], sep, last_sep=last_sep)

    if re.search(r"<+\w+:", phrase):
        assert 0, f"Missing special place handling for demonym-adj: {parts}"

    if has_parenthesis:
        phrase += ")"

    if is_english and not data["nodot"]:
        phrase += "."

    return phrase


def render_demonym_noun(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_demonym_noun("demonym-noun", ["it", "w:Abatemarco"], defaultdict(str))
    'native or inhabitant of Abatemarco'
    >>> render_demonym_noun("demonym-noun", ["it", "w:Abatemarco"], defaultdict(str, {"g": "m"}))
    'native or inhabitant of Abatemarco (<i>usually male</i>)'
    >>> render_demonym_noun("demonym-noun", ["it", "Abdera"], defaultdict(str, {"t": "Abderite"}))
    'Abderite (native or inhabitant of Abdera)'
    >>> render_demonym_noun("demonym-noun", ["it", "Alexandria in Egypt"], defaultdict(str, {"t": "Alexandrian", "t2": "Alexandrine"}))
    'Alexandrian, Alexandrine (native or inhabitant of Alexandria in Egypt)'
    >>> render_demonym_noun("demonym-noun", ["it", "Alghero<qq:in Sardinia>"], defaultdict(str, {"t": "Algherese"}))
    'Algherese (native or inhabitant of Alghero (<i>in Sardinia</i>))'
    >>> render_demonym_noun("demonym-noun", ["it", "America", "the Americas", "the United States"], defaultdict(str, {"g": "f", "t": "American"}))
    'female American (female native or inhabitant of America, the Americas or the United States)'
    >>> render_demonym_noun("demonym-noun", ["it", "Latin America"], defaultdict(str, {"t": "Latina", "g": "f", "gloss_is_gendered": "true"}))
    'Latina (female native or inhabitant of Latin America)'
    >>> render_demonym_noun("demonym-noun", ["es", "San Juan<t:capital of Puerto Rico>", "San Juan<t:city in Cuba>", "w:San Juan de los Morros<t:capital of the state of Guárico, Venezuela>", "w:San Juan de la Maguana<t:city or province of the Dominican Republic>"], defaultdict(str, {"t": "Sanjuanero", "g": "m"}))
    'Sanjuanero (native or inhabitant of San Juan (capital of Puerto Rico); San Juan (city in Cuba); San Juan de los Morros (capital of the state of Guárico, Venezuela); or San Juan de la Maguana (city or province of the Dominican Republic)) (<i>usually male</i>)'

    >>> render_demonym_noun("demonym-noun", ["en", "the <<city:pref/Adelaide>>, <<s/South Australia>>", "<<c/Germany>>"], defaultdict(str))
    'A native or inhabitant of the city of Adelaide, South Australia, Germany.'
    >>> render_demonym_noun("demonym-noun", ["en", "the <<p:Pref/Quebec>>, <<c/Canada>>"], defaultdict(str))
    'A native or inhabitant of the Province of Quebec, Canada.'
    """
    is_english = parts[0] == "en"
    is_female = data["g"] == "f"
    skip_female_prefix = data["gloss_is_gendered"]
    has_parenthesis = bool(data["t"])

    if is_female:
        del data["g"]

    phrase = "A " if is_english else ""
    if is_female and not skip_female_prefix:
        phrase += "female "
    if t1 := data["t"]:
        phrase += t1
        for idx in range(2, 16):
            if t := data[f"t{idx}"]:
                phrase += f", {t}"
            else:
                break
        phrase += " ("
    if is_female:
        phrase += "female "
    phrase += "native or inhabitant of "
    sep, last_sep = (
        (", ", ", ")
        if is_english
        else ("; ", "; or ")
        if any("<t:" in part or "<w:" in part for part in parts[1:])
        else (", ", " or ")
    )
    parts = alter_demonym_parts(parts)
    phrase += concat(parts[1:], sep, last_sep=last_sep)

    if re.search(r"<+\w+:", phrase):
        assert 0, f"Missing special place handling for demonym-noun: {parts}"

    if has_parenthesis:
        phrase += ")"

    if data["g"] == "m":
        phrase += " (<i>usually male</i>)"

    if is_english and not data["nodot"]:
        phrase += "."

    return phrase


def render_denominal_verb(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_denominal_verb("denominal verb", ["en", "Eskimo kiss"], defaultdict(str))
    'Denominal verb of <i>Eskimo kiss</i>'
    """
    return misc_variant("denominal verb", tpl, parts, data, word=word)


def render_displaced(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_displaced("displaced", ["ang", "ēaþmōdlīċe"], defaultdict(str))
    'Displaced Old English <i>ēaþmōdlīċe</i>'
    >>> render_displaced("displaced", ["ang", "ēaþmōdlīċe"], defaultdict(str, {"sl": "1"}))
    'Displaced <i>ēaþmōdlīċe</i>'
    >>> render_displaced("displaced", ["ang", "ēaþmōdlīċe"], defaultdict(str, {"by": "1"}))
    'Displaced by Old English <i>ēaþmōdlīċe</i>'
    >>> render_displaced("displaced", ["ang", "ēaþmōdlīċe"], defaultdict(str, {"by": "1", "sl": "1"}))
    'Displaced by <i>ēaþmōdlīċe</i>'
    >>> render_displaced("displaced", ["ang", "ēaþmōdlīċe"], defaultdict(str, {"t": "abundance, plenty"}))
    'Displaced Old English <i>ēaþmōdlīċe</i> (“abundance, plenty”)'
    """
    text = "Displaced"
    if data["by"]:
        text += " by"
    if not data["sl"]:
        text += f" {langs[parts[0]]}"
    gloss = data["t"] or data["gloss"]
    return f"{text} <i>{parts[-1]}</i>{gloss_tr_poss(data, gloss)}"


def render_en_noun(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_en_noun("en-noun", ["?"], defaultdict(str), word="achávalite")
    '<b>achávalite</b>'
    """
    return strong({"?": word}[parts[0]])


def render_en_proper_noun(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_en_proper_noun("en-proper noun", [], defaultdict(str, {"head": "Nutbush, TN"}))
    '<b>Nutbush, TN</b>'
    """
    if not (head := data["head"]):
        raise ValueError("en-proper noun is missing its head!")
    return f"<b>{head}</b>"


def render_foreign_derivation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_foreign_derivation("bor", ["en", "ar", "الْعِرَاق", "", "Iraq"], defaultdict(str))
    'Arabic الْعِرَاق (<i>al-ʕirāq</i>, “Iraq”)'
    >>> render_foreign_derivation("bor", [], defaultdict(str, {"1": "en", "2": "ja", "3": "マエバリ"}))
    'Japanese マエバリ'
    >>> render_foreign_derivation("bor+", [], defaultdict(str, {"1": "en", "2": "ja", "3": "マエバリ"}))
    'Borrowed from Japanese マエバリ'
    >>> render_foreign_derivation("der", ["en", "fro", "-"], defaultdict(str))
    'Old French'
    >>> render_foreign_derivation("der", ["en", "mul", "Jaborosa parviflora"], defaultdict(str))
    'translingual <i>Jaborosa parviflora</i>'
    >>> render_foreign_derivation("der", ["en", "mul", "Jaborosa parviflora"], defaultdict(str, {"tr": "a"}))
    'translingual <i>Jaborosa parviflora</i> (<i>a</i>)'
    >>> render_foreign_derivation("der", ["en", "mul", "Jaborosa parviflora"], defaultdict(str, {"tr": "-"}))
    'translingual <i>Jaborosa parviflora</i>'
    >>> render_foreign_derivation("der+", ["en", "mul", "Jaborosa parviflora"], defaultdict(str))
    'Derived from translingual <i>Jaborosa parviflora</i>'
    >>> render_foreign_derivation("etyl", ["enm", "en"], defaultdict(str))
    'Middle English'
    >>> render_foreign_derivation("etyl", ["grc"], defaultdict(str))
    'Ancient Greek'
    >>> render_foreign_derivation("inh", ["en", "enm", "water"], defaultdict(str))
    'Middle English <i>water</i>'
    >>> render_foreign_derivation("inh", ["en", "ang", "wæter", "", "water"], defaultdict(str))
    'Old English <i>wæter</i> (“water”)'
    >>> render_foreign_derivation("inh", ["en", "ang", "etan"], defaultdict(str, {"t":"to eat"}))
    'Old English <i>etan</i> (“to eat”)'
    >>> render_foreign_derivation("inh", ["en", "ine-pro", "*werdʰh₁om", "*wr̥dʰh₁om"], defaultdict(str))
    'Proto-Indo-European <i>*wr̥dʰh₁om</i>'
    >>> render_foreign_derivation("inh+", ["en", "ine-pro", "*werdʰh₁om", "*wr̥dʰh₁om"], defaultdict(str))
    'Inherited from Proto-Indo-European <i>*wr̥dʰh₁om</i>'
    >>> render_foreign_derivation("noncog", ["fro", "livret"], defaultdict(str, {"t":"book, booklet"}))
    'Old French <i>livret</i> (“book, booklet”)'
    >>> render_foreign_derivation("noncog", ["xta", "I̱ta Ita"], defaultdict(str, {"lit":"flower river"})) #xochopa
    'Alcozauca Mixtec <i>I̱ta Ita</i> (literally “flower river”)'
    >>> render_foreign_derivation("noncog", ["egy", "ḫt n ꜥnḫ", "", "grain, food"], defaultdict(str, {"lit":"wood/stick of life"}))
    'Egyptian <i>ḫt n ꜥnḫ</i> (“grain, food”, literally “wood/stick of life”)'
    >>> render_foreign_derivation("cal", ["fr" , "en", "light year"], defaultdict(str, {"alt":"alt", "tr":"tr", "t":"t", "g":"m", "pos":"pos", "lit":"lit"}))
    'Calque of English <i>alt</i> <i>m</i> (<i>tr</i>, “t”, pos, literally “lit”)'

    >>> render_foreign_derivation("pcal", ["en" , "de", "Leberwurst"], defaultdict(str, {"nocap":"1"}))
    'partial calque of German <i>Leberwurst</i>'
    >>> render_foreign_derivation("pclq", ["en" , "zh", "閩中語"], defaultdict(str))
    'Partial calque of Chinese 閩中語'

    >>> render_foreign_derivation("sl", ["en", "ru", "пле́нум", "", "plenary session"], defaultdict(str, {"nocap":"1"}))
    'semantic loan of Russian <i>пле́нум</i> (<i>plénum</i>, “plenary session”)'
    >>> render_foreign_derivation("learned borrowing", ["en", "la", "consanguineus"], defaultdict(str))
    'Learned borrowing from Latin <i>consanguineus</i>'
    >>> render_foreign_derivation("learned borrowing", ["en", "LL.", "trapezium"], defaultdict(str, {"notext":"1"}))
    'Late Latin <i>trapezium</i>'
    >>> render_foreign_derivation("slbor", ["en", "fr", "mauvaise foi"], defaultdict(str, {"nocap":"1"}))
    'semi-learned borrowing from French <i>mauvaise foi</i>'
    >>> render_foreign_derivation("obor", ["en", "ru", "СССР"], defaultdict(str))
    'Orthographic borrowing from Russian <i>СССР</i> (<i>SSSR</i>)'
    >>> render_foreign_derivation("unadapted borrowing", ["en", "ar", "قِيَاس", "", "measurement, analogy"], defaultdict(str))
    'Unadapted borrowing from Arabic قِيَاس (<i>qiyās</i>, “measurement, analogy”)'

    >>> render_foreign_derivation("adapted borrowing", ["ajp", "ota", "باشلامق"], defaultdict(str, {"t": "to begin", "tr": "başlamak"}))
    'Adapted borrowing of Ottoman Turkish باشلامق (<i>başlamak</i>, “to begin”)'
    >>> render_foreign_derivation("adapted borrowing", ["ajp", "ota", "-"], defaultdict(str))
    'Adapted borrowing from Ottoman Turkish'

    >>> render_foreign_derivation("psm", ["en", "yue", "-"], defaultdict(str))
    'Phono-semantic matching of Cantonese'
    >>> render_foreign_derivation("translit", ["en", "ar", "عَالِيَة"], defaultdict(str))
    'Transliteration of Arabic عَالِيَة (<i>ʕāliya</i>)'
    >>> render_foreign_derivation("back-form", ["en", "zero derivation"], defaultdict(str, {"nocap":"1"}))
    'back-formation from <i>zero derivation</i>'
    >>> render_foreign_derivation("bf", ["en"], defaultdict(str))
    'Back-formation'

    >>> render_foreign_derivation("l", ["cs", "háček"], defaultdict(str))
    'háček'
    >>> render_foreign_derivation("l", ["en", "go", "went"], defaultdict(str))
    'went'
    >>> render_foreign_derivation("l", ["en", "God be with you"], defaultdict(str))
    'God be with you'
    >>> render_foreign_derivation("l", ["la", "similis"], defaultdict(str, {"t":"like"}))
    'similis (“like”)'
    >>> render_foreign_derivation("l", ["la", "similis", "", "like"], defaultdict(str))
    'similis (“like”)'
    >>> render_foreign_derivation("l", ["mul", "☧", ""], defaultdict(str))
    '☧'
    >>> render_foreign_derivation("l", ["ru", "ру́сский", "", "Russian"], defaultdict(str, {"g":"m"}))
    'ру́сский <i>m</i> (<i>rússkij</i>, “Russian”)'
    >>> render_foreign_derivation("link", ["en", "water vapour"], defaultdict(str))
    'water vapour'
    >>> render_foreign_derivation("ll", ["en", "cod"], defaultdict(str))
    'cod'

    >>> render_foreign_derivation("m", ["en", "more"], defaultdict(str))
    '<b>more</b>'
    >>> render_foreign_derivation("m", ["en", "w:Group of Eight"], defaultdict(str))
    '<b>Group of Eight</b>'
    >>> render_foreign_derivation("m", ["enm", "us"], defaultdict(str))
    '<i>us</i>'
    >>> render_foreign_derivation("m", ["enm", "w:Group of Eight"], defaultdict(str))
    '<i>Group of Eight</i>'
    >>> render_foreign_derivation("m", ["ine-pro", "*h₁ed-"], defaultdict(str, {"t":"to eat"}))
    '<i>*h₁ed-</i> (“to eat”)'
    >>> render_foreign_derivation("m", ["ar", "عِرْق", "", "root"], defaultdict(str))
    'عِرْق (<i>ʕirq</i>, “root”)'
    >>> render_foreign_derivation("m", ["pal"], defaultdict(str, {"tr":"ˀl'k'", "ts":"erāg", "t":"lowlands"}))
    "(<i>ˀl'k'</i> /erāg/, “lowlands”)"
    >>> render_foreign_derivation("m", ["ar", "عَرِيق", "", "deep-rooted"], defaultdict(str))
    'عَرِيق (<i>ʕarīq</i>, “deep-rooted”)'
    >>> render_foreign_derivation("m", ["grc", "Τ//τ"], defaultdict(str, {"tr": "-"}))
    '<i>Τ / τ</i>'

    >>> render_foreign_derivation("langname-mention", ["en", "-"], defaultdict(str))
    'English'
    >>> render_foreign_derivation("m+", ["en", "-"], defaultdict(str))
    'English'
    >>> render_foreign_derivation("m+", ["ja", "力車"], defaultdict(str, {"tr":"rikisha"}))
    'Japanese 力車 (<i>rikisha</i>)'
    """
    # Short path for the {{m|en|WORD}} template
    if tpl in {"m", "m-lite"} and len(parts) == 2 and not data:
        word = parts[1]
        if word.startswith("w:"):
            word = word[2:]
        return strong(word) if parts[0] in {"en", "mul"} else italic(word)

    mentions = (
        "back-formation",
        "backformation",
        "back-form",
        "backform",
        "bf",
        "l",
        "l-lite",
        "link",
        "ll",
        "mention",
        "m",
        "m-lite",
    )
    dest_lang_ignore = (
        "cog",
        "cog-lite",
        "cognate",
        "etyl",
        "false cognate",
        "fcog",
        "langname-mention",
        "m+",
        "nc",
        "ncog",
        "noncog",
        "noncognate",
        *mentions,
    )
    if tpl not in dest_lang_ignore and parts:
        parts.pop(0)  # Remove the destination language

    dst_locale = parts.pop(0) if parts else data["2"]

    if tpl == "etyl" and parts:
        parts.pop(0)

    phrase = ""
    starter = ""
    if data["notext"] != "1":
        if tpl in {"bor+"}:
            starter = "borrowed from "
        elif tpl in {"adapted borrowing", "abor"}:
            if is_from := bool(parts and parts[0] == "-"):
                parts.pop(0)
            starter = "adapted borrowing " + ("from " if is_from else "of ")
        elif tpl in {"calque", "cal", "clq"}:
            starter = "calque of "
        if tpl in {"der+"}:
            starter = "derived from "
        if tpl in {"false cognate", "fcog"}:
            starter = "false cognate of "
        elif tpl in {"inh+"}:
            starter = "inherited from "
        elif tpl in {"partial calque", "pcal", "pclq"}:
            starter = "partial calque of "
        elif tpl in {"semantic loan", "sl"}:
            starter = "semantic loan of "
        elif tpl in {"learned borrowing", "lbor"}:
            starter = "learned borrowing from "
        elif tpl in {"semi-learned borrowing", "slbor"}:
            starter = "semi-learned borrowing from "
        elif tpl in {"orthographic borrowing", "obor"}:
            starter = "orthographic borrowing from "
        elif tpl in {"unadapted borrowing", "ubor"}:
            starter = "unadapted borrowing from "
        elif tpl in {"phono-semantic matching", "psm"}:
            starter = "phono-semantic matching of "
        elif tpl in {"transliteration", "translit"}:
            starter = "transliteration of "
        elif tpl in {"back-formation", "backformation", "back-form", "backform", "bf"}:
            starter = "back-formation"
            if parts:
                starter += " from"
        phrase = starter if data["nocap"] == "1" else starter.capitalize()

    lang = "translingual" if dst_locale == "mul" else langs.get(dst_locale, "")
    phrase += lang if tpl not in mentions else ""

    if parts or data["3"]:
        word = parts.pop(0) if parts else data["3"]
        if word.startswith("w:"):
            word = word[2:]
        if word == "-":
            return phrase
        if "//" in word:
            word = word.replace("//", " / ")
    else:
        word = ""

    word = data["alt"] or word
    gloss = data["t"] or data["gloss"]

    if parts:
        word = parts.pop(0) or word  # 4, alt=

    if tpl in {"l", "l-lite", "link", "ll"}:
        phrase += f" {word}"
    elif word:
        if (
            (starter == "partial calque of " and dst_locale in {"mul", "zh"})
            or starter == "adapted borrowing of "
            or dst_locale in {"ar", "ja"}
        ):
            phrase += f" {word}"
        else:
            phrase += f" {italic(word)}"
    if data["g"]:
        phrase += f" {gender_number_specs(data['g'])}"
    trans = "" if data["tr"] else transliterate(dst_locale, word)
    if parts:
        gloss = parts.pop(0)  # 5, t=, gloss=

    phrase += gloss_tr_poss(data, gloss, trans=trans)

    return phrase.lstrip()


def render_fa_sp(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_fa_sp("fa sp", ["en", "SH"], defaultdict(str, {"id": "self-harm", "t": "self-harm"}))
    '<i>Filter-avoidance spelling of</i> <b>SH</b> (“self-harm”).'
    """
    text = italic(("f" if data["nocap"] == "1" else "F") + "ilter-avoidance spelling of")
    text += f" {strong(parts[1])}"
    if t := data["t"]:
        text += f" (“{t}”)"
    dot = "" if data["nodot"] == "1" else (data["dot"] or ".")
    return f"{text}{dot}"


def render_fa_xlit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_fa_xlit("fa-xlit", ["اَرَاکِی"], defaultdict(str))
    'arākī&nbsp;/ arâki'
    """
    # Source: https://en.wiktionary.org/w/index.php?title=Module:fa-translit&oldid=85098029

    from .transliterator.fa import romanize_ira

    def cls_tr(text: str) -> str:
        # If // is present, ignore // and everything after
        text = re.sub(r"//.*", "", text)
        return transliterate("fa", text)

    def ira_tr(text: str) -> str:
        # If // is present, ignore everything before and including //
        text = re.sub(r"^.*//", "", text)
        result = transliterate("fa", text)

        # Apply IRA romanization
        return romanize_ira(result)

    return f"{cls_tr(parts[0])}&nbsp;/ {ira_tr(parts[0])}"


def render_form_of_t(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_form_of_t("eye dialect of", ["en", "ye#Etymology 6"], defaultdict(str, {"t": "t", "from": "from", "from2": "from2"}))
    '<i>Eye dialect spelling of</i> <b>ye</b> (“t”)<i>, representing from and from2 English</i>'

    >>> render_form_of_t("alternative spelling of", ["en" , "ye"], defaultdict(str, {"from": "from", "from2": "from2"}))
    '<i>From and from2 spelling of</i> <b>ye</b>'

    >>> render_form_of_t("initialism of", ["en", "w:Shockwave Flash"], defaultdict(str))
    '<i>Initialism of</i> <b>Shockwave Flash</b>'
    >>> render_form_of_t("initialism of", ["en", "optical character reader"], defaultdict(str, {"dot": "&nbsp;(the scanning device)"}))
    '<i>Initialism of</i> <b>optical character reader</b>&nbsp;(the scanning device)'
    >>> render_form_of_t("initialism of", ["en", "optical character reader"], defaultdict(str, {"tr": "tr", "t": "t", "ts": "ts"}))
    '<i>Initialism of</i> <b>optical character reader</b> (<i>tr</i> /ts/, “t”)'
    >>> render_form_of_t("initialism of", ["en", "OCR", "optical character reader"], defaultdict(str, {"nodot": "1", "nocap": "1"}))
    '<i>initialism of</i> <b>optical character reader</b>'

    >>> render_form_of_t("standard spelling of", ["en", "Irish Traveller"], defaultdict(str, {"from": "Irish English"}))
    '<i>Irish English standard spelling of</i> <b>Irish Traveller</b>'
    >>> render_form_of_t("standard spelling of", ["en", "enroll"], defaultdict(str))
    '<i>Standard spelling of</i> <b>enroll</b>'
    >>> render_form_of_t("cens sp", ["en", "bitch"], defaultdict(str))
    '<i>Censored spelling of</i> <b>bitch</b>'

    >>> render_form_of_t("pronunciation spelling of", ["en", "everything"], defaultdict(str, {"from": "AAVE"}))
    '<i>Pronunciation spelling of</i> <b>everything</b><i>, representing African-American Vernacular English</i>'

    >>> render_form_of_t("spelling of", ["en", "British alternative", "NORAD"], defaultdict(str))
    '<i>British alternative spelling of</i> <b>NORAD</b>'
    """
    from . import templates_italic

    form = form_of_templates[tpl]
    starter = form["value"]

    if "{{{2}}}" in starter:
        starter = starter.replace("{{{2}}}", parts[1])

    lang = data["1"] or (parts.pop(0) if parts else "")
    initial_cap = (
        (initial_cap_raw := form["initial-cap"]) == "English only" and lang == "en" or initial_cap_raw == "yes"
    )
    ender = ""
    word = (data["2"] or (parts.pop(0) if parts else "")).split("#", 1)[0]

    text = data["alt"] or data["3"] or (parts.pop(0) if parts else "")
    gloss = data["t"] or data["gloss"] or data["4"] or (parts.pop(0) if parts else "")
    word = text or word
    if word.startswith("w:"):
        word = word[2:]

    if fromtext := join_names(data, "from", " and "):
        from_suffix = "form of"
        if tpl == "standard spelling of":
            from_suffix = "standard spelling of"
        elif tpl == "alternative spelling of":
            from_suffix = "spelling of"
        elif tpl in {
            "eye dialect of",
            "pronunciation spelling of",
            "pronunciation variant of",
        }:
            ender = italic(f", representing {templates_italic.get(data['from'], fromtext)} {langs[lang]}")
        if not ender:
            starter = f"{fromtext} {from_suffix}"

    if initial_cap and not data["nocap"]:
        starter = capitalize(starter)
    phrase = italic(starter)
    phrase += f" {strong(word)}"
    phrase += gloss_tr_poss(data, gloss)
    if ender:
        phrase += ender
    if dot := data["dot"]:
        phrase += dot
    return phrase


def render_frac(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_frac("frac", ["39", "47", "127"], defaultdict(str))
    '39<small><sup>47</sup><big>⁄</big><sub>127</sub></small>'
    >>> render_frac("frac", ["39", "47"], defaultdict(str))
    '<small><sup>39</sup><big>⁄</big><sub>47</sub></small>'
    >>> render_frac("frac", ["39"], defaultdict(str))
    '<small><sup>1</sup><big>⁄</big><sub>39</sub></small>'
    """
    phrase = ""
    if len(parts) == 3:
        phrase = f"{parts[0]}<small><sup>{parts[1]}</sup><big>⁄</big><sub>{parts[2]}</sub></small>"
    elif len(parts) == 2:
        phrase = f"<small><sup>{parts[0]}</sup><big>⁄</big><sub>{parts[1]}</sub></small>"
    elif len(parts) == 1:
        phrase = f"<small><sup>1</sup><big>⁄</big><sub>{parts[0]}</sub></small>"
    return phrase


def render_g(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_g("g", ["m"], defaultdict(str))
    '<i>m</i>'
    >>> render_g("g", ["m", "f-p"], defaultdict(str))
    '<i>m</i> <i>or</i> <i>f pl</i>'
    """
    return " <i>or</i> ".join([gender_number_specs(part) for part in parts])


def render_geochronology(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    Source: https://en.wiktionary.org/w/index.php?title=Template:geochronology&oldid=73432381

    >>> render_geochronology("geochronology", ["en", "Hadean"], defaultdict(str))
    '<i>(geology)</i> The Hadean eon; part of the Precambrian supereon, spanning from around 4.6 to 4 billion years ago.'
    """
    lang = parts.pop(0)
    unit = parts.pop(0)

    desc = "The " if lang == "en" else "the"
    desc += f"{unit} {geochronology.unit_to_type[unit]}"
    desc += "; " if lang == "en" else " ("

    if unit in {"Precambrian", "Phanerozoic"}:
        pass
    elif parent := geochronology.unit_to_parent.get(unit):
        parent_type = geochronology.unit_to_type[parent]
        desc += f"part of the {parent} {parent_type}, "

    desc += f"spanning from {geochronology.unit_span.get(unit, 'unknown time span')}"
    desc += "." if lang == "en" else ")"

    return f"<i>(geology)</i> {desc}"


def render_given_name(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_given_name("given name", ["en" , "male"], defaultdict(str))
    '<i>A male given name</i>'
    >>> render_given_name("given name", ["en" , "male"], defaultdict(str, {"or":"female", "A":"a Japanese"}))
    '<i>a Japanese male or female given name</i>'
    >>> render_given_name("given name", ["en" , "male"], defaultdict(str, {"from":"Spanish", "from2":"Portuguese", "from3":"French"}))
    '<i>A male given name from Spanish, Portuguese or French</i>'
    >>> render_given_name("given name", ["en" , "male"], defaultdict(str, {"from":"la:Patricius<t:patrician>"}))
    '<i>A male given name from Latin Patricius (“patrician”)</i>'
    >>> render_given_name("given name", ["en" , "female"], defaultdict(str, {"from":"place names", "usage":"modern", "var":"Savannah"}))
    '<i>A female given name transferred from the place name, of modern usage, variant of Savannah</i>'
    >>> render_given_name("given name", ["da" , "male"], defaultdict(str, {"eq":"Bertram,fr:Bertrand"}))
    '<i>A male given name, equivalent to English Bertram or French Bertrand</i>'
    >>> render_given_name("given name", ["en" , "female"], defaultdict(str, {"from":"Hebrew", "m":"Daniel", "f":"Daniela"}))
    '<i>A female given name from Hebrew, masculine equivalent Daniel, feminine equivalent Daniela</i>'
    >>> render_given_name("given name", ["lv" , "male"], defaultdict(str, {"from":"Slavic languages", "eq":"pl:Władysław,cs:Vladislav,ru:Владисла́в"}))
    '<i>A male given name from the Slavic languages, equivalent to Polish Władysław, Czech Vladislav or Russian Владисла́в (Vladisláv)</i>'
    >>> render_given_name("given name", ["en" , "male"], defaultdict(str, {"from":"Germanic languages", "from2":"surnames"}))
    '<i>A male given name from the Germanic languages or transferred from the surname</i>'
    >>> render_given_name("given name", ["en", "female"], defaultdict(str, {"from":"coinages", "var":"Cheryl", "var2":"Shirley"}))
    '<i>A female given name originating as a coinage, variant of Cheryl or Shirley</i>'
    >>> render_given_name("given name", ["en", "male"], defaultdict(str, {"dim":"Mohammed", "dim2":"Moses", "dim3":"Maurice"}))
    '<i>A diminutive of the male given names Mohammed, Moses or Maurice</i>'
    >>> render_given_name("given name", ["en", "male", ], defaultdict(str, {"dim":"Mohammed"}))
    '<i>A diminutive of the male given name Mohammed</i>'
    >>> render_given_name("given name", ["en", "female"], defaultdict(str, {"diminutive":"Florence", "diminutive2":"Flora"}))
    '<i>A diminutive of the female given names Florence or Flora</i>'
    >>> render_given_name("given name", ["en", "male"], defaultdict(str, {"from":"Hindi", "meaning":"patience"}))
    '<i>A male given name from Hindi, meaning "patience"</i>'
    >>> render_given_name("given name", ["en", "female"], defaultdict(str, {"from":"Danish < grc:Αἰκατερῑ́νη", "var": "Karen"}))
    '<i>A female given name from Danish [in turn from Ancient Greek Αἰκατερῑ́νη], variant of Karen</i>'
    >>> render_given_name("given name", ["en", "male"], defaultdict(str, {"from":"la:Gabriēl < grc:Γαβρῑήλ < hbo:גַּבְרִיאֵל<tr:gaḇrīʾḗl><t:God is my strong man>"}))
    '<i>A male given name from Latin Gabriēl [in turn from Ancient Greek Γαβρῑήλ, in turn from Biblical Hebrew גַּבְרִיאֵל (<i>gaḇrīʾḗl</i>, “God is my strong man”)]</i>'
    >>> render_given_name("given name", ["da", "male"], defaultdict(str, {"usage":"traditionally popular", "eq": "Nicholas", "from":"la:Nīcolāī<pos:genitive>", "from2":"ru:Никола́й"}))
    '<i>A male given name from Latin Nīcolāī (genitive) or Russian Никола́й, of traditionally popular usage, equivalent to English Nicholas</i>'

    """
    parts.pop(0)  # language
    gender = data["gender"] or (parts.pop(0) if parts else "")
    gender += f" or {data['or']}" if data["or"] else ""
    phrase = f"{data['A'] or 'A'} "
    dimtext = join_names(data, "dim", " or ", include_langname=False, key_alias="diminutive")
    phrase += "diminutive of the " if dimtext else ""
    phrase += f"{gender} given name"
    phrase += "s" if ", " in dimtext or " or " in dimtext else ""
    phrase += f" {dimtext}" if dimtext else ""

    class Seg(TypedDict, total=False):
        prefix: str
        suffixes: list[str]

    fromsegs: list[Seg] = []
    lastfrom_seg: Seg = {}
    for i in range(1, 10):
        from_key = f"from{i}" if i != 1 else "from"
        if data[from_key]:
            from_text = data[from_key]
            suffix = ""
            if from_text == "surnames":
                prefix = "transferred from the "
                suffix = "surname"
            elif from_text == "place names":
                prefix = "transferred from the "
                suffix = "place name"
            elif from_text == "coinages":
                prefix = "originating as "
                suffix = "a coinage"
            else:
                prefix = "from "
                from_texts = [from_text]
                if " < " in from_text:
                    from_texts = from_text.split(" < ")
                prepend = False
                for from_text in from_texts:
                    if suffix:
                        suffix += ", in turn from " if prepend else " [in turn from "
                        prepend = True
                    if ":" in from_text:
                        # get t:
                        # remove <>
                        from_gloss = ""
                        from_data: defaultdict[str, str] = defaultdict(str)
                        matches = re.findall(r"<([^:]*):([^>]*)>", from_text)
                        for match in matches:
                            if match[0] == "t":
                                from_gloss = match[1]
                            else:
                                from_data[match[0]] = match[1]
                        from_text = re.sub(r"<([^>]*)>", "", from_text)
                        # todo fromalt
                        from_split = from_text.split(":")
                        lang = langs.get(from_split[0], from_split[0])
                        suffix += f"{lang} {from_split[1] if len(from_split) > 1 else ''}"
                        suffix += gloss_tr_poss(from_data, from_gloss)
                    elif from_text.endswith("languages"):
                        suffix = f"the {from_text}"
                    else:
                        suffix += from_text
                if prepend:
                    suffix += "]"
            if lastfrom_seg and lastfrom_seg.get("prefix", "") != prefix:
                fromsegs.append(lastfrom_seg)
                lastfrom_seg = {}
            if not lastfrom_seg:
                lastfrom_seg = {"prefix": prefix, "suffixes": []}
            lastfrom_seg["suffixes"].append(suffix)
    if lastfrom_seg:
        fromsegs.append(lastfrom_seg)
    if localphrase := [
        fromseg.get("prefix", "") + concat(fromseg.get("suffixes", []), ", ", last_sep=" or ") for fromseg in fromsegs
    ]:
        phrase += " " + concat(localphrase, ", ", last_sep=" or ")

    if meaningtext := join_names(data, "meaning", " or ", include_langname=False, prefix='"', suffix='"'):
        phrase += f", meaning {meaningtext}"

    if data["usage"]:
        phrase += ", of " + data["usage"] + " usage"

    if vartext := join_names(data, "var", " or "):
        phrase += f", variant of {vartext}"
    if mtext := join_names(data, "m", " and "):
        phrase += f", masculine equivalent {mtext}"
    if ftext := join_names(data, "f", " and "):
        phrase += f", feminine equivalent {ftext}"
    if eqext := join_names(data, "eq", " or ", include_langname=True):
        phrase += f", equivalent to {eqext}"

    return italic(phrase)


def render_han_simp(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_han_simp("Han simp", ["請"], defaultdict(str, {"f": "言", "t": "讠"}))
    'Simplified from 請 (言 → 讠)'
    >>> render_han_simp("Han simp", ["讀"], defaultdict(str, {"f": "言", "t": "讠", "f2": "賣", "t2": "卖"}))
    'Simplified from 讀 (言 → 讠 and 賣 → 卖)'
    """
    if data["a"]:
        assert 0
    text = ("s" if data["nocap"] else "S") + f"implified from {parts[0]} ("
    if f1 := data["f"]:
        text += f"{f1} → {data['t']}"
    if f2 := data["f2"]:
        text += f" and {f2} → {data['t2']}"
    return f"{text})"


def render_he_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_he_l("he-l", ["הר מגידו"], defaultdict(str, {"dwv": "הַר מְגִדּוֹ", "tr": "har megiddo"}))
    'הר מגידו / הַר מְגִדּוֹ (<i>har megiddo</i>)'
    """
    if dwv := data["dwv"]:
        parts[0] += f" / {dwv}"
    parts.insert(0, "he")
    return render_foreign_derivation("l", parts, data, word=word)


def render_he_m(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_he_m("he-m", ["צייר"], defaultdict(str, {"dwv": "צַיָּר", "tr": "tsayár"}))
    '<i>צייר / צַיָּר</i> (<i>tsayár</i>)'
    """
    if dwv := data["dwv"]:
        parts[0] += f" / {dwv}"
    parts.insert(0, "he")
    return render_foreign_derivation("m", parts, data, word=word)


def render_he_root(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_he_root("he-root", ["ל", "מ", "ד"], defaultdict(str))
    'From the root ל־מ־ד'
    >>> render_he_root("he-root", ["ל", "מ", "ד"], defaultdict(str, {"tr": "l-m-d", "nocap": "1"}))
    'from the root ל־מ־ד (l-m-d)'
    """
    text = f"{'f' if data['nocap'] else 'F'}rom the root {'־'.join(parts)}"
    if tr := data["tr"]:
        text += f" ({tr})"
    return text


def render_historical_given_name(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_historical_given_name("historical given name", ["en" , "male", "Saint Abundius, an early Christian bishop"], defaultdict(str))
    '<i>A male given name of historical usage, notably borne by Saint Abundius, an early Christian bishop</i>'
    >>> render_historical_given_name("historical given name", ["en" , "male"], defaultdict(str, {"eq": "John", "A":""}))
    '<i>male given name of historical usage, equivalent to English <b>John</b></i>'
    """
    data["1"] or (parts.pop(0) if parts else "")
    sex = data["2"] or (parts.pop(0) if parts else "")
    desc = data["3"] or (parts.pop(0) if parts else "")
    article = data.get("A", "A")
    phrase = f"{article} " if article else ""
    phrase += f"{sex} "
    phrase += "given name of historical usage"
    if data["eq"]:
        phrase += f", equivalent to English {strong(data['eq'])}"
    if desc:
        phrase += f", notably borne by {desc}"
    return italic(phrase)


def render_iata(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iata("IATA", ["London", "", "United Kingdom"], defaultdict(str, {"met": "1", "a1": "Heathrow Airport", "a2": "Gatwick Airport", "a3": "Stansted Airport", "a4": "Luton Airport", "a5": "London City Airport", "a6": "Southend Airport", "a7": "Biggin Hill Airport"}))
    '(<i>international standards, aviation</i>) <i>IATA metropolitan area code for</i> <b>London</b>, United Kingdom, <i>collectively referring to the airport system of Heathrow Airport, Gatwick Airport, Stansted Airport, Luton Airport, London City Airport, Southend Airport and Biggin Hill Airport</i>.'

    >>> render_iata("IATA", ["Anaa Airport", "", "Anaa", "", "French Polynesia"], defaultdict(str))
    '(<i>international standards, aviation</i>) <i>IATA airport code for</i> <b>Anaa Airport</b>, <i>which serves Anaa, French Polynesia</i>.'
    >>> render_iata("IATA", ["Anaa Airport", "", "Anaa", "", "French Polynesia"], defaultdict(str, {"mil": "1", "until": "2025"}))
    '(<i>international standards, aviation</i>) <i>IATA airport code for</i> <b>Anaa Airport</b>, <i>in Anaa, French Polynesia until 2025</i>.'
    """

    def p2_or_p1() -> str:
        name1 = parts.pop(0)
        name2 = parts.pop(0) if parts else ""
        return name2 or name1

    label = "international standards, aviation"
    if data["obs"]:
        label += ", obsolete"
    label = f"(<i>{label}</i>) <i>"
    if data["obs"]:
        label += "Former "
    label += "IATA"

    # Metropolitan area code mode
    if data["met"]:
        met_parts = [f"metropolitan area code for</i> <b>{p2_or_p1()}</b>"]
        while parts:
            met_parts.append(p2_or_p1())
        met_desc = ", ".join(met_parts)
        text = f"{label} {met_desc}, <i>collectively referring to the airport system of {data['a1']}"

        if airports := [airport for idx in range(2, 8) if (airport := data[f"a{idx}"])]:
            text += f", {concat(airports, ', ', last_sep=' and ')}"
        return f"{text}</i>."

    # Airport code mode
    text = f"{label} airport code for</i> <b>{p2_or_p1()}</b>"
    extras = []
    if parts:
        extras.append(f"{'in' if data['mil'] else 'which serves'} {p2_or_p1()}")
    while parts:
        extras.append(p2_or_p1())
    if extras:
        text += f", <i>{', '.join(extras)}"
    if until := data["until"]:
        text += f" until {until}"
    return f"{text}</i>."


def render_ipa_char(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ipa_char("historical given name", ["[tʃ]"], defaultdict(str))
    '[tʃ]'
    >>> render_ipa_char("historical given name", ["[tʃ]", "[ts]"], defaultdict(str))
    '[tʃ], [ts]'
    """
    return concat(parts, ", ")


def render_iso_216(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iso_216("ISO 216", ["1189", "1682"], defaultdict(str))
    '(<i>international standards</i>) ISO 216 standard paper size of 1189 mm × 1682 mm (46.81 in × 66.22 in), with a surface area of 2 m² (21.53 sq ft).'
    >>> render_iso_216("ISO 216", ["1189", "1682"], defaultdict(str, {"env": "1"}))
    '(<i>international standards</i>) ISO 216 standard envelope size of 1189 mm × 1682 mm (46.81 in × 66.22 in), with a surface area of 2 m² (21.53 sq ft).'
    >>> render_iso_216("ISO 216", ["1189", "1682"], defaultdict(str, {"untrimmed": "1"}))
    '(<i>international standards</i>) ISO 216 standard untrimmed paper size of 1189 mm × 1682 mm (46.81 in × 66.22 in), with a surface area of 2 m² (21.53 sq ft).'
    """
    width_mm = float(parts[0])
    height_mm = float(parts[1])

    if data["env"]:
        paper_type = "envelope"
    elif data["untrimmed"]:
        paper_type = "untrimmed paper"
    else:
        paper_type = "paper"

    # Dimensions in inches
    width_in = round(width_mm / 25.4, 2)
    height_in = round(height_mm / 25.4, 2)

    # Surface area in m² or cm²
    area_m2 = width_mm * height_mm / 1_000_000
    area_cm2 = width_mm * height_mm / 100

    def no_trailing_zeros(v: float) -> str:
        return str(v).rstrip("0").rstrip(".")

    # Decide between m² and cm²
    if area_m2 > 0.1:
        # Number of significant digits, at least 2
        sig_digits = math.ceil(-math.log10(area_m2)) + 2 if area_m2 < 1 else 2
        area_value = round(area_m2, sig_digits)
        area_str = f"{no_trailing_zeros(area_value)} m²"
    else:
        sig_digits = math.ceil(-math.log10(area_cm2)) + 2 if area_cm2 < 1 else 2
        area_value = round(area_cm2, sig_digits)
        area_str = f"{no_trailing_zeros(area_value)} cm²"

    # Surface area in sq ft or sq in
    area_ft2 = width_mm * height_mm / 92903.04
    area_in2 = width_mm * height_mm / 645.16
    if area_ft2 > 1:
        sig_digits = math.ceil(-math.log10(area_ft2)) + 2 if area_ft2 < 10 else 2
        imperial_area_value = round(area_ft2, sig_digits)
        imperial_area_str = f"{no_trailing_zeros(imperial_area_value)} sq ft"
    else:
        sig_digits = math.ceil(-math.log10(area_in2)) + 2 if area_in2 < 10 else 2
        imperial_area_value = round(area_in2, sig_digits)
        imperial_area_str = f"{no_trailing_zeros(imperial_area_value)} sq in"

    return (
        f"(<i>international standards</i>) {tpl} standard {paper_type} size of "
        f"{no_trailing_zeros(width_mm)} mm × {no_trailing_zeros(height_mm)} mm "
        f"({width_in} in × {height_in} in), with a surface area of "
        f"{area_str} ({imperial_area_str})."
    )


def render_iso_217(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iso_217("ISO 217", ["1189", "1682"], defaultdict(str, {"untrimmed": "1"}))
    '(<i>international standards</i>) ISO 217 standard untrimmed paper size of 1189 mm × 1682 mm (46.81 in × 66.22 in), with a surface area of 2 m² (21.53 sq ft).'
    """
    data["untrimmed"] = "1"
    return render_iso_216(tpl, parts, data, word=word)


def render_iso_639(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iso_639("ISO 639", [], defaultdict(str), word="ysr")
    '<i>(international standards) language code for</i> <b>Sirenik</b>.'
    >>> render_iso_639("ISO 639", ["ja"], defaultdict(str))
    'ISO 639-1 code <b>ja</b>'
    >>> render_iso_639("ISO 639", ["", "crk"], defaultdict(str))
    'ISO 639-2 code <b>crk</b>'
    >>> render_iso_639("ISO 639", ["", "", "zho"], defaultdict(str))
    'ISO 639-3 code <b>zho</b>'
    >>> render_iso_639("ISO 639", ["zh", "", "zho"], defaultdict(str, {"ref": "1"}))
    'ISO 639-1 code <b>zh</b>, ISO 639-3 code <b>zho</b>'
    >>> render_iso_639("ISO 639", ["3", "Ambonese Malay"], defaultdict(str))
    '(<i>international standards</i>) <i>ISO 639-3 language code for</i> <b>Ambonese Malay</b>.'
    >>> render_iso_639("ISO 639", ["1"], defaultdict(str), word="ab")
    '(<i>international standards</i>) <i>ISO 639-1 language code for</i> <b>Abkhaz</b>.'
    >>> render_iso_639("ISO 639", ["3", "Asa language", "Asa"], defaultdict(str, {"obs": "1"}), word="aam")
    '(<i>international standards, obsolete</i>) <i>Former ISO 639-3 language code for</i> <b>Asa</b>.'
    >>> render_iso_639("ISO 639", ["3", "Ari language (New Guinea)", "Ari"], defaultdict(str, {"dab": "New Guinea"}), word="aac")
    '(<i>international standards</i>) <i>ISO 639-3 language code for</i> <b>Ari</b> (New Guinea).'
    """
    if not parts:
        return f"{italic('(international standards) language code for')} {strong(langs[word])}."

    if parts[0].isdigit():
        phrase = f"({italic('international standards' + (', obsolete' if data['obs'] else ''))}) "
        phrase += f"{italic(('Former ' if data['obs'] else '') + 'ISO 639-' + parts[0] + ' language code for')} "
        phrase += strong(parts[-1] if len(parts) > 1 else langs[word])
        if dab := data["dab"]:
            phrase += f" ({dab})"
        return f"{phrase}."

    return ", ".join([f"ISO 639-{idx} code {strong(part)}" for idx, part in enumerate(parts, 1) if part])


def render_iso_3166(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iso_3166("ISO 3166", ["1", "3", "Aruba"], defaultdict(str, {"from": "1986"}), word="ABW")
    '(<i>international standards</i>) <i>ISO 3166-1 alpha-3 country code for</i> <b>Aruba</b> <i>since 1986</i>.'
    >>> render_iso_3166("ISO 3166", ["1", "2", "Ascension Island"], defaultdict(str, {"obs": "1"}), word="AC")
    '(<i>international standards, obsolete</i>) <i>Former ISO 3166-1 alpha-2 country code for</i> <b>Ascension Island</b>.'
    >>> render_iso_3166("ISO 3166", ["1", "2", "Ascension Island"], defaultdict(str, {"exr": "1"}), word="AC")
    '(<i>international standards</i>) <i>Exceptionally reserved ISO 3166-1 alpha-2 country code for</i> <b>Ascension Island</b>.'
    >>> render_iso_3166("ISO 3166", ["1", "2", "Ascension Island"], defaultdict(str, {"inr": "1"}), word="AC")
    '(<i>international standards</i>) <i>Indeterminately reserved ISO 3166-1 alpha-2 country code for</i> <b>Ascension Island</b>.'
    """
    phrase = "(<i>international standards"
    if data["obs"]:
        phrase += ", obsolete"
    phrase += "</i>) <i>"

    if data["exr"]:
        phrase += "Exceptionally reserved "
    elif data["inr"]:
        phrase += "Indeterminately reserved "
    elif data["obs"]:
        phrase += "Former "
    phrase += f"{tpl}-{parts[0]} alpha-{parts[1]} country code for</i> "

    phrase += strong(parts[-1] if len(parts) > 1 else langs[word])

    if since := data["from"]:
        phrase += f" <i>since {since}</i>"

    return f"{phrase}."


def render_iso_4217(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_iso_4217("ISO 4217", ["Cardano (blockchain platform)"], defaultdict(str))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano (blockchain platform)</b>.'
    >>> render_iso_4217("ISO 4217", ["Cardano (blockchain platform)", "Cardano"], defaultdict(str))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b>.'
    >>> render_iso_4217("ISO 4217", ["Cardano (blockchain platform)", "Cardano", "detail"], defaultdict(str))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b><i>; detail</i>.'

    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"unoff": "1", "crypto": "1"}))
    '(<i>international standards</i>) <i>Unofficial non-ISO 4217 currency code for the cryptocurrency</i> <b>Cardano</b>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"fund": "1"}))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b><i>; a unit of account</i>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"hist": "1"}))
    '(<i>international standards, historical</i>) <i>ISO 4217 currency code for the former</i> <b>Cardano</b>.'
    >>> render_iso_4217("ISO 4217", ["Cardano (blockchain platform)", "Cardano"], defaultdict(str, {"res": "1"}))
    '(<i>international standards</i>) <i>Reserved ISO 4217 currency code for the</i> <i>Cardano (blockchain platform)</i>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"obs": "1"}))
    '(<i>international standards, obsolete</i>) <i>Former ISO 4217 currency code for the</i> <b>Cardano</b>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"from": "1986"}))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b><i>; a currency used since 1986</i>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"to": "1986"}))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b><i>; a currency used until 1986</i>.'
    >>> render_iso_4217("ISO 4217", ["Cardano"], defaultdict(str, {"from": "1869", "to": "1986"}))
    '(<i>international standards</i>) <i>ISO 4217 currency code for the</i> <b>Cardano</b><i>; a currency used from 1869 to 1986</i>.'
    """
    phrase = "(<i>international standards"
    if data["hist"]:
        phrase += ", historical"
    if data["obs"]:
        phrase += ", obsolete"
    phrase += "</i>) <i>"

    if data["res"]:
        phrase += "Reserved "
    elif data["obs"]:
        phrase += "Former "
    elif data["unoff"]:
        phrase += "Unofficial non-"
    phrase += f"{tpl} currency code for the"
    if data["hist"]:
        phrase += " former"
    if data["crypto"]:
        phrase += " cryptocurrency"
    phrase += "</i> "

    if data["res"]:
        phrase += italic(parts[0])
    else:
        phrase += strong(parts[1 if len(parts) > 1 else 0])

    kind = "unit of account" if data["fund"] else "currency"
    if from_ := data["from"]:
        if to_ := data["to"]:
            phrase += f"<i>; a {kind} used from {from_} to {to_}</i>"
        else:
            phrase += f"<i>; a {kind} used since {from_}</i>"
    elif to_ := data["to"]:
        phrase += f"<i>; a {kind} used until {to_}</i>"
    elif data["fund"]:
        phrase += f"<i>; a {kind}</i>"

    if len(parts) > 2:
        phrase += f"<i>; {parts[2]}</i>"

    return f"{phrase}."


def render_ja_blend(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_blend("ja-blend", ["山%無し", "やま% なし", "落ち無し", "おち なし", "意味%無し", "いみ% なし"], defaultdict(str, {"t1": "no climax", "t2": "no point", "t3": "no meaning", "nocap": "1"}))
    'blend of <ruby>山<rt>やま</rt></ruby><ruby>無し<rt>なし</rt></ruby> (“no climax”) + <ruby>落ち無し<rt>おち なし</rt></ruby> (“no point”) + <ruby>意味<rt>いみ</rt></ruby><ruby>無し<rt>なし</rt></ruby> (“no meaning”)'
    """
    return f"{'b' if data['nocap'] else 'B'}lend of {render_ja_compound(tpl, parts, data, word=word)}"


def render_ja_compound(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_compound("ja-compound", ["小", "しょう", "学生", "がくせい", "の", "", "料%理", "りょう%り"], defaultdict(str, {"t1": "small", "t2": "student", "pos3": "possessive particle", "t4": "cuisine"}))
    '<ruby>小<rt>しょう</rt></ruby> (“small”) + <ruby>学生<rt>がくせい</rt></ruby> (“student”) + の (possessive particle) + <ruby>料<rt>りょう</rt></ruby><ruby>理<rt>り</rt></ruby> (“cuisine”)'
    >>> render_ja_compound("ja-compound", ["だ", "だ", "ってば", "ってば", "よ"], defaultdict(str, {"pos1": "auxiliary", "pos2": "informal emphatic particle", "pos3": "emphatic particle"}))
    'だ (auxiliary) + ってば (informal emphatic particle) + よ (emphatic particle)'
    """
    if len(parts) % 2 != 0:
        parts.append("")

    text: list[str] = []
    for idx, (part1, part2) in enumerate(zip(parts[::2], parts[1::2]), start=1):
        data_ = defaultdict(str)
        data_["t"] = data[f"t{idx}"] or data[f"pos{idx}"]
        if data[f"pos{idx}"]:
            data_["noquote"] = "1"
        text.append(render_ja_r(tpl, [part1, part2], data_, word=word))
    return concat(text, " + ")


def render_ja_etym_renyokei(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_etym_renyokei("ja-ryk", ["受ける"], defaultdict(str))
    "<ruby>連<rp>(</rp><rt>れん</rt><rp>)</rp></ruby><ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby><ruby>形<rp>(</rp><rt>けい</rt><rp>)</rp></ruby> (<i>ren'yōkei</i>, “stem or continuative form”) of the verb 受ける."
    >>> render_ja_etym_renyokei("ja-ryk", ["受ける", "うける"], defaultdict(str))
    "<ruby>連<rp>(</rp><rt>れん</rt><rp>)</rp></ruby><ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby><ruby>形<rp>(</rp><rt>けい</rt><rp>)</rp></ruby> (<i>ren'yōkei</i>, “stem or continuative form”) of the verb 受ける."
    >>> render_ja_etym_renyokei("ja-ryk", ["受ける", "うける", "to receive, to get"], defaultdict(str))
    "<ruby>連<rp>(</rp><rt>れん</rt><rp>)</rp></ruby><ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby><ruby>形<rp>(</rp><rt>けい</rt><rp>)</rp></ruby> (<i>ren'yōkei</i>, “stem or continuative form”) of the verb 受ける (“to receive, to get”)."
    """
    text = f"<ruby>連<rp>(</rp><rt>れん</rt><rp>)</rp></ruby><ruby>用<rp>(</rp><rt>よう</rt><rp>)</rp></ruby><ruby>形<rp>(</rp><rt>けい</rt><rp>)</rp></ruby> (<i>ren'yōkei</i>, “stem or continuative form”) of the verb {parts[0]}"
    if len(parts) > 2:
        text += f" (“{parts[2]}”)"
    return f"{text}."


def render_ja_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_l("ja-l", ["縄抜け"], defaultdict(str))
    '縄抜け'
    >>> render_ja_l("ja-l", ["縄抜け", "なわぬけ"], defaultdict(str))
    '縄抜け (なわぬけ)'
    >>> render_ja_l("ja-l", ["縄抜け", "なわぬけ", "nawanuke"], defaultdict(str))
    '縄抜け (なわぬけ, <i>nawanuke</i>)'
    """
    text = parts.pop(0)
    if parts:
        if len(parts) == 1:
            text += f" ({parts[0]})"
        else:
            text += f" ({parts[0]}, {italic(parts[1])})"
    return text


def render_ja_r(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_r("ja-r", ["羨ましい"], defaultdict(str))
    '羨ましい'
    >>> render_ja_r("ja-r", ["羨ましい", "羨ましい"], defaultdict(str))
    '羨ましい'
    >>> render_ja_r("ja-r", ["羨ましい", "うらやましい"], defaultdict(str))
    '<ruby>羨ましい<rt>うらやましい</rt></ruby>'
    >>> render_ja_r("ja-r", ["羨ましい", "うらやましい", "a"], defaultdict(str, {"lit": "lit"}))
    '<ruby>羨ましい<rt>うらやましい</rt></ruby> (“a”, literally “lit”)'
    >>> render_ja_r("ja-r", ["羨ましい", "", "a"], defaultdict(str, {"lit": "lit"}))
    '羨ましい (“a”, literally “lit”)'

    >>> render_ja_r("ja-r", ["任天堂", "^ニンテンドー"], defaultdict(str))
    '<ruby>任天堂<rt>ニンテンドー</rt></ruby>'

    >>> render_ja_r("ja-r", ["物%の%哀れ", "もの %の% あわれ"], defaultdict(str))
    '<ruby>物<rt>もの</rt></ruby>の<ruby>哀れ<rt>あわれ</rt></ruby>'
    >>> render_ja_r("ja-r", ["物 の 哀れ", "もの の あわれ"], defaultdict(str))
    '<ruby>物<rt>もの</rt></ruby>の<ruby>哀れ<rt>あわれ</rt></ruby>'

    >>> render_ja_r("ryu-r", ["唐手", "とーでぃー"], defaultdict(str, {"t": "Chinese hand"}))
    '<ruby>唐手<rt>とーでぃー</rt></ruby> (“Chinese hand”)'

    >>> render_ja_r("ja-compound", ["唐手", "とーでぃー"], defaultdict(str, {"t": "Chinese hand", "noquote": "1"}))
    '<ruby>唐手<rt>とーでぃー</rt></ruby> (Chinese hand)'
    """
    if len(parts) == 1 or not parts[1]:
        text = parts[0]
    else:
        if parts[0] == parts[1]:
            text = parts[0]
        else:
            parts[1] = parts[1].removeprefix("^")

            if sep := "%" if "%" in parts[0] else " " if " " in parts[0] else "":
                texts = [part.strip() for part in parts[0].split(sep)]
                tops = [part.strip() for part in parts[1].split(sep)]
                text = "".join(t if t == p else ruby(t, p) for t, p in zip(texts, tops))
            else:
                text = ruby(parts[0], parts[1])

    more: list[str] = []
    if len(parts) > 2:
        more.append(f"“{parts[2]}”")
    if lit := data["lit"]:
        more.append(f"literally “{lit}”")
    if t := data["t"]:
        more.append(t if data["noquote"] else f"“{t}”")
    if more:
        text += f" ({', '.join(more)})"

    return text


def render_ko_inline(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ko_inline("ko-l", ["한국어"], defaultdict(str))
    '한국어'
    >>> render_ko_inline("ko-l", ["한국어", "a"], defaultdict(str))
    '한국어 (<i>a</i>)'
    >>> render_ko_inline("ko-l", ["한국어", "a", "b"], defaultdict(str))
    '한국어 (<i>a</i>, “b”)'
    >>> render_ko_inline("ko-l", ["한국어", "a", "b", "c"], defaultdict(str))
    '한국어 (<i>a</i>, “b”)'
    >>> render_ko_inline("ko-l", ["한국어", "a", "b", "c", "d"], defaultdict(str))
    '한국어 (<i>a</i>, “b”) (<i>d</i>)'
    >>> render_ko_inline("ko-l", ["한국어", "a", "b", "c", "d", "e"], defaultdict(str))
    '한국어 (<i>a</i>, “b”) (<i>d</i>)'
    """
    # TODO: should be improved with transliteration
    text = parts.pop(0)
    if parts:
        text += f" (<i>{parts.pop(0)}</i>"
        if parts:
            text += f", “{parts.pop(0)}”"
        text += f") (<i>{parts[1]}</i>)" if len(parts) > 1 else ")"
    return text


def render_köppen(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_köppen("Köppen", ["tropical rainforest climate"], defaultdict(str))
    '<i>(climatology) Köppen climate classification for a</i> <b>tropical rainforest climate</b>.'
    >>> render_köppen("Köppen", ["tropical rainforest climate", "e-substitut", "something else"], defaultdict(str, {"an": "1"}))
    '<i>(climatology) Köppen climate classification for an</i> <b>e-substitut</b>, also known as a <b>something else</b>.'
    """
    text = "<i>(climatology) Köppen climate classification for a"
    if data["an"]:
        text += "n"
    text += f"</i> <b>{parts[1 if len(parts) > 1 else 0]}</b>"
    if len(parts) > 2:
        text += f", also known as a <b>{parts[-1]}</b>"
    return f"{text}."


def render_label(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_label("label", ["en" , "Australia", "slang"], defaultdict(str, {"nocat":"1"}))
    '<i>(Australia, slang)</i>'
    >>> render_label("lb", ["en" , "Australia"], defaultdict(str))
    '<i>(Australia)</i>'
    >>> render_label("lb", ["en" , "Australia", "or", "foobar"], defaultdict(str))
    '<i>(Australia or foobar)</i>'
    >>> render_label("lb", ["en" , "foobar", "and", "Australia", "or", "foobar"], defaultdict(str))
    '<i>(foobar and Australia or foobar)</i>'
    >>> render_label("lb", ["en" , "foobar", "_", "Australia", "foobar"], defaultdict(str))
    '<i>(foobar Australia, foobar)</i>'
    >>> # render_label("lb", ["en" , "roa-lor"], defaultdict(str))
    >>> # '<i>(Lorrain)</i>'
    >>> render_label("lbl", ["en" , "transitive"], defaultdict(str))
    '<i>(transitive)</i>'
    >>> render_label("lbl", ["en" , "ambitransitive"], defaultdict(str))
    '<i>(ambitransitive)</i>'
    >>> render_label("lbl", ["en" , "ambitransitive", "obsolete"], defaultdict(str))
    '<i>(ambitransitive, obsolete)</i>'
    >>> render_label("lbl", ["en" , "chiefly", "nautical"], defaultdict(str))
    '<i>(chiefly nautical)</i>'
    >>> render_label("lbl", ["en" , "", "nautical"], defaultdict(str))
    '<i>(nautical)</i>'
    """
    if len(parts) == 2:
        return term(lookup_italic(parts[1], "en"))

    res = ""
    omit_pre_comma = False
    omit_post_comma = True
    omit_pre_space = False
    omit_post_space = True

    for label in parts[1:]:
        omit_pre_comma = omit_post_comma
        omit_post_comma = False
        omit_pre_space = omit_post_space
        omit_post_space = False

        syntax = syntaxes.get(label)

        omit_comma = omit_pre_comma or (syntax["omit_pre_comma"] if syntax else False)
        omit_post_comma = syntax["omit_post_comma"] if syntax else False
        omit_space = omit_pre_space or (syntax["omit_pre_space"] if syntax else False)

        if label_display := lookup_italic(label, "en"):
            if res:
                res += "" if omit_comma else ","
                res += "" if omit_space else " "
            res += label_display

    return term(res)


def render_langname(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_langname("langname", ["en"], defaultdict(str))
    'English'
    """
    return langs[parts[0]]


def render_lit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lit("&lit", ["en", "foo", "bar"], defaultdict(str, {"nodot":"1"}))
    '<i>Used other than figuratively or idiomatically:</i> see <i>foo, bar</i>'
    >>> render_lit("&lit", ["en", "foo", "bar"], defaultdict(str, {"qualifier":"often", "dot":"!"}))
    '<i>often used other than figuratively or idiomatically:</i> see <i>foo, bar!</i>'
    >>> render_lit("&lit", ["en", "foo", "bar", "toto"], defaultdict(str))
    '<i>Used other than figuratively or idiomatically:</i> see <i>foo, bar, toto.</i>'
    >>> render_lit("&lit", ["en", "see <b>foo</b> or <b>bar</b>"], defaultdict(str))
    '<i>Used other than figuratively or idiomatically:</i> <i>see <b>foo</b> or <b>bar</b>.</i>'
    """
    starter = "Used other than figuratively or idiomatically"
    if data["qualifier"]:
        phrase = f"{data['qualifier']} {starter.lower()}"
    else:
        phrase = starter
    parts.pop(0)  # language
    endphrase = ""
    if parts:
        phrase += ":"
        phrase = italic(phrase)
        # first is wikified ?
        phrase += " " if "</" in parts[0] else " see "
        endphrase += concat(parts, ", ")

    if data["dot"]:
        endphrase += data["dot"]
    elif data["nodot"] != "1":
        endphrase += "."
    phrase += italic(endphrase)
    return phrase


def render_ltc_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ltc_l("ltc-l", ["螺貝"], defaultdict(str))
    '螺貝'
    >>> render_ltc_l("ltc-l", ["螺貝", "shell; conch; conch trumpet"], defaultdict(str))
    '螺貝 (“shell; conch; conch trumpet”)'
    """
    text = parts.pop(0)
    if parts:
        text += f" (“{concat(parts, ', ')}”)"
    return text


def render_lw(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lw("lw", ["ja", "ラブライブ!"], defaultdict(str))
    'ラブライブ!'
    >>> render_lw("lw", ["ja", "ラブライブ!", "ラブライブ！"], defaultdict(str))
    'ラブライブ！'
    >>> render_lw("lw", ["ja", "ラブライブ!", "ラブライブ！", "Love Live!"], defaultdict(str, {"pref": "「", "suf": "」"}))
    '「ラブライブ！」 (“Love Live!”)'
    """
    parts.pop(0)  # Remove the lang
    if len(parts) > 1:
        text = parts.pop(1)
        parts.pop(0)  # Remove the useless term
    else:
        text = parts.pop(0)
    if pref := data["pref"]:
        text = f"{pref}{text}"
    if suf := data["suf"]:
        text += suf
    if parts:
        text += f" (“{parts[0]}”)"
    return text


def render_m_self(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_m_self("m-self", ["en", "a", "b"], defaultdict(str))
    '<i>b</i>'
    >>> render_m_self("m-self", ["en", "a", "b"], defaultdict(str, {"tr": "c"}))
    '<i>b</i> (c)'
    >>> render_m_self("m-self", ["en", "a", "b"], defaultdict(str, {"tr": "-"}))
    '<i>b</i>'
    """
    text = italic(parts[-1])
    if (tr := data["tr"]) and tr != "-":
        text += f" ({tr})"
    return text


def render_metathesis(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_metathesis("metathesis", ["en"], defaultdict(str))
    'metathesis'
    >>> render_metathesis("metathesis", ["en"], defaultdict(str, {"cap": "1"}))
    'Metathesis'
    """
    if not data["cap"]:
        data["nocap"] = "1"
    return misc_variant_no_term("metathesis", tpl, parts, data, word=word)


def render_misconstruction(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_misconstruction("misconstruction", ["en", "commodious"], defaultdict(str))
    'Misconstruction of <i>commodious</i>'
    """
    return misc_variant("misconstruction", tpl, parts, data, word=word)


def render_morphology(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_morphology("affix", ["en"], defaultdict(str, {"alt1":"tisa-","pos1":"unique name","alt2":"-gen-", "t2": "transfer of genetic material (transduced)", "alt3":"-lec-", "t3":"selection and enrichment manipulation", "alt4":"-leu-", "t4":"leukocytes", "alt5":"-cel", "t5":"cellular therapy"}))
    '<i>tisa-</i> (unique name)&nbsp;+&nbsp;<i>-gen-</i> (“transfer of genetic material (transduced)”)&nbsp;+&nbsp;<i>-lec-</i> (“selection and enrichment manipulation”)&nbsp;+&nbsp;<i>-leu-</i> (“leukocytes”)&nbsp;+&nbsp;<i>-cel</i> (“cellular therapy”)'
    >>> render_morphology("affix", ["mul", "dys-", "schēma"], defaultdict(str, {"lang1":"NL.","t1":"difficult, impaired, abnormal, bad","lang2":"la", "g2": "f,n", "t2":"shape, form"}))
    'New Latin <i>dys-</i> (“difficult, impaired, abnormal, bad”)&nbsp;+&nbsp;Latin <i>schēma</i> <i>f or n</i> (“shape, form”)'
    >>> render_morphology("aff", ["en", "'gram<t:Instagram>", "-er<id:occupation>"], defaultdict(str))
    "<i>'gram</i> (“Instagram”) and <i>-er</i>"

    >>> render_morphology("blend", ["he", "תַּשְׁבֵּץ", "חֵץ"], defaultdict(str, {"tr1":"tashbéts", "t1":"crossword", "t2":"arrow", "tr2":"chets"}))
    'Blend of <i>תַּשְׁבֵּץ</i> (<i>tashbéts</i>, “crossword”)&nbsp;+&nbsp;<i>חֵץ</i> (<i>chets</i>, “arrow”)'
    >>> render_morphology("blend", ["en"], defaultdict(str))
    'Blend'
    >>> render_morphology("blend", ["en", "scratch", "bill", ""], defaultdict(str, {"notext":"1", "t1":"money", "alt2":"bills"}))
    '<i>scratch</i> (“money”)&nbsp;+&nbsp;<i>bills</i>'
    >>> render_morphology("blend of", ["en", "extrasolar", "solar system"], defaultdict(str))
    'Blend of <i>extrasolar</i>&nbsp;+&nbsp;<i>solar system</i>'
    >>> render_morphology("blend", [], defaultdict(str, {"notext": "1", "1": "en", "2": "yarb", "3": "balls"}))
    '<i>yarb</i>&nbsp;+&nbsp;<i>balls</i>'

    >>> render_morphology("compound", ["fy", "fier", "lj"], defaultdict(str, {"t1":"far", "t2":"leap", "pos1":"adj", "pos2":"v"}))
    '<i>fier</i> (“far”, adj)&nbsp;+&nbsp;<i>lj</i> (“leap”, v)'
    >>> render_morphology("compound", ["en", "en:where", "as"], defaultdict(str, {"gloss2":"that"}))
    'English <i>where</i>&nbsp;+&nbsp;<i>as</i> (“that”)'
    >>> render_morphology("com+", ["en", "where", "as"], defaultdict(str, {"gloss2":"that"}))
    'Compound of <i>where</i>&nbsp;+&nbsp;<i>as</i> (“that”)'

    >>> render_morphology("confix", ["en", "neuro", "genic"], defaultdict(str))
    '<i>neuro-</i>&nbsp;+&nbsp;<i>-genic</i>'
    >>> render_morphology("confix", ["en", "neuro", "gene"], defaultdict(str,{"tr2":"genic"}))
    '<i>neuro-</i>&nbsp;+&nbsp;<i>-gene</i> (<i>-genic</i>)'
    >>> render_morphology("confix", ["en", "be", "dew", "ed"], defaultdict(str))
    '<i>be-</i>&nbsp;+&nbsp;<i>dew</i>&nbsp;+&nbsp;<i>-ed</i>'
    >>> render_morphology("confix", ["en", "i-", "-tard"], defaultdict(str))
    '<i>i-</i>&nbsp;+&nbsp;<i>-tard</i>'

    >>> render_morphology("doublet", ["en" , "fire"], defaultdict(str))
    'Doublet of <i>fire</i>'
    >>> render_morphology("doublet", ["es" , "directo"], defaultdict(str, {"notext":"1"}))
    '<i>directo</i>'
    >>> render_morphology("doublet", ["en" , "advoke", "avouch", "avow"], defaultdict(str))
    'Doublet of <i>advoke</i>, <i>avouch</i> and <i>avow</i>'
    >>> render_morphology("doublet", ["ja", "モスコー"], defaultdict(str, {"tr1":"Mosukō", "nocap":"1"}))
    'doublet of <i>モスコー</i> (<i>Mosukō</i>)'
    >>> render_morphology("doublet", ["ja" , "ヴィエンヌ", "ウィーン"], defaultdict(str, {"tr1":"Viennu", "t1":"Vienne", "tr2":"Wīn"}))
    'Doublet of <i>ヴィエンヌ</i> (<i>Viennu</i>, “Vienne”) and <i>ウィーン</i> (<i>Wīn</i>)'
    >>> render_morphology("dbt", ["ru" , "ру́сский"], defaultdict(str, {"tr1":"rúkij", "t1":"R", "g1":"m", "pos1":"n", "lit1":"R"}))
    'Doublet of <i>ру́сский</i> <i>m</i> (<i>rúkij</i>, “R”, n, literally “R”)'

    >>> render_morphology("infix", ["en", "Mister", "x"], defaultdict(str))
    '<i>Mister</i>&nbsp;+&nbsp;<i>-x-</i>'
    >>> render_morphology("infix", ["en", "Mister", "-x-"], defaultdict(str))
    '<i>Mister</i>&nbsp;+&nbsp;<i>-x-</i>'
    >>> render_morphology("infix", ["tl", "bundok", "in"], defaultdict(str, {"t1": "mountain", "t2": "verb infix"}))
    '<i>bundok</i> (“mountain”)&nbsp;+&nbsp;<i>-in-</i> (“verb infix”)'

    >>> render_morphology("prefix", ["en", "un", "do"], defaultdict(str))
    '<i>un-</i>&nbsp;+&nbsp;<i>do</i>'
    >>> render_morphology("prefix", ["en", "e-", "bus"], defaultdict(str))
    '<i>e-</i>&nbsp;+&nbsp;<i>bus</i>'
    >>> render_morphology("prefix", ["en", "toto", "lala" ], defaultdict(str, {"t1":"t1", "tr1":"tr1", "alt1":"alt1", "pos1":"pos1"}))
    '<i>alt1-</i> (<i>tr1-</i>, “t1”, pos1)&nbsp;+&nbsp;<i>lala</i>'
    >>> render_morphology("prefix", ["en", "toto", "lala"], defaultdict(str, {"t2":"t2", "tr2":"tr2", "alt2":"alt2", "pos2":"pos2"}))
    '<i>toto-</i>&nbsp;+&nbsp;<i>alt2</i> (<i>tr2</i>, “t2”, pos2)'
    >>> render_morphology("pre", ["en", "in", "fare#Etymology_1"], defaultdict(str))
    '<i>in-</i>&nbsp;+&nbsp;<i>fare</i>'

    >>> render_morphology("suffix", ["en", "do", "ing"], defaultdict(str))
    '<i>do</i>&nbsp;+&nbsp;<i>-ing</i>'
    >>> render_morphology("suffix", ["en", "gabapentin", "-oid"], defaultdict(str))
    '<i>gabapentin</i>&nbsp;+&nbsp;<i>-oid</i>'
    >>> render_morphology("suffix", ["en", "toto", "lala"], defaultdict(str, { "t1":"t1", "tr1":"tr1", "alt1":"alt1", "pos1":"pos1"}))
    '<i>alt1</i> (<i>tr1</i>, “t1”, pos1)&nbsp;+&nbsp;<i>-lala</i>'
    >>> render_morphology("suffix", ["en", "toto", "lala"], defaultdict(str, {"t2":"t2", "tr2":"tr2", "alt2":"alt2", "pos2":"pos2"}))
    '<i>toto</i>&nbsp;+&nbsp;<i>-alt2</i> (<i>-tr2</i>, “t2”, pos2)'
    >>> render_morphology("suffix", ["en", "", "cide"], defaultdict(str))
    '&nbsp;+&nbsp;<i>-cide</i>'
    >>> render_morphology("suffix", ["mul", "<i>Mithrax</i>", "ulus"], defaultdict(str))
    '<i>Mithrax</i>&nbsp;+&nbsp;<i>-ulus</i>'

    >>> render_morphology("suffixusex", ["ang", "nama", "naman"], defaultdict(str, {"g1": "m", "t1": "name", "t2": "names"}))
    '<i>nama</i> <i>m</i> (“name”)&nbsp;+&nbsp;<i>-en → naman</i> (“names”)'
    >>> render_morphology("sufex", ["ang", "nama", "naman"], defaultdict(str, {"g1": "m", "t1": "name", "t2": "names"}))
    '<i>nama</i> <i>m</i> (“name”)&nbsp;+&nbsp;<i>-en → naman</i> (“names”)'
    >>> render_morphology("usex-suffix", ["ang", "nama", "naman"], defaultdict(str, {"g1": "m", "t1": "name", "t2": "names"}))
    '<i>nama</i> <i>m</i> (“name”)&nbsp;+&nbsp;<i>-en → naman</i> (“names”)'
    """

    def add_dash(tpl: str, index: int, parts_count: int, chunk: str) -> str:
        if tpl in {"con", "confix"} and index == parts_count:
            chunk = re.sub(r"^-+([^-]*)$", r"\g<1>", chunk)
            chunk = f"-{chunk}"
        elif tpl in {"con", "confix", "pre", "prefix"} and index == 1:
            # Remove trailing dashes
            chunk = re.sub(r"^([^-]*)-+$", r"\g<1>", chunk)
            chunk += "-"
        elif tpl in {"in", "infix"} and index > 1:
            chunk = f"-{chunk.strip('-')}-"
        elif tpl in {"suf", "suffix"} and index == 2:
            chunk = re.sub(r"^-+([^-]*)$", r"\g<1>", chunk)
            chunk = f"-{chunk}"
        elif tpl in {"sufex", "suffixusex", "usex-suffix"} and index == parts_count:
            chunk = f"-en → {chunk}"
        return chunk

    if not parts:
        return f"{italic(data['2'])}&nbsp;+&nbsp;{italic(data['3'])}"

    for idx, part in enumerate(parts):
        if "<" in part and ":" in part:
            part, rest = part.split("<", 1)
            kind, value = rest[:-1].split(":", 1)
            data[f"{kind}{idx}"] = value
            parts[idx] = part

    compound = [
        "af",
        "affix",
        "blend",
        "blend of",
        "com",
        "com+",
        "compound",
        "compound+",
        "con",
        "confix",
        "in",
        "infix",
        "pre",
        "prefix",
        "suf",
        "sufex",
        "suffix",
        "suffixusex",
        "usex-suffix",
    ]

    # Aliases
    tpl = {
        "dbt": "doublet",
        "piecewise_doublet": "piecewise doublet",
        "pw dbt": "piecewise doublet",
        "pwd": "piecewise doublet",
        "pwdbt": "piecewise doublet",
    }.get(tpl, tpl)

    with_start_text = ["blend", "blend of", "doublet", "piecewise doublet"]
    parts.pop(0)  # language code
    phrase = "Compound of " if tpl == "com+" else ""
    if data["notext"] != "1" and tpl in with_start_text:
        starter = tpl
        if parts:
            starter += " " if tpl.endswith(" of") else " of "
        phrase = starter if data["nocap"] else starter.capitalize()
    a_phrase = []

    i = 1
    parsed_parts = []
    while True:
        p_dic = defaultdict(str)
        si = str(i)
        chunk = parts.pop(0) if parts else ""
        chunk = chunk.split("#")[0] if chunk else ""
        chunk = data[f"alt{si}"] or chunk
        p_dic["chunk"] = chunk
        p_dic["g"] = gender_number_specs(gender) if (gender := data[f"g{si}"]) else ""
        p_dic["tr"] = data[f"tr{si}"]
        p_dic["t"] = data[f"t{si}"] or data[f"gloss{si}"]
        p_dic["pos"] = data[f"pos{si}"]
        p_dic["lit"] = data[f"lit{si}"]
        p_dic["lang"] = data[f"lang{si}"]
        if ":" in chunk:
            lang, chunk = chunk.split(":", 1)
            p_dic["chunk"] = chunk
            p_dic["lang"] = lang
        if not chunk and not p_dic["tr"] and not p_dic["ts"] and not parts:
            break
        else:
            parsed_parts.append(p_dic)
        i += 1

    parts_count = len(parsed_parts)
    i = 1
    while parsed_parts:
        c = parsed_parts.pop(0)
        chunk = c["chunk"]
        chunk = add_dash(tpl, i, parts_count, chunk)
        if chunk:
            chunk = italic(chunk)
        if lang := c["lang"]:
            chunk = f"{langs.get(lang, lang)} {chunk}"
        if c["g"]:
            chunk += " " + c["g"]
        local_phrase = []
        if c["tr"]:
            result = c["tr"]
            result = add_dash(tpl, i, parts_count, result)
            local_phrase.append(italic(result))
        if c["t"]:
            local_phrase.append(f"{'“' + c['t'] + '”'}")
        if c["pos"]:
            local_phrase.append(c["pos"])
        if c["lit"]:
            local_phrase.append(f"{'literally “' + c['lit'] + '”'}")
        if local_phrase:
            chunk += " (" + concat(local_phrase, ", ") + ")"
        a_phrase.append(chunk)
        i += 1

    sep = ", "
    last_sep = " and "
    if tpl in compound:
        sep = "&nbsp;+&nbsp;"
        last_sep = sep

    phrase += concat(a_phrase, sep, last_sep=last_sep)

    # special case : {{suffix|en||cide}}
    if tpl in {"suf", "suffix"} and "&nbsp;+&nbsp;" not in phrase:
        phrase = f"&nbsp;+&nbsp;{phrase}"

    return phrase


def _render_morse_code(part: str, data: defaultdict[str, str], suffix: str) -> str:
    text = f"{italic(f'Visual rendering of Morse code {suffix}')} {strong(part)}"
    if gloss := data["gloss"]:
        text += f" (“{gloss}”)"
    return f"{text}."


def render_morse_code_abbreviation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_morse_code_abbreviation("morse code abbreviation", ["AGN"], defaultdict(str))
    '<i>Visual rendering of Morse code abbreviation</i> <b>AGN</b>.'
    """
    return _render_morse_code(parts[0], data, "abbreviation")


def render_morse_code_for(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_morse_code_for("morse code for", ["M"], defaultdict(str))
    '<i>Visual rendering of Morse code for</i> <b>M</b>.'
    >>> render_morse_code_for("morse code for", ["="], defaultdict(str, {"gloss": "equal sign"}))
    '<i>Visual rendering of Morse code for</i> <b>=</b> (“equal sign”).'
    """
    return _render_morse_code(parts[0], data, "for")


def render_morse_code_prosign(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_morse_code_prosign("morse code prosign", ["SOS"], defaultdict(str))
    '<i>Visual rendering of Morse code prosign</i> <b>SOS</b>.'
    """
    return _render_morse_code(parts[0], data, "prosign")


def render_mul_cjk_stroke_def(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_mul_cjk_stroke_def("mul-cjk stroke-def", ["p"], defaultdict(str))
    '(<i>Chinese calligraphy</i>) The stroke {{m|mul|撇||left-falling}}.'
    >>> render_mul_cjk_stroke_def("mul-cjk stroke-def", ["h", "z", "t"], defaultdict(str))
    '(<i>Chinese calligraphy</i>) The stroke combination {{m|mul|橫||horizontal}} + {{m|mul|折||bent}} + {{m|mul|提||rising}}.'
    """
    # Source: https://en.wiktionary.org/w/index.php?title=Template:mul-cjk_stroke-def/char_def&oldid=40839292
    strokes = {
        "b": "{{m|mul|扁||flat}}",
        "d": "{{m|mul|點||dot}}",
        "g": "{{m|mul|鉤||hook}}",
        "h": "{{m|mul|橫||horizontal}}",
        "n": "{{m|mul|捺||right-falling}}",
        "p": "{{m|mul|撇||left-falling}}",
        "q": "{{m|mul|圈||circle}}",
        "s": "{{m|mul|豎||vertical}}",
        "t": "{{m|mul|提||rising}}",
        "w": "{{m|mul|彎||curved}}",
        "x": "{{m|mul|斜||slant}}",
        "z": "{{m|mul|折||bent}}",
    }

    text = "(<i>Chinese calligraphy</i>) The stroke "
    if len(parts) > 1:
        text += "combination "
    text += concat([strokes[part] for part in parts], " + ")
    return f"{text}."


def render_mul_domino_def(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_mul_domino_def("mul-domino def", [""], defaultdict(str), word="🀲")
    '<i>A domino tile, the 0-1</i>.'
    """
    # Source: https://en.wiktionary.org/w/index.php?title=Module:mul-domino_def&oldid=78846534
    name = unicodedata.name(word)  # Example: "DOMINO TILE HORIZONTAL-00-01"
    _, domino1, domino2 = name.split("-")
    return f"<i>A domino tile, the {int(domino1)}-{int(domino2)}</i>."


def render_mul_kanadef(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_mul_kanadef("mul-domino def", ["ク", "small", "Kana"], defaultdict(str))
    'The katakana syllable ク in small form for the Ainu language (アイヌ イタㇰ).'
    >>> render_mul_kanadef("mul-domino def", ["ク", "smallhalfwidth", "Kana"], defaultdict(str))
    'The katakana syllable ク in small form (Kana) and halfwidth form.'
    >>> render_mul_kanadef("mul-domino def", ["ク", "", "Kana"], defaultdict(str))
    'The katakana syllable at ク行段 (row , section ) in a gojūon table.'
    """
    # Source: https://en.wiktionary.org/w/index.php?title=Template:mul-kanadef&oldid=60135395
    row = parts[0]
    match modifier := parts[1]:
        case "゛":
            text = f"The katakana syllable {row} with a dakuten."
        case "゜":
            text = f"The katakana syllable {row} with a handakuten."
        case "small":
            text = f"The katakana syllable {row} in small form for the Ainu language (アイヌ イタㇰ)."
        case "halfwidth":
            text = f"The katakana syllable {row} in halfwidth form."
        case "smallhalfwidth":
            text = f"The katakana syllable {row} in small form ({parts[2]}) and halfwidth form."
        case "braille":
            text = f"The katakana syllable {row} in Braille."
        case "ン":
            text = "The katakana syllable without particular 行 (row) or 段 (section) in a gojūon table, positioned at a corner."
        case _:
            row_map = {
                "ア": "A",
                "カ": "KA",
                "サ": "SA",
                "タ": "TA",
                "ナ": "NA",
                "ハ": "HA",
                "マ": "MA",
                "ヤ": "YA",
                "ラ": "RA",
                "ワ": "WA",
            }
            section_map = {"ア": "A", "イ": "I", "ウ": "U", "エ": "E", "オ": "O"}
            row_ = row_map.get(row, "")
            section = section_map.get(modifier, "")
            text = f"The katakana syllable at {row}行{modifier}段 (row {row_}, section {section}) in a gojūon table."

    return text


def render_name_translit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_name_translit("name translit", ["en", "ka", "შევარდნაძე"], defaultdict(str, {"type":"surname"}))
    '<i>a transliteration of the Georgian surname</i> <b>შევარდნაძე</b>'
    >>> render_name_translit("name translit", ["en", "fa", "فرید<tr:farid>"], defaultdict(str, {"type":"male given name"}))
    '<i>a transliteration of the Persian male given name</i> <b>فرید</b> (<i>farid</i>)'
    >>> render_name_translit("name translit", ["en", "ru", "Ива́нович<t:son of Ivan>"], defaultdict(str, {"type":"patronymic"}))
    '<i>a transliteration of the Russian patronymic</i> <b>Ива́нович</b> (<i>Ivánovič</i>, “<i>son of Ivan</i>”)'
    >>> render_name_translit("name translit", ["pt", "bg", "Ива́нов", "Ивано́в"], defaultdict(str, {"type":"surname"}))
    '<i>a transliteration of the Bulgarian surname</i> <b>Ива́нов</b> <i>or</i> <b>Ивано́в</b>'
    >>> render_name_translit("name translit", ["en", "el", "Γιάννης<eq:John>"], defaultdict(str, {"type":"male given name"}))
    '<i>a transliteration of the Greek male given name</i> <b>Γιάννης</b>, <i>equivalent to John</i>'
    >>> render_name_translit("name translit", ["fr", "ja"], defaultdict(str, {"type":"female given name"}))
    '<i>a transliteration of a Japanese female given name</i>'
    >>> render_name_translit("name translit", ["en", "bg,mk,sh", "Никола"], defaultdict(str, {"type":"male given name", "eq": "Nicholas"}))
    '<i>a transliteration of the Bulgarian, Macedonian or Serbo-Croatian male given name</i> <b>Никола</b>, <i>equivalent to Nicholas</i>'
    >>> render_name_translit("name translit", ["en", "bg, mk,  sh ", "Никола"], defaultdict(str, {"type":"male given name", "eq": "Nicholas"}))
    '<i>a transliteration of the Bulgarian, Macedonian or Serbo-Croatian male given name</i> <b>Никола</b>, <i>equivalent to Nicholas</i>'
    >>> render_name_translit("name translit", ["en", "grc", "Ἀέτιος"], defaultdict(str, {"type":"male given name", "xlit": "Aetius"}))
    '<i>a transliteration of the Ancient Greek male given name</i> <b>Ἀέτιος</b>, <i><b>Aetius</b></i>'
    """
    parts.pop(0)  # Destination language
    src_langs = parts.pop(0)

    origins = concat([langs[src_lang.strip()] for src_lang in src_langs.split(",")], sep=", ", last_sep=" or ")
    text = italic(f"a transliteration of {'the' if parts else 'a'} {origins} {data['type']}")
    if not parts:
        return text

    what, rest = parts.pop(0), ""
    if "<" in what:
        what, rest = what.split("<", 1)

    transliterated = transliterate(src_langs.split(",", 1)[0], what)
    text += f" {strong(what)}"

    if rest:
        if transliterated:
            transliterated = f"{italic(transliterated)}, "

        kind, value = rest.split(":", 1)
        value = value.rstrip(">")
        match kind:
            case "eq":
                text += f", {italic(f'equivalent to {value}')}"
            case "t":
                text += f" ({transliterated}“{italic(value)}”)"
            case "tr":
                text += f" ({italic(value)})"
            case _:
                assert 0, f"Unhandled {kind=} in render_name_translit()"
    elif transliterated:
        text += f" ({italic(transliterated)})"

    if eq := data["eq"]:
        text += f", {italic(f'equivalent to {eq}')}"

    if parts:
        text += f" {italic('or')} {strong(parts[0])}"
        if transliterated:
            text += f" ({italic(transliterated)})"

    if xlit := data["xlit"]:
        text += f", {italic(strong(xlit))}"

    return text


def render_named_after(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_named_after("named-after", ["en", "Pierre Bézier"], defaultdict(str, {"nationality":"French", "occupation":"Renault engineer", "nocap":"1"}))
    'named after French Renault engineer Pierre Bézier'
    >>> render_named_after("named-after", ["en", "Bertrand Russell"], defaultdict(str, {"tr":"tr", "died":"1970", "born":"1872", "nat":"English", "occ":"mathematician", "occ2":"logician"}))
    'Named after English mathematician and logician Bertrand Russell (<i>tr</i>) (1872–1970)'
    >>> render_named_after("named-after", ["en", "Patrick Swayze"], defaultdict(str, {"alt":""}))
    'Patrick Swayze'
    >>> render_named_after("named-after", ["en"], defaultdict(str))
    'Named after an unknown person'
    """
    parts.pop(0)  # Remove the language
    p = parts.pop(0) if parts else ""
    p = p or "an unknown person"
    if "alt" in data:
        phrase = data["alt"]
    else:
        starter = "named after"
        phrase = starter if data["nocap"] else starter.capitalize()
        if data["nationality"]:
            phrase += f" {data['nationality']}"
        elif data["nat"]:
            phrase += f" {data['nat']}"
        if occ := join_names(data, "occ", " and ", include_langname=False, key_alias="occupation"):
            phrase += f" {occ}"
        phrase += " "
    phrase += f"{p}"
    if data["tr"]:
        phrase += f" ({italic(data['tr'])})"
    if data["died"] or data["born"]:
        phrase += f" ({data['born'] or '?'}–{data['died']})"
    return phrase


def render_nb(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_nb("...", [], defaultdict(str))
    ' […] '
    >>> render_nb("...", [], defaultdict(str, {"text":"etc."}))
    ' [etc.] '
    >>> render_nb("...", ["a"], defaultdict(str))
    ' [and the other form <i>a</i>] '
    >>> render_nb("...", ["a, b, c"], defaultdict(str))
    ' [and other forms <i>a, b, c</i>] '
    >>> render_nb("nb...", [], defaultdict(str))
    '&nbsp;[…]'
    >>> render_nb("nb...", [], defaultdict(str, {"text":"etc."}))
    '&nbsp;[etc.]'
    >>> render_nb("nb...", ["a"], defaultdict(str))
    '&nbsp;[and the other form <i>a</i>]'
    >>> render_nb("nb...", ["a, b, c"], defaultdict(str))
    '&nbsp;[and other forms <i>a, b, c</i>]'
    """
    sep = " " if tpl == "..." else "&nbsp;"
    phrase = f"{sep}["
    if not parts:
        phrase += data["text"] or "…"
    else:
        phrase += "and other forms " if "," in parts[0] else "and the other form "
        phrase += italic(parts[0])
    return f"{phrase}]{sep if tpl == '...' else ''}"


def render_nuclide(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_nuclide("nuclide", ["2", "1", "H"], defaultdict(str))
    '<sup>2</sup><sub style="margin-left:-1ex;">1</sub>H'
    >>> render_nuclide("nuclide", ["222", "86", "Rn"], defaultdict(str))
    '<sup>222</sup><sub style="margin-left:-2.3ex;">86</sub>Rn'
    >>> render_nuclide("nuclide", ["270", "108", "Hs"], defaultdict(str))
    '<sup>270</sup><sub style="margin-left:-3.5ex;">108</sub>Hs'
    """
    phrase = superscript(parts[0])
    sub_n = int(parts[1])
    if sub_n < 10:
        phrase += f'<sub style="margin-left:-1ex;">{sub_n}</sub>'
    elif sub_n < 100:
        phrase += f'<sub style="margin-left:-2.3ex;">{sub_n}</sub>'
    else:
        phrase += f'<sub style="margin-left:-3.5ex;">{sub_n}</sub>'
    phrase += parts[2]
    return phrase


def render_och_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_och_l("och-l", ["覺"], defaultdict(str))
    '覺 (OC)'
    >>> render_och_l("och-l", ["覺", "to awake, get insight"], defaultdict(str))
    '覺 (OC, “to awake, get insight”)'
    """
    # TODO: should be improved with transliteration
    text = f"{parts.pop(0)} (OC"
    if parts:
        text += f", “{parts[0]}”"
    return f"{text})"


def render_only_used_in(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_only_used_in("only used in", ["en", "Alexandrian limp"], defaultdict(str))
    '<i>Only used in</i> <b>Alexandrian limp</b>'
    >>> render_only_used_in("only used in", ["en", "Alexandrian limp"], defaultdict(str, {"t": "foo"}))
    '<i>Only used in</i> <b>Alexandrian limp</b> (“foo”)'
    """
    text = f"<i>Only used in</i> <b>{parts[-1]}</b>"
    if t := data["t"]:
        text += f" (“{t}”)"
    return text


def render_onomatopoeic(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_onomatopoeic("onom", ["en"], defaultdict(str))
    'Onomatopoeic'
    >>> render_onomatopoeic("onom", ["en"], defaultdict(str, {"nocap": "1"}))
    'onomatopoeic'
    >>> render_onomatopoeic("onom", ["en"], defaultdict(str, {"title": "imitative"}))
    'imitative'
    >>> render_onomatopoeic("onom", ["en"], defaultdict(str, {"notext": "1"}))
    ''
    """
    return misc_variant_no_term("onomatopoeic", tpl, parts, data, word=word)


def render_pedlink(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_pedlink("pedlink", ["foo"], defaultdict(str))
    'foo'
    >>> render_pedlink("pedlink", ["foo"], defaultdict(str, {"disp": "bar"}))
    'bar'
    """
    return data["disp"] or parts[0]


def render_pedia(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_pedia("pedia", [], defaultdict(str), word="Ismene")
    'Ismene on Wikipedia.'
    >>> render_pedia("pedia", ["foo#bar", "baz"], defaultdict(str))
    'baz on Wikipedia.'
    >>> render_pedia("pedlink", ["foo#bar"], defaultdict(str, {"nodot": "1", "i": "1"}))
    '<i>foo</i> on Wikipedia'
    """
    text = parts[-1].split("#", 1)[0] if parts else word
    if data["i"]:
        text = italic(text)
    text += " on Wikipedia"
    if not data["nodot"]:
        text += "."
    return text


def render_person(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_person("person", ["en"], defaultdict(str))
    ''
    >>> render_person("person", ["Q151874"], defaultdict(str))
    'Russian ballet dancer Anna Pavlova'
    >>> render_person("person", ["Q151874"], defaultdict(str, {"brackets": "1"}))
    'Anna Pavlova (Russian ballet dancer)'
    """
    if not (person_id := parts[0]).startswith("Q"):
        return ""
    return wikidata.person(person_id, brackets=bool(data["brackets"]))


def render_phonetic_alphabet(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_phonetic_alphabet("phonetic-alphabet", ["A"], defaultdict(str, {"NATO/ICAO": "1", "ITU/IMO": "1"}))
    '{{lb|mul|international standards}} <i>NATO, ICAO, ITU & IMO radiotelephony clear code (spelling-alphabet name) for the letter</i> <b>A</b>.'
    """
    standards: list[str] = []
    if data["NATO/ICAO"]:
        standards.extend(("NATO", "ICAO"))
    if data["ITU/IMO"]:
        standards.extend(("ITU", "IMO"))
    standards_str = concat(standards, ", ", last_sep=" & ")

    label = "{{lb|mul|international standards}}"
    ng = f"{standards_str} radiotelephony clear code (spelling-alphabet name)"

    if data["word"]:
        for_what = ""
    elif data["num"]:
        for_what = "the digit"
    else:
        for_what = "the letter"

    return f"{label} <i>{ng} for {for_what}</i> <b>{parts[0]}</b>."


def render_place(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_place("place", ["en", "A country in the Middle East"], defaultdict(str))
    'A country in the Middle East'
    >>> render_place("place", ["en", "A country"], defaultdict(str, {"modern":"Iraq"}))
    'A country; modern Iraq'
    >>> render_place("place", ["en", "island", "regency/Pandeglang", "province/Banten", "c/Indonesia"], defaultdict(str))
    'An island of Pandeglang, Banten, Indonesia'
    >>> render_place("place", ["en", "village", "co/Fulton County", "s/Illinois"], defaultdict(str))
    'A village in Fulton County, Illinois'
    >>> render_place("place", ["en", "village", "co/Fulton County", "s/Illinois"], defaultdict(str, {"a": "a"}))
    'a village in Fulton County, Illinois'
    >>> render_place("place", ["en", "city/county seat", "co/Lamar County", "s/Texas"], defaultdict(str))
    'A city, the county seat of Lamar County, Texas'
    >>> render_place("place", ["en", "small town/and/unincorporated community"], defaultdict(str))
    'A small town and unincorporated community'
    >>> render_place("place", ["en", "town", "s/New York", ";", "named after Paris"], defaultdict(str))
    'A town in New York; named after Paris'
    >>> render_place("place", ["en", "s"], defaultdict(str))
    'A state'
    >>> render_place("place", ["en", "state", "overseas territory/United States Virgin Islands"], defaultdict(str))
    'A state of the United States Virgin Islands'
    >>> render_place("place", ["en", "state", "administrative region/Réunion"], defaultdict(str))
    'A state of the Réunion region'
    >>> render_place("place", ["en", "state", "c/USA"], defaultdict(str))
    'A state of the United States'
    >>> render_place("place", ["en", "city", "c/Republic of Ireland"], defaultdict(str))
    'A city in Republic of Ireland'
    >>> render_place("place", ["en", "city", "s/Georgia", "c/United States"], defaultdict(str))
    'A city in Georgia, United States'
    >>> render_place("place", ["en", "river", "in", "England", ", forming the boundary between", "co/Derbyshire", "and", "co/Staffordshire"], defaultdict(str))
    'A river in England, forming the boundary between Derbyshire and Staffordshire'
    >>> render_place("place", ["en", "barangay", "mun/Hilongos", "p/Leyte", "c/Philippines"], defaultdict(str))
    'A barangay of Hilongos, Leyte, Philippines'
    >>> render_place("place", ["en", "hamlet", "par/South Leigh and High Cogges", "dist/West Oxfordshire", "co/Oxfordshire", "cc/England"], defaultdict(str))
    'A hamlet in South Leigh and High Cogges parish, West Oxfordshire district, Oxfordshire, England'
    >>> render_place("place", ["en", "village/and/cpar", "in", "uauth/Central Bedfordshire", "co/Bedfordshire", "cc/England"], defaultdict(str))
    'A village and civil parish in  Central Bedfordshire district, Bedfordshire, England'
    >>> render_place("place", ["en", "prefecture", "c/Japan"], defaultdict(str, {"capital": "Mito"}))
    'A prefecture of Japan. Capital: Mito'
    >>> render_place("place", ["en", "suburban area", "in", "par/New Milton", "dist/New Forest", "co/Hampshire", "cc/England", "formerly a village named", "x/Milton"], defaultdict(str))
    'A suburban area in  New Milton parish, New Forest district, Hampshire, England, formerly a village named Milton'
    >>> render_place("place", ["en", "The capital city of <<s/South Carolina>>, and the county seat of <<co/Richland County>>"], defaultdict(str))
    'The capital city of South Carolina, and the county seat of Richland County'
    """
    parts.pop(0)  # Remove the language
    parts = [re.sub(r"<<(?:[^/>]+)/([^>]+)>>", r"\1", part) for part in parts]
    phrase = ""
    i = 1
    previous_rawpart = False
    last = next((part for part in parts[::-1] if "/" not in part), "")
    while parts:
        si = str(i)
        part = parts.pop(0)
        subparts = part.split("/")
        if part in ("in", "and"):
            phrase += f" {part}"
            phrase += " " if part == "in" else ""
            previous_rawpart = True
        elif i == 1:
            no_article = False
            for j, subpart in enumerate(subparts):
                if subpart == "and":
                    phrase = f"{phrase[:-2]} and"
                    no_article = True
                    continue
                subpart = placetypes_aliases.get(subpart, subpart)
                s = recognized_placetypes.get(subpart, {})
                qualifier = ""
                if not s:
                    q_array = subpart.split(" ")
                    qualifier = q_array[0]
                    if qualifier in recognized_qualifiers:
                        qualifier = recognized_qualifiers[qualifier]
                        subpart = " ".join(q_array[1:])
                    else:
                        qualifier = ""
                    subpart = placetypes_aliases.get(subpart, subpart)
                    s = recognized_placetypes.get(subpart, {})
                if s:
                    if not (preposition := s.get("preposition")):
                        s_fallback = recognized_placetypes.get(s["fallback"], {})
                        preposition = s_fallback.get("preposition")
                    if j == 0:
                        article = data["a"] or s["article"].title()
                    else:
                        article = "" if no_article else s["article"]
                    phrase += article
                    phrase += f" {qualifier}" if qualifier else ""
                    phrase += " " + s["display"]
                    no_article = False
                    if j == len(subparts) - 1:
                        phrase += f" {preposition or 'in'} " if parts and parts[0] != "in" else ""
                    else:
                        phrase += ", "
                else:
                    phrase += part
        elif len(subparts) > 1:
            phrase += ", " if i > 2 and not previous_rawpart else ""
            phrase += " " if previous_rawpart else ""
            kind, *places = subparts
            place = "/".join(places)
            kind = placetypes_aliases.get(kind, kind)
            placename_key = f"{kind}/{place}"
            is_administrative = "administrative" in kind
            if is_administrative:
                phrase += "the "
            if recognized_placename := recognized_placenames.get(placename_key):
                if i < 3 and (article := recognized_placename["article"]):
                    phrase += f"{article} "
                phrase += recognized_placename["display"]
            else:
                phrase += place
            if is_administrative:
                phrase += f" {kind.split(' ')[-1]}"
            elif kind in {"department", "district", "parish"}:
                phrase += f" {kind}"
            elif kind == "unitary authority":
                phrase += " district"
        elif part == ";":
            phrase += "; "
        else:
            if part == last and not phrase.endswith(("; ", ", ")):
                phrase += ", "
            phrase += part

        modern_key = "modern" + "" if i == 1 else si
        if data[modern_key]:
            phrase += f"; modern {data[modern_key]}"
        previous_rawpart = len(subparts) == 1 and i > 1
        i += 1

    if capital := data["capital"]:
        phrase += f". Capital: {capital}"

    return phrase


def render_pseudo_acronym_of(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_pseudo_acronym_of("pseudo-acronym of", ["en", "St Cross"], defaultdict(str, {"addl": "i.e. St Cross College, Oxford"}))
    'Pseudo-acronym of <i>St Cross</i>, <i>i.e. St Cross College, Oxford</i>'
    """
    text = misc_variant("pseudo-acronym", tpl, parts, data, word=word)
    if addl := data["addl"]:
        text += f", {italic(addl)}"
    return text


def render_pseudo_loan(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_pseudo_loan("pseudo-loan", ["fr", "en"], defaultdict(str))
    'Pseudo-anglicism'
    >>> render_pseudo_loan("pseudo-loan", ["en", "fr"], defaultdict(str))
    'Pseudo-Gallicism'
    >>> render_pseudo_loan("pseudo-loan", ["en", "da"], defaultdict(str))
    'Pseudo-loan from Danish'

    >>> render_pseudo_loan("pseudo-loan", ["de", "en", "la:ego", "shooter"], defaultdict(str, {"t1": "I"}))
    'Pseudo-anglicism, derived from Latin <i>ego</i> (“I”) +&nbsp;<i>shooter</i>'
    >>> render_pseudo_loan("pseudo-loan", ["de", "en", "la:ego", "shooter"], defaultdict(str, {"t1": "I", "notext": "1"}))
    'Latin <i>ego</i> (“I”) +&nbsp;<i>shooter</i>'
    >>> render_pseudo_loan("pseudo-loan", ["ja", "en", "office", "lady"], defaultdict(str))
    'Wasei eigo (和製英語; pseudo-anglicism), derived from <i>office</i> +&nbsp;<i>lady</i>'
    >>> render_pseudo_loan("pseudo-loan", ["en", "enm", "<i>the</i> +&nbsp;<i>old</i>"], defaultdict(str))
    'Pseudo-loan from Middle English, derived from <i>the</i> +&nbsp;<i>old</i>'
    """
    pseudo_loan_by_source = {
        "ar": "Arabism",
        "de": "Germanism",
        "en": "anglicism",
        "es": "Hispanism",
        "fr": "Gallicism",
        "it": "Italianism",
        "ja": "Japonism",
        "la": "Latinism",
    }

    text = ""
    lang_code = parts.pop(0)
    lang_src = parts.pop(0)
    nocap = "nocap" in data

    if not data["notext"]:
        if lang_code == "ja" and lang_src == "en":
            text += f"{'w' if nocap else 'W'}asei eigo (和製英語; pseudo-anglicism)"
        elif plbs := pseudo_loan_by_source.get(lang_src, ""):
            text += f"{'p' if nocap else 'P'}seudo-{plbs}"
        else:
            text += f"{'p' if nocap else 'P'}seudo-loan from {langs[lang_src]}"
        if parts:
            text += f"{'' if nocap else ','} derived from "

    if parts:
        derivations: list[str] = []
        for idx, part in enumerate(parts, 1):
            if ":" in part:
                lang, value = part.split(":", 1)
                lang = langs[lang]
                part = f"{lang} <i>{value}</i>"
            else:
                part = italic(part)
            if t := data[f"t{idx}"]:
                part += f" (“{t}”)"
            derivations.append(part)
        text += concat(derivations, " +&nbsp;")

    return text


def render_rebracketing(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_rebracketing("rebracketing", ["en", "marathon"], defaultdict(str))
    'Rebracketing of <i>marathon</i>'
    """
    return misc_variant("rebracketing", tpl, parts, data, word=word)


def render_reduplication(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_reduplication("reduplication", ["mul", "Boops#Etymology1"], defaultdict(str))
    'Reduplication of <i>Boops</i>'
    """
    return misc_variant("reduplication", tpl, parts, data, word=word)


def render_rq(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_rq("RQ", ["King James Version"], defaultdict(str, {"book": "Mark", "chapter": "7", "verse": "33", "text": "And he took him aside from the multitude, and put his fingers into his ears, and he spit, and touched his tongue;"}))
    '“And he took him aside from the multitude, and put his fingers into his ears, and he spit, and touched his tongue;”'
    """
    return f"“{data['text']}”"


def render_script(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_script("script", ["Cpmn"], defaultdict(str))
    'Cypro-Minoan'
    """
    return scripts[parts[0]]


def render_semantic_shift(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_semantic_shift("ss", ["en"], defaultdict(str))
    'semantic shift'
    >>> render_semantic_shift("ss", ["en"], defaultdict(str, {"type": "a"}))
    'ameliorative semantic shift'
    >>> render_semantic_shift("ss", ["en"], defaultdict(str, {"type": "b"}))
    'semantic broadening'
    >>> render_semantic_shift("ss", ["en"], defaultdict(str, {"type": "n"}))
    'semantic narrowing'
    >>> render_semantic_shift("ss", ["en"], defaultdict(str, {"type": "p"}))
    'pejorative semantic shift'
    """
    return {
        "": "semantic shift",
        "a": "ameliorative semantic shift",
        "b": "semantic broadening",
        "n": "semantic narrowing",
        "p": "pejorative semantic shift",
    }[data["type"]]


def render_sic(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sic("SIC", [], defaultdict(str))
    '<sup>[<i>sic</i>]</sup>'
    >>> render_sic("SIC", ["misspelled"], defaultdict(str))
    '<sup>[<i>sic</i> - meaning <i>misspelled</i>]</sup>'
    """
    text = "<sup>[<i>sic</i>"
    if parts:
        text += f" - meaning <i>{parts[0]}</i>"
    return f"{text}]</sup>"


def render_si_unit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_si_unit("SI-unit", ["en", "peta", "second", "time"], defaultdict(str))
    '(<i>metrology</i>) An SI unit of time equal to 10<sup>15</sup> seconds. Symbol: Ps'
    >>> render_si_unit("SI-unit-np", ["en", "nano", "gauss", "magnetism"], defaultdict(str))
    '(<i>metrology</i>) An SI unit of magnetism equal to 10<sup>−9</sup> gauss.'
    >>> render_si_unit("SI-unit", ["en", "peta", "second"], defaultdict(str))
    '(<i>metrology</i>) An SI unit of time equal to 10<sup>15</sup> seconds. Symbol: Ps'
    """
    parts.pop(0)  # language
    prefix = data["2"] or (parts.pop(0) if parts else "")
    unit = data["3"] or (parts.pop(0) if parts else "")
    category = data["4"] or (parts.pop(0) if parts else "") or si_unit.unit_to_type.get(unit, "")
    exp = si_unit.prefix_to_exp.get(prefix, "")
    s_end = "" if unit.endswith("z") or unit.endswith("s") else "s"
    phrase = f"({italic('metrology')}) An SI unit of {category} equal to 10{superscript(exp)} {unit}{s_end}."
    if unit in si_unit.unit_to_symbol:
        symbol = f"{si_unit.prefix_to_symbol.get(prefix, '')}{si_unit.unit_to_symbol.get(unit, '')}"
        phrase += f" Symbol: {symbol}"
    return phrase


def render_si_unit_2(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_si_unit_2("SI-unit-2", ["peta", "meter", "length", "metre"], defaultdict(str))
    '(<i>metrology</i>) An SI unit of length equal to 10<sup>15</sup> meters; alternative spelling of <i>petametre</i>.'
    """
    prefix = data["1"] or (parts.pop(0) if parts else "")
    unit = data["2"] or (parts.pop(0) if parts else "")
    category = data["3"] or (parts.pop(0) if parts else "")
    alt = data["3"] or (parts.pop(0) if parts else "")
    exp = si_unit.prefix_to_exp.get(prefix, "")
    return f"({italic('metrology')}) An SI unit of {category} equal to 10{superscript(exp)} {unit}s; alternative spelling of {italic(prefix + alt)}."


def render_si_unit_abb(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_si_unit_abb("SI-unit-abb", ["femto", "mole", "amount of substance"], defaultdict(str))
    '(<i>metrology</i>) <i>Symbol for</i> <b>femtomole</b>, an SI unit of amount of substance equal to 10<sup>−15</sup> moles'
    >>> render_si_unit_abb("SI-unit-abbnp", ["exa", "hertz", "frequency"], defaultdict(str))
    '(<i>metrology</i>) <i>Symbol for</i> <b>exahertz</b>, an SI unit of frequency equal to 10<sup>18</sup> hertz'
    """
    prefix = data["1"] or (parts.pop(0) if parts else "")
    unit = data["2"] or (parts.pop(0) if parts else "")
    category = data["3"] or (parts.pop(0) if parts else "")
    exp = si_unit.prefix_to_exp.get(prefix, "")
    plural = "" if tpl.endswith("np") else "s"
    return f"({italic('metrology')}) {italic('Symbol for')} {strong(prefix + unit)}, an SI unit of {category} equal to 10{superscript(exp)} {unit}{plural}"


def render_si_unit_abb2(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_si_unit_abb2("SI-unit-abb2", ["exa", "liter", "litre", "fluid measure"], defaultdict(str))
    '(<i>metrology</i>) <i>Symbol for</i> <b>exaliter</b> (<i>exalitre</i>), an SI unit of fluid measure equal to 10<sup>18</sup> liters (<i>litres</i>).'
    """
    prefix = data["1"] or (parts.pop(0) if parts else "")
    unit = data["2"] or (parts.pop(0) if parts else "")
    kind = data["3"] or (parts.pop(0) if parts else "")
    category = data["4"] or (parts.pop(0) if parts else "")
    match prefix:
        case "quecto":
            exp = "&minus;30"
        case "ronto":
            exp = "&minus;27"
        case "yocto":
            exp = "&minus;24"
        case "zepto":
            exp = "&minus;21"
        case "atto":
            exp = "&minus;18"
        case "femto":
            exp = "&minus;15"
        case "pico":
            exp = "&minus;12"
        case "nano":
            exp = "&minus;9"
        case "micro":
            exp = "&minus;6"
        case "milli":
            exp = "&minus;3"
        case "centi":
            exp = "&minus;2"
        case "deci":
            exp = "&minus;1"
        case "deca":
            exp = "1"
        case "hecto":
            exp = "2"
        case "kilo":
            exp = "3"
        case "mega":
            exp = "6"
        case "giga":
            exp = "9"
        case "tera":
            exp = "12"
        case "peta":
            exp = "15"
        case "exa":
            exp = "18"
        case "zetta":
            exp = "21"
        case "yotta":
            exp = "24"
        case "ronna":
            exp = "27"
        case "quetta":
            exp = "30"
        case _:
            exp = "?"
    return f"({italic('metrology')}) {italic('Symbol for')} {strong(prefix + unit)} ({italic(prefix + kind)}), an SI unit of {category} equal to 10{superscript(exp)} {unit}s (<i>{kind}s</i>)."


def render_sound_symbolic(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sound_symbolic("sound-symbolic", ["en"], defaultdict(str, {"title": "expressive"}))
    'expressive'
    """
    return misc_variant_no_term("", tpl, parts, data, word=word)


def render_spelling_pronunciation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_spelling_pronunciation("spelling pronunciation", ["en"], defaultdict(str))
    'Spelling pronunciation'
    >>> render_spelling_pronunciation("spelling pronunciation", ["en"], defaultdict(str, {"title": "Title"}))
    'Title'
    >>> render_spelling_pronunciation("spelling pronunciation", ["en"], defaultdict(str, {"nocap": "1"}))
    'spelling pronunciation'
    """
    if data["notext"]:
        return ""
    text = data["title"] or tpl
    return text if data["nocap"] else capitalize(text)


def render_spoonerism(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_spoonerism("spoonerism", ["en", "Walmart"], defaultdict(str))
    'Spoonerism of <i>Walmart</i>'
    """
    return misc_variant("spoonerism", tpl, parts, data, word=word)


def render_sumti(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sumti("sumti", ["3"], defaultdict(str, {"int": "3"}))
    'x<sub>3</sub>'
    """
    return f"x<sub>{parts[0]}</sub>"


def render_surface_analysis(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_surface_analysis("surf", [], defaultdict(str))
    'By surface analysis'
    >>> render_surface_analysis("surf", ["en", "ignore", "-ance"], defaultdict(str))
    'By surface analysis, <i>ignore</i>&nbsp;+&nbsp;<i>-ance</i>'
    >>> render_surface_analysis("surf", ["+suf", "en", "ignore", "ance"], defaultdict(str))
    'By surface analysis, <i>ignore</i>&nbsp;+&nbsp;<i>-ance</i>'
    """
    phrase = ("b" if data["nocap"] else "B") + "y surface analysis"
    if not parts:
        return phrase

    if parts[0] == "+suf":
        parts.remove("+suf")
        parts[-1] = f"-{parts[-1].lstrip('-')}"

    phrase += f", {render_morphology('af', parts, data)}"
    return phrase


def render_surname(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_surname("surname", ["en"], defaultdict(str))
    '<i>A surname</i>'
    >>> render_surname("surname", [], defaultdict(str, {"lang": "en"}))
    '<i>A surname</i>'
    >>> render_surname("surname", ["en", ""], defaultdict(str))
    '<i>A surname</i>'
    >>> render_surname("surname", ["en", "rare"], defaultdict(str))
    '<i>A rare surname</i>'
    >>> render_surname("surname", ["en", "English"], defaultdict(str))
    '<i>An English surname</i>'
    >>> render_surname("surname", ["en", "occupational"], defaultdict(str, {"A": "An"}))
    '<i>An occupational surname</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"Latin"}))
    '<i>A surname from Latin</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"surnames"}))
    '<i>A surname transferred from the surname</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"given names"}))
    '<i>A surname transferred from the given name</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"nicknames"}))
    '<i>A surname transferred from the nickname</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"place names"}))
    '<i>A surname transferred from the place name</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"common nouns"}))
    '<i>A surname transferred from the common noun</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"coinages"}))
    '<i>A surname originating as a coinage</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"matronymics"}))
    '<i>A surname originating as a matronymic</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"patronymics"}))
    '<i>A surname originating as a patronymic</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"ethnonyms"}))
    '<i>A surname originating as an ethnonym</i>'
    >>> render_surname("surname", ["en"], defaultdict(str, {"from":"occupations"}))
    '<i>A surname originating as an occupation</i>'
    >>> render_surname("surname", ["en", "male"], defaultdict(str, {"parent": "Пётр"}))
    '<i>A male surname, meaning “son of Пётр”</i>'
    >>> render_surname("surname", ["en", "female"], defaultdict(str, {"parent": "Пётр"}))
    '<i>A female surname, meaning “daughter of Пётр”</i>'
    >>> render_surname("surname", ["en", "male"], defaultdict(str, {"from":"occupations", "xlit": "Petrovich", "parent": "Пётр<eq:Peter>", "eq": "Peter"}))
    '<i>A male surname, Petrovich, originating as an occupation, meaning “son of Пётр [=Peter]”, equivalent to English Peter</i>'

    >>> render_surname("patronymic", ["en", "male"], defaultdict(str, {"from":"occupations", "xlit": "Petrovich", "parent": "Пётр<eq:Peter>", "eq": "Peter"}))
    '<i>a male patronymic, Petrovich, originating as an occupation, meaning “son of Пётр [=Peter]”, equivalent to English Peter</i>'

    >>> render_surname("foreign name", ["it", "en"], defaultdict(str, {"type":"surname"}))
    '<i>a surname in English</i>'
    >>> render_surname("foreign name", ["en", "pl", "Wałęsa"], defaultdict(str, {"type":"surname"}))
    '<i>a surname in Polish</i>, <b>Wałęsa</b>'
    >>> render_surname("foreign name", ["it", "grc", "Σωκράτης"], defaultdict(str, {"type":"male given name"}))
    '<i>a male given name in Ancient Greek</i>, <b>Σωκράτης</b>'
    >>> render_surname("foreign name", ["en", "la", "Aetius"], defaultdict(str, {"type":"male given name"}))
    '<i>a male given name in Latin</i>, <b>Aetius</b>'
    """
    if parts:
        parts.pop(0)  # Remove the lang

    if not (art := data["A"]):
        art = "A" if tpl == "surname" else "a"
        if kind := data["type"]:
            if kind[0].lower() in "aeiou":
                art += "n"
        elif (
            len(parts) > (1 if tpl == "foreign name" else 0)
            and (kind := parts[1 if tpl == "foreign name" else 0])
            and kind
            and kind[0].lower() in "aeiou"
        ):
            art += "n"

    from_value, from_text = data["from"], ""
    if from_value in {
        "common nouns",
        "given names",
        "nicknames",
        "place names",
        "surnames",
    }:
        from_text = f"transferred from the {from_value[:-1]}"
    elif from_value in {"coinages", "matronymics", "patronymics"}:
        from_text = f"originating as a {from_value[:-1]}"
    elif from_value in {"ethnonyms", "occupations"}:
        from_text = f"originating as an {from_value[:-1]}"
    elif from_value == "the Bible":
        from_text = "originating from the Bible"
    elif from_value:
        from_text = f"from {from_value}"

    text: list[str] = []

    starter = f"{art} "
    if parts and parts[0] and tpl != "foreign name":
        starter += f"{parts[0]} "
    starter += data["type"] or {"foreign name": "surname"}.get(tpl, tpl)
    if parts and parts[0] and tpl == "foreign name":
        starter += f" in {langs[parts[0]]}"

    if xlit := data["xlit"]:
        text.extend((starter, xlit))
        if from_text:
            text.append(from_text)
    else:
        if from_text:
            starter += f" {from_text}"
        text.append(starter)

    if parent := data["parent"]:
        kind = {
            "male": "son",
            "female": "daughter",
        }.get(parts[0] if parts and parts[0] else "", "son/daughter")
        trad = ""
        if "<eq" in parent:
            parent, trad = parent.split("<eq:", 1)
            trad = f" [={trad.removesuffix('>')}]"
        text.append(f"meaning “{kind} of {parent}{trad}”")
    if eq := data["eq"]:
        text.append(f"equivalent to English {eq}")

    final = italic(", ".join(text))

    if tpl == "foreign name" and len(parts) > 1:
        final += f", <b>{parts[1]}</b>"
        if trans := transliterate(parts[0], parts[1]):
            final += f" ({trans})"

    return final


def render_syllabic_abbreviation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_syllabic_abbreviation("syllabic abbreviation", ["en", "Johannesburg"], defaultdict(str))
    'Syllabic abbreviation of <i>Johannesburg</i>'
    """
    return misc_variant("syllabic abbreviation", tpl, parts, data, word=word)


def render_syncopic_form(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_syncopic_form("syncopic form", ["en", "babe"], defaultdict(str))
    'Syncopic form of <i>babe</i>'
    """
    return misc_variant("syncopic form", tpl, parts, data, word=word)


def render_taxon(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_taxon("taxon", ["genus", "family", "Elephantidae"], defaultdict(str))
    'A taxonomic genus within the family Elephantidae.'
    >>> render_taxon("taxon", ["genus", "family", "Elephantidae", "mammoth"], defaultdict(str))
    'A taxonomic genus within the family Elephantidae&nbsp;– mammoth.'
    """
    text = f"A taxonomic {parts[0]} within the {parts[1]} {parts[2]}"
    if len(parts) > 3:
        text += f"&nbsp;– {parts[3]}"
    return f"{text}."


def render_th_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_th_l("th-l", ["แอร์"], defaultdict(str))
    'แอร์'
    >>> render_th_l("th-l", ["แอร์", "air conditioner"], defaultdict(str))
    'แอร์ (“air conditioner”)'
    """
    # TODO: should be improved with transliteration
    text = parts.pop(0)
    if parts:
        text += f" (“{parts.pop(0)}”)"
    return text


def at_transformer(value: str) -> str:
    """
    >>> at_transformer("Siasconset")
    'Siasconset'
    >>> at_transformer("@clip of:Siasconset")
    '<i>Clipping of</i> <b>Siasconset</b>'
    """
    if not value.startswith("@"):
        return value
    form, text = value[1:].split(":", 1)
    return f"<i>{capitalize(form_of_templates[form]['value'])}</i> <b>{text}</b>"


def render_transclude(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    This template is special as it needs to look for another word's specific definition (targeted with the `{{senseid}} template`).

    Single senseid case: https://en.wiktionary.org/wiki/Afrika
    Single senseid case with non-ASCII chars: https://en.wiktionary.org/wiki/Divonne
    Multiple senseid case: https://en.wiktionary.org/wiki/Macao
    Source is in the third argument + senseid in subdefinition: https://en.wiktionary.org/wiki/Peel_Region
    No senseid case: https://en.wiktionary.org/wiki/Ionian_Sea
    {{tcl}} arg with @: https://en.wiktionary.org/wiki/'Sconset
    """
    from ... import render, utils

    source_dir = render.get_source_dir("en", "en")
    file = render.get_latest_json_file(source_dir)
    assert file

    source_origin = parts[1]
    source = parts[-1]
    sense_id = data["id"]
    definitions: list[str] = []

    if ":" in source:
        source = source.split(":")[-1]

    for sid in sense_id.split(","):
        output = utils.grep(file, f'"{source}": "')
        pattern = re.compile(
            rf"#+\s*\{{\{{(?:senseid|sid)\|\w+\|{sid}\}}\}}\s*(.+)"
            if "{{senseid|" in output or "{{sid|" in output
            else r"#+\s*(\{\{place\|.+)"
        )
        definition = next(line.strip() for line in output.split("\\n") if pattern.search(line))
        definition = pattern.sub(r"\1", definition)

        # At this point, the definition is something like `{{place|...}}`, and if the `tcl=` arg is used, we need to alter template arguments
        if "tcl=" in definition:
            place_arg = re.search(r"\{\{place\|(\w+)", definition)[1]  # type: ignore[index]
            tcl_args = re.search(r"tcl=([^}]+)\}\}", definition)[1].split(";;")  # type: ignore[index]
            definition = f"{{{{place|{place_arg}|{'|'.join(tcl_args)}}}}}"

        definition = re.sub(r"<<\w+/([^>]+)>>", r"\1", definition)
        definition = utils.process_templates(word, definition, "en")
        definition = definition.split(".", 1)[0]
        definitions.append(definition)

    if parts[0] == "en" and source_origin[0] != "@":
        return "\n".join(definitions)

    return f"{at_transformer(source_origin)} ({'\n'.join(definitions)})"


def render_uncertain(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_uncertain("unc", ["en"], defaultdict(str))
    'Uncertain'
    >>> render_uncertain("unc", ["en", "unclear"], defaultdict(str))
    'unclear'
    >>> render_uncertain("uncertain", ["en"], defaultdict(str, {"nocap": "1"}))
    'uncertain'
    >>> render_uncertain("uncertain", ["en"], defaultdict(str, {"title": "Not certain"}))
    'Not certain'
    """
    if len(parts) > 1:
        title = parts[-1]
        data["nocap"] = "1"
    else:
        title = "uncertain"
    return misc_variant_no_term(title, tpl, parts, data, word=word)


def render_univerbation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_univerbation("univerbation", ["en"], defaultdict(str, {"nocap": "1"}))
    'univerbation'
    >>> render_univerbation("univerbation", ["en", "be", "gone"], defaultdict(str))
    'Univerbation of <i>be</i> + <i>gone</i>'
    """
    text = ("u" if data["nocap"] == "1" else "U") + "niverbation"
    if words := [italic(p) for p in parts[1:]]:
        text += " of "
    return f"{text}{concat(words, sep=' + ')}"


def render_unknown(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_unknown("unk", ["en"], defaultdict(str, { "notext":"1", "nocap":"1"}))
    ''
    >>> render_unknown("unk", ["en"], defaultdict(str))
    'Unknown'
    >>> render_unknown("unk", ["en"], defaultdict(str, {"nocap":"1"}))
    'unknown'
    >>> render_unknown("unk", ["en"], defaultdict(str, {"title":"Uncertain"}))
    'Uncertain'
    """
    if data["notext"] == "1":
        return ""
    elif data["title"]:
        return data["title"]
    elif data["nocap"] == "1":
        return "unknown"
    else:
        return "Unknown"


def render_used_in_phrasal_verbs(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_used_in_phrasal_verbs("used in phrasal verbs", ["abide by"], defaultdict(str, {"lang": "en", "t": "to accept and act in accordance with"}))
    '<i>Used in a phrasal verb:</i> <b>abide by</b> (“to accept and act in accordance with”).'
    """
    return f"<i>Used in a phrasal verb:</i> <b>{parts[0]}</b>{gloss_tr_poss(data, data['t'])}."


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("__variant__en-archaic third-person singular of", ["verb"], defaultdict(str))
    'verb'

    >>> render_variant("__variant__infl of", ["en", "human", "", "s-verb-form"], defaultdict(str), word="humans")
    'human'
    >>> render_variant("__variant__infl of", ["en", "human", "", "s-verb-form"], defaultdict(str, {"1": "en", "2": "human", "3": "", "4": "s-verb-form"}), word="humans")
    'human'

    >>> render_variant("__variant__plural of", ["en", "woman"], defaultdict(str), word="women")
    'woman'

    >>> render_variant("__variant__form of", ["en", "Alternative (anglicized) spelling", "Wrocław"], defaultdict(str), word="Wroclaw")
    'Wrocław'
    >>> render_variant("__variant__adj form of", ["en", "Alternative (anglicized) spelling", "Wrocław"], defaultdict(str), word="Wroclaw")
    'Alternative (anglicized) spelling'
    """
    if "en-archaic" in tpl:
        return parts[0]

    if "_form of" in tpl:
        return parts[-1]

    return data["2"] or parts[1]


def render_vern(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_vern("vern", ["Pacific cod"], defaultdict(str))
    'Pacific cod'
    >>> render_vern("vern", ["freshwater sculpin"], defaultdict(str, {"pl": "s"}))
    'freshwater sculpins'
    >>> render_vern("vern", ["freshwater sculpin", "freshwater sculpins"], defaultdict(str))
    'freshwater sculpins'
    """
    return parts[-1] + data["pl"]


def render_vi_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_vi_l("vi-l", ["bánh"], defaultdict(str))
    'bánh'
    >>> render_vi_l("vi-l", ["bánh", "𨋣"], defaultdict(str))
    'bánh (𨋣)'
    """
    text = parts.pop(0)
    if parts:
        text += f" ({parts[0]})"
    return text


def render_wasei_eigo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_wasei_eigo("wasei eigo", [], defaultdict(str))
    'Wasei eigo (和製英語; pseudo-anglicism)'
    >>> render_wasei_eigo("wasei eigo", ["family", "computer"], defaultdict(str))
    'Wasei eigo (和製英語; pseudo-anglicism) derived from <i>family</i>&nbsp;+&nbsp;<i>computer</i>'
    >>> render_wasei_eigo("wasei eigo", ["family", "computer"], defaultdict(str, {"nocap": "1"}))
    'wasei eigo (和製英語; pseudo-anglicism) derived from <i>family</i>&nbsp;+&nbsp;<i>computer</i>'
    """
    text = f"{'w' if data['nocap'] else 'W'}asei eigo (和製英語; pseudo-anglicism)"
    if parts:
        text += f" derived from {concat([italic(part) for part in parts], '&nbsp;+&nbsp;')}"
    return text


def render_xlit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_xlit("xlit", ["ar", "عُظْمَى"], defaultdict(str))
    'ʕuẓmā'
    >>> render_xlit("xlit", ["zz", "foo"], defaultdict(str))
    ''
    """
    return transliterate(parts[0], parts[1])


def render_zh_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_l("zh-l", ["痟", "mad"], defaultdict(str, {"tr": "siáu"}))
    '痟 (<i>siáu</i>, “mad”)'
    """
    return chinese(parts, data)


template_mapping = {
    "&lit": render_lit,
    "abbreviated": render_abbreviated,
    "aka": render_aka,
    "ante2": render_ante2,
    "aphetic form": render_aphetic_form,
    "apocopic form": render_apocopic_form,
    "ar-active participle": render_ar_active_participle,
    "ar-instance noun": render_ar_instance_noun,
    "ar-passive participle": render_ar_passive_participle,
    "ar-root": render_ar_root,
    "blockquote": render_blockquote,
    "bond credit rating": render_bond_credit_rating,
    "century": render_century,
    "chemical symbol": render_chemical_symbol,
    "clipped compound": render_clipped_compound,
    "Cyrl-def": render_cyrl_def,
    "demonym-adj": render_demonym_adj,
    "demonym-noun": render_demonym_noun,
    "denominal verb": render_denominal_verb,
    "deverbal": render_deverbal,
    "displaced": render_displaced,
    "en-noun": render_en_noun,
    "en-proper noun": render_en_proper_noun,
    "etydate": render_etydate,
    "fa-xlit": render_fa_xlit,
    "frac": render_frac,
    "g": render_g,
    "geochronology": render_geochronology,
    "given name": render_given_name,
    "Han simp": render_han_simp,
    "he-l": render_he_l,
    "he-m": render_he_m,
    "he-root": render_he_root,
    "historical given name": render_historical_given_name,
    "IATA": render_iata,
    "ISO 217": render_iso_217,
    "ISO 639": render_iso_639,
    "ISO 3166": render_iso_3166,
    "ISO 4217": render_iso_4217,
    "ja-blend": render_ja_blend,
    "ja-l": render_ja_l,
    "Köppen": render_köppen,
    "langname": render_langname,
    "ltc-l": render_ltc_l,
    "lw": render_lw,
    "m-self": render_m_self,
    "metathesis": render_metathesis,
    "misconstruction": render_misconstruction,
    "morse code abbreviation": render_morse_code_abbreviation,
    "morse code for": render_morse_code_for,
    "morse code prosign": render_morse_code_prosign,
    "mul-cjk stroke-def": render_mul_cjk_stroke_def,
    "mul-domino def": render_mul_domino_def,
    "mul-kanadef": render_mul_kanadef,
    "name translit": render_name_translit,
    "named-after": render_named_after,
    "nuclide": render_nuclide,
    "och-l": render_och_l,
    "pedlink": render_pedlink,
    "phonetic alphabet": render_phonetic_alphabet,
    "person": render_person,
    "place": render_place,
    "rebracketing": render_rebracketing,
    "RQ": render_rq,
    "SI-unit-2": render_si_unit_2,
    "SI-unit-abb2": render_si_unit_abb2,
    "SIC": render_sic,
    "spelling pronunciation": render_spelling_pronunciation,
    "sumti": render_sumti,
    "syllabic abbreviation": render_syllabic_abbreviation,
    "taxon": render_taxon,
    "th-l": render_th_l,
    "vi-l": render_vi_l,
    "xlit": render_xlit,
    **dict.fromkeys({"a", "accent"}, render_accent),
    **dict.fromkeys({"A.D", "AD", "B.C.E.", "BCE", "B.C.", "BC", "C.E.", "CE"}, render_bce),
    **dict.fromkeys(
        {
            "adapted borrowing",
            "abor",
            "back-formation",
            "backform",
            "backformation",
            "back-form",
            "bf",
            "borrowed",
            "bor",
            "bor-lite",
            "bor+",
            "calque",
            "cal",
            "clq",
            "cognate",
            "cog",
            "cog-lite",
            "derived",
            "der",
            "der+",
            "der-lite",
            "etyl",
            "false cognate",
            "fcog",
            "inherited",
            "inh-lite",
            "inh",
            "inh+",
            "l",
            "l-lite",
            "langname-mention",
            "learned borrowing",
            "lbor",
            "link",
            "ll",
            "mention",
            "m",
            "m+",
            "m-lite",
            "noncognate",
            "nc",
            "ncog",
            "noncog",
            "obor",
            "orthographic borrowing",
            "partial calque",
            "pcal",
            "pclq",
            "phono-semantic matching",
            "psm",
            "semantic loan",
            "semi-learned borrowing",
            "sl",
            "slbor",
            "transliteration",
            "translit",
            "unadapted borrowing",
            "ubor",
            "uder",
        },
        render_foreign_derivation,
    ),
    **dict.fromkeys(
        {
            "affix",
            "af",
            "blend of",
            "blend",
            "compound",
            "com",
            "compound+",
            "com+",
            "confix",
            "con",
            "doublet",
            "dbt",
            "infix",
            "in",
            "prefix",
            "pre",
            "piecewise doublet",
            "piecewise_doublet",
            "pw dbt",
            "pwd",
            "pwdbt",
            "suffix",
            "suf",
            "suffixusex",
            "sufex",
            "usex-suffix",
        },
        render_morphology,
    ),
    **dict.fromkeys({"ante", "a.", "circa", "c.", "post", "p."}, render_dating),
    **dict.fromkeys({"cap", "U"}, render_cap),
    **dict.fromkeys({"circa2", "post2"}, render_dating_full_and_short),
    **dict.fromkeys({"clipping", "clip"}, render_clipping),
    **dict.fromkeys({"codepoint", "unichar"}, render_codepoint),
    **dict.fromkeys({"coinage", "coined", "coin"}, render_coinage),
    **dict.fromkeys({"contraction", "contr"}, render_contraction),
    **dict.fromkeys({"el-UK-US", "l-UK-US"}, render_el_uk_us),
    **dict.fromkeys(form_of_templates.keys(), render_form_of_t),
    **dict.fromkeys({"filter-avoidance spelling of", "fa sp"}, render_fa_sp),
    **dict.fromkeys({"IPAchar", "ipachar", "ic"}, render_ipa_char),
    **dict.fromkeys({"ISO 216", "ISO 269"}, render_iso_216),
    **dict.fromkeys({"ja-compound", "com-ja", "ja-com"}, render_ja_compound),
    **dict.fromkeys({"ja-etym-renyokei", "ja-ryk", "ja-vstem"}, render_ja_etym_renyokei),
    **dict.fromkeys({"ja-r", "ryu-r"}, render_ja_r),
    **dict.fromkeys({"ko-inline", "ko-l"}, render_ko_inline),
    **dict.fromkeys({"label", "lb", "lbl", "term-label", "tlb"}, render_label),
    **dict.fromkeys({"Latn-def", "Latn-def-lite"}, render_latn_def),
    **dict.fromkeys({"nb...", "..."}, render_nb),
    **dict.fromkeys({"only used in", "only in"}, render_only_used_in),
    **dict.fromkeys({"onomatopoeic", "onomatopoeia", "onomatopeic", "onom"}, render_onomatopoeic),
    **dict.fromkeys({"pedia", "pedialite"}, render_pedia),
    **dict.fromkeys({"pseudo-acronym of", "pseudo-acronym"}, render_pseudo_acronym_of),
    **dict.fromkeys({"pseudo-loan", "pseudoloan", "pl"}, render_pseudo_loan),
    **dict.fromkeys({"reduplication of", "reduplication", "redup", "rdp"}, render_reduplication),
    **dict.fromkeys({"SI-unit-abb", "SI-unit-abbnp"}, render_si_unit_abb),
    **dict.fromkeys({"SI-unit", "SI-unit-np"}, render_si_unit),
    **dict.fromkeys({"semantic shift", "ss"}, render_semantic_shift),
    **dict.fromkeys({"sound symbolic", "sound-symbolic"}, render_sound_symbolic),
    **dict.fromkeys({"spoonerism of", "spoonerism", "spoon of"}, render_spoonerism),
    **dict.fromkeys({"surface analysis", "surface etymology", "surf"}, render_surface_analysis),
    **dict.fromkeys({"surname", "patronymic", "foreign name"}, render_surname),
    **dict.fromkeys({"syncopic form", "sync"}, render_syncopic_form),
    **dict.fromkeys({"transclude sense", "transclude", "tcl"}, render_transclude),
    **dict.fromkeys({"uncertain", "unc"}, render_uncertain),
    **dict.fromkeys({"univerbation", "univ"}, render_univerbation),
    **dict.fromkeys({"unknown", "unk"}, render_unknown),
    **dict.fromkeys({"used in phrasal verbs", "phrasal verb"}, render_used_in_phrasal_verbs),
    **dict.fromkeys({"vernacular", "vern"}, render_vern),
    **dict.fromkeys({"wasei eigo", "waei"}, render_wasei_eigo),
    **dict.fromkeys({"zh-l", "zh-m"}, render_zh_l),
    #
    # Variants
    #
    "__variant__active participle of": render_variant,
    "__variant__adj form of": render_variant,
    "__variant__agent noun of": render_variant,
    "__variant__an of": render_variant,
    "__variant__alternative plural of": render_variant,
    "__variant__female equivalent of": render_variant,
    "__variant__feminine equivalent of": render_variant,
    "__variant__femeq": render_variant,
    "__variant__feminine of": render_variant,
    "__variant__feminine plural of": render_variant,
    "__variant__feminine plural past participle of": render_variant,
    "__variant__feminine singular of": render_variant,
    "__variant__feminine singular past participle of": render_variant,
    "__variant__form of": render_variant,
    "__variant__gerund of": render_variant,
    "__variant__imperfective form of": render_variant,
    "__variant__inflection of": render_variant,
    "__variant__infl of": render_variant,
    "__variant__masculine plural of": render_variant,
    "__variant__masculine plural past participle of": render_variant,
    "__variant__neuter plural of": render_variant,
    "__variant__neuter singular past participle of": render_variant,
    "__variant__noun form of": render_variant,
    "__variant__participle of": render_variant,
    "__variant__passive of": render_variant,
    "__variant__passive participle of": render_variant,
    "__variant__past participle form of": render_variant,
    "__variant__past participle of": render_variant,
    "__variant__perfective form of": render_variant,
    "__variant__plural of": render_variant,
    "__variant__plural": render_variant,
    "__variant__present participle of": render_variant,
    "__variant__reflexive of": render_variant,
    "__variant__verbal noun of": render_variant,
    "__variant__verb form of": render_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
