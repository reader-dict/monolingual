"""Get and render a word; then compare with the rendering done on the Wiktionary to catch errors."""

from __future__ import annotations

import copy
import logging
import re
import urllib.parse
import warnings
from functools import partial
from time import sleep
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning, NavigableString
from requests.exceptions import RequestException

from . import constants, utils
from .render import parse_word
from .user_functions import color, int_to_roman

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any

    from bs4 import Tag

    from .stubs import Word

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Remove all kind of spaces and some unicode characters
_replace_noisy_chars = re.compile(r"[\s\u200a\u200b\u200e]").sub
no_spaces = partial(_replace_noisy_chars, "")

# Retry mechanism
MAX_RETRIES = 5  # count
SLEEP_TIME = 5  # time, seconds

log = logging.getLogger(__name__)


def check_mute(wiktionary_text: str, parsed_html: str, category: str) -> str:
    clean_text = get_text(parsed_html)

    # It's all good!
    if contains(clean_text, wiktionary_text):
        return ""

    # Try to highlight the bad text
    pattern = clean_text[:-1].rstrip()
    while pattern:
        if not contains(pattern, wiktionary_text):
            pattern = pattern[:-1].rstrip()
            continue

        idx = len(pattern)
        return f"[{category}] {clean_text[:idx]}\033[31m{clean_text[idx:]}\033[0m"

    # No highlight possible, just output the whole sentence
    return f"[{category}] {clean_text}"


def check(wiktionary_text: str, parsed_html: str, category: str) -> int:
    """Run checks and return the error count to increment. Used in tests only."""
    results = check_mute(wiktionary_text, parsed_html, category)
    log.error("Diff:\n%s", results)
    return bool(results)


def contains(pattern: str, text: str) -> bool:
    """Check if *pattern* is in *text*, with all spaces removed.
    *text* is already stripped from spaces in get_wiktionary_page().
    """
    return no_spaces(pattern) in text


def filter_html(html: str, locale: str) -> str:
    """Some parts of the Wiktionary HTML."""
    bs = BeautifulSoup(markup=html, features="html.parser")

    def find_all(name: str, *args: Any, **kwargs: Any) -> Iterator[Tag]:
        yield from bs.find_all(name, *args, **kwargs)  # type: ignore[misc]

    # Filter out warnings about obsolete template models used
    for tag in find_all("span", {"id": "FormattingError"}):
        tag.decompose()

    # Filter out Wikispecies links
    for tag in find_all("span", {"class": "trad-exposant"}):
        tag.decompose()

    # Filter out result of <math> and <chem>
    for tag in find_all("span", {"class": "mwe-math-element"}):
        tag.decompose()

    if locale == "ca":
        # {{sense accepcions}}
        for tag in find_all("i"):
            if tag.text.startswith("a aquesta paraula li falten les accepcions") and tag.next_sibling:
                # Remove the trailing dot
                tag.next_sibling.replace_with(tag.next_sibling.text[1:])
                tag.decompose()

        # Filter out anchors as they are ignored from templates
        for tag in find_all("a", href=True):
            href = str(tag["href"])
            if (
                href.startswith("#")
                and not href.startswith("#ca#")
                and href != "#ca"
                and "mw-selflink-fragment" not in (tag.get("class") or [])
            ):
                tag.replace_with(tag.text)

        # <ref>
        for a in bs.find_all("sup", {"class": "reference"}):
            a.decompose()

    elif locale == "da":
        for tag in find_all("sup"):
            if (id_ := str(tag.get("id") or "")) and id_.startswith("cite_"):
                tag.decompose()

    elif locale == "de":
        # <sup>☆</sup>
        for tag in find_all("sup", string="☆"):
            tag.decompose()

        # External links
        for tag in find_all("small", {"class": "noprint"}):
            tag.decompose()

        # Internet Archive
        for tag in find_all("a", {"class": "external"}):
            if "archive.org" in tag["href"]:
                tag.decompose()

        # Lang link in {{Üxx5}}
        for tag in find_all("a"):
            if (sub_tag := tag.find("sup")) and tag.text.startswith("→"):
                sub_tag.decompose()

        # Other Wikis
        for tag in find_all("a", {"class": "extiw"}):
            if (
                ":Special:" not in tag["title"]
                and (a_sup := tag.find("sup"))
                and "WP" in a_sup.text
                or ":Special:" in tag["title"]
            ):
                tag.decompose()

        for tag in find_all("sup"):
            if tag.get("style", "") == "color:slategray;":
                tag.decompose()

            # Filter out anchors as they are ignored from templates
            for tag in find_all("a", href=True):
                if str(tag["href"]).startswith("#"):
                    tag.decompose()

    elif locale == "el":
        # {{audio}} template
        for tag in find_all("span", {"class": "ext-phonos"}):
            if tag.parent:
                tag.parent.decompose()

        # Wikipedia link
        for tag in find_all("span", {"id": "mwDQ"}):
            if "ΒΠ" in str(tag.get("data-mw")):
                tag.decompose()

        for tag in find_all("sup"):
            if (id_ := str(tag.get("id", ""))) and id_.startswith(("cite_", "mwDg")):
                tag.decompose()

    elif locale == "en":
        for tag in find_all("span"):
            if tag.string == "and other forms":
                tag.string += f" {tag['title']}"

        # WikiSpecies sup
        for tag in find_all("sup"):
            for stag in tag.find_all("a", {"class": "extiw"}):
                stag.decompose()

        # Other anchors
        for tag in find_all("a", href=True):
            if str(tag["href"]).lower().startswith(("#cite", "#mw")):
                tag.decompose()

    elif locale == "eo":
        # <ref>
        for tag in find_all("sup", {"class": "reference"}):
            tag.decompose()

    elif locale == "es":
        # Replace color rectangle
        for tag in find_all("span", {"id": "ColorRect"}):
            for style in str(tag["style"]).split(";"):
                kv = style.strip().split(":")
                if len(kv) == 2 and kv[0] == "background" and tag.previous_sibling:
                    tag.previous_sibling.decompose()
                    tag.replace_with(NavigableString(color(kv[1].strip())))

        for tag in find_all("a", href=True):
            if str(tag["href"]).startswith("#cite"):
                tag.decompose()

            # Cita requerida
            elif (
                tag["href"] == "/wiki/Ayuda:Tutorial_(Ten_en_cuenta)#Citando_tus_fuentes"
                and tag.parent
                and tag.parent.parent
            ):
                tag.parent.parent.decompose()

        # Coord output
        for tag in find_all("span", {"class": ["geo-multi-punct", "geo-nondefault"]}):
            tag.decompose()

        # External autonumber
        for tag in find_all("a", {"class": "external autonumber"}):
            tag.decompose()

        for dt in find_all("dt"):
            if len(dt_array := dt.text.split(" ", 1)) != 2:
                continue

            dt.string = f"{dt_array[0]} "
            # 2 Historia. --> (Historia):
            if "." in dt_array[1]:
                dt_array_dot = dt_array[1].split(".")
                for da in dt_array_dot[:-1]:
                    dt.string = f"{dt.string}({da})"
                dt.string = f"{dt.string} {dt_array_dot[-1]}:"
            elif dt.parent:
                # Duplicate the definition to cope with both cases above
                newdt = copy.copy(dt)
                dt.parent.append(newdt)
                if dd := dt.find_next_sibling("dd"):
                    dt.parent.append(copy.copy(dd))
                # 2 Selva de Bohemia: --> Selva de Bohemia:
                newdt.string = f"{dt.string}{dt_array[1]}:"
                # 2 Coloquial: --> (Coloquial):
                dt.string = f"{dt.string}({dt_array[1]}):"

    elif locale in {"fr", "fro"}:
        # Filter out refnec tags
        for tag in find_all("span", {"id": "refnec"}):
            if tag.previous_sibling:
                tag.previous_sibling.decompose()
            tag.decompose()

        # Cette information a besoin d’être précisée
        for tag in find_all("span", {"title": "Cette information a besoin d’être précisée"}):
            tag.decompose()

        # {{invisible}}
        for tag in find_all("span", {"class": "invisible"}):
            tag.decompose()

        # — (Richelet, Dictionnaire français 1680)
        for tag in find_all("span", {"class": "sources"}):
            tag.decompose()

        # → consulter cet ouvrage
        for tag in find_all("a", {"class": "external text"}):
            if "consulter cet ouvrage" in tag.text:
                tag.decompose()

        # Liens externes autres Wikis
        for tag in find_all("a", {"class": "extiw"}):
            # Wikispecies
            if (
                str(tag["title"]).startswith("wikispecies")
                and tag.parent
                and tag.parent.next_sibling
                and "sur Wikispecies" in tag.parent.next_sibling.text
            ):
                tag.parent.next_sibling.extract()

            # Wikidata
            elif (
                str(tag["title"]).startswith("d:")
                and tag.next_sibling
                and "base de données Wikidata" in tag.next_sibling.text
            ):
                tag.next_sibling.extract()

            # {{LienRouge|lang=en|trad=Reconstruction
            elif "Reconstruction" in tag["title"]:
                tag.decompose()
        # External autonumber
        for tag in find_all("a", {"class": "external autonumber"}):
            tag.decompose()

        # Attention image
        for tag in find_all("a", {"title": "alt = attention"}):
            tag.replace_with(NavigableString("⚠"))

        # Other anchors
        for tag in find_all("a", href=True):
            if str(tag["href"]).lower().startswith(("#cite", "#ref", "#voir")):
                tag.decompose()

    elif locale == "it":
        # Numbered external links
        for tag in find_all("a", {"class": "external autonumber"}):
            tag.decompose()
        # Missing definitions
        for tag in find_all("i"):
            if tag.text.startswith("definizione mancante"):
                tag.decompose()

        # <ref>
        for tag in find_all("sup", {"class": "reference"}):
            tag.decompose()

        # Wikispecies
        for tag in find_all("img", {"alt": "Wikispecies"}):
            if (next_sibling := tag.next_sibling) and next_sibling.next_sibling:
                next_sibling.next_sibling.decompose()  # <b><a>...</a></b>
                next_sibling.next_sibling.replace_with(next_sibling.next_sibling.text[1:])  # Trailing ")"
                next_sibling.extract()  # Space
                if tag.previous_sibling:
                    tag.previous_sibling.extract()  # Leading "("
            tag.decompose()

        # Wikipedia, Wikiquote
        for tag in find_all("small"):
            if tag.find("a", {"title": "Wikipedia"}) or tag.find("a", {"title": "Wikiquote"}):
                tag.decompose()

    elif locale == "no":
        # <ref>
        for tag in find_all("sup", {"class": "reference"}):
            tag.decompose()

    elif locale == "pt":
        # Superscript locales
        for tag in find_all("sup"):
            if tag.find("a", {"class": "extiw"}) or tag.find("a", {"class": "new"}):
                tag.decompose()

        # Almost same as previous, but for all items not elligible to be printed
        for tag in find_all("span", {"class": "noprint"}):
            tag.decompose()

        # External links
        for tag in find_all("small"):
            if tag.find("a", {"class": "extiw"}):
                tag.decompose()

    elif locale == "sv":
        # <ref>
        for tag in find_all("sup", {"class": "reference"}):
            tag.decompose()

    return no_spaces(bs.text)


def get_text(html: str) -> str:
    """Parse the HTML code and return it as a string."""
    return str(BeautifulSoup(markup=html, features="html.parser").text)


def craft_url(word: str, locale: str, *, raw: bool = False) -> str:
    """Craft the *word* URL for the given *locale*."""
    url = f"https://{utils.guess_lang_origin(locale)}.wiktionary.org/w/index.php?title={urllib.parse.quote(word)}"
    if raw:
        url += "&action=raw"
    return url


def get_url_content(url: str) -> str:
    """Fetch given *url* content with retries mechanism."""
    retry = 0
    while retry < MAX_RETRIES:
        try:
            with constants.SESSION.get(url, timeout=10) as req:
                req.raise_for_status()
                return req.text
        except TimeoutError:
            sleep(SLEEP_TIME)
            retry += 1
        except RequestException as err:
            wait_time = 1
            resp = err.response
            if resp is not None:
                if resp.status_code == 429:
                    wait_time = int(resp.headers.get("retry-after") or "1")
                elif resp.status_code == 404:
                    log.error(err)
                    return "404"
            sleep(wait_time * SLEEP_TIME)
            retry += 1
    raise RuntimeError(f"Sorry, too many tries for {url!r}")


def get_word(word: str, locale: str, *, all_templates: list[tuple[str, str, str]] | None = None) -> Word:
    """Get a *word* wikicode and parse it."""
    url = craft_url(word, utils.guess_lang_origin(locale), raw=True)
    html = get_url_content(url)
    return parse_word(word, html, locale, all_templates=all_templates)


def get_wiktionary_page(word: str, locale: str) -> str:
    """Get a *word* HTML."""
    url = craft_url(word, locale)
    html = get_url_content(url)
    return filter_html(html, locale)


def check_word(
    word: str,
    locale: str,
    *,
    standalone: bool = True,
    all_templates: list[tuple[str, str, str]] | None = None,
) -> int:
    errors = 0
    results: list[str] = []

    if all_templates is None:
        all_templates = []

    details = get_word(word, locale, all_templates=all_templates)
    text = get_wiktionary_page(word, locale)

    if details.etymology:
        for etymology in details.etymology:
            if isinstance(etymology, tuple):
                for i, sub_etymology in enumerate(etymology, 1):
                    if r := check_mute(text, sub_etymology, f"Etymology {i}"):  # type: ignore[arg-type]
                        results.append(r)
            elif r := check_mute(text, etymology, "Etymology"):
                results.append(r)

    for pos, definitions in sorted(details.definitions.items(), key=lambda kv: kv[0]):
        for index, definition in enumerate(definitions, 1):
            if isinstance(definition, tuple):
                for a, subdef in zip("abcdefghijklmopqrstuvwxz", definition):
                    if isinstance(subdef, tuple):
                        for rn, subsubdef in enumerate(subdef, 1):
                            if r := check_mute(text, subsubdef, f"{pos} n°{index:02d}.{int_to_roman(rn).lower()}"):
                                results.append(r)
                    elif r := check_mute(text, subdef, f"{pos} n°{index:02d}.{a}"):
                        results.append(r)
            elif r := check_mute(text, definition, f"{pos} n°{index:02d}"):
                results.append(r)

    if results:
        errors = len(results)
        for result in results:
            log.error(result)
        log.warning("[%s] - Errors: %s", word, errors)
    else:
        log.debug("[%s] - OK", word)

    if standalone:
        print()
        errors += int(utils.check_for_missing_templates(all_templates))

    return errors


def main(locale: str, word: str) -> int:
    """Entry point."""

    _, lang_dst = utils.guess_locales(locale, use_log=False)

    # If *word* is empty, get a random word
    word = word or utils.get_random_word(lang_dst)

    return check_word(word, locale)
