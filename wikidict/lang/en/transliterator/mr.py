"""
Python conversion of the mr-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:mr-translit

Current version from 2025-02-23 10:32
  - https://en.wiktionary.org/w/index.php?title=Module:mr-translit&oldid=84014919
"""

import re
import unicodedata

conv = {
    "क": "k",
    "ख": "kh",
    "ग": "g",
    "घ": "gh",
    "ङ": "ṅ",
    "च": "c",
    "छ": "ch",
    "ज": "j",
    "झ": "jh",
    "ञ": "ñ",
    "ट": "ṭ",
    "ठ": "ṭh",
    "ड": "ḍ",
    "ढ": "ḍh",
    "ण": "ṇ",
    "त": "t",
    "थ": "th",
    "द": "d",
    "ध": "dh",
    "न": "n",
    "प": "p",
    "फ": "ph",
    "ब": "b",
    "भ": "bh",
    "म": "m",
    "य": "y",
    "र": "r",
    "ल": "l",
    "व": "v",
    "ळ": "ḷ",
    "श": "ś",
    "ष": "ṣ",
    "स": "s",
    "ह": "h",
    "ऱ": "r",
    "ज़": "j̈",
    "झ़": "j̈h",
    "च़": "ċ",
    "ि": "i",
    "ु": "u",
    "े": "e",
    "ो": "o",
    "ा": "ā",
    "ी": "ī",
    "ू": "ū",
    "ृ": "ru",
    "ै": "ai",
    "ौ": "au",
    "ॉ": "ŏ",
    "ॅ": "ĕ",
    "अ": "a",
    "इ": "i",
    "उ": "u",
    "ए": "e",
    "ओ": "o",
    "आ": "ā",
    "ई": "ī",
    "ऊ": "ū",
    "ऋ": "ru",
    "ऐ": "ai",
    "औ": "au",
    "ऑ": "ŏ",
    "ॲ": "ĕ",
    "ऍ": "ĕ",
    "ॐ": "om",
    "ँ": "̃",
    "ं": "ṁ",
    "ः": "ḥ",
    "्": "",
    "०": "0",
    "१": "1",
    "२": "2",
    "३": "3",
    "४": "4",
    "५": "5",
    "६": "6",
    "७": "7",
    "८": "8",
    "९": "9",
    "।": ".",
    "॥": ".",
    "+": "",
    "॰": ".",
}

nasal_assim = {
    "क": "ङ",
    "ख": "ङ",
    "ग": "ङ",
    "घ": "ङ",
    "च़": "न",
    "ज़": "न",
    "झ़": "न",
    "च": "ञ",
    "छ": "ञ",
    "ज": "ञ",
    "झ": "ञ",
    "ट": "ण",
    "ठ": "ण",
    "ड": "ण",
    "ढ": "ण",
    "प": "म",
    "फ": "म",
    "ब": "म",
    "भ": "म",
    "म": "म",
    "य": "इ",
    "र": "उ",
    "ल": "ल",
    "व": "उ",
    "श": "उ",
    "ष": "उ",
    "स": "उ",
    "ह": "उ",
}

all_cons = "कखगघङचछजझञटठडढतथदधपफबभशषसयरलवहणनमळ"
special_cons = "दतयरलवहनम"
vowel = r"\*aिुृेोाीूैौॉॅ"
vowel_sign = "अइउएओआईऊऋऐऔऑॲऍ"
syncope_pattern = rf"([{vowel}{vowel_sign}])(़?[{all_cons}])a(़?[{all_cons}])([ंँ]?[{vowel}{vowel_sign}])"


def tr(text: str) -> str:
    sub = re.sub

    text = text.replace(r"ाँ", "ॉं")
    text = text.replace(r"ँ", "ॅं")
    text = sub(rf"([^{vowel}{vowel_sign}])ं ", r"\1अ ", text)
    text = sub(rf"([^{vowel}{vowel_sign}])ं$", r"\1अ", text)
    text = sub(rf"([{all_cons}]़?)([{vowel}्]?)", lambda m: f"{m[1]}{m[2] or 'a'}", text)

    for word in re.findall(r"[ऀ-ॿa]+", text):
        orig_word = word
        word = sub(rf"^a(़?[{all_cons}][{vowel}{vowel_sign}])", r"\1", word[::-1])
        while re.search(syncope_pattern, word):
            word = sub(syncope_pattern, r"\1\2\3\4", word)

        def repl_nasal(m: re.Match[str]) -> str:
            succ, prev = m[1], m[2]
            if f"{succ}{prev}" == "a":
                return f"्म{prev}"
            if succ == "" and re.match(f"[{vowel}]", prev):
                return f"̃{prev}"
            return f"{succ}{nasal_assim.get(succ, 'n')}{prev}"

        word = sub(r"(़?.?)ं(.)", repl_nasal, word)
        text = text.replace(orig_word, word[::-1], 1)

    text = sub(r".़?", lambda m: conv.get(m[0], m[0]), text)
    text = text.replace("ñjñ", "ndny")
    text = text.replace("jñ", "dny")
    text = re.sub(r"a([iu])̃", r"a͠\1", text)
    text = text.replace("aa", "a")

    return unicodedata.normalize("NFC", text)


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:mr-translit/testcases&oldid=84015128

    >>> transliterate("दगड")
    'dagaḍ'
    >>> transliterate("दहशत")
    'dahśat'
    >>> transliterate("दऱ्या")
    'daryā'
    >>> transliterate("दहा")
    'dahā'
    >>> transliterate("दही")
    'dahī'
    >>> transliterate("दचकणे")
    'dacakṇe'
    >>> transliterate("खुद्द")
    'khudda'
    >>> transliterate("शुद्ध")
    'śuddha'
    >>> transliterate("घट्ट")
    'ghaṭṭa'
    >>> transliterate("भिन्न")
    'bhinna'
    >>> transliterate("मार्ग")
    'mārga'
    >>> transliterate("कर्म")
    'karma'
    >>> transliterate("शब्द")
    'śabda'
    >>> transliterate("पत्र")
    'patra'
    >>> transliterate("वृक्ष")
    'vrukṣa'
    >>> transliterate("महाराष्ट्र")
    'mahārāṣṭra'
    >>> transliterate("भारत")
    'bhārat'
    >>> transliterate("मराठी")
    'marāṭhī'
    >>> transliterate("हृदय")
    'hruday'
    >>> transliterate("गंगा")
    'gaṅgā'
    >>> transliterate("लंड")
    'laṇḍa'
    >>> transliterate("कंबल")
    'kambal'
    >>> transliterate("रक्त")
    'rakta'
    >>> transliterate("काव्य")
    'kāvya'
    >>> transliterate("मंद")
    'manda'
    >>> transliterate("उंच़")
    'unċa'
    >>> transliterate("कृपा")
    'krupā'
    >>> transliterate("ज्ञान")
    'dnyān'
    >>> transliterate("ऱ्हास")
    'rhās'
    >>> transliterate("दर्या")
    'daryā'
    >>> transliterate("कैरी")
    'kairī'
    >>> transliterate("हौस")
    'haus'
    >>> transliterate("संरक्षण")
    'saurakṣaṇ'
    >>> transliterate("संशय")
    'sauśay'
    >>> transliterate("दंष्ट्र")
    'dauṣṭra'
    >>> transliterate("हंस")
    'hausa'
    >>> transliterate("संयोग")
    'saiyog'
    >>> transliterate("संलग्न")
    'sallagna'
    >>> transliterate("संवाद")
    'sauvād'
    >>> transliterate("सिंह")
    'siuha'
    >>> transliterate("संहार")
    'sauhār'
    >>> transliterate("संज्ञा")
    'sandnyā'
    >>> transliterate("माझं")
    'mājha'
    >>> transliterate("बॅट")
    'bĕṭ'
    >>> transliterate("बँक")
    'bĕṅka'
    >>> transliterate("ॲप")
    'ĕp'
    >>> transliterate("ऍप")
    'ĕp'
    >>> transliterate("कॉट")
    'kŏṭ'
    >>> transliterate("हाँग काँग")
    'hŏṅga kŏṅga'
    >>> transliterate("ऑस्ट्रेलिया")
    'ŏsṭreliyā'
    >>> transliterate("च्या")
    'cyā'
    >>> transliterate("तुझ्या")
    'tujhyā'
    >>> transliterate("च़ार")
    'ċār'
    >>> transliterate("चार")
    'cār'
    >>> transliterate("काच़ा")
    'kāċā'
    >>> transliterate("काचा")
    'kācā'
    >>> transliterate("च़राच़र")
    'ċarāċar'
    >>> transliterate("चराचर")
    'carācar'
    >>> transliterate("ज़प")
    'j̈ap'
    >>> transliterate("जप")
    'jap'
    >>> transliterate("मोज़णे")
    'moj̈ṇe'
    >>> transliterate("लाज़")
    'lāj̈'
    >>> transliterate("झ़कझ़क")
    'j̈hakj̈hak'
    >>> transliterate("झकझक")
    'jhakjhak'
    >>> transliterate("झ़ापड")
    'j̈hāpaḍ'
    >>> transliterate("झापड")
    'jhāpaḍ'
    >>> transliterate("झीज़")
    'jhīj̈'
    >>> transliterate("चीज़")
    'cīj̈'
    >>> transliterate("अंग")
    'aṅga'
    >>> transliterate("अंगे")
    'aṅge'
    >>> transliterate("अंगं")
    'aṅga'
    """
    return tr(text)
