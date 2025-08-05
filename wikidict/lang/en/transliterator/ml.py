"""
Source: https://en.wiktionary.org/w/index.php?title=Module:ml-translit&oldid=79050562
"""

import re

CONSONANTS: dict[str, str] = {
    "ക": "k",
    "ഖ": "kh",
    "ഗ": "g",
    "ഘ": "gh",
    "ങ": "ṅ",
    "ച": "c",
    "ഛ": "ch",
    "ജ": "j",
    "ഝ": "jh",
    "ഞ": "ñ",
    "ട": "ṭ",
    "ഠ": "ṭh",
    "ഡ": "ḍ",
    "ഢ": "ḍh",
    "ണ": "ṇ",
    "ത": "t",
    "ഥ": "th",
    "ദ": "d",
    "ധ": "dh",
    "ന": "n",
    "പ": "p",
    "ഫ": "ph",
    "ബ": "b",
    "ഭ": "bh",
    "മ": "m",
    "യ": "y",
    "ര": "r",
    "ല": "l",
    "വ": "v",
    "ശ": "ś",
    "ഷ": "ṣ",
    "സ": "s",
    "ഹ": "h",
    "ള": "ḷ",
    "ഴ": "ḻ",
    "റ": "ṟ",
    "ഩ": "ṉ",
    "ഺ": "ṯ",
}

DIACRITICS: dict[str, str] = {
    "\u0d49\u0d55": "ŭ",  # \224\181\129\224\181\141
    "\u0d3e": "ā",  # \224\180\190
    "\u0d3f": "i",  # \224\180\191
    "\u0d40": "ī",  # \224\181\128
    "\u0d41": "u",  # \224\181\129
    "\u0d42": "ū",  # \224\181\130
    "\u0d43": "r̥",  # \224\181\131
    "\u0d44": "r̥̄",  # \224\181\132
    "\u0d46": "e",  # \224\181\134
    "\u0d47": "ē",  # \224\181\135
    "\u0d48": "ai",  # \224\181\136
    "\u0d4a": "o",  # \224\181\138
    "\u0d4b": "ō",  # \224\181\139
    "\u0d4c": "au",  # \224\181\140 (archaic au)
    "\u0d57": "au",  # \224\181\151
    "\u0d62": "l̥",  # \224\181\162
    "\u0d63": "l̥̄",  # \224\181\163
    "\u0d4d": "",  # \224\181\141 (virama)
    "": "a",  # no diacritic
}

NONCONSONANTS: dict[str, str] = {
    "അ": "a",
    "ആ": "ā",
    "ഇ": "i",
    "ഈ": "ī",
    "ഉ": "u",
    "ഊ": "ū",
    "ഋ": "r̥",
    "ൠ": "r̥̄",
    "ഌ": "l̥",
    "ൡ": "l̥̄",
    "എ": "e",
    "ഏ": "ē",
    "ഐ": "ai",
    "ഒ": "o",
    "ഓ": "ō",
    "ഔ": "au",
    "ൟ": "ī",
    "ം": "ṁ",
    "ഃ": "ḥ",
    "ഽ": "’",
    "ൺ": "ṇ",
    "ൻ": "ṉ",
    "ർ": "ṟ",
    "ൽ": "l",
    "ൾ": "ḷ",
    "ൿ": "k",
    "ൔ": "m",
    "ൕ": "y",
    "ൖ": "ḻ",
    "ൎ": "ṟ",
    "൦": "0",
    "൧": "1",
    "൨": "2",
    "൩": "3",
    "൪": "4",
    "൫": "5",
    "൬": "6",
    "൭": "7",
    "൮": "8",
    "൯": "9",
    "൰": "10",
    "൱": "100",
    "൲": "1000",
    "൳": "¼",
    "൴": "½",
    "൵": "¾",
    "൞": "⅕",
    "൷": "⅛",
    "൜": "⅒",
    "൶": "¹⁄₁₆",
    "൸": "3⁄16",
    "൛": "1⁄20",
    "൝": "3⁄20",
    "൙": "1⁄40",
    "൚": "3⁄80",
    "൘": "1⁄160",
}

VIRAMA = "\u0d4d"


def tr(text: str, lang: str) -> str:
    # Final virama rules
    if lang in {"ml", "tcy"}:
        # Add ŭ after word-final virama (optionally followed by punctuation)
        text = re.sub(rf"{VIRAMA}([,\.!\?:;]?)$", rf"{VIRAMA}ŭ\1", text)
        text = re.sub(rf"{VIRAMA}([,\.!\?:;]?) ", rf"{VIRAMA}ŭ\1 ", text)

    # Consonant + diacritic pattern:
    # Malayalam consonant (named explicitly), followed by optional diacritic.
    consonant_chars = "".join(CONSONANTS.keys())
    diacritic_chars = "".join(
        [
            "\u0d3e",
            "\u0d3f",
            "\u0d40",
            "\u0d41",
            "\u0d42",
            "\u0d43",
            "\u0d44",
            "\u0d46",
            "\u0d47",
            "\u0d48",
            "\u0d4a",
            "\u0d4b",
            "\u0d4c",
            "\u0d57",
            "\u0d62",
            "\u0d63",
            "\u0d4d",
        ]
    )
    # Also allow empty diacritic ("")
    pattern = rf"([{consonant_chars}])((?:\u0d49)?[{diacritic_chars}]?)"

    def cons_diacritics_repl(match: re.Match[str]) -> str:
        c, d = match[1], match[2]
        # Handle two-char diacritic (\u0d49\u0d55) for 'ŭ'
        diacrit = DIACRITICS.get(d, d) if d == "\u0d49\u0d4d" else DIACRITICS.get(d, d)
        return f"{CONSONANTS[c]}{diacrit}"

    text = re.sub(pattern, cons_diacritics_repl, text)

    # Replace non-consonants
    text = "".join(NONCONSONANTS.get(char, char) for char in text)

    # Anusvara rules
    text = re.sub(r"ṁ([kgṅ])", r"ṅ\1", text)
    text = re.sub(r"ṁ([cjñ])", r"ñ\1", text)
    text = re.sub(r"ṁ([ṭḍṇ])", r"ṇ\1", text)
    text = re.sub(r"ṁ([tdn])", r"n\1", text)
    text = re.sub(r"ṁ([pbm])", r"m\1", text)

    # ŭ is elided before vowels
    text = re.sub(r"ŭ ([,\.!\?:;]?)([aāiīuūeo])", r" \1\2", text)

    return text


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: hhttps://en.wiktionary.org/w/index.php?title=Module:ml-translit/testcases&oldid=63954274

    >>> transliterate("ഡിസംബര്")
    'ḍisambar'
    >>> transliterate("രാജാവ്")
    'rājāv'
    >>> transliterate("ഹിന്ദുമതം")
    'hindumataṁ'
    >>> transliterate("അവൻ")
    'avaṉ'
    >>> transliterate("ലളിതാഽപി")
    'laḷitā’pi'
    >>> transliterate("അനുസ്വാരഃ")
    'anusvāraḥ'
    >>> transliterate("ആത്മാവ്")
    'ātmāv'
    >>> transliterate("വിജ്ഞാനകോശം")
    'vijñānakōśaṁ'
    >>> transliterate("അസ്സലാമു അലൈക്കും")
    'assalāmu alaikkuṁ'
    >>> transliterate("പേര്")
    'pēr'
    >>> transliterate("തൎക്കം")
    'taṟkkaṁ'
    >>> transliterate("കാറ്റ്")
    'kāṟṟ'
    >>> transliterate("എന്റെ")
    'enṟe'
    >>> transliterate("എൻ്റെ")
    'eṉ്ṟe'
    """
    return tr(text, locale)
