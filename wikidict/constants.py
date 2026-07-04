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
WIKTIONARY_URL_API = "https://{locale}.wiktionary.org/w/api.php"
WIKIMEDIA_URL_BASE = "https://en.wikipedia.org/api/rest_v1"
WIKIMEDIA_URL_MATH_CHECK = f"{WIKIMEDIA_URL_BASE}/media/math/check/{{type}}"
WIKIMEDIA_URL_MATH_RENDER = f"{WIKIMEDIA_URL_BASE}/media/math/render/{{format}}/{{hash}}"

# Dictionary file suffix for etymology-free files
NO_ETYMOLOGY_SUFFIX = "-noetym"

# ZIP files
ZIP_WORDS_COUNT = "___count.txt"
ZIP_WORDS_SNAPSHOT = "___snapshot.txt"

# Algorithm used to compute dictionaries checksum
ASSET_CHECKSUM_ALGO = "sha256"

# Locales relations
# Example with FRO (Old French) that uses the FR (French) Wiktionary dump as source.
# Syntax: "locale": "origin locale"
LOCALE_ORIGIN = {"fro": "fr"}

# Mobi
COVER_FILE = Path(__file__).parent / "cover.png"
MOBIPOCKET_TOOL = Path.home() / ".local" / "bin" / "kindling"

# HTTP requests
SESSION = requests.Session()
SESSION.headers.update(WIKIMEDIA_HEADERS)

# --parse: modules & templates "end patterns" to ignore when saving them in the database
MODULES_TO_IGNORE = ("/doc", "/documentation", "/sandbox", "/testcases")

# --render: Lua modules aliases
PARSER_FUNCTIONS_ALIASES = {
    "pt": {
        "#se": "#if",
        "#seigual": "#ifeq",
        "#seerro": "#iferror",
        "#seexiste": "#ifexist",
        "#seexpr": "#ifexpr",
    }
}

# --parse: HTML entities to replace in modules & templates contents
HTML_REPL_BODY = {
    # Found in modules importing another module
    "&quot;": '"',
}
HTML_REPL_TITLE = {"&amp;": "&"}
