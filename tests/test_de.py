import re
from collections import OrderedDict
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
    "word, pronunciations, genders, etymology, definitions, variants, reverse_variants",
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
                ],
                "Synonyme": [
                    (
                        "At, At-Symbol, At-Zeichen, at sign, Ad-Zeichen, Ad, "
                        "Affenschwanz, Affenohr, Affenschaukel, Alef, Astat, "
                        "Klammeraffe"
                    )
                ],
            },
            [],
            [],
        ),
        (
            "CIA",
            ["[siːaɪ̯ˈɛɪ̯]"],
            ["mf"],
            ["Abkürzung von Central Intelligence Agency"],
            {"Abkürzung|mf.": ["US-amerikanischer Auslandsnachrichtendienst"]},
            [],
            [],
        ),
        (
            "Informationsverlusts",
            ["[ɪnfɔʁmaˈt͡si̯oːnsfɛɐ̯ˌlʊst͡s]"],
            [],
            [],
            {},
            ["Informationsverlust"],
            ["Informationsverlustes"],
        ),
        (
            "kartel",
            ["[ˈkaʁtl̩]"],
            [],
            [],
            {},
            ["karteln"],
            ["kartele", "kartle"],
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
            [],
        ),
        ("trage", ["[ˈtʁaːɡə]"], [], [], {}, ["tragen"], ["trag"]),
        ("daß", [], [], [], {}, ["dass"], []),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    genders: list[str],
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "de")

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    # `== CIA ({{Sprache|Deutsch}}) ==` → `== {{Sprache|Deutsch}} ==`
    code = re.sub(r"^==\s*.*\((\{\{Sprache\|[^}]+\}\})\)\s*==", r"== \1 ==", code, flags=re.MULTILINE)

    details = parse_word(word, code, "de", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
