"""
Source: https://en.wiktionary.org/w/index.php?title=Module:en-utilities&oldid=83796051
"""

import re
import unicodedata
from typing import Any

from .headword import comb_chars

vowels: str = "aæᴀᴁɐɑɒ@eᴇǝⱻəɛɘɜɞɤiıɪɨᵻoøœᴏɶɔᴐɵuᴜʉᵾɯꟺʊʋʌyʏ"
hyphens: str = "-‐‑‒–—"
vowel: str = rf"[{vowels}]"


def reverse(s: str) -> str:
    return s[::-1]


def sub(s: str, start: int, end: int | None = None) -> str:
    if end is None:
        return s[start:] if start < 0 else s[start - 1 :]
    if start < 0 and end < 0:
        return s[start : end + 1]
    elif start < 0:
        return s[start:end]
    elif end < 0:
        return s[start - 1 : end + 1]
    else:
        return s[start - 1 : end]


def match(s: str, pattern: str, pos: int | None = None) -> tuple[str, ...] | None:
    # pattern should be a Python regex
    m = re.match(pattern, s) if pos is None else re.match(pattern, s[pos - 1 :])
    if not m:
        return None
    return m.groups() if m.lastindex else (m[0],)


def umatch(s: str, pattern: str) -> str | None:
    m = re.search(pattern, s)
    return m[0] if m else None


def ugsub(s: str, pattern: str, repl: str) -> str:
    return re.sub(pattern, repl, s)


def usub(s: str, n: int) -> str:
    # last n chars if n < 0
    return s[n:]


diacritics: str = f"{comb_chars['diacritics_all']}+"


def normalize(text: str, followed_by: str = "", not_gu: bool = False) -> str:
    text = ugsub(
        unicodedata.normalize("NFD", text) + followed_by, f"([{'' if not_gu else 'Gg'}Qq])u([{vowels}])", r"\1\2"
    )
    return ugsub(sub(text, 1, len(text) - len(followed_by)), diacritics, "").lower()


def epenthetic_e_default(stem: str) -> bool:
    return sub(stem, -1) != "e"


def epenthetic_e_for_s(stem: str, term: str = "") -> bool:
    if stem != term:
        return True
    if re.match(r"^[^\x80-\xff]*$", stem):
        final = sub(stem, -1)
    else:
        stem = ugsub(unicodedata.normalize("NFD", stem), diacritics, "")
        final = usub(stem, -1)
    return (
        final == "g"
        and sub(stem, -2, -2) == "d"
        or bool(final == "h" and re.match(r"[csz]h+$", stem))
        or bool(final == "j" and umatch(stem, f"[^{vowels}]j$"))
        or final == "s"
        or bool(final == "u" and umatch(stem, r"\f[\w']u$"))
        or final == "x"
        or final == "z"
        or final == "ß"
    )


def remove_possessive(stem: str) -> str:
    m = re.match(r"^(.*)'s$", stem)
    if m:
        return m[1]
    m = re.match(r"^(.*s)'$", stem)
    return m[1] if m else stem


suffixes: dict[str, dict[str, Any]] = {
    "'s": {"truncated": lambda stem: "'" if sub(stem, -1) == "s" else "'s"},
    "s.plural": {
        "final_y_is_i": True,
        "epenthetic_e": epenthetic_e_for_s,
        "modifies_possessive": True,
    },
    "s.verb": {
        "final_y_is_i": True,
        "final_consonant_is_doubled": True,
        "epenthetic_e": epenthetic_e_for_s,
    },
    "ing": {"final_consonant_is_doubled": True, "remove_silent_e": True},
    "d": {
        "final_y_is_i": True,
        "final_consonant_is_doubled": True,
        "epenthetic_e": epenthetic_e_default,
    },
}
suffixes["dst"] = suffixes["d"]
suffixes["st.verb"] = suffixes["d"]
suffixes["th"] = suffixes["d"]
suffixes["n"] = {
    "final_y_is_i": True,
    "final_y_is_i_after_vowel": True,
    "final_guy_is_gui": True,
    "final_consonant_is_doubled": True,
    "epenthetic_e": lambda stem: not (sub(stem, -1) == "e" or umatch(normalize(stem), f"[{vowels}][irw]$")),
}
suffixes["r"] = {
    "final_y_is_i": True,
    "final_ey_is_i": True,
    "final_guy_is_gui": True,
    "final_consonant_is_doubled": True,
    "epenthetic_e": epenthetic_e_default,
}
suffixes["st.superlative"] = suffixes["r"]


def convert_final_y_to_i(
    text: str,
    not_gu: bool = True,
    final_ey_is_i: bool = False,
    final_y_is_i_after_vowel: bool = False,
) -> str:
    final3 = usub(text, -3)
    if final3 == "eey":
        return f"{sub(text, 1, len(text) - 1)}i"
    final2 = usub(text, -2)
    if final_ey_is_i and final2 == "ey":
        base_stem = sub(text, 1, len(text) - 2)
        if umatch(final3, rf"[{hyphens}]ey"):
            return f"{base_stem}i"
        normalized = normalize(base_stem, "ey")
        if sub(normalized, -1) == "y" and umatch(normalized, r"[\w@][yY]$"):
            return f"{base_stem}i"
        elif umatch(normalized, rf"[{vowels}\d]\w*$"):
            return f"{base_stem}i"
    elif umatch(final2, rf"[{hyphens}]y"):
        return f"{sub(text, 1, len(text) - 1)}i"
    else:
        base_stem = sub(text, 1, len(text) - 1)
        exclude = "" if final_y_is_i_after_vowel else vowels
        if umatch(normalize(base_stem, "y", not_gu), rf"[^{exclude}\s\p]$"):
            return f"{base_stem}i"
    return text


def double_final_consonant(text: str, final: str) -> str:
    initial = umatch(normalize(sub(text, 1, len(text) - 1), final), rf"^.*\b([a-z\p]*)[{vowels}]$")
    if initial and (
        initial == ""
        or initial == "y"
        or re.match(r"^.[\u0080-\u00BF]*$", initial)
        and umatch(initial, rf"[^{vowels}]")
        or umatch(initial, rf"^[^{vowels}]*\b$")
    ):
        return text + final
    return text


def remove_silent_e(text: str) -> str:
    final2 = sub(text, -2)
    if final2 == "ie":
        return ugsub(text, r"([^yY\s\p])ie$", r"\1y")
    base_stem = sub(text, 1, len(text) - 1)
    if final2 == "ue" or umatch(normalize(base_stem, "e"), f"[{vowels}][^{vowels}]+$"):
        return base_stem
    return text


def add_suffix(term: str, suffix: str, pos: str | None = None) -> str:
    data = suffixes[suffix]
    possessive = False
    if data.get("modifies_possessive"):
        new = remove_possessive(term)
        if new != term:
            term, possessive = new, True
    suffix_main = re.match(r"^([^.]+)", suffix)[1]
    final = sub(term, -1)
    if data.get("final_y_is_i") and final == "y" and pos != "proper noun":
        stem = convert_final_y_to_i(
            term,
            not data.get("final_guy_is_gui", False),
            data.get("final_ey_is_i", False),
            data.get("final_y_is_i_after_vowel", False),
        )
    elif data.get("remove_silent_e") and final == "e":
        stem = remove_silent_e(term)
    else:
        stem = term
    epenthetic_e = data.get("epenthetic_e")
    if epenthetic_e and epenthetic_e(stem, term):
        suffix_main = f"e{suffix_main}"
    if (
        data.get("final_consonant_is_doubled")
        and re.match(r"^[bcdfgjklmnpqrstvz]$", final)
        and re.match(rf"^[{vowels}]", suffix_main)
    ):
        stem = double_final_consonant(term, final)
    truncated = data.get("truncated")
    if truncated:
        suffix_main = truncated(stem)
    output = stem + suffix_main
    if possessive:
        output = add_suffix(output, "'s", pos)
    return output


def pluralize(text: str) -> str:
    if not ("[[" in text and text.endswith("]]")):
        return add_suffix(text, "s.plural")
    str_rev = reverse(text)
    b_open = str_rev.find("[[", 3)
    bad_close = str_rev.find("]]", 3)
    if bad_close != -1 and (b_open == -1 or bad_close < b_open):
        return add_suffix(text, "s.plural")
    if b_open == -1:
        return add_suffix(text, "s.plural")
    b_open = len(text) - b_open + 2
    m = re.match(rf"{re.escape(text[:b_open])}([^|]*)\|?(.*)\]\]$", text)
    if not m:
        return add_suffix(text, "s.plural")
    target, display = m[1], m[2]
    display = add_suffix(display if display != "" else target, "s.plural")
    if display.startswith(target):
        return text[:b_open] + target + display[len(target) :]
    return f"{text[:b_open]}{target}|{display}"


def is_regular_plural(plural: str, term: str, pos: str = "noun") -> bool:
    init_plural, init_term, try_as_proper_noun = plural, term, False
    if pos == "noun+":
        pos, try_as_proper_noun = "noun", True
    final_punc = umatch(term, r"\p*$") or ""
    final_punc_len = len(final_punc)
    if sub(plural, -final_punc_len) == final_punc:
        term = sub(term, 1, len(term) - final_punc_len)
        plural = sub(plural, 1, len(plural) - final_punc_len)
    if plural == add_suffix(term, "s.plural", pos):
        return True
    final = sub(term, -1)
    if (
        final == "s"
        and plural == f"{term}ses"
        or final == "z"
        and plural == f"{term}zes"
        or final == "y"
        and plural == f"{convert_final_y_to_i(term)}es"
        or final == "Y"
        and plural.lower() == f"{convert_final_y_to_i(term.lower())}es"
    ):
        return True

    if try_as_proper_noun:
        init = umatch(init_term, r"^[^\w\s]*(\w)")
        return (
            bool(init)
            and init.upper() == init
            and init.lower() != init
            and is_regular_plural(init_plural, init_term, "proper noun")
        )
    return False


def do_singularize(str_: str) -> str:
    sing = re.match(r"^(.*)ies$", str_)
    if sing:
        return f"{sing[1]}y"
    m = re.match(r"^(.*[cs]h\]*)es$", str_)
    if m:
        return m[1]
    m = re.match(r"^(.*x\]*)es$", str_)
    if m:
        return m[1]
    m = re.match(r"^(.*)s$", str_)
    return m[1] if m else str_


def collapse_link(link: str, linktext: str) -> str:
    return link if link == linktext else linktext


def singularize(text: str) -> str:
    if not (m := re.match(r"^(.*)\[\[([^|\]]+)\|?(.*?)\]\]$", text)):
        return do_singularize(text)
    beginning, link, linktext = m[1], m[2], m[3]
    if linktext != "":
        return beginning + collapse_link(link, do_singularize(linktext))
    return f"{beginning}{do_singularize(link)}"


def get_indefinite_article(text: str, ucfirst: bool = False) -> str:
    text = text or ""
    m = re.match(r"^\[\[([^|\]]+)\|?(.*?)\]\]", text)
    link, linktext = (m[1], m[2]) if m else (None, None)
    first_letter = linktext or link or text
    if re.match(r"^[AEIOUaeiou]", first_letter):
        return "An" if ucfirst else "an"
    return "A" if ucfirst else "a"


def add_indefinite_article(text: str, ucfirst: bool = False) -> str:
    return f"{get_indefinite_article(text, ucfirst)} {text}"
