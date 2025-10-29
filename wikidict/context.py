from __future__ import annotations

import atexit
import logging
import os
import re
from collections.abc import Generator
from functools import lru_cache
from pathlib import Path
from threading import Lock

import wikitextprocessor
from wikitextprocessor.dumpparser import add_default_templates
from wikitextprocessor.interwiki import init_interwiki_map
from wikitextprocessor.luaexec import initialize_lua

from . import constants, lang, parse, utils
from .namespaces import namespaces

# Thread-local storage for per-process contexts
_contexts: dict[int, Context] = {}
_lock = Lock()

# To print all Lua warnings & errors:
#    DEBUG_LUA=2 python -m wikidict LOCALE --render
DEBUG_LUA = int(os.getenv("DEBUG_LUA", "0")) > 1

# Remove greedy methods we do not need
setattr(wikitextprocessor.Wtp, "debug", lambda *_, **__: None)
setattr(wikitextprocessor.Wtp, "note", lambda *_, **__: None)
setattr(wikitextprocessor.Wtp, "warning", lambda *_, **__: None)

if not DEBUG_LUA:
    # Remove a noisy `print()` statement on error
    setattr(wikitextprocessor.Wtp, "_fmt_errmsg", lambda *_: None)


log = logging.getLogger(__name__)


class Context:
    def __init__(self, db: Path, locale: str, *, db_already_setup: bool = True) -> None:
        self.snapshot = db.stem.split("-", 1)[-1]
        self.ctx = wikitextprocessor.Wtp(
            db,
            extension_tags={"phonos": {"content": ["phrasing"]}},
            lang_code=locale,
            parser_function_aliases=constants.PARSER_FUNCTIONS_ALIASES.get(locale, {}),
            project="wiktionary",
            quiet=True,
            template_override_funcs={
                "flexion": lambda _: "",
                "rev-flexion": lambda _: "",
                **lang.template_overrides[locale],  # type: ignore[dict-item]
            },
        )

        initialize_lua(self.ctx)

        # Tweak SQLite behavior
        execute = self.ctx.db_conn.execute
        execute("PRAGMA journal_mode = WAL;")
        execute("PRAGMA busy_timeout = 5000;")
        execute("PRAGMA synchronous = NORMAL;")
        execute("PRAGMA cache_size = 1000000000;")
        execute("PRAGMA temp_store = memory;")

        if db_already_setup:
            self._cache: dict[str, str] = {}
            self._cache_exclusions = self._get_cache_exclusions()
        else:
            init_interwiki_map(self.ctx)
            add_default_templates(self.ctx)

    def close(self) -> None:
        self.ctx.close_db_conn()

    def expand(self, wikitext: str, locale: str) -> str:
        if wikitext.startswith(self._cache_exclusions):
            expanded = clean_html_output(self.ctx.expand(wikitext, quiet=True), locale)
        elif not (expanded := self._cache.get(wikitext, "")):
            expanded = clean_html_output(self.ctx.expand(wikitext, quiet=True), locale)
            self._cache[wikitext] = expanded
        return expanded

    def set_cache_exclusions(self) -> None:
        # sourcery skip: extract-duplicate-method
        """Update the database to set the cacheable state of templates/modules.
        Ones using the current word should not be cached.

        We first fetch modules to exclude from the cache.
        As a module can use the current word, but the upper call from a template will not know it, the template exclusion process is split:

            1. Fetch templates using the current word, simple cases.
            2. Fetch templates using excluded modules, complex cases.

        Complex case example:

            [EN] The "ms-pron" module uses the current word (so it must be excluded), and the caller template "ms-IPA" only contains `{{#invoke:ms-pron|show}}`,
            so we need to exclude both "ms-pron" & "ms-IPA".
        """
        conn = self.ctx.db_conn

        # Add a new column: cacheable (defaults to 1)
        conn.executescript("""
            BEGIN;
            ALTER TABLE pages
                    ADD COLUMN cacheable INTEGER NOT NULL DEFAULT 1;
            COMMIT;
        """)

        # Modules to exclude
        conn.execute(
            """
            UPDATE pages
               SET cacheable = 0
             WHERE namespace_id = 828
               AND instr(body, 'getCurrentTitle') > 0
            """
        )

        # Templates & modules to exclude, simple cases
        conn.execute("""
            UPDATE pages
               SET cacheable = 0
             WHERE cacheable != 0
               AND namespace_id IN (10, 828)
               AND instr(body, 'PAGENAME') > 0
        """)

        # Templates to exclude, complex cases (in 2 steps)

        # 1) Create a temporary table with patterns to exclude (i.e.: excluded modules)
        conn.executescript("""
            BEGIN;
            CREATE TEMP TABLE patterns (pat TEXT PRIMARY KEY);
            INSERT INTO patterns(pat)
                  SELECT trim(
                        CASE
                            WHEN instr(title, ':') > 0 THEN substr(title, instr(title, ':') + 1)
                            ELSE title
                        END
                    )
                   FROM pages
                  WHERE cacheable = 0
                    AND namespace_id = 828;
            COMMIT;
        """)

        # 2) Use the temporary table to properly set the templates "cacheable" state
        conn.execute("""
            UPDATE pages
               SET cacheable = 0
             WHERE namespace_id = 10
               AND EXISTS (
                    SELECT 1
                      FROM patterns
                     WHERE instr(pages.body, '#invoke:' || pat || '|') > 0
                        OR instr(pages.body, '#invoke:' || pat || '}') > 0
                        OR instr(pages.body, '#invoke:' || pat || '/') > 0
                );
        """)

        # Handle redirections (a template redirecting to an uncachable template must also be uncacheable)
        conn.execute("""
            UPDATE pages
               SET cacheable = 0
             WHERE cacheable = 1
               AND namespace_id = 10
               AND redirect_to IS NOT NULL
               AND redirect_to <> ''
               AND EXISTS (
                    SELECT 1
                      FROM pages AS target
                     WHERE target.cacheable = 0
                       AND target.namespace_id = 10
                       AND target.title = pages.redirect_to
                   )
        """)

        # Finally, create the partial covering index to speed-up read queries
        conn.execute("""
            CREATE INDEX idx_pages_cacheable0_title
                      ON pages(title)
                   WHERE cacheable = 0
        """)
        conn.execute("ANALYZE")
        conn.commit()

    def _get_cache_exclusions(self) -> tuple[str, ...]:
        """Templates/Modules using the current word should not be cached."""
        query = "SELECT title FROM pages WHERE cacheable = 0"
        return tuple(
            [
                "{{PAGENAME",
                *(
                    f"{{{{{page[0].split(':', 1)[1]}"  # `Template:foo` → `{{foo`
                    for page in self.ctx.db_conn.execute(query).fetchall()
                ),
            ]
        )

    def translate_requires(self, current_value: str, new_value: str) -> None:
        """Translate Lua inline module imports.

        Example with the JA dictionary:
            - `require "Module:xxx"` → `require "モジュール:xxx"`
            - `require("Module:xxx")` → `require("モジュール:xxx")`
            - `loadData("Module:xxx")` → `loadData("モジュール:xxx")`
        """
        search = f'"{current_value}:'
        replace = f'"{new_value}:'
        like = f"%{search}%"
        query = "UPDATE pages SET body = REPLACE(body, ?, ?) WHERE namespace_id = 828 AND body LIKE ?"
        self.ctx.db_conn.execute(query, (search, replace, like))
        self.ctx.db_conn.commit()

    def fetch_words(self) -> Generator[tuple[str, str]]:
        query = "SELECT title, body FROM pages WHERE namespace_id = 0 AND redirect_to IS NULL"
        yield from self.ctx.db_conn.execute(query)

    def fetch_redirections(self) -> Generator[tuple[str, str]]:
        query = "SELECT title, redirect_to FROM pages WHERE namespace_id = 0 AND redirect_to IS NOT NULL"
        yield from self.ctx.db_conn.execute(query)

    def get_errors(self) -> list[str]:
        everything = self.ctx.to_return()
        return [error["msg"] for error in everything["errors"]] + [error["msg"] for error in everything["wiki_notices"]]

    def new_page(self, title: str, namespace_id: int, body: str | None, redirect_to: str | None) -> None:
        model = "Scribunto" if namespace_id == 828 else "wikitext"
        self.ctx.add_page(title, namespace_id, body=body, model=model, redirect_to=redirect_to)

    def new_word(self, word: str) -> None:
        self.ctx.start_page(word)


def get_ctx() -> Context:
    pid = os.getpid()
    try:
        return _contexts[pid]
    except KeyError as exc:
        msg = f"Context not initialized for process {pid}. Call init() before using the context."
        raise RuntimeError(msg) from exc


def setup_modules_db(locale: str, *, db_already_setup: bool = True) -> bool:
    lang_src, _ = utils.guess_locales(locale, use_log=False)
    source_dir = parse.get_source_dir(lang_src)
    if not (input_file := parse.get_latest_dump_file(source_dir)):
        print("No dump found. Run with --download first ... ")
        return False

    snapshot = input_file.stem[6:14]
    assert len(snapshot) == 8 and snapshot.isdigit(), repr(snapshot)
    db_path = parse.get_output_file(source_dir, snapshot)
    db_path.parent.mkdir(exist_ok=True)
    init(db_path, lang_src, db_already_setup=db_already_setup)
    return True


def init(db: Path, locale: str, *, db_already_setup: bool = True) -> None:
    if (pid := os.getpid()) in _contexts:
        return

    with _lock:
        _contexts[pid] = Context(db, locale, db_already_setup=db_already_setup)
        atexit.register(lambda: close_ctx(pid))


def close_ctx(pid: int | None = None) -> None:
    with _lock:
        if ctx := _contexts.pop(pid or os.getpid(), None):
            ctx.close()


def reset(locale: str, *, db_already_setup: bool = True) -> bool:
    close_ctx()
    return setup_modules_db(locale, db_already_setup=db_already_setup)


def get_errors() -> list[str]:
    return get_ctx().get_errors()


def new_page(title: str, namespace_id: int, body: str | None, redirect_to: str | None) -> None:
    get_ctx().new_page(title, namespace_id, body, redirect_to)


def new_word(word: str) -> None:
    get_ctx().new_word(word)


def expand(wikitext: str, locale: str) -> str:
    return get_ctx().expand(wikitext, locale)


def adapt_templates(locale: str) -> None:
    this_ctx = get_ctx()

    ctx = this_ctx.ctx

    for template, adapter in lang.template_adapters[locale].items():
        if not (page := ctx.get_page(template)):
            log.error("Module/Template not found in the database: %r", template)
            continue

        assert page.body  # For Mypy

        if (new_body := adapter(page.body)) == page.body:
            log.info("Module/Template body unchanged: %r", template)
            continue

        ctx.add_page(
            template,
            page.namespace_id,
            body=new_body,
            model=page.model,
            need_pre_expand=page.need_pre_expand,
            redirect_to=page.redirect_to,
        )

    if locale == "ja":
        this_ctx.translate_requires("Module", "モジュール")

    this_ctx.set_cache_exclusions()


@lru_cache(maxsize=256)
def all_namespaces(locale: str) -> str:
    all_namespaces_ = set()
    for namespace in namespaces[locale] + namespaces["en"]:
        all_namespaces_.add(namespace)
        all_namespaces_.add(namespace.lower())
    return "|".join(iter(all_namespaces_))


def clean_html_input(code: str, locale: str) -> str:
    r"""
    >>> clean_html_input("[[Fichier:Blason ville fr Petit-Bersac 24.svg|vignette|120px|'''Base''' d’or ''(sens héraldique)'']][[something|else]]", "fr")
    '[[something|else]]'
    >>> clean_html_input("[[File:Sarcoscypha_coccinea,_Salles-la-Source_(Matthieu_Gauvain).JPG|vignette|Pézize écarlate]][[something|else]]", "en")
    '[[something|else]]'
    >>> clean_html_input("[[File:1864 Guernesey 8 Doubles.jpg|thumb|Pièce de 8 doubles (île de [[Guernesey]], 1864).]][[something|else]]", "en")
    '[[something|else]]'
    >>> clean_html_input("[[fil:ISO 7010 E002 new.svg|thumb|right|160px|piktogram nødudgang]][[something|else]]", "da")
    '[[something|else]]'
    >>> clean_html_input("[[Catégorie:Localités d’Afrique du Sud en français]][[something|else]]", "fr")
    '[[something|else]]'
    >>> clean_html_input("[[Archivo:Striped_Woodpecker.jpg|thumb|[1] macho.]][[something|else]]", "es")
    '[[something|else]]'
    >>> clean_html_input("[[Archivo:Mezquita de Córdoba - Celosía 006.JPG|thumb|[1]]][[something|else]]", "es")
    '[[something|else]]'
    >>> clean_html_input("[[Archivo:Diagrama bicicleta.svg|400px|miniaturadeimagen|'''Partes de una bicicleta:'''<br>\n[[asiento]] o [[sillín]], [[cuadro]]{{-sub|8}}, [[potencia]], [[puño]]{{-sub|4}}, [[cuerno]], [[manubrio]], [[telescopio]], [[horquilla]], [[amortiguador]], [[frenos]], [[tijera]], [[rueda]], [[rayos]], [[buje]], [[llanta]], [[cubierta]], [[válvula]], [[pedal]], [[viela]], [[cambio]], [[plato]]{{-sub|5}} o [[estrella]], [[piñón]], [[cadena]], [[tija]], [[tubo de asiento]], [[vaina]].]]\n\n[[something|else]]", "es")
    '\n\n[[something|else]]'
    >>> clean_html_input("[[File:Karwats.jpg|thumb|A scourge ''(noun {{senseno|en|whip}})'' [[exhibit#Verb|exhibited]] in a [[museum#Noun|museum]].]][[something|else]]", "en")
    '[[something|else]]'
    >>> clean_html_input("[[w:Burattino|Burattino]]", "it")
    '[[w:Burattino|Burattino]]'
    >>> clean_html_input("[[en:propedeutici]]", "it")
    '[[en:propedeutici]]'

    >>> clean_html_input("<!-- {{sco}} -->", "fr")
    ''
    >>> clean_html_input("<!--<i>sco</i> -->", "fr")
    ''
    >>> clean_html_input("<!--\nsco\n-->", "it")
    ''

    >>> clean_html_input("<ref name=oed/>Modelled<ref>Gerhard</ref> English<ref name=oed>Press.</ref>", "en")
    'Modelled English'
    >>> clean_html_input('From {{uder|en|la|Augeas}} {{suffix|en||an}}. {{w|Augeas}} is a figure in Greek mythology whose stables were never cleaned until {{w|Hercules}} was given the task of cleaning them.<ref name="AT">\n''Ariadne’s Thread: A Guide to International Tales Found in Classical Literature'' by William F. Hansen (2002; [http://www.cornellpress.cornell.edu/cup_detail.taf?ti_id=3674 Cornell University Press]; {{ISBN|9780801475726}}, 9780801436703), [http://books.google.co.uk/books?id=ezDlXl7gP9oC&pg=PA160&dq=%22Augean+stables%22&ei=ZAtOSoPJIY6-yQTn9ezvAg page 160]<br>  ''Herakles Cleans the Augean Stables''<br>  One of the best-known stories attached to Herakles tells how in one day he removed the dung from King Augeias’s cattle yard, which had not been cleaned in years.</ref>', "en")
    'From {{uder|en|la|Augeas}} {{suffix|en||an}}. {{w|Augeas}} is a figure in Greek mythology whose stables were never cleaned until {{w|Hercules}} was given the task of cleaning them.'
    >>> clean_html_input("<ref>{{Import:CFC}}</ref>", "en")
    ''
    >>> clean_html_input("<ref>{{Import:CFC}}</ref>bla bla bla <ref>{{Import:CFC}}</ref>", "en")
    'bla bla bla '
    >>> clean_html_input("<ref>{{Lit-Pfeifer: Etymologisches Wörterbuch|A=8}}, Seite 1551, Eintrag „Wein“<br />siehe auch: {{Literatur | Online=zitiert nach {{GBS|uEQtBgAAQBAJ|PA76|Hervorhebung=Wein}} | Autor=Corinna Leschber| Titel=„Wein“ und „Öl“ in ihren mediterranen Bezügen, Etymologie und Wortgeschichte | Verlag=Frank & Timme GmbH | Ort= | Jahr=2015 | Seiten=75–81 | Band=Band 24 von Forum: Rumänien, Culinaria balcanica, herausgegeben von Thede Kahl, Peter Mario Kreuter, Christina Vogel | ISBN=9783732901388}}.", "en")
    ''
    >>> clean_html_input('<ref name="CFC" />', "en")
    ''
    >>> clean_html_input('<ref name="CFC">{{Import:CFC}}</ref>', "en")
    ''
    >>> clean_html_input('<ref name="CFC">{{CFC\\n|foo}}</ref>', "en")
    ''
    >>> clean_html_input("<ref>D'après ''Dictionnaire du tapissier : critique et historique de l’ameublement français, depuis les temps anciens jusqu’à nos jours'', par J. Deville, page 32 ({{Gallica|http://gallica.bnf.fr/ark:/12148/bpt6k55042642/f71.image}})</ref>", "en")
    ''
    >>> clean_html_input("<ref>", "en")
    ''
    >>> clean_html_input("</ref>", "en")
    ''
    >>> clean_html_input('<ref name="Marshall 2001"><sup>he</sup></ref>', "en")
    ''
    >>> clean_html_input('a<references></references>b', "fr")
    'ab'
    >>> clean_html_input('a<references>xcv</references>b', "fr")
    'ab'
    """
    sub = re.sub

    # [[File:...|...]] → ''
    code = sub(
        # Courtesy of Casimir et Hippolyte & Wiktor Stribiżew from https://stackoverflow.com/q/79006887/1117028
        rf"""
        # Match [[
        \[\[

        # Namespace followed by :
        (?:{all_namespaces(locale)}):

        # Match any chars other than [ and ], or any ] that is not immediately followed with another ], or a [
        # that is not immediately followed with [ or one or more digits + ]
        [^][]*(?:](?!])[^][]*|\[(?!\[|\d+\])[^][]*)*

        # Match zero or more occurrences of either [+digit(s)+], or strings between [[ and ]] and then any chars
        # other than [ and ], or any ] that is not immediately followed with another ], or a [ that is not immediately
        # followed with [ or one or more digits + ]
        (?:(?:\[\d+\]|\[\[[^][]*(?:](?!])[^][]*|\[(?!\[)[^][]*)*\]\])[^][]*(?:](?!])[^][]*|\[(?!\[|\d+\])[^][]*)*)*

        # Match ]]
        ]]
        """,
        "",
        code,
        flags=re.VERBOSE,
    )

    # HTML comments (multiline supported)
    # <!-- foo --> → ''
    code = sub(r"(?=<!--)([\s\S]*?-->)", "", code)

    # <ref name="CFC"/> → ''
    code = sub(r"<ref[^>]*/>", "", code)

    # <ref>foo → ''
    # <ref>foo</ref> → ''
    # <ref name="CFC">{{Import:CFC}}</ref> → ''
    # <ref name="CFC"><tag>...</tag></ref> → ''
    code = sub(r"<ref[^>]*/?>[\s\S]*?(?:</\s*ref[^>]*>|$)", "", code)

    # <ref> → ''
    # </ref> → ''
    code = code.replace("<ref>", "").replace("</ref>", "")

    return code


def clean_html_output(html: str, locale: str) -> str:
    """
    >>> clean_html_output('<div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr"><p><span class="form-of-definition use-with-mention"><a href="/wiki/Appendix:Glossary#abbreviation" title="Appendix:Glossary">Abbreviation</a> of <span class="form-of-definition-link"><i class="Latn mention" lang="en"><a href="/wiki/Acre#English" title="Acre">Acre</a></i></span></span>: a <a href="/wiki/state" title="state">state</a> of <span class="Latn" lang="en"><a href="/wiki/Brazil#English" title="Brazil"><b some="attr">Brazil</a></b></span>\\n</p></div>', "en")
    'Abbreviation of <i>Acre</i>: a state of <b>Brazil</b>'
    >>> clean_html_output('<span class="interProject">[[w:Acanthis (mythology)|Wikipedia ]]</span>', "en")  # Acanthis
    ''
    >>> clean_html_output('<em title=Grabowski></em>', "eo")  # kaskedo
    ''
    >>> clean_html_output('<templatestyles src="definición impropia/styles.css" />', "eo")  # -acho
    ''
    >>> clean_html_output('&nbsp;[[:en:Special:Search/volley|<sup class="dewikttm">→&nbsp;en</sup>]][[Kategorie:Übersetzungen (Englisch)]]', "de")  # hüpfen
    ''
    >>> clean_html_output('&nbsp;<sup>→&nbsp;en</sup>', "de")  # hüpfen
    ''
    >>> clean_html_output('&nbsp;<sup style="color:slategray;">→&nbsp;en</sup>', "de")  # hüpfen
    ''
    >>> clean_html_output('<nowiki />', "da")  # ABC
    ''
    """
    # Wipe out inter project links
    html = re.sub(r'<span class="interProject[^>]*>[^<]*</span>', "", html)
    html = re.sub(r"&nbsp;\[\[:.+\]\]", "", html)
    html = re.sub(r"&nbsp;<sup[^>]*>→&nbsp;\w+</sup>", "", html)

    # Purge
    html = html.replace(" <small>[script needed]</small>", "")

    # Remove nowiki tags
    html = re.sub(r"<nowiki[^>]*>", "", html)

    # Apply italic on labels
    html = re.sub(r'<span class="ib-content[^>]*>([^<]*)</span>', r"<i>\1</i>", html)
    html = re.sub(r'<span class="label[^>]*>([^<]*)</span>', r"<i>\1</i>", html)

    # Remove those tags
    html = re.sub(r"</?(?:a|bdi|cite|div|em|li|ol|p|span|strong|templatestyles|ul)[^>]*>", "", html)
    html = html.replace("<hr>", "<br>")

    # Clean-up attributes from those tags
    html = re.sub(r"<(b|dl|i|small|sub|sup)\s+[^>]+>", r"<\1>", html)

    # Remove unwanted categories
    return clean_html_input(html, locale).strip()
