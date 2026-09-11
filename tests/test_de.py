import re
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = __name__.split("_", 1)[1]


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "@",
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
            ["Abkürzung von Central Intelligence Agency"],
            {"Abkürzung|f./m.": ["US-amerikanischer Auslandsnachrichtendienst"]},
            [],
            [],
        ),
        ("daß", [], [], {}, ["dass"], []),
        (
            "Informationsverlusts",
            ["[ɪnfɔʁmaˈt͡si̯oːnsfɛɐ̯ˌlʊst͡s]"],
            [],
            {},
            ["Informationsverlust"],
            ["Informationsverlustes"],
        ),
        (
            "kartel",
            ["[ˈkaʁtl̩]"],
            [],
            {},
            ["karteln"],
            ["kartele", "kartle"],
        ),
        (
            "Sinn",
            ["[zɪn]"],
            [
                "mittel- und althochdeutsch <i>sin,</i> weitere Herkunft nicht sicher; möglicherweise zur Gruppe von indogermanisch <i>*sent-,</i> „gehen, reisen, fahren“, zu der unter anderem althochdeutsch <i>sinnan,</i> „reisen, streben, trachten“ und lateinisch <i>sentire,</i> „empfinden, wahrnehmen“ zählen, vergleiche auch <i>senden, Gesinde</i>"
            ],
            {
                "Substantiv|f./m./n.": [
                    "<i>Biologie&#58;</i> bestimmte physiologische Fähigkeit zur Wahrnehmung von etwas",
                    "<i>kein Plural&#58;</i> innere Beziehung, Verständnis einer Person für eine Sache",
                    "<i>kein Plural&#58;</i> Zustand, Ausrichtung der Gedanken einer Person",
                    "<i>kein Plural&#58;</i> die Bedeutungen und Vorstellungen, die sich mit einem sprachlichen Ausdruck verbinden",
                    "<i>kein Plural&#58;</i> gedanklicher Hintergrund, Zweck einer Handlung oder Sache",
                ],
                "Synonyme|f./m./n.": [
                    "<i>Linguistik:</i> Intension",
                    "deutscher Familienname",
                    "<i>Geografie&#58;</i> Fluss in Deutschland",
                    "Stadt in Hessen, Gemeinde im Lahn-Dill-Kreis, gelegen am Fluss Sinn",
                ],
            },
            [],
            [],
        ),
        ("trage", ["[ˈtʁaːɡə]"], [], {}, ["tragen"], ["trag"]),
        (
            "volley",
            ["[ˈvɔle]", "[ˈvɔli]", "[ˈvɔlɛɪ̯]"],
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
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, LANG)

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    # `== CIA ({{Sprache|Deutsch}}) ==` → `== {{Sprache|Deutsch}} ==`
    code = re.sub(r"^==\s*.*\((\{\{Sprache\|[^}]+\}\})\)\s*==", r"== \1 ==", code, flags=re.MULTILINE)

    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
