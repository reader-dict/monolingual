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
        assert context.reset("sv")


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "abnorm",
            [],
            [],
            {
                "Adjektiv": [
                    "onormal, mycket långt ifrån att vara normal, onaturlig, felaktig",
                    (
                        '<dd class="semantic-relation template-synonymer">Synonymer: avvikande, grotesk, onaturlig, onormal, rubbad, sjuklig, underlig, missbildad</dd>',
                    ),
                ]
            },
            [],
            ["abnorma", "abnormare", "abnormast", "abnormaste", "abnorme", "abnormt"],
        ),
        (
            "abrupt",
            [],
            [],
            {
                "Adjektiv": [
                    "<i>(ålderdomligt)</i> avbruten, osammanhängande",
                    "plötslig, oväntad",
                    (
                        '<dd class="semantic-relation template-synonymer">Synonymer: hastig, oväntad, plötslig, tvär</dd>',
                    ),
                ],
                "Adverb": ["<i>(ålderdomligt)</i> avbrutet, osammanhängande"],
            },
            [],
            ["abrupta", "abruptare", "abruptast", "abruptaste", "abrupte"],
        ),
        ("auto", [], [], {"Substantiv": ["automatiskt läge", "autostart"]}, [], []),
        (
            "en",
            ["/en/", "/eːn/", "/ɛn/"],
            [
                "Av fornsvenska&nbsp;<i>ēn</i>, av fornnordiska&nbsp;<i>einn</i>, av urgermanska&nbsp;<i>*ainaz</i>, av urindoeuropeiska&nbsp;<i>*ójnos</i>",
                "Av fornsvenska&nbsp;<i>ēn</i>, av fornnordiska&nbsp;<i>*æiniʀ</i>, av urgermanska&nbsp;<i>*jainjaz</i>",
            ],
            {
                "Adverb": ["ungefär; omkring"],
                "Artikel": ["obestämd artikel singular utrum"],
                "Pronomen": [
                    "objektsform av <i>man</i>",
                    "<i>(vardagligt, dialektalt)</i> man",
                    "<i>(dialektalt)</i> honom, 'an",
                    "syftar tillbaka på det tidigare nämnda substantivet",
                ],
                "Substantiv": [
                    "<i>(träd)</i> en vintergrön barrväxt, en buske eller ett träd med tätt grenverk och vassa barr, av arten <i>Juniperus communis</i> inom släktet enar (<i>Juniperus</i>) och familjen cypressväxter (Cupressaceae)"
                ],
            },
            [],
            ["enar", "enarna", "enarnas", "enars", "enen", "enens", "ens"],
        ),
        ("dufvor", [], [], {}, ["dufva"], []),
        ("harmonierar", [], [], {}, ["harmoniera"], []),
        (
            "-hörning",
            [],
            [
                "Av <i>hörn</i> + <i>-ing</i>.",
                "Av <i>horn</i> + <i>-ing</i> med omljud.",
            ],
            {
                "Efterled": [
                    "<i>(geometri, vardagligt)</i> <i>suffix för månghörningar</i>",
                    ('<dd class="semantic-relation template-synonymer">Synonymer: -gon</dd>',),
                    "<i>suffix i ord som har med djurs horn att göra</i>",
                ]
            },
            [],
            [],
        ),
        (
            "min",
            ["/miːn/", "/mɪn/"],
            [
                'Fornnordiska <i>mínn</i>, av urgermanska <i>*mīnaz</i> (varav även engelska <i>mine</i>, tyska <i>mein</i>, etc.), av urindoeuropeiska <i>*meino-</i>, från <i>*mei</i> (lokativ av <i>*me-</i>, "mig") och <i>*-no</i>- (adjektivsuffix).',
                'I svenskan sedan 1631, från franska <i>mine</i> (varav även tyska <i>Miene</i>, engelska <i>mien</i>), av bretonskans <i>min</i>, "mun", "näbb", "nos"',
            ],
            {
                "Pronomen": [
                    "possessivt pronomen som indikerar ägande av eller tillhörighet till den talande (jag) om det ägda eller tillhörande är i ental och har n-genus; possessivt pronomen i första person singular med huvudordet i singular utrum",
                    "ovanstående i självständig form",
                    "reflexivt possessivt pronomen som syftar tillbaka på och indikerar ägande av eller tillhörighet till subjektet om subjektet är i första person singular (jag) och om det ägda eller tillhörande är i ental och har n-genus; reflexivt possessivt pronomen i första person singular med huvudordet i singular utrum",
                ],
                "Substantiv": ["känslouttryck i ansiktet"],
                "Förkortning": ["<i>förkortning för</i> minut", "<i>förkortning för</i> minimum"],
            },
            [],
            ["minen", "minens", "miner", "minerna", "minernas", "miners", "mins"],
        ),
        (
            "sand",
            ["/sand/"],
            [
                'Belagt i språket sedan 1300-talet. Av fornsvenska&nbsp;<i>sander</i>, av fornnordiska&nbsp;<i>sandr</i>, av urgermanska&nbsp;<i>*sanda(z)</i>. Besläktat med isländska <i>sandur</i>, norska <i>sand</i> fornengelska <i>sand</i> (engelska <i>sand</i>), fornhögtyska <i>sant</i> (tyska <i>Sand</i>). Ytterst av urindoeuropeiska <i>*sam(a)dho-</i>, motsvarande grekiska ἄμαθος, <i>amathos</i>, "sand"; troligen en uttalsförenkling av <i>*bhsam(a)dho-</i>, av roten <i>*bhes-</i>, med rotbetydelsen "att krossa", "att gnugga". Härigenom besläktat med latin <i>sabulum</i>, grekiska ψάμμος, <i>psammos</i> (varav <i>psammit</i>), båda "sand", och sanskrit <i>bhas</i>, "sönderkrossa".',
            ],
            {
                "Substantiv": [
                    "sten som blivit till små korn, antingen genom väder och vind eller på konstgjord väg",
                    "<i>(geologi)</i> jordart med kornstorlek mellan 0,06 och 2 mm",
                ]
            },
            [],
            ["sanden", "sandens", "sands"],
        ),
        (
            "svenska",
            [],
            [
                "Belagt sedan 1300-talet, som fornsvenska&nbsp;<i>svænska</i>.",
                "Belagt sedan 1773.",
            ],
            {
                "Substantiv": [
                    "nordiskt språk som talas i Sverige och Finland (officiellt i båda länderna)",
                    "svensk kvinna",
                ],
                "Verb": ["<i>(mindre brukligt)</i> tala svenska"],
            },
            ["svensk"],
            [
                "svenskade",
                "svenskades",
                "svenskan",
                "svenskande",
                "svenskandes",
                "svenskans",
                "svenskar",
                "svenskas",
                "svenskat",
                "svenskats",
                "svenskor",
                "svenskorna",
                "svenskornas",
                "svenskors",
            ],
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
    code = page(word, "sv")
    details = parse_word(word, code, "sv", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
