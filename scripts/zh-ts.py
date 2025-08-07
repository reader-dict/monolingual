import re

from scripts_utils import get_content

data = get_content("https://en.wiktionary.org/wiki/Module:zh/data/ts?action=raw")
pattern = re.compile(r'\["([^"]+)"\]="([^"]+)"').search

d_ts: dict[str, str] = {}
for line in data.splitlines():
    if (line := line.strip())[0] == "[":
        key, value = pattern(line).groups()  # type: ignore[union-attr]
        d_ts[key] = value

print("m_ts = {")
for key, name in sorted(d_ts.items()):
    print(f'    "{key}": "{name}",')
print(f"}}  # {len(d_ts):,}")
