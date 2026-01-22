from pathlib import Path
from unittest.mock import patch

import pytest
from requests import HTTPError

from wikidict import context, get_word


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("fr")


def test_simple() -> None:
    # The word exists and contains subsublists.
    assert get_word.main("fr", "base", local=True) == 0


@pytest.mark.webtest
def test_get_random_word() -> None:
    assert get_word.main("fr", "") == 0


def test_subdefinitions() -> None:
    assert get_word.main("fr", "mesure", local=True) == 0


def test_raw() -> None:
    assert get_word.main("fr", "marron", raw=True, local=True) == 0


def test_word_with_variants() -> None:
    assert get_word.main("fr", "suis", local=True) == 0


@pytest.mark.webtest
def test_word_not_found() -> None:
    with pytest.raises(HTTPError):
        get_word.main("fr", "mutinerssssssss")
