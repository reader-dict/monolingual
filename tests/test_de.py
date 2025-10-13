from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("de")


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
                    "<i>Sport&#58;</i> aus der Luft (angenommen und direkt kraftvoll abgespielt), ohne dass eine Bodenberührung des Sportgeräts vorher stattgefunden hat"
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
