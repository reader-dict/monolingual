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
            {"動詞": ["<small>(漳泉話，吳語)</small> 亂講、胡說", "<small>(<i>柳州官話</i>)</small> 用各種方式解釋"]},
            [],
        ),
        (
            "稍後",
            ["/shāohòu/"],
            [],
            [],
            {
                "副詞": [
                    "在短暫的時間之後",
                    (
                        "<dl>網絡錯誤，請<b>稍後</b>重試。 &#91;現代標準漢語，繁體&#93;<br>网络错误，请<b>稍后</b>重试。 &#91;現代標準漢語，簡體&#93;<dd><i>Wǎngluò cuòwù, qǐng <b>shāohòu</b> zhòngshì.</i> &#91;漢語拼音&#93;</dd></dl>",
                    ),
                ],
                "動詞": [
                    "<i>稍候</i> (shāohòu)的拼寫錯誤",
                    (
                        "<dl>之後，開始漫長的音樂等待，然後出現語音：「現在客服全部忙線中，請<b>稍後</b>，我們盡快為您服務……」 &#91;現代標準漢語，繁體&#93;<br>之后，开始漫长的音乐等待，然后出现语音：「现在客服全部忙线中，请<b>稍后</b>，我们尽快为您服务……」 &#91;現代標準漢語，簡體&#93;<dd><small>出自：<b>2015</b>年，洪繡巒《行家這樣做好服務》，台北：時報文化，ISBN 978-957-13-6308-0，page 67</small></dd><dd><i>zhīhòu, kāishǐ màncháng de yīnyuè děngdài, ránhòu chūxiàn yǔyīn: “Xiànzài kèfú quánbù mángxiàn zhōng, qǐng <b>shāohòu</b>, wǒmen jìnkuài wèi nín fúwù......”</i> &#91;漢語拼音&#93;</dd></dl>",
                    ),
                ],
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
                    "源自印度，奉釋迦牟尼為教主的宗教，以解脫生死、明心見性為教義，可以分為北傳佛教、南傳佛教以及禪宗、淨土宗、密宗等派別，信徒分布於東亞、南亞、東南亞，為世界三大宗教之一。",
                    (
                        "<b>佛教</b>經典／<b>佛教</b>经典&nbsp; ―&nbsp; <i><b>fójiào</b> jīngdiǎn</i>",
                        "<b>佛教</b>建築／<b>佛教</b>建筑&nbsp; ―&nbsp; <i><b>fójiào</b> jiànzhù</i>",
                    ),
                ]
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
