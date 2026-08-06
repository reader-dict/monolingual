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

from wikidict import constants, convert, utils
from wikidict.constants import ASSET_CHECKSUM_ALGO
from wikidict.stubs import Variants, Word, Words

WORDS = {
    "empty": Word(),
    "foo": Word(["pron"], [], ["etyl"], {"Noun": ["def 1", ("sdef 1",)]}),
    "foos": Word(["pron"], [], ["etyl"], {"Noun": ["def 1", ("sdef 1", ("ssdef 1",))]}, ["baz"]),
    "baz": Word(["pron"], [], ["etyl"], {"Noun": ["def 1", ("sdef 1",)]}, ["foobar"]),
    "empty1": Word(variants=["foo"]),
    "empty2": Word(variants=["empty1"]),
    "Multiple Etymologies": Word(["pron"], [], ["etyl 1", ("setyl 1",)], {"Noun|m": ["def 1", ("sdef 1",)]}),
    "Multiple Etymology": Word(["pron0"], [], ["etyl0"], {"Noun": ["def 0"]}, ["Multiple Etymologies"]),
    "GIF": Word(
        ["pron"],
        [],
        ["etyl"],
        {
            "Noun": [
                (
                    '<img style="height:100%;max-height:0.8em;width:auto;vertical-align:bottom"'
                    ' src="data:image/gif;base64,R0lGODdhNwAZAIEAAAAAAP///wAAAAAAACwAAAAANwAZAE'
                    "AIwwADCAwAAMDAgwgTKlzIUKDBgwUZFnw4cGLDihEvOjSYseFEigQtLhSpsaNGiSdTQgS5kiVG"
                    "lwhJeuRoMuHHkDBH1pT4cKdKmSpjUjT50efGnEWTsuxo9KbQnC1TFp051KhNpUid8tR6EijPkC"
                    "V3en2J9erLoBjRXl1qVS1amTWn6oSK1WfGpnjDQo1q1Wvbs125PgX5l6zctW1JFgas96/FxYwv"
                    'RnQsODHkyXuPDt5aVihYt5pBr9woGrJktmpNfxUYEAA7"/>'
                )
            ]
        },
        ["gif"],
    ),
}


def test_simple(tmp_path: Path) -> None:
    setup_logging_original = utils.setup_logging

    def setup_logging(*args: str, **kwargs: str) -> None:
        setup_logging_original("fr", "fr", folder=tmp_path)

    with patch.object(utils, "setup_logging", setup_logging):
        assert convert.main("fr") == 0

    log_file = tmp_path / "fr" / "fr.log"
    log_records = log_file.read_text().splitlines()

    # Ensure summaries are properly handled
    assert (
        len([record for record in log_records if "Effective words + variants" in record])
        == 2 * 2  # (KoboFormat + DictFileFormat) * (etym + noetym)
    )

    # Check for all dictionary files
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
        "mobi7",
        "mobi7/Images",
        "mobi7/Images/cover00009.jpeg",
        "mobi7/Images/image00010.gif",
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
        "test_generate_primary_dict[DictFileFormat-dict-fr-fr.df-True]",
        "test_generate_primary_dict[DictFileFormat-dict-fr-fr-noetym.df-False]",
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
<w><p><a name="Multiple Etymologies" /><b>Multiple Etymologies</b> pron<br/><br/><b>Noun</b> <i>m</i><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol><p>etyl 1</p><ol><li>setyl 1</li></ol><br/></p><var><variant name="multiple etymology"/></var></w>
"""
FORMATTED_WORD_KOBO_NO_ETYMOLOGY = """\
<w><p><a name="Multiple Etymologies" /><b>Multiple Etymologies</b> pron<br/><br/><b>Noun</b> <i>m</i><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol></p><var><variant name="multiple etymology"/></var></w>
"""
FORMATTED_WORD_DICTFILE = """\
@ Multiple Etymologies
: pron
& Multiple Etymology
<html><p><b>Noun</b> <i>m</i></p><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol><p>etyl 1</p><ol><li>setyl 1</li></ol><br/>\


"""
FORMATTED_WORD_DICTFILE_NO_ETYMOLOGY = """\
@ Multiple Etymologies
: pron
& Multiple Etymology
<html><p><b>Noun</b> <i>m</i></p><ol><li>def 1</li><ol style="list-style-type:lower-alpha"><li>sdef 1</li></ol></ol>\


"""
FORMATTED_WORD_JSONVOLUME_NO_ETYMOLOGY = """"""


@pytest.mark.parametrize(
    "formatter, include_etymology, expected",
    [
        pytest.param(convert.KoboFormat, True, FORMATTED_WORD_KOBO, id="kobo"),
        pytest.param(convert.KoboFormat, False, FORMATTED_WORD_KOBO_NO_ETYMOLOGY, id="kobo-noetym"),
        pytest.param(convert.DictFileFormat, True, FORMATTED_WORD_DICTFILE, id="df"),
        pytest.param(convert.DictFileFormat, False, FORMATTED_WORD_DICTFILE_NO_ETYMOLOGY, id="df-noetym"),
        pytest.param(convert.JSONVolumeFormat, True, FORMATTED_WORD_JSONVOLUME_NO_ETYMOLOGY, id="jsonvolume"),
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


VARIANTS_FR = {
    "estre": Word(pronunciations=["\\ɛtʁ\\"], definitions={"Verbe": ["Définition de 'estre'."]}),
    "être": Word(pronunciations=["\\ɛtʁ\\"], definitions={"Verbe": ["Définition de 'être'."]}),
    "suis": Word(pronunciations=["\\sɥi\\"], variants=["suivre", "être", "estre"]),
    "suivre": Word(pronunciations=["\\sɥivʁ\\"], definitions={"Verbe": ["Définition de 'suivre'."]}),
}
VARIANTS_FR_2 = deepcopy(VARIANTS_FR)
VARIANTS_FR_2["suis"].definitions["Nom"] = ["Définition de 'suis'."]
VARIANTS_FR_3 = {
    "loches": Word(variants=["loche", "locher"]),
    "loche": Word(definitions={"Nom": ["Définitions de 'loche'."]}, variants=["locher"]),
    "locher": Word(definitions={"Verbe": ["Définitions de 'locher'."]}),
    "Loches": Word(definitions={"Nom Propre": ["Définitions de 'Loches'."]}),
}
VARIANTS_ES = {
    "gastadan": Word(variants=["gastada"]),
    "gastada": Word(variants=["gastado"]),
    "gastado": Word(variants=["gastar"]),
    "gastar": Word(definitions={"Verb": ["Definition of 'gastar'."]}),
}
VARIANTS_ES_2 = {
    "-foba": Word(variants=["-fobo"]),
    "-fobas": Word(variants=["-foba", "-fobo"]),
    "-fobo": Word(definitions={"Suffix": ["-phobe", "-phobic"]}),
}
VARIANTS_RU = {
    "ФСБ": Word(definitions={"Значение": ["Definition of 'ФСБ'."]}),
}


@pytest.mark.parametrize(
    "words, expected",
    [
        pytest.param(VARIANTS_FR, {"suivre": {"suis"}, "estre": {"suis"}, "être": {"suis"}}, id="FR"),
        pytest.param(VARIANTS_FR_2, {"suivre": {"suis"}, "être": {"suis"}, "estre": {"suis"}}, id="FR-2"),
        pytest.param(VARIANTS_FR_3, {"loche": {"loches"}, "locher": {"loche", "loches"}}, id="FR-3"),
        pytest.param(VARIANTS_ES, {"gastada": {"gastadan"}, "gastado": {"gastada"}, "gastar": {"gastado"}}, id="ES"),
        pytest.param(VARIANTS_ES_2, {"-foba": {"-fobas"}, "-fobo": {"-foba", "-fobas"}}, id="ES-2"),
        pytest.param(VARIANTS_RU, {}, id="RU"),
    ],
)
def test_make_variants(words: Words, expected: dict[str, set[str]]) -> None:
    assert convert.make_variants(words) == expected


@pytest.mark.parametrize(
    "locale, words, word, expected",
    [
        pytest.param(
            "es",
            VARIANTS_ES,
            "gastadan|gastada|gastado|gastar",
            """\
@ gastar
& gastada
& gastado
<html><p><b>Verb</b></p><ol><li>Definition of 'gastar'.</li></ol>

""",
            id="variants with empty variant level 1",
        ),
        pytest.param(
            "es",
            VARIANTS_ES_2,
            "-foba|-fobas|-fobo",
            """\
@ -fobo
& -foba
& -fobas
<html><p><b>Suffix</b></p><ol><li>-phobe</li><li>-phobic</li></ol>

""",
            id="variants duplicates",
        ),
        pytest.param(
            "fr",
            VARIANTS_FR,
            "estre|être|suis|suivre",
            """\
@ estre
: \\ɛtʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'estre'.</li></ol>


@ être
: \\ɛtʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'être'.</li></ol>



@ suivre
: \\sɥivʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'suivre'.</li></ol>

""",
            id="variants with different prefix without definition",
        ),
        pytest.param(
            "fr",
            VARIANTS_FR_2,
            "estre|être|suis|suivre",
            """\
@ estre
: \\ɛtʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'estre'.</li></ol>


@ être
: \\ɛtʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'être'.</li></ol>


@ suis
: \\sɥi\\
<html><p><b>Nom</b></p><ol><li>Définition de 'suis'.</li></ol>


@ suivre
: \\sɥivʁ\\
& suis
<html><p><b>Verbe</b></p><ol><li>Définition de 'suivre'.</li></ol>

""",
            id="variants with different prefix with definition",
        ),
    ],
)
def test_df_format(locale: str, words: Words, word: str, expected: str, tmp_path: Path) -> None:
    variants = convert.make_variants(words)
    formatter = convert.DictFileFormat(locale, tmp_path, words, variants, "20250323")

    output = ["\n".join(formatter.handle_word(w, words)) for w in word.split("|")]
    assert "\n".join(output).lstrip() == expected


@pytest.mark.parametrize(
    "locale, words, word, expected",
    [
        pytest.param(
            "es",
            VARIANTS_ES,
            "gastadan|gastada|gastado|gastar",
            """\
<w><p><a name="gastar" /><b>gastar</b><br/><br/><b>Verb</b><ol><li>Definition of 'gastar'.</li></ol></p><var><variant name="gastada"/><variant name="gastado"/></var></w>
""",
            id="variants with empty variant level 1",
        ),
        pytest.param(
            "es",
            VARIANTS_ES_2,
            "-foba|-fobas|-fobo",
            """\
<w><p><a name="-fobo" /><b>-fobo</b><br/><br/><b>Suffix</b><ol><li>-phobe</li><li>-phobic</li></ol></p><var><variant name="-foba"/><variant name="-fobas"/></var></w>
""",
            id="variants duplicates",
        ),
        pytest.param(
            "fr",
            VARIANTS_FR,
            "estre|être|suis|suivre",
            """\
<w><p><a name="estre" /><b>estre</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'estre'.</li></ol></p></w>

<w><p><a name="être" /><b>être</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'être'.</li></ol></p></w>

<w><p><a name="suis" /><b>estre</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'estre'.</li></ol></p></w>

<w><p><a name="suis" /><b>être</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'être'.</li></ol></p></w>

<w><p><a name="suivre" /><b>suivre</b> \\sɥivʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'suivre'.</li></ol></p><var><variant name="suis"/></var></w>
""",
            id="variants with different prefix without definition",
        ),
        pytest.param(
            "fr",
            VARIANTS_FR_2,
            "estre|être|suis|suivre",
            """\
<w><p><a name="estre" /><b>estre</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'estre'.</li></ol></p></w>

<w><p><a name="être" /><b>être</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'être'.</li></ol></p></w>

<w><p><a name="suis" /><b>estre</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'estre'.</li></ol></p></w>

<w><p><a name="suis" /><b>suis</b> \\sɥi\\<br/><br/><b>Nom</b><ol><li>Définition de 'suis'.</li></ol></p></w>

<w><p><a name="suis" /><b>être</b> \\ɛtʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'être'.</li></ol></p></w>

<w><p><a name="suivre" /><b>suivre</b> \\sɥivʁ\\<br/><br/><b>Verbe</b><ol><li>Définition de 'suivre'.</li></ol></p><var><variant name="suis"/></var></w>
""",
            id="variants with different prefix with definition",
        ),
        pytest.param(
            "fr",
            VARIANTS_FR_3,
            "Loches",
            """\
<w><p><a name="Loches" /><b>Loches</b><br/><br/><b>Nom Propre</b><ol><li>Définitions de 'Loches'.</li></ol></p><var><variant name="loches"/></var></w>
""",
            id="variants from lowercased word (issue #2579)",
        ),
    ],
)
def test_kobo_format(locale: str, words: Words, word: str, expected: str, tmp_path: Path) -> None:
    variants = convert.make_variants(words)
    formatter = convert.KoboFormat(locale, tmp_path, words, variants, "20250322")

    output = ["\n".join(formatter.handle_word(w, words)) for w in word.split("|")]
    assert "\n".join(output).lstrip() == expected


@pytest.mark.parametrize(
    "locale, words, word, expected",
    [
        pytest.param(
            "ru",
            VARIANTS_RU,
            "ФСБ",
            """\
@ ФСБ
& фсб
<html><p><b>Значение</b></p><ol><li>Definition of 'ФСБ'.</li></ol>

""",
            id="RU: variants from uppercase-only word (issue #2623)",
        ),
    ],
)
def test_kindle_format(locale: str, words: Words, word: str, expected: str, tmp_path: Path) -> None:
    variants = convert.make_variants(words)
    formatter = convert.MobiFormat(locale, tmp_path, words, variants, "20260122")

    output = ["\n".join(formatter.handle_word(w, words)) for w in word.split("|")]
    assert "\n".join(output).lstrip() == expected


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
            mocked_dw.assert_any_call(
                convert.get_secondary_formatters(),
                *args,
                include_etymology=False,
                sequential=True,
            )
        assert mocked_dw.call_count == 4


@pytest.mark.parametrize("format", list(convert.FORMATTERS.keys()))
def test_format(format: str) -> None:
    primary, secondary = convert.get_formatters(format)
    assert primary == {convert.FORMATTERS[format][0]}
    if secondary:
        assert secondary == {convert.FORMATTERS[format][1]}


@pytest.mark.parametrize("format", ["mobi", "kindle"])
def test_format_mobi(format: str) -> None:
    primary, secondary = convert.get_formatters(format)
    assert primary == {convert.FORMATTERS["mobi"][0]}
    assert secondary == {convert.FORMATTERS["mobi"][1]}


@pytest.mark.parametrize("format", ["", "all"])
def test_format_all(format: str) -> None:
    primary, secondary = convert.get_formatters(format)
    assert primary == convert.get_primary_formatters()
    assert secondary == convert.get_secondary_formatters()


def test_format_unknown() -> None:
    primary, secondary = convert.get_formatters("unknown")
    assert not primary
    assert not secondary


def test_formats() -> None:
    primary, secondary = convert.get_formatters("df,mobi")
    assert primary == {convert.FORMATTERS["df"][0], convert.FORMATTERS["mobi"][0]}
    assert secondary == {convert.FORMATTERS["df"][1], convert.FORMATTERS["mobi"][1]}
