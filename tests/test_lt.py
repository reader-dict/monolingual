from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word

LANG = __name__.split("_", 1)[1]


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


def test_skip_variant(page: Callable[[str, str], str]) -> None:
    word = "informatikos"
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert not details
