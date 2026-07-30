"""English language."""

import re

from ... import utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://en.wiktionary.org/wiki/Special:RandomInCategory/English_lemmas#English"

float_separator = "."
thousands_separator = ","

head_sections = ("english", "translingual")
section_patterns = ("#", r"\*")
sublist_patterns = ("#", ":")
section_sublevels = (4, 3)
etyl_section = ("etymology", *[f"etymology {idx}" for idx in range(1, 20)])
sections = (
    *etyl_section,
    # https://en.wiktionary.org/w/index.php?title=Module:headword/data&oldid=85060361#L-41
    "adjective",
    "adverb",
    "article",
    "conjunction",
    "contraction",
    "determiner",
    "interjection",
    # "letter",  # See #2634
    "noun",
    "numeral",
    "number",
    "particle",
    "punctuation mark",
    "prefix",
    "preposition",
    "pronoun",
    "proper noun",
    "suffix",
    "symbol",
    "verb",
)

variant_templates = (
    "{{active participle of",
    "{{adj form of",
    "{{agent noun of",
    "{{an of",
    "{{alternative plural of",
    "{{en-archaic",
    "{{female equivalent of",
    "{{feminine equivalent of",
    "{{femeq",
    "{{feminine of",
    "{{feminine plural of",
    "{{feminine plural past participle of",
    "{{feminine singular of",
    "{{feminine singular past participle of",
    "{{form of",
    "{{gerund of",
    "{{imperfective form of",
    "{{inflection of",
    "{{infl of",
    "{{masculine plural of",
    "{{masculine plural past participle of",
    "{{neuter plural of",
    "{{neuter singular past participle of",
    "{{noun form of",
    "{{participle of",
    "{{passive of",
    "{{passive participle of",
    "{{past participle form of",
    "{{past participle of",
    "{{perfective form of",
    "{{plural of",
    "{{plural",
    "{{present participle of",
    "{{reflexive of",
    "{{verbal noun of",
    "{{verb form of",
)

definitions_to_ignore = (
    "rfdef",
    "translation hub",
    "translation only",
)

templates_ignored = (
    "{{att",
    "{{cite-",
    "{{cleanup",
    "{{def-",
    "{{emojipic",
    "{{etymon",
    "{{examples",
    "{{hide",
    "{{hot ",
    "{{Image requested",
    "{{img",
    "{{listen",
    "{{mapframe",
    "{{multiple ",
    "{{no entry",
    "{{nonlemma",
    "{{pic",
    "{{PIE word",
    "{{quote-",
    "{{R:",
    "{{RQ:",
    "{{ref",
    "{{rf",
    "{{see",
    "{{t-needed",
    "{{unsupported",
    "{{wiki",
    "{{Wiktionary:Picture",
    "{{wp",
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "en")
    []
    >>> find_genders("{{taxoninfl|i=1|g=f}}", "en")
    ['f']
    """
    pattern = re.compile(r"{taxoninfl\|(?:i=\d+\|)?g=(\w+).*")
    return utils.unique(utils.flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "en")
    []
    >>> find_pronunciations("{{IPA|en|/ʌs/}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("{{IPA|en|/ʌs/|/ʌs/}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("{{IPA|en|/ʌs/}} {{IPA|en|/ʌs/}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("{{IPA|en|/ʌs/}}, {{IPA|en|/ʌz/}}", "en")
    ['/ʌs/', '/ʌz/']
    >>> find_pronunciations("{{IPA|en|/ʌs/|/ʌz/}}", "en")
    ['/ʌs/', '/ʌz/']
    """
    pattern = re.compile(rf"\{{IPA\|{locale}\|(/[^/]+/)(?:\|(/[^/]+/))*")
    return utils.unique(utils.flatten(pattern.findall(code)))


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: assign-if-exp, inline-immediately-returned-variable, inline-variable, reintroduce-else
    r"""
    >>> adjust_wikicode('== English ==\n{| class="floatright"\n|-\n| {{PIE word|en|h₁eǵʰs}}\n| {{PIE word|en|ḱóm}}\n|}', "en")
    '== English ==\n'
    >>> adjust_wikicode('== English ==\n{| class="floatright"\n|-\n| {{PIE word|en|h₁eǵʰs}}\n| {{PIE word|en|ḱóm}}\n|}{{root|en|ine-pro|*(s)ker-|id=cut|*h₃reǵ-}}', "en")
    '== English ==\n{{root|en|ine-pro|*(s)ker-|id=cut|*h₃reǵ-}}'
    >>> adjust_wikicode("== English ==\n<math>\\frac{|AP|}{|BP|} = \\frac{|AC|}{|BC|}</math>", "en")
    '== English ==\n<math>\\frac{|AP|}{|BP|} = \\frac{|AC|}{|BC|}</math>'
    """
    # Remove tables (cf issue #2073)
    code = re.sub(r"^\{\|.*?\|\}", "", code, flags=re.DOTALL | re.MULTILINE)

    # Wipe out `{{text float box|...}}`
    if "{{text float box" in code:
        cleaned: list[str] = []
        in_unwanted_section = False
        for line in code.splitlines():
            if line.startswith("{{text float box|"):
                in_unwanted_section = True
            elif line.endswith("}}"):
                in_unwanted_section = False
            elif not in_unwanted_section:
                cleaned.append(line)
        code = "\n".join(cleaned)

    return code
