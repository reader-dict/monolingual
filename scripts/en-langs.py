import re
import string

from scripts_utils import get_soup


def get_content(url: str) -> str:
    soup = get_soup(url)
    content_div = soup.find("div", "mw-parser-output")
    content_div = content_div.find("div", {"class": "mw-highlight"}, recursive=False)
    return str(content_div.text)


def process_page(url: str) -> dict[str, str]:
    code = get_content(url)

    # Remove comments
    code = re.sub(r"\s*--.*", "", code)

    """
    The regexp matches the first 2 lines:
        m["uk-CA"] = {
            "Canadian Ukrainian",
            4161010,
            "uk",
        }
    """
    return dict(re.findall(r'^m\["([^"]+)"]\s*=\s*\{\s*"([^"]+)",', code, flags=re.MULTILINE))


languages: dict[str, str] = {}
for url in [
    "https://en.wiktionary.org/wiki/Module:etymology_languages/data",
    "https://en.wiktionary.org/wiki/Module:families/data",
    "https://en.wiktionary.org/wiki/Module:languages/data/2",
    "https://en.wiktionary.org/wiki/Module:languages/data/exceptional",
    *[f"https://en.wiktionary.org/wiki/Module:languages/data/3/{letter}" for letter in string.ascii_lowercase],
]:
    languages |= process_page(url)

print("langs = {")
for key, value in sorted(languages.items()):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(languages):,}")
