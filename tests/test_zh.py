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
    "word, pronunciations, etymology, definitions, variants",
    [
        (
            "七講八講",
            [],
            [],
            {"動詞": ["(漳泉話，吳語) 亂講、胡說", "(<i>柳州官話</i>) 用各種方式解釋"]},
            [],
        ),
        (
            "稍後",
            ["/shāohòu/"],
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
            [
                "和製漢語（和製漢語），借自日語 <ruby>世<rp>(</rp><rt>せ</rt><rp>)</rp></ruby><ruby>界<rp>(</rp><rt>かい</rt><rp>)</rp></ruby><ruby>語<rp>(</rp><rt>ご</rt><rp>)</rp></ruby> (<i>sekaigo</i>)。經過二葉亭四迷於1906年出版的同名書籍而普及。"
            ],
            {"專有名詞": ["波蘭籍猶太人眼科醫生柴門霍夫博士（1859-1917）在1887年公佈的一種人造的國際輔助語"]},
            [],
        ),
        (
            "貔貅",
            ["/píxiū/"],
            [
                "現存最早的文獻紀錄見於下方兩者：",
                "如《禮記》所述：",
                "<dl>前有摯獸，則載<b>貔貅</b>。 &#91;文言文，繁體&#93;<br/>前有挚兽，则载<b>貔貅</b>。 &#91;文言文，簡體&#93;<dd><small>出自：《禮記》，約公元前4 – 前2世紀</small></dd><dd><i>Qián yǒu zhìshòu, zé zǎi <b>píxiū</b>.</i> &#91;漢語拼音&#93;</dd><dd>當前面有兇猛的野獸（獵物）時，應懸掛披有<b>貔貅</b>（豹皮）的旗幟。</dd></dl>",
                "如《逸周书》所述：",
                "<dl>山之深也，虎豹<b>貔貅</b>何為可服？ &#91;文言文，繁體&#93;<br/>山之深也，虎豹<b>貔貅</b>何为可服？ &#91;文言文，簡體&#93;<dd><small>出自：《逸周書》，約公元前4 – 前1世紀</small></dd><dd><i>Shān zhī shēn yě, hǔbào <b>píxiū</b> héwèi kě fú?</i> &#91;漢語拼音&#93;</dd><dd>山如此之深，虎、豹、<b>貔貅</b>如何馴服？</dd></dl>",
            ],
            {
                "名詞": ["(<i>中國神話</i>) 傳說的一種瑞獸，能帶來歡樂及好運", "(<i>比喻義</i>) 勇猛的戰士"],
                "形容词": ["(<i>粵語</i>) 頑皮，淘氣"],
            },
            [],
        ),
        (
            "中華",
            ["/Zhōnghuá/"],
            [
                "古代華夏族多建都於黃河南北，因其在四方之中，所以稱作<b>中華</b>。",
                "最早見於東晉孫盛《晉陽秋》（4世紀）中記載，桓溫紀念譙秀而作的一則上表（347年），後來又被南朝宋史學家裴松之引用在《三國志注》（5世紀早期）中。",
                "<dl>於時皇極遘道消之會，群黎蹈顛沛之艱，<b>中華</b>有顧瞻之哀，幽谷無遷喬之望。 &#91;文言文，繁體&#93;<br/>于时皇极遘道消之会，群黎蹈颠沛之艰，<b>中华</b>有顾瞻之哀，幽谷无迁乔之望。 &#91;文言文，簡體&#93;<dd><small>出自：裴松之，《三国志注》，約公元5世紀</small></dd><dd><i>Yú shí huángjí gòu dàoxiāo zhī huì, qúnlí dǎo diānpèi zhī jiān, <b>zhōnghuá</b> yǒu gùzhān zhī āi, yōugǔ wú qiānqiáo zhī wàng.</i> &#91;漢語拼音&#93;</dd><dd>這時朝廷遇上衰落，民眾生活流離艱苦，<b>中原</b>[國家]有敗亡的憂慮，百姓沒有出頭高升的希望。</dd></dl>",
                "裴松之在為《諸葛亮傳》作注時，也使用了中華一詞。",
                "<dl>若使游步<b>中華</b>，騁其龍光，豈夫多士所能沈翳哉！ &#91;文言文，繁體&#93;<br/>若使游步<b>中华</b>，骋其龙光，岂夫多士所能沈翳哉！ &#91;文言文，簡體&#93;<dd><small>出自：裴松之，《三国志注》，約公元5世紀</small></dd><dd><i>Ruò shǐ yóubù <b>Zhōnghuá</b>, chěng qí lóngguāng, qǐ fū duō shì suǒ néng shěnyì zāi!</i> &#91;漢語拼音&#93;</dd></dl>",
            ],
            {"專有名詞": ["(正式，詩歌，exalted) 中國（多指文化、文明、民族等方面）", "(～里) 位於臺灣臺北松山區的里"]},
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
