import bz2
import os
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from xml.sax.saxutils import escape

import pytest

os.environ["CWD"] = str(Path(__file__).parent)


XML = '<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.11/" xml:lang="{locale}">'
PAGE_XML = """
  <page>
    <title>{word}</title>
    <ns>0</ns>
    <id>1</id>
    <revision>
        <id>{revision}</id>
        <parentid>221</parentid>
        <timestamp>2020-04-17T14:21:12Z</timestamp>
        <contributor>
            <username>Alice</username>
            <id>42</id>
        </contributor>
        <comment>/**/</comment>
        <model>wikitext</model>
        <format>text/x-wiki</format>
        <text xml:space="preserve">{text}</text>
    </revision>
  </page>
"""


@pytest.fixture(autouse=True)
def no_warnings(recwarn: pytest.WarningsRecorder) -> Generator[None]:
    """Fail on warning."""

    yield

    warnings = []
    for warning in recwarn:
        message = str(warning.message)
        warn = f"{warning.filename}:{warning.lineno} {message}"
        print(warn, file=sys.stderr)
        warnings.append(warn)

    assert not warnings


@pytest.fixture(scope="session")
def craft_data() -> Callable[[str], bytes]:
    def _craft_data(locale: str) -> bytes:
        data_dir = Path(os.environ["CWD"]) / "data" / locale
        content = XML.format(locale=locale)
        for file in sorted(data_dir.glob("*.wiki")):
            if file.stem == "vide":
                continue

            revision = 42
            text = escape(file.read_text(encoding="utf-8"))
            content += PAGE_XML.format(word=file.stem, revision=revision, text=text)

        content += "</mediawiki>"
        return bz2.compress(content.encode("utf-8"))

    return _craft_data


@pytest.fixture(scope="session")
def page() -> Callable[[str, str], str]:
    """Return the Wikicode of a word stored into "data/LOCALE/WORD.wiki"."""

    def _page(word: str, locale: str) -> str:
        data = Path(os.environ["CWD"]) / "data" / locale
        file = data / f"{word}.wiki"
        return file.read_text(encoding="utf-8")

    return _page
