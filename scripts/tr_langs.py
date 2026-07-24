import re

from scripts_utils import get_content

data = get_content("https://tr.wiktionary.org/wiki/Mod%C3%BCl:diller/veri2?action=raw")
pattern = re.compile(r'm\["([^"]+)"\][^"]+"([^"]+)",')
langs = re.findall(pattern, data)

# Missing langs (https://tr.wiktionary.org/wiki/Modül:diller/veri3/LETTER)
langs.extend(
    [
        ("ang", "Eski İngilizce"),
        ("enm", "Orta İngilizce"),
        ("fro", "Eski Fransızca"),
        ("grc", "Eski Yunanca"),
        ("jbo", "Lojban dili"),
        ("lkt", "Lakota"),
    ]
)

print("langs = {")
for key, name in sorted(langs):
    print(f'    "{key}": "{name.lower()}",')
print(f"}}  # {len(langs):,}")
