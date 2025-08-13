import logging
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest
from wikitextparser import Section

from wikidict import render
from wikidict.stubs import Word


def test_simple() -> None:
    assert render.main("fr") == 0
    assert render.main("fr", workers=0) == 0
    assert render.main("fr", workers=2) == 0


def test_no_json_file() -> None:
    with patch.object(render, "get_latest_json_file", return_value=None):
        assert render.main("fr") == 1


def test_empty_json_file(tmp_path: Path) -> None:
    file = tmp_path / "test.json"
    file.write_text("{}")
    with patch.object(render, "get_latest_json_file", return_value=file):
        assert render.main("fr") == 1


def test_render_word(page: Callable[[str, str], str]) -> None:
    assert render.render_word(["π", page("π", "fr")], {}, "fr")


def test_render_word_sv_with_almost_empty_definition(page: Callable[[str, str], str]) -> None:
    assert render.render_word(["Götet", page("Götet", "sv")], {}, "sv")


def test_render_word_with_empty_subdefinition(page: Callable[[str, str], str]) -> None:
    details = render.render_word(["test", page("tests-definitions", "fr")], {}, "fr")
    assert details

    defs = details.definitions
    assert defs == {
        "Nom": [
            "<i>(Botanique)</i> Espèce de mauves, grandes plantes laineuses aux feuilles entières ou à 3 lobes et à bordure dentée, et aux fleurs assez grandes de couleur blanc rosé, avec les anthères des étamines rougeâtres.",
            ("Sub sub list with empty definition", ("ok",)),
        ],
    }


def test_find_section_definitions_and_es_replace_defs_list_with_numbered_lists() -> None:
    section = Section(
        "=== {{sustantivo propio|es|género=femenino}} ===\n"
        ";1 archipiélago de 2&nbsp;000 peñascos.\n"
        ";2 países: país ubicado en el archipiélago anterior.\n"
        ";301 Lingüística:\n"
        ":;a: vocablo que titula un artículo de diccionario.\n\n\n"
        ":;b: artículo de un diccionario, enciclopedia u obra de referencia."
    )
    definitions = render.find_section_definitions("Bahamas", section, "es", "es")
    assert definitions == [
        "archipiélago de 2&nbsp;000 peñascos.",
        "países: país ubicado en el archipiélago anterior.",
        "Lingüística:",
        (
            "vocablo que titula un artículo de diccionario.",
            "artículo de un diccionario, enciclopedia u obra de referencia.",
        ),
    ]


@pytest.mark.parametrize("workers", [1, 2, 3])
@pytest.mark.parametrize("keep_unfinished", [True, False])
def test_missing_templates(keep_unfinished: bool, workers: int, caplog: pytest.LogCaptureFixture) -> None:
    """Ensure the "missing templates" feature is working."""

    # Craft wikicode with unsupported templates
    in_words = {
        "a": """
== {{langue|fr}} ==
=== {{S|lettre|fr}} ===
'''a'''
# Première [[lettre]] et première [[voyelle]] de l’[[alphabet latin]] ([[minuscule]]). {{unknown-1|0061}}.
# [[chiffre|Chiffre]] [[hexadécimal]] [[dix]] (minuscule) {{unknown-2|foo|bar|lang=hex}}.
# {{unknown-3}}
""",
        "b": """
== {{langue|fr}} ==
=== {{S|lettre|fr}} ===
'''b'''
# Deuxième [[lettre]] et première [[consonne]] de l’[[alphabet latin]] ([[minuscule]]). {{unknown-1|0062}}.
""",
        "c": """
== {{langue|fr}} ==
=== {{S|lettre|fr}} ===
'''c'''
# Troisième [[lettre]] et deuxième [[consonne]] de l’[[alphabet latin]] ([[minuscule]]). {{unknown-1|0063}}.
# {{unknown-3}}
""",
    }

    # Render
    if keep_unfinished:
        with patch.object(render.utils, "KEEP_UNFINISHED", True):
            words = render.render(in_words, "fr", workers)
    else:
        words = render.render(in_words, "fr", workers)

    # Check warnings
    warnings = [record.getMessage() for record in caplog.get_records("call") if record.levelno == logging.WARNING]
    assert len([w for w in warnings if "Skipped" in w]) == 0 if keep_unfinished else 3
    assert [w for w in warnings if "Skipped" not in w] == [
        "Missing `unknown-1` template support (3 times), example in: `a`, `b`, `c`",
        "Missing `unknown-3` template support (2 times), example in: `a`, `c`",
        "Missing `unknown-2` template support (1 times), example in: `a`",
        "Unhandled templates count: 3",
    ]

    # Check words
    if not keep_unfinished:
        assert not words
        return

    assert words == {
        "a": Word(
            pronunciations=[],
            genders=[],
            etymology=[],
            definitions={
                "Lettre": [
                    "Première lettre et première voyelle de l’alphabet latin (minuscule). {{unknown-1}}.",
                    "Chiffre hexadécimal dix (minuscule) {{unknown-2}}.",
                    "{{unknown-3}}",
                ]
            },
            variants=[],
        ),
        "b": Word(
            pronunciations=[],
            genders=[],
            etymology=[],
            definitions={
                "Lettre": ["Deuxième lettre et première consonne de l’alphabet latin (minuscule). {{unknown-1}}."]
            },
            variants=[],
        ),
        "c": Word(
            pronunciations=[],
            genders=[],
            etymology=[],
            definitions={
                "Lettre": [
                    "Troisième lettre et deuxième consonne de l’alphabet latin (minuscule). {{unknown-1}}.",
                    "{{unknown-3}}",
                ]
            },
            variants=[],
        ),
    }


@pytest.mark.parametrize(
    "locale, lang_src, lang_dst",
    [
        ("fr", "fr", "fr"),
        ("fro", "fr", "fro"),
        ("fr:fro", "fr", "fro"),
        ("fr:it", "fr", "it"),
        ("it:fr", "it", "fr"),
    ],
)
def test_sublang(locale: str, lang_src: str, lang_dst: str, tmp_path: Path) -> None:
    snapshot = "20250401"
    pages = Path(f"data_wikicode-{snapshot}.json")
    words: dict[str, str] = {"a": "b"}

    with patch.dict("os.environ", {"CWD": str(tmp_path)}):
        source_dir = render.get_source_dir(lang_src, lang_dst)
        assert source_dir == tmp_path / "data" / lang_dst / lang_src

        output_file = render.get_output_file(source_dir, snapshot)
        assert output_file == source_dir / f"data-{snapshot}.json"

        with (
            patch.object(render, "get_latest_json_file") as mocked_gljf,
            patch.object(render, "load") as mocked_l,
            patch.object(render, "render") as mocked_r,
            patch.object(render, "save") as mocked_s,
        ):
            mocked_gljf.return_value = pages
            mocked_l.return_value = words
            mocked_r.return_value = words

            render.main(locale, workers=1)
            mocked_gljf.assert_called_once_with(source_dir)
            mocked_l.assert_called_once_with(pages)
            mocked_r.assert_called_once_with(words, locale, 1)
            mocked_s.assert_called_once_with(output_file, words)
