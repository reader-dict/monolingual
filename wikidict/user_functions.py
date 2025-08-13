"""
Functions that can be used in *templates_multi* of any locale.
"""

import re
from collections import defaultdict
from html import escape


def capitalize(text: str) -> str:
    """
    Capitalize the first letter only.

        >>> capitalize("")
        ''
        >>> capitalize("alice")
        'Alice'
        >>> capitalize("BOB")
        'BOB'
        >>> capitalize("alice and bob")
        'Alice and bob'
    """
    return f"{text[0].capitalize()}{text[1:]}" if text else ""


def century(parts: list[str], century: str) -> str:
    """
    Format centuries.

        >>> century(["XVI"], "siècle")
        'XVI<sup>e</sup> siècle'
        >>> century(["XVIII", "XIX"], "century")
        'XVIII<sup>e</sup> century - XIX<sup>e</sup> century'
    """
    return " - ".join(f"{p}{superscript('e')} {century}" for p in parts)


def chimy(composition: list[str]) -> str:
    """
    Format chimy notations.

        >>> chimy(["H", "2", "O"])
        'H<sub>2</sub>O'
        >>> chimy(["FeCO", "3", ""])
        'FeCO<sub>3</sub>'
        >>> chimy(["CH", "2", "3==CHCOOH"])
        'CH<sub>2</sub>=CHCOOH'
        >>> chimy(["CH", "2", "&#61;CH", "2"])
        'CH<sub>2</sub>&#61;CH<sub>2</sub>'
        >>> chimy(["CH", "2", "&nbsp;=&nbsp;", "CH", "2"])
        'CH<sub>2</sub>CH<sub>2</sub>'
    """
    data: defaultdict[str, str] = defaultdict(str)
    i = 1
    for c in composition:
        sArray = c.split("=", 1)
        if len(sArray) == 2:
            if sArray[0].isdigit():
                data[sArray[0]] = sArray[1]
                continue
            elif sArray[0] == "&nbsp;":
                continue
        data[str(i)] = c
        i += 1

    phrase = ""
    for i in range(1, 21):
        stri = str(i)
        if data[stri]:
            phrase += data[stri] if i % 2 == 1 else subscript(data[stri])

    return phrase


def chinese(parts: list[str], data: defaultdict[str, str], *, laquo: str = "“", raquo: str = "”") -> str:
    """
    Format Chinese word or sentence.

        >>> chinese(["餃臺灣／台灣／台湾"], defaultdict(str))
        '餃臺灣／台灣／台湾'
        >>> chinese(["痟", "mad"], defaultdict(str, {"tr": "siáu"}))
        '痟 (<i>siáu</i>, “mad”)'
        >>> chinese(["秦"], defaultdict(str, {"gloss": "Qin"}))
        '秦 (“Qin”)'
        >>> chinese(["餃子／饺子", "jiǎozi"], defaultdict(str))
        '餃子／饺子 (<i>jiǎozi</i>)'
        >>> chinese(["餃子／饺子", "jiǎozi", "jiaozi bouillis"], defaultdict(str), laquo="«&nbsp;", raquo="&nbsp;»")
        '餃子／饺子 (<i>jiǎozi</i>, «&nbsp;jiaozi bouillis&nbsp;»)'
        >>> chinese(["*班長", ""], defaultdict(str, {"tr": "bānzhǎng", "gloss": "team leader"}))
        '*班長 (<i>bānzhǎng</i>, “team leader”)'
        >>> chinese(["木蘭"], defaultdict(str, {"tr": "Mùlán", "lit": "magnolia"}))
        '木蘭 (<i>Mùlán</i>, literally “magnolia”)'
    """
    phrase = parts.pop(0).replace("/", "／")
    tr = data["tr"] or (parts.pop(0) if parts else "")
    gl = data["gloss"] or (parts.pop(0) if parts else "")
    if not tr and not gl and not data["lit"]:
        return phrase

    phrase += " ("
    if tr:
        phrase += italic(tr)
    if gl:
        if tr:
            phrase += ", "
        phrase += f"{laquo}{gl}{raquo}"
    if data["lit"]:
        if tr:
            phrase += ", literally "
        phrase += f"{laquo}{data['lit']}{raquo}"
    phrase += ")"
    return phrase


def code(kind: str, value: str) -> str:
    """
    >>> code("html", "")
    ''
    >>> code("html", "</span>")
    '<code>&lt;/span&gt;</code>'

    >>> code("js", "(65535).toString(16) === 'ffff'")
    "<code>(65535).toString(16) === 'ffff'</code>"
    >>> code("js", "=(65535).toString(16) === 'ffff'")
    "<code>(65535).toString(16) === 'ffff'</code>"
    >>> code("js", "==(65535).toString(16) === 'ffff'")
    "<code>=(65535).toString(16) === 'ffff'</code>"
    """
    if not value:
        return ""
    if value[0] == "=":
        value = value[1:]
    if kind == "html":
        value = escape(value)
    return f"<code>{value}</code>"


def color(rgb: str) -> str:
    """
    Format a RGB hexadecimal color.

        >>> color("#B0F2B6")
        '[RGB #B0F2B6]'
        >>> color("#ffffff")
        '[RGB #FFFFFF]'
    """
    return f"[RGB {rgb.upper()}]"


def concat(
    parts: list[str],
    sep: str,
    *,
    last_sep: str | None = None,
    indexes: list[int] | None = None,
    skip: str | None = None,
) -> str:
    """
    Simply concat all *parts* using the *sep* character as glue.

    If *indexes* is set, it must be a list of integers where each of one is the part number to keep.
    If *skip* is set, it must be a string. If a part is equal to *skip* then is it skipped and the
    *sep* become a single space.
    It allowes to filter out some parts while keeping others.

        >>> concat(["92", "%"], "")
        '92%'
        >>> concat(["O", "M", "G"], "!")
        'O!M!G'
        >>> concat(["sport"], " ", indexes=[0, 2])
        'sport'
        >>> concat(["sport", "fr", "collectif"], " ", indexes=[0, 2])
        'sport collectif'
        >>> concat(["marca", "ca", "antigament", "_", "en plural"], " ", indexes=[2, 3, 4, 5], skip="_")
        'antigament en plural'
        >>> concat(["antigament", "_", "en plural"], ",", skip="_")
        'antigament en plural'
        >>> concat(["Arte", "", ""], " e ")
        'Arte'
        >>> concat(["Mathématique", "Physique", "Chimie"], ", ", last_sep=" et ")
        'Mathématique, Physique et Chimie'
        >>> concat(["Physique", "Chimie"], ", ", last_sep=" et ")
        'Physique et Chimie'
        >>> concat(["Physique"], ", ", last_sep=" et ")
        'Physique'
    """
    if indexes:
        result = [part for index, part in enumerate(parts) if index in indexes]
    else:
        result = list(parts)

    if skip:
        result = [part for part in result if part != skip]
        if parts.count(skip):
            sep = " "
    r = [p for p in result if p]
    if last_sep is None or last_sep == sep or len(r) == 1:
        return sep.join(r)
    return sep.join(r[:-1]) + last_sep + r[-1] if r else ""


def coord(raw_values: list[str], *, locale: str = "en") -> str:
    """
    Format lon/lat coordinates.

        >>> coord(["19.707", "-101.204"])
        '19.707, -101.204'
        >>> coord(["04", "39", "N", "74", "03", "O", "type:country", "display=inline,title"])
        '04°39′N 74°03′O'
        >>> coord(["04", "39", "15", "N", "74", "03", "17", "W"], locale="es")
        '04°39′15″N 74°03′17″O'
    """
    values = [value for value in raw_values if ":" not in value and "=" not in value]

    match len(values):
        case 2:
            fmt = "{}, {}"
        case 6:
            fmt = "{}°{}′{} {}°{}′{}"
        case 8:
            fmt = "{}°{}′{}″{} {}°{}′{}″{}"

    if locale == "es" and values[-1] == "W":
        values[-1] = "O"
    return fmt.format(*values)


def eval_expr(expr: str) -> str:
    """
    Compute and return the result of *expr*.

        >>> eval_expr("2 ^ 30")
        '1073741824'

    *expr* is sanitized and only a small range of characters are allowed:

        >>> eval_expr("cat /etc/passwd")  # doctest: +ELLIPSIS
        Traceback (most recent call last):
          File ".../doctest.py", line 1329, in __run
            compileflags, 1), test.globs)
          File "<doctest wikidict.user_functions.eval_expr[0]>", line 1, in <module>
          File ".../user_functions.py", line 33, in eval_expr
            raise ValueError(f"Dangerous characters in the expr {expr!r}")
        ValueError: Dangerous characters in the expr 'cat /etc/passwd'

    Allowed characters are digits (0-9), spaces and operators (+-*^).
    """
    # Prevent horrors
    # digits, space and operators (+-*^)
    if re.search(r"[^\d\s\*\-\+\^\.]+", expr):
        raise ValueError(f"Dangerous characters in the expr {expr!r}")

    # Replace signs
    expr = expr.replace("^", "**")

    return f"{eval(expr)}"


def extract_keywords_from(parts: list[str]) -> defaultdict[str, str]:
    """
    Given a list of strings, extract strings containing an equal sign ("=").

    Return a *defaultdict(str)* with key=value extracted from the original list.

    The left part of the sign is used as the dict key and the right part as the value.
    When a string contains the sign, it is removed from the original list.

        >>> extract_keywords_from([])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo"])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "bar=baz"])
        defaultdict(<class 'str'>, {'bar': 'baz'})
        >>> extract_keywords_from(["foo", "bar=baz=ouf"])
        defaultdict(<class 'str'>, {'bar': 'baz=ouf'})
        >>> extract_keywords_from(["foo", "bar = baz=ouf"])
        defaultdict(<class 'str'>, {'bar': 'baz=ouf'})
        >>> extract_keywords_from(["foo", "<span style='font-variant:small-caps'>xix</span><sup>e</sup> s."])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "À partir du <span style='font-variant:small-caps'>xix</span><sup>e</sup> siècle"])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "bar='baz'"])
        defaultdict(<class 'str'>, {'bar': "'baz'"})
    """
    data = defaultdict(str)
    for part in parts.copy():
        if "=" in part:
            key, value = part.split("=", 1)

            # Prevent splitting such parts:
            #   "<span style='font-variant:small-caps'>xix</span><sup>e</sup> s.".
            #   "À partir du <span style='font-variant:small-caps'>xix</span><sup>e</sup> siècle".
            if key.endswith("<span style"):
                continue

            data[key.strip()] = value.strip()
            parts.pop(parts.index(part))
    return data


def int_to_roman(number: int) -> str:
    """
    Convert an integer to a Roman numeral.

        >>> int_to_roman(12)
        'XII'
        >>> int_to_roman(2020)
        'MMXX'

    Source: https://www.oreilly.com/library/view/python-cookbook/0596001673/ch03s24.html
    """
    # if not 0 < number < 4000:
    #     raise ValueError("Argument must be between 1 and 3999")
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ("M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I")
    result = []
    for i in range(len(ints)):
        count = int(number / ints[i])
        result.append(nums[i] * count)
        number -= ints[i] * count
    return "".join(result)


def flatten(seq: list[str]) -> list[str]:
    """
    Flatten non-empty items from *seq*.

        >>> flatten(["a", ("b", "", "c"), ["d"]])
        ['a', 'b', 'c', 'd']
    """
    res: list[str] = []
    for item in seq:
        if isinstance(item, list | tuple):
            res.extend(sitem for sitem in item if sitem)
        elif item:
            res.append(item)
    return res


def italic(text: str) -> str:
    """
    Return the *text* surrounded by italic HTML tags.

        >>> italic("foo")
        '<i>foo</i>'
        >>> italic("<i>foo</i>")
        '<i>foo</i>'
    """
    if text.startswith("<i>") and text.endswith("</i>"):
        return text
    return f"<i>{text}</i>"


def lookup_italic(tpl: str, locale: str, *, empty_default: bool = False) -> str:
    """
    Find the *tpl* from the *templates_italic* table of the given *locale*.

    If the *tpl* is not found, it is returned as-is.

        >>> lookup_italic("", "fr")
        ''
        >>> lookup_italic("inexistant", "fr")
        'inexistant'
        >>> lookup_italic("alagoas", "pt")
        'Alagoas'
        >>> lookup_italic("Antropônimo", "pt")
        'Antropônimo'
    """
    from .lang import templates_italic

    default = "" if empty_default else tpl
    looking_for = tpl

    if locale == "pt":
        looking_for = capitalize(tpl)
        default = tpl

    return templates_italic[locale].get(looking_for, default)


def number(number: str, fsep: str, tsep: str) -> str:
    """
    Format a number using the provided float and thousands separators.

        >>> number("1 000 000 000 000", ",", " ")
        '1 000 000 000 000'
        >>> number("1000000", ",", " ")
        '1 000 000'
        >>> number("1000000", ".", "")
        '1000000'
        >>> number("1000000", ".", ",")
        '1,000,000'
        >>> number("-1000000", ",", " ")
        '−1 000 000'
        >>> number("-1000000", "", "")
        '−1000000'
        >>> number("−1000000", ".", ",")
        '−1,000,000'
        >>> number("4.54609", "," , " ")
        '4,54609'
        >>> number("4.54609", "." , ",")
        '4.54609'
        >>> number("22905", "," , ".")
        '22.905'
        >>> number("1.30", "," , ".")
        '1,30'
    """
    # Remove superfluous spaces
    number = number.replace(" ", "")

    # Handle unicode minus U+2212 character before doing the conversion
    number = number.replace("−", "-")

    # Keep that value to restore leading zeros that would be lost with the int/float conversion
    digits_count = sum(bool(c.isdigit()) for c in number)

    # Convert
    try:
        # Integer
        res = f"{int(number):,}"
    except ValueError:
        # Float
        res = f"{float(number):,}"

    new_digits_count = sum(bool(c.isdigit()) for c in res)
    if new_digits_count != digits_count:
        res += "0" * (digits_count - new_digits_count)

    # Replace the current thousands separator with "|";
    # then replace the dot with the float separator;
    # and lastly replace the "|" with the deisred thousands separator.
    # This 3-steps-replacement is needed for when separators are replacing each other.
    res = res.replace(",", "|").replace(".", fsep).replace("|", tsep)

    # Always return unicode minus U+2212 character for negative numbers
    return res.replace("-", "−")


def parenthesis(text: str) -> str:
    """
    Return the *text* surrounded by parenthesis.

        >>> parenthesis("foo")
        '(foo)'
    """
    return f"({text})"


def person(word: str, parts: list[str]) -> str:
    """
    Format a person name.

        >>> person("foo", ["Aldous", "Huxley"])
        'Aldous Huxley'
        >>> person("foo", ["Théodore Agrippa d’", "Aubigné"])
        'Théodore Agrippa d’ Aubigné'
        >>> person("foo", ["Théodore Agrippa d’", "Aubigné", "'=oui"])
        'Théodore Agrippa d’Aubigné'
        >>> person("foo", ["L. L. Zamenhof"])
        'L. L. Zamenhof'
        >>> person("foo", ["lang=en", "Roger", "Adams"])
        'Roger Adams'
        >>> person("foo", ["", "Brantôme", "Brantôme (écrivain)"])
        'Brantôme'

    Source: https://fr.wiktionary.org/wiki/Mod%C3%A8le:nom_w_pc
    """
    data = [p for p in parts if "=" in p]
    parts = [p for p in parts if "=" not in p]
    res = parts.pop(0)

    # First name only
    if not parts:
        return res

    # Last name only or first name + last name
    space = "" if ("'=oui" in data or not res) else " "
    res += space + parts.pop(0)
    return res


def ruby(text: str, top: str) -> str:
    """
    Render a Ruby HTML annotation.

        >>> ruby("A", "B")
        '<ruby>A<rt>B</rt></ruby>'
    """
    return f"<ruby>{text}<rt>{top}</rt></ruby>"


def sentence(parts: list[str]) -> str:
    """
    Capitalize the first item in *parts* and concat with the second one.

        >>> sentence(["superlatif de", "petit", "fr"])
        'Superlatif de petit'
        >>> sentence(["variante de", "ranche", "fr"])
        'Variante de ranche'
        >>> sentence(["RFC", "5322"])
        'RFC 5322'
        >>> sentence(["comparatif de", "bien", "fr", "adv"])
        'Comparatif de bien'
    """
    return capitalize(concat(parts, " ", indexes=[0, 1]))


def small(text: str) -> str:
    """
    Return the *text* surrounded by small HTML tags.

        >>> small("foo")
        '<small>foo</small>'
    """
    return f"<small>{text}</small>"


def small_caps(text: str) -> str:
    """
    Return the *text* surrounded by the CSS style to use small capitals.

    Small-caps glyphs typically use the form of uppercase letters but are reduced
    to the size of lowercase letters.

        >>> small_caps("Dupont")
        "<span style='font-variant:small-caps'>Dupont</span>"
    """
    return f"<span style='font-variant:small-caps'>{text}</span>"


def strike(text: str) -> str:
    """
    Return the *text* surrounded by strike HTML tags.

        >>> strike("foo")
        '<s>foo</s>'
    """
    return f"<s>{text}</s>"


def strong(text: str) -> str:
    """
    Return the *text* surrounded by strong HTML tags.

        >>> strong("foo")
        '<b>foo</b>'
    """
    return f"<b>{text}</b>"


def subscript(text: str) -> str:
    """
    Return the *text* surrounded by subscript HTML tags.

    Subscript text appears half a character below the normal line,
    and is sometimes rendered in a smaller font.
    Subscript text can be used for chemical formulas.

        >>> subscript("foo")
        '<sub>foo</sub>'
    """
    return f"<sub>{text}</sub>"


def superscript(text: str) -> str:
    """
    Return the *text* surrounded by superscript HTML tags.

    Superscript text appears half a character above the normal line,
    and is sometimes rendered in a smaller font.

        >>> superscript("foo")
        '<sup>foo</sup>'
    """
    return f"<sup>{text}</sup>"


def term(text: str) -> str:
    """
    Format a "term", e.g. return the *text* in italic and surrounded by parenthesis.

    If the *text* is already in such style, it will not be processed again.

        >>> term("")
        ''
        >>> term("foo")
        '<i>(foo)</i>'
        >>> term("Foo")
        '<i>(Foo)</i>'
        >>> term("<i>(Foo)</i>")
        '<i>(Foo)</i>'
    """
    if not text:
        return ""
    return text if text.startswith("<i>(") else italic(parenthesis(text))


def underline(text: str) -> str:
    """
    Return the *text* surrounded by underline HTML tags.

        >>> underline("foo")
        '<u>foo</u>'
    """
    return f"<u>{text}</u>"


def unique(seq: list[str]) -> list[str]:
    """
    Return *seq* without duplicates.

        >>> unique(["foo", "foo"])
        ['foo']
    """
    res: list[str] = []
    for item in seq:
        if item not in res:
            res.append(item)
    return res


__all__ = (
    "capitalize",
    "century",
    "chimy",
    "chinese",
    "extract_keywords_from",
    "code",
    "color",
    "concat",
    "coord",
    "eval_expr",
    "flatten",
    "int_to_roman",
    "italic",
    "lookup_italic",
    "number",
    "parenthesis",
    "person",
    "ruby",
    "sentence",
    "small",
    "small_caps",
    "strike",
    "strong",
    "subscript",
    "superscript",
    "term",
    "underline",
    "unique",
)
