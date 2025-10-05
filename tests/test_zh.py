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
        assert context.reset("zh")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "七講八講",
            [],
            [],
            [],
            {"動詞": ["<small>(漳泉話，吳語)</small> 亂講、胡說", "<small>(柳州官話)</small> 用各種方式解釋"]},
            [],
        ),
        (
            "稍後",
            [],
            [],
            [],
            {
                "副詞": ["在短暫的時間之後"],
                "動詞": ["<i>稍候</i>的拼寫錯誤。"],
            },
            [],
        ),
        (
            "佛教",
            [],
            [],
            [],
            {
                "專有名詞": [
                    "源自印度，奉釋迦牟尼為教主的宗教，以解脫生死、明心見性為教義，可以分為北傳佛教、南傳佛教以及禪宗、淨土宗、密宗等派別，信徒分布於東亞、南亞、東南亞，為世界三大宗教之一。"
                ],
            },
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
    code = page(word, "zh")
    details = parse_word(word, code, "zh", force=True)
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
