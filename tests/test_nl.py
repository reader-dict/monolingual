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
            "a",
            ["/a/"],
            [],
            {
                "Voorvoegsel": ["(natuurkunde) voorvoegsel voor atto-, 10<sup>−18</sup>"],
                "Symbool": [
                    "(wiskunde), (afkorting) symbool voor <i>are</i>, een oppervlaktemaat, gelijk aan 100 m², gelijk aan tien bij tien meter",
                    "(wiskunde), (afkorting) symbool voor <i>acre</i>, een Engelse oppervlaktemaat.",
                    "(tijdrekening), (eenheid), (geologie), (astronomie) het symbool voor annum.",
                    "(natuurkunde) het symbool voor versnelling.",
                    "(kristallografie) het symbool voor een glijspiegelvlak waarbij een spiegeling gevolgd wordt door een halve verschuiving in de richting van de a-as.",
                ],
                "Zelfstandig Naamwoord|m., v.": [
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
                "Synoniemen": ["Alfa <i>(NAVO-spellingsalfabet)</i>", "[4] la"],
            },
            [],
            ["a's", "a'tje", "a'tjes"],
        ),
        (
            "B",
            ["/be/"],
            ["verkorting van bachelor, binnen de Europese Unie gestandaardiseerd"],
            {
                "Symbool": [
                    "(scheikunde), (element) symbool voor het scheikundig element boor/borium met atoomnummer 5, een metalloïde",
                    "(informatica), (afkorting) het symbool voor byte, het kleinste adresseerbare gedeelte van een computergeheugen",
                    "(medisch) het symbool voor een bepaalde bloedgroep",
                    "(materiaalkunde) symbool voor de zachtheid van een potlood, in toenemende zachtheid: B, 2B, 3B, 4B, 5B, 6B, 7B, 8B en 9B",
                    "(muziek) symbool van het “B-majeurakkoord”",
                ],
                "Zelfstandig Naamwoord|m.": [
                    "(taalkunde) hoofdletter van de b, de tweede letter van het alfabet",
                    "(muziek), (afkorting) afkorting van “B-majeur”",
                    "als benaming binnen een reeks categorieën die met letters worden aangeduid",
                ],
                "Afkorting": ["bachelor <i>(academische titel)</i>"],
                "Synoniemen": ["Bravo <i>(NAVO-spellingsalfabet)</i>"],
            },
            [],
            ["B's", "B'tje", "B'tjes"],
        ),
        (
            "chatterbot",
            [],
            ["samenstelling&#32;van&#32;&#160;chat&#32;zn&#160;&#32;en&#32;&#160;robot&#32;zn&#160;"],
            {
                "Zelfstandig Naamwoord|m.": ["(internet) een geautomatiseerde gesprekspartner via het internet"],
                "Synoniemen": ["chatbot"],
            },
            [],
            ["chatterbotje", "chatterbotjes", "chatterbots"],
        ),
        (
            "cokes",
            ["/koks/"],
            [
                "[A]: alleen meervoud van Engels cokes, in de betekenis van ‘residu van steenkool’ voor het eerst aangetroffen in het jaar 1829",
                "[B]: &#160;coke&#32;zn&#160; met de uitgang <i>-s</i>",
            ],
            {
                "Zelfstandig Naamwoord|mv.": ["ontgaste steenkool"],
                "Opmerkingen": [
                    (
                        "Het woord is oorspronkelijk als meervoud ontleend, maar "
                        "doordat het als stofnaam wordt gebruikt, komt ook het "
                        "gebruik als enkelvoud voor, zonder verschil in betekenis."
                    )
                ],
            },
            [],
            [],
        ),
        (
            "dom",
            ["/dɔm/"],
            [
                "In de betekenis van ‘niet wijs’ voor het eerst aangetroffen in het jaar 901",
                "Leenwoord uit het Portugees, in de betekenis van ‘Portugese titel’ voor het eerst aangetroffen in het jaar 1574",
                "Leenwoord uit het Frans, in de betekenis van ‘kerk’ voor het eerst aangetroffen in het jaar 1574",
            ],
            {
                "Zelfstandig Naamwoord|m.": [
                    "(religie) kathedraal, de hoofdkerk van een bisdom",
                    "(bouwkunde) dak in de vorm van een halve bol",
                    "Portugese eretitel",
                    "(religie) titel van een benedictijner monnik",
                ],
                "Bijvoeglijk Naamwoord": [
                    "van weinig verstand getuigend",
                    "min of meer toevallig",
                    "routinematig, weinig geestelijke inspanning vereisend",
                ],
                "Synoniemen": ["(<i>hoofdkerk</i>)", ("kathedraal",), "(<i>boldak</i>)", ("koepel",)],
                "Opmerkingen": [
                    'In de betekenis van kathedraal is het alleen gangbaar voor het aanduiden van een bepaald kerkgebouw, bijvoorbeeld <i>"de dom van Utrecht"</i> of <i>"de Keulse dom"</i>, maar niet onbepaald (met het lidwoord <i>een</i>) of in het meervoud. Hiervoor kan beter (een vorm van) het woord "domkerk" worden gebruikt.'
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
            [],
            {
                "Zelfstandig Naamwoord|m., v.": [
                    "(demoniem) iemand afkomstig van de Konkan, het westelijk kustgebied van India",
                ],
                "Zelfstandig Naamwoord|mv.": [
                    "(demoniem) de oorspronkelijke bevolking van de Konkan",
                ],
                "Eigennaam|o.": [
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
                "Synoniemen": ["[2] Goa-Konkani", "[3] Maharashtra-Konkani"],
            },
            [],
            [],
        ),
        (
            "stint",
            ["/stɪnt/"],
            ['van de merknaam "Stint", gedeponeerd door het bedrijf <i>Stint Urban Mobility</i>'],
            {
                "Zelfstandig Naamwoord|m.": [
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
            {},
            ["stint"],
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
    # `{{=nld=}}` → `=={{nld}}==`
    code = re.sub(r"\{\{=(\w+)=\}\}", r"=={{\1}}==", code, flags=re.MULTILINE)

    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
