"""English language."""

import re

from ...user_functions import flatten, unique
from .labels import labels

# Float number separator
float_separator = "."

# Thousands separator
thousands_separator = ","

# Markers for sections that contain interesting text to analyse.
head_sections = ("english", "translingual")
section_patterns = ("#", r"\*")
section_sublevels = (4, 3)
etyl_section = ("etymology", *[f"etymology {idx}" for idx in range(1, 20)])
sections = (
    *etyl_section,
    "adjective",
    "adverb",
    "article",
    "conjunction",
    "contraction",
    "determiner",
    "interjection",
    "letter",
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

# Variants
variant_titles = sections
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

# Some definitions are not good to keep
definitions_to_ignore = ("rfdef", "translation hub", "translation only")

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "#tag",
    "anchor",
    "Anchor",
    "ant",
    "att",
    "attention",
    "attn",
    "audio",
    "book of the Bible",
    "box",
    "box-bottom",
    "box-top",
    "c",
    "C",
    "catlangname",
    "center bottom",
    "center top",
    "character info",
    "cite-av",
    "cite-book",
    "cite-journal",
    "cite-newsgroup",
    "cite-song",
    "cite-thesis",
    "cite-video game",
    "cite-web",
    "cleanup",
    "clear",
    "cln",
    "col",
    "col-bottom",
    "col-top",
    "commonscat",
    "def-unc",
    "def-uncertain",
    "dercat",
    "dhub",
    "elements",
    "emojipic",
    "en-preposition",
    "enum",
    "etymid",
    "etymon",
    "etystub",
    "examples",
    "fullurl",
    "head-lite",
    "hide",
    "hot sense",
    "hot word",
    "Image requested",
    "img",
    "interwiktionary",
    "lena",
    "letter_disp2",
    "listen",
    "multiple image",
    "multiple images",
    "nl",
    "no entry",
    "non-lemma",
    "nonlemma",
    "number box",
    "+obj",
    "PIE word",
    "picdic",
    "picdicimg",
    "picdiclabel",
    "quote-book",
    "quote-hansard",
    "quote-journal",
    "quote-mailing list",
    "quote-newsgroup",
    "quote-song",
    "quote-us-patent",
    "quote-video game",
    "quote-web",
    "quote-wikipedia",
    "R",
    "ref",
    "reflist",
    "refn",
    "rel-bottom",
    "rel-top",
    "rf-sound example",
    "rfap",
    "rfc",
    "rfc-sense",
    "rfclarify",
    "rfd",
    "rfd-redundant",
    "rfd-sense",
    "rfdate",
    "rfdef",
    "rfe",
    "rfeq",
    "rfetym",
    "rfex",
    "rfi",
    "rfm",
    "rfm-sense",
    "rfp",
    "rfq",
    "rfq-sense",
    "rfquote",
    "rfquote-sense",
    "rfref",
    "rfscript",
    "rfusex",
    "rfv",
    "rfv-etym",
    "rfv-sense",
    "root",
    "see",
    "see desc",
    "seeMoreCites",
    "slim-wikipedia",
    "senseid",
    "senseno",
    "seeCites",
    "sid",
    "swp",
    "syndiff",
    "synonyms",
    "t-needed",
    "tea room",
    "tea room sense",
    "thub",
    "top",
    "topic",
    "topics",
    "translation only",
    "unsupported",
    "ux",
    "uxi",
    "void",
    "was wotd",
    "wikidata",
    "wikidata lexeme",
    "wikipedia",
    "Wikipedia",
    "wikiquote",
    "wikispecies",
    "Wikispecies",
    "word",
    "wp",
)

# Templates that will be completed/replaced using italic style.
templates_italic = {
    **labels,
    "gentrade": "Genericized trademark",
}

# Templates more complex to manage.
templates_multi = {
    # {{1|interactive}}
    "1": "capitalize(parts[-1])",
    # {{abbr|pmo.|Proto-Mongolic}}
    "abbr": "parts[1]",
    # {{abbrev|en|goodbye}}
    "abbrev": 'f"Abbreviation of {italic(parts[-1])}"',
    # {{ar-form|IV}}
    # {{ar-form|IV|verb form}}
    "ar-form": "f'{parts[2] if len(parts) > 2 else 'Form'} {parts[1]}'",
    # {{C.|21|st}}
    "C.": "parts[1] + (parts[2] if len(parts) > 2 else 'th') + f' c.'",
    # {{caps|discourse}}
    "caps": "parts[-1]",
    # {{caret notation of|null}}
    "caret notation of": "f'<i>(computing) The ASCII control character</i> <b>{parts[1]}</b> <i>in caret notation</i>.'",
    # {{code|js|=(65535).toString(16) === 'ffff'}}
    "code": "code(parts[1], parts[2])",
    # {{color panel|vermilion|E34234}}
    "color panel": "((parts[1] + ': ') if len(parts) > 2 else '') + color(parts[-1])",
    # {{defdate|from 15th c.}}
    "defdate": "small('[' + parts[1] + (f'–{parts[2]}' if len(parts) > 2 else '') + ']')",
    # {{doi|10.1159/000070783}}
    "doi": "f'→ https://doi.org/{concat(parts[1:], '/')}'",
    # {{en:w|Pepe the Frog}} -> {{en|w|Pepe the Frog}}
    "en": "parts[-1]",
    # {{en-comparative of|term}}
    "en-comparative of": "italic('comparative form of') + f' {strong(parts[1])}' + ': more ' + parts[1]",
    # {{en-obsolete past participle of|baptize}}
    "en-obsolete past participle of": "f\"{term('obsolete')} <i>past participle of</i> {strong(parts[1])}\"",
    # {{en-superlative of|Brummie}}
    "en-superlative of": "f\"{italic('superlative form of')} {strong(parts[1])}: most {parts[1]}\"",
    # {{en-early modern spelling of|colour}}
    "en-early modern spelling of": 'f"<i>Early Modern spelling of</i> {strong(parts[1])}"',
    # {{from|en|-er|id=Oxford}}
    "from": "parts[2]",
    # {{gloss|liquid H<sub>2</sub>O}}
    "gloss": "parenthesis(parts[1])",
    # {{glossary|inflected}}
    "glossary": "parts[-1]",
    # {{h-less dialect|have}}
    "h-less dialect": "f'A representation of the pronunciation of {parts[1]} by someone whose dialect lacks the voiceless glottal fricative or transition (/h/).'",
    # {{i|Used only ...}}
    "i": "'(' + concat([italic(p) for p in parts[1:]], ', ') + ')'",
    # {{IPAfont|[[ʌ]]}}
    "IPAfont": "parts[1]",
    # {{ISBN|1-86429-081-1}}
    "ISBN": "f'ISBN {parts[1]}'",
    # {{italic|Love Island}}
    "italic": "italic(parts[1])",
    # {{IUPAC-1|alanine}}
    "IUPAC-1": 'f"IUPAC 1-letter symbol for {parts[1]}"',
    # {{IUPAC-3|alanine}}
    "IUPAC-3": 'f"IUPAC 3-letter symbol for {parts[1]}"',
    # {{ja-def|茨城}}
    "ja-def": 'f"{parts[1]}:"',
    # {{key press/core|F}}
    "key press/core": "f'<kdb>{parts[1]}</kdb>'",
    # {{lang|fr|texte}}
    "lang": "parts[-1]",
    # {{less common spelling of|en|African-like}
    "less common spelling of": 'f"<i>rare spelling of</i> <b>{parts[-1]}</b>"',
    # {{lit|eagle killer}}
    "lit": 'f"Literally, “{parts[1]}”"',
    # {{male equivalent of|en|Imperatrix}}
    "male equivalent of": "f'male equivalent of {parts[-1]}'",
    # {{mention-gloss|silver-bearing}}
    "mention-gloss": 'f"“{parts[-1]}”"',
    # {{monospace|#!}}
    "mono": "f'<span style=\"font-family:monospace\">{parts[1]}</span>'",
    # {{mul-attributive|Abbott's}}
    "mul-attributive": "f'<i>used in taxonomic names for organisms having English names of the form \"{parts[-1]} ...\"</i>'",
    # {{mul-semaphore for|O}}
    "mul-semaphore for": "f'<i>Flag semaphore for</i> <b>{parts[-1]}</b>.'",
    # {{mul-symbol}}
    "mul-symbol": "word",
    # {{neuter equivalent of|en|dead man walking}}
    "neuter equivalent of": "f'<i>neuter equivalent of</i> <b>{parts[2]}</b>'",
    # {{nobold|or}}
    "nobold": "f'</b>{parts[1]}<b>'",
    # {{noitalic|ふうじん}}
    "noitalic": "f'</i>{parts[1]}<i>'",
    # {{nobr|1=[ ...=C=C=C=... ]}}
    "nobr": 'f\'<span style="white-space:nowrap">{parts[1].lstrip("1=")}</span>\'',
    "nominalization": 'f"Nominalization of {italic(parts[-1])}"',
    # {{non gloss|Definite grammatical ...}}
    "non-gloss": "italic(parts[-1].lstrip('1='))",
    # {{nowrap|1=[ ...=C=C=C=... ]}}
    "nowrap": 'f\'<span style="white-space:nowrap">{parts[1].lstrip("1=")}</span>\'',
    # {{orthography|&thinsp;𝼊&thinsp;}}
    "orthography": "f'⟨{parts[1]}⟩'",
    # {overline|s}}
    "overline": "f'<span style=\"text-decoration:overline\">{parts[1]}</span>'",
    # {{PMID|17286801}}
    "PMID": "f'PMID {parts[1]}'",
    # {{qualifier|Used only ...}}
    "qualifier": "'(' + concat([italic(p) for p in parts[1:]], ', ') + ')'",
    # {{rfv-term|enm|comered|section=comered}}
    "rfv-term": "parts[2]",
    # {{Runr-def|ᛗ}}
    "Runr-def": 'f"The Runic character {parts[1]}."',
    # {{sense|foo}}
    "sense": "f'{parenthesis(italic(parts[1]))} :'",
    # {{shitgibbon|en|arse|muncher}}
    "shitgibbon": 'f"Shitgibbon compound of {italic(parts[2])} + {italic(parts[3])}"',
    # {{small|(kraken)}}
    "small": "small(parts[1])",
    # {{smallcaps|ce}}
    "smallcaps": "small_caps(parts[1])",
    # {{speciesabbrev|C|difficile||la}}
    "speciesabbrev": "f'Used, in context, to shorten the name and simplify the pronunciation of a species name with a generic name beginning with {parts[1]} and a specific epithet of {parts[2]}.'",
    # {{specieslite|Io (Asteraceae)|''Io'' (Asteraceae)}}
    "specieslite": "f'{parts[-1]} on Wikispecies.'",
    # {{sqbrace|a}}
    "sqbrace": "f'[{parts[1]}]'",
    # {{station code|Airport station (MTR)|Airport|Hong Kong}}
    "station code": 'f"<i>(rail transport) The station code of</i> <b>{parts[2] or parts[1]}</b> <i>in {parts[3]}</i>."',
    # {{sub|KI}}
    "sub": "subscript(parts[1])",
    # {{syc-root|ܪ ܩ ܥ}}
    "syc-root": "parts[-1]",
    # {{t|mi|pōhutukawa}}
    "t": "parts[-1]",
    # {{taxfmt|Gadus macrocephalus|species|ver=170710}}
    "taxfmt": "italic(parts[1])",
    # {{tooltip|binding -- here, used in the sense of 'putting (a person) under definite (legal) obligations|[[binding]]}}
    "tooltip": "parts[-1]",
    # {{trademark erosion|en|Zamboni|Frank J. Zamboni & Co. Inc.}}
    "trademark erosion": "f'<i>{parts[2]}</i> was originally (and may still be) a trademark of {parts[3]}. Its use in the general sense is an example of trademark erosion.'",
    # {{wsource|Pro Sexto Roscio Amerino|lang=la}}
    "wsource": "[part for part in parts[1:] if '=' not in part][-1]",
}
templates_multi["angbr"] = templates_multi["IPAfont"]
templates_multi["angbr IPA"] = templates_multi["IPAfont"]
templates_multi["brackets"] = templates_multi["sqbrace"]
templates_multi["colour panel"] = templates_multi["color panel"]
templates_multi["datedef"] = templates_multi["defdate"]
templates_multi["def-date"] = templates_multi["defdate"]
templates_multi["defdt"] = templates_multi["defdate"]
templates_multi["enPRchar"] = templates_multi["small"]
templates_multi["g"] = templates_multi["gloss"]
templates_multi["gl"] = templates_multi["gloss"]
templates_multi["gloss-lite"] = templates_multi["gloss"]
templates_multi["lg"] = templates_multi["glossary"]
templates_multi["IPAlink"] = templates_multi["IPAfont"]
templates_multi["m-g"] = templates_multi["mention-gloss"]
templates_multi["monospace"] = templates_multi["mono"]
templates_multi["nom"] = templates_multi["nominalization"]
templates_multi["n-g"] = templates_multi["non-gloss"]
templates_multi["n-g-lite"] = templates_multi["non-gloss"]
templates_multi["ng"] = templates_multi["non-gloss"]
templates_multi["ng-lite"] = templates_multi["non-gloss"]
templates_multi["ngd"] = templates_multi["non-gloss"]
templates_multi["non gloss"] = templates_multi["non-gloss"]
templates_multi["non-gloss definition"] = templates_multi["non-gloss"]
templates_multi["non gloss definition"] = templates_multi["non-gloss"]
templates_multi["orth"] = templates_multi["orthography"]
templates_multi["q"] = templates_multi["qualifier"]
templates_multi["q-lite"] = templates_multi["qualifier"]
templates_multi["qf"] = templates_multi["qualifier"]
templates_multi["qua"] = templates_multi["qualifier"]
templates_multi["qual"] = templates_multi["qualifier"]
templates_multi["qualifier-lite"] = templates_multi["qualifier"]
templates_multi["s"] = templates_multi["sense"]
templates_multi["small caps"] = templates_multi["smallcaps"]
templates_multi["smc"] = templates_multi["smallcaps"]
templates_multi["sqb"] = templates_multi["sqbrace"]
templates_multi["staco"] = templates_multi["station code"]
templates_multi["taxlink"] = templates_multi["taxfmt"]
templates_multi["taxlink2"] = templates_multi["taxfmt"]
templates_multi["taxlinknew"] = templates_multi["taxfmt"]
templates_multi["upright"] = templates_multi["noitalic"]

# Templates that will be completed/replaced using custom text.
templates_other = {
    "2022 SI prefixes": "Coined by Richard J. C. Brown and adopted by the General Conference on Weights and Measures in 2022 as an expansion to the metric prefixes beyond 10<sup>±24</sup>.<br/><br/>Some popular unofficial terms already in use were <b>hella-</b>, <b>bronto-</b> and <b>xenna-</b>, but terms beginning with the same letters as existing prefixes were considered undesirable, as were as those beginning with common scientific letters such as <b>b</b> or <b>x</b>. Richard J. C. Brown suggested that the new terms begin with <b>r</b> and <b>q</b>, due to their rarity as unit symbols, and that the trends followed by the other prefixes be continued: that they be based on Latin or Greek; that large prefixes end with <b>-a</b> and small prefixes end with <b>-o</b>; that they should be in corresponding large and small pairs; and that the first letters of each prefix should be in reverse alphabetical order (as has been the case for the newer prefixes). He therefore suggested <i>ronna-</i> and <i>ronto-</i> (evoking Ancient Greek ἐννέα (<i>ennéa</i>) and Latin <i>novem</i> (“nine”)), and <i>quecca-</i> and <i>quecto-</i> (evoking Ancient Greek δέκα (<i>déka</i>) and Latin <i>decem</i> (“ten”)), because as 10<sup>27</sup> and 10<sup>30</sup> when written have nine and ten groups of zeroes, respectively. These were adopted, with <i>quecca-</i> changed to <i>quetta-</i>.",
    "'": "'",
    "--": "&nbsp;—",
    "-a-o-x": "The gender-neutral suffix <i>-x</i> replaces the gendered suffixes <i>-a/i> and <i>-o</i>.",
    "-a-o-@": "The at-sign (@) resembles both the feminine ending/element <i>a</i> and the masculine <i>o</i>.",
    "-a-us-x": "The gender-neutral suffix <i>-x</i> replaces the gendered Latinate suffixes <i>-us</i> and <i>-a</i>.",
    "-a-o-e": "The gender-neutral suffix <i>-e</i> replaces the gendered suffixes <i>-a</i> and <i>-o</i>.",
    "=": "=",
    ",": ",",
    "Brai-ety": "Invented by Louis Braille, braille cells were arranged in numerical order and assigned to the letters of the French alphabet. Most braille alphabets follow this assignment for the 26 letters of the basic Latin alphabet or, in non-Latin scripts, for the transliterations of those letters. In such alphabets, the first ten braille letters (the first decade: ⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚) are assigned to the Latin letters A to J and to the digits 1 to 9 and 0. (Apart from '2', the even digits all have three dots: ⠃⠙⠋⠓⠚.)<br/><br/>The letters of the first decade are those cells with at least one dot in the top row and at least one in the left column, but none in the bottom row.  The next decade repeat the pattern with the addition of a dot at the lower left, the third decade with two dots in the bottom row, and the fourth with a dot on the bottom right. The fifth decade is like the first, but shifted downward one row. The first decade is supplemented by the two characters with dots in the right column and none in the bottom row, and that supplement is propagated to the other decades using the generation rules above. Finally, there are four characters with no dots in the top two rows. Many languages that use braille letters beyond the 26 of the basic Latin alphabet follow an approximation of the English or French values for additional letters.",
    "corruption": "corruption",
    "epi-def": "<i>Used as a specific epithet</i>",
    "genericized trademark": "Genericized trademark",
    "grc-ark": "Arcadocypriot",
    "grc-att": "Attic",
    "grc-ion": "Ionic",
    "internationalism": "Internationalism",
    "LR": "\u200e",
    "nbsp": "&nbsp;",
    "mdash": "&mdash;",
    "ndash": "&ndash;",
    "pre-Germanic": "pre-Germanic",
    "sic": "<sup>[<i>sic</i>]</sup>",
}
templates_other["en dash"] = templates_other["ndash"]
templates_other["Genericized trademark"] = templates_other["genericized trademark"]


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "en")
    []
    >>> find_genders("{{taxoninfl|i=1|g=f}}", "en")
    ['f']
    """
    pattern = re.compile(r"{taxoninfl\|(?:i=\d+\|)?g=(\w+).*")
    return unique(flatten(pattern.findall(code)))


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
    return unique(flatten(pattern.findall(code)))


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """Will be call in utils.py::transform() when all template handlers were not used."""

    from .. import defaults
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        text = render_template(word, template)
        if tpl == "xlit" and not text and all_templates is not None:
            all_templates.append((f"{tpl}:{parts[0]}", word, "missed"))
        return text

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


# https://en.wiktionary.org/wiki/Wiktionary:Random_page
random_word_url = "https://en.wiktionary.org/wiki/Special:RandomInCategory/English_lemmas#English"


def adjust_wikicode(code: str, locale: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode('{| class="floatright"\\n|-\\n| {{PIE word|en|h₁eǵʰs}}\\n| {{PIE word|en|ḱóm}}\\n|}', "en")
    ''
    >>> adjust_wikicode('{| class="floatright"\\n|-\\n| {{PIE word|en|h₁eǵʰs}}\\n| {{PIE word|en|ḱóm}}\\n|}{{root|en|ine-pro|*(s)ker-|id=cut|*h₃reǵ-}}', "en")
    '{{root|en|ine-pro|*(s)ker-|id=cut|*h₃reǵ-}}'
    >>> adjust_wikicode("<math>\\\\frac{|AP|}{|BP|} = \\\\frac{|AC|}{|BC|}</math>", "en")
    '<math>\\\\frac{|AP|}{|BP|} = \\\\frac{|AC|}{|BC|}</math>'
    """
    # Remove tables (cf issue #2073)
    code = re.sub(r"^\{\|.*?\|\}", "", code, flags=re.DOTALL | re.MULTILINE)

    return code
