"""
Transliterator used across multiple templates.
"""

from .ar import transliterate as transliterate_ar
from .fa import transliterate as transliterate_fa
from .gu import transliterate as transliterate_gu
from .mr import transliterate as transliterate_mr
from .ru import transliterate as transliterate_ru

transliterations = {
    "ar": transliterate_ar,
    "fa": transliterate_fa,
    "gu": transliterate_gu,
    "mr": transliterate_mr,
    "ru": transliterate_ru,
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
transliterations["vah"] = transliterations["mr"]
transliterations["vgr"] = transliterations["gu"]


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

    >>> transliterate("ar", "عُظْمَى")
    'ʕuẓmā'
    >>> transliterate("fa", "سَرْاَنْجَام")
    'sar-anjām'
    >>> transliterate("gu", "અમ્રાઈવાડી")
    'amrāīvāḍī'
    >>> transliterate("mr", "च़ांदअणी च़ौक")
    'ċāndaṇī ċauk'
    >>> transliterate("ru", "без")
    'bez'
    """
    return func(text, locale=locale) if (func := transliterations.get(locale)) else ""
