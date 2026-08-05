from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "jbo"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, reverse_variants",
    [
        (
            "forca",
            ["/ˈfor.ʃa/"],
            [],
            {
                "gismu": [
                    "<small>ko'a</small> tutci <small>ko'e</small> noi ka ralte ja lafti ku'o gi'e se pagbu lo grana noi se jimca lo su'o re kinli"
                ]
            },
            ["for"],
        ),
        (
            "grizgi",
            [],
            [],
            {"lujvo": ["ko'a du girzu1.e zgike1.i ko'e du zgike2"]},
            [],
        ),
        (
            "kacmyxra",
            [],
            ["kacma + pixra"],
            {"lujvo": ["ko'a pixra ko'e lo kacma poi selsazri ko'i ku'o ko'o"]},
            [],
        ),
        (
            "mun",
            [],
            [],
            {"rafsi": ["<i>lo rafsi po zo smuni</i>"]},
            [],
        ),
        (
            "smuni",
            [],
            [],
            {"gismu": ["ko'i pe'a fanva ko'e lo ko'i menli bangu lo ka zasti ku ko'a"]},
            ["mun", "smu"],
        ),
        (
            "♁",
            [],
            [],
            {"snile'u": ["(kesyske) plini cu du le.terdi.", "(xumjetske) antimoni"]},
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert reverse_variants == details.reverse_variants
