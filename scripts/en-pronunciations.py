import re

from scripts_utils import get_content


def get_prons(url: str) -> list[tuple[str, str]]:
    code = get_content(url)
    # ["吖"]="ā",
    sep = r"'\""
    return re.findall(rf"^\s+\[[{sep}]([^{sep}]+)[{sep}]\]\s*=\s*[{sep}]([^{sep}]+)[{sep}]", code, flags=re.MULTILINE)


# Note: do not change the order to ease `git diff` reviewes
for lang, url in [
    ("cmn", "https://en.wiktionary.org/wiki/Module:zh/data/cmn-pron?action=raw"),
    ("yue", "https://en.wiktionary.org/wiki/Module:zh/data/yue-pron?action=raw"),
]:
    prons = get_prons(url)
    print(f"{lang} = {{")
    for key, value in sorted(prons):
        print(f'    "{key}": "{value}",')
    print(f"}}  # {len(prons):,}")
