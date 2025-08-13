import re

from scripts_utils import get_content

text = get_content("https://eo.wiktionary.org/wiki/Modulo:mtagg?action=raw")

# Special treatment
text = text.replace('"ava"..string.char(197,173)', f'"ava{chr(197)}{chr(173)}"')

# Uniformize maps
# contabtt ['ASKI'] = 'askia signo' → contabtt["ASKI"] = "askia signo"
text = re.sub(r"(contab\w+)\s*\['([^']+)'\]\s*=\s*'([^'|]+)['|]", r'\1["\2"] = "\3"', text)

tags = re.findall(r'^\s+contab\w+\s*\["([^"]+)"\]\s*=\s*"([^"|]+)', text, flags=re.MULTILINE)
print("tags = {")
for key, value in sorted(tags):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(tags):,}")
