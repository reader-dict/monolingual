"""Shared constants."""

from pathlib import Path

import requests

# Dictionaries metadata
PROJECT = "reader.dict"
TITLE = "{project} {langs}"
WEBSITE = "https://www.reader-dict.com"

# Wiktionary dump URL
BASE_URL = "https://dumps.wikimedia.org/{locale}wiktionary"
DUMP_URL = f"{BASE_URL}/{{snapshot}}/{{locale}}wiktionary-{{snapshot}}-pages-articles.xml.bz2"

# Wikimedia REST API
WIKIMEDIA_HEADERS = {"User-Agent": WEBSITE}
WIKIMEDIA_URL_BASE = "https://en.wikipedia.org/api/rest_v1"
WIKIMEDIA_URL_MATH_CHECK = f"{WIKIMEDIA_URL_BASE}/media/math/check/{{type}}"
WIKIMEDIA_URL_MATH_RENDER = f"{WIKIMEDIA_URL_BASE}/media/math/render/{{format}}/{{hash}}"

# Dictionary file suffix for etymology-free files
NO_ETYMOLOGY_SUFFIX = "-noetym"

# ZIP files
ZIP_WORDS_COUNT = "words.count"
ZIP_WORDS_SNAPSHOT = "words.snapshot"

# Algorithm used to compute dictionaries checksum
ASSET_CHECKSUM_ALGO = "sha256"

# Locales relations
# Example with FRO (Old French) that uses the FR (French) Wiktionary dump as source.
# Syntax: "locale": "origin locale"
LOCALE_ORIGIN = {"fro": "fr"}

# Mobi
COVER_FILE = Path(__file__).parent / "cover.png"
KINDLEGEN_FILE = Path.home() / ".local" / "bin" / "kindlegen"

# HTTP requests
SESSION = requests.Session()
