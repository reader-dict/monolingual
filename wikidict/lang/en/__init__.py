"""English language."""

import re
from collections import defaultdict

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
    r"""
    We only keep Received Pronunciation (RP), and General American (GA).

    >>> find_pronunciations("", "en")
    []
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/əs/|a=weak form}}", "en")
    []
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ʌs/}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{IPA|en|/kʌm/|/kʊm/}}", "en")
    ['/kʌm/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/wɜːd/|a=RP}}", "en")
    ['UK: /wɜːd/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈmɑɹz/|a=GA}}", "en")
    ['US: /ˈmɑɹz/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈsʌmwʌn/|a=RP,GA}}", "en")
    ['/ˈsʌmwʌn/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/skɜɹd͡ʒ/|[skɔɹd͡ʒ]|a=GA}}", "en")
    ['US: /skɜɹd͡ʒ/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈmɑɹz/|a=GA}} {{IPA|en|/wɜːd/|a=RP}}", "en")
    ['UK: /wɜːd/', 'US: /ˈmɑɹz/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈmɑɹz/|a=GA}} {{IPA|en|/ˈmɑɹz/|a=RP}}", "en")
    ['/ˈmɑɹz/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|RP}}\n** {{IPA|en|/əs/|/əz/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}", "en")
    ['UK: /ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|GA}}\n** {{IPA|en|/əs/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}", "en")
    ['US: /ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|RP}}\n** {{IPA|en|/əs/|/əz/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}\n* {{a|en|GA}}\n** {{IPA|en|/əs/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}\n* {{a|en|Northern England,Local Dublin}}\n** {{IPA|en|/ʊz/|a=strong form}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|weak form, before consonants}}\n** {{enPR|''th''ə}}, {{IPA|en|/ðə/}}\n* {{a|en|weak form, before vowels, see notes below}}\n** {{enPR|''th''ē|''th''ə}}, {{IPA|en|/ði/ [ðɪj]|/ðə/}}\n* {{a|en|strong form}}\n** {{enPR|''th''ē}}, {{IPA|en|/ðiː/}}", "en")
    ['/ðiː/']
    """
    lines: list[str] = []
    in_section = False
    was_in_section = False
    for line in code.splitlines():
        if line.startswith("="):
            in_section = "Pronunciation" in line
        elif in_section:
            was_in_section = True
            lines.append(line.strip())
        elif was_in_section:
            break

    pattern = re.compile(r"\{\{IPA\|en\|([^}]+)\}\}")
    if not lines or not (matches := re.findall(pattern, code)):
        return []

    pronunciations = defaultdict(list)

    # The pronuciation system is clearly defined
    for match in matches:
        if "|a=RP,GA" in match or "|a=GA,RP" in match:
            kind = ""
        elif "|a=RP" in match:
            kind = "UK"
        elif "|a=GA" in match:
            kind = "US"
        else:
            continue
        if not (pron := next((p for p in match.split("|") if p.startswith("/") and p.endswith("/")), "")):
            continue
        pronunciations[pron].append(kind)

    # No pronunciation system found via template arguments, maybe it is defined at a highler level
    if not pronunciations:
        kind = ""
        for line in lines:
            if "{{a|en|RP}}" in line:
                kind = "UK"
            elif "{{a|en|GA}}" in line:
                kind = "US"
            elif "{{a|en|" in line:
                kind = ""

            if (
                kind
                and "a=strong form" in line
                and (matches := re.findall(pattern, line))
                and (pron := next((p for p in matches[0].split("|") if p.startswith("/") and p.endswith("/")), ""))
            ):
                pronunciations[pron].append(kind)

    # No pronunciation system found at all, ensure to pick only strong forms
    if not pronunciations:
        inteteresting = False
        for line in lines:
            if "{{a|en|strong form" in line:
                inteteresting = True
                continue

            if " {{a|en|weak form" in line:
                inteteresting = False
                continue

            if (
                inteteresting
                and (matches := re.findall(pattern, line))
                and (pron := next((p for p in matches[0].split("|") if p.startswith("/") and p.endswith("/")), ""))
            ):
                pronunciations[pron].append("")

    # No specific form found, take the first one as it should be the general one
    if not pronunciations:
        for match in matches:
            if "a=weak form" in match:
                continue
            if pron := next((p for p in matches[0].split("|") if p.startswith("/") and p.endswith("/")), ""):
                pronunciations[pron].append("")

    # If all pronunciations are the same, merge them without the system prefix
    final: list[str] = []
    for pron, kinds in pronunciations.items():
        if len(kinds) > 1:
            final.append(pron)
        elif kinds[0]:
            final.append(f"{kinds[0]}: {pron}")
        else:
            final.append(pron)

    return utils.unique(utils.flatten(sorted(final)))


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
