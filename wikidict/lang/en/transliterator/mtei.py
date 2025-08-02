"""
Python conversion of the Mtei-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:Mtei-translit

Current version from 2025-04-03 05:13
  - https://en.wiktionary.org/w/index.php?title=Module:Mtei-translit&oldid=84450018
"""

import re

U = chr

tt = {
    # consonants
    "ꯀ": "kᵃ",
    "ꯈ": "khᵃ",
    "ꯒ": "gᵃ",
    "ꯘ": "ghᵃ",
    "ꯉ": "ngᵃ",
    "ꯆ": "cᵃ",
    "ꫢ": "chᵃ",
    "ꯖ": "jᵃ",
    "ꯓ": "jhᵃ",
    "ꫣ": "nyᵃ",
    "ꫤ": "ttᵃ",
    "ꫥ": "tthᵃ",
    "ꫦ": "ddᵃ",
    "ꫧ": "ddhᵃ",
    "ꫨ": "nnᵃ",
    "ꯇ": "tᵃ",
    "ꯊ": "thᵃ",
    "ꯗ": "dᵃ",
    "ꯙ": "dhᵃ",
    "ꯅ": "nᵃ",
    "ꯄ": "pᵃ",
    "ꯐ": "phᵃ",
    "ꯕ": "bᵃ",
    "ꯚ": "bhᵃ",
    "ꯃ": "mᵃ",
    "ꯌ": "yᵃ",
    "ꯔ": "rᵃ",
    "ꯂ": "lᵃ",
    "ꯋ": "wᵃ",
    "ꫩ": "shᵃ",
    "ꫪ": "ssᵃ",
    "ꯁ": "sᵃ",
    "ꯍ": "hᵃ",
    # finals
    "ꯛ": "k",
    "ꯜ": "l",
    "ꯝ": "m",
    "ꯞ": "p",
    "ꯟ": "n",
    "ꯠ": "t",
    "ꯡ": "ng",
    "ꯢ": "i",
    # independent vowels
    "ꯑ": "ʼᵃ",
    "ꯏ": "ʼi",
    "ꯎ": "ʼu",
    "ꫠ": "ʼe",
    "ꫡ": "ʼo",
    # dependent vowels and diacritics
    "ꯥ": "ā",
    "ꯤ": "i",
    "ꫫ": "ī",
    "ꯨ": "u",
    "ꫬ": "ū",
    "ꯦ": "e",
    "ꯩ": "ei",
    "ꫭ": "āi",
    "ꯣ": "o",
    "ꯧ": "ou",
    "ꫮ": "au",
    "ꫯ": "āu",
    "ꯪ": "ṃ",
    "ꫵ": "ḥ",
    "꫶": "¤",
    # marks
    "꯫": ".",
    "꫰": ",",
    "꫱": "?",
    "ꫳ": "˶",
    "ꫴ": "˶˶",
    "꯭": "͟",
    # numerals
    "꯰": "0",
    "꯱": "1",
    "꯲": "2",
    "꯳": "3",
    "꯴": "4",
    "꯵": "5",
    "꯶": "6",
    "꯷": "7",
    "꯸": "8",
    "꯹": "9",
    # zero-width space (display it if it's hidden in a word)
    U(0x200B): "‼",
    # zero-width non-joiner and joiner (display it if it's hidden in a word)
    U(0x200C): "₋",
    U(0x200D): "₊",
}


def tr(text: str) -> str:
    # Replace each character using the mapping table
    text = "".join(tt.get(char, char) for char in text)

    # 1. Remove ᵃ if followed by a vowel
    text = re.sub(r"ᵃ([aeiouāīū])", r"\1", text)
    # 2. Remove ᵃ followed by ¤
    text = re.sub(r"ᵃ¤", "", text)
    # 3. Replace ᵃ followed by ͟ with ͟
    text = re.sub(r"ᵃ͟", "͟", text)
    # 4. Replace remaining ᵃ with a
    text = text.replace("ᵃ", "a")
    # 5. Remove ¤
    return text.replace("¤", "")


def transliterate(text: str, locale: str = "") -> str:
    """
    >>> transliterate("ꯑꯔꯥꯝꯕꯥꯢ")
    'ʼarāmbāi'
    """
    return tr(text)
