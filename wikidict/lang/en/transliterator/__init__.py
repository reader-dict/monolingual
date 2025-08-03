"""
Transliterator used across multiple templates.
"""

from .ar import transliterate as transliterate_ar
from .bn import transliterate as transliterate_bn
from .fa import transliterate as transliterate_fa
from .gu import transliterate as transliterate_gu
from .hi import transliterate as transliterate_hi
from .mr import transliterate as transliterate_mr
from .mtei import transliterate as transliterate_mtei
from .ru import transliterate as transliterate_ru
from .zh import transliterate as transliterate_zh

transliterations = {
    "ar": transliterate_ar,
    "bn": transliterate_bn,
    "fa": transliterate_fa,
    "gu": transliterate_gu,
    "hi": transliterate_hi,
    "mr": transliterate_mr,
    "Mtei": transliterate_mtei,
    "ru": transliterate_ru,
    "zh": transliterate_zh,
}
transliterations["ady"] = transliterations["ar"]
transliterations["ahr"] = transliterations["mr"]
transliterations["av"] = transliterations["ar"]
transliterations["ce"] = transliterations["ar"]
transliterations["crp-rsn"] = transliterations["ru"]
transliterations["crp-slb"] = transliterations["ru"]
transliterations["crp-tpr"] = transliterations["ru"]
transliterations["inh"] = transliterations["ar"]
transliterations["kbd"] = transliterations["ar"]
transliterations["kfr"] = transliterations["gu"]
transliterations["kok"] = transliterations["mr"]
transliterations["mni"] = transliterations["Mtei"]
transliterations["omp"] = transliterations["Mtei"]
transliterations["vah"] = transliterations["mr"]
transliterations["vgr"] = transliterations["gu"]
for sublang in {
    "anp",
    "awa",
    "bfy",
    "bfz",
    "bgc",
    "bhd",
    "bns",
    "bpx",
    "bra",
    "cdh",
    "cdj",
    "dhd",
    "doi",
    "gbk",
    "gbm",
    "hne",
    "hoj",
    "jns",
    "kfs",
    "kfx",
    "kru",
    "mjl",
    "mtr",
    "mup",
    "mwr",
    "noe",
    "pgg",
    "sck",
    "skr",
    "unr",
    "vjk",
    "wtm",
    "xnr",
}:
    transliterations[sublang] = transliterations["hi"]
for sublang in {
    "cdo",
    "cmn",
    "csp",
    "gan",
    "hsn",
    "ltc",
    "lzh",
    "mnp",
    "nan-tws",
    "och",
    "wuu",
    "yue",
    "zhx-sic",
    "zhx-tai",
}:
    transliterations[sublang] = transliterations["zh"]


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

    >>> transliterate("ar", "عُظْمَى")
    'ʕuẓmā'
    >>> transliterate("cmn", "^褚")
    'Chǔ'
    >>> transliterate("bn", "চাঁদ্নি চক")
    'cãdni cok'
    >>> transliterate("fa", "سَرْاَنْجَام")
    'sar-anjām'
    >>> transliterate("gu", "અમ્રાઈવાડી")
    'amrāīvāḍī'
    >>> transliterate("hi", "संस्कार")
    'sanskār'
    >>> transliterate("mni", "ꯑꯔꯥꯝꯕꯥꯢ")
    'ʼarāmbāi'
    >>> transliterate("mr", "च़ांदअणी च़ौक")
    'ċāndaṇī ċauk'
    >>> transliterate("mwr", "शेखाव*टी")
    'śekhāvaṭī'
    >>> transliterate("ru", "без")
    'bez'
    >>> transliterate("閩中語", "zh")
    'mǐnzhōngyǔ'
    """
    return func(text, locale=locale) if (func := transliterations.get(locale)) else ""
