import re
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
        assert context.reset("nl")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants, reverse_variants",
    [
        (
            "a",
            ["/a/"],
            ["m", "v"],
            [],
            {
                "Synoniemen": ["Alfa <i>(NAVO-spellingsalfabet)</i>", "[4] la"],
                "Voorvoegsel": ["(natuurkunde) voorvoegsel voor atto-, 10<sup>−18</sup>"],
                "Symbool": [
                    "(wiskunde), (afkorting) symbool voor <i>are</i>, een oppervlaktemaat, gelijk aan 100 m², gelijk aan tien bij tien meter",
                    "(wiskunde), (afkorting) symbool voor <i>acre</i>, een Engelse oppervlaktemaat.",
                    "(tijdrekening), (eenheid), (geologie), (astronomie) het symbool voor annum.",
                    "(natuurkunde) het symbool voor versnelling.",
                    "(kristallografie) het symbool voor een glijspiegelvlak waarbij een spiegeling gevolgd wordt door een halve verschuiving in de richting van de a-as.",
                ],
                "Zelfstandig Naamwoord": [
                    "(taalkunde) de eerste letter van het alfabet",
                    "het op de eerste plaats genoemde",
                    "(muziek) de standaardmuziektoon van 440 Hz",
                    "(muziek) de tiende toon van de chromatische, en de zesde toon van de diatonische toonladder",
                    "(muziek), (afkorting) afkorting van “a-mineur”",
                    "het eerste element van een opsomming",
                ],
                "Spreekwoorden": [
                    "Wie a zegt moet ook b zeggen.",
                    (
                        "<i>Als je aan iets bent begonnen moet je het ook afmaken</i>",
                        "<i>Stoppen is onverantwoordelijk</i>",
                    ),
                ],
                "Uitdrukkingen En Gezegden": ["van A tot Z", ("<i>Van het begin tot het einde.</i>",)],
            },
            [],
            ["a's", "a'tje", "a'tjes"],
        ),
        (
            "B",
            ["/be/"],
            ["m"],
            ["verkorting van bachelor, binnen de Europese Unie gestandaardiseerd"],
            {
                "Synoniemen": ["Bravo <i>(NAVO-spellingsalfabet)</i>"],
                "Symbool": [
                    "(scheikunde), (element) symbool voor het scheikundig element boor/borium met atoomnummer 5, een metalloïde",
                    "(informatica), (afkorting) het symbool voor byte, het kleinste adresseerbare gedeelte van een computergeheugen",
                    "(medisch) het symbool voor een bepaalde bloedgroep",
                    "(materiaalkunde) symbool voor de zachtheid van een potlood, in toenemende zachtheid: B, 2B, 3B, 4B, 5B, 6B, 7B, 8B en 9B",
                    "(muziek) symbool van het “B-majeurakkoord”",
                ],
                "Zelfstandig Naamwoord": [
                    "(taalkunde) hoofdletter van de b, de tweede letter van het alfabet",
                    "(muziek), (afkorting) afkorting van “B-majeur”",
                    "als benaming binnen een reeks categorieën die met letters worden aangeduid",
                ],
                "Afkorting": ["bachelor <i>(academische titel)</i>"],
            },
            [],
            ["B's", "B'tje", "B'tjes"],
        ),
        (
            "chatterbot",
            [],
            ["m"],
            ["samenstelling&#32;van&#32;&#160;chat&#32;zn&#160;&#32;en&#32;&#160;robot&#32;zn&#160;"],
            {
                "Zelfstandig Naamwoord": ["(internet) een geautomatiseerde gesprekspartner via het internet"],
                "Synoniemen": ["chatbot"],
            },
            [],
            ["chatterbotje", "chatterbotjes", "chatterbots"],
        ),
        (
            "cokes",
            ["/koks/"],
            ["mv"],
            [
                "[A]: alleen meervoud van Engels cokes, in de betekenis van ‘residu van steenkool’ voor het eerst aangetroffen in het jaar 1829",
                "[B]: &#160;coke&#32;zn&#160; met de uitgang <i>-s</i>",
            ],
            {
                "Opmerkingen": [
                    (
                        "Het woord is oorspronkelijk als meervoud ontleend, maar "
                        "doordat het als stofnaam wordt gebruikt, komt ook het "
                        "gebruik als enkelvoud voor, zonder verschil in betekenis."
                    )
                ],
                "Zelfstandig Naamwoord": ["ontgaste steenkool"],
            },
            [],
            [],
        ),
        (
            "dom",
            ["/dɔm/"],
            ["m"],
            [
                "In de betekenis van ‘niet wijs’ voor het eerst aangetroffen in het jaar 901",
                "Leenwoord uit het Portugees, in de betekenis van ‘Portugese titel’ voor het eerst aangetroffen in het jaar 1574",
                "Leenwoord uit het Frans, in de betekenis van ‘kerk’ voor het eerst aangetroffen in het jaar 1574",
            ],
            {
                "Zelfstandig Naamwoord": [
                    "(religie) kathedraal, de hoofdkerk van een bisdom",
                    "(bouwkunde) dak in de vorm van een halve bol",
                    "Portugese eretitel",
                    "(religie) titel van een benedictijner monnik",
                ],
                "Opmerkingen": [
                    'In de betekenis van kathedraal is het alleen gangbaar voor het aanduiden van een bepaald kerkgebouw, bijvoorbeeld <i>"de dom van Utrecht"</i> of <i>"de Keulse dom"</i>, maar niet onbepaald (met het lidwoord <i>een</i>) of in het meervoud. Hiervoor kan beter (een vorm van) het woord "domkerk" worden gebruikt.'
                ],
                "Synoniemen": ["(<i>hoofdkerk</i>)", ("kathedraal",), "(<i>boldak</i>)", ("koepel",)],
                "Bijvoeglijk Naamwoord": [
                    "van weinig verstand getuigend",
                    "min of meer toevallig",
                    "routinematig, weinig geestelijke inspanning vereisend",
                ],
            },
            [],
            [
                "domkerken",
                "domme",
                "dommen",
                "dommer",
                "dommere",
                "dommers",
                "dommetje",
                "dommetjes",
                "doms",
                "domst",
                "domste",
            ],
        ),
        (
            "Konkani",
            ["/kɔŋˈkani/"],
            ["m", "v"],
            [],
            {
                "Zelfstandig Naamwoord": [
                    "(demoniem) iemand afkomstig van de Konkan, het westelijk kustgebied van India",
                    "(demoniem) de oorspronkelijke bevolking van de Konkan",
                ],
                "Synoniemen": ["[2] Goa-Konkani", "[3] Maharashtra-Konkani"],
                "Eigennaam": [
                    (
                        "geen meervoud (taal) , <i>(algemeen)</i> Indische taal "
                        "gesproken door 6 miljoen mensen in de Konkan <i>(omvat de "
                        "beide volgende talen)</i>"
                    ),
                    "(taal), <i>(specifiek)</i> officiële taal van de deelstaat Goa in India",
                    (
                        "(taal), <i>(specifiek)</i> taal met verschillende dialecten in "
                        "de deelstaat Maharashtra in India, die samen een overgang "
                        "tussen Marathi en het Goa-Konkani vormen"
                    ),
                ],
            },
            [],
            [],
        ),
        (
            "stint",
            ["/stɪnt/"],
            ["m"],
            ['van de merknaam "Stint", gedeponeerd door het bedrijf <i>Stint Urban Mobility</i>'],
            {
                "Zelfstandig Naamwoord": [
                    (
                        "(verkeer) elektrisch aangedreven karretje met een rechtop staande "
                        "bestuurder en een bak waarin tot 10 jonge kinderen vervoerd kunnen "
                        "worden"
                    )
                ],
                "Synoniemen": ["bso-bus"],
            },
            [],
            ["stints"],
        ),
        (
            "stints",
            ["/stɪnts/"],
            [],
            [],
            {},
            ["stint"],
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
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "nl")

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    # `{{=nld=}}` → `=={{nld}}==`
    code = re.sub(r"\{\{=(\w+)=\}\}", r"=={{\1}}==", code, flags=re.MULTILINE)

    details = parse_word(word, code, "nl", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
