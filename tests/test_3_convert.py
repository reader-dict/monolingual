import logging
import os
import shutil
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

import mobi
import pytest
from marisa_trie import Trie

from wikidict import constants, convert
from wikidict.constants import ASSET_CHECKSUM_ALGO
from wikidict.stubs import Variants, Word, Words

WORDS = {
    "empty": Word(),
    "foo": Word(["pron"], ["gender"], ["etyl"], {"Noun": ["def 1", ("sdef 1",)]}),
    "foos": Word(["pron"], ["gender"], ["etyl"], {"Noun": ["def 1", ("sdef 1", ("ssdef 1",))]}, ["baz"]),
    "baz": Word(["pron"], ["gender"], ["etyl"], {"Noun": ["def 1", ("sdef 1",)]}, ["foobar"]),
    "empty1": Word(variants=["foo"]),
    "empty2": Word(variants=["empty1"]),
    "Multiple Etymologies": Word(["pron"], ["gender"], ["etyl 1", ("setyl 1",)], {"Noun": ["def 1", ("sdef 1",)]}),
    "Multiple Etymology": Word(["pron0"], ["gender0"], ["etyl0"], {"Noun": ["def 0"]}, ["Multiple Etymologies"]),
    "GIF": Word(
        ["pron"],
        ["gender"],
        ["etyl"],
        {
            "Noun": [
                '<img style="height:100%;max-height:0.8em;width:auto;vertical-align:bottom"'
                ' src="data:image/gif;base64,R0lGODdhNwAZAIEAAAAAAP///wAAAAAAACwAAAAANwAZAE'
                "AIwwADCAwAAMDAgwgTKlzIUKDBgwUZFnw4cGLDihEvOjSYseFEigQtLhSpsaNGiSdTQgS5kiVG"
                "lwhJeuRoMuHHkDBH1pT4cKdKmSpjUjT50efGnEWTsuxo9KbQnC1TFp051KhNpUid8tR6EijPkC"
                "V3en2J9erLoBjRXl1qVS1amTWn6oSK1WfGpnjDQo1q1Wvbs125PgX5l6zctW1JFgas96/FxYwv"
                'RnQsODHkyXuPDt5aVihYt5pBr9woGrJktmpNfxUYEAA7"/>'
            ]
        },
        ["gif"],
    ),
}


def test_simple(caplog: pytest.LogCaptureFixture, tmp_path: Path) -> None:
    with caplog.at_level(logging.DEBUG):
        assert convert.main("fr") == 0

        # Check Mobi warnings
        assert all(
            "media file not found" not in record.getMessage()
            for record in caplog.records
            if record.levelno < logging.WARNING
        )

        # Check PyGlossary logging filters
        assert not [record.getMessage() for record in caplog.records if record.levelno >= logging.WARNING]

    # Check for all dictionaries
    output_dir = Path(os.environ["CWD"]) / "data" / "fr" / "fr" / "output"

    count = 0
    for file in [
        "dict-fr-fr{etym}.df",  # DictFile
        "dict-fr-fr{etym}.df.bz2",  # DictFile bz2
        "dictorg-fr-fr{etym}.zip",  # DICT.org
        "dicthtml-fr-fr{etym}.zip",  # Kobo
        "dict-fr-fr{etym}.mobi.zip",  # Mobi
        "dict-fr-fr{etym}.zip",  # StarDict
    ]:
        for etym in ["", "-noetym"]:
            fname = file.format(etym=etym)
            assert (output_dir / fname).is_file()
            assert (output_dir / f"{fname}.{ASSET_CHECKSUM_ALGO}").is_file()
            count += 2

    assert count == 24

    dicthtml = output_dir / "dicthtml-fr-fr.zip"
    mobi_file = output_dir / "dict-fr-fr.mobi.zip"
    stardict = output_dir / "dict-fr-fr.zip"

    # Check the Kobo ZIP content
    expected_files = [
        "11.html",
        constants.ZIP_WORDS_COUNT,
        constants.ZIP_WORDS_SNAPSHOT,
        "aa.html",
        "ac.html",
        "ba.html",
        "bo.html",
        "co.html",
        "de.html",
        "dj.html",
        "du.html",
        "ef.html",
        "em.html",
        "en.html",
        "ge.html",
        "gr.html",
        "gè.html",
        "ic.html",
        "ko.html",
        "mi.html",
        "mu.html",
        "na.html",
        "pi.html",
        "pr.html",
        "ra.html",
        "sa.html",
        "si.html",
        "sl.html",
        "te.html",
        "ve.html",
        "words",
        "ép.html",
        "œc.html",
        "πa.html",
    ]
    expected_trie_keys = [
        "-aux",
        "-eresse",
        "42",
        "5E",
        "Bogotanais",
        "DES",
        "Slovène",
        "a",
        "accueil",
        "acrologie",
        "barbe à papa",
        "base",
        "bath",
        "chacune",
        "colligeait",
        "colliger",
        "corollaires",
        "corps portant",
        "djed",
        "dubitatif",
        "effluve",
        "employer",
        "en",
        "encyclopædie",
        "geler",
        "greffier",
        "gèlent",
        "ich",
        "koro",
        "minute",
        "minuter",
        "minutes",
        "mutiner",
        "naguère",
        "pinyin",
        "précepte",
        "rance",
        "sapristi",
        "silicone",
        "suis",
        "tests-definitions",
        "venoient",
        "éperon",
        "œcuménique",
        "π",
    ]
    with ZipFile(dicthtml) as fh:
        assert sorted(fh.namelist()) == expected_files

        # testfile returns the name of the first corrupt file, or None
        errors = fh.testzip()
        assert errors is None

        # Check the trie
        trie = Trie()
        trie.map(fh.read("words"))
        assert sorted(trie.keys()) == expected_trie_keys

    # Check the StarDict ZIP content
    expected_files = [
        "dict-data.dict.dz",
        "dict-data.idx",
        "dict-data.ifo",
        "dict-data.syn",
        "res/db28a816.gif",
    ]
    expected_ifo_lines = [
        "StarDict's dict ifo file",
        "version=3.0.0",
        "bookname=reader.dict FR",
        "wordcount=39",
        "idxfilesize=619",
        "sametypesequence=h",
        "synwordcount=5",
        "website=https://www.reader-dict.com",
        "date=2020-12-17",
        f"description=© reader.dict {datetime.now(tz=UTC).year}",
        "lang=fr-fr",
    ]
    with ZipFile(stardict) as fh:
        assert sorted(fh.namelist()) == expected_files

        # testfile returns the name of the first corrupt file, or None
        errors = fh.testzip()
        assert errors is None

        ifo = fh.read("dict-data.ifo").decode()
        assert ifo.splitlines() == expected_ifo_lines

    # Check the Mobi content
    with ZipFile(mobi_file) as fh:
        fh.extract(mobi_file.name.removesuffix(".zip"), tmp_path)
    tempdir, _ = mobi.extract(str(tmp_path / mobi_file.name.removesuffix(".zip")))
    files = sorted(path.relative_to(tempdir).as_posix() for path in Path(tempdir).glob("**/*"))
    expected_files = [
        "HDImages",
        "kindlegenbuild.log",
        "mobi7",
        "mobi7/Images",
        "mobi7/Images/cover00022.jpeg",
        "mobi7/Images/image00021.gif",
        "mobi7/Images/image00024.jpeg",
        "mobi7/book.html",
        "mobi7/content.opf",
        "mobi7/toc.ncx",
    ]
    try:
        assert files == expected_files
    finally:
        shutil.rmtree(tempdir)


def test_no_json_file() -> None:
    with patch.object(convert, "get_latest_json_file", return_value=None):
        assert convert.main("fr") == 1


@pytest.mark.dependency()
@pytest.mark.parametrize(
    "formatter, filename, include_etymology",
    [
        (convert.DictFileFormat, "dict-fr-fr.df", True),
        (convert.DictFileFormat, "dict-fr-fr-noetym.df", False),
        (convert.KoboFormat, "dicthtml-fr-fr.zip", True),
        (convert.KoboFormat, "dicthtml-fr-fr-noetym.zip", False),
    ],
)
def test_generate_primary_dict(formatter: type[convert.BaseFormat], filename: str, include_etymology: bool) -> None:
    output_dir = Path(os.environ["CWD"]) / "data" / "fr" / "fr"
    variants = convert.make_variants(WORDS)
    convert.run_formatter(
        formatter,
        "fr",
        output_dir,
        WORDS,
        variants,
        "20201218",
        include_etymology=include_etymology,
    )

    assert (output_dir / filename).is_file()


@pytest.mark.parametrize(
    "formatter, filename, include_etymology",
    [
        (convert.BZ2DictFileFormat, "dict-fr-fr.df.bz2", True),
        (convert.BZ2DictFileFormat, "dict-fr-fr-noetym.df.bz2", False),
        (convert.DictOrgFormat, "dictorg-fr-fr.zip", True),
        (convert.DictOrgFormat, "dictorg-fr-fr-noetym.zip", False),
        (convert.MobiFormat, "dict-fr-fr.mobi", True),
        (convert.MobiFormat, "dict-fr-fr-noetym.mobi", False),
        (convert.StarDictFormat, "dict-fr-fr.zip", True),
        (convert.StarDictFormat, "dict-fr-fr-noetym.zip", False),
    ],
)
@pytest.mark.dependency(
    depends=[
        "test_generate_primary_dict[DictFileFormat-dict-fr-fr.df]",
        "test_generate_primary_dict[DictFileFormat-dict-fr-fr-noetym.df]",
    ]
)
def test_generate_secondary_dict(formatter: type[convert.BaseFormat], filename: str, include_etymology: bool) -> None:
    output_dir = Path(os.environ["CWD"]) / "data" / "fr" / "fr"
    convert.run_formatter(
        formatter,
        "fr",
        output_dir,
        {},
        {},
        "20201218",
        include_etymology=include_etymology,
    )
    assert (output_dir / filename).is_file()


FORMATTED_WORD_KOBO = """\
<w><p><a name="Multiple Etymologies" /><b>Multiple Etymologies</b> pron <i>gender</i>.<br/><br/><b>Noun</b><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol><p>etyl 1</p><ol><li>setyl 1</li></ol><br/></p><var><variant name="multiple etymology"/></var></w>
"""
FORMATTED_WORD_KOBO_NO_ETYMOLOGY = """\
<w><p><a name="Multiple Etymologies" /><b>Multiple Etymologies</b> pron <i>gender</i>.<br/><br/><b>Noun</b><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol></p><var><variant name="multiple etymology"/></var></w>
"""
FORMATTED_WORD_DICTFILE = """\
@ Multiple Etymologies
: pron <i>gender</i>.
& Multiple Etymology
<html><p><b>Noun</b></p><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol><p>etyl 1</p><ol><li>setyl 1</li></ol><br/></html>\


"""
FORMATTED_WORD_DICTFILE_NO_ETYMOLOGY = """\
@ Multiple Etymologies
: pron <i>gender</i>.
& Multiple Etymology
<html><p><b>Noun</b></p><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol></html>\


"""
FORMATTED_WORD_JSONVOLUME_NO_ETYMOLOGY = """"""


@pytest.mark.parametrize(
    "formatter, include_etymology, expected",
    [
        (convert.KoboFormat, True, FORMATTED_WORD_KOBO),
        (convert.KoboFormat, False, FORMATTED_WORD_KOBO_NO_ETYMOLOGY),
        (convert.DictFileFormat, True, FORMATTED_WORD_DICTFILE),
        (convert.DictFileFormat, False, FORMATTED_WORD_DICTFILE_NO_ETYMOLOGY),
        (convert.JSONVolumeFormat, True, FORMATTED_WORD_JSONVOLUME_NO_ETYMOLOGY),
    ],
)
def test_word_rendering(
    formatter: type[convert.BaseFormat],
    include_etymology: bool,
    expected: str,
) -> None:
    output_dir = Path(os.environ["CWD"]) / "data" / "fr" / "fr"
    cls = formatter(
        "fr",
        output_dir,
        WORDS,
        convert.make_variants(WORDS),
        "20221212",
        include_etymology=include_etymology,
    )

    content = next(cls.handle_word("Multiple Etymologies", WORDS))
    assert content == expected


WORDS_VARIANTS_FR = {
    "estre": Word(pronunciations=["\\ɛtʁ\\"], definitions={"Verbe": ["Définition de 'estre'."]}),
    "être": Word(pronunciations=["\\ɛtʁ\\"], genders=["m"], definitions={"Verbe": ["Définition de 'être'."]}),
    "suis": Word(pronunciations=["\\sɥi\\"], variants=["suivre", "être", "estre"]),
    "suivre": Word(pronunciations=["\\sɥivʁ\\"], definitions={"Verbe": ["Définition de 'suivre'."]}),
}
WORDS_VARIANTS_FR_2 = {
    "loches": Word(variants=["loche", "locher"]),
    "loche": Word(definitions={"Nom": ["Définitions de 'loche'."]}, variants=["locher"]),
    "locher": Word(definitions={"Verbe": ["Définitions de 'locher'."]}),
    "Loches": Word(definitions={"Nom Propre": ["Définitions de 'Loches'."]}),
}
WORDS_VARIANTS_ES = {
    "gastadan": Word(variants=["gastada"]),
    "gastada": Word(variants=["gastado"]),
    "gastado": Word(variants=["gastar"]),
    "gastar": Word(definitions={"Verb": ["Definition of 'gastar'."]}),
}
WORDS_VARIANTS_ES_2 = {
    "-foba": Word(variants=["-fobo"]),
    "-fobas": Word(variants=["-foba", "-fobo"]),
    "-fobo": Word(definitions={"Suffix": ["-phobe", "-phobic"]}),
}
WORDS_VARIANTS_RU = {
    "ФСБ": Word(definitions={"Значение": ["Definition of 'ФСБ'."]}),
}


def test_make_variants() -> None:
    assert convert.make_variants(WORDS_VARIANTS_FR) == {"suivre": ["suis"], "estre": ["suis"], "être": ["suis"]}
    assert convert.make_variants(WORDS_VARIANTS_ES) == {
        "gastada": ["gastadan"],
        "gastado": ["gastada"],
        "gastar": ["gastado"],
    }


def test_kobo_format_variants_different_prefix_with_definition(tmp_path: Path) -> None:
    words = deepcopy(WORDS_VARIANTS_FR)
    words["suis"].definitions["Nom"] = ["Définition de 'suis'."]
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat("fr", tmp_path, words, variants, "20250322")

    assert formatter.make_groups(words) == {
        "es": {"estre": words["estre"]},
        "êt": {"être": words["être"]},
        "su": {"suis": words["suis"], "suivre": words["suivre"]},
    }

    estre = "".join(formatter.handle_word("estre", words))
    être = "".join(formatter.handle_word("être", words))
    suis = "".join(formatter.handle_word("suis", words))
    suivre = "".join(formatter.handle_word("suivre", words))
    assert suis.count('<a name="suis" />') == 3
    assert "<b>estre</b>" in suis
    assert "<b>suivre</b>" not in suis
    assert "<b>suis</b>" in suis
    assert "<b>être</b>" in suis
    assert "variant" not in estre  # Because group prefixes are differents
    assert "variant" not in suis  # Because variant == word
    assert "variant" not in être  # Because group prefixes are differents
    assert '<var><variant name="suis"/></var>' in suivre  # Because group prefixes are the same


def test_kobo_format_variants_different_prefix_without_definition(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_FR
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat("fr", tmp_path, words, variants, "20250322")

    assert formatter.make_groups(words) == {
        "es": {"estre": words["estre"]},
        "êt": {"être": words["être"]},
        "su": {"suis": words["suis"], "suivre": words["suivre"]},
    }

    estre = "".join(formatter.handle_word("estre", words))
    être = "".join(formatter.handle_word("être", words))
    suis = "".join(formatter.handle_word("suis", words))
    suivre = "".join(formatter.handle_word("suivre", words))
    assert suis.count('<a name="suis" />') == 2
    assert "<b>estre</b>" in suis
    assert "<b>suivre</b>" not in suis
    assert "<b>être</b>" in suis
    assert "variant" not in estre  # Because group prefixes are differents
    assert "variant" not in suis  # Because variant == word
    assert "variant" not in être  # Because group prefixes are differents
    assert '<var><variant name="suis"/></var>' in suivre  # Because group prefixes are the same


def test_kobo_format_variants_from_lowercased_word(tmp_path: Path) -> None:
    """See issue #2579."""
    words = WORDS_VARIANTS_FR_2
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat("fr", tmp_path, words, variants, "20260121")

    Loches = "".join(formatter.handle_word("Loches", words))
    assert '<var><variant name="loches"/></var>' in Loches


def test_kobo_format_variants_empty_variant_level_1(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_ES
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat("es", tmp_path, words, variants, "20250322")

    assert formatter.make_groups(words) == {
        "ga": {
            "gastada": words["gastada"],
            "gastadan": words["gastadan"],
            "gastado": words["gastado"],
            "gastar": words["gastar"],
        }
    }

    gastadan = "".join(formatter.handle_word("gastadan", words))
    gastada = "".join(formatter.handle_word("gastada", words))
    gastado = "".join(formatter.handle_word("gastado", words))
    gastar = "".join(formatter.handle_word("gastar", words))
    assert not gastadan
    assert not gastada
    assert not gastado
    assert '<var><variant name="gastada"/><variant name="gastado"/></var>' in gastar


def test_kobo_format_variants_duplicates(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_ES_2
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat("es", tmp_path, words, variants, "20250702")

    assert formatter.make_groups(words) == {
        "11": {
            "-foba": words["-foba"],
            "-fobas": words["-fobas"],
            "-fobo": words["-fobo"],
        }
    }

    foba = "".join(formatter.handle_word("-foba", words))
    fobas = "".join(formatter.handle_word("-fobas", words))
    fobo = "".join(formatter.handle_word("-fobo", words))
    assert not foba
    assert not fobas
    assert '<var><variant name="-foba"/><variant name="-fobas"/></var>' in fobo


def test_kindle_format_variants_from_uppercase_only_word(tmp_path: Path) -> None:
    """See issue #2623."""
    words = WORDS_VARIANTS_RU
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormatForMobi("ru", tmp_path, words, variants, "20260122")

    ФСБ = "".join(formatter.handle_word("ФСБ", words))
    assert "@ ФСБ" in ФСБ
    assert "& фсб" in ФСБ


def test_df_format(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_FR
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormat("fr", tmp_path, words, variants, "20250323")
    formatter.process()
    output = formatter.dictionary_file(formatter.output_file)

    assert (
        output.read_text(encoding="utf-8")
        == r"""@ estre
: \ɛtʁ\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'estre'.</li></ol></html>

@ être
: \ɛtʁ\ <i>m</i>.
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'être'.</li></ol></html>

@ suivre
: \sɥivʁ\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'suivre'.</li></ol></html>

"""
    )


def test_df_format_variants_different_prefix_with_definition(tmp_path: Path) -> None:
    words = deepcopy(WORDS_VARIANTS_FR)
    words["suis"].definitions["Nom"] = ["Définition de 'suis'."]
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormat("fr", tmp_path, words, variants, "20250323")

    estre = "".join(formatter.handle_word("estre", words))
    être = "".join(formatter.handle_word("être", words))
    suis = "".join(formatter.handle_word("suis", words))
    suivre = "".join(formatter.handle_word("suivre", words))
    assert "@ suis" in suis
    assert ": <b>estre</b>" not in suis
    assert ": <b>suivre</b>" not in suis
    assert ": <b>suis</b>" not in suis
    assert ": <b>être</b>" not in suis
    assert estre.count("&") == 1 and "& suis" in estre
    assert "&" not in suis  # Because variant == word
    assert être.count("&") == 1 and "& suis" in être
    assert "& suis" in suivre


def test_df_format_variants_different_prefix_without_definition(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_FR
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormat("fr", tmp_path, words, variants, "20250323")

    estre = "".join(formatter.handle_word("estre", words))
    être = "".join(formatter.handle_word("être", words))
    suis = "".join(formatter.handle_word("suis", words))
    suivre = "".join(formatter.handle_word("suivre", words))
    assert "@ suis" not in suis
    assert ": <b>estre</b>" not in suis
    assert ": <b>suivre</b>" not in suis
    assert ": <b>être</b>" not in suis
    assert estre.count("&") == 1 and "& suis" in estre
    assert "&" not in suis  # Because variant == word
    assert être.count("&") == 1 and "& suis" in être
    assert "& suis" in suivre


def test_df_format_variants_empty_variant_level_1(tmp_path: Path) -> None:
    words = WORDS_VARIANTS_ES
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormat("es", tmp_path, words, variants, "20250323")

    gastadan = "".join(formatter.handle_word("gastadan", words))
    gastada = "".join(formatter.handle_word("gastada", words))
    gastado = "".join(formatter.handle_word("gastado", words))
    gastar = "".join(formatter.handle_word("gastar", words))
    assert not gastadan
    assert not gastada
    assert not gastado
    assert "& gastada" in gastar
    assert "& gastado" in gastar


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
    pages = Path(f"data-{snapshot}.json")
    words: Words = {}
    variants: Variants = {}

    with (
        patch.dict("os.environ", {"CWD": str(tmp_path)}),
        patch.object(convert, "get_latest_json_file") as mocked_gljf,
        patch.object(convert, "load") as mocked_l,
        patch.object(convert, "make_variants") as mocked_mv,
        patch.object(convert, "distribute_workload") as mocked_dw,
        patch.object(convert, "run_mobi_formatter") as mocked_rmf,
    ):
        mocked_gljf.return_value = pages
        mocked_l.return_value = words
        mocked_mv.return_value = variants
        source_dir = tmp_path / "data" / lang_dst / lang_src

        convert.main(locale)
        mocked_gljf.assert_called_once_with(source_dir)
        mocked_l.assert_called_once_with(pages)
        mocked_mv.assert_called_once_with(words)

        args = (source_dir / "output", snapshot, locale, words, variants)
        for include_etymology in [False, True]:
            mocked_dw.assert_any_call(convert.get_primary_formatters(), *args, include_etymology=include_etymology)
            mocked_dw.assert_any_call(convert.get_secondary_formatters(), *args, include_etymology=False)
            mocked_rmf.assert_any_call(*args, include_etymology=False)
        assert mocked_dw.call_count == 4
        assert mocked_rmf.call_count == 2


@pytest.mark.parametrize("format", list(convert.FORMATTERS.keys()))
def test_format(format: str) -> None:
    primary, secondary, mobi_run = convert.get_formatters(format)
    assert primary == {convert.FORMATTERS[format][0]}
    if secondary:
        assert secondary == {convert.FORMATTERS[format][1]}
    assert not mobi_run


@pytest.mark.parametrize("format", ["mobi", "kindle"])
def test_format_mobi(format: str) -> None:
    primary, secondary, mobi_run = convert.get_formatters(format)
    assert not primary
    assert not secondary
    assert mobi_run


@pytest.mark.parametrize("format", ["", "all"])
def test_format_all(format: str) -> None:
    primary, secondary, mobi_run = convert.get_formatters(format)
    assert primary == convert.get_primary_formatters()
    assert secondary == convert.get_secondary_formatters()
    assert mobi_run


def test_format_unknown() -> None:
    primary, secondary, mobi_run = convert.get_formatters("unknown")
    assert not primary
    assert not secondary
    assert not mobi_run


def test_formats() -> None:
    primary, secondary, mobi_run = convert.get_formatters("df,mobi")
    assert primary == {convert.FORMATTERS["df"][0]}
    assert secondary == {convert.FORMATTERS["df"][1]}
    assert mobi_run
