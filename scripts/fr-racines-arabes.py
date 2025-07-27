import re

from scripts_utils import get_content, get_soup

ROOT = "https://fr.wiktionary.org"
START_URL = "https://fr.wiktionary.org/wiki/Cat%C3%A9gorie:Mod%C3%A8les_de_racine_en_arabe_du_Wiktionnaire"
NEXTPAGE_TEXT = "page suivante"
RACINE_URL = "https://fr.wiktionary.org/wiki/Mod%C3%A8le:{}?action=raw"
GET_FORM = re.compile(r"<!-- \((\w+)[^>]+>").findall
STRIP_COMMENT = re.compile(r"<!--[^>]+>").sub


def process_category_page(url: str, results: dict[str, dict[str, str]]) -> str:
    soup = get_soup(url)
    nextpage = ""
    nextpage_div = soup.find(id="mw-pages")
    last_link = nextpage_div.find_all("a")[-1]
    if NEXTPAGE_TEXT == last_link.text:
        nextpage = ROOT + last_link.get("href")

    content_div = soup.find(id="mw-pages")
    for li in content_div.find_all("li"):
        tpl_title = li.find("a").get("title")
        if " " in tpl_title or "/" in tpl_title or "ar-racine" in tpl_title:
            continue

        process_root(tpl_title.removeprefix("Modèle:"), results)

    return nextpage


def romaniser(value: str) -> str:
    return {
        "i": "(1)",
        "ii": "(2)",
        "iii": "(3)",
        "iv": "(4)",
        "v": "(5)",
        "vi": "(6)",
        "vii": "(7)",
        "viii": "(8)",
        "ix": "(9)",
        "x": "(10)",
        "xi": "(11)",
        "xii": "(12)",
    }[value.lower()]


def process_root(tpl: str, results: dict[str, dict[str, str]]) -> None:
    url = RACINE_URL.format(tpl)
    data = get_content(url)
    tpl_dict = {}
    for line in data.splitlines():
        if line.startswith(("|***", "| ***")):
            sens = line.split("=")[1].strip()
            tpl_dict["aa_sens"] = sens
        if not line.startswith("| ar-"):
            continue

        racine, text = line[1:].split("=")
        text = text.strip()
        forme = romaniser(form[0]) if (form := GET_FORM(text)) else ""
        text = STRIP_COMMENT("", text).strip()
        tpl_dict[racine.strip()] = (forme, text)
    if tpl_dict:
        results[tpl] = tpl_dict


next_page_url = START_URL
results: dict[str, dict[str, str]] = {}

while next_page_url:
    next_page_url = process_category_page(next_page_url, results)

print("racines_schemes_arabes: dict[str, dict[str, str | tuple[str, str]]] = {")
for k, v in sorted(results.items()):
    print(f'    "{k}" : {{')
    for k1, v1 in sorted(v.items()):
        print(f'        "{k1}": {v1!r},')
    print(f"    }},  # {len(v):,}")
print(f"}}  # {len(results):,}")
