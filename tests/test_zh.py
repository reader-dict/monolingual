from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "七講八講",
            [],
            [],
            [],
            {"動詞": ["(漳泉話，吳語) 亂講、胡說", "(柳州官話) 用各種方式解釋"]},
            [],
        ),
        (
            "稍後",
            [],
            [],
            [],
            {
                "副詞": ["在短暫的時間之後"],
                "動詞": ["稍候的拼寫錯誤。"],
                "讀音": ["官話: shāohòu<br/>粵語: saau<sup>2</sup> hau<sup>6</sup>"],
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
                "讀音": ["官話: Fójiào<br/>粵語: fat<sup>6</sup> gaau<sup>3</sup>"],
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


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{abbreviation of|zh|留名}}", "留名之縮寫。"),
        ("{{cmn-pinyin of|塔吉克}}", '<span style="font-size:larger">塔吉克</span>的漢語拼音讀法'),
        ("{{defdate|from 15th c.}}", "<small>（from 15th c.）</small>"),
        ("{{gloss|對患者}}", "（對患者）"),
        ("{{gl|對患者}}", "（對患者）"),
        ("{{IPA|zh|/tʷãɔ̃⁵⁴⁵⁴/}}", "/tʷãɔ̃⁵⁴⁵⁴/"),
        ("{{IPAchar|[kiŋ²¹ naŋ⁵⁵ nˡiʔ⁵]}}", "[kiŋ²¹ naŋ⁵⁵ nˡiʔ⁵]"),
        ("{{IPAfont|/kʰɑlpin/}}", "/kʰɑlpin/"),
        ("{{lang|zh|中華}}", "中華"),
        ("{{misspelling of|zh|稍候}}", "稍候的拼寫錯誤。"),
        ("{{n-g|用來表示全範圍}}", "用來表示全範圍"),
        ("{{non-gloss definition|用來表示全範圍}}", "用來表示全範圍"),
        ("{{qual|前句常有“一方面”……}}", "(前句常有“一方面”……)"),
        ("{{qualifier|前句常有“一方面”……}}", "(前句常有“一方面”……)"),
        ("{{taxlink|Okapia johnstoni|species}}", "<i>Okapia johnstoni</i>"),
        ("{{zh-character component|彡}}", "漢字部件「彡」的名稱。"),
        ("{{zh-ref|Schuessler, 2007}}", "Schuessler, 2007"),
    ],
)
def test_process_template(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "zh") == expected
