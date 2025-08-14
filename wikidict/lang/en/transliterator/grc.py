"""
Python conversion of the grc-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:grc-translit

Current version from 2025-04-24 11:34
  - https://en.wiktionary.org/w/index.php?title=Module:grc-translit&oldid=85707340
  - https://en.wiktionary.org/w/index.php?title=Module:grc-utilities/data&oldid=85711172
"""

import re
import unicodedata
from typing import Any

# Module:grc-utilities/data
U = chr
macron = U(0x304)
spacing_macron = U(0xAF)
modifier_macron = U(0x2C9)
breve = U(0x306)
spacing_breve = U(0x2D8)
rough = U(0x314)
smooth = U(0x313)
diaeresis = U(0x308)
acute = U(0x301)
grave = U(0x300)
circum = U(0x342)
Latin_circum = U(0x302)
coronis = U(0x343)
subscript = U(0x345)
undertie = U(0x35C)  # combining double breve below

diacritics = {
    "macron": macron,
    "spacing_macron": spacing_macron,
    "modifier_macron": modifier_macron,
    "breve": breve,
    "spacing_breve": spacing_breve,
    "rough": rough,
    "smooth": smooth,
    "diaeresis": diaeresis,
    "acute": acute,
    "grave": grave,
    "circum": circum,
    "Latin_circum": Latin_circum,
    "coronis": coronis,
    "subscript": subscript,
}

diacritics_all = list(diacritics.values())
diacritics_combining = [d for d in diacritics_all if d not in (spacing_macron, modifier_macron, spacing_breve)]

data: dict[str, Any] = {"diacritics": diacritics.copy()}
data["diacritics"]["all"] = "".join(diacritics_all)
data["diacritics"]["combining"] = "".join(diacritics_combining)
data["named"] = data["diacritics"]
data["diacritic"] = rf"[{data['diacritics']['all']}]"
data["combining_diacritic"] = rf"[{data['diacritics']['combining']}]"
data["all"] = data["diacritic"]
data["diacritic_groups"] = {
    1: rf"[{macron}{breve}]",
    2: rf"[{diaeresis}{smooth}{rough}]",
    3: rf"[{acute}{grave}{circum}]",
    4: subscript,
}
data["groups"] = data["diacritic_groups"]
data["diacritic_groups"]["accents"] = data["groups"][3]
data["length"] = {"optional": rf"{macron}?{breve}?"}
data["length"]["mandatory"] = rf"\f[{macron}{breve}]{data['length']['optional']}"
data["diacritic_order"] = {
    macron: 1,
    breve: 2,
    rough: 3,
    smooth: 3,
    diaeresis: 3,
    acute: 4,
    grave: 4,
    circum: 4,
    subscript: 5,
}
data["diacritical_conversions"] = {
    spacing_macron: macron,
    modifier_macron: macron,
    spacing_breve: breve,
    "῾": rough,
    "ʽ": rough,
    "᾿": smooth,
    "ʼ": smooth,
    "´": acute,
    "`": grave,
    "῀": circum,
    "ˆ": circum,
    Latin_circum: circum,
    "¨": diaeresis,
}
data["canonical"] = {
    "ϴ": "Θ",
    "Ϗ": "Καί",
    "Ϗ̀": "Καὶ",
    "Ϟ": "Ϙ",
    "Ϲ": "Σ",
    "ϒ": "Υ",
    "ϓ": "Ύ",
    "ϔ": "Ϋ",
    "Ϡ": "Ͳ",
    "ϐ": "β",
    "ϵ": "ε",
    "ϑ": "θ",
    "ϰ": "κ",
    "ϗ": "καί",
    "ϗ̀": "καὶ",
    "ϖ": "π",
    "ϟ": "ϙ",
    "ϱ": "ρ",
    "ς": "σ",
    "ϲ": "σ",
    "ϕ": "φ",
    "ϡ": "ͳ",
}
data["consonants"] = "ΒβΓγΔδϜϝͶͷϚϛΖζͰͱΘθͿϳΚκΛλΜμΝνΞξΠπϺϻϘϙϞϟΡρΣσςϹϲΤτΦφΧχΨψͲͳϠϡϷϸ"
data["consonant"] = rf"[{data['consonants']}]"
data["vowels"] = "ΑαΕεΗηΙιΟοΥυΩω"
data["vowel"] = rf"[{data['vowels']}]"
data["word_characters"] = (
    r"\*ΑαΒβΓγΔδΕεΖζΗηΘθΙιΚκΛλΜμΝνΞξΟοΠπΡρΣσΤτΥυΦφΧχΨψΩωϜϝϚϛϞϟϠϡϷϸͰͱͲͳϺϻϘϙϹϲϏϗ"
    + data["diacritics"]["combining"]
    + undertie
)
data["word_character"] = rf"[{data['word_characters']}]"

# Module:grc-translit
diacritic = data["diacritic"]
diacritics = data["diacritics"]

acute = diacritics["acute"]
grave = diacritics["grave"]
circumflex = diacritics["circum"]
smooth = diacritics["smooth"]
rough = diacritics["rough"]
breve = diacritics["breve"]
macron = diacritics["macron"]
subscript = diacritics["subscript"]
vowel = data["vowel"]
hat = diacritics["Latin_circum"]
au_subscript = rf"^[αυ].*{subscript}$"
question_mark = chr(0x37E)
velar = r"[γκξχϙ]"
long_vowels = {"η": "e", "ω": "o"}
tt = {
    # Vowels
    "α": "a",
    "ε": "e",
    "ι": "i",
    "ο": "o",
    "υ": "u",
    # Consonants
    "β": "b",
    "γ": "g",
    "δ": "d",
    "ζ": "z",
    "θ": "th",
    "κ": "k",
    "λ": "l",
    "μ": "m",
    "ν": "n",
    "ξ": "x",
    "π": "p",
    "ρ": "r",
    "σ": "s",
    "ς": "s",
    "τ": "t",
    "φ": "ph",
    "χ": "kh",
    "ψ": "ps",
    # Other letters
    "ϛ": "st",
    "ϝ": "w",
    "ͱ": "h",
    "ϳ": "j",
    "ϙ": "q",
    "ϻ": "s",
    "ϸ": "š",
    "ͳ": "s",
    # Diacritics
    smooth: "",
    rough: "",
    circumflex: hat,
    subscript: "i",
}
UTF8_char = r".[\x80-\xBF]*"
basic_Greek = r"[\u03A0-\u03FF]"


def get_next_token(tokens: list[str], i: int) -> tuple[int, str, str, str]:
    new = i + 1
    token = tokens[new] if new < len(tokens) else ""
    while token and re.search(r"[()[\]{}]", token):
        new += 1
        token = tokens[new] if new < len(tokens) else ""
    token_lower = token.lower()
    joined = "".join(tokens[i + 1 : new]) if new > i + 1 else ""
    return new, token, token_lower, joined


def translit_letter(match: re.Match[str]) -> str:
    letter, trail = match.groups()
    if tr := long_vowels.get(letter):
        return tr + ("" if breve in trail else macron) + "".join(tt.get(c, c) for c in trail)
    return f"{tt.get(letter, letter)}{''.join(tt.get(c, c) for c in trail)}"


def do_translit(token: str) -> str:
    # Move iota subscript before accent marks
    token = re.sub(f"([{acute}{grave}{circumflex}]+){subscript}", rf"{subscript}\1", token)
    # Transliterate each letter and trailing diacritics
    return re.sub(r"(.)(\W*)", translit_letter, token)


def remove_macron_if_hat(match: re.Match[str]) -> str:
    m = match[0]
    return m.replace(macron, "") if hat in m else m


def standard_diacritics(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(data["diacritical_conversions"].get(char, char) for char in text)
    return unicodedata.normalize("NFD", text)


def canonicalize(text: str) -> str:
    text = standard_diacritics(text)
    text = unicodedata.normalize("NFC", text)
    text = re.sub(f".{grave}", lambda m: data["canonical"].get(m[0], m[0]), text)
    text = "".join(data["canonical"].get(char, char) for char in text)
    return unicodedata.normalize("NFD", text)


def insert_translit(
    output: list[str],
    translit: str,
    token: str,
    lower_token: str,
    next_token: str,
    next_token_lower: str,
    suffix: str,
) -> None:
    # Remove duplicate diacritics
    n = 1
    while n:
        translit, n = re.subn(rf"({diacritic})(\W*)\1", r"\1\2", translit)

    # Remove macron from vowel with circumflex
    translit = re.sub(r"\W+", remove_macron_if_hat, translit)

    # Capitalization logic
    if token == lower_token:
        term = translit + suffix
    elif next_token == next_token_lower:
        # Capitalize first codepoint (may not handle combining marks perfectly)
        term = translit[0].upper() + translit[1:] + suffix
    else:
        term = translit.upper() + suffix

    output.append(term)


info: dict[str, dict[str, Any]] = {}
vowel_t = {"vowel": True}
iota_t = {"vowel": True, "offglide": True}
upsilon_t = {"vowel": True, "offglide": True}
breathy_cons_t: dict[str, Any] = {}
diacritic_t = {"diacritic": True}
breathing_t = {"diacritic": True}


def add_info(characters: str | list[str], t: dict[str, Any]) -> None:
    for character in characters:
        info[character] = t


add_info([macron, breve, diaeresis, acute, grave, circumflex, subscript], diacritic_t)
add_info([rough, smooth], breathing_t)
add_info("ΑΕΗΟΩαεηοω", vowel_t)
add_info("Ιι", iota_t)
add_info("Υυ", upsilon_t)
add_info("ϜϝΡρ", breathy_cons_t)


def make_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    token_i = 0
    vowel_count = 0
    prev = None
    prev_info: dict[str, Any] = {}

    for character in text:
        curr_info = info.get(character, {})
        if curr_info.get("vowel"):
            vowel_count += 1
            if prev and (
                not (vowel_count == 2 and curr_info.get("offglide") and prev_info.get("vowel"))
                or prev_info.get("offglide")
                and curr_info == upsilon_t
                or curr_info == prev_info
            ):
                token_i += 1
                if prev_info.get("vowel"):
                    vowel_count = 1
            elif vowel_count == 2:
                vowel_count = 0
            if token_i >= len(tokens):
                tokens.append("")
            tokens[token_i] += character
        elif curr_info.get("diacritic"):
            vowel_count = 0
            if token_i >= len(tokens):
                tokens.append("")
            tokens[token_i] += character
            if prev_info.get("diacritic") or prev_info.get("vowel"):
                if character == diaeresis:
                    m = re.match(f"^({basic_Greek})({basic_Greek}.+)", tokens[token_i])
                    if m:
                        previous_vowel, vowel_with_diaeresis = m.groups()
                        tokens[token_i] = previous_vowel
                        tokens.insert(token_i + 1, vowel_with_diaeresis)
                        token_i += 1
        else:
            vowel_count = 0
            if prev is not None:
                token_i += 1
            if token_i >= len(tokens):
                tokens.append("")
            tokens[token_i] += character
        prev = character
        prev_info = curr_info
    return tokens


cache: dict[str, list[str]] = {}


def tokenize(text: str) -> list[str]:
    text = unicodedata.normalize("NFD", text)
    if text not in cache:
        cache[text] = make_tokens(text)
    return cache[text]


def tr(text: str, lang: str) -> str:
    if text == "῾":
        return "h"

    # Replace semicolon or Greek question mark with regular question mark, except inside HTML entities
    parts = re.split(r"(&#?\w+;)", canonicalize(text))
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace(";", "?").replace(question_mark, "?")
    text = "".join(parts)

    # Middle dot to semicolon
    text = text.replace("·", ";")
    tokens = tokenize(text)
    next_i, next_token, next_token_lower, suffix = get_next_token(tokens, -1)
    output = [suffix]
    while next_token:
        i, token, lower_token, is_rough = next_i, next_token, next_token_lower, False
        translit = do_translit(lower_token)
        next_i, next_token, next_token_lower, suffix = get_next_token(tokens, i)
        # γ before velar -> n
        if "γ" in lower_token and next_token_lower and re.search(velar, next_token_lower):
            translit = translit.replace("g", "n")
        elif lang == "xbc" and "φ" in lower_token:
            translit = translit.replace("ph", "f")
        elif token == f"ρ{rough}":
            translit = "rh"
        elif token == f"ρ{smooth}":
            translit = "r"
        elif "ρ" in lower_token:
            while next_token_lower and "ρ" in next_token_lower:
                insert_translit(output, translit, token, lower_token, next_token, next_token_lower, suffix)
                i, token, lower_token, is_rough = next_i, next_token, next_token_lower, True
                translit = do_translit(lower_token)
                next_i, next_token, next_token_lower, suffix = get_next_token(tokens, i)
        elif re.search(au_subscript, lower_token):
            translit = re.sub(r"[au]", lambda m: m.group(0) + macron, translit)
        if is_rough or rough in lower_token:
            if re.search(vowel, lower_token):
                translit = f"h{translit}"
            else:
                final = re.search(r"(\w)\W*$", translit)
                if final and final.group(1) != "h":
                    translit += "h"
        insert_translit(output, translit, token, lower_token, next_token, next_token_lower, suffix)
    return unicodedata.normalize("NFC", "".join(output))


def transliterate(text: str, locale: str = "") -> str:
    """
    Test cases: https://en.wiktionary.org/w/index.php?title=Module:grc-translit/testcases&oldid=85742618

    >>> transliterate("λόγος", "grc")
    'lógos'
    >>> transliterate("οἷαι", "grc")
    'hoîai'
    >>> transliterate("ἄγγελος", "grc")
    'ángelos'
    >>> transliterate("ἔγκειμαι", "grc")
    'énkeimai'
    >>> transliterate("σφίγξ", "grc")
    'sphínx'
    >>> transliterate("τυγχάνω", "grc")
    'tunkhánō'
    >>> transliterate("Ἀγϙυλίων", "grc")
    'Anqulíōn'
    >>> transliterate("Ϙόρῐνθοϻ", "grc")
    'Qórĭnthos'
    >>> transliterate("ϝάναξ", "grc")
    'wánax'
    >>> transliterate("ἀρκͱᾱγέτας", "grc")
    'arkhāgétas'
    >>> transliterate("*-ϳω", "grc")
    '*-jō'
    >>> transliterate("'''Υ'''ἱός", "grc")
    "'''U'''hiós"
    >>> transliterate("ταῦρος", "grc")
    'taûros'
    >>> transliterate("νηῦς", "grc")
    'nēûs'
    >>> transliterate("σῦς", "grc")
    'sûs'
    >>> transliterate("ὗς", "grc")
    'hûs'
    >>> transliterate("γυῖον", "grc")
    'guîon'
    >>> transliterate("ἀναῡ̈τέω", "grc")
    'anaṻtéō'
    >>> transliterate("δαΐφρων", "grc")
    'daḯphrōn'
    >>> transliterate("πρηῠ́ς", "grc")
    'prēŭ́s'
    >>> transliterate("τῶν", "grc")
    'tôn'
    >>> transliterate("τοὶ", "grc")
    'toì'
    >>> transliterate("τῷ", "grc")
    'tōî'
    >>> transliterate("τούτῳ", "grc")
    'toútōi'
    >>> transliterate("σοφίᾳ", "grc")
    'sophíāi'
    >>> transliterate("Θρᾴκη", "grc")
    'Thrāíkē'
    >>> transliterate("προσηύδᾱ", "grc")
    'prosēúdā'
    >>> transliterate("Καῖσᾰρ", "grc")
    'Kaîsăr'
    >>> transliterate("ᾰ̓γᾰ́πη", "grc")
    'ăgắpē'
    >>> transliterate("μᾱ̆νός", "grc")
    'mā̆nós'
    >>> transliterate("ὑπόγυͅον", "grc")
    'hupógūion'
    >>> transliterate("ὁ", "grc")
    'ho'
    >>> transliterate("οἱ", "grc")
    'hoi'
    >>> transliterate("εὕρισκε", "grc")
    'heúriske'
    >>> transliterate("ὑϊκός", "grc")
    'huïkós'
    >>> transliterate("πυρρός", "grc")
    'purrhós'
    >>> transliterate("ῥέω", "grc")
    'rhéō'
    >>> transliterate("ῤάριον", "grc")
    'rárion'
    >>> transliterate("Ρ̓ᾶρος", "grc")
    'Râros'
    >>> transliterate("σάἁμον", "grc")
    'sáhamon'
    >>> transliterate("ϝ̔έ", "grc")
    'whé'
    >>> transliterate("μύῤῥᾱ", "grc")
    'múrrhā'
    >>> transliterate("**ἔῥῥευσᾰ", "grc")
    '**érhrheusă'
    >>> transliterate("**Βοῤῤᾶς", "grc")
    '**Borrâs'
    >>> transliterate("Ὀδυσσεύς", "grc")
    'Odusseús'
    >>> transliterate("Εἵλως", "grc")
    'Heílōs'
    >>> transliterate("ᾍδης", "grc")
    'Hāídēs'
    >>> transliterate("ἡ Ἑλήνη", "grc")
    'hē Helḗnē'
    >>> transliterate("ΙΧΘΥΣ", "grc")
    'IKHTHUS'
    >>> transliterate("ἔχεις μοι εἰπεῖν, ὦ Σώκρατες, ἆρα διδακτὸν ἡ ἀρετή;", "grc")
    'ékheis moi eipeîn, ô Sṓkrates, âra didaktòn hē aretḗ?'
    >>> transliterate("τί τηνικάδε ἀφῖξαι, ὦ Κρίτων; ἢ οὐ πρῲ ἔτι ἐστίν;", "grc")
    'tí tēnikáde aphîxai, ô Krítōn? ḕ ou prōì éti estín?'
    >>> transliterate("τούτων φωνήεντα μέν ἐστιν ἑπτά· α ε η ι ο υ ω.", "grc")
    'toútōn phōnḗenta mén estin heptá; a e ē i o u ō.'
    >>> transliterate("πήγ(νῡμῐ)", "grc")
    'pḗg(nūmĭ)'
    >>> transliterate("ἄ(γ)γελος", "grc")
    'á(n)gelos'
    >>> transliterate("ἄγκυρ(ρ)α", "grc")
    'ánkur(rh)a'
    >>> transliterate("καλός&nbsp;καὶ&nbsp;ἀγαθός", "grc")
    'kalós&nbsp;kaì&nbsp;agathós'
    >>> transliterate("καλός&#32;καὶ&#32;ἀγαθός", "grc")
    'kalós&#32;kaì&#32;agathós'
    """
    return tr(text, locale)
