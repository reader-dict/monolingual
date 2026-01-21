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
                "Substantiv": [
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
            {"Frase": ["<i>(om straffedømt)</i> i fengsel", ("<i>Den mistenkte ble satt bak <b>lås og slå</b>.</i>",)]},
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
                    ("<i>Det er <b>bare</b> lov å spise brunost</i>",),
                    "Gir dempende effekt",
                    ("<i>Jeg skal <b>bare</b> på do</i>",),
                    "Gir forsterkende effekt",
                    ("<i>Han er <b>bare</b> så kul!</i>",),
                    "Gir en sitatfunksjon, særlig i muntlig språk.",
                    ("<i>Hun <b>bare</b>: GI meg katten min!</i>",),
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
                "Substantiv": [
                    "(<i>anatomi</i>) kroppsdel ved enden av underarmen som gjør mennesker og aper i stand til å gripe",
                    "side",
                    ("<i>Butikken ligger på høyre <b>hånd</b>.</i>",),
                    "(<i>kortspill</i>) kortene en spiller sitter med",
                    ("<i>Det var lenge siden jeg hadde hatt en så god <b>hånd</b>.</i>",),
                ]
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
                "Substantiv": [
                    "Det å konsentrere seg; ha stort fokus på noe.",
                    ("<i><b>Konsentrasjon</b> er viktig for å ikke bli avledet.</i>",),
                    "(<i>kjemi</i>) Andelen stoff i noe; mengde stoff løst pr. enhet.",
                    ("<i><b>Konsentrasjonen</b> i løsningen er på 0,1 molar.</i>",),
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
            {"Substantiv": ["stort reptil, lever i og nær vann. <i>(lat. Crocodylia)</i>"]},
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
                    ("<i>Vi fant på masse liksom-ord, og lagde vårt eget språk.</i>",),
                    "Antyder en sammenligning, brukes ofte som et slags fyllord, særlig i muntlig språk.",
                    ("<i>Det var liksom veldig ordentlig.</i>", "<i>Bark er liksom huden til trærne.</i>"),
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
                "Substantiv": ["anus; brukt som skjellsord"],
            },
            [],
        ),
        (
            "seg",
            [],
            [],
            ["Av norrønt <i>sik</i>."],
            {
                "Pronomen": [
                    "refleksivt pronomen, tredje person entall og flertall",
                    ("Han skyndte <b>seg</b> til bussen.", "De bestemte <b>seg</b> for å vente."),
                ]
            },
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
            {
                "Konjunksjon": [
                    "danner sammen med eller en konjunksjon som binder sammen to nektinger",
                    ("<i>Han fikk verken vått <b>eller</b> tørt.</i>", "<i>Jeg har verken tid <b>eller</b> råd.</i>"),
                ]
            },
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
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
