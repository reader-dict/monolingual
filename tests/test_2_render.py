from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest
from wikitextparser import Section

from wikidict import context, render, utils
from wikidict.stubs import Words


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("fr")


def test_no_database() -> None:
    with patch.object(context, "setup_modules_db", return_value=False):
        assert render.main("fr") == 1


def test_no_words(tmp_path: Path) -> None:
    file = tmp_path / "test.json"
    file.write_text("{}")
    with (
        patch.object(context, "setup_modules_db", return_value=True),
        patch.object(render, "load_words", return_value=("", [], [])),
    ):
        assert render.main("fr") == 1


def test_render_word(page: Callable[[str, str], str]) -> None:
    results: Words = {}
    render.render_word(("π", page("π", "fr")), results, "fr")
    assert results


def test_render_word_with_empty_subdefinition(page: Callable[[str, str], str]) -> None:
    results: Words = {}
    render.render_word(("test", page("tests-definitions", "fr")), results, "fr")
    assert results

    defs = results["test"].definitions
    assert defs == {
        "Nom|f.": [
            "<i>(Botanique)</i> Espèce de mauves, grandes plantes laineuses aux feuilles entières ou à 3 lobes et à bordure dentée, et aux fleurs assez grandes de couleur blanc rosé, avec les anthères des étamines rougeâtres.",
            (
                "Sub sub list with empty definition",
                # ("ok",),  # TODO: it seems to be a regression to tackle!
            ),
        ],
        "Synonymes": ["guimauve sauvage", "mauve blanche", "guimauve"],
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
    words: dict[str, str] = {"a": "b"}
    redirections: list[str] = []

    with patch.dict("os.environ", {"CWD": str(tmp_path)}), patch.object(context, "setup_modules_db", return_value=True):
        source_dir = render.get_source_dir(lang_src, lang_dst)
        assert source_dir == tmp_path / "data" / lang_dst / lang_src

        output_file = render.get_output_file(source_dir, snapshot)
        assert output_file == source_dir / f"data-{snapshot}.json"

        with (
            patch.object(render, "load_words") as mocked_lw,
            patch.object(render, "render") as mocked_r,
            patch.object(render, "save") as mocked_s,
        ):
            mocked_lw.return_value = (snapshot, words, [])
            mocked_r.return_value = words

            render.main(locale, workers=1)

            lang_src, lang_dst = utils.guess_locales(locale)
            mocked_lw.assert_called_once_with(lang_src, lang_dst)
            mocked_r.assert_called_once_with(words, redirections, locale, 1, parallelism_start_method="spawn")
            mocked_s.assert_called_once_with(output_file, words)
