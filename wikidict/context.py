import atexit
import os
import re
from functools import lru_cache
from pathlib import Path

import wikitextprocessor
from wikitextprocessor.dumpparser import add_default_templates
from wikitextprocessor.interwiki import init_interwiki_map

CTX: wikitextprocessor.Wtp
INITIALIZED = False

# To print all Lua warnings & errors:
#    DEBUG_LUA=2 python -m wikidict LOCALE --render
DEBUG_LUA = int(os.getenv("DEBUG_LUA", "0")) > 1


def setup_modules_db(locale: str) -> bool:
    from . import parse, utils

    lang_src, lang_dst = utils.guess_locales(locale, use_log=False)
    source_dir = parse.get_source_dir(lang_src)
    if not (input_file := parse.get_latest_file(source_dir)):
        print("No dump found. Run with --parse first ... ")
        return False

    snapshot = input_file.stem[6:14]
    assert len(snapshot) == 8 and snapshot.isdigit(), repr(snapshot)
    db_path = parse.get_output_file_modules(source_dir, lang_src, lang_dst, snapshot)
    db_path.parent.mkdir(exist_ok=True)
    init(db_path, lang_dst)
    return True


def patch() -> None:
    if DEBUG_LUA:
        return

    # Remove a noisy `print()` statement on error
    assert hasattr(wikitextprocessor.Wtp, "_fmt_errmsg")  # To catch future API changes
    setattr(wikitextprocessor.Wtp, "_fmt_errmsg", lambda *_: None)

    # Remove noisy `print()` statements emitted from Lua code
    # https://github.com/tatuylonen/wikitextprocessor/blob/1ab82dac511a36ad3aa089ff908637d2ddabf5e2/src/wikitextprocessor/lua/mw.lua#L68
    lua_src = Path(wikitextprocessor.__file__).parent / "lua"
    lua_mv = lua_src / "mw.lua"
    lua_mv.write_text(
        lua_mv.read_text()
        .replace(
            '    print("mw.addWarning", text)',
            '    -- print("mw.addWarning", text)',
            count=1,
        )
        .replace(
            '    print("mw.incrementExpensiveFunctionCount")',
            '    -- print("mw.incrementExpensiveFunctionCount")',
            count=1,
        )
    )


def init(db: Path, locale: str) -> None:
    global CTX, INITIALIZED

    if INITIALIZED:
        return

    from . import constants, lang

    patch()

    CTX = wikitextprocessor.Wtp(
        db,
        extension_tags={
            "phonos": {"content": ["phrasing"]},  # Example: [ES] hala
        },
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
    init_interwiki_map(CTX)
    add_default_templates(CTX)

    # Ensure to close the DB connection at exit
    atexit.register(CTX.close_db_conn)

    INITIALIZED = True


def reset(locale: str) -> bool:
    global INITIALIZED

    INITIALIZED = False
    return setup_modules_db(locale)


def new_word(word: str) -> None:
    CTX.start_page(word)


def expand(wikitext: str, locale: str) -> str:
    return clean_html_output(CTX.expand(wikitext, quiet=True), locale)


def adapt_templates(locale: str) -> None:
    from . import lang

    for template, adapter in lang.template_adapters[locale].items():
        if not (page := CTX.get_page(template)):
            raise RuntimeError(f"Module/Template not found in the database: {template!r}")

        assert page.body  # For Mypy

        if (new_body := adapter(page.body)) == page.body:
            print(f"Module/Template body unchanged: {template!r}")
            continue

        CTX.add_page(
            template,
            page.namespace_id,
            new_body,
            redirect_to=page.redirect_to,
            need_pre_expand=page.need_pre_expand,
            model=page.model,
        )


@lru_cache(maxsize=256)
def all_namespaces(locale: str) -> str:
    from .namespaces import namespaces

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
    """
    # Wipe out inter project links
    html = re.sub(r'<span class="interProject[^>]*>[^<]*</span>', "", html)

    # Apply italic on labels
    html = re.sub(r'<span class="ib-content[^>]*>([^<]*)</span>', r"<i>\1</i>", html)
    html = re.sub(r'<span class="label[^>]*>([^<]*)</span>', r"<i>\1</i>", html)

    # Remove those tags
    html = re.sub(r"</?(?:a|bdi|div|em|li|ol|p|span|strong|templatestyles|ul)[^>]*>", "", html)

    # Clean-up attributes from those tags
    html = re.sub(r"<(b|i|small|sub|sup)\s+[^>]+>", r"<\1>", html)

    # Remove unwanted categories
    return clean_html_input(html, locale).strip()
