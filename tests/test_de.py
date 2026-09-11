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
            "Doppelkreuz (Zeichen)",
            [],
            [],
            {
                "Symbol": [
                    "<i>Mathematik&#58;</i> Zeichen zur Kennzeichnung der Mächtigkeit (Kardinalität) einer Menge"
                ],
                "Synonyme": [
                    '<svg width="2.973ex" height="2.843ex" style="vertical-align:-0.838ex" aria-labelledby="MathJax-SVG-1-Title" focusable="false" role="img" viewBox="0 -863.1 1279.9 1223.9" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs aria-hidden="true"><path id="E1-MJMAIN-7C" d="m139-249h-2q-12 0-18 14v486l1 486q10 13 19 13 13 0 20-15v-970q-8-14-18-14h-2z"/><path id="E1-MJMAIN-22C5" d="m78 250q0 24 17 42t43 18q24 0 42-16t19-43q0-25-17-43t-43-18-43 17-18 43z"/></defs><g transform="scale(1 -1)" fill="currentColor" stroke="currentColor" stroke-width="0" aria-hidden="true"><use xlink:href="#E1-MJMAIN-7C"/><use x="500" xlink:href="#E1-MJMAIN-22C5"/><use x="1001" xlink:href="#E1-MJMAIN-7C"/></g></svg>'
                ],
            },
            [],
            [],
        ),
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
            "Löss",
            ["[lœs]"],
            [],
            {
                "Substantiv|m.": [
                    "<i>Geologie&#58;</i> schluffiges Sedimentgestein, das aus der Zerstörung anderer Gesteine, deren Verwehung und Ablagerung entstanden ist"
                ]
            },
            [],
            ["Löß"],
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
            ["[ˈvɔli]", "[ˈvɔle]", "[ˈvɔlɛɪ̯]"],
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
