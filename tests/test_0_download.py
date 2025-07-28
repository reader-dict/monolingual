import logging
import os
import re
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest
import responses

from wikidict import download
from wikidict.constants import BASE_URL, DUMP_URL

WIKTIONARY_INDEX = """<html>
<head><title>Index of /frwiktionary/</title></head>
<body bgcolor="white">
<h1>Index of /frwiktionary/</h1><hr><pre><a href="../">../</a>
<a href="20191120/">20191120/</a>                                          02-Jan-2020 01:29                   -
<a href="20191201/">20191201/</a>                                          21-Jan-2020 01:36                   -
<a href="20191220/">20191220/</a>                                          02-Feb-2020 01:28                   -
<a href="20200101/">20200101/</a>                                          21-Feb-2020 01:38                   -
<a href="20200120/">20200120/</a>                                          02-Mar-2020 01:28                   -
<a href="20200201/">20200201/</a>                                          02-Apr-2020 01:36                   -
<a href="20200220/">20200220/</a>                                          24-Feb-2020 17:32                   -
<a href="20200301/">20200301/</a>                                          09-Mar-2020 03:42                   -
<a href="20200514/">20200514/</a>                                          17-Apr-2020 15:20                   -
<a href="latest/">latest/</a>                                              17-Apr-2020 15:20                   -
</pre><hr></body>
</html>
"""
DUMPS = sorted(re.findall(r'href="(\d+)/"', WIKTIONARY_INDEX))


def cleanup(folder: Path) -> None:
    for file in folder.glob("pages-*.xml"):
        file.unlink()
    for file in folder.glob("pages-*.xml.bz2"):
        file.unlink()


@responses.activate
def test_simple(craft_data: Callable[[str], bytes]) -> None:
    """It should download the Wiktionary dump file and extract it."""

    output_dir = Path(os.environ["CWD"]) / "data" / "fr"

    dump = DUMPS[-1]
    assert dump == "20200514"
    pages_xml = output_dir / f"pages-{dump}.xml"
    pages_bz2 = output_dir / f"pages-{dump}.xml.bz2"

    # Clean-up before we start
    cleanup(output_dir)

    # List of requests responses to falsify:
    #   - fetch_snapshots()
    #   - fetch_pages()
    responses.add(responses.GET, BASE_URL.format(locale="fr"), body=WIKTIONARY_INDEX)
    responses.add(responses.GET, DUMP_URL.format(locale="fr", snapshot=dump), body=craft_data("fr"))

    # Start the whole process
    assert download.main("fr") == 0

    # Check that files are created
    assert pages_xml.is_file()
    assert pages_bz2.is_file()


@responses.activate
def test_download_already_done(craft_data: Callable[[str], bytes]) -> None:
    """It should not download again a processed Wiktionary dump."""

    output_dir = Path(os.environ["CWD"]) / "data" / "fr"

    dump = DUMPS[-1]
    assert dump == "20200514"
    pages_xml = output_dir / f"pages-{dump}.xml"
    pages_bz2 = output_dir / f"pages-{dump}.xml.bz2"

    # The BZ2 file was already downloaded
    pages_bz2.write_bytes(craft_data("fr"))

    # List of requests responses to falsify:
    #   - fetch_snapshots()
    responses.add(responses.GET, BASE_URL.format(locale="fr"), body=WIKTIONARY_INDEX)

    # Start the whole process
    assert download.main("fr") == 0

    # Check that files are created
    assert pages_xml.is_file()
    assert pages_bz2.is_file()


@responses.activate
def test_ongoing_dump(craft_data: Callable[[str], bytes]) -> None:
    """When a dump is not finished on the Wiktionary side, the previous dump should be used until a valid one is found."""

    output_dir = Path(os.environ["CWD"]) / "data" / "fr"
    expected_dump = DUMPS[-3]
    assert expected_dump == "20200220"

    # Clean-up before we start
    cleanup(output_dir)

    # List of requests responses to falsify:
    #   - fetch_snapshots()
    #   - fetch_pages() for 20200514, 20200301, and 20200220
    responses.add(responses.GET, BASE_URL.format(locale="fr"), body=WIKTIONARY_INDEX)
    for dump in DUMPS[:-3:-1]:
        responses.add(responses.GET, DUMP_URL.format(locale="fr", snapshot=dump), status=404)
    responses.add(responses.GET, DUMP_URL.format(locale="fr", snapshot=expected_dump), body=craft_data("fr"))

    # Start the whole process
    assert download.main("fr") == 0

    # Check files
    for dump in DUMPS:
        page_xml = output_dir / f"pages-{dump}.xml"
        page_bz2 = output_dir / f"pages-{dump}.xml.bz2"
        if dump == expected_dump:
            # Check that files are created
            assert page_xml.is_file()
            assert page_bz2.is_file()
        else:
            # Check that files are not created
            assert not page_xml.is_file()
            assert not page_bz2.is_file()


@responses.activate
def test_no_dump_found(craft_data: Callable[[str], bytes]) -> None:
    output_dir = Path(os.environ["CWD"]) / "data" / "fr"

    # Clean-up before we start
    cleanup(output_dir)

    # List of requests responses to falsify:
    #   - fetch_snapshots()
    #   - fetch_pages() for all dumps
    responses.add(responses.GET, BASE_URL.format(locale="fr"), body=WIKTIONARY_INDEX)
    for dump in DUMPS:
        responses.add(responses.GET, DUMP_URL.format(locale="fr", snapshot=dump), status=404)

    # Start the whole process
    assert download.main("fr") == 1

    # Check that files are created
    for dump in DUMPS:
        assert not (output_dir / f"pages-{dump}.xml").is_file()
        assert not (output_dir / f"pages-{dump}.xml.bz2").is_file()


def test_progress_callback(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        download.callback_progress("Some text", 42 * 1024, False)
        download.callback_progress("Some text", 42 * 1024, True)

    assert caplog.records[0].getMessage() == "Some text: 43,008 bytes"
    assert caplog.records[1].getMessage() == "Some text: OK [43,008 bytes]"


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
    pages_compressed = Path(f"pages-{snapshot}.xml.bz2")
    pages_uncompressed = Path(f"pages-{snapshot}.xml")

    with patch.dict("os.environ", {"CWD": str(tmp_path), "FORCE_SNAPSHOT": snapshot}):
        assert download.fetch_snapshots(lang_src) == [snapshot]

        output_compressed = download.get_output_file_compressed(lang_src, snapshot)
        assert output_compressed == tmp_path / "data" / lang_src / pages_compressed

        output_uncompressed = download.get_output_file_uncompressed(output_compressed)
        assert output_uncompressed == tmp_path / "data" / lang_src / pages_uncompressed

        with (
            patch.object(download, "get_output_file_compressed") as mocked_gofc,
            patch.object(download, "get_output_file_uncompressed") as mocked_gofu,
            patch.object(download, "fetch_pages") as mocked_fp,
            patch.object(download, "decompress") as mocked_d,
        ):
            mocked_gofc.return_value = pages_compressed
            mocked_gofu.return_value = pages_uncompressed

            download.main(locale)
            mocked_gofc.assert_called_once_with(lang_src, snapshot)
            mocked_gofu.assert_called_once_with(pages_compressed)
            mocked_fp.assert_called_once_with(snapshot, lang_src, pages_compressed, callback=download.callback_progress)
            mocked_d.assert_called_once_with(pages_compressed, pages_uncompressed, download.callback_progress)
