import pytest
from requests import HTTPError

from wikidict import get_word


@pytest.mark.webtest
def test_simple() -> None:
    # The word exists and contains subsublists.
    assert get_word.main("fr", "base") == 0


@pytest.mark.webtest
def test_get_random_word() -> None:
    assert get_word.main("en", "") == 0


@pytest.mark.webtest
def test_subdefinitions() -> None:
    assert get_word.main("fr", "mesure") == 0


@pytest.mark.webtest
def test_raw() -> None:
    assert get_word.main("fr", "marron", raw=True) == 0


@pytest.mark.webtest
def test_word_with_variants() -> None:
    assert get_word.main("fr", "suis") == 0


@pytest.mark.webtest
def test_word_not_found() -> None:
    with pytest.raises(HTTPError):
        get_word.main("fr", "mutinerssssssss")


@pytest.mark.webtest
@pytest.mark.parametrize(
    ("locale", "word", "pronunciations"),
    [
        ("sv", "en", ["/en/", "/eːn/", "/ɛn/"]),
    ],
)
def test_locale_pronunciations(locale: str, word: str, pronunciations: list[str]) -> None:
    details = get_word.get_word(word, locale)
    assert details.pronunciations == pronunciations


@pytest.mark.webtest
@pytest.mark.parametrize(
    ("locale", "word", "etymology_len"),
    [
        ("es", "hocico", 1),
        ("pt", "alguém", 1),
    ],
)
def test_locale_etymologies(locale: str, word: str, etymology_len: int) -> None:
    details = get_word.get_word(word, locale)
    assert len(details.etymology) == etymology_len
