"""Utilities for internal use."""

from __future__ import annotations

import logging
import os
import re
from collections import defaultdict
from functools import cache, partial
from pathlib import Path
from typing import TYPE_CHECKING

import regex
import wikitextparser

from . import constants, context, lang, part_of_speech, svg
from .hiero_utils import render_hiero

if TYPE_CHECKING:
    from collections.abc import Callable

KEEP_UNFINISHED = os.getenv("KEEP_UNFINISHED", "0") == "1"

log = logging.getLogger(__name__)


def setup_logging(lang_src: str, lang_dst: str, file_mode: str = "a") -> Path:
    log_dir = Path("logs") / lang_dst
    log_dir.mkdir(exist_ok=True, parents=True)
    log_file = log_dir / f"{lang_src}.log"
    logging.basicConfig(
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=log_file,
        filemode=file_mode,
        force=True,
        format="%(asctime)s %(levelname)s:%(name)s:%(process)d %(message)s",
        level=logging.INFO,
    )
    return log_file


def check_for_templates_status(templates_status: list[tuple[str, str]]) -> bool:
    skipped: set[str] = set()

    for word, status in templates_status:
        if status == "skipped" and word not in skipped:
            log.warning("Skipped: %r", word)
            skipped.add(word)

    return bool(skipped)


def convert_gender(genders: list[str]) -> str:
    """Return the HTML code to include for gender(s) of a word."""
    if not genders:
        return ""
    genders = [f"<i>{gender}</i>" for gender in genders]
    return f" {', '.join(genders)}."


def convert_pronunciation(pronunciations: list[str]) -> str:
    """Return the HTML code to include for pronunciation(s) of a word."""
    return f" {', '.join(pronunciations)}" if pronunciations else ""


def flatten(seq: list[str]) -> list[str]:
    """
    Flatten non-empty items from *seq*.

    >>> flatten(["a", ("b", "", "c"), ["d"]])
    ['a', 'b', 'c', 'd']
    """
    res: list[str] = []
    for item in seq:
        if isinstance(item, list | tuple):
            res.extend(sitem for sitem in item if sitem)
        elif item:
            res.append(item)
    return res


def unique(seq: list[str]) -> list[str]:
    """
    Return *seq* without duplicates.

    >>> unique(["foo", "foo"])
    ['foo']
    """
    res: list[str] = []
    for item in seq:
        if item not in res:
            res.append(item)
    return res


def get_random_word(locale: str) -> str:
    """Retrieve a random word."""
    url = lang.random_word_url[locale]

    while True:
        with constants.SESSION.get(url) as req:
            req.raise_for_status()
            if match := re.findall(r'<span class="mw-page-title-main">([^<]+)</span>', req.text):
                word: str = match[0]
                if ":" not in word and "/" not in word:
                    log.info(f"Got random: {word!r}")
                    break
                log.info(f"Got {word=}, trying a new one instead ...")
            log.info("Got no match, trying again ...")

    if "CI" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "ab") as fh:
            fh.write(f"word={word}\n".encode())

    return word


def guess_lang_origin(locale: str) -> str:
    """
    Determine the lang origin from a locale.

    >>> guess_lang_origin("fr")
    'fr'
    >>> guess_lang_origin("fro")
    'fr'
    >>> guess_lang_origin("fr:it")
    'fr'
    >>> guess_lang_origin("it:fr")
    'it'
    """
    if ":" in locale:
        # `fr:fro` → source is FR
        return locale.lower().split(":", 1)[0]
    return constants.LOCALE_ORIGIN.get(locale, locale)


def guess_locales(locale: str, *, use_log: bool = True) -> tuple[str, str]:
    """
    >>> guess_locales("fr")
    ('fr', 'fr')
    >>> guess_locales("fro")
    ('fr', 'fro')
    >>> guess_locales("fr:fro")
    ('fr', 'fro')
    >>> guess_locales("fr:it")
    ('fr', 'it')
    >>> guess_locales("it:fr")
    ('it', 'fr')
    """
    if ":" in locale:
        # Example with "fr:fro" → source is FR, destination is FRO
        # because FRO is part of the FR Wiktionary
        lang_src, lang_dst = locale.split(":", 1)
    else:
        lang_src = lang_dst = locale

    lang_src = guess_lang_origin(lang_src)

    if use_log:
        log.info(
            "Determined source lang %r, and destination lang %r, from %s",
            lang_src,
            lang_dst,
            f"{locale=}",
        )

    return lang_src, lang_dst


@cache
def format_pos(locale: str, value: str) -> str:
    """Properly format the part of speech (POS).

    >>> format_pos("da", "{{pers-pronom 1}}")
    'Pronomen'
    >>> format_pos("da", "formelt subjekt")
    'Formelt Subjekt'
    >>> format_pos("da", "verb")
    'Verbum'
    >>> format_pos("da", "verbum")
    'Verbum'

    >>> format_pos("de", "substantiv")
    'Substantiv'
    >>> format_pos("de", "substantiv/wortverbindung/redewendung")
    'Substantiv'

    >>> format_pos("el", "{{έκφραση|el}}")
    'Έκφραση'
    >>> format_pos("el", "έκφραση")
    'Έκφραση'

    >>> format_pos("en", "proper noun 1")
    'Proper Noun'
    >>> format_pos("en", "proper noun")
    'Proper Noun'

    >>> format_pos("eo", "{{signifoj}}")
    'Signifo'
    >>> format_pos("eo", "{{vortospeco|adverbo, vortgrupo|eo}}")
    'Adverbo'
    >>> format_pos("eo", "signifo")
    'Signifo'

    >>> format_pos("es", "{{verbo transitivo|es|terciopersonal}}")
    'Verbo'
    >>> format_pos("es", "{{verbo|es|terciopersonal}}")
    'Verbo'
    >>> format_pos("es", "verbo transitivo")
    'Verbo'
    >>> format_pos("es", "verbo")
    'Verbo'

    >>> format_pos("fr", "{{s|lettre|fr}}")
    'Lettre'
    >>> format_pos("fr", "adjectif démonstratif")
    'Adjectif'
    >>> format_pos("fr", "lettre")
    'Lettre'

    >>> format_pos("it", "{{loc nom}}")
    'Nome'
    >>> format_pos("it", "{{nome}}")
    'Nome'
    >>> format_pos("it", "nome")
    'Nome'

    >>> format_pos("no", "verb 1")
    'Verb'
    >>> format_pos("no", "egennavn, toponym")
    'Egennavn'
    >>> format_pos("no", "verb")
    'Verb'

    >>> format_pos("pt", "substantivo1")
    'Substantivo'
    >>> format_pos("pt", "substantivo 1")
    'Substantivo'
    >>> format_pos("pt", "substantivo²")
    'Substantivo'
    >>> format_pos("pt", "Substantivo")
    'Substantivo'
    >>> format_pos("pt", "substantivo <small>''Feminino''</small>")
    'Substantivo'
    >>> format_pos("pt", "{{locução substantiva|pt}}<sup><small>2</small></sup>")
    'Locução'
    >>> format_pos("pt", "pronome pessoal")
    'Pronome'
    >>> format_pos("pt", "verbo")
    'Verbo'
    >>> format_pos("pt", "verbos derivados")
    'Verbo'

    >>> format_pos("ro", "{{verb auxiliar}}")
    'Verb'
    >>> format_pos("ro", "verb")
    'Verb'

    >>> format_pos("zh", "發音 1")
    '發音'
    >>> format_pos("zh", "發音1")
    '發音'
    >>> format_pos("zh", "讀音①")
    '讀音'
    """
    for pattern in part_of_speech.PATTERNS.get(locale, []):
        value = pattern(r"\1", value)
    value = part_of_speech.MERGE.get(locale, {}).get(value, value)
    return value.strip().title()


@cache
def is_cyrillic(char: str) -> bool:
    return (
        "\u0400" <= char <= "\u04ff"  # Cyrillic
        or "\u0500" <= char <= "\u052f"  # Cyrillic Supplement
        or "\u2de0" <= char <= "\u2dff"  # Cyrillic Extended-A
        or "\ua640" <= char <= "\ua69f"  # Cyrillic Extended-B
        or "\u1c80" <= char <= "\u1c8f"  # Cyrillic Extended-C
    )


@cache
def is_japanese_hiragana(char: str) -> bool:
    return "\u3040" <= char <= "\u30ff"


@cache
def is_japanese_or_chinese(char: str) -> bool:
    return (
        "\u30ff" <= char <= "\u4dbf"  # Japanese
        or "\u4e00" <= char <= "\u9fff"  # Chinese
    )


@cache
def guess_prefix(word: str, *, locale: str = "") -> str:
    """Determine the word prefix for the given *word*.

    Inspiration: me ᕦ(ò_óˇ)ᕤ  <-- aka BoboTiG ^^
    Inspiration: https://pgaskin.net/dictutil/dicthtml/prefixes.html
    Inspiration: https://github.com/pettarin/penelope/blob/v3.1.3/penelope/prefix_kobo.py#L16
    Inspiration: https://github.com/cessen/kobo_jp_dict/blob/2f14c08dbd6e5dfb7f3bc95bace6ecead3a8ddb5/src/kobo.rs#L183 (for Japanese support)

    Converted from https://github.com/pgaskin/dictutil/blob/v0.3.2/kobodict/util.go#L44.

    Note: for words like "°GL", the Kobo will first check "11.html" and then "gl.html",
          so to speed-up the lookup, let's store such words into "11.html".

    Here are some debug logs to help understand what Kobo does:

        (dictionary.debug) got alternative search terms: "°GL", "°gl", "GL" for word "°GL"
        (ui.debug) static QByteArray Unzipper::extractFile() "/mnt/onboard/.kobo/dict/dicthtml-fr.zip", "11.html")

        (dictionary.debug) got alternative search terms: "X temps", "x temps", "X TEMPS", "Xtemps" for word "X temps"
        (ui.debug) static QByteArray Unzipper::extractFile("/mnt/onboard/.kobo/dict/dicthtml-fr.zip", "xa.html")

        (dictionary.debug) got alternative search terms: "A/cm2", "a/cm2", "A/CM2", "Acm2" for word "A/cm2"
        (ui.debug) static QByteArray Unzipper::extractFile("/mnt/onboard/.kobo/dict/dicthtml-fr.zip", "11.html")

        (dictionary.debug) got alternative search terms: ".vi", ".VI", "vi" for word ".vi"
        (ui.debug) static QByteArray Unzipper::extractFile("/mnt/onboard/.kobo/dict/dicthtml-fr.zip", "11.html")

        (dictionary.debug) HtmlForJapanese:  "レ"  (originally:  "レ" ) => prefix:  "レ"
        (dictionary.debug) HtmlForJapanese:  "レ"  => In prefix file:  "レ"
        (dictionary.debug) SearchForJapaneseWordInHtml: => index:  "レ" Regex:  "(<a name="レ" />.*</w>)"
        (dictionary.debug) got alternative search terms:  ("レ")  for word:  "レ"
        (dictionary.debug) SearchForJapaneseWordInHtml: => index:  "レ" Regex:  "(<a name="レ" />.*</w>)"

        (dictionary.debug) HtmlForJapanese:  "レイモン"  (originally:  "レイモン" ) => prefix:  "レイ"
        (dictionary.debug) HtmlForJapanese:  "レイモン"  => In prefix file:  "レイ"
        (dictionary.debug) SearchForJapaneseWordInHtml: => index:  "レイモン" Regex:  "(<a name="レイモン" />.*</w>)"
        (dictionary.debug) got alternative search terms:  ("レイモン")  for word:  "レイモン"
        (dictionary.debug) SearchForJapaneseWordInHtml: => index:  "レイプ" Regex:  "(<a name="レイプ" />.*</w>)

        (dictionary.debug) HtmlForJapanese:  "ハ"  (originally:  "は" ) => prefix:  "ハ"
        (dictionary.debug) HtmlForJapanese:  "は"  => In prefix file:  "ハ"
        (dictionary.debug) SearchForJapaneseWordInHtml: => index:  "ハ" Regex:  "(<a name="ハ" />.*</w>)"

        >>> guess_prefix("test")
        'te'
        >>> guess_prefix("a-")
        '11'
        >>> guess_prefix("-an")
        '11'
        >>> guess_prefix("GB")
        'gb'
        >>> guess_prefix("a")
        'aa'
        >>> guess_prefix("aa")
        'aa'
        >>> guess_prefix("aaa")
        'aa'
        >>> guess_prefix("Èe")
        'èe'
        >>> guess_prefix("Ȅe")
        'ȅe'
        >>> guess_prefix("eȄ")
        'eȅ'
        >>> guess_prefix("Ȅ!")
        '11'
        >>> guess_prefix("ébahir")
        'éb'
        >>> guess_prefix("kébab")
        'ké'
        >>> guess_prefix("aérer")
        'aé'
        >>> guess_prefix("living-room")
        'li'
        >>> guess_prefix("multiple words")
        'mu'
        >>> guess_prefix("àççèñts")
        'àç'
        >>> guess_prefix("à")
        'àa'
        >>> guess_prefix("a1")
        '11'
        >>> guess_prefix("ô")
        'ôa'
        >>> guess_prefix("ç")
        'ça'
        >>> guess_prefix("")
        '11'
        >>> guess_prefix(" ")
        '11'
        >>> guess_prefix(" x")
        'xa'
        >>> guess_prefix("x ")
        'xa'
        >>> guess_prefix(" xx")
        'xa'
        >>> guess_prefix(" ")
        '11'
        >>> guess_prefix("  ")
        '11'
        >>> guess_prefix("   ")
        '11'
        >>> guess_prefix("\t\t")
        '11'
        >>> guess_prefix("\t\t\t")
        '11'
        >>> guess_prefix("  x")
        '11'
        >>> guess_prefix("  xy")
        '11'
        >>> guess_prefix("  xyz")
        '11'
        >>> guess_prefix("x z")
        'xa'
        >>> guess_prefix(" 123")
        '11'
        >>> guess_prefix("42")
        '11'
        >>> guess_prefix("x 23")
        'xa'
        >>> guess_prefix("д")
        'д'
        >>> guess_prefix(" д")
        'д'
        >>> guess_prefix("д ")
        'д'
        >>> guess_prefix(" дд")
        'д'
        >>> guess_prefix("aд")
        'aд'
        >>> guess_prefix("дa")
        'дa'
        >>> guess_prefix("aдa")
        'aд'
        >>> guess_prefix("дaд")
        'дa'
        >>> guess_prefix("未未")
        '未未'
        >>> guess_prefix("未")
        '未a'
        >>> guess_prefix("  未")
        '11'
        >>> guess_prefix(" 未")
        '未a'
        >>> guess_prefix("x未")
        'x未'
        >>> guess_prefix("未x")
        '未x'
        >>> guess_prefix("xy未")
        'xy'
        >>> guess_prefix("还没")
        '还没'
        >>> guess_prefix(".vi")
        '11'
        >>> guess_prefix("/aba")
        '11'
        >>> guess_prefix("a/b")
        '11'
        >>> guess_prefix("’alif")
        '11'
        >>> guess_prefix("°GL")
        '11'
        >>> guess_prefix("وهيبة")
        'وه'
        >>> guess_prefix("!")
        '11'
        >>> guess_prefix("!!")
        '11'
        >>> guess_prefix("!!!")
        '11'
        >>> guess_prefix("x!")
        '11'
        >>> guess_prefix("x!!")
        '11'
        >>> guess_prefix("xx!")
        'xx'
        >>> guess_prefix("xxx!")
        'xx'
        >>> guess_prefix("  !")
        '11'
        >>> guess_prefix(" !!")
        '11'
        >>> guess_prefix(" !!!")
        '11'
        >>> guess_prefix(" !")
        '11'
        >>> guess_prefix("  !!")
        '11'
        >>> guess_prefix("   !!!")
        '11'
        >>> guess_prefix(" x!")
        'xa'
        >>> guess_prefix(" x!!")
        'xa'
        >>> guess_prefix(" xx!")
        'xa'
        >>> guess_prefix(" xxx!")
        'xa'
        >>> guess_prefix("x\\x00y")
        'xa'
        >>> guess_prefix("\\x00xy")
        '11'

        Past problematic cases:

        >>> guess_prefix("İslahiye")
        'is'
        >>> guess_prefix("б/а")
        ''
        >>> guess_prefix("б-p")
        'б-'

        # Japanese from non-Japaense dictionary:

        >>> guess_prefix("阪")
        '阪a'
        >>> guess_prefix("大阪")
        '大阪'
        >>> guess_prefix("長すぎる")
        '長す'
        >>> guess_prefix("の人気が高いことはもちろん若い女性からも「")
        'の人'
        >>> guess_prefix(" 】")
        '11'
        >>> guess_prefix("あ")
        'あa'
        >>> guess_prefix("あかつき")
        'あか'
        >>> guess_prefix("は")
        'はa'
        >>> guess_prefix("ア")
        'アa'
        >>> guess_prefix("アカツキ")
        'アカ'
        >>> guess_prefix("日")
        '日a'
        >>> guess_prefix("日大本")
        '日大'

        #
        # Cases for Japanese dictionary.
        #

        # Chinese:

        >>> guess_prefix("未未", locale="ja")
        '未'
        >>> guess_prefix("未", locale="ja")
        '未'
        >>> guess_prefix("  未", locale="ja")
        '11'
        >>> guess_prefix(" 未", locale="ja")
        '未'
        >>> guess_prefix("x未", locale="ja")
        'x未'
        >>> guess_prefix("未x", locale="ja")
        '未'
        >>> guess_prefix("还没", locale="ja")
        '还'

        # Japanese:

        >>> guess_prefix("阪", locale="ja")
        '阪'
        >>> guess_prefix("大阪", locale="ja")
        '大'
        >>> guess_prefix("長すぎる", locale="ja")
        '長'
        >>> guess_prefix("の人気が高いことはもちろん若い女性からも「", locale="ja")
        'の人'
        >>> guess_prefix(" 】", locale="ja")
        '11'
        >>> guess_prefix("あ", locale="ja")
        'あ'
        >>> guess_prefix("あかつき", locale="ja")
        'あか'
        >>> guess_prefix("は", locale="ja")
        'は'
        >>> guess_prefix("ア", locale="ja")
        'ア'
        >>> guess_prefix("アカツキ", locale="ja")
        'アカ'
        >>> guess_prefix("日", locale="ja")
        '日'
        >>> guess_prefix("日大本", locale="ja")
        '日'
    """
    if "\x00" in (prefix := word):
        prefix = prefix.split("\x00", 1)[0]

    if len(prefix) > 2:
        prefix = prefix[:2]
    prefix = prefix.strip()

    # Special lowercasing: handle Turkish 'İ' (U+0130) to 'i'.
    # Turkish 'İ' (U+0130) lowercases to 'i̇' (i + combining dot above), but Kobo and Go convert it to 'i'.
    # So we manually convert 'İ' to 'i'.
    if not (prefix := "".join("i" if char == "\u0130" else char.lower() for char in prefix)):
        return "11"

    if is_cyrillic(prefix[0]):
        return "" if prefix[-1] == "/" else prefix

    if locale == "ja":
        if is_japanese_hiragana(prefix[0]):
            return prefix

        if is_japanese_or_chinese(prefix[0]):
            return prefix[0]

    if len(prefix) < 2:
        prefix += "a"

    return prefix if prefix.isalpha() else "11"


def clean(text: str) -> str:
    r"""Cleans up the provided Wikicode.
    Removes templates, tables, parser hooks, magic words, HTML tags and file embeds.
    Keeps links.
    Source: https://github.com/macbre/mediawiki-dump/blob/3f1553a/mediawiki_dump/tokenizer.py#L8

        >>> clean(r"<math>x \in ]x_0 - \epsilon, x_0[</math> och <math>f(x) > f(x_0)</math> för alla <math>x \in ]x_0, x_0 + \epsilon[</math>")
        '<math>x \\in ]x_0 - \\epsilon, x_0[</math> och <math>f(x) > f(x_0)</math> för alla <math>x \\in ]x_0, x_0 + \\epsilon[</math>'
        >>> clean(r'<math style="vertical-align:+0%;">x \in ]x_0 - \epsilon, x_0[</math>')
        '<math>x \\in ]x_0 - \\epsilon, x_0[</math>'
        >>> clean(r"<math> \epsilon > 0 </math>")
        '<math> \\epsilon > 0 </math>'
        >>> clean(r"<math> d(x_k, x_m) < \epsilon </math>")
        '<math> d(x_k, x_m) < \\epsilon </math>'

        >>> clean("{{Lien web|url=http://stella.atilf.fr/few/|titre=Französisches Etymologisches Wörterbuch}}")
        '{{Lien web|url=http://stella.atilf.fr/few/|titre=Französisches Etymologisches Wörterbuch}}'
        >>> clean("d'<nowiki/>''Arvernus'', surnom ethnique, ou composé d'''are''")
        "d'<i>Arvernus</i>, surnom ethnique, ou composé d'<i>are</i>"

        >>> clean("")
        ''
        >>> clean("<span style='color:black'>[[♣]]</span>")
        "<span style='color:black'>♣</span>"
        >>> clean("''italic''")
        '<i>italic</i>'
        >>> clean("'''strong'''")
        '<b>strong</b>'
        >>> clean("''italic and '''strong'''''")
        '<i>italic and <b>strong</b></i>'
        >>> clean("'''strong and ''italic'''''")
        '<b>strong and <i>italic</b></i>'
        >>> clean("'''''Parer à'''''")
        '<i><b>Parer à</b></i>'
        >>> clean("''Contraction de [[préposition]] ''[[à]]'' et de l'[[article]] défini ''[[les]]'' .''")
        "<i>Contraction de préposition </i>à<i> et de l'article défini </i>les<i>.</i>"
        >>> clean("'''Contraction de [[préposition]] '''[[à]]''' et de l'[[article]] défini '''[[les]]''' .'''")
        "<b>Contraction de préposition </b>à<b> et de l'article défini </b>les<b>.</b>"

        >>> clean("[[{{nom langue|gcr}}]]")
        '{{nom langue|gcr}}'
        >>> clean("[[a|b]]")
        'b'
        >>> clean("[[-au|-[e]au]]")
        '-[e]au'
        >>> clean("[[Stó:lō]]")
        'Stó:lō'
        >>> clean("[[Annexe:Principales puissances de 10|10{{e|&minus;6}}]] [[gray#fr-nom|gray]]")
        '10{{e|&minus;6}} gray'

        >>> clean("[http://www.bertrange.fr/bienvenue/historique/]")
        ''
        >>> clean("[https://fr.wikipedia.org/wiki/Gerardus_Johannes_Mulder Gerardus Johannes Mulder]")
        'Gerardus Johannes Mulder'
        >>> clean("[//www.nps.gov/ande/historyculture/myth-shebang.htm the US National Park Service]")
        'the US National Park Service'
        >>> clean("<sup>[http://www.iupac.org/6612x2419.pdf]</sup> à la [[place]] en 1997<sup>[http://www.iupac.org/6912x2471.pdf]</sup>")
        'à la place en 1997'
        >>> clean("[[http://www.tv5monde.com/cms/chaine-francophone/lf/Merci-Professeur/p-17081-Une-peur-bleue.htm?episode=10 Voir aussi l’explication de Bernard Cerquiglini en images]]")
        ''

        >>> clean("<nowiki/>")
        ''
        >>> clean("<nowiki>«</nowiki>")
        '«'
        >>> clean("foo|anticuado por [[cerrojo]] e influido por [[fierro]] [http://books.google.es/books?id=or7_PqeALCMC&pg=PA21&dq=%22ferrojo%22]|yeah")
        'foo|anticuado por cerrojo e influido por fierro |yeah'
        >>> clean("<<country>>")
        'country'
        >>> clean("<<region/Middle East>>")
        '<<region/Middle East>>'

        >>> clean("__NOTOC__")
        ''
        >>> clean("A_____B, B_____A")
        'A_____B, B_____A'

        >>> clean("<gallery>\nImage: Hydra (creature).jpg|due idre minacciose\nImage: Hydre.jpg|idra minacciosa\nImage: Chateauneuf-Randon de Joyeuse.svg|d'oro, a tre pali d'azzurro; al capo di rosso caricato di tre idre minacciose del campo<br /></gallery>")
        ''

        >>> clean("<br />")
        '<br />'
        >>> clean("<br>")
        '<br>'
        >>> clean("<br/><br /><br>")
        '<br/>'
        >>> clean("{{code|html|<br />}}")
        '{{code|html|<br />}}'
        >>> clean("{{code|js|<br />}}")
        '{{code|js|<br />}}'

        >>> clean(" <")
        '<'
        >>> clean('<\\"')
        '<\\"'
        >>> clean('< \\"')
        '< \\"'
        >>> clean("< ")
        '&lt;'
        >>> clean(" < ")
        '&lt;'
        >>> clean(" >")
        '&gt;'
        >>> clean("> ")
        '>'
        >>> clean(" > ")
        '&gt;'
        >>> clean('\\">')
        '\\">'
        >>> clean('\\" >')
        '\\" >'
    """

    # Speed-up lookup
    sub = re.sub
    sub2 = regex.sub

    # <math style="bla" foo=bar>formula</math> → <math>formula</math>
    text = re.sub(r"<math\s+[^>]+>(.+?)</math>", r"<math>\1</math>", text)

    # Save <math> formulas to prevent altering them
    if formulas := re.findall(r"(<math>.+?</math>)", text):
        for idx, formula in enumerate(formulas):
            text = text.replace(formula, f"##math{idx}##")

    # Remove line breaks
    text = text.replace("\n", "")

    # HTML
    # Source: https://github.com/5j9/wikitextparser/blob/b24033b/wikitextparser/_wikitext.py#L83
    text = sub2(r"'''(\0*+[^'\n]++.*?)(?:''')", r"<b>\1</b>", text)
    # ''foo'' → <i>foo></i>
    text = sub2(r"''(\0*+[^'\n]++.*?)(?:'')", r"<i>\1</i>", text)
    # consecutive <br> → '<br/>'
    text = sub(r"(<br[^>]*/?>){2,}", "<br/>", text)

    # <nowiki/> → ''
    text = text.replace("<nowiki/>", "")
    # <nowiki>»</nowiki> → '»'
    text = sub("<nowiki>([^<]+)</nowiki>", r"\1", text)

    # <gallery>
    text = sub(r"<gallery>[\s\S]*?</gallery>", "", text)

    # Local links
    text = sub(r"\[\[([^|:\]]+)\]\]", r"\1", text)  # [[a]] → a

    # Links
    # Internal: [[{{a|b}}]] → {{a|b}}
    text = sub(r"\[\[({{[^}]+}})\]\]", r"\1", text)
    # Internal: [[a|b]] → b
    text = sub(r"\[\[[^|]+\|(.+?(?=\]\]))\]\]", r"\1", text)
    # External: [[http://example.com Some text]] → ''
    text = sub(r"\[\[https?://[^\s]+\s[^\]]+\]\]", "", text)
    # External: [http://example.com] → ''
    text = sub(r"\[https?://[^\s\]]+\]", "", text)
    # External: [http://example.com Some text] → 'Some text'
    text = sub(r"\[https?://[^\s]+\s([^\]]+)\]", r"\1", text)
    # External: [//example.com Some text] → 'Some text'
    text = sub(r"\[//[^\s]+\s([^\]]+)\]", r"\1", text)
    text = text.replace("[[", "").replace("]]", "")

    # Tables
    # {|foo..|}
    text = sub(r"{\|[^}]+\|}", "", text)

    # Headings
    # == a == → a
    text = sub(r"^=+\s?([^=]+)\s?=+", lambda matches: matches.group(1).strip(), text)

    # Lists
    text = sub(r"^\*+\s?", "", text)

    # Magic words
    text = sub(r"__[A-Z]+__", "", text)  # __TOC__

    # Remove extra quotes left
    text = text.replace("''", "")

    # Remove extra brackets left
    text = text.replace(" []", "")
    text = text.replace(" ]", "")

    # Remove empty HTML tags
    # <sup></sup> → ''
    text = sub(r"<([^>]+)></\1>", "", text)

    # Remove extra spaces
    text = sub(r"\s{2,}", " ", text)
    text = sub(r"\s{1,}\.", ".", text)

    # <<bar>> → foo
    text = sub(r"<<([^/>]+)>>", r"\1", text)
    # <<foo/bar>> → bar
    # text = sub(r"<<(?:[^/>]+)/([^>]+)>>", r"\1", text)

    # Convert single "< ", and " >" to HTML quotes
    text = re.sub(r'<[ ]+(?!\\")', "&lt; ", text)
    text = re.sub(r'(?<!\\")[ ]+>', " &gt;", text)

    # Restore math formulas
    for idx, formula in enumerate(formulas):
        text = text.replace(f"##math{idx}##", formula)

    return text.strip()


def process_templates(
    word: str,
    wikicode: str,
    locale: str,
    *,
    callback: Callable[[str], str] = clean,
    templates_status: list[tuple[str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    r"""Process all templates.

    It will also handle the <math> HTML tag as it is not part of the *clean()* function on purpose.

    >>> _ = context.reset("fr")
    >>> context.new_word("word")

    >>> process_templates("foo", "{{}}", "fr")
    '&lbrace;&lbrace;&rbrace;&rbrace;'
    >>> process_templates("foo", "{{unknown}}", "fr")
    ''
    >>> process_templates("foo", "{{!}}", "fr")
    '|'
    >>> process_templates("foo", "{{fchim|OH|2|{{!}}OH|2}}", "fr")  # TODO: this is wrong, `{{!}}` should be converted to `|`
    'OH<sub>2</sub><sub>OH</sub>2'
    >>> process_templates("EPR=ER", "{{fchim|ER{{=}}EPR}}", "fr")  # TODO: this is wrong, expecting `ER=EPR`
    ''

    >>> process_templates("octonion", " <math>V^n</math>", "fr")  # doctest: +ELLIPSIS
    '<svg ...'
    >>> process_templates("", r"<chem>C10H14N2O4</chem>", "fr") # doctest: +ELLIPSIS
    '<svg ...'
    >>> process_templates("test", r"<hiero>R11</hiero>", "fr")
    '<table class="mw-hiero-table mw-hiero-outer" dir="ltr" style=" border: 0; border-spacing: 0; font-size:1em;"><tr><td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;">\n<table class="mw-hiero-table" style="border: 0; border-spacing: 0; font-size:1em;"><tr>\n<td style="padding: 0; text-align: center; vertical-align: middle; font-size:1em;"><img src="data:image/gif;base64...'

    >>> process_templates("hasta", "<i>حتى</i>", "fr")
    'حتى'
    >>> process_templates("tasse", "<i>س tas'</i>", "fr")
    "س tas'"

    >>> process_templates("foo", "{{flexion|{{lien|terne|fr}}}}", "fr", variant_only=True)
    'terne'
    >>> process_templates("foo", "{{flexion|terne}}", "fr", variant_only=True)
    'terne'
    """
    # Clean-up the code
    if not (text := callback(wikicode)):
        return ""

    # Save <math> formulas to prevent altering them
    if formulas := re.findall(r"(<math>.+?</math>)", text):
        for idx, formula in enumerate(formulas):
            text = text.replace(formula, f"##math{idx}##")

    # {{foo}}
    # {{foo|bar}}
    # {{foo|{{bar}}|123}}
    # {{foo|{{bar|baz}}|123}}
    # {{foo|{{bar|lang|{{baz|args}}}}|123}}

    # Handle all templates
    last_template_idx = text.count("{{")
    current_template_idx = 0
    while templates := re.findall(r"({{[^{}]*}})", text):
        for tpl in templates:
            # Skip undesired templates
            if tpl.startswith(lang.templates_ignored[locale]):
                new_text = ""

            # `variant_only` is True only when:
            #   1. It is predefined;
            #   2. And it is the last template in nested templates.
            #      Example: [FR] `{{flexion|{{lien|foo}}}}` where:
            #          - `lien` should be handled normaly;
            #          - while `flexion` should be handled as variant-specific.
            elif variant_only and current_template_idx == last_template_idx - 1:
                new_text = transform_variant(word, tpl[2:-2], locale)

            # Expand the template
            else:
                new_text = clean(context.expand(tpl, locale))

            text = text.replace(tpl, new_text)

        current_template_idx += len(templates)

    sub = re.sub

    # Restore math formulas
    for idx, formula in enumerate(formulas):
        text = text.replace(f"##math{idx}##", formula)

    # Handle <chem>, <hiero>, and <math>, HTML tags
    for tag, func in [("chem", convert_chem), ("hiero", convert_hiero), ("math", convert_math)]:
        text = text.replace("&#92;", "\\")
        text = sub(rf"<{tag}>(.+?)</{tag}>", partial(func, word=word), text)
        if f"<{tag}>" in text or f"</{tag}>" in text:
            raise ValueError(f"Missed <{tag}> HTML tag in {word!r}") from None

    # Issue #584: move Arabic/Persian characters out of italic tags
    text = sub(r"<i>([^<]*[\u0627-\u064a]+[^<]*)</i>", r"\1", text)

    # Remove extra spaces (it happens when a template is ignored for instance)
    text = sub(r"\s{2,}", " ", text)
    text = sub(r"\s{1,}\.", ".", text)

    # Catch incorrect wikitext, likely to be fixed on the Wiktionary directly
    if not KEEP_UNFINISHED and (
        bool(context.get_errors())
        or f":{lang.module_trans[locale]}:" in text
        or f":{lang.template_trans[locale]}:" in text
        or "{{" in text
        or "}}" in text
        or "<h1>" in text
        or "<h2>" in text
        or "<h3>" in text
    ):
        if templates_status is not None:
            templates_status.append((word, "skipped"))
        return ""

    return text.strip()


def extract_keywords_from(parts: list[str]) -> defaultdict[str, str]:
    """
    Given a list of strings, extract strings containing an equal sign ("=").

    Return a *defaultdict(str)* with key=value extracted from the original list.

    The left part of the sign is used as the dict key and the right part as the value.
    When a string contains the sign, it is removed from the original list.

        >>> extract_keywords_from([])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo"])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "bar=baz"])
        defaultdict(<class 'str'>, {'bar': 'baz'})
        >>> extract_keywords_from(["foo", "bar=baz=ouf"])
        defaultdict(<class 'str'>, {'bar': 'baz=ouf'})
        >>> extract_keywords_from(["foo", "bar = baz=ouf"])
        defaultdict(<class 'str'>, {'bar': 'baz=ouf'})
        >>> extract_keywords_from(["foo", "<span style='font-variant:small-caps'>xix</span><sup>e</sup> s."])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "À partir du <span style='font-variant:small-caps'>xix</span><sup>e</sup> siècle"])
        defaultdict(<class 'str'>, {})
        >>> extract_keywords_from(["foo", "bar='baz'"])
        defaultdict(<class 'str'>, {'bar': "'baz'"})
    """
    data = defaultdict(str)
    for part in parts.copy():
        if "=" in part:
            key, value = part.split("=", 1)

            # Prevent splitting such parts:
            #   "<span style='font-variant:small-caps'>xix</span><sup>e</sup> s.".
            #   "À partir du <span style='font-variant:small-caps'>xix</span><sup>e</sup> siècle".
            if key.endswith("<span style"):
                continue

            data[key.strip()] = value.strip()
            parts.pop(parts.index(part))
    return data


def extract_relevant_sections(wikitext: str, locale: str) -> str:
    """Extract relevant sections for the chosen locale from a given wikitext."""
    level = lang.section_level[locale]
    equals = "=" * level

    interesting_sections_raw = []
    for section in lang.head_sections[locale]:
        interesting_sections_raw.extend([f"{equals}{section}", f"{equals} {section}"])
    interesting_sections = tuple(interesting_sections_raw)

    cleaned: list[str] = []
    in_expected_section = False
    for line in wikitext.splitlines():
        if not (line := line.strip()):
            continue
        if line.startswith(equals) and line[level] != "=":
            in_expected_section = line.lower().startswith(interesting_sections)
        if in_expected_section:
            cleaned.append(line)
    return "\n".join(cleaned) if cleaned else ""


def transform_variant(word: str, template: str, locale: str) -> str:
    parts_raw = template.split("|")
    parts = [p.strip().strip("\u200e") for p in parts_raw]
    tpl, *parts = parts

    if funcs := lang.variant_handlers[locale]:
        data = extract_keywords_from(parts)
        return funcs[tpl](tpl, parts, data, word)

    return ""


def render_formula(formula: str, *, cat: str = "tex", output_format: str = "svg") -> str:
    """
    Convert mathematic/chemical symbols to a SVG string.

    Technical details can be found on those websites:
        - https://en.wikipedia.org/api/rest_v1/#/Math
        - https://github.com/maxbuchan/viv/blob/d9dc1f95348b458e0251bcf908084f2e0b8baf1f/apps/mediawiki/htdocs/extensions/Math/math/texutil.ml#L513
        - https://github.com/wikimedia/restbase/blob/ecef17bda6f4efc0d6e187fb05b1eeb389bf7120/sys/mathoid.js#L33
        - https://phabricator.wikimedia.org/diffusion/GMAT/browse/master/lib/math.js
    """

    if cat == "chem":
        formula = f"\\ce{{{formula}}}"

    # 1. Get the formula hash (type can be tex, inline-tex, or chem)
    url_hash = constants.WIKIMEDIA_URL_MATH_CHECK.format(type=cat)
    with constants.SESSION.post(url_hash, json={"q": formula}) as req:
        req.raise_for_status()
        res = req.json()
        assert res["success"]
        formula_hash = req.headers["x-resource-location"]

    # 2. Get the rendered formula (format can be svg, mml, or png)
    url_render = constants.WIKIMEDIA_URL_MATH_RENDER.format(format=output_format, hash=formula_hash)
    with constants.SESSION.get(url_render) as req:
        req.raise_for_status()
        return req.text


def formula_to_svg(formula: str, *, cat: str = "tex") -> str:
    """Return an optimized SVG file as a string."""
    force = "FORCE_FORMULA_RENDERING" in os.environ
    if force or not (svg_raw := svg.get(formula)):
        svg_raw = render_formula(formula, cat=cat, output_format="svg")
        svg.set(formula, svg_raw)
    return svg.optimize(svg_raw)


def convert_chem(match: str | re.Match[str], word: str) -> str:
    """Convert chemistry symbols to a base64 encoded GIF file.

    >>> convert_chem("<chem>foo</chem>", "foo")
    '<chem>foo</chem>'
    """
    formula: str = (match.group(1) if isinstance(match, re.Match) else match).strip()
    if "<chem>" in formula or "</chem>" in formula:
        return formula
    try:
        return formula_to_svg(formula, cat="chem")
    except Exception:
        log.exception("<chem> ERROR with %r in [%s]", formula, word)
        return formula


def convert_hiero(match: str | re.Match[str], word: str) -> str:
    """Convert hieroglyph symbols to a base64 encoded GIF file."""
    expr: str = (match.group(1) if isinstance(match, re.Match) else match).strip()
    return expr if "<hiero>" in expr or "</hiero>" in expr else render_hiero(expr)


def convert_math(match: str | re.Match[str], word: str) -> str:
    """Convert mathematics symbols to a base64 encoded GIF file.

    >>> convert_math("<math>foo</math>", "foo")
    '<math>foo</math>'
    """
    formula: str = (match.group(1) if isinstance(match, re.Match) else match).strip()
    if "<math>" in formula or "</math>" in formula:
        return formula
    try:
        return formula_to_svg(formula)
    except Exception:
        log.exception("<math> ERROR with %r in [%s]", formula, word)
        return formula


def table2html(word: str, locale: str, table: wikitextparser.Table) -> str:
    phrase = "<table>"
    style_table = 'style="border: 1px solid black; border-collapse: collapse; font-size: inherit;"'
    style_td = 'style="border: 1px solid black; padding: 0.2em 0.4em;"'
    phrase = f"<table {style_table}>"
    for row in table.cells(span=False):
        phrase += "<tr>"
        for cell in row:
            tag = "th" if cell.is_header else "td"
            phrase += f"<{tag} {style_td}>{process_templates(word, cell.value, locale)}</{tag}>"
        phrase += "</tr>"
    phrase += "</table>"
    return phrase


def remove_parens(text: str) -> str:
    if "(" in text:
        # atlase(r)ne
        text = re.sub(r"(\w+)\b\((\w+)\)\b(\w+)", r"\1\2\3", text)
    if "(" in text:
        # atlas(ser)
        text = re.sub(r"(\w+)\b\((\w+)\)", r"\1\2", text)
    return text


def cleanup_rev_variant(form: str, *, rpl: set[str] | None = None, skip: set[str] | None = None) -> str:
    cleaned = remove_parens(form).replace("&nbsp;", " ")
    for replacement in rpl or []:
        cleaned = cleaned.replace(replacement, "")
    cleaned = cleaned.strip(" []()/")

    if " (" in cleaned:
        cleaned = cleaned.split(" (", 1)[0]

    if any(char in cleaned for char in "{|[]"):
        return ""

    if (to_skip := (skip or set())) and cleaned.lower() in to_skip:
        return ""

    return cleaned.strip()
