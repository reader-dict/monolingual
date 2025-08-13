"""
Python conversion of the ru-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:ru-translit

Current version from 2025-01-08 09:03
  - https://en.wiktionary.org/w/index.php?title=Module:ru-translit&oldid=83519164
"""

import re
import unicodedata
from dataclasses import dataclass

# Unicode constants
AC = "\u0301"  # acute ́
GR = "\u0300"  # grave ̀
BR = "\u0306"  # breve ̆
DI = "\u0308"  # diaeresis ̈
DIACRITICS = AC + GR + BR + DI + "\u0302\u0304\u0307\u030a\u030c\u030f\u0323\u0328"
TEMP_G = "\ufff1"

# Character sets
VOWELS = "аеиіоуыѣэюяѥѵaæɐeəɛiɪɨoɵuyʊʉАЕИІОУЫѢЭЮЯѤѴAEƐIOUY"
WORD_CHARS = rf"a-zA-Zа-яА-ЯёЁ{re.escape(DIACRITICS)}"

# Translation tables
LETTERS = str.maketrans(
    {
        ord(c): r
        for c, r in [
            # Cyrillic lowercase
            ("а", "a"),
            ("б", "b"),
            ("в", "v"),
            ("г", "g"),
            ("д", "d"),
            ("е", "je"),
            ("ж", "ž"),
            ("з", "z"),
            ("и", "i"),
            ("й", "j"),
            ("к", "k"),
            ("л", "l"),
            ("м", "m"),
            ("н", "n"),
            ("о", "o"),
            ("п", "p"),
            ("р", "r"),
            ("с", "s"),
            ("т", "t"),
            ("у", "u"),
            ("ф", "f"),
            ("х", "x"),
            ("ц", "c"),
            ("ч", "č"),
            ("ш", "š"),
            ("щ", "šč"),
            ("ъ", "ʺ"),
            ("ы", "y"),
            ("ь", "ʹ"),
            ("э", "e"),
            ("ю", "ju"),
            ("я", "ja"),
            # Cyrillic uppercase
            ("А", "A"),
            ("Б", "B"),
            ("В", "V"),
            ("Г", "G"),
            ("Д", "D"),
            ("Е", "Je"),
            ("Ж", "Ž"),
            ("З", "Z"),
            ("И", "I"),
            ("Й", "J"),
            ("К", "K"),
            ("Л", "L"),
            ("М", "M"),
            ("Н", "N"),
            ("О", "O"),
            ("П", "P"),
            ("Р", "R"),
            ("С", "S"),
            ("Т", "T"),
            ("У", "U"),
            ("Ф", "F"),
            ("Х", "X"),
            ("Ц", "C"),
            ("Ч", "Č"),
            ("Ш", "Š"),
            ("Щ", "Šč"),
            ("Ъ", "ʺ"),
            ("Ы", "Y"),
            ("Ь", "ʹ"),
            ("Э", "E"),
            ("Ю", "Ju"),
            ("Я", "Ja"),
            # Special cases
            ("«", '"'),
            ("»", '"'),
            ("і", "i"),
            ("ѳ", "f"),
            ("ѣ", "jě"),
            ("ѵ", "i"),
            ("І", "I"),
            ("Ѳ", "F"),
            ("Ѣ", "Jě"),
            ("Ѵ", "I"),
            ("ѥ", "je"),
            ("ѯ", "ks"),
            ("ѱ", "ps"),
            ("Ѥ", "Je"),
            ("Ѯ", "Ks"),
            ("Ѱ", "Ps"),
            (AC, AC),
        ]
    }
)

ALIASES = str.maketrans(
    {
        ord(c): r
        for c, r in [
            ("є", "е"),
            ("ꙁ", "з"),
            ("ꙃ", "з"),
            ("ѕ", "з"),
            ("ї", "і"),
            ("ꙋ", "у"),
            ("ѡ", "о"),
            ("ѿ", "о"),
            ("ꙑ", "ы"),
            ("ꙗ", "я"),
            ("ѧ", "я"),
            ("ѫ", "у"),
            ("ѩ", "я"),
            ("ѭ", "ю"),
            ("Є", "Е"),
            ("Ꙁ", "З"),
            ("Ꙃ", "З"),
            ("Ѕ", "З"),
            ("Ї", "І"),
            ("Ꙋ", "У"),
            ("Ѡ", "О"),
            ("Ѿ", "О"),
            ("Ꙑ", "Ы"),
            ("Ꙗ", "Я"),
            ("Ѧ", "Я"),
            ("Ѫ", "У"),
            ("Ѩ", "Я"),
            ("Ѭ", "Ю"),
            ("'", "'"),
        ]
    }
)

# Special mappings
PLAIN_E = {"е": "e", "ѣ": "ě", "э": "ɛ", "Е": "E", "Ѣ": "Ě", "Э": "Ɛ"}
JO_LETTERS = {"ё": "jo", "ѣ̈": "jǒ", "я̈": "jǫ", "Ё": "Jo", "Ѣ̈": "Jǒ", "Я̈": "Jǫ"}


@dataclass
class State:
    """Transliteration state."""

    i: int = 0
    vowels: int = 0
    primary: bool = False
    final_jo: int | None = None
    dash_before: bool = False


def apply_tr_fixes(text: str) -> str:
    """Apply pronunciation transformations."""
    text = text.translate(ALIASES)
    text = unicodedata.normalize("NFD", text)

    if "го" not in text and "то" not in text:
        return text

    if "го" in text:
        text = _handle_go_transformations(text)

    if "то" in text:
        text = _handle_chto_transformations(text)

    # Handle мягкий, лёгкий
    return re.sub(rf"([МмЛл][яеё][{AC}{GR}]?)г([кч])", r"\1х\2", text)


def _handle_go_transformations(text: str) -> str:
    """Handle all -го related transformations."""
    g_to_v = {"г": "в", "Г": "В"}

    def replace_g(match: re.Match[str]) -> str:
        groups = match.groups()
        return f"{groups[0]}{g_to_v[groups[1]]}{groups[2]}{''.join(groups[3:])}"

    # Handle какого-нибудь/-либо/-то first
    text = re.sub(rf"([кКтТ][аА][кК][оеОЕ][{AC}{GR}]?)([гГ])([оО]-)", replace_g, text)

    def protect_exception(text: str, pattern: str) -> str:
        """Protect specific patterns from г→в transformation."""
        if match := re.match(rf"^(.)(.*)(го[{AC}{GR}]?)(%-?)$", pattern):
            m1, m2, m3, m4 = match.groups()

            regex = rf"(?<![{WORD_CHARS}])([{m1.upper()}{m1}"
            regex += re.sub(r"\204[\128\129]", f"[{AC}{GR}]?", m2) + ")"
            regex += re.sub(r"\204[\128\129]", f"[{AC}{GR}]?", m3)
            regex = re.sub(r"г\(", f"г({TEMP_G}", regex)
            regex += "%-)" if m4 == "-" else rf")(?![{WORD_CHARS}])"

            return re.sub(regex, rf"\1{TEMP_G}\2", text)
        return text

    # Apply exceptions from Lua
    exceptions = [
        "мно́го",
        "н[еа]мно́го",
        "до́рого",
        "недо́рого",
        "стро́го",
        "нестро́го",
        "на́строго",
        "убо́го",
        "пол[ао]́го",
        "ого́",
        "го́го",
        "ваго́го",
        "ло́го",
        "п[ео]́го",
        "со́го",
        "То́го",
        "ле́го",
        "игого́",
        "огого́",
        "альбиньязего",
        "д[иі]е́го",
        "бо́лого",
        "гр[иі]е́го",
        "манче́го",
        "пичис[иі]е́го",
        "тенкодого",
        "хио́го",
        "аго-",
        "его-",
        "ого-",
    ]

    for exception in exceptions:
        text = protect_exception(text, exception)

    # Handle compound adjectives
    if re.search(rf"но[{AC}{GR}]?го(?![{WORD_CHARS}])", text):
        compounds = [
            "безно́го",
            "босоно́го",
            "веслоно́го",
            "длинноно́го",
            "двуно́го",
            "коротконо́го",
            "кривоно́го",
            "одноно́го",
            "пятино́го",
            "трёхно́го",
            "трехно́го",
            "хромоно́го",
            "четвероно́го",
            "шестино́го",
        ]
        for compound in compounds:
            text = protect_exception(text, compound)

    # Main -го transformations
    boundary = rf"[{WORD_CHARS}{re.escape(TEMP_G)}]"
    pattern = rf"([оеОЕ][{AC}{GR}]?)([гГ])([оО][{AC}{GR}]?)"
    text = re.sub(rf"{pattern}(?!{boundary})", replace_g, text)
    text = re.sub(rf"{pattern}([сС][яЯ][{AC}{GR}]?)(?!{boundary})", replace_g, text)

    # Handle сегодня
    text = re.sub(rf"(?<![{WORD_CHARS}])([Сс]е)г(о[{AC}{GR}]?дня(?:шн)?)(?![{WORD_CHARS}])", r"\1в\2", text)

    return text.replace(TEMP_G, "г")


def _handle_chto_transformations(text: str) -> str:
    """Handle что transformations."""
    ch_to_sh = {"ч": "ш", "Ч": "Ш"}

    def replace_ch(match: re.Match[str]) -> str:
        return ch_to_sh[match[1]] + match[2]

    # что, чтобы, чтоб and ничто
    text = re.sub(rf"(?<![{WORD_CHARS}])([Чч])(то[{AC}{GR}]?(?:бы?)?)(?![{WORD_CHARS}])", replace_ch, text)
    return re.sub(rf"(?<![{WORD_CHARS}])([Нн]и)ч(то[{AC}{GR}]?)(?![{WORD_CHARS}])", r"\1ш\2", text)


def tr_after_fixes(text: str, jo_accent: str = "auto") -> str:
    """Transliterate after pronunciation fixes."""
    text = unicodedata.normalize("NFC", text.translate(ALIASES))
    result: list[str] = []

    # Process word by word
    non_word_pattern = rf"([^{WORD_CHARS}'()\[\]]*)"
    word_pattern = rf"([{WORD_CHARS}'()\[\]]*)"

    for match in re.finditer(rf"{non_word_pattern}{word_pattern}", text):
        before, word = match.groups()

        result.extend(before)
        if word:
            result.extend(_transliterate_word(word, jo_accent, result))

    return unicodedata.normalize("NFC", "".join(result))


def _transliterate_word(word: str, jo_accent: str, context: list[str]) -> list[str]:
    """Transliterate a single word."""
    chars = list(unicodedata.normalize("NFD", word))
    state = State()
    result: list[str] = []

    # Check for prefix (preceded by dash)
    if context and context[-1] == "-" and (len(context) < 2 or context[-2].isspace()):
        state.dash_before = True

    while state.i < len(chars):
        _process_char(chars, state, result)
        state.i += 1

    # Add implicit stress to ё if needed
    if (
        jo_accent != "none"
        and state.final_jo is not None
        and not state.primary
        and not (chars and chars[-1] == "-")
        and (jo_accent == "mono" or state.vowels > 1 or state.dash_before)
    ):
        result[state.final_jo] += AC

    return result


def _process_char(chars: list[str], state: State, result: list[str]) -> None:
    """Process a single character."""
    char = chars[state.i]
    prev = _get_prev_char(chars, state.i)
    next_char = _get_next_char(chars, state.i)

    if char in VOWELS:
        state.vowels += 1

    # Handle composite characters
    if next_char == DI:
        state.i += 1
        char = unicodedata.normalize("NFC", char + DI)
        if _handle_jo_letter(char, prev, result, chars, state):
            return
    elif next_char == BR:
        state.i += 1
        char = unicodedata.normalize("NFC", char + BR)
    elif char == AC:
        state.primary = True
        result.append(char)
        return

    # Special transformations
    if char in PLAIN_E and _should_be_plain(char, prev, state.dash_before):
        result.append(PLAIN_E[char])
    elif char in "юЮ" and _check_plain(char, prev, "жшЖШ"):
        result.append("u" if char == "ю" else "U")
    elif char == "ѵ" and prev and prev in "аеиіѣэяѥaæɐeəɛiɪɨАЕИІѢЭЯѤAEƐI":
        chars[state.i] = "в"
        result.append("v")
    elif char in "ъЪ" and state.i == len(chars) - 1:
        pass  # Ignore word-final hard signs
    else:
        result.append(char.translate(LETTERS))


def _get_prev_char(chars: list[str], i: int) -> str | None:
    """Get previous character, skipping diacritics."""
    for j in range(i - 1, -1, -1):
        if chars[j] not in f"{DIACRITICS}()'":
            return _handle_short_i(chars, chars[j], j + 1)
    return None


def _get_next_char(chars: list[str], i: int) -> str | None:
    """Get next character, skipping parentheses."""
    for j in range(i + 1, len(chars)):
        if chars[j] not in "()":
            return _handle_short_i(chars, chars[j], j + 1, True)
    return None


def _handle_short_i(chars: list[str], char: str, i: int, adjust: bool = False) -> str:
    """Handle и with breve (й)."""
    if char in "иИ" and i < len(chars) and chars[i] == BR:
        if adjust:
            chars.pop(i)
        char = unicodedata.normalize("NFC", char + BR)
        chars[i - 1] = char
    return char


def _check_plain(this: str, prev: str | None, check: str) -> bool:
    """Check if should be plain based on previous char."""
    return prev is not None and (this.islower() or prev.islower()) and prev in check


def _should_be_plain(char: str, prev: str | None, dash_before: bool) -> bool:
    """Check if e-type letter should be plain."""
    if not prev and dash_before:
        return True
    check_set = VOWELS + "ʹʺъЪьЬ" + ("" if char in "эЭ" else "йЙ")
    return prev is not None and (char.islower() or prev.islower()) and prev not in check_set


def _handle_jo_letter(char: str, prev: str | None, result: list[str], chars: list[str], state: State) -> bool:
    """Handle ё letters."""
    if tr := JO_LETTERS.get(char):
        # Remove "j" after hushing consonants
        if _check_plain(char, prev, "жчшщЖЧШЩ"):
            tr = tr[1:]
            if char.isupper():
                tr = tr.upper()

        result.append(tr)

        # Mark for potential stress
        if state.i + 1 < len(chars) and chars[state.i + 1] != GR:
            state.final_jo = len(result) - 1

        return True
    return False


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:ru-translit/testcases&oldid=80630776

    >>> transliterate("без")
    'bez'
    >>> transliterate("То́го")
    'Tóvo'
    >>> transliterate("того́")
    'tovó'
    """
    return tr_after_fixes(apply_tr_fixes(text))
