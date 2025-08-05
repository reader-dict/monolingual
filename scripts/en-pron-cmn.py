import re

from scripts_utils import get_content


def get_prons(url: str) -> list[tuple[str, str]]:
    code = get_content(url)
    sep = r"'\""
    return re.findall(rf"^\s+\[[{sep}]([^{sep}]+)[{sep}]\]\s*=\s*[{sep}]([^{sep}]+)[{sep}]", code, flags=re.MULTILINE)


prons = get_prons("https://en.wiktionary.org/wiki/Module:zh/data/cmn-pron?action=raw")
print("pron = {")
for key, value in sorted(prons):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(prons):,}")
