from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants",
    [
        ("auto", [], [], {"Substantiv": ["automatiskt läge", "autostart"]}, []),
        (
            "en",
            ["/en/", "/eːn/", "/ɛn/"],
            [
                "Av fornsvenska <i>ēn</i>, av fornnordiska <i>einn</i>, av urgermanska <i>*ainaz</i>, av urindoeuropeiska <i>*ójnos</i>",
                "Av fornsvenska <i>ēn</i>, av fornnordiska <i>*æiniʀ</i>, av urgermanska <i>*jainjaz</i>",
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
        ),
        ("dufvor", [], [], {}, ["dufva"]),
        ("harmonierar", [], [], {}, ["harmoniera"]),
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
                    "<i>suffix i ord som har med djurs horn att göra</i>",
                ]
            },
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
                "Förkortning": ["<i>förkortning för</i> minut", "<i>förkortning för</i> minimum"],
                "Pronomen": [
                    "possessivt pronomen som indikerar ägande av eller tillhörighet till den talande (jag) om det ägda eller tillhörande är i ental och har n-genus; possessivt pronomen i första person singular med huvudordet i singular utrum",
                    "ovanstående i självständig form",
                    "reflexivt possessivt pronomen som syftar tillbaka på och indikerar ägande av eller tillhörighet till subjektet om subjektet är i första person singular (jag) och om det ägda eller tillhörande är i ental och har n-genus; reflexivt possessivt pronomen i första person singular med huvudordet i singular utrum",
                ],
                "Substantiv": ["känslouttryck i ansiktet"],
            },
            [],
        ),
        ("og", [], [], {}, []),
        (
            "sand",
            ["/sand/"],
            [
                'Av fornsvenska <i>sander</i>, av fornnordiska <i>sandr</i>, av urgermanska <i>*sanda(z)</i>. Besläktat med isländska <i>sandur</i>, norska <i>sand</i> fornengelska <i>sand</i> (engelska <i>sand</i>), fornhögtyska <i>sant</i> (tyska <i>Sand</i>). Ytterst av urindoeuropeiska <i>*sam(a)dho-</i>, motsvarande grekiska ἄμαθος, <i>amathos</i>, "sand"; troligen en uttalsförenkling av <i>*bhsam(a)dho-</i>, av roten <i>*bhes-</i>, med rotbetydelsen "att krossa", "att gnugga". Härigenom besläktat med latin <i>sabulum</i>, grekiska ψάμμος, <i>psammos</i> (varav <i>psammit</i>), båda "sand", och sanskrit <i>bhas</i>, "sönderkrossa".',
            ],
            {
                "Substantiv": [
                    "sten som blivit till små korn, antingen genom väder och vind eller på konstgjord väg",
                    "<i>(geologi)</i> jordart med kornstorlek mellan 0,06 och 2 mm",
                ]
            },
            [],
        ),
        (
            "svenska",
            [],
            [
                "Belagt sedan 1300-talet, som fornsvenska <i>svænska</i>.",
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
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "sv")
    details = parse_word(word, code, "sv", force=True)
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{led|sv|f|gata}}", "<i>förled tillhörigt ordet</i> gata"),
        ("{{led|sv|e|hand}}", "<i>efterled tillhörigt ordet</i> hand"),
        ("{{ö|en|test}}", "test"),
        ("{{ö+|en|test}}", "test <sup>(en)</sup>"),
        ("{{ö-inte|en|test}}", "<b>inte</b> <i><s>test</s></i>"),
        ("{{övrigatecken|punkt|.}}", '"<code>.</code>"'),
        ('{{övrigatecken|quote|"}}', '"<code>"</code>"'),
        ("{{övrigatecken|special1|<}}", '"<code>&lt;</code>"'),
        ("{{övrigatecken|special2|>}}", '"<code>&gt;</code>"'),
        ("{{övrigatecken|special3|&}}", '"<code>&amp;</code>"'),
        ("{{tagg|historia}}", "<i>(historia)</i>"),
        (
            "{{tagg|kat=nedsättande|text=något nedsättande}}",
            "<i>(något nedsättande)</i>",
        ),
        ("{{uttal|sv|ipa=mɪn}}", "<b>uttal:</b> /mɪn/"),
        ("{{uttal|sv|ipa=eːn/, /ɛn/, /en}}", "<b>uttal:</b> /eːn/, /ɛn/, /en/"),
    ],
)
def test_process_template(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "sv") == expected
