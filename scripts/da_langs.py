import re

from scripts_utils import get_content

# Primary
data = get_content("https://da.wiktionary.org/wiki/Modul:lang/data?action=raw")
pattern = re.compile(r'data\["([^"]+)"\]\s+=\s+\{\s+name\s+=\s+"([^"]+)",')
langs = re.findall(pattern, data)

# Missing langs
langs.append(("enm", "middelengelsk"))
langs.append(("otk", "oldtyrkisk"))
langs.append(("syr", "assyrisk"))

# Aliases
data = get_content("https://da.wiktionary.org/wiki/Bruger:PolyBot~dawiktionary/Languages?action=raw")
pattern = re.compile(r"^\| (\w+)\|\|\|\|(\w+)\|\|", flags=re.MULTILINE)
langs.extend(re.findall(pattern, data))

known_langs: set[str] = set()
print("langs = {")
for key, name in sorted(langs):
    if key in known_langs:
        continue
    known_langs.add(key)
    print(f'    "{key}": "{name.lower()}",')
print(f"}}  # {len(langs):,}")
