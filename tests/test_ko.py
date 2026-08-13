from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "ko"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "한국어",
            ["[한<b>(ː)</b><b>구</b><b>거</b>]"],
            [],
            {
                "명사": [
                    "한국인이 쓰는 말. 한국어는 한반도와 제주도 그리고 만주 및 한국인이 이주하여 살고 있는 세계의 여러 지역에서 쓰이고 있다. 오늘날 비교언어학에서는 고립어로 분류하고 있다."
                ]
            },
            [],
            [],
        ),
        (
            "느리다",
            ["[느리다]"],
            [],
            {"형용사": ["무엇을 하는 데 시간이 많이 걸리다.", "(비유) 속도 또는 이해력이 더디다."]},
            [],
            [],
        ),
        ("느림", ["[느림]"], [], {"형용사 활용형": ["'느리다'의 명사형."]}, [], []),
        (
            "고사",
            ["[고사]"],
            [],
            {
                "명사": [
                    "동양화에서, 석간주(石間硃)라는 검붉은 흙에 먹을 섞어 만든 검붉은 색. 담채화, 수묵화, 진채화 따위에 쓴다.",
                    "옛날 역사.",
                    "오래된 절.",
                    "지나간 과거의 일.",
                    "오래된 낡은 사당(祠堂).",
                    "오래 묵은 나뭇등걸이나 그루터기.",
                    "머리를 조아려서 고마운 마음을 나타냄.",
                    "머리를 조아려서 죄를 빎.",
                    "의식(儀式) 때에 상급자가 글로 써서 읽어 축하하거나 훈시하는 말.",
                    "제의나 권유 따위를 굳이 사양함.",
                    "나쁜 기운은 없어지고 복은 오도록 집안에서 섬기는 신에게 올리는 제사.",
                ],
                "어근": ["'고사하다'의 어근."],
            },
            [],
            [],
        ),
        (
            "♁",
            [],
            [],
            {
                "기호": ["세계", "(천문학) 지구", "(연금) 안티몬"],
                "유의어": ["🜨"],
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
    definitions: list[Definitions],
    variants: list[str],
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
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
