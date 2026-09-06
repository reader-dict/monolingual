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
        assert context.reset("eo")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants, reverse_variants",
    [
        (
            "♍",
            [],
            [],
            [],
            {"Signifo": ["(<i>astrologio</i>) zodiaka signo de Virgulino (<i>Virgo</i>)"]},
            [],
            [],
        ),
        (
            "💀",
            [],
            [],
            [],
            {"Signifo": ["morto"]},
            [],
            [],
        ),
        (
            "alkazabo",
            [],
            [],
            ["el la andalus-araba <i>alqaṣába</i>, kaj tiu ĉi el la klasika araba <i>qaṣabah</i>, قصبة"],
            {
                "Signifo": [
                    "(<i>historio</i>; <i>arkitekturo</i>; <i>militado</i>) fortikita konstruaĵaro; citadelo aŭ palaco de araba ĉefo en Nord-Afriko kaj Suda-Hispanio"
                ]
            },
            [],
            ["alkazaboj", "alkazabojn", "alkazabon"],
        ),
        (
            "ekami",
            [],
            [],
            [],
            {"Signifo": ["(<i>transitiva</i>) komenci senti amon por iu aŭ eĉ io"]},
            [],
            [
                "ekamanta",
                "ekamante",
                "ekamanto",
                "ekamas",
                "ekamata",
                "ekamate",
                "ekamato",
                "ekaminta",
                "ekaminte",
                "ekaminto",
                "ekamis",
                "ekamita",
                "ekamite",
                "ekamito",
                "ekamonta",
                "ekamonte",
                "ekamonto",
                "ekamos",
                "ekamota",
                "ekamote",
                "ekamoto",
                "ekamu",
                "ekamus",
            ],
        ),
        (
            "ekamus",
            [],
            [],
            [],
            {},
            ["ekami"],
            [],
        ),
        (
            "kaskedo",
            ["kasked/o"],
            [],
            [],
            {
                "Signifo": [
                    "Ĉapo kun viziero, civilvesta aŭ uniforma: <i>homoj armitaj en nigraj kaskedetoj; la hotela pordisto levis sian kaskedon.</i>"
                ]
            },
            [],
            ["kaskedoj", "kaskedojn", "kaskedon"],
        ),
        (
            "komputilo",
            [],
            [],
            [],
            {
                "Signifo": [
                    "(<i>komputado</i>) maŝino aŭ elektronikaĵo kiu kapablas kalkuli, precipe sen intervenoj de homoj, aŭ rapide trakti, stori, kaj preni larĝajn kvantojn de datumo"
                ],
                "Sinonimoj": ["<i>(arkaikaj kaj evitendaj)</i> komputero, komputoro, komputatoro"],
            },
            [],
            ["komputiloj", "komputilojn", "komputilon"],
        ),
        (
            "latina",
            [],
            [],
            ["De Latino"],
            {"Adjektivo": ["rilata al Latino."]},
            [],
            [],
        ),
        (
            "luko",
            ["luk/o"],
            [],
            ["el la germana <i>Luke</i>"],
            {
                "Signifo": [
                    "ordinare vitrita aŭ kradita, en tegmento, plafono aŭ kelo, por enlasi lumon: <i>mansarda luko</i>.",
                    "fermebla per pordo aŭ tabuloj, en la ferdeko de ŝipo, por ebligi penetron en la holdon (pli precize: holdluko).",
                    "fermita per kovrilo el giso, kiu en la strato, sur trotuaro ks ebligas al metiisto malsupreniri en kloakon, aŭ subteran galerion.",
                ],
                "Sinonimoj": ["lumluko, bovokulo, vazistaso."],
            },
            [],
            ["lukoj", "lukojn", "lukon"],
        ),
        (
            "Teodoriko",
            [],
            ["m"],
            [],
            {},
            [],
            [],
        ),
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
    code = page(word, "eo")
    details = parse_word(word, code, "eo", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
