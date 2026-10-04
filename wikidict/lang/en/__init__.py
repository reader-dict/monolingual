"""English language."""

import re
from collections import defaultdict

from ... import utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://en.wiktionary.org/wiki/Special:RandomInCategory/English_lemmas#English"

head_sections = ("english", "translingual")
section_patterns = ("#", r"\*")
sublist_patterns = ("#", ":")
section_sublevels = (3, 4, 5)
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
    pattern = re.compile(r"\{\{taxoninfl\|(?:i=\d++\|)?g=(\w++).*")
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
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈmɑɹz/|a=GA}}\n{{IPA|en|/wɜːd/|a=RP}}", "en")
    ['UK: /wɜːd/', 'US: /ˈmɑɹz/']
    >>> find_pronunciations("====Pronunciation====\n{{IPA|en|/ˈmɑɹz/|a=GA}}\n{{IPA|en|/ˈmɑɹz/|a=RP}}", "en")
    ['/ˈmɑɹz/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|RP}}\n** {{IPA|en|/əs/|/əz/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}", "en")
    ['UK: /ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|GA}}\n** {{IPA|en|/əs/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}", "en")
    ['US: /ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|RP}}\n** {{IPA|en|/əs/|/əz/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}\n* {{a|en|GA}}\n** {{IPA|en|/əs/|a=weak form}}\n** {{IPA|en|/ʌs/|a=strong form}}\n* {{a|en|Northern England,Local Dublin}}\n** {{IPA|en|/ʊz/|a=strong form}}", "en")
    ['/ʌs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|weak form, before consonants}}\n** {{enPR|''th''ə}}, {{IPA|en|/ðə/}}\n* {{a|en|weak form, before vowels, see notes below}}\n** {{enPR|''th''ē|''th''ə}}, {{IPA|en|/ði/ [ðɪj]|/ðə/}}\n* {{a|en|strong form}}\n** {{enPR|''th''ē}}, {{IPA|en|/ðiː/}}", "en")
    ['/ðiː/']
    >>> find_pronunciations("===Pronunciation===\n* {{IPA|en|/ˈɹi.dɚ/|a=GenAm}}\n* {{a|en|UK}}\n** {{IPA|en|/ˈɹiː.də/|a=RP}}\n** {{IPA|en|/ˈɹiː.dɐ/|a=Northumbria}}\n* {{audio|en|en-us-reader.ogg|a=US}}\n* {{rhymes|en|iːdə(ɹ)|s=2}}\n* {{hyph|en|read|er}}", "en")
    ['UK: /ˈɹiː.də/', 'US: /ˈɹi.dɚ/']
    >>> find_pronunciations("===Pronunciation===\n* {{enPR|ə-kwârʹē-əm|a=GA}}, {{IPA|en|/əˈkwɛɹ.i.jəm/|/-ɛɹiəm/}}\n* {{audio|en|en-us-aquarium.ogg|a=US}}", "en")
    ['US: /əˈkwɛɹ.i.jəm/']
    >>> find_pronunciations("===Pronunciation===\n* {{IPA|en|/ˈjuːnɪˌvɜːs/|a=RP}} {{audio|en|LL-Q1860 (eng)-Bytekast-universe (RP).wav|-}}\n* {{IPA|en|/ˈjunəˌvɝs/|a=US}} {{audio|en|en-us-universe.ogg|-}}\n* {{IPA|en|/ˈjʉːnɪˌvɜːs/|a=AU}}\n* {{IPA|en|/ˈjʉːnəˌvøːs/|a=NZ}}\n* {{IPA|en|/ˈjʉːnɪˌvɛɾs/|a=Scotland}}\n* {{IPA|en|/ˈjɪʊ̯nɪˌvøːs/|a=Wales}}\n\n* {{IPA|en|/ˈjʉːnɪˌveːs/|a=Scouse,square-nurse}}\n* {{IPA|en|/ˈjuːnɪˌvɛːs/|a=Humberside,Teesside,square-nurse}}\n* {{rhymes|en|ɜː(ɹ)s|s=3}}", "en")
    ['UK: /ˈjuːnɪˌvɜːs/', 'US: /ˈjunəˌvɝs/']
    >>> find_pronunciations("====Pronunciation====\n* {{a|en|non-rhotic}}\n** {{a|en|UK}}\n*** {{IPA|en|/ˈflaʊ̯.ə/|[ˈflaʊ̯.ə]|a=RP}}\n**** {{audio|en|en-uk-flower.ogg|a=London}}\n*** {{IPA|en|/ˈflawə/|a=SSB}}\n*** {{IPA|en|/ˈfluː.ɐ/|[ˈfluː.ɐ]|a=Northumbria}}\n** {{IPA|en|/ˈflæɔ.ə/|[ˈflæɔ̯.ə]|a=AU,[[w:Fronting (sound change)|/aʊ̯/-fronting]]}}\n*** {{audio|en|en-au-flower.ogg|a=Queensland}}\n** {{IPA|en|/ˈflæʊ.ə/|[ˈflæʊ̯.ə]|a=NZ,[[w:Fronting (sound change)|/aʊ̯/-fronting]]}}\n** {{IPA|en|/ˈflaː.ə/|[ˈflaː.ə]|a=ZA,[[w:monophthongization|/aʊ̯/-monophthongization]]}}\n* {{a|en|rhotic}}\n** {{IPA|en|/ˈflaʊ̯.ɚ/|[ˈflaʊ̯.ɚ]|~|[ˈflaʊ̯.ɹ̩]|a=GA,[[w:Standard Canadian English|Standard Canadian]]}}\n*** {{audio|en|en-us-flower.ogg|a=California}}\n** {{IPA|en|/ˈflæʊ̯.ɚ/|[ˈflæʊ̯.ɚ]|~|[ˈflæʊ̯.ɹ̩]|a=Southern US,Midland US,Mid-Atlantic US,NYC,[[w:Fronting (sound change)|/aʊ̯/-fronting]]}}\n** {{IPA|en|/ˈflaː.ɚ/|[ˈflaː.ɚ]|~|[ˈflaː.ɹ̩]|a=Pittsburgh,[[w:monophthongization|/aʊ̯/-monophthongization]]}}\n* {{a|en|Indic}}\n** {{IPA|en|/ˈflaː(r)/|[ˈflaː(r)]|;|/ˈflɐ.ʋə(r)/|[ˈflɐ.ʋə(r)]|;|/ˈflɐ.wə(r)/|[ˈflɐ.wə(r)]|a=India}}\n* {{rhymes|en|aʊ.ə(ɹ)|s1=2}}\n* {{hyph|en|flow|er}}\n* {{homophones|en|flour|aa1=for people who pronounce ''flower'' as one syllable, or ''flour'' as two}}", "en")
    ['UK: /ˈflaʊ̯.ə/', 'US: /ˈflaʊ̯.ɚ/']
    >>> find_pronunciations("===Pronunciation===\n* {{enPR|stĕm}}, {{IPA|en|/stɛm/|a=RP,GA}}\n** {{audio|en|en-us-stem.ogg|a=US}}\n* {{IPA|en|/stɪm/|a=US,pin-pen}}\n* {{IPA|en|/stem/|a=AU,NZ}}\n* {{rhymes|en|ɛm|s=1}}\n* {{hmp|en|stim<aa:pin-pen>}}", "en")
    ['/stɛm/']
    >>> find_pronunciations("===Pronunciation===\n* {{qualifier|stressed}}\n** {{IPA|en|/ɪt/|a=RP,GA,Aus}} {{enPR|ĭt}}\n** {{audio|en|en-uk-it.ogg|a=UK}}\n** {{audio|en|en-us-it.ogg|a=US}}\n** {{IPA|en|/ɘt/|a=NZ}}\n** {{rhymes|en|ɪt|s=1}}\n* {{qualifier|unstressed}}\n** {{IPA|en|/ɪt/|[ɪ̈t]|[ɪt]|a=RP}}\n** {{rhymes|en|ɪt|s=1}}\n** {{IPA|en|/ət/|[ɪ̈t]|[ɪ̈ʔ]|a=GA}}, {{enPR|ət}}\n** {{IPA|en|[ɪʔ]|a=Pacific Northwest}}\n** {{IPA|en|/ət/|a=Aus}}\n** {{IPA|en|/ɘt/|a=NZ}}\n* {{audio|en|LL-Q1860 (eng)-Vealhurl-it.wav|a=Southern England}}\n* {{homophones|en|at}} {{qualifier|unstressed}} {{a|en|General American|General Australian}}\n<!-- 1 syllable words !-->", "en")
    ['/ɪt/']
    >>> find_pronunciations("====Pronunciation====\n* {{q|letter name}}\n** {{IPA|en|/eɪ/|a=UK,US}}\n*** {{audio|en|en-us-a.ogg|a=US}}\n** {{IPA|en|/æɪ/|a=AusE}}\n** {{IPA|en|[eː]|a=CA}}\n** {{rhymes|en|eɪ|s=1}}\n*: The current pronunciation resulted from the [[w:Great Vowel Shift|Great Vowel Shift]]. Before the early part of the 17th century, the pronunciation was similar to that in other languages.\n* {{q|phoneme}} {{IPA|en|/æ/|/ɑː/|/eɪ/|/ə/}}, etc.", "en")
    ['/eɪ/']
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

    if not lines:
        return []

    interesting_code = "\n".join(lines)
    pattern = re.compile(r"^.*?\{\{IPA\|en\|([^}]++)\}\}", flags=re.MULTILINE)
    if not (matches := list(re.finditer(pattern, interesting_code))):
        return []

    pronunciations = defaultdict(list)

    # The pronunciation system is clearly defined
    for match in matches:
        line, target = match[0], match[1]
        if "a=" not in line:
            continue
        if "GA" in line or "GenAm" in line or "US" in line:
            kind = "" if "RP" in line or "UK" in line else "US"
        elif "RP" in line or "UK" in line:
            kind = "UK"
        else:
            continue

        if pron := next((p for p in target.split("|") if p.startswith("/") and p.endswith("/")), ""):
            pronunciations[pron].append(kind)

    # No pronunciation system found via template arguments, maybe it is defined at a highler level
    if not pronunciations:
        kind = ""
        for line in lines:
            if "{{a|en|RP}}" in line or "{{a|en|UK}}" in line:
                kind = "UK"
            elif "{{a|en|GA}}" in line or "{{a|en|GenAm}}" in line or "{{a|en|US}}" in line:
                kind = "US"
            elif "{{a|en|" in line:
                kind = ""

            if (
                kind
                and "strong form" in line
                and (match_ := re.search(pattern, line))
                and (pron := next((p_ for p_ in match_[1].split("|") if p_.startswith("/") and p_.endswith("/")), ""))
            ):
                pronunciations[pron].append(kind)

    # No pronunciation system found at all, ensure to pick only strong forms
    if not pronunciations:
        inteteresting = False
        for line in lines:
            if "strong form" in line:
                inteteresting = True
            elif "weak form" in line:
                inteteresting = False

            if (
                inteteresting
                and (match_ := re.search(pattern, line))
                and (pron := next((p_ for p_ in match_[1].split("|") if p_.startswith("/") and p_.endswith("/")), ""))
            ):
                pronunciations[pron].append("")
                inteteresting = False

    # No specific form found, take the first one as it should be the general one
    if not pronunciations:
        for match in matches:
            line, target = match[0], match[1]
            if "weak form" in line:
                continue

            if pron := next((p_ for p_ in target.split("|") if p_.startswith("/") and p_.endswith("/")), ""):
                pronunciations[pron].append("")

    # If all pronunciations are the same, merge them without the system prefix
    final: list[str] = []
    pronunciation_already_handled: defaultdict[str, bool] = defaultdict(bool)
    for pron, kinds in sorted(pronunciations.items(), key=lambda kv: kv[1]):
        if len(kinds) > 1:
            final.append(pron)
            break
        elif kinds[0]:
            if not pronunciation_already_handled[kinds[0]]:
                pronunciation_already_handled[kinds[0]] = True
                final.append(f"{kinds[0]}: {pron}")
        else:
            final.append(pron)
            break

    return final


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
