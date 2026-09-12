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
        ("Kilo", ["/ˈkilo/"], [], {"Anarana Iombonana": ["faneva famantarana ho an'ny litera K"]}, [], []),
        (
            "nasian-tenimiafina",
            ["/nasintenimiafinạ/"],
            ["fampikambanana ny matoanteny <i>nasiana</i> ary <i>tenimiafina</i>"],
            {
                "Mpamaritra": [
                    'Zavatra izay nasiana tenimiafina mba tsy hahafahan\'ny rehetra mamangy. Azo soratana koa hoe <i>"nasiana tenimiafina"</i>'
                ]
            },
            [],
            [],
        ),
        (
            "Trombiculidae",
            [],
            [],
            {
                "Anarana": [
                    "fianakaviana lehibe misy ny tsimokaretina izay fantatra amin'ny hoe tsimokaretina ny dingana misy ny gidro"
                ]
            },
            [],
            [],
        ),
        (
            "tsitondroina",
            [],
            [],
            {
                "Anarana Iombonana": [
                    "Anarana nomena ny vatolampy sasany izay tsy sahy notondroina noho ny hatahorana fa misy lolo na angatra.",
                    "Fanafody na zavatra apetraky ny mpampiady ombalahy amin'ny ombiny mba hampatanjaka azy.",
                ]
            },
            [],
            [],
        ),
        ("tsitondroitsika", ["/t͡situnɖ͡ʐuit͡sikʲạ/"], [], {}, ["tsitondroina"], []),
        (
            "voavily",
            [],
            [],
            {
                "Bika Matoanteny": [
                    "Izy io dia endriky ny matoanteny avy amin'ny fototeny 'vily', manondro zavatra natao na nisy fiovam-poana miverimberina."
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
    print(f"{word = }")
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
