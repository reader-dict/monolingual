from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants",
    [
        (
            "▶",
            [],
            [],
            {"Symbol": ["knap som bruges til at afspille en video, lyd el. musik"]},
            [],
        ),
        (
            "bakterie",
            [],
            [
                "fra latin <i>bacterium</i>, latinisering af græsk <i>bakterion</i> (βακτήριον\xa0- lille stav), diminutiv af <i>baktron</i> (βάκτρον - stav)"
            ],
            {"Substantiv": ["(mikrobiologi) en encellet mikroskopisk organisme uden cellekerne"]},
            [],
        ),
        (
            "disse",
            [],
            [],
            {"Substantiv": ["ikke noget"]},
            ["denne"],
        ),
        (
            "et",
            [],
            [],
            {"Artikel": ["intetkøn af en"]},
            [],
        ),
        (
            "her",
            ["/hɛːˀɒ̯/"],
            [],
            {
                "Adverbium": [
                    "Stedet hvor vi er nu. Vores placering.",
                    "(<i>radiokommunikation, radiotelefoni</i>) Dette opkalder stammer fra denne opkalder",
                ],
                "Formelt Subjekt": [
                    "bruges som upersonligt subjekt, refererer ofte fremad eller tilbage til et andet led i sætningen."
                ],
            },
            [],
        ),
        (
            "hund",
            ["[ˈhunə-]", "[ˈhunˀ]"],
            [
                "Menes at stamme fra indoeuropæisk sprog <i>ḱʷn̥tós</i>, fra <i>ḱwṓ</i> og derfra videre til germansk sprog <i>*hundaz</i> og fra oldnordisk hundr."
            ],
            {
                "Substantiv": [
                    "(<i>zoologi</i>): et pattedyr af underarten <i>Canis lupus familiaris</i>.",
                    "(<i>slang</i>): 100 DKK-seddel (bruges ikke i flertal)",
                ]
            },
            [],
        ),
        (
            "godt nytår",
            [],
            [],
            {"Sætning": ["En hilsen der siges omkring den 1. januar."]},
            [],
        ),
        ("jørme", [], [], {"Verbum": ["vrimle, myldre; sværme"]}, []),
        (
            "mus",
            [],
            [
                "Fra oldnordisk mús.",
                "Fra engelsk mouse.",
            ],
            {"Substantiv": ["(<i>zoologi</i>) pattedyr", "(<i>data</i>) en enhed som tilsluttes computere"]},
            [],
        ),
        (
            "-ør",
            [],
            ["Fra fransk: -eur, af latin -ator."],
            {"Endelse": ["Betegner den, der udfører et arbejde."]},
            [],
        ),
        ("skulle", [], [], {"Verbum": ["Er nødt til at gøre. Forpligtet til at gøre."]}, []),
        (
            "søm",
            [],
            ["Fra oldnordisk saumr, fra sýja (<i>at sy</i>).", "Fra oldnordisk saumr <i>hankøn</i>."],
            {
                "Substantiv": [
                    "sammensyning",
                    "spids metalpind med et hoved, beregnet til at sammenføje træstykker til hinanden",
                ]
            },
            [],
        ),
        (
            "til",
            [],
            [
                'Indoeuropæisk: *ad (i betydningen: fastsætte, ordne) -> germansk *tila- (i betydningen: mål; jf. tysk: Ziel) -> oldnordisk til. Ordet betyder altså egentlig: "<i>med</i> xxx <i>som mål</i>", hvor xxx kan erstattes af et substantiv (navneord).'
            ],
            {"Præposition": ["Ordet betegner en retning hen imod eller et tilhørsforhold"]},
            [],
        ),
        (
            "tolvte",
            ["/ˈtɔldə/"],
            ["Fra oldnordisk tolfti."],
            {"Ordenstal": ["nummer tolv i rækken"]},
            [],
        ),
        (
            "tyv",
            [],
            [],
            {
                "Substantiv": ["En person, der uretmæssigt tager andre folks ejendele i besiddelse."],
                "Udtryk": [
                    "(når noget bliver gjort uden at nogen får det at vide før det er for sent): Som en <b>tyv</b> om natten."
                ],
            },
            [],
        ),
        ("PMV", [], [], {"Substantiv": ["<i>(militær)</i> <i>Forkortelse af</i> <b>pansret mandskabsvogn</b>"]}, []),
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
    code = page(word, "da")
    details = parse_word(word, code, "da", force=True)
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{fysik}}", "(<i>fysik</i>)"),
        ("{{label|militær|våben}}", "(<i>militær</i>, <i>våben</i>)"),
        ("{{l|da|USA}}", "USA"),
        ("{{l|da|USA|America}}", "USA"),
        ("{{trad|en|limnology}}", "limnology<sup>(en)</sup>"),
        ("{{URchar|الكحل}}", "الكحل"),
        ("{{ZHchar|北京}}", "北京"),
    ],
)
def test_process_template(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "da") == expected
