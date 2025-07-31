"""
Python conversion of the bn-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:bn-translit

Current version from 2025-07-12 09:25
  - https://en.wiktionary.org/w/index.php?title=Module:bn-translit&oldid=85519336
"""

import re
import unicodedata

_char: dict[str, str] = {
    # consonants
    "ক": "k",
    "খ": "kh",
    "গ": "g",
    "ঘ": "gh",
    "ঙ": "ṅ",
    "চ": "c",
    "ছ": "ch",
    "জ": "j",
    "ঝ": "jh",
    "ঞ": "ñ",
    "ট": "ṭ",
    "ঠ": "ṭh",
    "ড": "ḍ",
    "ঢ": "ḍh",
    "ণ": "ṇ",
    "ত": "t",
    "থ": "th",
    "দ": "d",
    "ধ": "dh",
    "ন": "n",
    "প": "p",
    "ফ": "ph",
    "ব": "b",
    "ভ": "bh",
    "ম": "m",
    "য": "j",
    "র": "r",
    "ল": "l",
    "শ": "ś",
    "ষ": "ṣ",
    "স": "s",
    "হ": "h",
    "ড়": "ṛ",
    "ঢ়": "ṛh",
    "য়": "ẏ",
    # vowel diacritics
    "ি": "i",
    "ু": "u",
    "ৃ": "ri",
    "ে": "e",
    "ো": "ō",
    "া": "a",
    "ী": "i",
    "ূ": "u",
    "ৈ": "ōi",
    "ৌ": "ōu",
    # archaic vowel diacritics
    "ৄ": "ri",
    "ৢ": "li",
    "ৣ": "li",
    # visarga
    "ঃ": "ḥ",
    # vowel signs
    "অ": "o",
    "ই": "i",
    "উ": "u",
    "ঋ": "ri",
    "এ": "e",
    "ও": "ō",
    "আ": "a",
    "ঈ": "i",
    "ঊ": "u",
    "ঐ": "ōi",
    "ঔ": "ōu",
    # archaic vowel signs
    "ৠ": "ri",
    "ঌ": "li",
    "ৡ": "li",
    # virama
    "্": "",
    # chandrabindu
    "ঁ": "̃",
    # avagraha
    "ঽ": "’",
    # anusvara
    "ং": "ṅ",
    # khandata
    "ৎ": "t",
    # numerals
    "০": "0",
    "১": "1",
    "২": "2",
    "৩": "3",
    "৪": "4",
    "৫": "5",
    "৬": "6",
    "৭": "7",
    "৮": "8",
    "৯": "9",
    # punctuation
    "।": ".",
}

_vowel = "oা-ৌ’"
_vowel_sign = "অ-ঔ"
_c = r"[কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়]"
_cc = rf"়?{_c}"
_v = rf"[{_vowel}{_vowel_sign}o]"
_syncope_pattern = rf"({_v}{_cc}{_v}{_cc})o({_cc}ঁ?{_v})"
_deaspirate = r"[কগচজটডতদপব]"


def tr(text: str) -> str:
    sub = re.sub

    text = sub(rf"({_c})ও", r"\1্ও", text)
    text = sub(rf"^({_c})্ও", r"\1ও", text)
    text = sub(rf"({_c})্‌({_c})$", r"\1্\2্", text)
    text = sub(rf"({_c})্‌({_c}) ", r"\1্\2্ ", text)
    text = sub(rf"({_v})ঞ({_v})", r"\1̃\2", text)
    text = sub(rf"({_c}়?)([{_vowel}’?্]?)", lambda m: m[1] + (m[2] or "o"), text)

    for word in re.findall(r"[ঁ-৽o’]+", text):
        orig_word = word
        word = word[::-1]
        word = sub(rf"^o(়?{_c})(ঁ?{_v})", r"\1\2", word)
        while re.search(_syncope_pattern, word):
            word = sub(_syncope_pattern, r"\1\2", word)
        text = text.replace(orig_word, word[::-1], 1)

    text = sub(f"({_deaspirate})হ", r"\1'h", text)
    text = text.replace("্ম", "ṃ")
    text = text.replace("্য", "y")
    text = text.replace("্ব", "v")
    text = sub(r"িত$", "ito", text)
    text = text.replace("িত ", "ito ")
    text = sub(r"ৃত$", "rito", text)
    text = text.replace("ৃত ", "rito ")
    text = sub(r"িব$", "ibo", text)
    text = text.replace("িব ", "ibo ")
    text = sub(r"র্চ$", "র্চ্‌", text)
    text = text.replace("র্চ ", "র্চ্‌ ")
    text = sub(r"ছিল$", "chilo", text)
    text = text.replace("ছিল ", "chilo ")
    text = sub(r"র([মফ])o", r"রo\1", text)
    text = sub(f"({_cc})o([অআ])", r"\1\2", text)
    text = sub(f"({_cc})ও", r"\1oō", text)
    text = sub(r".[়’]?", lambda m: _char.get(m[0], m[0]), text)
    text = sub(r".", lambda m: _char.get(m[0], m[0]), text)
    v_Latn = r"[oaiueō]̃?"
    c_Latn = r"[bcdḍghjklmṃnṇprsśṣtṭvẇyẏ]"
    consonants_no_h = r"[bcdgjklmnpsśtṭḍ]"
    text = sub(f"({v_Latn})bo([bdps])({v_Latn})", r"\1b\2\3", text)
    text = sub(f"({v_Latn})cho([bpt])({v_Latn})", r"\1ch\2\3", text)
    text = sub(f"({v_Latn})do([bp])({v_Latn})", r"\1d\2\3", text)
    text = sub(f"({v_Latn})dho([bp])({v_Latn})", r"\1dh\2\3", text)
    text = sub(f"({v_Latn})go([bpr])({v_Latn})", r"\1g\2\3", text)
    text = sub(f"({v_Latn})jo([bpr])({v_Latn})", r"\1j\2\3", text)
    text = sub(f"({v_Latn})ko([bmprsśtṭ])({v_Latn})", r"\1k\2\3", text)
    text = sub(f"({v_Latn})kho([bmpt])({v_Latn})", r"\1kh\2\3", text)
    text = sub(f"({v_Latn})lo([bdp]h?)({v_Latn})", r"\1l\2\3", text)
    text = sub(f"({v_Latn})lo([dp]v)({v_Latn})", r"\1l\2\3", text)
    text = sub(f"({v_Latn})mo([bckprṛ])({v_Latn})", r"\1m\2\3", text)
    text = sub(f"({v_Latn})no([bcglpṭ]?)({v_Latn})", r"\1n\2\3", text)
    text = sub(f"({v_Latn})ṅo([blmp]h?)({v_Latn})", r"\1ṅ\2\3", text)
    text = sub(f"({v_Latn})po([bcp])({v_Latn})", r"\1p\2\3", text)
    text = sub(f"({v_Latn})pho([bdjmtpz]?)({v_Latn})", r"\1ph\2\3", text)
    text = sub(f"({v_Latn})ro([bcdghjklsṣś]h?)({v_Latn})", r"\1r\2\3", text)
    text = sub(f"({v_Latn})ṣo([bjlmp])({v_Latn})", r"\1ṣ\2\3", text)
    text = sub(f"({v_Latn})śo([bgjlmp])({v_Latn})", r"\1ś\2\3", text)
    text = sub(f"({v_Latn})so([bjlmp])({v_Latn})", r"\1s\2\3", text)
    text = sub(f"({v_Latn})ṭo([bgkp])({v_Latn})", r"\1ṭ\2\3", text)
    text = sub(f"({v_Latn})ẏo([j])({v_Latn})", r"\1ẏ\2\3", text)
    text = sub(r"([cr])ch$", r"\1cho", text)
    text = sub(r"([cr])ch ", r"\1cho ", text)
    text = sub(r"([cr])ch(\?)", r"\1cho\2", text)
    text = sub(rf"apon({v_Latn})", r"apn\1", text)
    text = text.replace("arbi", "arobi")
    text = sub(r"goñjo$", "gonj", text)
    text = text.replace("goñjo ", "gonj ")
    text = text.replace("got", "goto")
    text = text.replace("hojjo", "hojj")
    text = sub(r"ikta$", "ikota", text)
    text = sub("ikta ", "ikota ", text)
    text = sub(r"iẏ$", "iẏo", text)
    text = text.replace("iẏ ", "iẏo ")
    text = sub(r"ken$", "keno", text)
    text = text.replace("ken ", "keno ")
    text = sub(r"ken(\?)", r"keno\1", text)
    text = text.replace("korob", "korbo")
    text = sub(r"sṭo$", "sṭ", text)
    text = text.replace("sṭo ", "sṭ ")
    text = sub(f"ajon({v_Latn})", r"ajn", text)
    text = sub(f"({v_Latn})koṭr({v_Latn})", r"\1kṭr\2", text)
    text = sub(f"({v_Latn})khost({v_Latn})", r"\1khst\2", text)
    text = sub(f"({v_Latn})jost({v_Latn})", r"\1jst\2", text)
    text = sub(f"({v_Latn})no({c_Latn}h?)({c_Latn}h?)({v_Latn})", r"\1n\2\3\4", text)
    text = sub(f"({v_Latn})rkoṭ({v_Latn})", r"\1rkṭ\2", text)
    text = sub(f"({v_Latn})ṣdh({v_Latn})", r"\1ṣodh\2", text)
    text = sub(f"({v_Latn})sm({v_Latn})", r"\1śom\2", text)
    text = sub(f"^up({c_Latn})", r"upo\1", text)
    text = sub(f" up({c_Latn})", r" upo\1", text)
    text = sub(f"({c_Latn})oṭa$", r"\1ṭa", text)
    text = sub(f"({c_Latn})oṭa ", r"\1ṭa ", text)
    text = sub(f"({c_Latn})oṭi$", r"\1ṭi", text)
    text = sub(f"({c_Latn})oṭi ", r"\1ṭi ", text)
    text = sub(r"([bgmr])v", r"\1b", text)
    text = text.replace("udv", "udb")
    text = text.replace("ttv", "tt")
    text = text.replace("jjv", "jj")
    text = sub(r"^[sś]v", "ś", text)
    text = sub(r"([sś])v", "śś", text)
    text = sub(rf"^({consonants_no_h}h?)v", r"\1", text)
    text = sub(rf" ({consonants_no_h}h?)v", r" \1", text)
    text = sub(rf"([lṅ])({consonants_no_h}h?)v", r"\1\2", text)
    text = sub(rf"({consonants_no_h})v", r"\1\1", text)
    text = sub(rf"({consonants_no_h})hv", r"\1\1h", text)
    text = text.replace("ahv", "aubh")
    text = text.replace("ihv", "iubh")
    text = text.replace("hv", "hb")
    text = sub(r"^kṣ", "kh", text)
    text = text.replace(" kṣ", " kh")
    text = text.replace("ṅkṣ", "ṅkh")
    text = text.replace("kṣ", "kkh")
    text = text.replace("kkhṃ", "kkh")
    text = sub(rf"^([ṣs])ṃ({v_Latn})", r"ś\2̃", text)
    text = sub(rf"([ṣs])ṃ({v_Latn})", r"śś\2̃", text)
    text = sub(r"^tṃ", "t", text)
    text = text.replace("tṃ", "tt")
    text = text.replace("ṃ", "m")
    text = text.replace("ṣ", "ś")
    text = text.replace("ḥkh", "kkh")
    text = sub(r"([ln])ḍo$", r"\1ḍ", text)
    text = sub(r"([ln])nḍo ", r"\1ḍ ", text)
    text = sub(r"rko$", "rk", text)
    text = text.replace("rko ", "rk ")
    text = sub(rf"({v_Latn})h$", r"\1ho", text)
    text = sub(rf"({v_Latn})h ", r"\1ho ", text)
    text = sub(r"([glś])aho$", r"\1ah", text)
    text = sub(r"([glś])aho ", r"\1ah ", text)
    text = text.replace("ṇn", "ṇon")
    text = text.replace("ṇ", "n")
    text = sub(r"^eya", "ê", text)
    text = text.replace(" eya", " ê")
    text = sub(r"^oya", "ê", text)
    text = text.replace(" oya", " ê")
    text = sub(rf"^({consonants_no_h}h?)ya", r"\1ê", text)
    text = sub(rf" ({consonants_no_h}h?)ya", r" \1ê", text)
    text = sub(rf"^({consonants_no_h}h?)({consonants_no_h}h?)ya", r"\1\2ê", text)
    text = sub(rf" ({consonants_no_h}h?)({consonants_no_h}h?)ya", r" \1\2ê", text)
    text = sub(r"^hya", "hê", text)
    text = sub(r"yal$", "êl", text)
    text = sub(r"^jñan", "gên", text)
    text = text.replace(" jñan", " gên")
    text = text.replace("jñan", "ggên")
    text = text.replace("ñ", "n")
    text = text.replace("yanḍ", "ênḍ")
    text = sub(rf"^({consonants_no_h}h?)yo", r"\1ê", text)
    text = sub(rf" ({consonants_no_h}h?)yo", r" \1ê", text)
    text = sub(rf"^({consonants_no_h}h?)y", r"\1", text)
    text = sub(rf"ṅ({consonants_no_h}h?)y", r"ṅ\1", text)
    text = sub(rf"({consonants_no_h})y", r"\1\1", text)
    text = sub(rf"({consonants_no_h})hy", r"\1\1h", text)
    text = sub(r"^hy", "h", text)
    text = text.replace(" hy", " h")
    text = text.replace("hy", "jjh")
    text = text.replace("ry", "rj")
    text = sub(r"ẏo([gklmn])([aeiīōuū])", r"ẏ\1\2", text)
    text = text.replace("ẏoō", "ẏō")
    text = sub(r"oō$", "ō", text)
    text = sub(rf"([ei])ẏ({_c})", r"\1ẏo\2", text)
    text = sub(r"([ei])ẏ$", r"\1ẏo", text)
    text = sub(rf"s({v_Latn})$", r"ś\1", text)
    text = sub(rf"s({v_Latn}) ", r"ś\1 ", text)
    text = sub(rf"s({v_Latn})", r"ŝ\1", text)
    text = sub(r"([ai])s$", r"\1ś", text)
    text = sub(r"([ai])s ", r"\1ś ", text)
    text = sub(r"os$", "oŝ", text)
    text = text.replace("os ", "oŝ ")
    text = sub(rf"^({c_Latn})oŝ$", r"\1os", text)
    text = sub(rf" ({c_Latn})oŝ$", r" \1os", text)
    text = sub(rf"^({c_Latn})oŝ ", r"\1os ", text)
    text = sub(rf"^ŝe({c_Latn})$", r"^se\1", text)
    text = sub(rf" ŝe({c_Latn})$", r" se\1", text)
    text = sub(rf"^ŝe({c_Latn}) ", r"^se\1 ", text)
    text = sub(rf" ŝe({c_Latn}) ", r" se\1 ", text)
    text = text.replace("ŝalam", "salam")
    text = text.replace("ŝ", "ś")
    text = text.replace("śl", "sl")
    text = text.replace("śr", "sr")
    text = text.replace("sp", "śp")
    text = sub(r"^śp", "sp", text)
    text = text.replace(" śp", " sp")
    text = sub(r"śṭh$", "śṭho", text)
    text = sub(r"^([kg]h?)([dḍtṭ])", r"\1o\2", text)
    text = sub(rf"^({c_Latn})([aou])b$", r"\1\2bo", text)
    text = sub(rf"^({c_Latn})([aou])b ", r"\1\2bo ", text)
    text = sub(r"^([bcdḍghjkmṃnṇprsśṣtṭẇẏ])([aou])bh$", r"\1\2bho", text)
    text = sub(r"^([bcdḍghjkmṃnṇprsśṣtṭẇẏ])([aou])bh ", r"\1\2bho ", text)
    text = sub(r"lona$", "lna", text)
    text = sub(r"nola$", "nla", text)
    text = text.replace("ōẏ", "ōẇ")
    text = text.replace("ō̃ẏ", "ō̃ẇ")
    text = sub(r"ōẇ$", "ōẏ", text)
    text = text.replace("ōẇ ", "ōẏ ")
    text = text.replace("oo", "o")
    return "" if re.search(r"[ঁ-৽]", text) else unicodedata.normalize("NFC", text)


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:bn-translit/testcases&oldid=72714083

    >>> transliterate("ত্বক")
    'tok'
    >>> transliterate("ঠ্যাং")
    'ṭhêṅ'
    >>> transliterate("মানচিত্র")
    'mancitro'
    >>> transliterate("সূত্র")
    'śutro'
    >>> transliterate("মই")
    'moi'
    >>> transliterate("কারখানা")
    'karkhana'
    >>> transliterate("দুঃখিত")
    'dukkhito'
    >>> transliterate("লেবানন")
    'lebanon'
    >>> transliterate("যন্ত্রমানব")
    'jontromanob'
    >>> transliterate("প্রতিবেশী")
    'protibeśi'
    >>> transliterate("রচনা")
    'rocona'
    >>> transliterate("অংগুষ্ঠানা")
    'oṅguśṭhana'
    >>> transliterate("পানি")
    'pani'
    >>> transliterate("আগুন")
    'agun'
    >>> transliterate("পশ্চিমবঙ্গ")
    'pościmboṅgo'
    >>> transliterate("বাংলা")
    'baṅla'
    >>> transliterate("সর্বনাম")
    'śorbonam'
    >>> transliterate("ইতিহাস")
    'itihaś'
    >>> transliterate("শুভ")
    'śubho'
    >>> transliterate("শুদ্ধ")
    'śuddho'
    >>> transliterate("জল")
    'jol'
    >>> transliterate("তদ্ভব")
    'todbhob'
    >>> transliterate("তৎসম")
    'totśom'
    >>> transliterate("পশ্চিম")
    'pościm'
    >>> transliterate("পছন্দ")
    'pochondo'
    >>> transliterate("জন্মদিন")
    'jonmodin'
    >>> transliterate("অসভ্য")
    'ośobbho'
    >>> transliterate("প্রাণ")
    'pran'
    >>> transliterate("ক্ষুদ্র")
    'khudro'
    >>> transliterate("অক্ষর")
    'okkhor'
    >>> transliterate("জ্ঞান")
    'gên'
    >>> transliterate("বিজ্ঞান")
    'biggên'
    >>> transliterate("ওয়াদা")
    'ōẇada'
    >>> transliterate("বর্ষ")
    'borśo'
    >>> transliterate("আখতার")
    'akhtar'
    >>> transliterate("পঙ্কজ")
    'poṅkoj'
    """
    return tr(text)
