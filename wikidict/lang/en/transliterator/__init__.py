"""
Transliterator used across multiple templates.
"""

from .ar import transliterate as transliterate_ar
from .fa import transliterate as transliterate_fa
from .gu import transliterate as transliterate_gu
from .ru import transliterate as transliterate_ru

transliterations = {
    "ar": transliterate_ar,
    "fa": transliterate_fa,
    "gu": transliterate_gu,
    "ru": transliterate_ru,
}
transliterations["ady"] = transliterations["ar"]
transliterations["av"] = transliterations["ar"]
transliterations["ce"] = transliterations["ar"]
transliterations["inh"] = transliterations["ar"]
transliterations["kbd"] = transliterations["ar"]
transliterations["crp-rsn"] = transliterations["ru"]
transliterations["crp-slb"] = transliterations["ru"]
transliterations["crp-tpr"] = transliterations["ru"]


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

    >>> transliterate("ar", "عُظْمَى")
    'ʕuẓmā'
    >>> transliterate("fa", "سَرْاَنْجَام")
    'sar-anjām'
    >>> transliterate("gu", "અમ્રાઈવાડી")
    'amrāīvāḍī'
    >>> transliterate("ru", "без")
    'bez'
    """
    return func(text, locale=locale) if (func := transliterations.get(locale)) else ""
