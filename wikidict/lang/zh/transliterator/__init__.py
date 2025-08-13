"""
Transliterator used across multiple templates.
"""

transliterations = {}  # type: ignore


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

    >> transliterate("zh", "一丁點")
    'yīdīngdiǎn'
    """
    return func(text, locale=locale) if (func := transliterations.get(locale)) else ""
