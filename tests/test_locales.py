import json
from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

CURRENT_LOCALE = ""
ROOT = Path(context.__file__).parent.parent
DATA = ROOT / "tests" / "data"
TEST_CASES = sorted(DATA.glob("**/test-cases.json"))


@pytest.mark.parametrize(
    "locale, word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        pytest.param(data.parent.name, word, *details, id=f"{data.parent.name}-{word}")
        for data in TEST_CASES
        for word, details in json.loads(data.read_text(encoding="utf-8")).items()
    ],
)
def test_parse_word(
    locale: str,
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    global CURRENT_LOCALE
    if CURRENT_LOCALE != locale:
        CURRENT_LOCALE = locale
        with patch.dict("os.environ", {"CWD": str(ROOT)}):
            assert context.reset(locale)

    print(f"{locale = }, {word = }")
    code = page(word, locale)
    details = parse_word(word, code, locale, force=True)
    assert details

    # To know what to put in test-cases.json, you can use this helper:
    # assert 0, details.tojson()

    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants

    assert not context.get_then_clear_errors()
