from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "@",
            [],
            [],
            [],
            {
                "Symbol": [
                    "<i>Informatik (seit 1972):</i> das At; notwendiger Bestandteil und Trennzeichen zwischen Benutzername und Domainname bei E-Mail-Adressen",
                    "<i>Informatik:</i> das At; Syntax-Bestandteil einiger Programmiersprachen (beispielsweise als Präfix vor Array-Variablen in der Programmiersprache Perl)",
                ]
            },
            [],
        ),
        (
            "CIA",
            ["[siːaɪ̯ˈɛɪ̯]"],
            ["mf"],
            ["Abkürzung von Central Intelligence Agency"],
            {"Abkürzung": ["US-amerikanischer Auslandsnachrichtendienst"]},
            [],
        ),
        (
            "volley",
            ["[ˈvɔle]", "[ˈvɔli]", "[ˈvɔlɛɪ̯]"],
            [],
            [
                "Dem seit 1960 im Duden lexikalisierten Wort liegt die englische Kollokation <i>at/on the volley</i> ‚aus der Luft‘ zugrunde.",
            ],
            {
                "Adverb": [
                    "<i>Sport:</i> aus der Luft (angenommen und direkt kraftvoll abgespielt), ohne dass eine Bodenberührung des Sportgeräts vorher stattgefunden hat"
                ]
            },
            [],
        ),
        ("trage", ["[ˈtʁaːɡə]"], [], [], {}, ["tragen"]),
        ("daß", [], [], [], {}, ["dass"]),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    genders: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "de")
    details = parse_word(word, code, "de", force=True)
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{gM}}", "(männliche)"),
        ("{{gM|r}}", "(männlicher)"),
        (
            "{{Kontamination|tele|Telekommunikation|matik|Informatik}}",
            "Kontamination, zusammengesetzt aus „tele-“ (von Telekommunikation) und „-matik“ (von Informatik)",
        ),
        (
            "{{MZ|1|2|3|4|5|6|7|8|9|10|11}}",
            "[1] 2<br/>3<br/>4<br/>5<br/>6<br/>7<br/>8<br/>9<br/>10<br/>11",
        ),
        (
            "{{MZ|0|2|3|4|5|6|7|8|9|10|11}}",
            "[0] 2<br/>3<br/>4<br/>5<br/>6<br/>7<br/>8<br/>9<br/>10<br/>11",
        ),
        (
            "{{Plainlink|1=http://de.wikipedia.org/wiki/Ludwig_XIV.|2=Ludwig XIV.}}",
            "Ludwig XIV.",
        ),
        (
            "{{Plainlink|1=http://de.wikipedia.org/wiki/Ludwig_XIV.|Ludwig XIV.}}",
            "Ludwig XIV.",
        ),
        (
            "{{Plainlink|http://de.wikipedia.org/wiki/Ludwig_XIV.|2=Ludwig XIV.}}",
            "Ludwig XIV.",
        ),
        ("{{Ü|pl|dzień}}", "dzień"),
        ("{{übertr.}}", "<i>übertragen</i>"),
        ("{{übertr.|:}}", "<i>übertragen:</i>"),
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "de") == expected
