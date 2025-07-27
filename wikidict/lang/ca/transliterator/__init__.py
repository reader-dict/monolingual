"""
Transliterator used across multiple templates.
"""

from .be import transliterate as transliterate_be
from .ber import transliterate as transliterate_ber
from .el import transliterate as transliterate_el
from .grc import transliterate as transliterate_grc
from .ky import transliterate as transliterate_ky
from .ru import transliterate as transliterate_ru
from .uk import transliterate as transliterate_uk
from .xib import transliterate as transliterate_xib
from .zh import transliterate as transliterate_zh

transliterations = {
    "be": transliterate_be,
    "ber": transliterate_ber,
    "el": transliterate_el,
    "grc": transliterate_grc,
    "ky": transliterate_ky,
    "ru": transliterate_ru,
    "uk": transliterate_uk,
    "xib": transliterate_xib,
    "zh": transliterate_zh,
}
transliterations["taq"] = transliterations["ber"]
transliterations["thv"] = transliterations["ber"]
transliterations["thz"] = transliterations["ber"]
transliterations["tmh"] = transliterations["ber"]
transliterations["ttq"] = transliterations["ber"]
transliterations["zgh"] = transliterations["ber"]


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

        >>> transliterate("be", "Белару́сь")
        'Belarús'
        >>> transliterate("ber", "ⴰⴷⵔⴰⵔ")
        'adrar'
        >>> transliterate("el", "Υ")
        'I'
        >>> transliterate("grc", "λόγος")
        'lógos'
        >>> transliterate("ky", "кырк")
        'kurk'
        >>> transliterate("ru", "абха́з")
        'abkhaz'
        >>> transliterate("uk", "Украї́на")
        'Ukraïna'
        >>> transliterate("xib", "ba")  # doctest: +ELLIPSIS
        '<svg ...'
        >>> transliterate("xib", "*Icosia")
        ''
        >>> transliterate("zh", "汉字")
        'hànzì'
    """
    if locale == "xib" and text.startswith("*"):
        return ""
    return func(text, locale=locale) if (func := transliterations.get(locale)) else ""
