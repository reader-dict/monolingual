from collections.abc import Callable
from typing import Any
from unittest.mock import patch

import pytest
import responses
from requests.exceptions import RequestException
from requests.models import Response

from wikidict import check_word, utils
from wikidict.lang import random_word_url

# Word used in test_filter_html()
WORD = {
    "ca": "pelegrí",
    "de": "volley",
    "en": "42",
    "el": "σελοτέιπ",
    "es": "buena",
    "fr": "42",
    "it": "Upupidi",
    "pt": "-izar",
    "sv": "Benjamin",
}


@pytest.fixture
def craft_urls(html: Callable[[str, str], str], page: Callable[[str, str], str]) -> Callable[[str, str], str]:
    def _craft_urls(locale: str, word: str) -> str:
        responses.add(
            responses.GET,
            check_word.craft_url(word, locale, raw=True),
            body=page(word, locale),
        )
        responses.add(
            responses.GET,
            check_word.craft_url(word, locale),
            body=html(word, locale),
        )
        return word

    return _craft_urls


@pytest.fixture
def craft_urls_with_body() -> Callable[[str, str, str], str]:
    def _craft_urls(locale: str, word: str, body: str) -> str:
        responses.add(
            responses.GET,
            check_word.craft_url(word, locale, raw=True),
            body=body,
        )
        responses.add(
            responses.GET,
            check_word.craft_url(word, locale),
            body=body,
        )
        return word

    return _craft_urls


@responses.activate
def test_simple(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "42")
    assert check_word.main("fr", "42") == 0


@pytest.mark.webtest
def test_get_random_word() -> None:
    assert check_word.main("en", "") == 0


@responses.activate
def test_get_random_word_unwanted_word() -> None:
    url = random_word_url["en"]
    body = '<span class="mw-page-title-main">WORD</span>'
    word = "désiré"

    responses.add(responses.GET, url=url, body=body.replace("WORD", "Conjugaison:tchèque/srovnat"))
    responses.add(responses.GET, url=url, body=body.replace("WORD", "tchèque/srovnat"))
    responses.add(responses.GET, url=url, body=body.replace("WORD", word))
    assert utils.get_random_word("en") == word


@responses.activate
def test_etymology_list(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "bath")
    assert check_word.main("fr", "bath") == 0


@responses.activate
def test_sublist(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "éperon")
    assert check_word.main("fr", "éperon") == 0


@responses.activate
def test_subsublist(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "base")
    assert check_word.main("fr", "base") == 0


@responses.activate
def test_error(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "42")
    with patch.object(check_word, "contains", return_value=False):
        assert check_word.main("fr", "42") > 0
        assert check_word.check_word("42", "fr") > 0


@responses.activate
def test_no_definition_nor_etymology(craft_urls: Callable[[str, str], str]) -> None:
    craft_urls("fr", "vide")
    assert check_word.main("fr", "vide") == 0


@pytest.mark.parametrize(
    "locale, body, expected",
    [
        # CA - {{sense accepcions}}
        [
            "ca",
            '<i>a aquesta paraula li falten les accepcions o significats. Podeu <span class="plainlinks"><a class="external text" href="https://ca.wiktionary.org/w/index.php?title=pelegr%C3%AD&amp;action=edit">ajudar</a></span> el Viccionari incorporant-los</i>.',
            "",
        ],
        # CA - anchors
        [
            "ca",
            '<li>Una persona <a href="#Adjectiu">milionària</a>.</li>',
            "Unapersonamilionària.",
        ],
        # DE - star
        [
            "de",
            "<sup>☆</sup>",
            "",
        ],
        # DE - Internet Archive
        [
            "de",
            '<a rel="nofollow" class="external text" href="http://www.archive.org/stream/dasbuchhenochhrs00flemuoft/page/59/mode/1up">Internet&nbsp;Archive</a>',
            "",
        ],
        # DE - external links
        [
            "de",
            '<small class="noprint" title="Luther 2017 bei www.bibleserver.com"></small>',
            "",
        ],
        # DE - lang link in {{Üxx5}}
        [
            "de",
            '<a href="/w/index.php?title=grc:%E1%BC%80%CE%BD%CE%AE%CF%81&amp;action=edit&amp;redlink=1" class="new" title="grc:ἀνήρ (Seite nicht vorhanden)"><sup>→&nbsp;grc</sup>',
            "",
        ],
        # DE - other Wikis
        [
            "de",
            '<a href="https://en.wiktionary.org/wiki/Special:Search/volley" class="extiw" title="en:Special:Search/volley"><sup class="dewikttm">→&nbsp;en</sup></a>',
            "",
        ],
        # DE - Wikipedia: WP template
        [
            "de",
            '<a href="https://de.wikipedia.org/wiki/Datenkompression" class="extiw" title="w:Datenkompression"><sup>→&nbsp;WP</sup></a>',
            "",
        ],
        # DE - grey sup link
        [
            "de",
            '<sup style="color:slategray;">→&nbsp;grc</sup>',
            "",
        ],
        # EN - and other forms
        [
            "en",
            '<span title="doubt, doubten, dought, doughten, douti, douʒte, dut, duten, duti">and other forms</span>',
            "and other forms doubt, doubten, dought, doughten, douti, douʒte, dut, duten, duti",
        ],
        # EN - anchors
        [
            "en",
            '<a class="mw-jump-link" href="#mw-head">Jump to navigation</a>',
            "",
        ],
        # EN - WikiSpecies sup
        [
            "en",
            '<a href="/w/index.php?title=Teredo_navalis&amp;action=edit&amp;redlink=1" class="new" title="Teredo navalis (page does not exist)">Teredo navalis</a><sup><a href="https://en.wikipedia.org/wiki/Teredo_navalis" class="extiw" title="w:Teredo navalis">WP</a>&nbsp;<a href="https://species.wikimedia.org/wiki/Teredo_navalis" class="extiw" title="wikispecies:Teredo navalis">WSp</a>&nbsp;<a href="https://commons.wikimedia.org/wiki/Category:Teredo_navalis" class="extiw" title="commons:Category:Teredo navalis">Commons</a></sup>',
            "Teredonavalis",
        ],
        # EL - {{audio}} template
        [
            "el",
            '<span style="text-align:left;"><span class="ext-phonos"><span><a><span></span><span></span><span></span></a></span><sup><a>ⓘ</a></sup></span></span>&nbsp;<span><sup></sup></span>',
            "",
        ],
        # EL - documentation needed
        [
            "el",
            '<sup about="#mwt5" typeof="mw:Transclusion" id="mwDg" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;χρειάζεται τεκμηρίωση&quot;,&quot;href&quot;:&quot;./Πρότυπο:χρειάζεται_τεκμηρίωση&quot;},&quot;params&quot;:{},&quot;i&quot;:0}}]}">(<span style="color: red; --darkreader-inline-color: var(--darkreader-text-ff0000, #c54035);" data-darkreader-inline-color="">Χρειάζεται<span typeof="mw:Entity">&nbsp;</span>τεκμηρίωση…</span>)</sup><link rel="mw:PageProp/Category" href="./Κατηγορία:Σελίδες_για_τεκμηρίωση" about="#mwt5" id="mwDw">',
            "",
        ],
        # EL - Wikipedia link
        [
            "el",
            '<span style="background:#f7f7f7;" about="#mwt5" typeof="mw:Transclusion" id="mwDQ" data-mw="{&quot;parts&quot;:[{&quot;template&quot;:{&quot;target&quot;:{&quot;wt&quot;:&quot;ΒΠ&quot;,&quot;href&quot;:&quot;./Πρότυπο:ΒΠ&quot;},&quot;params&quot;:{&quot;0&quot;:{&quot;wt&quot;:&quot;-&quot;},&quot;1&quot;:{&quot;wt&quot;:&quot;Οργάνωση Χ&quot;},&quot;2&quot;:{&quot;wt&quot;:&quot;Οργάνωση Χ&quot;}},&quot;i&quot;:0}}]}"><a rel="mw:WikiLink/Interwiki" href="https://el.wikipedia.org/wiki/Οργάνωση%20Χ" title="w:Οργάνωση Χ" class="extiw">Οργάνωση Χ</a>  στη <span style="white-space:nowrap"><a rel="mw:WikiLink/Interwiki" href="https://el.wikipedia.org/wiki/Κύρια_Σελίδα" title="w:Κύρια Σελίδα" class="extiw"><span title="Λήμμα στη Βικιπαίδεια"> <span style="color:#000000;">Βικιπαίδεια<span typeof="mw:Entity">&nbsp;</span></span></span></a><span typeof="mw:File" data-mw="{&quot;caption&quot;:&quot;Λήμμα στη Βικιπαίδεια&quot;}"><a href="//el.wiktionary.org/wiki/w:Κύρια_Σελίδα" title="Λήμμα στη Βικιπαίδεια"><img alt="Λήμμα στη Βικιπαίδεια" resource="//el.wiktionary.org/wiki/Αρχείο:Wikipedia-logo-v2.svg" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/20px-Wikipedia-logo-v2.svg.png" decoding="async" data-file-width="103" data-file-height="94" data-file-type="drawing" height="14" width="15" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/40px-Wikipedia-logo-v2.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/40px-Wikipedia-logo-v2.svg.png 2x" class="mw-file-element"></a></span></span></span>',
            "",
        ],
        # ES - 2 Historia. --> (Historia)
        [
            "es",
            "<dl><dt>1 Finanzas.</dt></dl>",
            "1 (Finanzas):",
        ],
        # ES - 2 Coloquial: --> (Coloquial):
        [
            "es",
            "<dl><dt>2 Coloquial</dt></dl>",
            "2 (Coloquial): 2 Coloquial:",
        ],
        # ES
        [
            "es",
            "</dl><dl><dt>3 Coloquial</dt><dd>Úsase.</dd>",
            "3(Coloquial):Úsase.3Coloquial:Úsase.",
        ],
        # ES - cita requerida
        [
            "es",
            (
                '<sup>[<i><a href="/wiki/Ayuda:Tutorial_(Ten_en_cuenta)#Citando_tus_fuentes" class="mw-'
                'redirect" title="Ayuda:Tutorial (Ten en cuenta)">cita&nbsp;requerida</a></i>]</sup>'
            ),
            "",
        ],
        # ES - cite
        [
            "es",
            (
                '<a href="#cite_note-drae-1"><span class="corchete-llamada">[</span>1<span class="corchete-'
                'llamada">]</span></a>'
            ),
            "",
        ],
        # ES - color
        [
            "es",
            (
                '<span style="color:#FFFFFF;">_____________</span><span id="ColorRect" dir="LTR" style="position:'
                " absolute; width: 1.8cm; height: 0.45cm; border: 0.50pt solid #000000; padding: 0cm; background:"
                ' #CF1020"></span>'
            ),
            "[RGB #CF1020]",
        ],
        # ES - coord output
        [
            "es",
            (
                '<span class="geo-multi-punct"> / </span><span class="geo-nondefault"><span class="geo-dec geo">'
                '<span class="latitude">-4.2</span>, <span class="longitude">-69.917</span></span></span>'
            ),
            "",
        ],
        # ES - external autonumber
        [
            "es",
            (
                '<a rel="nofollow" class="external autonumber" href="http://books.google.es/books?id='
                '9nOz63haQysC&amp;pg=PA296&amp;dq=%22gesticulor%22">[1]</a>'
            ),
            "",
        ],
        # FR - anchors
        [
            "fr",
            '<a href="#cite">[1]</a>',
            "",
        ],
        # FR - attention
        [
            "fr",
            (
                '<a href="/wiki/Fichier:Twemoji12_26a0.svg" class="image" title="alt = attention"><img alt="'
                'alt = attention" src="//26a0.svg.png"></a>'
            ),
            "⚠",
        ],
        # FR - à préciser
        [
            "fr",
            (
                '<span title="Cette information a besoin d’être précisée"><small>&nbsp;<span style="color:red">('
                "information&nbsp;<i>à préciser ou à vérifier</i>)</span></small></span>"
            ),
            "",
        ],
        # FR - external autonumber
        [
            "fr",
            (
                '<a rel="nofollow" class="external autonumber" href="http://www.iupac.org/publications/pac/1994'
                '/pdf/6612x2419.pdf">[2]</a>'
            ),
            "",
        ],
        # FR - invisible
        [
            "fr",
            (
                'Du latin ecclésiastique<span class="invisible" style="display:none">latin <i><span class="lang-la"'
                ' lang="la"><a href="/wiki/Dalmatica#la" title="Dalmatica">Dalmatica</a></span></i></span> <i><a hr'
                'ef="/wiki/Dalmatica" title="Dalmatica">Dalmatica</a></i>'
            ),
            "Du latin ecclésiastique Dalmatica",
        ],
        # FR - lien rouge trad
        [
            "fr",
            (
                '<a href="https://en.wiktionary.org/wiki/Reconstruction:Proto-Indo-European/wemh%E2%82%81-" class="'
                'extiw" title="en:Reconstruction:Proto-Indo-European/wemh₁-"><span style="font-family:monospace;font'
                '-weight:bold;font-size:small;font-style:normal;" title="Équivalent de l’article « Reconstruction:i'
                'ndo-européen commun/*wem- » dans une autre langue">(en)</span></a>'
            ),
            "",
        ],
        # FR - math chem
        [
            "fr",
            '<span class="mwe-math-element"></span>',
            "",
        ],
        # FR - obsolete tpl
        [
            "fr",
            "<span id='FormattingError'>bouh !</span>",
            "",
        ],
        # FR - ref nec
        [
            "fr",
            '<span><sup><i><b>Référence nécessaire</b></i></sup></span><span id="refnec"></span>',
            "",
        ],
        # FR - sources
        [
            "fr",
            (
                '<span class="sources"><span class="tiret">—&nbsp;</span>(<i>Ordonnance de Louis XI pour la formation d'
                "un port et château fort à la Hague</i>)</span>"
            ),
            "",
        ],
        # FR - Wikidata
        [
            "fr",
            (
                '<a href="https://www.wikidata.org/wiki/Q30092597" class="extiw" title="d:Q30092597">Frederick H. '
                '<span class="petites_capitales" style="font-variant: small-caps">Pough</span></a> dans la base de'
                ' données Wikidata <img alt="Wikidata-logo.svg" src="//upload.wikimedia.org/wikipedia/commons/thu'
                'mb/f/ff/Wikidata-logo.svg/20px-Wikidata-logo.svg.png" decoding="async" width="20" height="11" src'
                'set="//upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Wikidata-logo.svg/30px-Wikidata-logo.svg'
                ".png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Wikidata-logo.svg/40px-Wikidata-lo"
                'go.svg.png 2x" data-file-width="1050" data-file-height="590" />'
            ),
            "Frederick H. Pough",
        ],
        # FR - Wikispecies
        [
            "fr",
            (
                '<i><a href="https://species.wikimedia.org/wiki/Panthera_leo" class="extiw" title="wikispecies'
                ':Panthera leo">Panthera leo</a></i> sur Wikispecies'
            ),
            "Panthera leo",
        ],
        # IT - numbered external links
        [
            "it",
            '<a class="external autonumber" href="https://it.wikipedia.org/wiki/Scomber_scombrus">[1]</a>',
            "",
        ],
        # IT - missing definition
        [
            "it",
            '<i>definizione mancante; se vuoi, <span class="plainlinks"><a class="external text" href="https://it.wiktionary.org/w/index.php?title=Upupidi&amp;action=edit">aggiungila</a></span> tu</i>',
            "",
        ],
        # IT - Wikiquote
        [
            "it",
            '<small>&nbsp;(<a href="/wiki/File:Wikiquote-logo.svg" class="image" title="Wikiquote"><img alt="Wikiquote" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikiquote-logo.svg/20px-Wikiquote-logo.svg.png" decoding="async" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikiquote-logo.svg/30px-Wikiquote-logo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Wikiquote-logo.svg/40px-Wikiquote-logo.svg.png 2x" data-file-width="300" data-file-height="355" width="20" height="24"></a> <b><a href="https://it.wikiquote.org/wiki/manuale" class="extiw" title="q:manuale">citazioni</a></b>)</small>',
            "",
        ],
        # IT - <ref>
        [
            "it",
            '<sup id="cite_ref-1" class="reference"><a href="#cite_note-1">[1]</a>',
            "",
        ],
        # IT - Wikipedia
        [
            "it",
            '<small>&nbsp;(<a href="/wiki/File:Wikipedia-logo-v2.svg" class="image" title="Wikipedia"><img alt="Wikipedia" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/20px-Wikipedia-logo-v2.svg.png" decoding="async" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/30px-Wikipedia-logo-v2.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/40px-Wikipedia-logo-v2.svg.png 2x" data-file-width="103" data-file-height="94" width="20" height="18"></a> <b><a href="https://it.wikipedia.org/wiki/Banda_(araldica)" class="extiw" title="w:Banda (araldica)">approfondimento</a></b>)</small>',
            "",
        ],
        # IT - Wikispecies
        [
            "it",
            '(<img alt="Wikispecies" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/20px-WikiSpecies.svg.png" decoding="async" title="Wikispecies" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/30px-WikiSpecies.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/40px-WikiSpecies.svg.png 2x" data-file-width="125" data-file-height="177" width="20" height="28"> <b><a href="https://species.wikimedia.org/wiki/Aegypiinae" class="extiw" title="wikispecies:Aegypiinae">tassonomia</a></b>)',
            "",
        ],
        # IT - Wikispecies (ensure next siblings are kept)
        [
            "it",
            '(<img alt="Wikispecies" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/20px-WikiSpecies.svg.png" decoding="async" title="Wikispecies" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/30px-WikiSpecies.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/40px-WikiSpecies.svg.png 2x" data-file-width="125" data-file-height="177" width="20" height="28"> <b><a href="https://species.wikimedia.org/wiki/Aegypiinae" class="extiw" title="wikispecies:Aegypiinae">tassonomia</a></b>);',
            ";",
        ],
        # IT - Wikispecies (without next siblings)
        [
            "it",
            '<img alt="Wikispecies" class="mw-file-element" data-file-height="177" data-file-width="125" decoding="async" height="28" src="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/20px-WikiSpecies.svg.png" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/30px-WikiSpecies.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/d/d9/WikiSpecies.svg/40px-WikiSpecies.svg.png 2x" width="20"/>',
            "",
        ],
        # PT - superscript locales
        [
            "pt",
            '<sup>(<a class="extiw" href="https://la.wiktionary.org/wiki/izare" title="la:izare"><span style="letter-spacing:1px" title="ver no Wikcionário em latim">la</span></a>)</sup>',
            "",
        ],
        # PT - superscript locales (inexistent)
        [
            "pt",
            '<sup>(<a class="new" href="https://la.wiktionary.org/wiki/izare" title="la:izare (página não existe)"><span style="letter-spacing:1px" title="ver no Wikcionário em latim">la</span></a>)</sup>',
            "",
        ],
        # PT - no print
        [
            "pt",
            '<span class="noprint"><a class="extiw" href="https://sr.wiktionary.org/wiki/%D0%88%D1%83%D0%B3%D0%BE%D1%81%D0%BB%D0%B0%D0%B2%D0%B8%D1%98%D0%B0" title="sr:Југославија"><sup><span style="letter-spacing:1px" title="Clique aqui para ver “Југославија” no Wikcionário em sérvio">(sr)</span></sup></a></span>',
            "",
        ],
        # PT - keep anchors
        ["pt", '<a href="#Adjetivo">ainu</a>', "ainu"],
        # PT - external links
        [
            "pt",
            '<small>(<a href="https://la.wiktionary.org/wiki/aer" class="extiw" title="la:aer">ver no Wikcionário em Latim</a>)</small>',
            "",
        ],
        # SV - <ref>
        [
            "sv",
            '<sup id="cite_ref-1" class="reference"><a href="#cite_note-1">[1]</a></sup>',
            "",
        ],
    ],
)
@responses.activate
def test_filter_html(
    locale: str,
    body: str,
    expected: str,
    craft_urls_with_body: Callable[[str, str, str], str],
) -> None:
    word = craft_urls_with_body(locale, WORD[locale], body)
    assert check_word.filter_html(body, locale) == expected.replace(" ", "")
    assert check_word.main(locale, word) == 0


@pytest.mark.parametrize(
    "wiktionary_text, parsed_html, ret_code, is_highlighted",
    [
        ("some text", "text", 0, False),
        ("this is orginal text", "foo bar", 1, False),
        ("this is orginal text", "originaal text", 1, True),
        ("this is orginal text", "tiis is original text", 1, False),
        ("this is orginal text", "This is original text", 1, False),
    ],
)
def test_check_highlighting(
    wiktionary_text: str,
    parsed_html: str,
    ret_code: int,
    is_highlighted: bool,
    caplog: pytest.LogCaptureFixture,
) -> None:
    error = check_word.check(wiktionary_text, parsed_html, "Test")
    assert error == ret_code
    if is_highlighted:
        errors = "\n".join(m.getMessage() for m in caplog.records)
        assert "\033[31m" in errors


def test_get_url_content_timeout_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def get(*_: Any, **__: Any) -> None:
        raise TimeoutError()

    monkeypatch.setattr("wikidict.check_word.SLEEP_TIME", 0.01)
    monkeypatch.setattr("requests.get", get)
    with pytest.raises(RuntimeError):
        check_word.get_url_content("https://...")


def test_get_url_content_too_many_requests_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def get(*_: Any, **__: Any) -> None:
        response = Response()
        response.status_code = 429
        response.headers["retry-after"] = "1"
        raise RequestException(response=response)

    monkeypatch.setattr("wikidict.check_word.SLEEP_TIME", 0.01)
    monkeypatch.setattr("requests.get", get)
    with pytest.raises(RuntimeError):
        check_word.get_url_content("https://...")
