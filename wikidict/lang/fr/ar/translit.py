"""
manual conversion of Module:ar-translit from
https://fr.wiktionary.org/wiki/Module:ar-translit

Current version: 13 février 2021 21:12
    https://fr.wiktionary.org/w/index.php?title=Module:ar-translit&oldid=29172743
"""

import re
import string

zwnj = "‌"  # zero-width non-joiner
alif_madda = "آ"
alif_hamza_below = "إ"
alif = "ا"
taa_marbuuTa = "ة"
laam = "ل"
waaw = "و"
alif_maqSuura = "ى"
yaa = "ي"
fatHataan = "ً"
Dammataan = "ٌ"
kasrataan = "ٍ"
fatHa = "َ"
Damma = "ُ"
kasra = "ِ"
shadda = "ّ"
sukuun = "ْ"
dagger_alif = "ٰ"
alif_waSl = "ٱ"
# zwj = "‍" # zero-width joiner
lrm = "‎"  # left-to-right mark
rlm = "‏"  # right-to-left mark

tt = {
    # consonants
    "ب": "b",
    "ت": "t",
    "ث": "ṯ",
    "ج": "j",
    "ح": "ḥ",
    "خ": "ḵ",
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
    "ع": "ʿ",
    "غ": "ḡ",
    "ف": "f",
    "ق": "q",
    "ك": "k",
    "ڪ": "k",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "ه": "h",
    # tāʾ marbūṭa (special) - always after a fátḥa (a), silent at the end of
    # an utterance, "t" in ʾiḍāfa or with pronounced tanwīn. We catch
    # most instances of tāʾ marbūṭa before we get to this stage.
    taa_marbuuTa: "t",  # tāʾ marbūṭa
    # control characters
    zwnj: "-",  # ZWNJ (zero-width non-joiner)
    # zwj: "",  # ZWJ (zero-width joiner)
    # rare letters
    "پ": "p",
    "چ": "č",
    "ڤ": "v",
    "ڥ": "v",
    "گ": "g",
    "ڨ": "g",
    "ڧ": "q",
    # semivowels or long vowels, alif, hamza, special letters
    "ا": "ā",  # ʾalif
    # hamzated letters
    "أ": "ʾ",  # hamza over alif
    alif_hamza_below: "ʾ",  # hamza under alif
    "ؤ": "ʾ",  # hamza over wāw
    "ئ": "ʾ",  # hamza over yā
    "ء": "ʾ",  # hamza on the line
    # long vowels
    waaw: "w",  # "ū" after ḍamma (u) and not before diacritic
    yaa: "y",  # "ī" after kasra (i) and not before diacritic
    alif_maqSuura: "ā",  # ʾalif maqṣūra
    alif_madda: "ʾā",  # ʾalif madda
    alif_waSl: "",  # hamzatu l-waṣl
    dagger_alif: "ā",  # ʾalif xanjariyya = dagger ʾalif (Koranic diacritic)
    # short vowels, šádda and sukūn
    fatHataan: "an",  # fatḥatan
    Dammataan: "un",  # ḍammatan
    kasrataan: "in",  # kasratan
    fatHa: "a",  # fatḥa
    Damma: "u",  # ḍamma
    kasra: "i",  # kasra
    # šadda - doubled consonant
    sukuun: "",  # sukūn - no vowel
    # ligatures
    "ﻻ": "lā",
    "ﷲ": "llāh",
    # taṭwīl
    "ـ": "",  # taṭwīl, no sound
    # numerals
    "١": "1",
    "٢": "2",
    "٣": "3",
    "٤": "4",
    "٥": "5",
    "٦": "6",
    "٧": "7",
    "٨": "8",
    "٩": "9",
    "٠": "0",
    # punctuation (leave on separate lines)
    "؟": "?",  # question mark
    "«": "“",  # quotation mark
    "»": "”",  # quotation mark
    "٫": ".",  # decimal point
    "٬": ",",  # thousands separator
    "٪": "%",  # percent sign
    "،": ",",  # comma
    "؛": ";",  # semicolon
}

sun_letters = "تثدذرزسشصضطظلن"

# For use in implementing sun-letter assimilation of ال (al-)
ttsun1 = {}
ttsun2 = {}
# For use in implementing elision of al-
sun_letters_tr = ""
for cp in sun_letters:
    ttsun1[cp] = tt[cp]
    ttsun2[f"l-{cp}"] = f"{tt[cp]}-{cp}"
    sun_letters_tr += tt[cp]

consonants_needing_vowels = "بتثجحخدذرزسشصضطظعغفقكڪلمنهپچڤگڨڧأإؤئءةﷲ"
# consonants on the right side; includes alif madda
rconsonants = f"{consonants_needing_vowels}ويآ"
# consonants on the left side; does not include alif madda
lconsonants = f"{consonants_needing_vowels}وي"
# Arabic semicolon, comma, question mark; taṭwīl; period, exclamation point,
# single quote for bold/italic, double quotes for quoted material
punctuation = "؟،؛" + "ـ" + ".!'" + '"'
space_like = r"\s'\""
space_like_class = f"[{space_like}]"
numbers = "١٢٣٤٥٦٧٨٩٠"


before_diacritic_checking_subs: list[list[str]] = [
    # transformations prior to checking for diacritics #######
    # convert llh for allāh into ll+shadda+dagger-alif+h
    ["لله", "للّٰه"],
    # shadda+short-vowel (including tanwīn vowels, i.e. -an -in -un) gets
    # replaced with short-vowel+shadda during NFC normalisation, which
    # MediaWiki does for all Unicode strings; however, it makes the
    # transliteration process inconvenient, so undo it.
    [
        f"([{fatHataan}{Dammataan}{kasrataan}{fatHa}{Damma}{kasra}{dagger_alif}]){shadda}",
        shadda + r"\1",
    ],
    # ignore alif jamīla (otiose alif in 3pl verb forms)
    #     #1: handle ḍamma + wāw + alif (final -ū)
    [Damma + waaw + alif, Damma + waaw],
    #     #2: handle wāw + sukūn + alif (final -w in -aw in defective verbs)
    #     this must go before the generation of w, which removes the waw here.
    [waaw + sukuun + alif, waaw + sukuun],
    # ignore final alif or alif maqṣūra following fatḥatan (e.g. in accusative
    # singular or words like عَصًا "stick" or هُذًى "guidance"; this is called
    # tanwin nasb)
    [f"{fatHataan}[{alif}{alif_maqSuura}]", fatHataan],
    # same but with the fatḥatan placed over the alif or alif maqṣūra
    # instead of over the previous letter (considered a misspelling but
    # common)
    [f"[{alif}{alif_maqSuura}]{fatHataan}", fatHataan],
    # tāʾ marbūṭa should always be preceded by fatḥa, alif, alif madda or
    # dagger alif; infer fatḥa if not
    [
        f"([{lconsonants}]{shadda}?){alif}([{rconsonants}])",
        rf"\1{fatHa}{alif}\2",
    ],
    # similarly for alif between consonants, possibly marked with shadda
    # (does not apply to initial alif, which is silent when not marked with
    # hamza, or final alif, which might be pronounced as -an)
    [
        f"([{lconsonants}]{shadda}?){alif}([{rconsonants}])",
        rf"\1{fatHa}{alif}\2",
    ],
    # infer fatḥa in case of non-fatḥa + alif/alif-maqṣūra + dagger alif
    [
        f"([^{fatHa}])([{alif}{alif_maqSuura}]{dagger_alif})",
        rf"\1{fatHa}\2",
    ],
    # infer kasra in case of hamza-under-alif not + kasra
    [f"{alif_hamza_below}([^{kasra}])", alif_hamza_below + kasra + r"\1"],
    # ignore dagger alif placed over regular alif or alif maqṣūra
    [f"([{alif}{alif_maqSuura}]){dagger_alif}", r"\1"],
    # rest of these concern definite article alif-lām #####
    # in kasra/ḍamma + alif + lam, make alif into hamzatu l-waṣl, so we
    # handle cases like بِالتَّوْفِيق (bi-t-tawfīq) correctly
    [f"([{Damma}{kasra}]){alif}{laam}", r"\1" + alif_waSl + laam],
    # al + consonant + shadda (only recognize word-initially if regular alif): remove shadda
    [f"^({alif}{fatHa}?{laam}[{lconsonants}]){shadda}", r"\1"],
    [
        f"({space_like_class}{alif}{fatHa}?{laam}[{lconsonants}]){shadda}",
        r"\1",
    ],
    [f"({alif_waSl}{fatHa}?{laam}[{lconsonants}]){shadda}", r"\1"],
    # handle l- hamzatu l-waṣl or word-initial al-
    [f"^{alif}{fatHa}?{laam}", "al-"],
    [f"({space_like_class}){alif}{fatHa}?{laam}", r"\1al-"],
    # next one for bi-t-tawfīq
    [f"([{Damma}{kasra}]){alif_waSl}{fatHa}?{laam}", r"\1-l-"],
    # next one for remaining hamzatu l-waṣl (at beginning of word)
    [f"{alif_waSl}{fatHa}?{laam}", "l-"],
    # special casing if the l in al- has a shadda on it (as in الَّذِي "that"),
    # so we don't mistakenly double the dash
    [f"l-{shadda}", "ll"],
    # implement assimilation of sun letters
    # ["l-[" + sun_letters + "]", ttsun2], # lasconic: cf (1) in tr()
]


has_diacritics_subs = [
    # FIXME! What about lam-alif ligature?
    # remove punctuation and shadda
    # must go before removing final consonants
    (rf"[{punctuation}{shadda}]", ""),
    # Remove consonants at end of word or utterance, so that we're OK with
    # words lacking iʿrāb (must go before removing other consonants).
    # If you want to catch places without iʿrāb, comment out the next two lines.
    (rf"[{lconsonants}]$", ""),
    (rf"[{lconsonants}]({space_like_class})", r"\1"),
    # remove consonants (or alif) when followed by diacritics
    # must go after removing shadda
    # do not remove the diacritics yet because we need them to handle
    # long-vowel sequences of diacritic + pseudo-consonant
    (
        rf"[{lconsonants}{alif}]([{fatHataan}{Dammataan}{kasrataan}{fatHa}{Damma}{kasra}{sukuun}{dagger_alif}])",
        r"\1",
    ),
    # the following two must go after removing consonants w/diacritics because
    # we only want to treat vocalic wāw/yā' in them (we want to have removed
    # wāw/yā' followed by a diacritic)
    # remove ḍamma + wāw
    (Damma + waaw, ""),
    # remove kasra + yā'
    (kasra + yaa, ""),
    # remove fatḥa/fatḥatan + alif/alif-maqṣūra
    (rf"[{fatHataan}{fatHa}][{alif}{alif_maqSuura}]", ""),
    # remove diacritics
    (
        rf"[{fatHataan}{Dammataan}{kasrataan}{fatHa}{Damma}{kasra}{sukuun}{dagger_alif}]",
        "",
    ),
    # remove numbers, hamzatu l-waṣl, alif madda
    (rf"[{numbers}ٱآ]", ""),
    # remove non-Arabic characters
    (r"[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]", ""),
]


def has_diacritics(text: str) -> bool:
    text = re.sub(f"[{lrm}{rlm}]", "", text)
    for sub in has_diacritics_subs:
        text = re.sub(sub[0], sub[1], text)
    return len(text) == 0


# Transliterate the word(s) in TEXT. LANG (the language) and SC (the script)
# are ignored. OMIT_I3RAAB means leave out final short vowels (ʾiʿrāb).
# GRAY_I3RAAB means render transliterate short vowels (ʾiʿrāb) in gray.
# FORCE_TRANSLIT causes even non-vocalized text to be transliterated
# (normally the function checks for non-vocalized text and returns nil,
# since such text is ambiguous in transliteration).
def tr(text: str) -> str:
    """
    >>> tr("اَلْعَرَبِيَّة‏")
    'al-ʿarabiyya'
    >>> tr("اَلْعَرَبِيَّة.")
    'al-ʿarabiyya.'
    >>> tr("لِلْكِتَاب")
    'lilkitāb'
    >>> tr("لِلتَّأْكِيد")
    ''
    >>> tr("لِلَّبَنِ")
    'lillabani'
    >>> tr("لِللَّبَنِ")
    ''
    >>> tr("شْنِيتْزَل")
    'šnītzal'
    >>> tr("عُظْمَى")
    'ʿuẓmā'
    >>> tr("إِحْدَى")
    'ʾiḥdā'

    lasconic: this one is different in en testcases and fr implementation...
    we follow fr implementation
    >>> tr("خَطَإٍ")
    'ḵaṭaʾiin'

    >>> tr("بِٱلتَّأْكِيد")
    'bi-t-taʾkīd'
    >>> tr("بِالتَّأْكِيد")
    'bi-t-taʾkīd'
    >>> tr("بِالتَأْكِيد")
    'bi-t-taʾkīd'
    >>> tr("بِالكِتَاب")
    'bi-l-kitāb'
    >>> tr("بِالْكِتَاب")
    'bi-l-kitāb'
    >>> tr("اَللُّغَةُ ٱلْعَرَبِيَّةُ")
    'al-luḡatu l-ʿarabiyyatu'
    >>> tr("اَللُّغَةُ الْعَرَبِيَّةُ")
    'al-luḡatu l-ʿarabiyyatu'
    >>> tr("نَسُوا")
    'nasū'
    >>> tr("رَمَوْا")
    'ramaw'
    >>> tr("عَصًا")
    'ʿaṣan'
    >>> tr("هُدًى")
    'hudan'
    >>> tr("عَصاً")
    'ʿaṣan'
    >>> tr("هُدىً")
    'hudan'
    >>> tr("كاتِب")
    'kātib'
    >>> tr("كُتّاب")
    'kuttāb'
    >>> tr("إلاه")
    'ʾilāh'
    >>> tr("كاتب")
    ''
    >>> tr("رَبّ")
    'rabb'
    >>> tr("نَوَاةٌ")
    'nawātun'
    >>> tr("اَلشَّدَّة")
    'aš-šadda'
    >>> tr("شَدَّة الشَكْل")
    'šadda(t) aš-šakl'
    >>> tr("مُعَادَاة")
    'muʿādāh'
    >>> tr("مِرْآة")
    'mirʾāh'
    >>> tr("صلاح")
    ''
    >>> tr("اِيبَ")
    'ība'
    >>> tr("دِيُون")
    'diyūn'
    >>> tr("دُوِين")
    'duwīn'
    >>> tr("الَّذِي")
    'allaḏī'
    >>> tr("رَأَيْتُ ٱبْنَهُ")
    'raʾaytu bnahu'
    >>> tr("ڪُفُوًا")
    'kufuwan'
    >>> tr("حُووِلَ")
    'ḥūwila'
    >>> tr("دُوَيْبَّة")
    'duwaybba'

    From en:ar-pronunciation testcases
    >>> tr("عَبْدُ اللّٰه")
    'ʿabdu llāh'
    """
    # make it possible to call this function from a template
    for sub in before_diacritic_checking_subs:
        text = re.sub(sub[0], sub[1], text)

    # ["l-[" + sun_letters + "]", ttsun2], # (1)
    text = re.sub(f"l-[{sun_letters}]", lambda m: ttsun2[m.group(0)], text)

    if not has_diacritics(text):
        return ""

    # transformations after checking for diacritics #######
    # Replace plain alif with hamzatu l-waṣl when followed by fatḥa/ḍamma/kasra.
    # Must go after handling of initial al-, which distinguishes alif-fatḥa
    # from alif w/hamzatu l-waṣl. Must go before generation of ū and ī, which
    # eliminate the ḍamma/kasra.
    text = re.sub(f"{alif}([{fatHa}{Damma}{kasra}])", alif_waSl + r"\1", text)
    # ḍamma + waw not followed by a diacritic is ū, otherwise w
    text = re.sub(
        Damma
        + waaw
        + "([^"
        + fatHataan
        + Dammataan
        + kasrataan
        + fatHa
        + Damma
        + kasra
        + shadda
        + sukuun
        + dagger_alif
        + "])",
        r"ū\1",
        text,
    )

    text = re.sub(Damma + waaw + "$", "ū", text)
    # kasra + yaa not followed by a diacritic (or ū from prev step) is ī, otherwise y
    text = re.sub(
        kasra
        + yaa
        + "([^"
        + fatHataan
        + Dammataan
        + kasrataan
        + fatHa
        + Damma
        + kasra
        + shadda
        + sukuun
        + dagger_alif
        + "ū])",
        r"ī\1",
        text,
    )
    text = re.sub(kasra + yaa + "$", "ī", text)
    # convert shadda to double letter.
    text = re.sub(f"(.){shadda}", r"\1\1", text)

    # text = re.sub(rf"[{fatHataan}{Dammataan}{kasrataan}]", "", text)
    # text = re.sub(rf"[{fatHa}{Damma}{kasra}]({space_like_class})", r"\1", text)
    # text = re.sub(rf"[{fatHa}{Damma}{kasra}]$", "", text)

    # tāʾ marbūṭa should not be rendered by -t if word-final even when
    # ʾiʿrāb (desinential inflection) is shown; instead, use (t) before
    # whitespace, nothing when final; but render final -ﺍﺓ and -ﺁﺓ as -āh,
    # consistent with Wehr's dictionary
    # Left-to-right or right-to-left mark at end of text will prevent tāʾ marbūṭa
    # from being transliterated correctly.
    text = text.replace(lrm, "")
    text = text.replace(rlm, "")

    text = re.sub(f"([{alif}{alif_madda}]){taa_marbuuTa}$", r"\1h", text)
    # Ignore final tāʾ marbūṭa (it appears as "a" due to the preceding
    # short vowel). Need to do this after graying or omitting word-final
    # ʾiʿrāb.
    text = re.sub(f"{taa_marbuuTa}$", "", text)
    text = re.sub(rf"{taa_marbuuTa}([{re.escape(string.punctuation)}])", r"\1", text)

    # CAUTION here, lasconic removed if omit_i3raab
    # show ʾiʿrāb in transliteration
    text = re.sub(f"{taa_marbuuTa}({space_like_class})", r"(t)\1", text)

    # tatwīl should be rendered as - at beginning or end of word. It will
    # be rendered as nothing in the middle of a word
    # FIXME, do we want this?
    text = re.sub("^ـ", "-", text)
    text = re.sub(f"({space_like_class})ـ", r"\1-", text)
    text = re.sub("ـ$", "-", text)
    text = re.sub(f"ـ({space_like_class})", r"-\1", text)

    # Now convert remaining Arabic chars according to table.
    for k, v in tt.items():
        text = text.replace(k, v)
    text = re.sub("aā", "ā", text)
    # Implement elision of al- after a final vowel. We do this
    # conservatively, only handling elision of the definite article rather
    # than elision in other cases of hamzat al-waṣl (e.g. form-I imperatives
    # or form-VII and above verbal nouns) partly because elision in
    # these cases isn't so common in MSA and partly to avoid excessive
    # elision in case of words written with initial bare alif instead of
    # properly with hamzated alif. Possibly we should reconsider.
    # At the very least we currently don't handle elision of الَّذِي (allaḏi)
    # correctly because we special-case it to appear without the hyphen;
    # perhaps we should reconsider that.
    text = re.sub(f"([aiuāīū]'* +'*)a([{sun_letters_tr}]-)", r"\1\2", text)
    # Special-case the transliteration of allāh, without the hyphen
    text = re.sub("^(a?)l-lāh", r"\1llāh", text)
    text = re.sub(f"({space_like_class}a?)l-lāh", r"\1llāh", text)

    return text
