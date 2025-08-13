import re

from scripts_utils import get_content

soup = get_content("https://zh.wiktionary.org/wiki/Module:Languages/code_to_canonical_name?action=raw")
pattern = re.compile(r'\s*\["([^"]+)"\]\s*=\s*"([^"]+)",', flags=re.MULTILINE)

langs = re.findall(pattern, soup)

print("langs = {")
for key, name in sorted(langs):
    print(f'    "{key}": "{name}",')
print(f"}}  # {len(langs):,}")
