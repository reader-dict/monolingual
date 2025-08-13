"""Retrieve Wiktionary data."""

from __future__ import annotations

import bz2
import logging
import os
import re
from datetime import timedelta
from pathlib import Path
from time import monotonic
from typing import TYPE_CHECKING

from requests.exceptions import HTTPError

from . import constants, utils

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)


def callback_progress(text: str, done: int, last: bool) -> None:
    """Progression callback. Used when fetching the Wiktionary dump and when extracting it."""
    size = f"OK [{done:,} bytes]" if last else f"{done:,} bytes"
    log.debug("%s: %s", text, size)


def decompress(file_in: Path, file_out: Path, callback: Callable[[str, int, bool], None]) -> None:
    """Decompress a BZ2 file."""
    msg = f"Uncompressing into {file_out}"
    log.info(msg)

    if file_out.is_file():
        return

    comp = bz2.BZ2Decompressor()
    with file_in.open("rb") as fi, file_out.open("wb") as fo:
        done = 0
        while data := fi.read(1024**2):
            uncompressed = comp.decompress(data)
            done += fo.write(uncompressed)
            callback(msg, done, False)

    callback(msg, file_out.stat().st_size, True)


def fetch_snapshots(locale: str) -> list[str]:
    """Fetch available snapshots.
    Return a list of sorted dates.
    """
    if forced_snapshot := os.environ.get("FORCE_SNAPSHOT"):
        return [forced_snapshot]

    with constants.SESSION.get(constants.BASE_URL.format(locale=locale)) as req:
        req.raise_for_status()
        return sorted(re.findall(r'href="(\d+)/"', req.text))


def fetch_pages(date: str, locale: str, output: Path, *, callback: Callable[[str, int, bool], None]) -> None:
    """Download all pages, current versions only.
    Return the path of the XML file BZ2 compressed.
    """
    url = constants.DUMP_URL.format(locale=locale, snapshot=date)
    msg = f"Fetching {url} into {output}"
    log.info(msg)

    if output.is_file():
        return

    with constants.SESSION.get(url, stream=True) as req:
        req.raise_for_status()

        # Ensure the folder exists
        output.parent.mkdir(exist_ok=True, parents=True)

        with output.open(mode="wb") as fh:
            done = 0
            for chunk in req.iter_content(chunk_size=1024**2):
                done += fh.write(chunk)
                callback(msg, done, False)

    callback(msg, output.stat().st_size, True)


def get_output_file_compressed(locale: str, snapshot: str) -> Path:
    return Path(os.getenv("CWD", "")) / "data" / locale / f"pages-{snapshot}.xml.bz2"


def get_output_file_uncompressed(file: Path) -> Path:
    return file.with_suffix(file.suffix.replace(".bz2", ""))


def main(locale: str) -> int:
    """Entry point."""

    start = monotonic()
    locale = utils.guess_lang_origin(locale)

    # Get the snapshot to handle
    snapshots = fetch_snapshots(locale)

    # Fetch and uncompress the snapshot file
    for snapshot in snapshots[::-1]:
        file_compressed = get_output_file_compressed(locale, snapshot)
        file_uncompressed = get_output_file_uncompressed(file_compressed)
        try:
            fetch_pages(snapshot, locale, file_compressed, callback=callback_progress)
            decompress(file_compressed, file_uncompressed, callback_progress)
            break
        except HTTPError as exc:
            file_compressed.unlink(missing_ok=True)
            file_uncompressed.unlink(missing_ok=True)
            if exc.response.status_code != 404:
                raise
            log.warning("Wiktionary dump is ongoing ... ")
            log.info("Will use the previous one.")
    else:
        log.error("No Wiktionary dump found!")
        return 1

    log.info("Retrieval done in %s!", timedelta(seconds=monotonic() - start))
    return 0
