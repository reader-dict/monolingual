"""
Python conversion of the gu-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:gu-translit

Current version from 2024-05-12 15:32
  - https://en.wiktionary.org/w/index.php?title=Module:gu-translit&oldid=79229509
"""

import re
import unicodedata

conv = {
    # consonants
    "ક": "k",
    "ખ": "kh",
    "ગ": "g",
    "ઘ": "gh",
    "ઙ": "ṅ",
    "ચ": "c",
    "છ": "ch",
    "જ": "j",
    "ઝ": "jh",
    "ઞ": "ñ",
    "ટ": "ṭ",
    "ઠ": "ṭh",
    "ડ": "ḍ",
    "ઢ": "ḍh",
    "ણ": "ṇ",
    "ત": "t",
    "થ": "th",
    "દ": "d",
    "ધ": "dh",
    "ન": "n",
    "પ": "p",
    "ફ": "ph",
    "બ": "b",
    "ભ": "bh",
    "મ": "m",
    "ય": "y",
    "ર": "r",
    "લ": "l",
    "વ": "v",
    "ળ": "ḷ",
    "શ": "ś",
    "ષ": "ṣ",
    "સ": "s",
    "હ": "h",
    "ત઼": "t̰",
    "જ઼": "z",
    "ંઘ઼": "ng",
    "ડ઼": "ṛ",
    "ઢ઼": "ṛh",
    "ન઼": "ṉ",
    "ફ઼": "f",
    # vowel diacritics
    "ા": "ā",
    "િ": "i",
    "ી": "ī",
    "ુ": "u",
    "ૂ": "ū",
    "ૃ": "ŕ",
    "ૄ": "ṝ",
    "ે": "e",
    "ૈ": "ai",
    "ો": "o",
    "ૌ": "au",
    "ૅ": "ě",
    "ૉ": "ŏ",
    # vowel mātras
    "અ": "a",
    "આ": "ā",
    "ઇ": "i",
    "ઈ": "ī",
    "ઉ": "u",
    "ઊ": "ū",
    "ઋ": "ŕ",
    "ૠ": "ṝ",
    "એ": "e",
    "ઐ": "ai",
    "ઓ": "o",
    "ઔ": "au",
    "ઍ": "ě",
    "ઑ": "ŏ",
    # chandrabindu
    "ઁ": "m̐",
    # anusvara
    "ં": "ṃ",
    # visarga
    "ઃ": "ḥ",
    # virama
    "્": "",
    # avagraha
    "ઽ": "’",
    # numerals
    "૦": "0",
    "૧": "1",
    "૨": "2",
    "૩": "3",
    "૪": "4",
    "૫": "5",
    "૬": "6",
    "૭": "7",
    "૮": "8",
    "૯": "9",
    # punctuation
    "।": ".",  # danda
    "+": "",  # compound separator
    # om
    "ૐ": "OM",
}

nasal_assim = {
    r"[kg]h?": "ṅ",
    r"[cj]h?": "ñ",
    r"[ṭḍṛ]h?": "ṇ",
    r"[td]h?": "n",
    r"[pb]h?": "m",
    r"n": "n",
    r"m": "m",
}


def _sub_with_dict(pattern: str, mapping: dict[str, str], text: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        return mapping.get(match[0], match[0])

    return re.sub(pattern, _repl, text)


def tr(text: str) -> str:
    sub = re.sub

    c = r"([કખગઘઙચછજઝઞટઠડઢતથદધપફબભશષસયરલવહણનમ]઼?)"
    no_drop = "ય"
    final_no_drop = "યરલવહનમ"
    v = r"([a્ાિીુૂેૈોૌૃૄૅૉ]ઁ?)"
    virama = r"(્)"
    n = r"(ં?)"
    nukta = r"([તજઘડઢનફ]઼)"

    can_drop = sub(rf"[{no_drop}]", "", c)
    final_can_drop = sub(rf"[{final_no_drop}]", "", c)
    no_virama = sub(virama, "", v)

    text += " "

    # text = sub(r'(\S)'+c+r'%2', r'\1ː\2', text)

    text = sub(c, r"\1a", text)
    text = sub(f"a{v}", r"\1", text)
    text = sub(rf"{no_virama}{n}{can_drop}a ", r"\1\2\3 ", text)  # ending
    text = sub(rf"{virama}{n}{final_can_drop}a ", r"\1\2\3 ", text)  # ending
    pattern = rf"{no_virama}{n}{can_drop}a{c}{no_virama}"
    while re.search(rf"(.*){pattern}", text):
        text = sub(rf"(.*){pattern}", r"\1\2\3\4\5\6", text)

    text = _sub_with_dict(nukta, conv, text)
    text = _sub_with_dict(r".", conv, text)

    for key, val in nasal_assim.items():
        text = sub(rf"([aeiou])ṃ({key})", rf"\1{val}\2", text)

    text = sub(r"([aiueēoāīū])ṃ", r"\1̃", text)
    text = sub(r"ː(.)", r"\1\1", text)
    text = sub(r" $", "", text)
    text = sub("ā̃tar", "āntar", text)
    text = sub("OM", "oṃ", text)
    text = sub(r"a*\*a*", "a", text)

    return unicodedata.normalize("NFC", text)


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:gu-translit/testcases&oldid=50056094

    >>> transliterate("રુગ્ણાલય")
    'rugṇālya'
    >>> transliterate("અતિવલય")
    'ativalya'
    >>> transliterate("ક્ષમા")
    'kṣamā'
    >>> transliterate("ગોળો")
    'goḷo'
    >>> transliterate("ગુજરાતી")
    'gujrātī'
    >>> transliterate("બત્તી")
    'battī'
    >>> transliterate("ઉંદર")
    'undar'
    >>> transliterate("એરું")
    'erũ'
    >>> transliterate("હ્યત઼્")
    'hyat̰'
    >>> transliterate("સંપત્તિ")
    'sampatti'
    >>> transliterate("જિંદગી")
    'jindgī'
    >>> transliterate("સંન્યાસી")
    'sannyāsī'
    >>> transliterate("પૂછવું")
    'pūchvũ'
    >>> transliterate("છોકરું")
    'chokrũ'
    >>> transliterate("ઊંચાં")
    'ū̃cā̃'
    >>> transliterate("ખડબચડું")
    'khaḍbacḍũ'
    >>> transliterate("સમજાવવું")
    'samjāvvũ'
    >>> transliterate("વાંકું")
    'vā̃kũ'
    >>> transliterate("બળજબરી")
    'baḷjabrī'
    >>> transliterate("વર્તવું")
    'vartavũ'
    >>> transliterate("એંસી")
    'ẽsī'
    >>> transliterate("ઇચ્છવું")
    'icchavũ'
    >>> transliterate("વિદુગ્ધધુ")
    'vidugdhadhu'
    >>> transliterate("આંતર")
    'āntar'
    >>> transliterate("અતિઘણું")
    'atighṇũ'
    >>> transliterate("ઉદાહરણ")
    'udāhraṇ'
    >>> transliterate("અતિશયોક્તિ")
    'atiśyokti'
    >>> transliterate("કેળવણી")
    'keḷvaṇī'
    >>> transliterate("ચકચકિત")
    'cakackit'
    >>> transliterate("દસ્તાવેજીકરણ")
    'dastāvejīkraṇ'
    >>> transliterate("જાળવવું")
    'jāḷvavũ'
    >>> transliterate("ગઈ")
    'gaī'
    """
    return tr(text)
