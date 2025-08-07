import re

from scripts_utils import get_content

soup = get_content("https://zh.wiktionary.org/wiki/Module:Languages/data/2?action=raw")
pattern = re.compile(r'm\["([^"]+)"\]\s*=\s*\{\s*"([^"]+)",', flags=re.DOTALL | re.MULTILINE)

langs = re.findall(pattern, soup)

print("langs = {")
for key, name in sorted(langs):
    print(f'    "{key}": "{name}",')
print(f"}}  # {len(langs):,}")
