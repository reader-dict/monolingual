"""
Python conversion of the hi-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:hi-translit

Current version from 2024-08-24 17:04
  - https://en.wiktionary.org/w/index.php?title=Module:hi-translit&oldid=81376020
"""

import re
import unicodedata

conv = {
    # consonants
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
    "क़": "q",
    "ख़": "x",
    "ग़": "ġ",
    "ऴ": "ḻ",
    "ज़": "z",
    "ष़": "ẓ",
    "झ़": "ź",
    "ड़": "ṛ",
    "ढ़": "ṛh",
    "फ़": "f",
    "ऩ": "ṉ",
    "ऱ": "ṟ",
    "य़": "ẏ",
    "व़": "w",
    # vowel diacritics
    "ि": "i",
    "ु": "u",
    "े": "e",
    "ो": "o",
    "ॊ": "ǒ",
    "ॆ": "ě",
    "ा": "ā",
    "ी": "ī",
    "ू": "ū",
    "ृ": "ŕ",
    "ै": "ai",
    "ौ": "au",
    "ॉ": "ŏ",
    "ॅ": "ĕ",
    # vowel signs
    "अ": "a",
    "इ": "i",
    "उ": "u",
    "ए": "e",
    "ओ": "o",
    "आ": "ā",
    "ई": "ī",
    "ऊ": "ū",
    "ऎ": "ě",
    "ऒ": "ǒ",
    "ऋ": "ŕ",
    "ऐ": "ai",
    "औ": "au",
    "ऑ": "ŏ",
    "ऍ": "ĕ",
    "ॐ": "om",
    # chandrabindu
    "ँ": "̃",
    # anusvara
    "ं": "̃",
    # visarga
    "ः": "ḥ",
    # virama
    "्": "",
    # numerals
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
    # punctuation
    "।": ".",
    "॥": ".",
    "+": "",
    # abbreviation sign
    "॰": ".",
}

nasal_assim_short = {
    "क": "ङ",
    "ख": "ङ",
    "ग": "ङ",
    "घ": "ङ",
    "ङ": "ङ",
    "च": "ञ",
    "छ": "ञ",
    "ज": "ञ",
    "झ": "ञ",
    "ञ": "ञ",
    "ट": "ण",
    "ठ": "ण",
    "ड": "ण",
    "ढ": "ण",
    "ण": "ण",
    "त": "न",
    "थ": "न",
    "द": "न",
    "ध": "न",
    "न": "न",
    "प": "म",
    "फ": "म",
    "ब": "म",
    "भ": "म",
    "म": "म",
    "य": "ँ",
    "र": "न",
    "ल": "न",
    "व": "म",
    "श": "ञ",
    "ष": "ण",
    "स": "न",
    "ह": "ँ",
    "ज़": "न",
    "फ़": "म",
    "क़": "ङ",
    "ख़": "ङ",
    "ग़": "ङ",
    "ड़": "ँ",
    "ढ़": "ँ",
}

nasal_assim_long = {
    "क": "ँ",
    "ख": "ँ",
    "ग": "ङ",
    "घ": "ङ",
    "ङ": "ँ",
    "च": "ँ",
    "छ": "ँ",
    "ज": "ञ",
    "झ": "ञ",
    "ञ": "ँ",
    "ट": "ँ",
    "ठ": "ँ",
    "ड": "ण",
    "ढ": "ण",
    "ण": "ँ",
    "त": "ँ",
    "थ": "ँ",
    "द": "न",
    "ध": "न",
    "न": "ँ",
    "प": "ँ",
    "फ": "ँ",
    "ब": "म",
    "भ": "म",
    "म": "ँ",
    "ह": "ँ",
    "ज़": "न",
    "फ़": "म",
    "क़": "ङ",
    "ख़": "ङ",
    "ग़": "ङ",
    "ड़": "ँ",
    "ढ़": "ँ",
}

perm_cl = {"म्ल", "व्ल", "न्ल", "म्र", "व्र", "न्र", "ण्र", "न्न", "म्म", "ण्ण", "ल्ल", "र्र"}

all_cons = "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवषशसह"
special_cons = "यरलवहनमञण"
vowel = "*aिुृेोाीूैौॉॅॆॊ'"
vowel_sign = "अइउएओआईऊऋऐऔऑऍ'"
long_vowel = "ाीूेैोौआईऊएऐओऔ"
short_vowel = "*aिुृॆॊॅॉअइउऋऍऑऎऒ'"
syncope_pattern = rf"([{vowel}{vowel_sign}])(़?[{all_cons}])a(़?[{all_cons}])([ंँ]?[{vowel}{vowel_sign}])"


def tr(text: str) -> str:
    sub = re.sub

    # treat anusvara + nasal as geminate nasal after short vowels
    text = sub(rf"([{short_vowel}{all_cons}])ं([नम])", r"\1\2्\2", text)
    # word-final apostrophe (e.g. from bold formatting) does not delete schwa
    text = sub(rf"([{all_cons}]़?)('\\W)", r"\1a\2", text)
    text = sub(rf"([{all_cons}]़?)(')$", r"\1a\2", text)
    text = sub(rf"([{all_cons}]़?)([{vowel}्]?)", lambda m: m[1] + (m[2] if m[2] != "" else "a"), text)

    words = re.findall(r"[ऀ-ॣॱ-ॿa*]+", text)
    for word in words:
        orig_word = word
        word = word[::-1]

        # Handle special word-initial schwa
        def replace_initial_a(m: re.Match[str]) -> str:
            opt, first, second, third = m.groups()
            cluster = first + second + third
            # Cluster not in perm_cl and first in special_cons and second is halant
            if first in special_cons and second == "्" and cluster not in perm_cl:
                return f"a{opt}{first}{second}{third}"
            # e.g. य[ीिई]
            if re.match(r"य[ीिई]", first + second):
                return f"a{opt}{first}{second}{third}"
            return opt + first + second + third

        word = sub(rf"^a(़?)([{all_cons}])(.)(.?)", replace_initial_a, word)

        while re.search(syncope_pattern, word):
            word = sub(syncope_pattern, r"\1\2\3\4", word)

        word = word[::-1]

        special_vowel = "ीेैोौईऐओऔ"
        normal_vowel = "*aिुाूृॆॅॊॉअइउआऊऋऎऍऒऑए'"
        # nasalization with candrabindu on special vowels
        word = sub(rf"([{special_vowel}])ँ(.़?)", lambda m: f"{m[1]}̃{m[2]}", word)
        # sometimes chandrabindu != anusvara
        word = sub(
            rf"([{normal_vowel}])ं([सशषवयकखटतथदडपचछ]़?)",
            lambda m: f"{m[1]}{nasal_assim_short.get(m[2], '̃')}{m[2]}",
            word,
        )
        word = sub(rf"([{normal_vowel}])ँ([सशषवयकखटतथदडपचछ]़?)", lambda m: f"{m[1]}̃{m[2]}", word)
        word = word.replace("ँ", "ं")
        word = sub(rf"([{short_vowel}])ं(.़?)", lambda m: m[1] + (nasal_assim_short.get(m[2], "̃")) + m[2], word)
        word = sub(rf"([{long_vowel}])ं(.़?)", lambda m: m[1] + (nasal_assim_long.get(m[2], "̃")) + m[2], word)
        text = text.replace(orig_word, word, 1)

    text = sub(r".़?", lambda m: conv.get(m[0], m[0]), text)
    text = sub(r"a([iu])̃", r"a͠\1", text)
    text = text.replace("ñz", "nz")
    text = text.replace("*", "a")

    return unicodedata.normalize("NFC", text)


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:hi-translit/testcases&oldid=78024529

    >>> transliterate("सँस")
    'sãs'
    >>> transliterate("संस्कार")
    'sanskār'
    >>> transliterate("संविधान")
    'samvidhān'
    >>> transliterate("उसाँस")
    'usā̃s'
    >>> transliterate("मैंने")
    'ma͠ine'
    >>> transliterate("ऊँचाई")
    'ū̃cāī'
    >>> transliterate("ऊंचाई")
    'ūñcāī'
    >>> transliterate("साँप")
    'sā̃p'
    >>> transliterate("सूँघना")
    'sūṅghnā'
    >>> transliterate("सूंघना")
    'sūṅghnā'
    >>> transliterate("शंका")
    'śaṅkā'
    >>> transliterate("अशांत")
    'aśānt'
    >>> transliterate("सर्व")
    'sarv'
    >>> transliterate("अन्न")
    'ann'
    >>> transliterate("भिन्न")
    'bhinn'
    >>> transliterate("बांह")
    'bā̃h'
    >>> transliterate("बाँह")
    'bā̃h'
    >>> transliterate("साँझ")
    'sāñjh'
    >>> transliterate("बाँटना")
    'bā̃ṭnā'
    >>> transliterate("चाँपना")
    'cā̃pnā'
    >>> transliterate("प्रमेय")
    'pramey'
    >>> transliterate("उपप्रमेय")
    'upapramey'
    >>> transliterate("चायवाला")
    'cāyvālā'
    >>> transliterate("डायनासोर")
    'ḍāynāsor'
    >>> transliterate("साँवला")
    'sā̃vlā'
    >>> transliterate("कोयला")
    'koylā'
    >>> transliterate("ज़िंदगी")
    'zindgī'
    >>> transliterate("धड़कने")
    'dhaṛakne'
    >>> transliterate("लपट")
    'lapaṭ'
    >>> transliterate("लपटें")
    'lapṭẽ'
    >>> transliterate("उपयोग")
    'upyog'
    >>> transliterate("आलप्पुष़ा")
    'ālappuẓā'
    >>> transliterate("कपड़ा")
    'kapṛā'
    >>> transliterate("नज़दीक")
    'nazdīk'
    >>> transliterate("जुड़वाँ")
    'juṛvā̃'
    >>> transliterate("कॉफ़ी")
    'kŏfī'
    >>> transliterate("फ़िल्म")
    'film'
    >>> transliterate("फ़ावड़ा")
    'fāvṛā'
    >>> transliterate("करना")
    'karnā'
    >>> transliterate("करन")
    'karan'
    >>> transliterate("वस्त्र")
    'vastra'
    >>> transliterate("भस्म")
    'bhasma'
    >>> transliterate("अस्पताल")
    'aspatāl'
    >>> transliterate("उत्तम")
    'uttam'
    >>> transliterate("क़लम")
    'qalam'
    >>> transliterate("देवनागरी")
    'devnāgrī'
    >>> transliterate("नमकीन")
    'namkīn'
    >>> transliterate("वेद")
    'ved'
    >>> transliterate("राम")
    'rām'
    >>> transliterate("रचना")
    'racnā'
    >>> transliterate("अंग्रेज़")
    'aṅgrez'
    >>> transliterate("अंगरेज़")
    'aṅgrez'
    >>> transliterate("विमला")
    'vimlā'
    >>> transliterate("भारतीय")
    'bhārtīya'
    >>> transliterate("समझा")
    'samjhā'
    >>> transliterate("समझ")
    'samajh'
    >>> transliterate("सुलोचना")
    'sulocnā'
    >>> transliterate("भारत")
    'bhārat'
    >>> transliterate("दूःख")
    'dūḥkh'
    >>> transliterate("नहीं")
    'nahī̃'
    >>> transliterate("।")
    '.'
    >>> transliterate("प्लीज़")
    'plīz'
    >>> transliterate("कृपया")
    'kŕpyā'
    >>> transliterate("मानहानि")
    'mānhāni'
    >>> transliterate("तिरस्कार")
    'tiraskār'
    >>> transliterate("प्रतिबिंब")
    'pratibimb'
    >>> transliterate("सुवर्ण")
    'suvarṇ'
    >>> transliterate("संपत्ति")
    'sampatti'
    >>> transliterate("प्रवेशमार्ग")
    'praveśmārg'
    >>> transliterate("अंतःस्राव")
    'antaḥsrāv'
    >>> transliterate("बहिष्कार")
    'bahiṣkār'
    >>> transliterate("व्यवच्छेद")
    'vyavacched'
    >>> transliterate("जलावतनी")
    'jalāvatnī'
    >>> transliterate("स्वत्व+हरण")
    'svatvaharaṇ'
    >>> transliterate("जब्ती")
    'jabtī'
    >>> transliterate("निस्सारण")
    'nissāraṇ'
    >>> transliterate("मैथमैटिक्स")
    'maithmaiṭiks'
    >>> transliterate("पिक्चर")
    'pikcar'
    >>> transliterate("संगमरमर")
    'saṅgmarmar'
    >>> transliterate("तलवार")
    'talvār'
    >>> transliterate("अलमारी")
    'almārī'
    >>> transliterate("उब्द्रशाला")
    'ubdraśālā'
    >>> transliterate("टमाटर")
    'ṭamāṭar'
    >>> transliterate("पेपरमिंट")
    'peparmiṇṭ'
    >>> transliterate("इंगलिश")
    'iṅgliś'
    >>> transliterate("अन्तर्राष्ट्रीय")
    'antarrāṣṭrīya'
    >>> transliterate("रेफ्रिजरेटर")
    'rephrijreṭar'
    >>> transliterate("रेफरिजरेटर")
    'rephrijreṭar'
    >>> transliterate("रेफ्रिज्रेटर")
    'rephrijreṭar'
    >>> transliterate("रेफरिज्रेटर")
    'rephrijreṭar'
    >>> transliterate("अधिकांश")
    'adhikāñś'
    >>> transliterate("अज़रबैजान")
    'azarbaijān'
    >>> transliterate("अज़र्बैजान")
    'azarbaijān'
    >>> transliterate("अफ्रीका")
    'aphrīkā'
    >>> transliterate("अफरीका")
    'aphrīkā'
    >>> transliterate("अफगानिस्तान")
    'aphgānistān'
    >>> transliterate("अफ्गानिस्तान")
    'aphgānistān'
    >>> transliterate("अफगानिसतान")
    'aphgānistān'
    >>> transliterate("अफ्गानिसतान")
    'aphgānistān'
    >>> transliterate("स्फिंकटर")
    'sphiṅkṭar'
    >>> transliterate("मांडवी")
    'māṇḍvī'
    >>> transliterate("लंपसम")
    'lampsam'
    >>> transliterate("मयराम")
    'mayrām'
    >>> transliterate("मैय्य")
    'maiyya'
    >>> transliterate("रंगद्रव्य")
    'raṅgadravya'
    >>> transliterate("रंगदार")
    'raṅgdār'
    >>> transliterate("उमंगभर")
    'umaṅgbhar'
    >>> transliterate("उमंगहीन")
    'umaṅghīn'
    >>> transliterate("तंगहाल")
    'taṅghāl'
    >>> transliterate("तत्वमीमांसा")
    'tatvamīmānsā'
    >>> transliterate("तनहाई")
    'tanhāī'
    >>> transliterate("त्रिकोणमिति")
    'trikoṇmiti'
    >>> transliterate("दिसम्बर")
    'disambar'
    >>> transliterate("दिसंबर")
    'disambar'
    >>> transliterate("दिसमबर")
    'disambar'
    >>> transliterate("दिलचस्प")
    'dilcasp'
    >>> transliterate("दुरूपयोग")
    'durūpyog'
    >>> transliterate("पचहत्तर")
    'pachattar'
    >>> transliterate("ढ")
    'ḍha'
    >>> transliterate("किंमत")
    'kimmat'
    >>> transliterate("हैं")
    'ha͠i'
    >>> transliterate("डाउनलोड")
    'ḍāunloḍ'
    >>> transliterate("इंद्र+धनुष")
    'indradhanuṣ'
    >>> transliterate("आगमन")
    'āgman'
    >>> transliterate("अनुमति")
    'anumti'
    >>> transliterate("सम्मति")
    'sammati'
    >>> transliterate("संमति")
    'sammati'
    >>> transliterate("मंज़ूर")
    'manzūr'
    >>> transliterate("प्रदेशीय")
    'pradeśīya'
    >>> transliterate("नाईं")
    'nāī̃'
    >>> transliterate("ख़ुशबुओं")
    'xuśbuõ'
    >>> transliterate("रहस्य क्या")
    'rahasya kyā'
    """
    return tr(text)
