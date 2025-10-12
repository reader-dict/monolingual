from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context, gen_dict


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("fr")


@pytest.mark.webtest
@pytest.mark.parametrize(
    "locale, words",
    [
        ("fr", "logiciel"),  # Single word
        ("fr", "base,logiciel"),  # Multiple words
        ("fr", "cercle unité"),  # Accentued word + space
        ("fr:fr", "logiciel"),  # Sublang falsy
        ("fr:it", "glielo"),  # Another lang
    ],
)
def test_gen_dict(locale: str, words: str, tmp_path: Path) -> None:
    for format in ["dictfile", "df", "dictorg", "kobo", "dicthtml", "kindle", "mobi", "stardict"]:
        assert gen_dict.main(locale, words, tmp_path, format=format) == 0
