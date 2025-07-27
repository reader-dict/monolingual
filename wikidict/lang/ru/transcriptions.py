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


# apply rsub() repeatedly until no change
def sub_repeatedly(pattern: str, repl: str, text: str) -> str:
    while True:
        if (new_text := re.sub(pattern, repl, text, count=1)) == text:
            return text
        text = new_text


def translate(text: str, translation: dict[str, str]) -> str:
    return re.compile("|".join(map(re.escape, translation))).sub(lambda match: translation[match[0]], text)


AC = "\u0301"  # acute =  ́
GR = "\u0300"  # grave =  ̀
CFLEX = "\u0302"  # circumflex =  ̂
DUBGR = "\u030f"  # double grave =  ̏
DOTABOVE = "\u0307"  # dot above =  ̇
DOTBELOW = "\u0323"  # dot below =  ̣
BREVE = "\u0306"  # breve  ̆
DIA = "\u0308"  # diaeresis =  ̈
CARON = "\u030c"  # caron  ̌
TEMP_G = "\ufff1"  # substitute to preserve g from changing to v


# any accent
accent = f"{AC}{GR}{DIA}{BREVE}{CARON}"
# regex for any optional accent(s)
opt_accent = f"[{accent}]*"
# any composed Cyrillic vowel with grave accent
composed_grave_vowel = "ѐЀѝЍ"
# any Cyrillic vowel except ёЁ
vowel_no_jo = f"аеиоуяэыюіѣѵАЕИОУЯЭЫЮІѢѴ{composed_grave_vowel}"
# any Cyrillic vowel, including ёЁ
vowel = f"{vowel_no_jo}ёЁ"

vow = "aeiouyɛəäạëöü"
ipa_vow = f"{vow}ɐɪʊɨæɵʉ"
vowels = f"[{vow}]"
vowels_c = f"({vowels})"
# No need to include DUBGR here because we rewrite it to CFLEX very early
acc = f"{AC}{GR}{CFLEX}{DOTABOVE}{DOTBELOW}"
accents = f"[{acc}]"
consonants = r"\A[^аеиоуяэыюіѣѵүАЕИОУЯЭЫЮІѢѴҮѐЀѝЍёЁAEIOUYĚƐaeiouyěɛЪЬъьʹʺ]"

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


# FIXME: Consider changing ӂ internally to ʑ to match ɕ (it is used externally
# in e.g. дроӂӂи (pronunciation spelling of дрожжи)
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
    }[match[1]]


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

iotating = {
    "a": "ä",
    "e": "ë",
    "o": "ö",
    "u": "ü",
}

retracting = {
    "e": "ɛ",
    "i": "y",
}

fronting = {
    "a": "æ",
    "u": "ʉ",
    "ʊ": "ʉ",
}

# Prefixes that we recognize specially when they end in a geminated
# consonant. The first element is the result after applying voicing/devoicing,
# gemination and other changes. The second element is the original spelling,
# so that we don't overmatch and get cases like Поттер. We check for these
# prefixes at the beginning of words and also preceded by ne-, po- and nepo-.
geminate_pref = {
    #'abː', #'adː',
    r"be[szšž]ː": r"be[sz]",
    #'braomː',
    r"[vf]ː": "v",
    r"vo[szšž]ː": r"vo[sz]",
    r"i[szšž]ː": r"i[sz]",
    #'^inː',
    "kontrː": "kontr",
    "superː": "super",
    r"tran[szšž]ː": "trans",
    r"na[tdcč]ː": "nad",
    r"ni[szšž]ː": r"ni[sz]",
    r"o[tdcč]ː": "ot",  #'^omː',
    r"o[bp]ː": "ob",
    r"obe[szšž]ː": r"obe[sz]",
    r"po[tdcč]ː": "pod",
    r"pre[tdcč]ː": "pred",  #'^paszː', '^pozː',
    r"ra[szšž]ː": r"ra[sz]",
    r"[szšž]ː": r"[szšž]",  # ž on right for жжёт etc., ш on left for США
    r"su[bp]ː": "sub",
    r"me[žš]ː": "mež",
    r"če?re[szšž]ː": r"če?re[sz]",
    # certain double prefixes involving ra[zs]-
    r"predra[szšž]ː": r"predra[sz]",
    r"bezra[szšž]ː": r"bezra[sz]",
    r"nara[szšž]ː": r"nara[sz]",
    r"vra[szšž]ː": r"vra[sz]",
    r"dora[szšž]ː": r"dora[sz]",
    # '^sverxː', '^subː', '^tröxː', '^četyröxː',
}


phon_respellings: dict[str, str | Callable[[re.Match[str]], str]] = {
    # Безударный неконечный Е после Ж, Ш, Ц
    rf"([žšc])e([^{acc}⁀])": r"\1y\2",
    # окончания прил./прич. мн. ч.
    r"y(́?)je⁀": r"y\1i⁀",
    r"([gkx])i(́?)je⁀": r"\1i\2i⁀",
    r"([vdntžš])nije⁀": r"\1nii⁀",
    r"ščije(sja?)⁀": r"ščii\1⁀",
    r"všije(sja?)⁀": r"všii\1⁀",
    "h": "ɣ",
    "šč": "ɕː",  # conversion of šč to geminate
    "čš": "tš",
    # the following group is ordered before changes that affect ts
    # FIXME!!! Should these also pay attention to grave accents?
    r"́tʹ?sja⁀": "́cca⁀",
    r"([^́])tʹ?sja⁀": r"\1ca⁀",
    r"n[dt]sk": r"n(t)sk",
    r"s[dt]sk": "sck",
    # Add / before цз, чж sequences (Chinese words) and assimilate чж
    "cz": "/cz",
    "čž": "/ĝž",
    # main changes for affricate assimilation of [dt] + sibilant, including ts;
    # we either convert to "short" variants t͡s, d͡z, etc. or to "long" variants t͡ss, d͡zz, etc.
    # 1. т с, д з across word boundary, also т/с, д/з with explicitly written slash, use long variants.
    r"[dt](ʹ?[ ‿⁀/]+)s": r"c\1s",
    r"[dt](ʹ?[ ‿⁀/]+)z": r"ĵ\1z",
    # 2. тс, дз + vowel use long variants.
    rf"[dt](ʹ?)s(j?{vowels})": r"c\1s\2",
    rf"[dt](ʹ?)z(j?{vowels})": r"ĵ\1z\2",
    # 3. тьс, дьз use long variants.
    r"[dt]ʹs": "cʹs",
    r"[dt]ʹz": "ĵʹz",
    # 4. word-initial от[сз]-, под[сз]- use long variants because there is a morpheme boundary.
    rf"(⁀o{accents}?)t([sz])": lambda match: match[1] + {"s": "cs", "z": "ĵz"}[match[2]],
    rf"(⁀po{accents}?)d([sz])": lambda match: match[1] + {"s": "cs", "z": "ĵz"}[match[2]],
    # 5. other тс, дз use short variants.
    r"[dt]s": "c",
    r"[dt]z": "ĵ",
    # 6. тш, дж always use long variants (FIXME, may change)
    r"[dt](ʹ?[ \-‿⁀/]*)š": r"ĉ\1š",
    r"[dt](ʹ?[ \-‿⁀/]*)ž": r"ĝ\1ž",
    # 7. soften palatalized hard hushing affricates resulting from the previous
    "ĉʹ": "č",
    "ĝʹ": "ǰ",
    # changes that generate ɕː and ɕč through assimilation:
    # зч and жч become ɕː, as does сч at the beginning of a word and in the
    # sequence счёт when not following [цдт] (подсчёт); else сч becomes ɕč
    # (отсчи́тываться), as щч always does (рассчитáть written ращчита́ть)
    r"[cdt]sč": "čɕː",
    "ɕːč": "ɕč",
    r"[zž]č": "ɕː",
    r"[szšž]ɕː?": "ɕː",
    rf"sčjo({accents}?)t": r"ɕːjo\1t",
    rf"sče({accents}?)t": r"ɕːe\1t",
    rf"sčja({accents}?)s": r"ɕːja\1s",
    "sč": "ɕč",
    # misc. changes for assimilation of [dtsz] + sibilants and affricates
    r"[sz][dt]c": "sc",
    r"([rn])[dt]([cč])": r"\1\2",
    # -дцат- (in numerals) has optionally-geminated дц
    rf"dca({accents}?)t": r"c(c)a\1t",
    # дц, тц, дч, тч + vowel always remain geminated, so mark this with ˑ;
    # if not followed by a vowel, as in e.g. путч, use normal gemination
    # (it will normally be degeminated)
    rf"[dt]([cč])({vowels})": r"\1ˑ\2",
    r"[dt]([cč])": r"\1\1",
    # the following is ordered before the next one, which applies assimilation
    # of [тд] to щ (including across word boundaries)
    r"n[dt]ɕ": "nɕ",
    # [сз] and [сз]ь before soft affricates [щч], including across word
    # boundaries; note that the common sequence сч has already been handled
    r"[zs]ʹ?([ ‿⁀/]*[ɕč])": r"ɕ\1",
    # reduction of too many ɕ's, which can happen from the previous
    "ɕɕː": "ɕː",
    # assimilation before [тдц] and [тдц]ь before щ
    r"[cdt]ʹ?([ ‿⁀/]*)ɕ": r"č\1ɕ",
    # assimilation of [сз] and [сз]ь before [шж]
    r"[zs]([ ‿⁀/]*)š": r"š\1š",
    r"[zs]([ ‿⁀/]*)ž": r"ž\1ž",
    r"[zs]ʹ([ ‿⁀/]*)š": r"ɕ\1š",
    r"[zs]ʹ([ ‿⁀/]*)ž": r"ӂ\1ž",
    "sverxi": "sverxy",
    "stʹd": "zd",
    "tʹd": "dd",
    # loss of consonants in certain clusters
    r"([ns])[dt]g": r"\1g",
    "zdn": "zn",
    "lnc": "nc",
    r"[sz]tn": "sn",
    rf"[sz]tli({accents}?)v([^š])": r"sli\1v\2",
    r"čju(́?)vstv": r"ču\1stv",
    r"zdra(́?)vstv": r"zdra\1stv",
    "lvstv": "lstv",
    # backing of /i/ after hard consonants in close juncture
    r"([mnpbtdkgfvszxɣrlšžcĵĉĝ])⁀‿⁀i": r"\1⁀‿⁀y",
}

cons_assim_palatal = {
    # assimilation of tn, dn, sn, zn, st, zd, nč, nɕ is handled specially
    "compulsory": {"ntʲ", "ndʲ", "xkʲ", "csʲ", "ĵzʲ", "ncʲ", "nĵʲ"},
    "optional": {"nsʲ", "nzʲ", "mpʲ", "mbʲ", "mfʲ", "fmʲ"},
}

# words which will be treated as accentless (i.e. their vowels will be
# reduced), and which will liaise with a preceding or following word;
# this will not happen if the words have an accent mark, cf.
# по́ небу vs. по не́бу, etc.
accentless = {
    # class 'pre': particles that join with a following word
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
    # class 'prespace': particles that join with a following word, but only
    #   if a space (not a hyphen) separates them; hyphens are used here
    #   to spell out letters, e.g. а-эн-бэ́ for АНБ (NSA = National Security
    #   Agency) or о-а-э́ for ОАЭ (UAE = United Arab Emirates)
    "prespace": {"a", "o"},
    # class 'post': particles that join with a preceding word
    "post": {"by", "b", "ž", "že", "li", "libo", "lʹ", "ka", "nibudʹ", "tka"},
    # class 'posthyphen': particles that join with a preceding word, but only
    #   if a hyphen (not a space) separates them
    "posthyphen": {"to"},
}

# Pronunciation of final unstressed -е, depending on the part of speech and
#   exact ending.
#
# Endings:
#   oe = -ое
#   ve = any other vowel plus -е (FIXME, may have to split out -ее)
#   je = -ье
#   softpaired = soft paired consonant + -е
#   hardsib = hard sibilant (ц, ш, ж) + -е
#   softsib = soft sibilant (ч, щ) + -е
#
# Parts of speech:
#   def = default used in absence of pos
#   n/noun = neuter noun in the nominative/accusative singular (but not ending
#     in adjectival -ое or -ее; those should be considered as adjectives)
#   pre = prepositional case singular
#   dat = dative case singular (treated same as prepositional case singular)
#   voc = vocative case (currently treated as 'mid')
#   nnp = noun nominative plural in -е (гра́ждане, боя́ре, армя́не); not
#     adjectival plurals in -ие or -ые, including adjectival nouns
#     (да́нные, а́вторские)
#   inv = invariable noun or other word (currently treated as 'mid')
#   a/adj = adjective or adjectival noun (typically either neuter in -ое or
#     -ее, or plural in -ие, -ые, or -ье, or short neuter in unpaired
#     sibilant + -е)
#   c/com = comparative (typically either in -ее or sibilant + -е)
#   adv = adverb
#   p = preposition (treated same as adverb)
#   v/vb/verb = finite verbal form (usually 2nd-plural in -те); not
#     participle forms, which should be treated as adjectives
#   pro = pronoun (кое-, какие-, ваше, сколькие)
#   num = number (двое, трое, обе, четыре; currently treated as 'mid')
#   pref = prefix (treated as 'high' because integral part of word)
#   hi/high = force high values ([ɪ] or [ɨ])
#   mid = force mid values ([e] or [ɨ])
#   lo/low/schwa = force low, really schwa, values ([ə])
#
# Possible values:
#   1. ə [ə], e [e], i [ɪ] after a vowel or soft consonant
#   2. ə [ə] or y [ɨ] after a hard sibilant
#
# If a part of speech doesn't have an entry for a given type of ending,
#   it receives the default value. If a part of speech's entry is a string,
#   it's an alias for another way of specifying the same part of speech
#   (e.g. n=noun).
final_e: dict[str, dict[str, str] | str] = {
    "def": {"oe": "ə", "ve": "ə", "je": "ə", "softpaired": "ɪ", "hardsib": "ə", "softsib": "ɪ"},
    "noun": {"oe": "ə", "ve": "e", "je": "e", "softpaired": "e", "hardsib": "ə", "softsib": "e"},
    "n": "noun",
    "pre": {"oe": "e", "ve": "e", "softpaired": "e", "hardsib": "y", "softsib": "e"},
    "dat": "pre",
    "voc": "mid",
    # FIXME, not sure about this
    "nnp": {"softpaired": "e"},
    # FIXME, not sure about this (e.g. вице-, кофе)
    "inv": "mid",
    # FIXME: Not sure about -ее, e.g. neut adj си́нее; FIXME, not sure about short neuter adj, e.g. похо́же from похо́жий, дорогосто́яще from дорогосто́ящий, should this be treated as neuter noun?
    "adj": {"oe": "ə", "ve": "e", "je": "ə"},
    "a": "adj",
    "com": {"ve": "e", "hardsib": "y", "softsib": "e"},
    "c": "com",
    "adv": {"softpaired": "e", "hardsib": "y", "softsib": "e"},
    # FIXME, not sure about prepositions
    "p": "adv",
    "verb": {"softpaired": "e"},
    "v": "verb",
    "vb": "verb",
    # FIXME, not sure about ваше, сколькие, какие-, кое-
    "pro": {"oe": "i", "ve": "i"},
    # FIXME, not sure about обе
    "num": "mid",
    "pref": "high",
    # forced values
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
    f"е{DIA}": "ё",  # WARNING: Cyrillic е and Е
    f"Е{DIA}": "Ё",
    f"e{CARON}": "ě",  # WARNING: Latin e and E
    f"E{CARON}": "Ě",
    f"c{CARON}": "č",
    f"C{CARON}": "Č",
    f"s{CARON}": "š",
    f"S{CARON}": "Š",
    f"z{CARON}": "ž",
    f"Z{CARON}": "Ž",
    # used in ru-pron:
    f"ж{BREVE}": "ӂ",  # used in ru-pron
    f"Ж{BREVE}": "Ӂ",
    f"j{CFLEX}": "ĵ",
    f"J{CFLEX}": "Ĵ",
    f"j{CARON}": "ǰ",
    # no composed uppercase equivalent of J-caron
    f"ʒ{CARON}": "ǯ",
    f"Ʒ{CARON}": "Ǯ",
}

# In this table, we now map Cyrillic е and э to je and e, and handle the
# post-consonant version (plain e and ɛ) specially.
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
    # Russian style quotes
    "«": "“",
    "»": "”",
    # archaic, pre-1918 letters
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


# For use with {{ru-IPA|phon=+.}}; remove accents that we don't want
# to appear in the phonetic respelling
def phon_respelling(text: str) -> str:
    text = re.sub(rf"[{CFLEX}{DUBGR}{DOTABOVE}{DOTBELOW}]", "", text)
    return text.replace("‿", " ")


# For use with {{ru-IPA|adj=+.}}; rewrite adjectival endings to the form
# used for phonetic respelling
def adj_respelling(text: str) -> str:
    sub = re.sub

    # ого, его, аго (pre-reform spelling), with optional accent on either
    # vowel, optionally with reflexive -ся suffix, at end of phrase or end
    # of word followed by space or hyphen
    text = sub(rf"(.[аое]́?)го({AC}?)$", r"\1во\2", text)
    text = sub(rf"(.[аое]́?)го({AC}?ся)$", r"\1во\2", text)
    text = sub(rf"(.[аое]́?)го{AC}?[ \-])", r"\1во\2", text)
    return sub(rf"(.[аое]́?)го({AC}?ся[ \-])", r"\1во\2", text)


def decompose(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    return re.compile(rf"(.[{BREVE}{DIA}{CARON}])").sub(lambda match: recomposer[match[1]], text)


map_to_plain_e_map = {"Е": "E", "е": "e", "Ѣ": "Ě", "ѣ": "ě", "Э": "Ɛ", "э": "ɛ"}


def is_monosyllabic(word: str) -> bool:
    return not re.search(rf"[{vowels}].*[{vowels}]", word)


# Transliterate after the pronunciation-related transformations of
# export.apply_tr_fixes() have been applied. Called from {{ru-IPA}}.
# INCLUDE_MONOSYLLABIC_JO_ACCENT is as in export.tr().
def tr_after_fixes(text: str, include_monosyllabic_jo_accent: bool) -> str:
    sub = re.sub

    # Remove word-final hard sign, either utterance-finally or followed by
    # a non-letter character such as space, comma, period, hyphen, etc.
    text = sub(r"[Ъъ]$", "", text)
    text = sub(r"\A[Ъъ](.+)", r"\1", text)

    # the if-statement below isn't necessary but may speed things up,
    # particularly when include_monosyllabic_jo_accent isn't set, in that
    # in the majority of cases where ё doesn't occur, we avoid a pattern find
    # (in is_monosyllabic()) and three pattern subs. The translit module needs
    # to be as fast as possible since it may be called hundreds or
    # thousands of times on some pages.
    if re.search(r"[Ёё]", text):
        # We need to special-case ё after a "hushing" consonant, which becomes
        # ó (or o), without j. We also need special cases for monosyllabic ё
        # when INCLUDE_MONOSYLLABIC_JO_ACCENT isn't set, so we don't add the
        # accent mark that we would otherwise include.
        if not include_monosyllabic_jo_accent and is_monosyllabic(text):
            text = sub(r"([жшчщЖШЧЩ])ё", r"\1o", text)
            text = text.replace("ё", "jo")
            text = text.replace("Ё", "Jo")
        else:
            text = sub(r"([жшчщЖШЧЩ])ё", r"\1ó", text)
            # conversion of remaining ё will occur as a result of 'tab'.

    # ю after ж and ш becomes u (e.g. брошюра, жюри)
    text = sub(r"([жшЖШ])ю", r"\1u", text)

    # the if-statement below isn't necessary but may speed things up in that
    # in the majority of cases where the letters below don't occur, we avoid
    # six pattern subs.
    if re.search(r"[ЕеѢѣЭэ]", text):
        # е after a dash at the beginning of a word becomes e, and э becomes ɛ
        # (like after a consonant)
        text = re.compile(r"^(\-)([ЕеѢѣЭэ])").sub(lambda match: match[1] + map_to_plain_e_map[match[2]], text)
        text = re.compile(r"(\s-)([ЕеѢѣЭэ])").sub(lambda match: match[1] + map_to_plain_e_map[match[2]], text)
        # don't get confused by single quote or parens between consonant and е;
        # e.g. Б'''ез''', американ(ец)
        text = re.compile(rf"({consonants}['()]*)([ЕеѢѣЭэ])").sub(
            lambda match: match[1] + map_to_plain_e_map[match[2]], text
        )

    return translate(text, tab)


# Apply transformations to the Cyrillic to more closely match pronunciation.
# Return two arguments: the "original" text (after decomposing composed
# grave characters), and the transformed text. If the two are different,
# {{ru-IPA}} should display a "phonetic respelling" notation.
# NOADJ disables special-casing for adjectives in -го, while FORCEADJ forces
# special-casing for adjectives, including those in -аго (pre-reform spelling)
# and disables checking for exceptions (e.g. много, ого). NOSHTO disables
# special-casing for что and related words.
def apply_tr_fixes(text: str) -> tuple[str, str]:
    # decompose composed grave characters before we convert Cyrillic е to Latin e or je
    text = translate(text, decompose_grave_map)

    sub = re.sub

    origtext = text
    # the second half of the if-statement below is an optimization; see above.
    if "го" in text:
        # handle много
        text = sub(
            r"\f[\a\204\129\204\128]([Мм]но[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle немного, намного
        text = sub(
            r"\f[\a\204\129\204\128]([Нн][еа]мно[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle ненамного
        text = sub(
            r"\f[\a\204\129\204\128]([Нн]енамно[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle до́рого [short form of дорогой, adverb]
        text = sub(
            r"\f[\a\204\129\204\128]([Дд]о[\204\129\204\128]?ро)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle недо́рого [short form of недорогой, adverb]
        text = sub(
            r"\f[\a\204\129\204\128]([Нн]едо[\204\129\204\128]?ро)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle задо́рого [short form of недорогой, adverb]
        text = sub(
            r"\f[\a\204\129\204\128]([Зз]адо[\204\129\204\128]?ро)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle незадо́рого [short form of недорогой, adverb]
        text = sub(
            r"\f[\a\204\129\204\128]([Зз]анедо[\204\129\204\128]?ро)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle стро́го
        text = sub(
            r"\f[\a\204\129\204\128]([Сс]тро[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle на́строго
        text = sub(
            r"\f[\a\204\129\204\128]([Нн]а[\204\129\204\128]?стро)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle нестро́го
        text = sub(
            r"\f[\a\204\129\204\128]([Нн]естро[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle убо́го
        text = sub(
            r"\f[\a\204\129\204\128]([Уу]бо[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle поло́го
        text = sub(
            r"\f[\a\204\129\204\128]([Пп]оло[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle длинноно́го
        text = sub(
            r"\f[\a\204\129\204\128]([Дд]линноно[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle коротконо́го
        text = sub(
            r"\f[\a\204\129\204\128]([Кк]оротконо[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle кривоно́го
        text = sub(
            r"\f[\a\204\129\204\128]([Кк]ривоно[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle колчено́го
        text = sub(
            r"\f[\a\204\129\204\128]([Кк]олчено[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle отло́го
        text = sub(
            r"\f[\a\204\129\204\128]([Оо]тло[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle пе́го [short form of пе́гий "piebald"]
        text = sub(
            r"\f[\a\204\129\204\128]([Пп]е[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle лого, сого, ого
        text = sub(
            r"\f[\a\204\129\204\128]([лсЛС]?[Оо][\204\129\204\128]?)г(о[\204\129\204\128]?)\f[^\a\204\129\204\128]",
            r"\1" + TEMP_G + "\2",
            text,
        )
        # handle Того, То́го (but not того or Того́, which have /v/)
        text = sub(
            r"\f[\a\204\129\204\128]([Тт]о[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle лего
        text = sub(
            r"\f[\a\204\129\204\128]([Лл]е[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle игого, огого; note, we substitute TEMP_G for both г's
        # because otherwise the ого- at the beginning gets converted to ово
        text = sub(
            r"\f[\a\204\129\204\128]([ИиОо])гог(о[\204\129\204\128]?)\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о{TEMP_G}\2",
            text,
        )
        # handle Диего
        text = sub(
            r"\f[\a\204\129\204\128]([Дд]ие[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )
        # handle слого-
        text = sub(
            r"\f[\a\204\129\204\128]([Сс]ло[\204\129\204\128]?)го\f[^\a\204\129\204\128]",
            rf"\1{TEMP_G}о",
            text,
        )

        # handle genitive/accusative endings, which are spelled -ого/-его/-аго
        # (-ogo/-ego/-ago) but transliterated -ovo/-evo/-avo; only for adjectives
        # and pronouns, excluding words like много, ого (-аго occurs in
        # pre-reform spelling); \204\129 is an acute accent, \204\128 is a grave accent
        pattern = r"([оеОЕ][\204\129\204\128]?)([гГ])([оО][\204\129\204\128]?)"
        reflexive = r"([сС][яЯ][\204\129\204\128]?)"
        v = {"г": "в", "Г": "В"}
        text = re.compile(rf"{pattern}\f[^\a\204\129\204\128]").sub(
            lambda match: match[1] + v[match[2]] + match[3] + match[4],
            text,
        )
        text = re.compile(rf"{pattern}{reflexive}\f[^\a\204\129\204\128]").sub(
            lambda match: match[1] + v[match[2]] + match[3] + match[4],
            text,
        )

        # handle сегодня
        text = sub(r"\f[\a\204\129\204\128]([Сс]е)г(о[\204\129\204\128]?дня)\f[^\a\204\129\204\128]", r"\1в\2", text)

        # handle сегодняшн-
        text = sub(r"\f[\a\204\129\204\128]([Сс]е)г(о[\204\129\204\128]?дняшн)", r"\1в\2", text)

        # replace TEMP_G with g; must be done after the -go -> -vo changes
        text = sub(TEMP_G, "г", text)

    # the second half of the if-statement below is an optimization; see above.
    if "то" in text:
        ch2sh = {"ч": "ш", "Ч": "Ш"}
        # Handle что
        text = re.compile(r"\f[\a\204\129\204\128]([Чч])(то[\204\129\204\128]?)\f[^\a\204\129\204\128]").sub(
            lambda match: ch2sh[match[1]] + match[2], text
        )
        # Handle чтобы, чтоб
        text = re.compile(r"\f[\a\204\129\204\128]([Чч])(то[\204\129\204\128]?бы?)\f[^\a\204\129\204\128]").sub(
            lambda match: ch2sh[match[1]] + match[2], text
        )
        # Handle ничто
        text = sub(r"\f[\a\204\129\204\128]([Нн]и)ч(то[\204\129\204\128]?)\f[^\a\204\129\204\128]", r"\1ш\2", text)

    text = sub(r"([МмЛл][яеё][\204\129\204\128]?)г([кч])", r"\1х\2", text)

    return origtext, text


# Transliterates text, which should be a single word or phrase. It should
# include stress marks, which are: preserved in the transliteration.
# ё is a special case: it is rendered (j)ó in multisyllabic words and
# monosyllabic words in multi-word phrases, but rendered (j)o without an
# accent in isolated monosyllabic words, unless INCLUDE_MONOSYLLABIC_JO_ACCENT
# is specified. (This is used in conjugation and declension tables.)
# NOADJ disables special-casing for adjectives in -го, while FORCEADJ forces
# special-casing for adjectives and disables checking for exceptions
# (e.g. много). NOSHTO disables special-casing for что and related words.
def tr(text: str, lang: None, sc: None, include_monosyllabic_jo_accent: bool) -> str:
    origtext, subbed_text = apply_tr_fixes(text)
    return tr_after_fixes(subbed_text, include_monosyllabic_jo_accent)


def translit(text: str, no_include_monosyllabic_jo_accent: bool) -> str:
    return decompose(tr(text, None, None, not no_include_monosyllabic_jo_accent))


def ipa(text: str, adj: str, gem: str, pos: str) -> str:
    gem = gem[0] if gem else ""
    pos = pos or "def"

    # If a multipart part of speech, split into components, and convert
    # each blank component to the default.
    # if "/" in pos:
    #     pos = pos.split("/")
    #     for i, p in enumerate(pos):
    #         if p == "":
    #             pos[i] = "def"

    text = text.lower()
    text = text.replace("``", DUBGR)
    text = text.replace("`", GR)
    text = text.replace("@", DOTABOVE)
    text = text.replace("^", CFLEX)
    text = text.replace(DUBGR, CFLEX)

    sub = re.sub
    sub2 = regex.sub

    # translit doesn't always convert э to ɛ (depends on whether a consonant precedes), so: it ourselves before translit
    text = text.replace("э", "ɛ")
    # vowel + йе should have double jj, but the translit module will translit
    # it the same as vowel + е, so: it ourselves before translit
    text = sub(rf"([{vowel}]{opt_accent})й([еѐ])", r"\1йй\2", text)
    # transliterate and decompose Latin vowels with accents, recomposing
    # certain key combinations; don't include accent on monosyllabic ё, so
    # that we end up without an accent on such words
    text = translit(text, True)

    # handle old ě (e.g. сѣдло́), and ě̈ from сѣ̈дла
    text = text.replace("ě̈", f"jo{AC}")
    text = text.replace("ě", "e")
    # handle sequences of accents (esp from ё with secondary/tertiary stress)
    text = sub(f"{accents}+({accents})", r"\1", text)

    # canonicalize multiple spaces
    text = sub(r"\s+", " ", text)

    # Add primary stress to single-syllable words preceded or followed by
    # unstressed particle or preposition. Add "tertiary" stress to remaining
    # single-syllable words that aren't a particle, preposition, prefix or
    # suffix and don't already bear an accent (including force-reduction
    # accents, i.e. dot-above/dot-below); "tertiary stress" means a vowel is
    # treated as stressed for the purposes of vowel reduction but isn't
    # marked with a primary or secondary stress marker; we repurpose a
    # circumflex for this purpose. We need to preserve the distinction
    # between spaces and hyphens because (1) we only recognize certain
    # post-accentless particles following a hyphen (to distinguish e.g.
    # 'то' from '-то'); (2) we only recognize certain pre-accentless
    # particles preceding a space (to distinguish particles 'о' and 'а' from
    # spelled letters о and а, which should not be reduced); and (3) we
    # recognize hyphens for the purpose of marking unstressed prefixes and
    # suffixes.
    word = re.split(r"([ \-]+)", text)
    for i in range(len(word)):
        # check for single-syllable words that need a stress; they must meet
        # the following conditions:
        if not (
            (
                # 1. must not be an accentless word, which is any of the following:
                # 1a. in the "pre" class, or
                word[i] in accentless["pre"]
                or
                # 1b. in the "prespace" class if followed by space and another word, or
                i < len(word) - 1
                and word[i] in accentless["prespace"]
                and word[i + 1] == " "
                or
                # 1c. in the "post" class if preceded by another word, or
                i > 2
                and word[i] in accentless["post"]
                or
                # 1d. in the "posthyphen" class preceded by a hyphen and another word;
                i > 2
                and word[i] in accentless["posthyphen"]
                and word[i - 1] == "-"
            )
            and
            # 2. must be one syllable;
            len(sub(rf"[^{vow}]", "", word[i])) == 1
            and
            # 3. must not have any accents (including dot-above, forcing reduction);
            not re.search(accents, word[i])
            and
            # 4. must not be a prefix or suffix, identified by a preceding or trailing hyphen, i.e. one of the following:
            # 4a. utterance-initial preceded by a hyphen, or
            not (
                i == 3
                and word[2] == "-"
                and word[1] == ""
                or
                # 4b. non-utterance-initial preceded by a hyphen, or
                i >= 3
                and word[i - 1] == " -"
                or
                # 4c. utterance-final followed by a hyphen, or
                i == len(word) - 2
                and word[i + 1] == "-"
                and word[i + 2] == ""
                or
                # 4d. non-utterance-final followed by a hyphen;
                i <= len(word) - 2
                and word[i + 1] == "- "
            )
        ):
            # OK, we have a stressable single-syllable word; either add primary
            # or tertiary stress:
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
                # 1. add primary stress if preceded or followed by an accentless word,
                word[i] = sub(vowels_c, rf"\1{AC}", word[i])
            else:
                # 2. else add tertiary stress
                word[i] = sub(vowels_c, rf"\1{CFLEX}", word[i])

    # make unaccented prepositions and particles liaise with the following or
    # preceding word
    for i in range(len(word)):
        if i < len(word) - 1 and (
            word[i] in accentless["pre"] or word[i] in accentless["prespace"] and word[i + 1] == " "
        ):
            word[i + 1] = "‿"
        elif i > 2 and (word[i] in accentless["post"] or word[i] in accentless["posthyphen"] and word[i - 1] == "-"):
            word[i - 1] = "‿"

    # rejoin words, convert hyphens to spaces and eliminate stray spaces resulting from this
    text = sub(r"[\-\s]+", " ", "".join(word))
    text = text.strip()

    # convert commas and en/en dashes to IPA foot boundaries
    text = sub(r"\s*[,–—]\s*", " | ", text)

    # add a ⁀ at the beginning and end of every word and at close juncture
    # boundaries; we will remove this later but it makes it easier to:
    # word-beginning and word-end re.subs
    text = text.replace(" ", "⁀ ⁀")
    text = "⁀" + text + "⁀"
    text = text.replace("‿", "⁀‿⁀")

    # save original word spelling before respellings, (de)voicing changes,
    # geminate changes, etc. for implementation of geminate_pref
    orig_word = text.split(" ")

    # insert or remove /j/ before [aou] so that palatal versions of these
    # vowels are always preceded by /j/ and non-palatal versions never are
    # (do this before the change below adding tertiary stress to final
    # palatal о):
    # (1) Non-palatal [ou] after always-hard шж (e.g. in брошю́ра, жю́ри) despite the spelling (FIXME, should this also affect [a]?)
    text = sub(r"([šž])j([ou])", r"\1\2", text)
    # (2) Palatal [aou] after always-soft щчӂ and voiced variant ǰ (NOTE: this happens before the change šč -> ɕː in phon_respellings)
    text = sub(r"([čǰӂ])([aou])", r"\1j\2", text)
    # (3) ьо is pronounced as ьйо, i.e. like (possibly unstressed) ьё, e.g. in Асунсьо́н
    text = text.replace("ʹo", "ʹjo")

    # add tertiary stress to some final -о (this needs to be done before
    # eliminating dot-above, after adding ⁀, after adding /j/ before palatal о):
    # (1) after vowels, e.g. То́кио
    text = sub(rf"({vowels}{accents}?o)⁀", rf"\1{CFLEX}⁀", text)
    # (2) when palatal, e.g. ра́нчо, га́учо, ма́чо, Ога́йо
    text = text.replace("jo⁀", f"jo{CFLEX}⁀")

    # eliminate dot-above, which has served its purpose of preventing any
    # sort of stress (needs to be done after adding tertiary stress to final -о)
    text = text.replace(DOTABOVE, "")
    # eliminate dot-below (needs to be done after changes above that insert j before [aou] after always-soft щчӂ)
    text = text.replace(f"ja{DOTBELOW}", "jạ")
    if DOTBELOW in text:
        raise ValueError("Dot-below accent can only be placed on я or palatal а")

    text = sub(rf"(.[aoe]́?)go({AC}?)⁀", r"\1vo\2⁀", text) if adj else text
    text = sub(rf"(.[aoe]́?)go({AC}?)sja⁀", r"\1vo\2sja⁀", text) if adj else text

    # phonetic respellings
    for pattern, repl in phon_respellings.items():
        if isinstance(repl, str):
            text = sub(pattern, repl, text)
        else:
            text = re.compile(pattern).sub(repl, text)

    # voicing, devoicing
    # NOTE: v before an obstruent assimilates in voicing and triggers voicing
    # assimilation of a preceding consonant; neither happens before a sonorant

    # 1. absolutely final devoicing
    text = re.compile(r"([bdgvɣzžĝĵǰӂ])(ʹ?⁀)$").sub(lambda match: devoicing[match[1]] + match[2], text)

    # 2. word-final devoicing before another word
    text = re.compile(r"([bdgvɣzžĝĵǰӂ])(ʹ?⁀ ⁀[^bdgɣzžĝĵǰӂ])").sub(lambda match: devoicing[match[1]] + match[2], text)

    # 3. voicing/devoicing assimilation; repeat to handle recursive assimilation
    while True:
        new_text = re.compile(r"([bdgvɣzžĝĵǰӂ])([ ‿⁀ʹːˑ()/]*[ptkfxsščɕcĉ])").sub(
            lambda match: devoicing[match[1]] + match[2], text
        )
        new_text = re.compile(r"([ptkfxsščɕcĉ])([ ‿⁀ʹːˑ()/]*v?[ ‿⁀ʹːˑ()/]*[bdgɣzžĝĵǰӂ])").sub(
            lambda match: voicing[match[1]] + match[2], new_text
        )
        if new_text == text:
            break
        text = new_text

    # re-notate orthographic geminate consonants
    text = sub2(rf"([^{vow}.\-_])\1", r"\1ː", text)
    text = sub2(rf"([^{vow}.\-_])\(\1\)", r"\1(ː)", text)

    # rewrite iotated vowels
    text = re.compile(r"(j[\(ːˑ\)]*)([aeou])").sub(lambda match: match[1] + iotating[match[2]], text)

    # eliminate j after consonant and before iotated vowel (including semi-reduced ạ)
    text = sub(rf"([^{vow}{acc}ʹʺ‿⁀ ]/?)j([äạëöü])", r"\1\2", text)

    # split by word and process each word
    word = text.split(" ")

    for pron in word:
        # Check for gemination at prefix boundaries; if so, convert the
        # regular gemination symbol ː to a special symbol ˑ that indicates
        # we always preserve the gemination unless gem=n. We look for
        # certain sequences at the beginning of a word, but make sure that
        # the original spelling is appropriate as well (see comment above
        # for geminate_pref).
        if "ː" in pron:
            orig_pron = orig_word[i]
            deac = sub(accents, "", pron)
            orig_deac = sub(accents, "", orig_pron)
            for newspell, oldspell in geminate_pref.items():
                # FIXME! The re.sub below will be incorrect if there is
                # gemination in a joined preposition or particle
                if (
                    re.search(f"⁀{oldspell}", orig_deac)
                    and re.search(f"⁀{newspell}", deac)
                    or re.search(f"⁀ne{oldspell}", orig_deac)
                    and re.search(f"⁀ne{newspell}", deac)
                ):
                    pron = sub(r"(⁀[^‿⁀ː]*)ː", r"\1ˑ", pron)

        # degemination, optional gemination
        if gem == "y":
            # leave geminates alone, convert ˑ to regular gemination; ˑ is a
            # special gemination symbol used at prefix boundaries that we
            # remove only when gem=n, else we convert it to regular gemination
            pron = pron.replace("ˑ", "ː")
        elif gem == "o":
            # make geminates optional, except for ɕӂ, also ignore left paren in (ː) sequence
            pron = sub(r"([^ɕӂ()])[ːˑ]", r"\1(ː)", pron)
        elif gem == "n":
            # remove gemination, except for ɕӂ
            pron = sub(r"([^ɕӂ()])[ːˑ]", r"\1", pron)
        else:
            # degeminate l's
            pron = sub(r"(l)ː", r"\1", pron)
            # preserve gemination between vowels immediately after the stress,
            # special gemination symbol ˑ also remains, ɕӂ remain geminated,
            # žn remain geminated between vowels even not immediately after
            # the stress, n becomes optionally geminated when after but not
            # immediately after the stress, ssk and zsk remain geminated
            # immediately after the stress, else degeminate; we signal that
            # gemination should remain by converting to special symbol ˑ,
            #: removing remaining ː not after ɕӂ and left paren;:
            # various subs repeatedly in case of multiple geminations in a word
            # 1. immediately after the stress
            pron = sub_repeatedly(rf"({vowels}{accents}[^ɕӂ()])ː({vowels})", r"\1ˑ\2", pron)

            # 2. remaining geminate n after the stress between vowels
            pron = sub_repeatedly(rf"({AC}.-{vowels}{accents}?n)ː({vowels})", r"\1(ː)\2", pron)

            # 3. remaining ž and n between vowels
            pron = sub_repeatedly(rf"({vowels}{accents}?[žn])ː({vowels})", r"\1ˑ\2", pron)

            # 4. ssk (and zsk, already normalized) immediately after the stress
            pron = sub(rf"({vowels}{accents}[^{vow}]*s)ː(k)", r"\1ˑ\2", pron)

            # 5. eliminate remaining gemination, except for ɕː and ӂː
            pron = sub(r"([^ɕӂ()])ː", r"\1", pron)

            # 6. convert special gemination symbol ˑ to regular gemination
            pron = pron.replace("ˑ", "ː")

        # handle soft and hard signs, assimilative palatalization
        # 1. insert j before i when required
        pron = pron.replace("ʹi", "ʹji")

        # 2. insert glottal stop after hard sign if required
        pron = sub(r"ʺ([aɛiouy])", r"ʔ\1", pron)

        # 3. (ь) indicating optional palatalization
        pron = pron.replace(r"\(ʹ\)", "⁽ʲ⁾")

        # 4. assimilative palatalization of consonants when followed by
        #    front vowels or soft sign
        pron = sub(r"([mnpbtdkgfvszxɣrl])([ː()]*[eiäạëöüʹ])", r"\1ʲ\2", pron)
        pron = sub(r"([cĵ])([ː()]*[äạöüʹ])", r"\1ʲ\2", pron)

        # 5. remove hard and soft signs
        pron = sub(r"[ʹʺ]", "", pron)

        # reduction of unstressed word-final -я, -е; but special-case
        # unstressed не, же. Final -я always becomes [ə]; final -е may
        # become [ə],e],ɪ] or [ɨ] depending on the part of speech and
        # the preceding consonants/vowels.
        pron = sub(r"[äạ]⁀", "ə⁀", pron)
        pron = pron.replace("⁀nʲe⁀", "⁀nʲi⁀")
        pron = pron.replace("⁀že⁀", "⁀žy⁀")

        # function to fetch the appropriate value for ending and part of
        # speech, handling aliases and defaults and converting 'e' to 'ê'
        # so that the unstressed [e] sound is preserved
        def fetch_e_sub(ending: str) -> str:
            thispos = pos[i] if isinstance(pos, list) else pos
            chart = final_e[thispos]
            while isinstance(chart, str):  # handle aliases
                chart = final_e[chart]
            assert isinstance(final_e["def"], dict)  # For Mypy
            sub = chart[ending] or final_e["def"][ending]
            assert sub
            if sub == "e":
                # add CFLEX to preserve the unstressed [e] sound, which
                # will otherwise be converted to [ɪ]; NOTE: DO NOT use ê
                # here directly because it's a single composed char, when
                # we need the e and accent to be separate
                return f"e{CFLEX}"
            return sub

        # handle substitutions in two parts, one for vowel+j+e sequences
        # and the other for cons+e sequences
        pron = re.compile(rf"{vowels_c}({accents}?j)ë⁀").sub(
            lambda match: (ch := match[1]) + match[2] + fetch_e_sub("oe" if ch == "o" else "ve"), pron
        )
        # consonant may palatalized, geminated or optional-geminated
        pron = re.compile(r"(.)(ʲ?[ː()]*)[eë]⁀").sub(
            lambda match: (
                (ch := match[1])
                + match[2]
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

        # Do the old way, which mostly converts final -е to schwa, but
        # has highly broken retraction code for vowel + [шжц] + е (but
        # not with accent on vowel!) before it that causes final -е in
        # this circumstance to become [ɨ], and a special hack for кое-.
        # pron = sub(rf"{vowels_c}([cĵšžĉĝ][ː()]*)[eë]", r'\1\2ɛ', pron)
        # pron = sub(rf"⁀ko({accents})jë⁀", r'⁀ko\1ji⁀', pron)
        # pron = sub(r'[eë]⁀', 'ə⁀', pron)

        # retraction of е and и after цшж
        pron = re.compile(r"([cĵšžĉĝ][ː()]*)([ei])").sub(lambda match: match[1] + retracting[match[2]], pron)

        # syllabify, inserting @ at syllable boundaries

        # 1. insert @ after each vowel
        pron = sub(rf"({vowels}{accents}?)", r"\1@", pron)

        # 2. eliminate word-final @
        pron = sub(r"@+⁀$", "⁀", pron)

        # 3. move @ forward directly before any ‿⁀, as long as at least one consonant follows that; we will move it across ‿⁀ later
        pron = sub(rf"@([^@{vow}{acc}]*)([‿⁀]+[^‿⁀@{vow}{acc}])", r"\1@\2", pron)

        # 4. in a consonant cluster, move @ forward so it's before the last consonant
        pron = sub(rf"@([^‿⁀@{vow}{acc}]*)([^‿⁀@{vow}{acc}ːˑ()ʲ]ʲ?[ːˑ()]*‿?[{vow}{acc}])", r"\1@\2", pron)

        # 5. move @ backward if in the middle of a "permanent onset" cluster,
        #   e.g. sk, str, that comes before a vowel, putting the @ before
        #   the permanent onset cluster
        def matcher1(match: re.Match[str]) -> str:
            a, aund, b, bund, c, d = match.groups()
            if f"{a}{b}{c}" in perm_syl_onset or c == "j" and re.search(r"[čǰɕӂʲ]", b):
                return f"@{a}{aund}{b}{bund}{c}{d}"
            elif f"{b}{c}" in perm_syl_onset:
                return f"{a}{aund}@{b}{bund}{c}{d}"
            return ""

        pron = re.compile(
            rf"([^‿⁀@_{vow}{acc}]?)(_*)([^‿⁀@_{vow}{acc}])(_*)@([^‿⁀@{vow}{acc}ːˑ()ʲ])(ʲ?[ːˑ()]*[‿⁀]*[{vow}{acc}])"
        ).sub(matcher1, pron)

        # 6. if / is present (explicit syllable boundary), remove any @ (automatic boundary) and convert / to @
        if "/" in pron:
            pron = re.compile(rf"[^{vow}{acc}]+").sub(
                lambda match: x.replace("@", "").replace("/", "@") if "/" in (x := match[1]) else x, pron
            )

        # 7. remove @ followed by a final consonant cluster
        pron = sub(rf"@([^‿⁀@{vow}]+⁀)$", r"\1", pron)

        # 8. remove @ preceded by an initial consonant cluster (should only happen when / is inserted by user or in цз, чж sequences)
        pron = sub(rf"^(⁀[^‿⁀@{vow}]+)@", r"\1", pron)

        # 9. make sure @ isn't directly before linking ‿⁀
        pron = sub(r"@([‿⁀]+)", r"\1@", pron)

        # handle word-initial unstressed o and a; note, vowels always
        # followed by at least one char because of word-final ⁀
        #: after syllabification because syllabification doesn't know
        # about ɐ as a vowel
        pron = sub(rf"^⁀[ao]([^{acc}])", r"⁀ɐ\1", pron, flags=re.MULTILINE)

        # split by syllable
        syllable = pron.split("@")

        # create set of 1-based syllable indexes of stressed syllables (acute, grave, circumflex)
        stress = [bool(re.search(accents, syl)) for syl in syllable]

        # iterate syllable by syllable to handle stress marks, vowel allophony
        syl_conv: list[str] = []
        for j, syl in enumerate(syllable):
            # vowel allophony
            if stress[j]:
                # convert acute/grave/circumflex accent to appropriate
                # IPA marker of primary/secondary/unmarked stress
                alnum = 0
                syl = sub(r"(.*)́", r"ˈ\1", syl)
                syl = sub(r"(.*)̀", r"ˌ\1", syl)
                syl = syl.replace(CFLEX, "")
            elif stress[j + 1]:
                alnum = 1
            else:
                alnum = 2
            syl_conv.append(
                re.compile(vowels_c).sub(lambda match: allophones[a][alnum] if (a := match[1]) else "", syl)
            )

        pron = "".join(syl_conv)

        # Optional (j) before ɪ, which is always unstressed
        pron = sub(rf"([{ipa_vow}])jɪ", r"\1(j)ɪ", pron)

        # consonant assimilative palatalization of tn/dn/sn/zn, depending on whether [rl] precedes
        def matcher2(match: re.Match[str]) -> str:
            a, b, c = match.groups()
            return f"{a}{b}ʲ{c}" if not a else f"{a}{b}⁽ʲ⁾{c}"

        pron = re.compile(r"([rl]?)([ː()ˈˌ]*[dtsz])([ː()ˈˌ]*nʲ)").sub(matcher2, pron)

        # consonant assimilative palatalization of st/zd, depending on whether [rl] precedes
        pron = re.compile(r"([rl]?)([ˈˌ]?[sz])([ː()ˈˌ]*[td]ʲ)").sub(matcher2, pron)

        # general consonant assimilative palatalization
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

        # further assimilation before alveolopalatals
        pron = sub(r"n([ː()ˈˌ]*)([čǰɕӂ])", r"nʲ\1\2", pron)

        # optional palatal assimilation of вп, вб only word-initially
        pron = sub(r"⁀([ː()ˈˌ]*[fv])([ː()ˈˌ]*[pb]ʲ)", r"⁀\1⁽ʲ⁾\2", pron)

        # optional palatal assimilation of бв but not in обв-
        pron = sub(r"b([ː()ˈˌ]*vʲ)", r"b⁽ʲ⁾\1", pron)
        if re.search(rf"⁀o{accents}?bv", word[i]):
            # ə in case of a word with a preceding preposition
            pron = sub(r"⁀([ː()ˈˌ]*[ɐəo][ː()ˈˌ]*)b⁽ʲ⁾([ː()ˈˌ]*vʲ)", r"⁀\1b\2", pron)

        if re.search(r"ls[äạ]⁀", word[i]):
            pron = pron.replace("lsʲə⁀", "ls⁽ʲ⁾ə⁀")

        word[i] = pron

    text = f"[{' '.join(word)}]"

    # Front a and u between soft consonants. If between a soft and
    # optionally soft consonant (should only occur in that order, shouldn't
    # ever have a or u preceded by optionally soft consonant),
    # split the result into two. We only split into two even if there
    # happen to be multiple optionally fronted a's and u's to avoid
    # excessive numbers of possibilities (and it simplifies the code).
    # 1. First, temporarily add soft symbol to inherently soft consonants.
    text = sub(r"([čǰɕӂj])", r"\1ʲ", text)

    # 2. Handle case of [au] between two soft consonants
    text = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.ʲ)").sub(lambda match: match[1] + fronting[match[2]] + match[3], text)

    # 3. Handle [au] between soft consonant and optional j, which is still fronted
    text = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?\(jʲ\))").sub(
        lambda match: match[1] + fronting[match[2]] + match[3], text
    )

    # 4. Handle case of [au] between soft and optionally soft consonant
    if re.search(r"ʲ[ː()]*[auʊ][ˈˌ]?.⁽ʲ⁾", text):
        opt_hard = sub(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.)⁽ʲ⁾", r"\1\2\3", text)
        opt_soft = re.compile(r"(ʲ[ː()]*)([auʊ])([ˈˌ]?.)⁽ʲ⁾").sub(
            lambda match: match[1] + fronting[match[2]] + match[3] + "ʲ", text
        )
        text = f"{opt_hard}, {opt_soft}"

    # 5. Undo addition of soft symbol to inherently soft consonants.
    text = sub(r"([čǰɕӂj])ʲ", r"\1", text)

    # convert special symbols to IPA
    text = sub(r"[cĵ]ʲ", translit_conv_j, text)
    text = sub(r"[cčgĉĝĵǰšžɕӂ]", translit_conv, text)

    # Assimilation involving hiatus of ɐ and ə
    text = sub(r"ə([‿⁀]*)[ɐə]", r"ɐ\1ɐ", text)

    # eliminate ⁀ symbol at word boundaries
    # eliminate _ symbol that prevents assimilations
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
    '[məɫɐˈko]'
    >>> transcript("нево́лящий")
    '[nʲɪˈvolʲɪɕːɪɪ̯]'
    """
    return ipa(text, "", "", "")
