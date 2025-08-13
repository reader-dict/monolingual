from scripts_utils import get_content

url = "https://en.wiktionary.org/wiki/Module:scripts/code_to_canonical_name.json?action=raw"
scripts = get_content(url, as_json=True)

print("scripts = {")
for key, value in sorted(scripts.items()):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(scripts):,}")
