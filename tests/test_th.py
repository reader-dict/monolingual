from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "th"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "หมายความว่า",
            [],
            ["&#32;<i>หมายความ</i> +&lrm; <i>ว่า</i>"],
            {"คำกริยา": ["แปลความว่า, ตีความว่า"]},
            [],
            [],
        ),
        (
            "เลย",
            [],
            [
                "ร่วมเชื้อสายกับจ้วงแบบจั่วเจียง <i>leh</i> (แล่-จึง ก็เลย)",
                "จึง",
                "ร่วมเชื้อสายกับลาว <i>ເລີຍ</i> (เลีย), ไทใหญ่ <i>လိူဝ်</i> (เลิว)",
                "วิกิพีเดียภาษาไทยมีบทความ:<b>จังหวัดเลย</b>",
            ],
            {
                "คำกริยา": ["พ้นหรือเกินจุดที่กำหนด"],
                "คำกริยาวิเศษณ์": [
                    "แสดงการกระทำกริยาอีกอย่างหนึ่งต่อไป ใช้ประกอบหน้ากริยา",
                    "เน้นความว่า ทันที, ทีเดียว ใช้ประกอบหลังคำอื่น",
                    "โดยสิ้นเชิง, แม้แต่น้อย",
                ],
                "คำวิสามานยนาม": ["(จังหวัด~) ชื่อจังหวัดในภาคตะวันออกเฉียงเหนือของประเทศไทย"],
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
