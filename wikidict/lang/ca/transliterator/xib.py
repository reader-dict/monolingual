"""
Python conversion of the xib-trans module.
Link:
  - https://ca.wiktionary.org/wiki/M%C3%B2dul:xib-trans

Current version from 2024-07-10 11:18
  - https://ca.wiktionary.org/w/index.php?title=M%C3%B2dul:xib-trans&oldid=2349253
"""

import re

table_epigraphy = {
    "a2": '<svg width="33" height="53" viewBox="0 0 33 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path830" d="m7 12v28l19-14z" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "a3": '<svg width="26" height="53" viewBox="0 0 26 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path1465" d="m8 8v35" fill="none" stroke="#000" stroke-width="3.5"/><path id="path39" d="m11 10a8.8955 9.4969 0 0 1 8.5159 9.6341 8.8955 9.4969 0 0 1-8.789 9.3504" fill="none" stroke="#000" stroke-linecap="square" stroke-width="3.5"/></svg>',
    "ba1": '<svg width="16" height="53" viewBox="0 0 16 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path1465" d="m8 8v35" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "be1": '<svg width="36" height="53" viewBox="0 0 36 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path10" d="m7 42 22-22-11-10-11 10 22 22" fill="none" stroke="#000" stroke-linecap="square" stroke-width="3"/></svg>',
    "bi1": '<svg width="31" height="53" viewBox="0 0 31 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path4527" d="m8 43.15v-33h15l-7 11" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "bo2": '<svg width="37" height="53" viewBox="0 0 37 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><g fill="none" stroke="#000" stroke-width="3.5"><path id="path4524" d="m7 9.1496 23 34"/><path id="path4524-1" d="m30 9.1496-23 34"/><path id="path4541" d="m6 26.15h25"/></g></svg>',
    "e1": '<svg width="27" height="53" viewBox="0 0 7.1437 14.023" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer1" transform="translate(0 -282.98)" fill="none" stroke="#000" stroke-width=".92604"><path id="path823" d="m2.1167 284.83v9.525"/><path id="path825" d="m2.1167 294.09 3.175-2.6458" stroke-linejoin="round"/><path id="path827" d="m2.1167 290.91 3.175-2.6458"/></g></svg>',
    "i1": '<svg width="36" height="53" viewBox="0 0 36 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path21" d="m8 43v-31l15 14 7-15" fill="none" stroke="#000" stroke-width="3.5"/><path id="path23" d="m22 8-5 11" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "i2": '<svg width="53" height="53" viewBox="0 0 53 53" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3" transform="matrix(1 0 0 1.0385 1.3155 -2.7155)"><path id="path4832" d="m5.6845 44.02 14-29.85 12 25.998 14-29.85" fill="none" stroke="#000" stroke-width="3.8"/></g><path id="path4533" d="m27 25 7-17" fill="none" stroke="#000" stroke-width="3.8"/></svg>',
    "ka1": '<svg width="42" height="53" viewBox="0 0 42 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path844" d="m6 43 15-31.85 15 32" fill="none" stroke="#000" stroke-width="3.5"/><path id="path1398" d="m28 27-7 16" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "ke1": '<svg width="31" height="53" viewBox="0 0 31 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path4505" d="m25 10-17 16 17 16" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "ke2": '<svg width="31" height="53" viewBox="0 0 31 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path4505" d="m25 10-17 16 17 16" fill="none" stroke="#000" stroke-width="3.5"/><path id="path4520" d="m18 18 7 7" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "ki1": '<svg width="42" height="53" viewBox="0 0 11.112 14.023" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer1" transform="translate(0 -282.98)"><path id="path839" d="m9.2604 288.27-3.7042-2.6458v8.2021l-3.7042-2.6458" fill="none" stroke="#000" stroke-width=".92604"/></g></svg>',
    "ko1": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3"><path id="text2856" d="m7.712 9.1005 10.875 16.313-12.469 18.688h29.937l-12-18.188 11.25-16.813h-27.594zm7.1875 3.1563h13.188l-6.5938 9.8438-6.5938-9.8438zm6.2188 16.938 7.75 11.75h-15.562l7.8125-11.75z"/></g></svg>',
    "ku1": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3"><path id="path4628" d="m7.1016 26.725 14.37-15.52 13.49 15.434-13.49 15.305-14.37-15.22zm15.249-0.13528c0 0.46592-0.43214 0.84406-0.96463 0.84406s-0.96463-0.37814-0.96463-0.84406c0-0.46591 0.43214-0.84405 0.96463-0.84405s0.96463 0.37814 0.96463 0.84405z" fill="none" stroke="#000" stroke-width="3.8px"/></g></svg>',
    "ku3": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path2857" d="m7.9167 26.235 14.37-15.52 13.49 15.434-13.49 15.305-14.37-15.22z" fill="none" stroke="#000" stroke-width="3.8px"/></svg>',
    "l1": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3"><path id="text4600" d="m10.209 44.157-4.4158-1.0376 12.783-33.955h5.3672l12.875 33.955-4.4607 1.0376-11.109-30.328-11.039 30.328"/></g></svg>',
    "n2": '<svg width="53" height="53" viewBox="0 0 53 53" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3" transform="matrix(1 0 0 1.0385 1.3155 -2.7155)"><path id="path4832" d="m5.6845 44.02 14-29.85 12 25.998 14-29.85" fill="none" stroke="#000" stroke-width="3.8"/></g></svg>',
    "o1": '<svg width="35" height="53" viewBox="0 0 35 53" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer1" transform="translate(0 -282.98)" fill="none" stroke="#000" stroke-width="3.5"><path id="path46" d="m8 290.98v35"/><path id="path46-0" d="m28 290.98v35"/><path id="path1450" d="m9 308.98h18"/></g></svg>',
    "r1": '<svg width="33" height="53" viewBox="0 0 33 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path830" d="m26 12v28l-19-14z" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "ŕ3": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="rect3835" d="m21.091 8.7916-1.3062 1.3064-10.569 10.45-1.3062 1.425 1.3062 1.3061 10.094 10.094-0.11875 11.519 3.8 0.1185 0.11875-11.994 9.7375-9.8565 1.3062-1.306-1.3062-1.3061-10.45-10.45-1.3062-1.3064zm0 5.3435 7.7188 7.719-7.8375 7.8375-7.7188-7.7186 7.8375-7.8379z" fill-rule="evenodd"/></svg>',
    "ŕ5": '<svg width="42" height="53" viewBox="0 0 42.52 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3"><path id="path5280" d="m20.906 9.1875c-6.4498 3e-7 -11.812 5.3121-11.812 11.969-1e-7 5.8355 4.1343 10.596 9.5 11.688v11.531h4.0625v-11.438c5.6512-0.84733 10.094-5.7323 10.094-11.781 0-6.6566-5.3939-11.969-11.844-11.969zm0 3.9062c4.5902 0 8.1875 3.6791 8.1875 8.0625 1e-6 4.3834-3.5973 8-8.1875 8-4.5902 0-8.1562-3.6166-8.1562-8 0-4.3834 3.5661-8.0625 8.1562-8.0625z"/></g></svg>',
    "s1": '<svg width="27" height="53" viewBox="0 0 27 53" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer3" transform="matrix(1 0 0 1.0333 0 -1.5213)"><path id="path3473" d="m19 11.15-11 10 11 10-11 10" fill="none" stroke="#000" stroke-linecap="square" stroke-width="3.4431"/></g></svg>',
    "ś1": '<svg width="40" height="53" viewBox="0 0 10.583 14.023" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer1" transform="translate(0 -282.98)" fill="none" stroke="#000" stroke-width=".92604"><path id="path2041" d="m2.1167 294.35 1e-7 -8.4667 3.4396 2.3812"/><path id="path2043" d="m5.0271 288.27 3.4396-2.3812v8.4667"/></g></svg>',
    "ta1": '<svg width="37" height="53" viewBox="0 0 37 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path4524" d="m7 9.1496 23 34" fill="none" stroke="#000" stroke-width="3.5"/><path id="path4524-1" d="m30 9.1496-23 34" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "ti4": '<svg width="36" height="53" viewBox="0 0 36 53" xmlns:xlink="http://www.w3.org/1999/xlink"><g id="layer1" transform="translate(0 -282.98)" fill="none" stroke="#000" stroke-width="3.5"><path id="path19" d="m18 325.98v-35"/><path id="path826" d="m6 291.98 12 18 12-18"/></g></svg>',
    "to2": '<svg width="48" height="53" viewBox="0 0 48 53.15" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path26" d="m7 13.15 16 26h2l16-26" fill="none" stroke="#000" stroke-width="3.5"/><path id="path833" d="m24 12.15v26" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "tu1": '<svg width="42" height="53" viewBox="0 0 42 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path24" d="m7 41 14-30 14 30z" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "u3": '<svg width="40" height="53" viewBox="0 0 40 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path20" d="m6 27 14-17 14 17" fill="none" stroke="#000" stroke-width="3.5"/><path id="path827" d="m20 12v31" fill="none" stroke="#000" stroke-width="3.5"/></svg>',
    "p2": '<svg width="16" height="53" viewBox="0 0 16 53" xmlns:xlink="http://www.w3.org/1999/xlink"><ellipse id="path37" cx="8.0239" cy="31.673" rx="1.5347" ry="1.4894" stroke="#000" stroke-width="1.5119"/><ellipse id="path37-5" cx="8.0647" cy="19.189" rx="1.5347" ry="1.4894" stroke="#000" stroke-width="1.5119"/></svg>',
}
table_epigraphy["ŕ1"] = table_epigraphy["ku3"]
table_epigraphy["r6"] = table_epigraphy["a2"]
table_epigraphy["s102"] = table_epigraphy["s1"]

table_no_dual = {
    "a": table_epigraphy["a2"],
    "e": table_epigraphy["e1"],
    "i": table_epigraphy["i2"],
    "o": table_epigraphy["o1"],
    "u": table_epigraphy["u3"],
    "ba": table_epigraphy["ba1"],
    "be": table_epigraphy["be1"],
    "bi": table_epigraphy["bi1"],
    "bo": table_epigraphy["bo2"],
    "ka": table_epigraphy["ka1"],
    "ke": table_epigraphy["ke1"],
    "ki": table_epigraphy["ki1"],
    "ko": table_epigraphy["ko1"],
    "ku": table_epigraphy["ku1"],
    "ta": table_epigraphy["ta1"],
    "ti": table_epigraphy["ti4"],
    "to": table_epigraphy["to2"],
    "tu": table_epigraphy["tu1"],
    "l": table_epigraphy["l1"],
    "n": table_epigraphy["n2"],
    "r": table_epigraphy["r1"],
    "ŕ": table_epigraphy["ŕ3"],
    "s": table_epigraphy["s102"],
    "ś": table_epigraphy["ś1"],
    " ": table_epigraphy["p2"],
    "I": table_epigraphy["ba1"],
}

table_dual = {
    "á": table_epigraphy["a3"],
    "a": table_epigraphy["a3"],
    "i": table_epigraphy["i1"],
    "u": table_epigraphy["u3"],
    "ba": table_epigraphy["ba1"],
    "gi": table_epigraphy["ki1"],
    "go": table_epigraphy["ko1"],
    "da": table_epigraphy["ta1"],
    "du": table_epigraphy["tu1"],
    "ř": table_epigraphy["ŕ5"],
    "ś": table_epigraphy["ś1"],
    "I": table_epigraphy["ba1"],
}


def transliterate(text: str, locale: str = "") -> str:
    """
    >>> transliterate("ba")
    '<svg style="width:24px;height:auto;vertical-align:middle" width="16" height="53" viewBox="0 0 16 53" xmlns:xlink="http://www.w3.org/1999/xlink"><path id="path1465" d="m8 8v35" fill="none" stroke="#000" stroke-width="3.5"/></svg>'
    """
    syllabic = {"b", "k", "g", "t", "d"}
    sign = ""
    tr = []
    table = (
        table_epigraphy
        if re.search(r"[123456789]", text)
        else table_dual
        if re.search(r"[áéíóúgḱdâřŝ]", text)
        else table_no_dual
    )

    for i in range(len(text)):
        letter = text[i]
        if letter != "-":
            sign += letter
            if not (text[i + 1 : i + 2].isdigit() or letter in syllabic):
                try:
                    file = table[sign.removesuffix("01")]  # Support both `a1`, and `a101`, keys
                except KeyError:
                    assert 0, f"Missing xib-trans SVG: {sign!r}"
                if file:
                    svg = f'{file[:4]} style="width:24px;height:auto;vertical-align:middle" {file[5:]}'
                    tr.append(svg)
                sign = ""

    return "".join(tr)
