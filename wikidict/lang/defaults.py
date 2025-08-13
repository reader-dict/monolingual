"""Defaults values for locales without specific needs."""

import logging
from collections import defaultdict

from ..user_functions import subscript, superscript

log = logging.getLogger(__name__)

# Float number separator
float_separator = ""

# Thousands separator
thousands_separator = ""

# Markers for sections that contain interesting text to analyse.
section_patterns = ("#",)
sublist_patterns = ("#",)
section_level = 2
section_sublevels = (3,)
head_sections = ("",)
etyl_section = ("",)

# Variants
variant_titles: tuple[str, ...] = ()
variant_templates: tuple[str, ...] = ()

# Some definitions are not good to keep
definitions_to_ignore: tuple[str, ...] = ()

# Templates to ignore: the text will be deleted.
templates_ignored: tuple[str, ...] = ()

# Templates that will be completed/replaced using italic style.
templates_italic: dict[str, str] = {}

# More complex templates that will be completed/replaced using custom style.
templates_multi: dict[str, str] = {}

# Templates that will be completed/replaced using custom style.
templates_other: dict[str, str] = {}


def find_genders(code: str, locale: str) -> list[str]:
    """Function used to find genders within `code`."""
    return []


def find_pronunciations(code: str, locale: str) -> list[str]:
    """Function used to find pronunciations within `code`."""
    return []


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be call in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["formatnum", "42000"], "es")
        '42 000'
        >>> last_template_handler(["formatnum", "42000"], "it")
        '42 000'
        >>> last_template_handler(["formatnum", "42000"], "no")
        '42 000'

        >>> last_template_handler(["sub", "42"], "no")
        '<sub>42</sub>'
        >>> last_template_handler(["sup", "42"], "no")
        '<sup>42</sup>'
    """
    from ..user_functions import capitalize, extract_keywords_from, lookup_italic, number, term

    tpl, *parts = template
    data = extract_keywords_from(parts)

    if tpl == "BASEPAGENAME":
        return word

    if tpl == "formatnum":
        from . import float_separator as locale_aware_fs
        from . import thousands_separator as locale_aware_ts

        return number(parts[0], locale_aware_fs[locale], locale_aware_ts[locale])

    if tpl in {"sub", "Sub"}:
        return subscript(parts[0])

    if tpl in {"sup", "Sup"}:
        return superscript(parts[0])

    if tpl == "t2i-Egyd":
        return render_demotic(tpl, parts, data, word=word)

    if tpl in {"w", "W"}:
        return render_wikilink(tpl, parts, data, word=word)

    if tpl == "Wikidata entity link":
        return render_wikidata_entity_link(tpl, parts, data, word=word)

    if tpl == "!":
        return "|"

    if italic := lookup_italic(tpl, locale, empty_default=True):
        return term(capitalize(italic))

    if all_templates is not None:
        all_templates.append((tpl, word, "missed"))

    from ..utils import CLOSE_DOUBLE_CURLY, OPEN_DOUBLE_CURLY

    return f"{OPEN_DOUBLE_CURLY}{tpl}{CLOSE_DOUBLE_CURLY}"


def render_demotic(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_demotic("t2i-Egyd", ["t", "b-2", "O39"], defaultdict(str))
    '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAABtCAQAAAB5Yus5AAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAAD2EAAA9hAag/p2kAAAAHdElNRQfpBA8RLCKhybVxAAABkElEQVRo3u3VPWtTURgH8F/SxDShlRasLSmtQlFxUKy6Ozg5Ko79AI4Krn4BwaWriwgOuvgBlLq4CA6ioEMHiyCS1ta+aEuTJsdFTW1jG/AiDs/vWS7nHv6ct3suIYQQQgghhBBCJnJy3Xbt2bdH2QWX1KxkM7aqaYvmnM0mbsxjLckDfVnEHfZIkrwzmUXckHtakgVXsogb91BTsupaFxu3rzNmJMmamw78/Zm76I0kWXZ9W1xOyYCqE047Z9JxI8q7z+fOhrzL7jiCebfcVzRgyKhxR40ZNqhPScGWb+bNeumZWc0/BeZNuW0YySsv9Bkx4pCDeuU7zuer56Y91eg83atq0o9q/Xrau+qeON857pS3XYb8XktutE9CYdtXPeXkntuVbGnYVNfQkuRUVBQ19ev5uY7twF7HdgVsWrNsQU3NgiWrFq3YsCWhrGrChJLX7TVsB264671Rg0rqvvjkgzkffbZsXV1L6jDqgop+6+13uR2XWUlRXlNdXeu/uIrz8TsKIYQQQgghhPDPfQf0Cpf62Ubr/AAAAA50RVh0YXV0aG9yAFMgP2lyaT+bUBUgAAAAJXRFWHRkYXRlOmNyZWF0ZQAyMDI1LTA0LTE1VDE3OjQ0OjMzKzAwOjAwtaujLQAAACV0RVh0ZGF0ZTptb2RpZnkAMjAyNS0wNC0xNVQxNzo0NDozMyswMDowMMT2G5EAAADSelRYdGljYzpjb3B5cmlnaHQAABiVbY6xbgIxEER/ZUuQwIZEaS5NkJUiUjqSD/D5JncrfN6Tdwni72MEZcqR5r2ZIMu18jgZPe32Lxt6zxl0NCmg1QW9sqGjyWzpvC9cMGCsgPbIcnFJZv9KmCPnjtBIvYFv//XWjr4mVvoIgZYqP9xmWsycUBQDncuASpFCRTT+BQWZZylKB7PK/dlYyvY4xYpD5hPo2e3ouyxSrcGfdwutbke1PU0PS7pLnNTRP6bU99etRt8EPmOMOcmAtfsDlcpeKRZ8VSUAAAAodEVYdGljYzpkZXNjcmlwdGlvbgBzUkdCLWVsbGUtVjItc3JnYnRyYy5pY2PLOZHmAAAAAElFTkSuQmCC" alt="t" width="14" height="38"/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAABQCAQAAADBhv9KAAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAAD2EAAA9hAag/p2kAAAAHdElNRQfpBAkPDiDbpkPbAAACZ0lEQVRYw+3WzW9MURjH8Y/p9J3SpAi68BIWQppUumoXrC0RIkRsJP4BQSMSsUAidiKIhJ1YsGBrQSJiQSKashBEpW281stM22nnWszpaY2I6V3f39nc58nN9zznPL97ziVTpkyZMmXKlKlW1cWnnPW6jJiKmTV6jZpIC97jpUEbY2aLRwZtSFvpdiMSBTtCvNgdiRE98wXlQKtDlqPZ2pBfpRsLLU8HzGmM+1bJNKpDvcXpgAXvQtypCRRNoC4tcNr7EC/TAkqmUKctHZChYJe2CJwES9ICPyiCFs1gMvivfY5T5wX85FcAtgVgMdgnnw74QwE0BWApxK1pgeMBkNcKpvwEDfGNeQILxsIn2Bz6Pj7HjymAE34EYMWHZaUATLnk6bDkmfMnCV3Op13ydOjqjJLgw0S7Hh3pKyxHcBmscMVd562uFZiPFRWCXb6GOAnfdif2qnfc2/lUmISuFgOwetpdztZ22M5ueaWr332JU/yJ3OmSbeprB1b2bNTnEE+F7Hh8c5tr+q3/Z98bdcrlqtADvof6yuHQuDxnE1brd0u/bq0WVOGWOOqgObZtwKT78dar+PGhU4Yd0R6X3mWTQ5544IUh35Q06NBlnx4HQhnIuy7xyrpY71WJp7rQ4rDXkqoxbcwbzzz23LCSktMaZgtuc1/iYqy43hk3bI7T9blp7C/o7Pjl3J+n+yoDPuqN8QKL4sU1s0e73Taq/BesbMDBcKhEdRt24b+mWKTPCfcM+mzcpKJRDx2zbrZFMw9b7XfSUE3ObdFhpWWa/DTkrbEqz4a7Y2n2o5cpU6ZMmTJl+o9+A+YBwGTWZcj0AAAADnRFWHRhdXRob3IAUyA/aXJpP5tQFSAAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjUtMDQtMDlUMTU6MTQ6MzIrMDA6MDAiU6kbAAAAJXRFWHRkYXRlOm1vZGlmeQAyMDI1LTA0LTA5VDE1OjE0OjMyKzAwOjAwUw4RpwAAANJ6VFh0aWNjOmNvcHlyaWdodAAAGJVtjrFuAjEQRH9lS5DAhkRpLk2QlSJSOpIP8Pkmdyt83pN3CeLvYwRlypHmvZkgy7XyOBk97fYvG3rPGXQ0KaDVBb2yoaPJbOm8L1wwYKyA9shycUlm/0qYI+eO0Ei9gW//9daOviZW+giBlio/3GZazJxQFAOdy4BKkUJFNP4FBZlnKUoHs8r92VjK9jjFikPmE+jZ7ei7LFKtwZ93C61uR7U9TQ9Lukuc1NE/ptT3161G3wQ+Y4w5yYC1+wOVyl4pFnxVJQAAACh0RVh0aWNjOmRlc2NyaXB0aW9uAHNSR0ItZWxsZS1WMi1zcmdidHJjLmljY8s5keYAAAAASUVORK5CYII=" alt="b-2" width="14" height="38"/><img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAABrCAQAAACvOwgkAAAAAmJLR0QAAKqNIzIAAAAJcEhZcwAAD2EAAA9hAag/p2kAAAAHdElNRQfpAxEPLQ/pU6qDAAACoElEQVRo3u2WPU8UQRiAn729O/ZAuQMJX8EDo8ZQSILEQm39SEzsNbEhdhbGWNhY0NlYWplgyx8wmqiJVNoYK00olIBwkCPC3fJ1HMfujA0ss3AzB4WNmWebnf149p1533eyYLFYLBaLxWKxWCz/OU7daxkEVcChiRxZWmmlGY8kCQLW+cMcJQLkUYRJbnCfSSY5w2WGGaCdFjySuCQAQY1VpvnGO76y0ShilwcUkRSYwkcgtUfILM/JNxLeYsEgOXhUeMkpky7Hm2PoJJISoyTiK6YyyAgAknkKbCJxEAQEQJocnXTRElv3Nu7xnkWdsI8sAFVeMEEIOAgkAnBpppMhbnMzNs0RhlVhnCeESCQ7PNYuSzuPKCiTFoypMSdiJdSxO06SPxD7PiXGec2W8tZ5mnTCfUmejDbGChP8UMY9NNcXQhidDdBuqIZpPiCU2sjUF0rloR66DcKAz/jR6IROCLWoO7P0GxvgN+XoPK1bQ0k5mnSGc3U3jj3KrCjtmtRFuMxOdH0QzyCsKBHGPhwX+tSUtJw0CHeoxOamEZaU+uo2tr1QPi30Qp81pSP6DEJJoAiFTlhmWSmGs8Y8y6MIK0ru0lzQtp+BuHCbJWV0kQ5DfKJeSg4X9oIyusQdtWS1a+iS0u2HMM92JGnjGf28ZZ7N3b3RJYmDJCCkqgTl6oWzbChR9fOUUYqsUQMSeKRxEGzhk0dGJe3ohXMUY/WXopfeBnnYYFO3hrDAl2Mn1leF7qGW8hmhq4GiyjJTzJDFo8IrPu7n/PCOkuI6D7lG7sA9wTbrLDHDd37yi1k87nKVT4yzav63SdDFFYY4TRspBFXWWWGRAnMUKbEVxeORpRTtUFrh3p0UKRwkIQFhvR8ji8VisVgsFovF8u/5C4/7+VLfVKnPAAAADnRFWHRhdXRob3IAUyA/aXJpP5tQFSAAAAAldEVYdGRhdGU6Y3JlYXRlADIwMjUtMDMtMTdUMTU6NDU6MTUrMDA6MDDWXuE3AAAAJXRFWHRkYXRlOm1vZGlmeQAyMDI1LTAzLTE3VDE1OjQ1OjE1KzAwOjAwpwNZiwAAANJ6VFh0aWNjOmNvcHlyaWdodAAAGJVtjrFuAjEQRH9lS5DAhkRpLk2QlSJSOpIP8Pkmdyt83pN3CeLvYwRlypHmvZkgy7XyOBk97fYvG3rPGXQ0KaDVBb2yoaPJbOm8L1wwYKyA9shycUlm/0qYI+eO0Ei9gW//9daOviZW+giBlio/3GZazJxQFAOdy4BKkUJFNP4FBZlnKUoHs8r92VjK9jjFikPmE+jZ7ei7LFKtwZ93C61uR7U9TQ9Lukuc1NE/ptT3161G3wQ+Y4w5yYC1+wOVyl4pFnxVJQAAACh0RVh0aWNjOmRlc2NyaXB0aW9uAHNSR0ItZWxsZS1WMi1zcmdidHJjLmljY8s5keYAAAAASUVORK5CYII=" alt="O39" width="19" height="38"/>'
    """
    from ..demotic import glyph_to_image

    return "".join(glyph_to_image(part) for part in parts)


def render_wikidata_entity_link(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_wikidata_entity_link("Wikidata entity link", ["112383134"], defaultdict(str))
    'Steve Bruce'
    """
    from .en import wikidata

    return wikidata.person(f"Q{parts[0]}", name_only=True)


def render_wikilink(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_wikilink("w", [], defaultdict(str))
    ''
    >>> render_wikilink("w", ["Li Ptit Prince (roman)", "Li Ptit Prince"], defaultdict(str, {"lang": "wa"}))
    'Li Ptit Prince'
    >>> render_wikilink("w", ["Gesse aphaca", "Lathyrus aphaca"], defaultdict(str))
    'Lathyrus aphaca'
    >>> render_wikilink("w", [], defaultdict(str, {"Paulin <span style": "'font-variant:small-caps'>Paris</span>", "lang": "fr"}))
    "Paulin <span style='font-variant:small-caps'>Paris</span>"
    >>> render_wikilink("w", ["Еремеев, Павел Владимирович"], defaultdict(str, {"lang": "ru", "Pavel Vladimirovitch <span style": "'font-variant:small-caps'>Ieremeïev</span>"}))
    "Pavel Vladimirovitch <span style='font-variant:small-caps'>Ieremeïev</span>"
    >>> render_wikilink("w", ["mitrospin obscur 0", "mitrospin obscur 1", "(''Mitrospingus cassinii'')"], defaultdict(str))
    'mitrospin obscur 1'
    >>> render_wikilink("W", ["Nomenclature de l'UICPA"], defaultdict(str, {"dif": "Nom UICPA"}))
    "Nomenclature de l'UICPA"
    """
    # Possible imbricated templates: {{w| {{pc|foo bar}} }}
    if wiki_data := {k: v for k, v in data.items() if k not in ("lang", "dif")}:
        return "".join(f"{k}={v}" for k, v in wiki_data.items())

    try:
        return parts[1]
    except IndexError:
        return parts[0] if parts else ""


def adjust_wikicode(code: str, locale: str) -> str:
    return code
