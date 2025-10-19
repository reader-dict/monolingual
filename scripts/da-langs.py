import re

from scripts_utils import get_content, get_soup

# Primary
soup = get_soup("https://da.wiktionary.org/wiki/Modul:lang/data").text
pattern = re.compile(r'data\["([^"]+)"\]\s+=\s+\{\s+name\s+=\s+"([^"]+)",')
langs = re.findall(pattern, soup)

# Missing langs
langs.append(("enm", "middelengelsk"))
langs.append(("otk", "oldtyrkisk"))
langs.append(("syr", "assyrisk"))

# Aliases
soup = get_content("https://da.wiktionary.org/wiki/Bruger:PolyBot~dawiktionary/Languages?action=raw")
pattern = re.compile(r"^\| (\w+)\|\|\|\|(\w+)\|\|", flags=re.MULTILINE)
langs.extend(re.findall(pattern, soup))

known_langs: set[str] = set()
print("langs = {")
for key, name in sorted(langs):
    if key in known_langs:
        continue
    known_langs.add(key)
    print(f'    "{key}": "{name.lower()}",')
print(f"}}  # {len(langs):,}")
