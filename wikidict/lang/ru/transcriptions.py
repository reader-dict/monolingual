"""
Python conversion of the "ru-pron" module.

Links:
  - https://ru.wiktionary.org/wiki/Модуль:ru-pron

Current version from 2020-07-21T09:24:00
  - https://ru.wiktionary.org/w/index.php?title=Модуль:ru-pron&oldid=11489162
"""

import re
import unicodedata
from collections.abc import Callable

import regex

U = chr
AC = U(0x0301)  # acute =  ́
GR = U(0x0300)  # grave =  ̀
CFLEX = U(0x0302)  # circumflex =  ̂
DUBGR = U(0x030F)  # double grave =  ̏
DOTABOVE = U(0x0307)  # dot above =  ̇
DOTBELOW = U(0x0323)  # dot below =  ̣
BREVE = U(0x0306)  # breve  ̆
DIA = U(0x0308)  # diaeresis =  ̈
CARON = U(0x030C)  # caron  ̌
TEMP_G = U(0xFFF1)  # substitute to preserve g from changing to v

accent = f"{AC}{GR}{DIA}{BREVE}{CARON}"
opt_accent = f"[{accent}]*"
composed_grave_vowel = "ѐЀѝЍ"
vowel_no_jo = f"аеиоуяэыюіѣѵАЕИОУЯЭЫЮІѢѴ{composed_grave_vowel}"
vowel = f"{vowel_no_jo}ёЁ"

vow = "aeiouyɛəäạëöü"
ipa_vow = f"{vow}ɐɪʊɨæɵʉ"
vowels = f"[{vow}]"
vowels_c = f"({vowels})"
acc = f"{AC}{GR}{CFLEX}{DOTABOVE}{DOTBELOW}"
accents = f"[{acc}]"
consonants = r"[^аеиоуяэыюіѣѵүАЕИОУЯЭЫЮІѢѴҮѐЀѝЍёЁAEIOUYĚƐaeiouyěɛЪЬъьʹʺ]"

perm_syl_onset = {
    "bd",
    "bj",
    "bz",
    "bl",
    "br",
    "vd",
    "vz",
    "vzv",
    "vzd",
    "vzr",
    "vl",
    "vm",
    "vn",
    "vr",
    "gl",
    "gn",
    "gr",
    "dž",
    "dn",
    "dv",
    "dl",
    "dr",
    "dj",
    "žg",
    "žd",
    "žm",
    "žn",
    "žr",
    "zb",
    "zd",
    "zl",
    "zm",
    "zn",
    "zv",
    "zr",
    "kv",
    "kl",
    "kn",
    "kr",
    "ks",
    "kt",
    "ml",
    "mn",
    "nr",
    "pl",
    "pn",
    "pr",
    "ps",
    "pt",
    "pš",
    "stv",
    "str",
    "sp",
    "st",
    "stl",
    "sk",
    "skv",
    "skl",
    "skr",
    "sl",
    "sf",
    "sx",
    "sc",
    "sm",
    "sn",
    "sv",
    "sj",
    "spl",
    "spr",
    "sr",
    "tv",
    "tk",
    "tkn",
    "tl",
    "tr",
    "fk",
    "fl",
    "fr",
    "fs",
    "fsx",
    "fsp",
    "fspl",
    "ft",
    "fš",
    "xv",
    "xl",
    "xm",
    "xn",
    "xr",
    "cv",
    "čv",
    "čl",
    "čm",
    "čr",
    "čt",
    "šv",
    "šk",
    "škv",
    "šl",
    "šm",
    "šn",
    "šp",
    "šr",
    "št",
    "šč",
}


def sub_repeatedly(pattern: str, repl: str, text: str) -> str:
    while True:
        new_text = re.sub(pattern, repl, text, count=1)
        if new_text == text:
            return text
        text = new_text


def translate(text: str, translation: dict[str, str]) -> str:
    return re.compile("|".join(map(re.escape, translation))).sub(lambda m: translation[m[0]], text)


def translit_conv(match: re.Match[str]) -> str:
    return {
        "c": "t͡s",
        "č": "t͡ɕ",
        "ĉ": "t͡ʂ",
        "g": "ɡ",
        "ĝ": "d͡ʐ",
        "ĵ": "d͡z",
        "ǰ": "d͡ʑ",
        "ӂ": "ʑ",
        "š": "ʂ",
        "ž": "ʐ",
        "ɕ": "ɕ",
    }[match[0]]


def translit_conv_j(match: re.Match[str]) -> str:
    return {"cʲ": "tʲ͡sʲ", "ĵʲ": "dʲ͡zʲ"}[match[0]]


allophones = {
    "a": "aɐə",
    "e": "eɪɪ",
    "i": "iɪɪ",
    "o": "oɐə",
    "u": "uʊʊ",
    "y": "ɨɨɨ",
    "ɛ": "ɛɛɛ",
    "ä": "aɪɪ",
    "ạ": "aɐə",
    "ë": "eɪɪ",
    "ö": "ɵɪɪ",
    "ü": "uʊʊ",
    "ə": "əəə",
}
devoicing = {
    "b": "p",
    "d": "t",
    "g": "k",
    "z": "s",
    "v": "f",
    "ž": "š",
    "ɣ": "x",
    "ĵ": "c",
    "ǰ": "č",
    "ĝ": "ĉ",
    "ӂ": "ɕ",
}
voicing = {
    "p": "b",
    "t": "d",
    "k": "g",
    "s": "z",
    "f": "v",
    "š": "ž",
    "c": "ĵ",
    "č": "ǰ",
    "ĉ": "ĝ",
    "x": "ɣ",
    "ɕ": "ӂ",
}
iotating = {"a": "ä", "e": "ë", "o": "ö", "u": "ü"}
retracting = {"e": "ɛ", "i": "y"}
fronting = {"a": "æ", "u": "ʉ", "ʊ": "ʉ"}

geminate_pref = {
    r"be[szšž]ː": r"be[sz]",
    r"[vf]ː": "v",
    r"vo[szšž]ː": r"vo[sz]",
    r"i[szšž]ː": r"i[sz]",
    "kontrː": "kontr",
    "superː": "super",
    r"tran[szšž]ː": "trans",
    r"na[tdcč]ː": "nad",
    r"ni[szšž]ː": r"ni[sz]",
    r"o[tdcč]ː": "ot",
    r"o[bp]ː": "ob",
    r"obe[szšž]ː": r"obe[sz]",
    r"po[tdcč]ː": "pod",
    r"pre[tdcč]ː": "pred",
    r"ra[szšž]ː": r"ra[sz]",
    r"[szšž]ː": r"[szšž]",
    r"su[bp]ː": "sub",
    r"me[žš]ː": "mež",
    r"če?re[szšž]ː": r"če?re[sz]",
    r"predra[szšž]ː": r"predra[sz]",
    r"bezra[szšž]ː": r"bezra[sz]",
    r"nara[szšž]ː": r"nara[sz]",
    r"vra[szšž]ː": r"vra[sz]",
    r"dora[szšž]ː": r"dora[sz]",
}

phon_respellings: dict[str, str | Callable[[re.Match[str]], str]] = {
    rf"([žšc])e([^{acc}⁀])": r"\1y\2",
    r"y(́?)je⁀": r"y\1i⁀",
    r"([gkx])i(́?)je⁀": r"\1i\2i⁀",
    r"([vdntžš])nije⁀": r"\1nii⁀",
    r"ščije(sja?)⁀": r"ščii\1⁀",
    r"všije(sja?)⁀": r"všii\1⁀",
    "h": "ɣ",
    "šč": "ɕː",
    "čš": "tš",
    r"́tʹ?sja⁀": "́cca⁀",
    r"([^́])tʹ?sja⁀": r"\1ca⁀",
    r"n[dt]sk": r"n(t)sk",
    r"s[dt]sk": "sck",
    "cz": "/cz",
    "čž": "/ĝž",
    r"[dt](ʹ?[ ‿⁀/]+)s": r"c\1s",
    r"[dt](ʹ?[ ‿⁀/]+)z": r"ĵ\1z",
    rf"[dt](ʹ?)s(j?{vowels})": r"c\1s\2",
    rf"[dt](ʹ?)z(j?{vowels})": r"ĵ\1z\2",
    r"[dt]ʹs": "cʹs",
    r"[dt]ʹz": "ĵʹz",
    rf"(⁀o{accents}?)t([sz])": lambda m: m[1] + {"s": "cs", "z": "ĵz"}[m[2]],
    rf"(⁀po{accents}?)d([sz])": lambda m: m[1] + {"s": "cs", "z": "ĵz"}[m[2]],
    r"[dt]s": "c",
    r"[dt]z": "ĵ",
    r"[dt](ʹ?[ \-‿⁀/]*)š": r"ĉ\1š",
    r"[dt](ʹ?[ \-‿⁀/]*)ž": r"ĝ\1ž",
    "ĉʹ": "č",
    "ĝʹ": "ǰ",
    r"[cdt]sč": "čɕː",
    "ɕːč": "ɕč",
    r"[zž]č": "ɕː",
    r"[szšž]ɕː?": "ɕː",
    rf"sčjo({accents}?)t": r"ɕːjo\1t",
    rf"sče({accents}?)t": r"ɕːe\1t",
    rf"sčja({accents}?)s": r"ɕːja\1s",
    "sč": "ɕč",
    r"[sz][dt]c": "sc",
    r"([rn])[dt]([cč])": r"\1\2",
    rf"dca({accents}?)t": r"c(c)a\1t",
    rf"[dt]([cč])({vowels})": r"\1ˑ\2",
    r"[dt]([cč])": r"\1\1",
    r"n[dt]ɕ": "nɕ",
    r"[zs]ʹ?([ ‿⁀/]*[ɕč])": r"ɕ\1",
    "ɕɕː": "ɕː",
    r"[cdt]ʹ?([ ‿⁀/]*)ɕ": r"č\1ɕ",
    r"[zs]([ ‿⁀/]*)š": r"š\1š",
    r"[zs]([ ‿⁀/]*)ž": r"ž\1ž",
    r"[zs]ʹ([ ‿⁀/]*)š": r"ɕ\1š",
    r"[zs]ʹ([ ‿⁀/]*)ž": r"ӂ\1ž",
    "sverxi": "sverxy",
    "stʹd": "zd",
    "tʹd": "dd",
    r"([ns])[dt]g": r"\1g",
    "zdn": "zn",
    "lnc": "nc",
    r"[sz]tn": "sn",
    rf"[sz]tli({accents}?)v([^š])": r"sli\1v\2",
    r"čju(́?)vstv": r"ču\1stv",
    r"zdra(́?)vstv": r"zdra\1stv",
    "lvstv": "lstv",
    r"([mnpbtdkgfvszxɣrlšžcĵĉĝ])⁀‿⁀i": r"\1⁀‿⁀y",
}

cons_assim_palatal = {
    "compulsory": {"ntʲ", "ndʲ", "xkʲ", "csʲ", "ĵzʲ", "ncʲ", "nĵʲ"},
    "optional": {"nsʲ", "nzʲ", "mpʲ", "mbʲ", "mfʲ", "fmʲ"},
}

accentless = {
    "pre": {
        "bez",
        "bliz",
        "v",
        "vedʹ",
        "vo",
        "da",
        "do",
        "za",
        "iz",
        "iz-pod",
        "iz-za",
        "izo",
        "k",
        "ko",
        "mež",
        "na",
        "nad",
        "nado",
        "ne",
        "ni",
        "ob",
        "obo",
        "ot",
        "oto",
        "pered",
        "peredo",
        "po",
        "pod",
        "podo",
        "pred",
        "predo",
        "pri",
        "pro",
        "s",
        "so",
        "u",
        "čerez",
    },
    "prespace": {"a", "o"},
    "post": {"by", "b", "ž", "že", "li", "libo", "lʹ", "ka", "nibudʹ", "tka"},
    "posthyphen": {"to"},
}

final_e: dict[str, dict[str, str] | str] = {
    "def": {"oe": "ə", "ve": "ə", "je": "ə", "softpaired": "ɪ", "hardsib": "ə", "softsib": "ɪ"},
    "noun": {"oe": "ə", "ve": "e", "je": "e", "softpaired": "e", "hardsib": "ə", "softsib": "e"},
    "n": "noun",
    "pre": {"oe": "e", "ve": "e", "softpaired": "e", "hardsib": "y", "softsib": "e"},
    "dat": "pre",
    "voc": "mid",
    "nnp": {"softpaired": "e"},
    "inv": "mid",
    "adj": {"oe": "ə", "ve": "e", "je": "ə"},
    "a": "adj",
    "com": {"ve": "e", "hardsib": "y", "softsib": "e"},
    "c": "com",
    "adv": {"softpaired": "e", "hardsib": "y", "softsib": "e"},
    "p": "adv",
    "verb": {"softpaired": "e"},
    "v": "verb",
    "vb": "verb",
    "pro": {"oe": "i", "ve": "i"},
    "num": "mid",
    "pref": "high",
    "high": {"oe": "i", "ve": "i", "je": "i", "softpaired": "i", "hardsib": "y", "softsib": "i"},
    "hi": "high",
    "mid": {"oe": "e", "ve": "e", "je": "e", "softpaired": "e", "hardsib": "y", "softsib": "e"},
    "low": {"oe": "ə", "ve": "ə", "je": "ə", "softpaired": "ə", "hardsib": "ə", "softsib": "ə"},
    "lo": "low",
    "schwa": "low",
}

recomposer = {
    f"и{BREVE}": "й",
    f"И{BREVE}": "Й",
    f"е{DIA}": "ё",
    f"Е{DIA}": "Ё",
    f"e{CARON}": "ě",
    f"E{CARON}": "Ě",
    f"c{CARON}": "č",
    f"C{CARON}": "Č",
    f"s{CARON}": "š",
    f"S{CARON}": "Š",
    f"z{CARON}": "ž",
    f"Z{CARON}": "Ž",
    f"ж{BREVE}": "ӂ",
    f"Ж{BREVE}": "Ӂ",
    f"j{CFLEX}": "ĵ",
    f"J{CFLEX}": "Ĵ",
    f"j{CARON}": "ǰ",
    f"ʒ{CARON}": "ǯ",
    f"Ʒ{CARON}": "Ǯ",
}

tab = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "Je",
    "Ё": "Jó",
    "Ж": "Ž",
    "З": "Z",
    "И": "I",
    "Й": "J",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "X",
    "Ц": "C",
    "Ч": "Č",
    "Ш": "Š",
    "Щ": "Šč",
    "Ъ": "ʺ",
    "Ы": "Y",
    "Ь": "ʹ",
    "Э": "E",
    "Ю": "Ju",
    "Я": "Ja",
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "je",
    "ё": "jó",
    "ж": "ž",
    "з": "z",
    "и": "i",
    "й": "j",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "x",
    "ц": "c",
    "ч": "č",
    "ш": "š",
    "щ": "šč",
    "ъ": "ʺ",
    "ы": "y",
    "ь": "ʹ",
    "э": "e",
    "ю": "ju",
    "я": "ja",
    "«": "“",
    "»": "”",
    "І": "I",
    "і": "i",
    "Ѳ": "F",
    "ѳ": "f",
    "Ѣ": "Jě",
    "ѣ": "jě",
    "Ѵ": "I",
    "ѵ": "i",
}

decompose_grave_map = {
    "ѐ": f"е{GR}",
    "Ѐ": f"Е{GR}",
    "ѝ": f"и{GR}",
    "Ѝ": f"И{GR}",
}


def phon_respelling(text: str) -> str:
    text = re.sub(rf"[{CFLEX}{DUBGR}{DOTABOVE}{DOTBELOW}]", "", text)
    return text.replace("‿", " ")


def adj_respelling(text: str) -> str:
    sub = re.sub
    text = sub(rf"(.[аое]{AC}?)го({AC}?)$", r"\1во\2", text)
    text = sub(rf"(.[аое]{AC}?)го({AC}?ся)$", r"\1во\2", text)
    text = sub(rf"(.[аое]{AC}?)го{AC}?[ \-])", r"\1во\2", text)
    return sub(rf"(.[аое]{AC}?)го({AC}?ся[ \-])", r"\1во\2", text)


def decompose(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return re.compile(rf"(.[{BREVE}{DIA}{CARON}])").sub(lambda match: recomposer.get(match[0], match[0]), text)


map_to_plain_e_map = {"Е": "E", "е": "e", "Ѣ": "Ě", "ѣ": "ě", "Э": "Ɛ", "э": "ɛ"}


def is_monosyllabic(word: str) -> bool:
    return not re.search(rf"{vowels}.*{vowels}", word)


def tr_after_fixes(text: str, include_monosyllabic_jo_accent: bool) -> str:
    sub = re.sub

    text = sub(r"[Ъъ]$", "", text)
    text = sub(r"^[Ъъ](.+)", r"\1", text)

    if re.search(r"[Ёё]", text):
        if not include_monosyllabic_jo_accent and is_monosyllabic(text):
            text = sub(r"([жшчщЖШЧЩ])ё", r"\1o", text)
            text = text.replace("ё", "jo")
            text = text.replace("Ё", "Jo")
        else:
            text = sub(r"([жшчщЖШЧЩ])ё", r"\1ó", text)
    text = sub(r"([жшЖШ])ю", r"\1u", text)
    if re.search(r"[ЕеѢѣЭэ]", text):
        text = re.compile(r"^(-)([ЕеѢѣЭэ])").sub(lambda m: m[1] + map_to_plain_e_map[m[2]], text)
        text = re.compile(r"(\s-)([ЕеѢѣЭэ])").sub(lambda m: m[1] + map_to_plain_e_map[m[2]], text)
        text = re.compile(rf"({consonants}['()]*)([ЕеѢѣЭэ])").sub(lambda m: m[1] + map_to_plain_e_map[m[2]], text)
    return translate(text, tab)


def apply_tr_fixes(text: str) -> tuple[str, str]:
    # Decompose grave Cyrillic letters before converting е to Latin e/je
    text = translate(text, decompose_grave_map)
    origtext = text

    # Replace endings -го for specific words with TEMP_G to prevent g→v conversion later
    # Patterns now use unicode accent marks and Python regex boundaries
    for pat in [
        r"\b([Мм]но[́̀]?)го\b",
        r"\b([Нн][еа]мно[́̀]?)го\b",
        r"\b([Нн]енамно[́̀]?)го\b",
        r"\b([Дд]о[́̀]?ро)го\b",
        r"\b([Нн]едо[́̀]?ро)го\b",
        r"\b([Зз]адо[́̀]?ро)го\b",
        r"\b([Зз]анедо[́̀]?ро)го\b",
        r"\b([Сс]тро[́̀]?)го\b",
        r"\b([Нн]а[́̀]?стро)го\b",
        r"\b([Нн]естро[́̀]?)го\b",
        r"\b([Уу]бо[́̀]?)го\b",
        r"\b([Пп]оло[́̀]?)го\b",
        r"\b([Дд]линноно[́̀]?)го\b",
        r"\b([Кк]оротконо[́̀]?)го\b",
        r"\b([Кк]ривоно[́̀]?)го\b",
        r"\b([Кк]олчено[́̀]?)го\b",
        r"\b([Оо]тло[́̀]?)го\b",
        r"\b([Пп]е[́̀]?)го\b",
        r"\b([лсЛС]?[Оо][́̀]?)г(о[́̀]?)\b",
        r"\b([Тт]о[́̀]?)го\b",
        r"\b([Лл]е[́̀]?)го\b",
        r"\b([ИиОо])гог(о[́̀]?)\b",
        r"\b([Дд]ие[́̀]?)го\b",
        r"\b([Сс]ло[́̀]?)го\b",
    ]:
        text = re.sub(pat, lambda m: f"{m[1]}{TEMP_G}о", text)

    # Genitive/accusative endings: -ого/-его/-аго → -ово/-ево/-аво (but not for listed exceptions above)
    # Reflexive -ся suffix
    pattern = r"([оеОЕ][́̀]?)([гГ])([оО][́̀]?)"
    reflexive = r"([сС][яЯ][́̀]?)"
    v = {"г": "в", "Г": "В"}
    text = re.sub(rf"{pattern}\b", lambda m: m[1] + v[m[2]] + m[3], text)
    text = re.sub(rf"{pattern}{reflexive}\b", lambda m: m[1] + v[m[2]] + m[3] + m[4], text)

    # сегодня → севодня
    text = re.sub(r"\b([Сс]е)г(о[́̀]?дня)\b", r"\1в\2", text)
    # сегодняшн-
    text = re.sub(r"\b([Сс]е)г(о[́̀]?дняшн)", r"\1в\2", text)

    # Replace TEMP_G back with г after above substitutions
    text = text.replace(TEMP_G, "г")

    # что and derivatives: ч → ш
    text = re.sub(r"\b([Чч])(то[́̀]?)\b", lambda m: {"ч": "ш", "Ч": "Ш"}[m[1]] + m[2], text)
    text = re.sub(r"\b([Чч])(то[́̀]?бы?)\b", lambda m: {"ч": "ш", "Ч": "Ш"}[m[1]] + m[2], text)
    text = re.sub(r"\b([Нн]и)ч(то[́̀]?)\b", r"\1ш\2", text)

    # г → х after certain letters (e.g. мягляк: мяякг → мяях)
    text = re.sub(r"([МмЛл][яеё][́̀]?)г([кч])", r"\1х\2", text)

    return origtext, text


def tr(text: str, lang: None, sc: None, include_monosyllabic_jo_accent: bool) -> str:
    origtext, subbed_text = apply_tr_fixes(text)
    return tr_after_fixes(subbed_text, include_monosyllabic_jo_accent)


def translit(text: str, no_include_monosyllabic_jo_accent: bool) -> str:
    return decompose(tr(text, None, None, not no_include_monosyllabic_jo_accent))


def ipa(text: str, adj: str, gem: str, pos: str) -> str:
    gem = gem[0] if gem else ""
    pos = pos or "def"
    text = text.lower()
    text = text.replace("``", DUBGR)
    text = text.replace("`", GR)
    text = text.replace("@", DOTABOVE)
    text = text.replace("^", CFLEX)
    text = text.replace(DUBGR, CFLEX)
    sub = re.sub
    sub2 = regex.sub
    text = text.replace("э", "ɛ")
    text = sub(rf"([{vowel}]{opt_accent})й([еѐ])", r"\1йй\2", text)
    text = translit(text, True)
    text = text.replace("ě̈", f"jo{AC}")
    text = text.replace("ě", "e")
    text = sub(f"{accents}+({accents})", r"\1", text)
    text = sub(r"\s+", " ", text)
    word = re.split(r"([ \-]+)", text)
    for i in range(len(word)):
        if not (
            (
                word[i] in accentless["pre"]
                or (i < len(word) - 1 and word[i] in accentless["prespace"] and word[i + 1] == " ")
                or (i > 2 and word[i] in accentless["post"])
                or (i > 2 and word[i] in accentless["posthyphen"] and word[i - 1] == "-")
            )
            and len(sub(rf"[^{vow}]", "", word[i])) == 1
            and not re.search(accents, word[i])
            and not (
                i == 3
                and word[2] == "-"
                and word[1] == ""
                or i >= 3
                and word[i - 1] == " -"
                or i == len(word) - 2
                and word[i + 1] == "-"
                and word[i + 2] == ""
                or i <= len(word) - 2
                and word[i + 1] == "- "
            )
        ):
            if (
                i > 2
                and word[i - 2] in accentless["pre"]
                or i > 2
                and word[i - 1] == " "
                and word[i - 2] in accentless["prespace"]
                or i < len(word) - 1
                and word[i + 2] in accentless["post"]
                or i < len(word) - 1
                and word[i + 1] == "-"
                and word[i + 2] in accentless["posthyphen"]
            ):
                word[i] = sub(vowels_c, rf"\1{AC}", word[i])
            else:
                word[i] = sub(vowels_c, rf"\1{CFLEX}", word[i])
    for i in range(len(word)):
        if i < len(word) - 1 and (
            word[i] in accentless["pre"] or word[i] in accentless["prespace"] and word[i + 1] == " "
        ):
            word[i + 1] = "‿"
        elif i > 2 and (word[i] in accentless["post"] or word[i] in accentless["posthyphen"] and word[i - 1] == "-"):
            word[i - 1] = "‿"
    text = sub(r"[\-\s]+", " ", "".join(word))
    text = text.strip()
    text = sub(r"\s*[,–—]\s*", " | ", text)
    text = text.replace(" ", "⁀ ⁀")
    text = "⁀" + text + "⁀"
    text = text.replace("‿", "⁀‿⁀")
    orig_word = text.split(" ")
    text = sub(r"([šž])j([ou])", r"\1\2", text)
    text = sub(r"([čǰӂ])([aou])", r"\1j\2", text)
    text = text.replace("ʹo", "ʹjo")
    text = sub(rf"({vowels}{accents}?o)⁀", rf"\1{CFLEX}⁀", text)
    text = text.replace("jo⁀", f"jo{CFLEX}⁀")
    text = text.replace(DOTABOVE, "")
    text = text.replace(f"ja{DOTBELOW}", "jạ")
    if DOTBELOW in text:
        raise ValueError("Dot-below accent can only be placed on я or palatal а")
    if adj:
        text = sub(rf"(.[aoe]{AC}?)go({AC}?)⁀", r"\1vo\2⁀", text)
        text = sub(rf"(.[aoe]{AC}?)go({AC}?)sja⁀", r"\1vo\2sja⁀", text)
    for pattern, repl in phon_respellings.items():
        if isinstance(repl, str):
            text = sub(pattern, repl, text)
        else:
            text = re.compile(pattern).sub(repl, text)
    # voicing, devoicing
    text = re.compile(r"([bdgvɣzžĝĵǰӂ])(ʹ?⁀)$").sub(lambda m: devoicing[m[1]] + m[2], text)
    text = re.compile(r"([bdgvɣzžĝĵǰӂ])(ʹ?⁀ ⁀[^bdgɣzžĝĵǰӂ])").sub(lambda m: devoicing[m[1]] + m[2], text)
    while True:
        new_text = re.compile(r"([bdgvɣzžĝĵǰӂ])([ ‿⁀ʹːˑ()/]*[ptkfxsščɕcĉ])").sub(lambda m: devoicing[m[1]] + m[2], text)
        new_text = re.compile(r"([ptkfxsščɕcĉ])([ ‿⁀ʹːˑ()/]*v?[ ‿⁀ʹːˑ()/]*[bdgɣzžĝĵǰӂ])").sub(
            lambda m: voicing[m[1]] + m[2], new_text
        )
        if new_text == text:
            break
        text = new_text
    text = sub2(rf"([^{vow}.\-_])\1", r"\1ː", text)
    text = sub2(rf"([^{vow}.\-_])\(\1\)", r"\1(ː)", text)
    text = re.compile(r"(j[\(ːˑ\)]*)([aeou])").sub(lambda m: m[1] + iotating[m[2]], text)
    text = sub(rf"([^{vow}{acc}ʹʺ‿⁀ ]/?)j([äạëöü])", r"\1\2", text)
    word = text.split(" ")
    for i in range(len(word)):
        pron = word[i]
        if "ː" in pron:
            orig_pron = orig_word[i]
            deac = sub(accents, "", pron)
            orig_deac = sub(accents, "", orig_pron)
            for newspell, oldspell in geminate_pref.items():
                if (
                    re.search(f"⁀{oldspell}", orig_deac)
                    and re.search(f"⁀{newspell}", deac)
                    or re.search(f"⁀ne{oldspell}", orig_deac)
                    and re.search(f"⁀ne{newspell}", deac)
                ):
                    pron = sub(r"(⁀[^‿⁀ː]*)ː", r"\1ˑ", pron)
        if gem == "y":
            pron = pron.replace("ˑ", "ː")
        elif gem == "o":
            pron = sub(r"([^ɕӂ()])[ːˑ]", r"\1(ː)", pron)
        elif gem == "n":
            pron = sub(r"([^ɕӂ()])[ːˑ]", r"\1", pron)
        else:
            pron = sub(r"(l)ː", r"\1", pron)
            pron = sub_repeatedly(rf"({vowels}{accents}[^ɕӂ()])ː({vowels})", r"\1ˑ\2", pron)
            pron = sub_repeatedly(rf"({AC}.-{vowels}{accents}?n)ː({vowels})", r"\1(ː)\2", pron)
            pron = sub_repeatedly(rf"({vowels}{accents}?[žn])ː({vowels})", r"\1ˑ\2", pron)
            pron = sub(rf"({vowels}{accents}[^{vow}]*s)ː(k)", r"\1ˑ\2", pron)
            pron = sub(r"([^ɕӂ()])ː", r"\1", pron)
            pron = pron.replace("ˑ", "ː")
        pron = pron.replace("ʹi", "ʹji")
        pron = sub(r"ʺ([aɛiouy])", r"ʔ\1", pron)
        pron = pron.replace(r"\(ʹ\)", "⁽ʲ⁾")
        pron = sub(r"([mnpbtdkgfvszxɣrl])([ː()]*[eiäạëöüʹ])", r"\1ʲ\2", pron)
        pron = sub(r"([cĵ])([ː()]*[äạöüʹ])", r"\1ʲ\2", pron)
        pron = sub(r"[ʹʺ]", "", pron)
        pron = sub(r"[äạ]⁀", "ə⁀", pron)
        pron = pron.replace("⁀nʲe⁀", "⁀nʲi⁀")
        pron = pron.replace("⁀že⁀", "⁀žy⁀")

        def fetch_e_sub(ending: str) -> str:
            chart = final_e[pos]
            while isinstance(chart, str):
                chart = final_e[chart]
            subval = chart.get(ending, final_e["def"][ending])  # type: ignore[index]
            assert subval
            if subval == "e":
                return f"e{CFLEX}"
            return subval

        pron = re.compile(rf"{vowels_c}({accents}?j)ë⁀").sub(
            lambda m: (ch := m[1]) + m[2] + fetch_e_sub("oe" if ch == "o" else "ve"), pron
        )
        pron = re.compile(r"(.)(ʲ?[ː()]*)[eë]⁀").sub(
            lambda m: (
                (ch := m[1])
                + m[2]
                + fetch_e_sub(
                    "je"
                    if ch == "j"
                    else "hardsib"
                    if re.search(r"[cĵšžĉĝ]", ch)
                    else "softsib"
                    if re.search(r"[čǰɕӂ]", ch)
                    else "softpaired"
                )
            ),
            pron,
        )
        pron = re.compile(r"([cĵšžĉĝ][ː()]*)([ei])").sub(lambda m: m[1] + retracting[m[2]], pron)
        pron = sub(rf"({vowels}{accents}?)", r"\1@", pron)
        pron = sub(r"@+⁀$", "⁀", pron)
        pron = sub(rf"@([^@{vow}{acc}]*)([‿⁀]+[^‿⁀@{vow}{acc}])", r"\1@\2", pron)
        pron = sub(rf"@([^‿⁀@_{vow}{acc}]*)([^‿⁀@_{vow}{acc}ːˑ()ʲ]ʲ?[ːˑ()]*‿?[{vow}{acc}])", r"\1@\2", pron)

        def matcher1(match: re.Match[str]) -> str:
            a, aund, b, bund, c, d = match.groups()
            if f"{a}{b}{c}" in perm_syl_onset or (c == "j" and re.search(r"[čǰɕӂʲ]", b)):
                return f"@{a}{aund}{b}{bund}{c}{d}"
            elif f"{b}{c}" in perm_syl_onset:
                return f"{a}{aund}@{b}{bund}{c}{d}"
            return ""

        pron = re.compile(
            rf"([^‿⁀@_{vow}{acc}]?)(_*)([^‿⁀@_{vow}{acc}])(_*)@([^‿⁀@{vow}{acc}ːˑ()ʲ])(ʲ?[ːˑ()]*[‿⁀]*[{vow}{acc}])"
        ).sub(matcher1, pron)
        if "/" in pron:
            pron = re.compile(rf"[^{vow}{acc}]+").sub(
                lambda m: m[0].replace("@", "").replace("/", "@") if "/" in m[0] else m[0], pron
            )
        pron = sub(rf"@([^‿⁀@{vow}]+⁀)$", r"\1", pron)
        pron = sub(rf"^(⁀[^‿⁀@{vow}]+)@", r"\1", pron)
        pron = sub(r"@([‿⁀]+)", r"\1@", pron)
        pron = sub(rf"^⁀[ao]([^{acc}])", r"⁀ɐ\1", pron, flags=re.MULTILINE)
        syllable = pron.split("@")
        stress = [bool(re.search(accents, syl)) for syl in syllable]
        syl_conv: list[str] = []
        for j, syl in enumerate(syllable):
            if stress[j]:
                syl = sub(r"(.*)́", r"ˈ\1", syl)
                syl = sub(r"(.*)̀", r"ˌ\1", syl)
                syl = syl.replace(CFLEX, "")
                alnum = 0
            elif j + 1 < len(stress) and stress[j + 1]:
                alnum = 1
            else:
                alnum = 2
            syl_conv.append(re.compile(vowels_c).sub(lambda m: allophones[m[1]][alnum] if m[1] else "", syl))
        pron = "".join(syl_conv)
        pron = sub(rf"([{ipa_vow}])jɪ", r"\1(j)ɪ", pron)

        def matcher2(match: re.Match[str]) -> str:
            a, b, c = match.groups()
            return f"{a}{b}ʲ{c}" if not a else f"{a}{b}⁽ʲ⁾{c}"

        pron = re.compile(r"([rl]?)([ː()ˈˌ]*[dtsz])([ː()ˈˌ]*nʲ)").sub(matcher2, pron)
        pron = re.compile(r"([rl]?)([ˈˌ]?[sz])([ː()ˈˌ]*[td]ʲ)").sub(matcher2, pron)

        def matcher3(match: re.Match[str]) -> str:
            a, b, c = match.groups()
            if f"{a}{c}" in cons_assim_palatal["compulsory"]:
                return f"{a}ʲ{b}{c}"
            elif f"{a}{c}" in cons_assim_palatal["optional"]:
                return f"{a}⁽ʲ⁾{b}{c}"
            return f"{a}{b}{c}"

        while True:
            new_pron = re.compile(r"([szntdpbmfcĵx])([ː()ˈˌ]*)([szntdpbmfcĵlk]ʲ)").sub(matcher3, pron)
            if new_pron == pron:
                break
            pron = new_pron
        pron = sub(r"n([ː()ˈˌ]*)([čǰɕӂ])", r"nʲ\1\2", pron)
        pron = sub(r"⁀([ː()ˈˌ]*[fv])([ː()ˈˌ]*[pb]ʲ)", r"⁀\1⁽ʲ⁾\2", pron)
        pron = sub(r"b([ː()ˈˌ]*vʲ)", r"b⁽ʲ⁾\1", pron)
        if re.search(rf"⁀o{accents}?bv", word[i]):
            pron = sub(r"⁀([ː()ˈˌ]*[ɐəo][ː()ˈˌ]*)b⁽ʲ⁾([ː()ˈˌ]*vʲ)", r"⁀\1b\2", pron)
        if re.search(r"ls[äạ]⁀", word[i]):
            pron = pron.replace("lsʲə⁀", "ls⁽ʲ⁾ə⁀")
        word[i] = pron
    text = f"[{' '.join(word)}]"
    text = sub(r"([čǰɕӂj])", r"\1ʲ", text)
    text = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.ʲ)").sub(lambda m: m[1] + fronting[m[2]] + m[3], text)
    text = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?\(jʲ\))").sub(lambda m: m[1] + fronting[m[2]] + m[3], text)
    if re.search(r"ʲ[ː()]*[auʊ][ˈˌ]?.⁽ʲ⁾", text):
        opt_hard = sub(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.)⁽ʲ⁾", r"\1\2\3", text)
        opt_soft = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.)⁽ʲ⁾").sub(lambda m: m[1] + fronting[m[2]] + m[3] + "ʲ", text)
        text = f"{opt_hard}, {opt_soft}"
    text = sub(r"([čǰɕӂj])ʲ", r"\1", text)
    text = sub(r"[cĵ]ʲ", translit_conv_j, text)
    text = sub(r"[cčgĉĝĵǰšžɕӂ]", translit_conv, text)
    text = sub(r"ə([‿⁀]*)[ɐə]", r"ɐ\1ɐ", text)
    text = sub(r"[⁀_]", "", text)
    text = sub(r"j([^aæeiɵuʉ])", r"ɪ̯\1", text)
    text = sub(r"j$", "ɪ̯", text)
    text = sub(r"l([^ʲ])", r"ɫ\1", text)
    text = sub(r"l$", "ɫ", text)
    text = sub(r"([aæə])[()]ɪ̯[()]ɪsʲ$", r"\1ɪ̯əsʲ", text)
    return text


def transcript(text: str) -> str:
    """
    >>> transcript("вот")
    '[vot]'
    >>> transcript("прон")
    '[pron]'
    >>> transcript("молоко́")
    '[moɫoˈko]'
    >>> transcript("нево́лящий")
    '[nʲevoˈlʲæɕːiɪ̯]'
    """
    return ipa(text, "", "", "")
