import re

from scripts_utils import get_content


def clean_lua(text: str) -> str:
    text = text.replace("local ", "")
    text = text.replace("end", "")
    text = text.replace("true", "True")
    text = text.replace("false", "False")
    text = text.replace("--", "#")
    return text


def process_display(display: str) -> str:
    if "[[" in display:
        display = re.sub(r"\[\[[^\|\]]*\|(^\])*", "", display)
        display = display.replace("]]", "")
        display = display.replace("[[", "")
    return display


def get_labels_data() -> dict[str, str]:
    text = clean_lua(get_content("https://zh.wiktionary.org/wiki/Module:Labels/data?action=raw"))
    repl = (
        "aliases",
        "deprecated",
        "deprecated_aliases",
        "display",
        "glossary",
        "omit_postComma",
        "plain_categories",
        "pos_categories",
        "regional_categories",
        "sense_categories",
        "topical_categories",
        "track",
        "Wikipedia",
    )
    text = re.sub(rf"[ \t]+({'|'.join(repl)})[\s]*=", r'    "\1":', text)

    code = ""
    for line in text.split("\n")[:-1:]:
        code += line + "\n"

    _locals: dict[str, dict[str, dict[str, str | set[str]]]] = {}
    exec(code, None, _locals)

    labels = _locals.get("labels", {})

    all_labels = {}
    for key, values in labels.items():
        aliases = values.get("aliases", set())
        if display := values.get("display"):
            assert isinstance(display, str)  # For Mypy
            display = process_display(display)
        elif not aliases:
            continue
        else:
            display = key

        all_labels[key] = display
        for alias in aliases:
            all_labels[alias] = display

    return all_labels


def get_etymology_data() -> dict[str, str]:
    text = clean_lua(get_content("https://zh.wiktionary.org/wiki/Module:Etymology_languages/data?action=raw"))
    text = text[text.find("m = ") : text.find("return require")]
    text = (
        text.replace("[[", "")
        .replace("]]", "")
        .replace("{", "[")
        .replace("}", "]")
        .replace("nil,", "None,")
        .replace("aliases = ", "")
    )
    text = text.replace("m = []", "m = {}")
    repl = [
        "ancestors",
        "display_text",
        "family",
        "ietf_subtag",
        "preprocess_links",
        "remove_diacritics",
        "remove_exceptions",
        "translit",
        "wikipedia_article",
    ]
    text = re.sub(rf"[ \t]+(?:{'|'.join(repl)})[\s]*=.+", "", text)
    text = re.sub(r"entry_name = \[[^]]+],", "", text, flags=re.MULTILINE | re.DOTALL)
    text = re.sub(r"[ \t]+entry_name[\s]*=.+", "", text)

    _locals: dict[str, dict[str, dict[str, str | set[str]]]] = {}
    exec(text, None, _locals)

    labels = _locals.get("m", {})

    all_labels = {}
    for key, (display, _, _, *values) in labels.items():
        aliases = values[0] if values else []
        all_labels[key] = display
        for alias in aliases:
            all_labels[alias] = display

    return all_labels


labels = get_labels_data() | get_etymology_data()
print("labels = {")
for key, value in sorted(labels.items()):
    print(f'    "{key}": "{value}",')
print(f"}}  # {len(labels):,}")
