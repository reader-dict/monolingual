import re

from scripts_utils import get_content

soup = get_content("https://zh.wiktionary.org/wiki/Module:Languages/data/2?action=raw")
pattern = re.compile(r'm\["([^"]+)"\]\s*=\s*\{\s*"([^"]+)",', flags=re.DOTALL | re.MULTILINE)

langs = re.findall(pattern, soup)

# 3-letters code
# (No need to sync with Module:Languages/data/3/XXX since there are only a few cases.)
langs.extend(
    [
        ("arz", "埃及阿拉伯語"),
        ("mnc", "滿語"),
    ]
)

print("langs = {")
for key, name in sorted(langs):
    print(f'    "{key}": "{name}",')
print(f"}}  # {len(langs):,}")
