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
        assert context.reset("ja")


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "みてる",
            [],
            [],
            {"動詞": ["「みている」の音便", "なくなる、消失する", "しぬ、くさる"]},
            [],
            [],
        ),
        (
            "みる",
            ["みる (頭高型 – [1])"],
            ["古典日本語「みる」 &lt; 日本祖語 <i>*miru</i>"],
            {
                "動詞": [
                    "【見る・視る】<ruby>目<rp>（</rp><rt>め</rt><rp>）</rp></ruby>を使って、<ruby>物<rp>（</rp><rt>もの</rt><rp>）</rp></ruby>の<ruby>形<rp>（</rp><rt>かたち</rt><rp>）</rp></ruby>や<ruby>色<rp>（</rp><rt>いろ</rt><rp>）</rp></ruby>を<ruby>知<rp>（</rp><rt>し</rt><rp>）</rp></ruby>る。視覚によって対象をとらえる。注意して見る。注視する。観察する。",
                    "ある場面に遭遇する。ある現象がおこる。",
                    "【観る】視覚にいるものを楽しむ、観賞する。",
                    "【見る・観る】かんがえる。判断する。推測する。",
                    "世話をする。対処する。指導・監督する。",
                    ("【看る】病人の世話をする。介護する。看取る、看護する。",),
                    "【診る】(医療)患者の具合を調べる。診察する、診断する。",
                    "（補助動詞）ためしにおこなう。軽い気持ちでする。挑む気持ちでやる。",
                ],
                "名詞": [
                    "(藻類)ミル科ミル属の海藻。枝分かれが外見上の特徴で、食用になる。学名: <i>Codium fragile</i>。",
                    "(色)暗い緑色。",
                ],
                "類義語": ["ながめる", "凝視する", "傍観する", "みるめ"],
            },
            [],
            ["みた", "みない", "みます", "みよ", "みよう", "みること", "みれば", "みろ"],
        ),
        (
            "駐",
            [],
            ["形声。「馬」+音符「主 /*TO/」。漢語｛駐 /*tros/｝を表す字。"],
            {
                "ことわざ": ["駐軍", "駐在", "駐箚", "駐車", "駐屯", "駐歩", "駐留", "駐輦", "移駐", "常駐", "進駐"],
                "意義": ["（馬や車を）長時間、停める。", "（別に本拠とするところがあるが）じっと一箇所にいる。"],
                "造語成分": ["国外に派遣されて、長期間滞在しているという意味の語を作る。"],
            },
            [],
            [],
        ),
        (
            "併",
            [],
            [
                "形声。「人」+音符「幷 /*PENG/」。「ならぶ」「あわさる」を意味する漢語｛併 /*peng/｝を表す字。もと「幷」が｛併｝を表す字であったが、人偏を加えた。"
            ],
            {
                "ことわざ": ["併起", "併行", "併合", "併設", "併吞", "併発", "併用", "合併"],
                "意義": [
                    "（『説文解字』では「幷・并」）あわす。あわさる。あわせる。",
                    "（『説文解字』では「倂・併」）ならぶ。ならべる。「並」とも書く。",
                ],
            },
            [],
            [],
        ),
        (
            "有する",
            [],
            [],
            {"動詞": ["(他動詞,&#32;文章語)持つ。持っている。"]},
            [],
            ["有される", "有した", "有しない", "有します", "有しろ", "有すること", "有すれば", "有せず", "有せよ"],
        ),
        (
            "V",
            [],
            [],
            {
                "名詞": ["ラテン文字の第二十二字。", "（victoryより）勝利。", "（テレビ放送業界）VTRの略。映像。"],
                "記号": ["バナジウムの元素記号", "電圧", "電圧の単位ボルト", "ローマ数字で5を表す記号（Ⅴ）"],
            },
            [],
            [],
        ),
        (
            "いる",
            [],
            [
                "古典日本語「いる」を語源とするもの。",
                "古典日本語「いる」（上古はヤ行の「い」）を語源とするもの。",
                "古典日本語「ゐる」を語源とするもの。",
            ],
            {
                "動詞": [
                    "(自動詞) はいる。外から中へと移動する。",
                    "主に京都で、東西方向の移動を表す方言。単独では用いられず、「東入る」（東方向への移動）「西入る」（西方向への移動）の形で、若しくは「る」をカタカナにした「東入ル」「西入ル」の形で用いる。",
                    "(自動詞) 必要とされる。必要だ。",
                    "(自動詞) ほしいと思う。",
                    "（「いらない」「いらぬ」などの形で）しなくていい。すべきでない。余計だ。",
                    "(近畿方言,&#32;補助動詞)（「していらん」の形で）しなくていい。しないでほしい。",
                    "(他動詞) ものに向かって矢を放つ。撃つ。",
                    "(他動詞) 放った矢によりねらったものを射抜く、射当てる。またそのように試みる。",
                    "(他動詞) 火にかける。調理において鍋などを用い、強く熱を加え、水気を飛ばす。いりつける。",
                    "(他動詞) 自然乾燥したものを鍋などに入れて加熱し、さらに水分を飛ばして香ばしくまたくだけやすくする。",
                    "(他動詞) 鋳造する。",
                    "(自動詞) 熟する。",
                    "(自動詞)（生物がそこに）存在する。",
                    (
                        "（「（するような者は）いない」「（するような者が）いるか」などの形で）普通はしない。すべきでない。したことは問題だ。",
                    ),
                    "(自動詞) 滞在する。",
                    "(自動詞) とどまる。",
                    "(自動詞) すわる。",
                    "（補助動詞）その状態を保つことをする。",
                ],
                "連語": ["悦に入る、気に入る、興に入る"],
                "類義語": ["射撃する", "あぶる、焙煎する", "ある（主に主語が無生物の場合）", "おる"],
            },
            [],
            [
                "いた",
                "いった",
                "いない",
                "います",
                "いよ",
                "いよう",
                "いらない",
                "いります",
                "いること",
                "いれ",
                "いれば",
                "いろ",
                "いろう",
            ],
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
    code = page(word, "ja")

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    if "{{kanji header" in code:
        code = f"=={{{{kanji}}}}==\n{code}"

    details = parse_word(word, code, "ja", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
