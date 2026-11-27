"""Korean language."""

import re
from functools import lru_cache

from ... import context

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://ko.wiktionary.org/wiki/%ED%8A%B9%EC%88%98:%EC%9E%84%EC%9D%98%EB%AC%B8%EC%84%9C"

module_trans = "모듈"
template_trans = "틀"

head_sections = (
    "한국어",  # Korean
    "국제",  # international
)
section_sublevels = (3, 4)
sections = (
    # https://ko.wiktionary.org/w/index.php?title=모듈:headword/data&oldid=4480618#L-41
    "형용사",  # adjectives
    "부사",  # adverbs
    "접사",  # affixes
    "관사",  # articles
    "접속사",  # conjunctions
    "관형사",  # determiners
    "한자",  # hanja
    "감탄사",  # interjections
    "형태소",  # morphemes
    "명사",  # nouns
    "수사",  # numerals
    "조사",  # particles
    "접두사",  # prefixes
    "전치사",  # preposition
    "대명사",  # pronouns
    "고유명사",  # proper nouns
    "어근",  # roots
    "접미사",  # suffixes
    "기호",  # symbols
    "유의어",  # synonyms
    "타동사",  # transitive verb
    "동사",  # verbx
    "연어",  # ?
)


RE_FIND_PRONS = re.compile(r"발음: (\[[^\]]+\])")


@lru_cache
def cache_pattern(locale: str) -> re.Pattern[str]:
    return re.compile(rf"(\{{\{{{locale}-IPA[^}}]*}}}})")


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", LANG)
    []

    >>> from wikidict import context
    >>> _ = context.reset(LANG)

    >>> context.new_word("교육자")
    >>> find_pronunciations("{{ko-IPA}}", LANG)
    ['[교육<b>짜</b>]']

    >>> context.new_word("신진대사")
    >>> find_pronunciations("{{ko-IPA}}", LANG)
    ['[신진대사/신진<b>데</b>사]']
    """
    for tpl in cache_pattern(locale).findall(code):
        expanded = context.expand(tpl, LANG)
        if not (prons := RE_FIND_PRONS.findall(expanded)):
            continue
        return sorted(set(prons))

    return []


RE_CLEANUPS = [
    # Convert manual lists to automatic ones
    # `* '''1.''' (...)` → `# (...)`
    (re.compile(r"(?m)^\*[ ]*'+\d+\.'+[ ]*"), "# "),
    # `:[1, 2]: (...)` → `# (...)`
    (re.compile(r"(?m)^:[ ]*\[\d+, \d+\]:[ ]*"), "# "),
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    """
    >>> adjust_wikicode("* '''1.''' [[당구]].", LANG)
    '# [[당구]].'
    >>> adjust_wikicode(":[1, 2]: [[당구]].", LANG)
    '# [[당구]].'
    """
    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    return code
