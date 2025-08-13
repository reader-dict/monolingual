"""
Python conversion of the fa-cls-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:fa-cls-translit

Current version from 2025-05-25 01:59
  - https://en.wiktionary.org/w/index.php?title=Module:fa-cls-translit&oldid=84923309
"""

import re

# Unicode character definitions
U = chr
fat_hataan = U(0x64B)  # اً, tanvin-e nasb (تنوین نصب)
dammataan = U(0x64C)  # un
kasrataan = U(0x64D)  # in
zabar = U(0x64E)
zer = U(0x650)
pesh = U(0x64F)
tashdid = U(0x651)  # also called shadda
jazm = "ْ"
he = "ه"
zwnj = U(0x200C)
high_hmz = U(0x654)
lrm = U(0x200E)  # left-to-right mark
rlm = U(0x200F)  # right-to-left mark
balticons = "ڃڇڑڗݜݨݩǩ"

consonants = "بپتټٹثجچحخدډڈذرزژسشصضطظعغفقکگلمنؤهئء" + balticons
consonants2 = "ءبپتټٹثجچحخدډڈذرزژسشصضطظعغفقکگلمنوؤهیئywة" + balticons  # including semivowels
vowels = "āēīōū"
semivowel = "یو"
hes = "هح"
diacritics = "َُِّْٰ"
zzp = "َُِ"
alif_wasla = "ٱ"
space_like = r"\s'" + '"'
space_like_class = f"[{space_like}{zwnj}]"

# Character mapping dictionary
mapping = {
    "آ": "ā",
    "ب": "b",
    "پ": "p",
    "ت": "t",
    "ث": "s",
    "ج": "j",
    "چ": "č",
    "ح": "h",
    "خ": "x",
    "د": "d",
    "ذ": "z",
    "ر": "r",
    "ز": "z",
    "ژ": "ž",
    "س": "s",
    "ش": "š",
    "ص": "s",
    "ض": "z",
    "ط": "t",
    "ظ": "z",
    "غ": "ġ",
    "ف": "f",
    "ق": "q",
    "ک": "k",
    "گ": "g",
    "ل": "l",
    "م": "m",
    "ن": "n",
    "و": "ō",
    "ی": "ē",
    "۔": ".",
    "ه": "h",
    "ع": "'",
    "ء": "'",
    "ئ": "'",
    "ؤ": "'",
    "أ": "'",
    # diacritics
    zabar: "a",
    zer: "i",
    pesh: "u",
    jazm: "",
    zwnj: "-",
    high_hmz: "-yi",
    # ligatures
    "ﻻ": "lā",
    "ﷲ": "allāh",
    # kashida
    "ـ": "-",
    # alif_wasla
    alif_wasla: "",
    # numerals
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
    "۰": "0",
    # punctuation
    "؟": "?",
    "،": ",",
    "؛": ";",
    "«": """, "»": """,
    "٪": "%",
    "؉": "‰",
    "٫": ".",
    "٬": ",",
    # regional characters
    "ټ": "ṭ",
    "ٹ": "ṭ",
    "ډ": "ḍ",
    "ڈ": "ḍ",
    "ڃ": "ž",
    "ڇ": "č̣",
    "ڑ": "ṛ",
    "ڗ": "dz",
    "ݜ": "ṣ",
    "ݨ": "ng",
    "ݩ": "ny",
    "ھ": "h",
    "ے": "e",
}

punctuation = r":\(\)\[\]*&٫؛؟،ـ«\".'!»٪؉۔`,/–—\{\}"
numbers = "۱۲۳۴۵۶۷۸۹۰"

ain = "ع"
alif = "ا"
malif = "آ"
hamza = "ء"
ye = "ی"
ye2 = "ئ"
vao = "و"
dagger_alif = U(0x670)
marbuta = U(0x629)
te = "ت"
ye3 = "ے"
laam = "ل"
vowel = f"[{vowels}{zzp}{jazm}{semivowel}{malif}]"
sun_letters = "تثدذرزسشصضطظلن"

# Substitution patterns
before_diacritic_checking_subs = [
    (U(0x06E5), "و"),
    (U(0x06E6), "ی"),
    ("ہ", he),
    (f"ک{high_hmz}", "ǩ"),
    (f"([{fat_hataan}{zzp}{dagger_alif}]){tashdid}", rf"{tashdid}\1"),
    (f"{alif}{fat_hataan}", f"{zabar}ن"),
    (f"{fat_hataan}{alif}", f"{zabar}ن"),
    (f"{jazm}{ye}{dagger_alif}", f"{jazm}{ye}{zabar}{alif}"),
    (f"{zabar}[{ye}{vao}]{dagger_alif}", f"{zabar}{alif}"),
    (f"{ye}{dagger_alif}", f"{zabar}{alif}"),
    (ye3, ye),
    (r"[أإ]", ye2),
    (f"^ـ{zabar}{alif}", f"ـ{malif}"),
    (f"^ـ([{zzp}])", rf"ـ{alif}\1"),
    (f"{zabar}{dagger_alif}", f"{zabar}{alif}"),
    (dagger_alif, f"{zabar}{alif}"),
    (fat_hataan, f"{zabar}ن"),
    (dammataan, f"{pesh}ن"),
    (kasrataan, f"{zer}ن"),
    (f"{alif_wasla}{laam}", "l-"),
    (alif_wasla, ""),
    (f"([{consonants2}]{tashdid}?[{pesh}{zer}]){alif}{laam}{jazm}?([{consonants2}])", r"\1-l-\2"),
    (f"([{consonants2}]{tashdid}?[{pesh}{zer}][{vao}{ye}]){alif}{laam}{jazm}?([{consonants2}])", r"\1-l-\2"),
    (f"([{consonants2}]{tashdid}?[{zzp}]{space_like_class}){alif}{laam}{jazm}?([{consonants2}])", r"\1l-\2"),
    (
        f"([{consonants2}]{tashdid}?[{pesh}{zer}][{vao}{ye}]{space_like_class}){alif}{laam}{jazm}?([{consonants2}])",
        r"\1l-\2",
    ),
    (f"{marbuta}([{zzp}]){alif}{laam}", rf"{te}\1-{laam}-"),
    (f"l-([{sun_letters}]){tashdid}", rf"\1{jazm}-\1"),
    (f"l-{laam}{tashdid}", f"{laam}{laam}"),
    (f"l-{laam}", f"{laam}{laam}"),
    ("l-", f"{laam}-"),
    (f"{marbuta}([{zzp}]){alif}", rf"{te}\1-"),
    (f"{marbuta}([{zzp}{jazm}])", rf"{te}\1"),
    (marbuta, he),
    (f"([{consonants2}][{zzp}])({space_like_class}){alif}{laam}([{jazm}{laam}])", rf"\1\2{laam}\3"),
    (f"{laam}{laam}{tashdid}", f"{laam}{tashdid}"),
    (f"(خ){vao}{zabar}{alif}", rf"\1{zabar}{alif}"),
    (f"(خ){vao}{zabar}", rf"\1{pesh}"),
    (f"(خ){vao}{ye}([^{zzp}{jazm}])", rf"\1{ye}\2"),
    (zwnj, "-"),
    (f"{jazm}{alif}", f"{jazm}-{alif}"),
    (f"{zabar}{jazm}", "-"),
]

has_diacritics_subs = [
    ("l-", ""),
    (f"[{sun_letters}]{jazm}-", ""),
    (f"[{consonants2}]([{zzp}]){space_like_class}{alif}{laam}", ""),
    (f"[{punctuation}{tashdid}{high_hmz}{numbers}{fat_hataan}]", ""),
    (f"[{consonants}]$", ""),
    (f"[{consonants}]({space_like_class})", r"\1"),
    (f"[{consonants}]-", "-"),
    (f"[{consonants2}]([{zer}{pesh}]){alif}{laam}", laam),
    (f"[{consonants2}]([{zer}{pesh}])-{alif}{laam}", laam),
    (f"[{consonants2}]{jazm}", ""),
    (f"[{consonants2}]{jazm}{malif}", ""),
    (f"[{consonants2}]{zabar}{alif}", ""),
    (f"[{consonants}{alif}][{semivowel}{zzp}]([{semivowel}])([{semivowel}])", r"\1\2"),
    (f"[{consonants2}{alif}][{zzp}][{semivowel}]", ""),
    (f"[{consonants2}{alif}][{zzp}{jazm}{semivowel}]", ""),
    (f"[{alif}{consonants2}][{zzp}][{semivowel}]", ""),
    (malif, ""),
    (f"{jazm}{alif}[{zzp}]", ""),
    (f"[{consonants2}{alif}][{zzp}]", ""),
    (f"[{consonants2}{alif}{semivowel}][{semivowel}]", ""),
    (f"[{numbers}ٱآ]", ""),
    (r"\s", ""),
    ("-", ""),
    (f"[{semivowel}]", ""),
    (f"({vowel})", ""),
]


def tr(text: str) -> str:
    """Transliterate Persian/Farsi text to Latin script."""

    sub = re.sub

    # Apply pre-diacritic checking substitutions
    for pattern, replacement in before_diacritic_checking_subs:
        text = sub(pattern, replacement, text)

    # Define word boundaries
    text = text.replace("#", "HASHTAG")
    text = sub("^", "#", text)
    text = sub("$", "#", text)
    text = sub(r" \| ", "# | #", text)
    text = sub(r"\s", "# #", text)
    text = sub("\n", "#\n#", text)
    text = sub(f"([{punctuation}])", r"#\1#", text)
    text = f"##{sub(' ', '# #', text)}##"
    text = text.replace("-", "#-#")

    # Character reformatting and exceptions
    text = (
        text.replace(high_hmz, f"#{high_hmz}#")
        .replace(f"#{vao}#", "#u#")
        .replace(f"#{vao}{jazm}{malif}", f"#w-{malif}")
    )

    # Tashdeed handling
    text = sub(f"([{consonants}]){tashdid}", r"\1\1", text)
    text = sub(f"([{consonants}]){tashdid}([{zzp}])", r"\1\1\2", text)
    text = sub(f"([{consonants}])([{zzp}]){tashdid}", r"\1\1\2", text)
    text = sub(f"{ye}([{zzp}]){tashdid}", r"yy\1", text)
    text = sub(f"{vao}([{zzp}]){tashdid}", r"ww\1", text)
    text = sub(f"{ye}{tashdid}([{zzp}])", r"yy\1", text)
    text = sub(f"{vao}{tashdid}([{zzp}])", r"ww\1", text)

    # Alif handling
    text = sub(f"([{consonants2}]){zabar}{alif}", r"\1ā", text)
    text = sub(f"([{consonants2}]){alif}", r"\1ā", text)
    text = text.replace(f"{jazm}{malif}", "'ā")
    text = sub(f"([{consonants2}]){malif}", r"\1'ā", text)
    text = (
        text.replace(f"{alif}{ye}", "ē")
        .replace(f"{alif}{vao}", "ō")
        .replace(f"{alif}{zer}{ye}", "ī")
        .replace(f"{alif}{pesh}{vao}", "ū")
    )
    text = sub(f"{tashdid}{alif}", f"{tashdid}ā", text)

    # Semi vowel conversions
    text = text.replace(f"{ye}ā", "yā").replace(f"{vao}ā", "wā")
    text = sub(f"{vao}([{diacritics}{zzp}])", r"w\1", text)
    text = sub(f"{ye}([{diacritics}{zzp}])", r"y\1", text)
    text = sub(f"{ye}([{semivowel}])([{semivowel}])", r"ē\1\2", text)
    text = sub(f"{vao}([{semivowel}])([{semivowel}])", r"ō\1\2", text)
    text = sub(f"([{diacritics}{zzp}]){ye}([{semivowel}])", r"\1y\2", text)
    text = sub(f"([{diacritics}{zzp}]){vao}([{semivowel}])", r"\1w\2", text)
    text = sub(f"([{consonants}]){ye}([{semivowel}])", r"\1y\2", text)
    text = sub(f"([{consonants}]){vao}([{semivowel}])", r"\1w\2", text)

    # Vaav/waaw/vao conversions
    text = text.replace(f"{pesh}{vao}", "ū")
    text = sub(f"{vao}([{diacritics}{zzp}])", r"w\1", text)
    text = sub(f"({vowel}){vao}", r"\1w", text)

    # Ye conversions
    text = text.replace(f"{zer}{ye}", "ī")
    text = sub(f"{ye}([{diacritics}{zzp}])", r"y\1", text)
    text = sub(f"({vowel}){ye}", r"\1y", text)

    # Alif with short vowel
    text = sub(f"{alif}([{zzp}])", r"\1", text)

    # Final changes - izafa
    text = text.replace(f"ē{zer}#", "ē-yi#").replace(f"{zer}y{zer}#", "ī-yi#")
    text = sub(f"([^{consonants}{jazm}])y{zer}#", r"\1-yi#", text)
    text = sub(f"([{consonants2}]){zer}#", r"\1-i#", text)
    text = sub(f"(['\"])##{zer}#", r"\1-i#", text)

    # Izafa corrections
    text = sub(f"-i##({space_like_class})##([{sun_letters}]{jazm}#-#)", r"i\1\2", text)
    text = sub(f"-i#-#([{sun_letters}]#-#)", r"i-\1", text)

    # He deletion
    text = sub(f"([{zzp}]){he}#{zwnj}", r"\1-", text)
    text = sub(f"([{zzp}]){he}#", r"\1#", text)
    text = text.replace(f"#{ain}", "#")

    # Remove hashtags
    text = text.replace("#", "").replace("HASHTAG", "#").replace(lrm, "").replace(rlm, "")

    # Convert all characters using mapping
    text = "".join(mapping.get(char, char) for char in text)

    # Final corrections
    text = text.replace("āa", "ā").replace("aaa", "ā").replace("āā", "ā").replace("aa", "ā")
    text = sub(f"ī([{vowels}])", r"iy\1", text)
    text = sub(f"ū([{vowels}])", r"uw\1", text)

    return text


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:fa-cls-translit/testcases&oldid=85038156

    >>> transliterate("سَرْاَنْجَام")
    'sar-anjām'
    >>> transliterate("کُروز")
    'kurōz'
    >>> transliterate("دَهْ")
    'dah'
    >>> transliterate("دَه")
    'da'
    >>> transliterate("سُؤَال")
    "su'āl"
    >>> transliterate("کُرُوز")
    'kurūz'
    >>> transliterate("وَاوْ")
    'wāw'
    >>> transliterate("نَوْروز")
    'nawrōz'
    >>> transliterate("قَهْوَه‌اِی")
    'qahwa-ī'
    >>> transliterate("قَهْوَه‌یِی")
    'qahwa-yī'
    >>> transliterate("خْوَانْدَن")
    'xwāndan'
    >>> transliterate("خْویش")
    'xwēš'
    >>> transliterate("خْوَد")
    'xwad'
    >>> transliterate("چَامَه‌سَرَایِی")
    'čāma-sarāyī'
    >>> transliterate("طَنِین")
    'tanīn'
    >>> transliterate("لِهٰذَا")
    'lihāzā'
    >>> transliterate("قَهْرًا")
    'qahran'
    >>> transliterate("عَصاً")
    'asan'
    >>> transliterate("خَانَه")
    'xāna'
    >>> transliterate("کورِیَایِ شُمَالِی")
    'kōriyā-yi šumālī'
    >>> transliterate("ضَمَّه")
    'zamma'
    >>> transliterate("ضَمِّهْ")
    'zammih'
    >>> transliterate("کِه")
    'ki'
    >>> transliterate("کِهْ")
    'kih'
    >>> transliterate("اَرْمَنِسْتَان")
    'armanistān'
    >>> transliterate("بَاکُو")
    'bākū'
    >>> transliterate("کَسی")
    'kasē'
    >>> transliterate("بَرَادَرِ بُزُرْگ")
    'barādar-i buzurg'
    >>> transliterate("قُرُونِ وُسْطیٰ")
    'qurūn-i wustā'
    >>> transliterate("دَر-آمَد")
    'dar-āmad'
    >>> transliterate("بَازِیِ شَطْرَنْج")
    'bāzī-yi šatranj'
    >>> transliterate("ایرَانِیَان")
    'ērāniyān'
    >>> transliterate("صُبَاح")
    'subāh'
    >>> transliterate("صُبْح")
    'subh'
    >>> transliterate("صُبْه")
    'subh'
    >>> transliterate("دُروغ گویْ")
    'durōġ gōy'
    >>> transliterate("او")
    'ō'
    >>> transliterate("وَ")
    'wa'
    >>> transliterate(" و ")
    ' u '
    >>> transliterate("بَه نَامِ خُدَا")
    'ba nām-i xudā'
    >>> transliterate("جَوَانِی")
    'jawānī'
    >>> transliterate("شَاهْنَامَه")
    'šāhnāma'
    >>> transliterate("زِنْدَگِی")
    'zindagī'
    >>> transliterate("زِنْدَه‌گِی")
    'zinda-gī'
    >>> transliterate("میوَهٔ جَاپَانِی")
    'mēwa-yi jāpānī'
    >>> transliterate("نُوید")
    'nuwēd'
    >>> transliterate("دُخْتَرَْبَچَّه")
    'duxtar-bačča'
    >>> transliterate("کِیَه")
    'kiya'
    >>> transliterate("کُرُوَاسِیَا")
    'kuruwāsiyā'
    >>> transliterate("مِیَایِین")
    'miyāyīn'
    >>> transliterate("مْیَایین")
    'myāyēn'
    >>> transliterate("طِلَّا")
    'tillā'
    >>> transliterate("لیکِن")
    'lēkin'
    >>> transliterate("بَچَّهٔ لَطِیفَه کَلَان اَسْت")
    'bačča-yi latīfa kalān ast'
    >>> transliterate("مَعْرُوف و مَجْهُول")
    "ma'rūf u majhūl"
    >>> transliterate("مَعْرُوف وَ مَجْهُول")
    "ma'rūf wa majhūl"
    >>> transliterate("وَٱللّٰه")
    'wal-lāh'
    >>> transliterate("کَسے")
    'kasē'
    >>> transliterate("کَٹَه")
    'kaṭa'
    >>> transliterate("آیَةُ‌اللّٰه")
    'āyatu-l-lāh'
    >>> transliterate("فِالْحَال")
    'fi-l-hāl'
    >>> transliterate("بویِ تُو")
    'bō-yi tū'
    >>> transliterate("بِسْمِ اللّٰهِ الْرَّحْمٰنِ الْرَّحِیم")
    'bismi l-lāhi r-rahmāni r-rahīm'
    >>> transliterate("اِیَالَاتِ مُتَّحِدَه")
    'iyālāt-i muttahida'
    >>> transliterate("دَارُ الخَلَافَه")
    'dāru l-xalāfa'
    >>> transliterate("اَبُو الهَوْد")
    'abū l-hawd'
    >>> transliterate("گُرُسْنَه چِه کَارِی کُنَد چِهِل نَر، کِه دَهْ لَک بَرْآیَد بَر او بی‌خَبَر، کِه پَیْمَان‌شِکَسْت بی‌دَرَنْگ آمَدَنْد، مِیَانِ تیغ و تِیر و تُفَنْگ آمَدَنْد")
    "gurusna či kārī kunad čihil nar, ki dah lak bar'āyad bar ō bē-xabar, ki paymān-šikast bē-darang āmadand, miyān-i tēġ u tīr u tufang āmadand"
    """
    return tr(text)


dental = U(0x32A)
pitchaccent = U(0x301)
devoice = U(0x325)
dtack = U(0x31E)
vowels_minus_a = "iuāīūüēōːʷ"
vowels = "aiuāīūüēōːʷ"
vowel = rf"[{vowels}]"
consonant = rf"[^{vowels}. -]"


def romanize_ira(text: str) -> str:
    """Romanize text using IRA (International Romanization of Arabic) system."""
    # Source: https://en.wiktionary.org/w/index.php?title=Module:fa-IPA&oldid=85693636

    # Initial preprocessing
    text = re.sub(r"^[-]", "\x01", text)  # Use \x01 as placeholder for \1
    text = re.sub(r"`", "", text)
    text = re.sub(r"ˈ", "", text)
    text = re.sub(r"%%", "#", text)
    text = re.sub(r"[,]", ", ", text)
    text = re.sub(r" \| ", "# | #", text)
    text = "##" + re.sub(r" ", "# #", text) + "##"
    text = re.sub(r"([iī]y(\.?))y", r"i\2y", text)

    # Kill incorrect characters
    text = re.sub(f"[{dental}{pitchaccent}{devoice}{dtack}ʰ]", "", text)
    text = re.sub(r"[ɴŋ]", "n", text)
    text = re.sub(r"v", "w", text)

    # Replace xw clusters
    text = re.sub(r"([#-])xw([āē])", r"\1x\2", text)
    text = re.sub(r"([#-])xwa", r"\1xu", text)
    text = re.sub(r"ʷ", "", text)
    text = re.sub(f"w({vowel})", r"v\1", text)
    text = re.sub(f"w({consonant})", r"w\1", text)
    text = re.sub(f"([{vowels_minus_a}])w", r"\1v", text)
    text = re.sub(r"v\(w", "v(v", text)
    text = re.sub(f"({consonant})w#", r"\1v#", text)
    text = re.sub(r"wv", "vv", text)
    text = re.sub(r"wæ", "væ", text)

    # Ensure vowels are paired to a consonant
    text = re.sub(f"([.])([{vowels}])", r"\1'\2", text)
    text = re.sub(r"([.])", "", text)
    text = re.sub(r"iy", "īy", text)

    # Replace diphthong
    def replace_diphthong(match: re.Match[str]) -> str:
        """Replace diphthong based on following character."""
        semivowel = match.group(1)
        position = match.end()

        if position < len(text):
            consonant = text[position]
            if consonant == "" or consonant in consonant:
                return "uw" if semivowel == "w" else "ey"

        return match.group(0)  # No replacement

    if re.search(f"a([wy])([^{vowels}])", text):
        text = re.sub(r"a([wy])", replace_diphthong, text)

    # Character replacements
    replacements = [
        ("ḍ", "z"),
        ("ḏ", "z"),
        ("ṭ", "t"),
        ("q", "ġ"),
        ("ṯ", "s"),
        ("ṣ", "s"),
        ("ḥ", "h"),
        ("ā", "â"),
        ("u", "o"),
        ("i", "e"),
        # Remove Hazaragi retroflexes
        ("D", "d"),
        ("T", "t"),
        ("ɖ", "d"),
        ("ʈ", "t"),
    ]

    for old, new in replacements:
        text = re.sub(old, new, text)

    # Majhul-Ma'ruf merger
    text = re.sub(r"[ēī]", "i", text)
    text = re.sub(r"[ūō]", "u", text)

    # Final adjustments
    text = re.sub(r"([o]0)w#", "v#", text)  # Note: This seems like it might be a typo in original
    text = re.sub(r"a#", "e#", text)
    text = re.sub(r"#ve#", "#va#", text)
    text = re.sub(r"a-", "e-", text)
    text = re.sub(r"æ", "a", text)
    text = re.sub(r"#'", "#", text)
    text = re.sub(r"#", "", text)
    text = re.sub(r"\x01", "&#45;", text)  # Restore the placeholder

    return text
