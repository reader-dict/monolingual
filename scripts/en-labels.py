import re

from scripts_utils import get_content

REPLACEMENTS = sorted(
    [
        "accent_display",
        "accent_Wikipedia",
        "addl",
        "aliases",
        "alias_of",
        "category",
        "country",
        "labels",
        "def",
        "deprecated",
        "deprecated_aliases",
        "display",
        "form_of_display",
        "from",
        "fulldef",
        "glossary",
        "langs",
        "language",
        "nolink",
        "noreg",
        "omit_preComma",
        "omit_postComma",
        "omit_preSpace",
        "omit_postSpace",
        "othercat",
        "parent",
        "parent_label",
        "plain_categories",
        "pos_categories",
        "prep",
        "region",
        "regional_categories",
        "sense_categories",
        "special_display",
        "the",
        "topical_categories",
        "track",
        "type",
        "verb",
        "Wikidata",
        "wikipedia",
        "Wikipedia",
        "Wiktionary",
    ],
    key=len,
    reverse=True,
)


def clean_display(display: str) -> str:
    if "[[" in display:
        display = re.sub(r"\[\[(?:w|wikipedia|Wiktionary):[^|]*\|(^\])*", "", display, flags=re.MULTILINE)
        display = re.sub(r"\[\[[^\|\]]*\|(^\])*", "", display, flags=re.MULTILINE)
        display = display.replace("]]", "")
        display = display.replace("[[w:", "")
        display = display.replace("[[", "")
    if "''" in display:
        display = re.sub(r"''([^']+)''", r"<i>\1</i>", display)
    return display


def clean_lua_text(text: str) -> str:
    text = text.replace("local ", "")
    text = text.replace("true", "True")
    text = text.replace("false", "False")
    text = text.replace("--", "#")
    return text


def get_and_clean_page(url: str) -> str:
    text = clean_lua_text(get_content(f"{url}?action=raw"))

    for replacement in REPLACEMENTS:
        text = re.sub(rf"[ \t]+{replacement}[\s]*=", f'    "{replacement}":', text)
        if replacement != "labels":
            text = re.sub(rf"{replacement}[\s]*=", f'"{replacement}":', text)

    return text


def process_qualifiers_page(url: str) -> dict[str, dict[str, list[str] | bool]]:
    text = get_and_clean_page(url)
    code = ""

    for line in text.split("\n"):
        if line.startswith("return"):
            break
        elif line.strip().startswith(("#", "end")):
            continue
        code += f"{line}\n"

    _locals: dict[str, dict[str, dict[str, list[str] | bool]]] = {"labels": {}}
    exec(code, {}, _locals)
    return _locals["labels"]


def process_page(url: str) -> dict[str, str]:
    text = get_and_clean_page(url)

    is_english_page = url.endswith("/en")
    in_function = False
    aliases_to_add = {}
    generate_non_todo = []
    code = ""

    for line in text.split("\n"):
        if line.startswith("return"):
            break
        elif line.strip().startswith("#"):
            continue
        elif is_english_page:
            if line.startswith("function"):
                in_function = True
            elif line.startswith("end"):
                in_function = False
            if in_function:
                continue
            elif line.startswith("table.insert"):
                # table.insert(labels["non-Mary-marry-merry"].aliases, "nMmmm")
                parts = line.split('"')
                aliases_to_add[parts[1]] = parts[3]
                continue
            elif line.startswith("generate_non") and (matches := re.match(r'generate_non\("([^"]+)"', line)):
                generate_non_todo.append(matches[1])
                continue

        if not line.startswith("end"):
            code += f"{line}\n"

    _locals: dict[str, dict[str, dict[str, str]]] = {"labels": {}}
    exec(code, {}, _locals)
    labels = _locals["labels"]

    results: dict[str, str] = {}
    for label, values in labels.items():
        if label == "deprecated label":
            continue

        display = clean_display(values.get("display", label))
        results[label] = display
        for alias in values.get("aliases") or []:
            results[alias] = display

    for label in generate_non_todo:
        results[f"non-{label}"] = f"non-{results[label]}"
        for alias in labels[label].get("aliases") or []:
            results[f"non-{alias}"] = results[f"non-{label}"]

    for label, alias in aliases_to_add.items():
        results[alias] = results[label]

    return results


results: dict[str, str] = {}
for url in [
    "https://en.wiktionary.org/wiki/Module:labels/data",
    "https://en.wiktionary.org/wiki/Module:labels/data/lang/en",
    "https://en.wiktionary.org/wiki/Module:labels/data/qualifiers",
    "https://en.wiktionary.org/wiki/Module:labels/data/regional",
    "https://en.wiktionary.org/wiki/Module:labels/data/topical",
]:
    results |= process_page(url)
print("labels = {")
for key, value in sorted(results.items()):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(results):,}")

syntaxes: dict[str, dict[str, bool]] = {}
qualifiers = process_qualifiers_page("https://en.wiktionary.org/wiki/Module:labels/data/qualifiers")
for label, values in qualifiers.items():
    qual = {
        "omit_post_comma": bool(values.get("omit_postComma")),
        "omit_pre_comma": bool(values.get("omit_preComma")),
        "omit_pre_space": bool(values.get("omit_preSpace")),
    }
    syntaxes[label] = qual
    for alias in values.get("aliases", []):  # type: ignore[union-attr]
        syntaxes[alias] = qual
print("\nsyntaxes = {")
for key, value in sorted(syntaxes.items()):  # type: ignore[assignment]
    print(f'    "{key}": {{')
    for label, values in value.items():  # type: ignore[attr-defined]
        print(f'        "{label}": {values},')
    print("    },")
print(f"}}  # {len(syntaxes):,}")
