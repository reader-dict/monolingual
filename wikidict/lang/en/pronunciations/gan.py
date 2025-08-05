"""
Source: https://en.wiktionary.org/w/index.php?title=Module:gan-pron&oldid=79050099
"""

import re

initial_conv: dict[str, str] = {
    "b": "p",
    "p": "pʰ",
    "m": "m",
    "f": "f",
    "d": "t",
    "t": "tʰ",
    "l": "l",
    "z": "t͡s",
    "c": "t͡sʰ",
    "s": "s",
    "j": "t͡ɕ",
    "q": "t͡ɕʰ",
    "x": "ɕ",
    "ny": "n̠ʲ",
    "g": "k",
    "k": "kʰ",
    "ng": "ŋ",
    "h": "h",
    "": "",
}

final_conv: dict[str, str] = {
    "z": "z̩",
    "i": "i",
    "u": "u",
    "y": "y",
    "a": "a",
    "ia": "ia",
    "ua": "ua",
    "o": "o",
    "uo": "uo",
    "e": "e",
    "ie": "ie",
    "ue": "ue",
    "ye": "ye",
    "eo": "ɵ",
    "ai": "ai",
    "uai": "uai",
    "oi": "oi",
    "ei": "ei",
    "ii": "ɨi",
    "ui": "ui",
    "au": "au",
    "eu": "ɛu",
    "ieu": "iɛu",
    "iu": "iu",
    "iiu": "ɨu",
    "an": "an",
    "uan": "uan",
    "on": "ɵn",
    "uon": "uɵn",
    "yon": "yɵn",
    "en": "ɛn",
    "ien": "iɛn",
    "in": "in",
    "iin": "ɨn",
    "un": "un",
    "yn": "yn",
    "ang": "aŋ",
    "iang": "iaŋ",
    "uang": "uaŋ",
    "ong": "ɔŋ",
    "iong": "iɔŋ",
    "uong": "uɔŋ",
    "ung": "uŋ",
    "iung": "iuŋ",
    "at": "at̚",
    "uat": "uat̚",
    "ot": "ɵt̚",
    "uot": "uɵt̚",
    "yot": "yɵt̚",
    "et": "ɛt̚",
    "iet": "iɛt̚",
    "uet": "uɛt̚",
    "it": "it̚",
    "iit": "ɨt̚",
    "ut": "ut̚",
    "yt": "yt̚",
    "ah": "aʔ",
    "iah": "iaʔ",
    "uah": "uaʔ",
    "oh": "ɔʔ",
    "ioh": "iɔʔ",
    "uoh": "uɔʔ",
    "uh": "uʔ",
    "iuh": "iuʔ",
    "m": "m̩",
    "n": "n̩",
    "ng": "ŋ̍",
}

tone_conv: dict[str, str] = {
    "1": "⁴²",
    "2": "²⁴",
    "3": "²¹³",
    "4": "³⁵",
    "5": "¹¹",
    "6": "⁵",
    "7": "²",
    "8-1": "¹",
    "8-2": "²",
    "3-1": "²¹³⁻¹³",
    "3-2": "²¹³⁻²⁴",
    "3-3": "²¹³⁻²¹",
    "": "",
}


def ipa(text: str) -> str:
    result: list[str] = []

    for word in text.split("/"):
        syllables = word.strip().split()
        stress: list[str] = []
        initial: list[str] = []
        final: list[str] = []
        tone: list[str] = []
        ipa_syllables: list[str] = []

        for index, syllable in enumerate(syllables):
            s = syllable
            # Stress mark
            if s.startswith("'"):
                stress.append("ˈ")
                s = s[1:]
            else:
                stress.append("")

            # Initial extraction
            m = re.match(r"^[bpmfdtlnzcsjqxgkh]?[gy]?", s)
            ini = m[0] if m else ""
            # Lua's special "ny" handling
            if re.match(r"^.y$", ini) and ini != "ny":
                ini = ini[0]
            if ini == "y":
                ini = ""
            initial.append(ini)

            # Final extraction: skip initial, get up to first digit, star, or string end
            rest = s[len(ini) :]
            m_final = re.match(r"^[^1-8\*]*", rest)
            fin = m_final[0] if m_final else ""
            if fin == "":
                fin = ini
                ini = ""
                initial[-1] = ini
            final.append(fin)

            # Tone extraction
            m_tone = re.search(r"[1-7]+$", s)
            if m_tone:
                t = m_tone[0]
            else:
                t = "8" if index != 0 else ""
            tone.append(t)

        # Now convert
        for idx in range(len(syllables)):
            ini = initial[idx]
            fin = final[idx]
            t = tone[idx]

            ini_conv = initial_conv[ini]

            # Special final rewrites
            if re.match(r"s", ini_conv) and fin == "i":
                fin = "z"
            if ini_conv == "f" and fin == "i":
                fin = "ii"
            if re.match(r"s", ini_conv) and fin == "iu":
                fin = "iiu"
            fin_conv = final_conv[fin]

            # Tone rewrites
            # "3" tone context
            if t == "3":
                next_tone = tone[idx + 1] if idx + 1 < len(tone) else ""
                if re.match(r"[1246]", next_tone):
                    t = "3-1"
                elif re.match(r"[357]", next_tone):
                    t = "3-2"
                elif next_tone:  # 8
                    t = "3-3"
            elif t == "8":
                prev_ipa = ipa_syllables[idx - 1] if idx > 0 else ""
                prev_tone = prev_ipa[-3:] if prev_ipa and len(prev_ipa) >= 3 else ""
                if prev_tone in {"²¹³⁻²¹", "¹¹", "²"}:
                    t = "8-1"
                else:
                    t = "8-2"
            t_conv = tone_conv[t]

            ipa_syllables.append(f"{stress[idx]}{ini_conv}{fin_conv}{t_conv}")

        result.append(" ".join(ipa_syllables))

    return "/, /".join(result)


def rom(text: str) -> str:
    text = ipa(text)
    text = re.sub(r"/", " / ", text)
    text = re.sub(r"([\d-]+)", r"<sup>\1</sup>", text)
    return text
