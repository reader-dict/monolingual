from scripts_utils import get_soup

ROOT = "https://en.wiktionary.org"


def get_text(url: str) -> str:
    soup = get_soup(url)
    div = soup.find("span", "form-of-definition")
    if not div:
        return ""
    res = str(div.text).replace(" term", "")
    return res.replace(" [Term?]", "")


aliases: list[tuple[str, str]] = []


def fetch_aliases(template: str) -> None:
    url_template = f"{ROOT}/wiki/Special:WhatLinksHere?target=Template%3A{template}&namespace=&hidetrans=1&hidelinks=1"
    soup = get_soup(url_template)
    if ul := soup.find("ul", attrs={"id": "mw-whatlinkshere-list"}):
        for li in ul.children:
            alias = li.find("a").text.split(":")[1]
            aliases.append((alias, template))


url = f"{ROOT}/wiki/Category:Form-of_templates"
soup = get_soup(url)
main_div = soup.find("div", "mw-parser-output")
table = main_div.find("table", recursive=False)

columns = ["template", "aliases", "cat", "inflection", "initial-cap", "from", "pos"]

body = table.find("tbody")
trs = body.find_all("tr")
trs.pop(0)  # remove header
count = 0
print("form_of_templates = {")
for tr in trs:
    tds0 = [t.text.strip() for t in tr.find_all("td")]
    if tds := dict(zip(columns, tds0)):
        if text := get_text(ROOT + tr.find("a")["href"]):
            print('    "{}": {{"value": "{}", "initial-cap": "{}"}},'.format(tds["template"], text, tds["initial-cap"]))
            count += 1
            fetch_aliases(tds["template"])
print(f"}}  # {count:,}")

print(f"\n# Aliases ({len(aliases):,})")
for alias, tpl in sorted(aliases):
    print(f'form_of_templates["{alias}"] = form_of_templates["{tpl}"]')
