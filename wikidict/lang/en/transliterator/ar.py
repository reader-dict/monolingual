"""
Python conversion of the ar-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:ar-translit

Current version from 2025-04-24 11:34
  - https://en.wiktionary.org/w/index.php?title=Module:ar-translit&oldid=84628499
"""

import re

# Unicode constants
U = chr
ZWNJ = U(0x200C)  # zero-width non-joiner
ALIF_MADDA = U(0x622)
ALIF_HAMZA_BELOW = U(0x625)
ALIF = U(0x627)
TAA_MARBUUTA = U(0x629)
LAAM = U(0x644)
WAAW = U(0x648)
ALIF_MAQSUURA = U(0x649)
YAA = U(0x64A)
FATHATAAN = U(0x64B)
DAMMATAAN = U(0x64C)
KASRATAAN = U(0x64D)
FATHA = U(0x64E)
DAMMA = U(0x64F)
KASRA = U(0x650)
SHADDA = U(0x651)
SUKUUN = U(0x652)
DAGGER_ALIF = U(0x670)
ALIF_WASL = U(0x671)
LRM = U(0x200E)  # left-to-right mark
RLM = U(0x200F)  # right-to-left mark
ALLADI_MARKER = U(0xFFF0)  # Special marker for allaḏī variants

# Character mappings
TRANSLITERATION_MAP = str.maketrans(
    {
        # consonants
        ord("ب"): "b",
        ord("ت"): "t",
        ord("ث"): "ṯ",
        ord("ج"): "j",
        ord("ح"): "ḥ",
        ord("خ"): "ḵ",
        ord("د"): "d",
        ord("ذ"): "ḏ",
        ord("ر"): "r",
        ord("ز"): "z",
        ord("س"): "s",
        ord("ش"): "š",
        ord("ص"): "ṣ",
        ord("ض"): "ḍ",
        ord("ط"): "ṭ",
        ord("ظ"): "ẓ",
        ord("ع"): "ʕ",
        ord("غ"): "ḡ",
        ord("ف"): "f",
        ord("ق"): "q",
        ord("ك"): "k",
        ord("ڪ"): "k",
        ord("ل"): "l",
        ord("م"): "m",
        ord("ن"): "n",
        ord("ه"): "h",
        # tāʾ marbūṭa
        ord(TAA_MARBUUTA): "t",
        # control characters
        ord(ZWNJ): "-",
        # rare letters
        ord("پ"): "p",
        ord("چ"): "č",
        ord("ژ"): "ž",
        ord("ڤ"): "v",
        ord("ڥ"): "v",
        ord("گ"): "g",
        ord("ڨ"): "g",
        ord("ڧ"): "q",
        ord("ڢ"): "f",
        ord("ں"): "n",
        ord("ڭ"): "g",
        # alif and hamza
        ord("ا"): "ā",
        ord("أ"): "ʔ",
        ord(ALIF_HAMZA_BELOW): "ʔ",
        ord("ؤ"): "ʔ",
        ord("ئ"): "ʔ",
        ord("ء"): "ʔ",
        # long vowels
        ord(WAAW): "w",
        ord(YAA): "y",
        ord(ALIF_MAQSUURA): "ā",
        ord(ALIF_MADDA): "ʔā",
        ord(ALIF_WASL): "",
        ord(DAGGER_ALIF): "ā",
        # short vowels and tanween
        ord(FATHATAAN): "an",
        ord(DAMMATAAN): "un",
        ord(KASRATAAN): "in",
        ord(FATHA): "a",
        ord(DAMMA): "u",
        ord(KASRA): "i",
        ord(SUKUUN): "",
        # ligatures
        ord("ﻻ"): "lā",
        ord("ﷲ"): "llāh",
        # tatweel
        ord("ـ"): "",
        # numerals
        ord("١"): "1",
        ord("٢"): "2",
        ord("٣"): "3",
        ord("٤"): "4",
        ord("٥"): "5",
        ord("٦"): "6",
        ord("٧"): "7",
        ord("٨"): "8",
        ord("٩"): "9",
        ord("٠"): "0",
        # punctuation
        ord("؟"): "?",
        ord("«"): "'",
        ord("»"): "'",
        ord("٫"): ".",
        ord("٬"): ",",
        ord("٪"): "%",
        ord("،"): ",",
        ord("؛"): ";",
    }
)

# Character sets
SUN_LETTERS = "تثدذرزسشصضطظلن"
CONSONANTS_NEEDING_VOWELS = "بتثجحخدذرزسشصضطظعغفقكڪلمنهپچژڤگڨڧڢںڭأإؤئءةﷲ"
RCONSONANTS = f"{CONSONANTS_NEEDING_VOWELS}ويآ"
LCONSONANTS = f"{CONSONANTS_NEEDING_VOWELS}وي"
SPACE_LIKE = r"\s'"
SPACE_LIKE_CLASS = f"[{SPACE_LIKE}]"
NUMBERS = "١٢٣٤٥٦٧٨٩٠"
PUNCTUATION = r"[!\"#$%&'()*+,-./:;<=>?@[\\\]^_`{|}~]"

# Build sun letter mappings
SUN_MAP1 = {ch: TRANSLITERATION_MAP[ord(ch)] for ch in SUN_LETTERS}
SUN_MAP2 = {f"l-{ch}": f"{TRANSLITERATION_MAP[ord(ch)]}-{ch}" for ch in SUN_LETTERS}
SUN_LETTERS_TR = "".join(TRANSLITERATION_MAP[ord(ch)] for ch in SUN_LETTERS)

# Pre-diacritic transformations
PRE_DIACRITIC_SUBS = [
    # Koranic marks and presentation forms
    (U(0x06E1), SUKUUN),
    (U(0x06DA), ""),
    (U(0x06DF), ""),
    (U(0x08F0), U(0x64B)),
    (U(0x08F1), U(0x64C)),
    (U(0x08F2), U(0x64D)),
    (U(0x06E4), ""),
    (U(0x06D6), ""),
    (U(0x06E5), "و"),
    (U(0x06E6), "ي"),
    # Convert llh for allāh
    ("لله", "للّٰه"),
    # Fix shadda+vowel order
    (f"([{FATHATAAN}{DAMMATAAN}{KASRATAAN}{FATHA}{DAMMA}{KASRA}{DAGGER_ALIF}]){SHADDA}", rf"{SHADDA}\1"),
    # Ignore initial gemination
    (f" ([{LCONSONANTS}]){SHADDA}", r" \1"),
    # Handle alif jamīla
    (f"{DAMMA}{WAAW}{ALIF}", f"{DAMMA}{WAAW}"),
    (f"{WAAW}{SUKUUN}{ALIF}", f"{WAAW}{SUKUUN}"),
    # Handle tanween nasb
    (f"{FATHATAAN}[{ALIF}{ALIF_MAQSUURA}]", FATHATAAN),
    (f"[{ALIF}{ALIF_MAQSUURA}]{FATHATAAN}", FATHATAAN),
    # Infer fatha before taa marbuuta
    (f"([^{FATHA}{ALIF}{ALIF_MADDA}{DAGGER_ALIF}]){TAA_MARBUUTA}", rf"\1{FATHA}{TAA_MARBUUTA}"),
    # Infer fatha between consonants
    (f"([{LCONSONANTS}]{SHADDA}?){ALIF}([{RCONSONANTS}])", rf"\1{FATHA}{ALIF}\2"),
    # Infer fatha with alif + dagger alif
    (f"([^{FATHA}])([{ALIF}{ALIF_MAQSUURA}]{DAGGER_ALIF})", rf"\1{FATHA}\2"),
    # Infer kasra with hamza under alif
    (f"{ALIF_HAMZA_BELOW}([^{KASRA}{KASRATAAN}])", rf"{ALIF_HAMZA_BELOW}{KASRA}\1"),
    # Remove dagger alif over regular alif
    (f"([{ALIF}{ALIF_MAQSUURA}]){DAGGER_ALIF}", r"\1"),
    # Handle definite article
    (f"([{DAMMA}{KASRA}]){ALIF}{LAAM}", rf"\1{ALIF_WASL}{LAAM}"),
    # Remove shadda after al-
    (f"^({ALIF}{FATHA}?{LAAM}[{LCONSONANTS}]){SHADDA}", r"\1"),
    (f"([{SPACE_LIKE}]{ALIF}{FATHA}?{LAAM}[{LCONSONANTS}]){SHADDA}", r"\1"),
    (f"({ALIF_WASL}{FATHA}?{LAAM}[{LCONSONANTS}]){SHADDA}", r"\1"),
    # Handle al- conversions
    (f"^{ALIF}{FATHA}?{LAAM}", "al-"),
    (f"([{SPACE_LIKE}]){ALIF}{FATHA}?{LAAM}", r"\1al-"),
    (f"([{DAMMA}{KASRA}]){ALIF_WASL}{FATHA}?{LAAM}", r"\1-l-"),
    (f"{ALIF_WASL}{FATHA}?{LAAM}", "l-"),
    # Special casing for shadda on lam
    (f"l-{SHADDA}", f"l{ALLADI_MARKER}l"),
]


def apply_substitutions(text: str, subs: list[tuple[str, str]]) -> str:
    """Apply regex substitutions sequentially."""
    sub = re.sub

    for pattern, replacement in subs:
        if isinstance(replacement, dict):

            def repl_func(match: re.Match[str]) -> str:
                return replacement.get(match.group(0), match.group(0))

            text = sub(pattern, repl_func, text)
        else:
            text = sub(pattern, replacement, text)
    return text


def tr(text: str) -> str:
    sub = re.sub

    # Apply pre-diacritic transformations
    text = apply_substitutions(text, PRE_DIACRITIC_SUBS)

    # Add sun letter assimilation
    text = apply_substitutions(text, [(f"l-[{SUN_LETTERS}]", SUN_MAP2)])  # type: ignore[list-item]

    # Post-diacritic transformations
    # Replace alif with hamzatu l-wasl
    text = sub(f"{ALIF}([{FATHA}{DAMMA}{KASRA}])", rf"{ALIF_WASL}\1", text)

    # Handle long vowels
    vowel_pattern = f"[^{FATHATAAN}{DAMMATAAN}{KASRATAAN}{FATHA}{DAMMA}{KASRA}{SHADDA}{SUKUUN}{DAGGER_ALIF}ū]"
    text = sub(f"{DAMMA}{WAAW}({vowel_pattern})", r"ū\1", text)
    text = sub(f"{DAMMA}{WAAW}$", "ū", text)
    text = sub(f"{KASRA}{YAA}({vowel_pattern})", r"ī\1", text)
    text = sub(f"{KASRA}{YAA}$", "ī", text)

    # Convert shadda to double letter
    text = sub(f"(.){SHADDA}", r"\1\1", text)

    # Handle taa marbuuta
    text = sub(f"[{LRM}{RLM}]", "", text)  # Remove direction marks
    text = sub(f"([{ALIF}{ALIF_MADDA}]){TAA_MARBUUTA}$", r"\1h", text)
    text = sub(f"{TAA_MARBUUTA}$", "", text)
    text = sub(rf"{TAA_MARBUUTA}({PUNCTUATION})", r"\1", text)

    text = sub(f"{TAA_MARBUUTA}([{SPACE_LIKE}])", r"(t)\1", text)

    # Handle tatweel
    text = sub("^ـ", "-", text)
    text = sub(f"([{SPACE_LIKE}])ـ", r"\1-", text)
    text = sub("ـ$", "-", text)
    text = sub(f"ـ([{SPACE_LIKE}])", r"-\1", text)

    # Main character transliteration
    text = text.translate(TRANSLITERATION_MAP)

    # Fix double alif
    text = text.replace("aā", "ā")

    # Implement elision of al- after vowels
    elision_pattern = f"([aiuāīū]'* +')a([{SUN_LETTERS_TR}][-{ALLADI_MARKER}])"
    text = sub(elision_pattern, r"\1\2", text)

    # Remove alladi marker
    text = text.replace(ALLADI_MARKER, "")

    # Special case for Allah
    text = sub("^(a?)l-lāh", r"\1llāh", text)
    text = sub(f"([{SPACE_LIKE}]a?)l-lāh", r"\1llāh", text)

    # Compress multiple spaces
    text = sub(r"(\s)\s+", r"\1", text)

    return text


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:ar-translit/testcases&oldid=78710147

    >>> transliterate("اَلْعَرَبِيَّة.")
    'al-ʕarabiyya.'
    >>> transliterate("لِلْكِتَاب")
    'lilkitāb'
    >>> transliterate("لِلتَّأْكِيد")
    'lilttaʔkīd'
    >>> transliterate("لِلَّبَنِ")
    'lillabani'
    >>> transliterate("لِللَّبَنِ")
    'lilllabani'
    >>> transliterate("شْنِيتْزَل")
    'šnītzal'
    >>> transliterate("عُظْمَى")
    'ʕuẓmā'
    >>> transliterate("إِحْدَى")
    'ʔiḥdā'
    >>> transliterate("خَطَإٍ")
    'ḵaṭaʔin'
    >>> transliterate("بِٱلتَّأْكِيد")
    'bi-t-taʔkīd'
    >>> transliterate("بِالتَّأْكِيد")
    'bi-t-taʔkīd'
    >>> transliterate("بِالتَأْكِيد")
    'bi-t-taʔkīd'
    >>> transliterate("بِالكِتَاب")
    'bi-l-kitāb'
    >>> transliterate("بِالْكِتَاب")
    'bi-l-kitāb'
    >>> transliterate("اَللُّغَةُ ٱلْعَرَبِيَّةُ")
    'al-luḡatu l-ʕarabiyyatu'
    >>> transliterate("اَللُّغَةُ الْعَرَبِيَّةُ")
    'al-luḡatu al-ʕarabiyyatu'
    >>> transliterate("نَسُوا")
    'nasū'
    >>> transliterate("رَمَوْا")
    'ramaw'
    >>> transliterate("دَعَوُا اللّٰهَ")
    'daʕawuā allāha'
    >>> transliterate("عَصًا")
    'ʕaṣan'
    >>> transliterate("هُدًى")
    'hudan'
    >>> transliterate("عَصاً")
    'ʕaṣan'
    >>> transliterate("هُدىً")
    'hudan'
    >>> transliterate("كاتِب")
    'kātib'
    >>> transliterate("كُتّاب")
    'kuttāb'
    >>> transliterate("إلاه")
    'ʔilāh'
    >>> transliterate("كاتب")
    'kātb'
    >>> transliterate("رَبّ")
    'rabb'
    >>> transliterate("نَوَاةٌ")
    'nawātun'
    >>> transliterate("اَلشَّدَّة")
    'aš-šadda'
    >>> transliterate("شَدَّة الشَكْل")
    'šadda(t) aš-šakl'
    >>> transliterate("مُعَادَاة")
    'muʕādāh'
    >>> transliterate("مِرْآة")
    'mirʔāh'
    >>> transliterate("صلاح")
    'ṣlāḥ'
    >>> transliterate("اِيبَ")
    'ība'
    >>> transliterate("دِيُون")
    'diyūn'
    >>> transliterate("دُوِين")
    'duwīn'
    >>> transliterate("الَّذِي")
    'allaḏī'
    >>> transliterate("رَأَيْتُ ابْنَهُ")
    'raʔaytu ābnahu'
    >>> transliterate("رَأَيْتُ ٱبْنَهُ")
    'raʔaytu bnahu'
    >>> transliterate("ڪُفُوًا")
    'kufuwan'
    >>> transliterate("أَحَدٌ ٱللّٰهُ ٱلصَّمَدُ")
    'ʔaḥadun llāhu ṣ-ṣamadu'
    >>> transliterate("حُووِلَ")
    'ḥūwila'
    >>> transliterate("دُوَيْبَّة")
    'duwaybba'
    """
    return tr(text)
