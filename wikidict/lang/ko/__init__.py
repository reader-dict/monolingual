"""Korean language."""

import re

from ... import context

random_word_url = "https://ko.wiktionary.org/wiki/%ED%8A%B9%EC%88%98:%EC%9E%84%EC%9D%98%EB%AC%B8%EC%84%9C"

module_trans = "모듈"
template_trans = "틀"

float_separator = ","
thousands_separator = " "

head_sections = ("한국어", "국제")
section_sublevels = (4, 3)
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


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ko")
    []

    >>> from wikidict import context
    >>> _ = context.reset("ko")

    >>> context.new_word("교육자")
    >>> find_pronunciations("{{ko-IPA}}", "ko")
    ['[교육<b>짜</b>]']

    >>> context.new_word("신진대사")
    >>> find_pronunciations("{{ko-IPA}}", "ko")
    ['[신진대사/신진<b>데</b>사]']
    """
    for tpl in re.findall(rf"(\{{\{{{locale}-IPA[^}}]*}}}})", code):
        expanded = context.expand(tpl, "ko")
        if not (prons := re.findall(r"발음: (\[[^\]]+\])", expanded)):
            continue
        return sorted(set(prons))

    return []


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    """
    >>> adjust_wikicode("* '''1.''' [[당구]].", "ko")
    '# [[당구]].'
    >>> adjust_wikicode(":[1, 2]: [[당구]].", "ko")
    '# [[당구]].'
    """
    # Convert manual lists to automatic ones
    # `* '''1.''' (...)` → `# (...)`
    code = re.sub(r"^\*[ ]*'+\d+\.'+[ ]*", "# ", code, flags=re.MULTILINE)
    # `:[1, 2]: (...)` → `# (...)`
    code = re.sub(r"^:[ ]*\[\d+, \d+\]:[ ]*", "# ", code, flags=re.MULTILINE)

    return code
