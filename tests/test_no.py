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
        assert context.reset("no")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "aberrasjon",
            [],
            ["m"],
            [
                "Fra latin <i>aberrātiō</i>&nbsp;(«lindring, avvikelse») , fra <i>aberrō</i>&nbsp;(«gå unna/bort, gå vill»), fra <i>ab</i>&nbsp;(«bort») + <i>errō</i>&nbsp;(«vandre/gå»).",
                "Se aberrate.",
            ],
            {
                "Substantiv|m.": [
                    "avvik, avvikelse",
                    "(<i>astronomi</i>) avvik i en stjernes avbildede posisjon relativ til dens sanne posisjon.",
                    "(<i>optikk</i>) avbildningsfeil i linser og speil.",
                    "(<i>biologi</i>) endring i et kromosom mens celledeling pågår.",
                ]
            },
            [],
        ),
        (
            "-bar",
            [],
            [],
            ["Fra nedertysk, egentlig «bærende»"],
            {
                "Suffiks": [
                    "suffiks som lager adjektiv av substantiv (<i>fruktbar</i>), verb (<i>sammenlignbar</i>) og adjektiv (<i>åpenbar</i>)"
                ]
            },
            [],
        ),
        (
            "bak lås og slå",
            [],
            [],
            [],
            {"Frase": ["<i>(om straffedømt)</i> i fengsel"]},
            [],
        ),
        (
            "bare",
            [],
            [],
            [],
            {
                "Adverb": [
                    "begrensende, kun",
                    "Gir dempende effekt",
                    "Gir forsterkende effekt",
                    "Gir en sitatfunksjon, særlig i muntlig språk.",
                ]
            },
            ["bar"],
        ),
        (
            "én svale gjør ingen sommer",
            [],
            [],
            [],
            {"Ordtak": ["Det at noen har vært observert én gang betyr ikke at det er en regel eller et sikkert tegn"]},
            [],
        ),
        (
            "et",
            [],
            [],
            [],
            {"Artikkel": ["artikkel for substantiv i ubestemt entall, av intetkjønn"]},
            ["ete"],
        ),
        (
            "funnet",
            [],
            [],
            [],
            {},
            ["finne", "funn"],
        ),
        (
            "gjente",
            [],
            [],
            [],
            {"Subjektiv": ["jente"]},
            [],
        ),
        (
            "hand",
            [],
            [],
            [],
            {
                "Synonymer": [
                    "<i>(kropsdel)</i> neve",
                    "<i>(retningsangivelse)</i> side",
                    "<i>(spillkortterm)</i> kort på hånden",
                ],
                "Substantiv|f.": [
                    "(<i>anatomi</i>) kroppsdel ved enden av underarmen som gjør mennesker og aper i stand til å gripe",
                    "side",
                    "(<i>kortspill</i>) kortene en spiller sitter med",
                ],
            },
            [],
        ),
        (
            "Kiberg",
            [],
            [],
            [],
            {"Ordklasse": ["et tettsted i Vardø kommune i Finnmark"]},
            [],
        ),
        (
            "konsentrasjon",
            [],
            ["m"],
            ["Fra <i>konsentrere</i> + <i>-sjon</i>"],
            {
                "Substantiv|m.": [
                    "Det å konsentrere seg; ha stort fokus på noe.",
                    "(<i>kjemi</i>) Andelen stoff i noe; mengde stoff løst pr. enhet.",
                ]
            },
            [],
        ),
        (
            "krokodille",
            [],
            ["m"],
            [
                "Fra middelalderlatin <i>cocodrillus</i>&nbsp;(«krokodille»), fra gammelgresk κροκόδειλος&nbsp;(<i>krokodeilos</i>)"
            ],
            {"Substantiv|m.": ["stort reptil, lever i og nær vann. <i>(lat. Crocodylia)</i>"]},
            [],
        ),
        (
            "liksom",
            [],
            [],
            [],
            {
                "Subjunksjon": [
                    "Antyder at noe er på lek, at man later som noe.",
                    "Antyder en sammenligning, brukes ofte som et slags fyllord, særlig i muntlig språk.",
                ]
            },
            [],
        ),
        (
            "lumpen",
            [],
            [],
            [],
            {"Adjektiv": ["tarvelig, nedrig"]},
            ["lump"],
        ),
        (
            "NS",
            [],
            [],
            [],
            {"Initialord": ["<i>initialord for</i> partiet Nasjonal Samling", "<i>initialord for</i> Norsk Standard"]},
            [],
        ),
        (
            "rasshol",
            [],
            ["n"],
            [],
            {
                "Interjeksjon": ["<i>(brukt som skjellsord)</i> utropsord med samme betydning som substantivet"],
                "Substantiv|n.": ["anus; brukt som skjellsord"],
            },
            [],
        ),
        (
            "seg",
            [],
            [],
            ["Av norrønt <i>sik</i>."],
            {"Pronomen": ["refleksivt pronomen, tredje person entall og flertall"]},
            [],
        ),
        (
            "slå to fluer i en smekk",
            [],
            [],
            [],
            {"Idiom": ["(<i>idiomatisk</i>) få gjort to ting med én handling"]},
            [],
        ),
        (
            "sviger-",
            [],
            [],
            [],
            {"Prefiks": ["som befinner seg i inngiftet familie"]},
            [],
        ),
        (
            "tolvte",
            [],
            [],
            ["Fra norrønt <i>tolfti</i>; <i>tolv</i> + <i>-te</i>"],
            {"Tallord": ["ordenstallet til tolv"]},
            [],
        ),
        (
            "uten",
            [],
            [],
            [],
            {"Preposisjon": ["som ikke har;som mangler"]},
            [],
        ),
        (
            "verken",
            [],
            [],
            ["Fra gammeldansk: hwærki/hwærkin via dansk: hverken. Jamfør norrønt: hvárki."],
            {"Konjunksjon": ["danner sammen med eller en konjunksjon som binder sammen to nektinger"]},
            ["verk"],
        ),
        (
            "vg.",
            [],
            [],
            [],
            {"Forkortelse": ["forkortelse for <i>videregående</i>/<i>videregåande</i>"]},
            [],
        ),
        (
            "Øyvind",
            [],
            [],
            [],
            {"Egennavn": ["Norsk mannsnavn"]},
            [],
        ),
        (
            "ØNH",
            [],
            [],
            [],
            {"Forklaring": ["forkortelse for <i>øre-nese-hals</i>"]},
            [],
        ),
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
    code = page(word, "no")
    details = parse_word(word, code, "no", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
