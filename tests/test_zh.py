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
            {"動詞": ["(漳泉話，吳語) 亂講、胡說", "(<i>柳州官話</i>) 用各種方式解釋"]},
            [],
        ),
        (
            "稍後",
            ["/shāohòu/"],
            [],
            [],
            {
                "副詞": ["在短暫的時間之後"],
                "動詞": ["<i>稍候</i> (shāohòu)的拼寫錯誤"],
            },
            [],
        ),
        (
            "佛教",
            ["/Fójiào/"],
            [],
            [],
            {
                "專有名詞": [
                    "源自印度，奉釋迦牟尼為教主的宗教，以解脫生死、明心見性為教義，可以分為北傳佛教、南傳佛教以及禪宗、淨土宗、密宗等派別，信徒分布於東亞、南亞、東南亞，為世界三大宗教之一。"
                ],
            },
            [],
        ),
        (
            "世界語",
            ["/shìjièyǔ/"],
            [],
            [
                "和製漢語（和製漢語），借自日語 <ruby>世<rp>(</rp><rt>せ</rt><rp>)</rp></ruby><ruby>界<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby> (<i>sekaigo</i>)。經過二葉亭四迷於1906年出版的同名書籍而普及。"
            ],
            {"專有名詞": ["波蘭籍猶太人眼科醫生柴門霍夫博士（1859-1917）在1887年公佈的一種人造的國際輔助語"]},
            [],
        ),
        (
            "貔貅",
            ["/píxiū/"],
            [],
            [
                "現存最早的文獻紀錄見於下方兩者：<dl>前有摯獸，則載<b>貔貅</b>。 &#91;文言文，繁體&#93;<br>前有挚兽，则载<b>貔貅</b>。 &#91;文言文，簡體&#93;<dd><small>出自：《禮記》，約公元前4 – 前2世紀</small></dd><dd><i>Qián yǒu zhìshòu, zé zǎi <b>píxiū</b>.</i> &#91;漢語拼音&#93;</dd><dd>當前面有兇猛的野獸（獵物）時，應懸掛披有<b>貔貅</b>（豹皮）的旗幟。</dd></dl><dl>山之深也，虎豹<b>貔貅</b>何為可服？ &#91;文言文，繁體&#93;<br>山之深也，虎豹<b>貔貅</b>何为可服？ &#91;文言文，簡體&#93;<dd><small>出自：《逸周書》，約公元前4 – 前1世紀</small></dd><dd><i>Shān zhī shēn yě, hǔbào <b>píxiū</b> héwéi kě fú?</i> &#91;漢語拼音&#93;</dd><dd>山如此之深，虎、豹、<b>貔貅</b>如何馴服？</dd></dl>"
            ],
            {
                "名詞": ["(<i>中國神話</i>) 傳說的一種瑞獸，能帶來歡樂及好運", "(<i>比喻義</i>) 勇猛的戰士"],
                "形容词": ["(<i>粵語</i>) 頑皮，淘氣"],
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
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
