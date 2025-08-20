import re
from collections import defaultdict
from logging import getLogger

from . import caches, constants

log = getLogger(__name__)
UNWANTED_TAGS = {"a", "div", "p", "span"}
WANTED_TAGS = {"b", "/b", "i", "/i", "small", "/small"}
CACHE = caches.load_cache_file("places")


def sanitize(html: str) -> str:
    """
    >>> sanitize('<div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr"><p><span class="form-of-definition use-with-mention"><a href="/wiki/Appendix:Glossary#abbreviation" title="Appendix:Glossary">Abbreviation</a> of <span class="form-of-definition-link"><i class="Latn mention" lang="en"><a href="/wiki/Acre#English" title="Acre">Acre</a></i></span></span>: a <a href="/wiki/state" title="state">state</a> of <span class="Latn" lang="en"><a href="/wiki/Brazil#English" title="Brazil"><b some="attr">Brazil</a></b></span>\\n</p></div>')
    'Abbreviation of <i>Acre</i>: a state of <b>Brazil</b>'
    """
    # Remove those tags
    for tag in UNWANTED_TAGS:
        html = re.sub(rf"<{tag}[^>]+>", "", html)
        html = html.replace(f"<{tag}>", "").replace(f"</{tag}>", "")

    # Clean-up attributes from those tags
    html = re.sub(r"<(b|i|small)[^>]+>", r"<\1>", html)

    # Check for tags left
    if missings := set(re.findall(r"<([^>]+)>", html)) - WANTED_TAGS:
        assert 0, f"More sanitization required for the 'place' template: {missings}"

    return html.strip()


def retrieve_parser_output(wikitext: str, locale: str) -> str:
    params = {
        "action": "parse",
        "contentmodel": "wikitext",
        "disablelimitreport": "1",
        "format": "json",
        "prop": "text",
        "text": wikitext,
    }
    with constants.SESSION.get(constants.WIKTIONARY_URL_API.format(locale=locale), params=params, timeout=10) as req:
        result = req.json()["parse"]["text"]["*"]
    return sanitize(result)


def get(parts: list[str], data: defaultdict[str, str], locale: str) -> str:
    template = ["place"] + parts
    if data:
        template.extend(f"{k}={v}" for k, v in sorted(data.items()))
    wikitext = f"{{{{{'|'.join(template)}}}}}"

    if not (cached := CACHE.get(wikitext, "")):
        CACHE[wikitext] = cached = retrieve_parser_output(wikitext, locale)
        save(wikitext, cached)
    return cached


def save(wikitext: str, result: str) -> None:
    log.warning("[new place] %r: %r,", wikitext, result)
    CACHE[wikitext] = result
