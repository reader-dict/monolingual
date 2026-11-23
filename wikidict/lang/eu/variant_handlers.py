import re
from collections import defaultdict

from ... import context, utils


def cleanup(word: str, form: str) -> str:
    cleaned = utils.cleanup_rev_variant(form)
    if " " not in word and " " in cleaned:
        cleaned = cleaned.split(" ")[-1]
    return cleaned


RE_CLEANUP1 = re.compile(r"\[//\w++.wiktionary.org[^ ]++ ([^\]]++)\]")
RE_CLEANUP2 = re.compile(r"<sup>[^<]++</sup>")
RE_CLEANUP3 = re.compile(r"(?m)\| colspan[^|]++")
RE_FIND_FORMS1 = re.compile(r"(?m)\[\[([^#|\]]++)")
RE_FIND_FORMS2 = re.compile(r"(?m)^\|[ ]*+([^|=\n]++)$")


def table_to_forms(word: str, wikitext: str) -> list[str]:
    wikitext = wikitext.replace(" || ", "\n| ")
    wikitext = RE_CLEANUP1.sub(r"[[\1]]", wikitext)
    wikitext = RE_CLEANUP2.sub("", wikitext)
    lines = "\n".join(
        [
            line
            for line in wikitext.splitlines()
            if line.startswith("|")
            and not line.startswith(("|-", "|}"))
            and "background" not in line
            and "bgcolor" not in line
            and "edota:" not in line
        ]
    )
    lines = RE_CLEANUP3.sub("", lines)

    forms = {cleanup(word, form) for form in RE_FIND_FORMS1.findall(lines) or RE_FIND_FORMS2.findall(lines)}
    forms.discard(word)
    forms.discard("―")
    forms.discard("—")
    forms.discard("-")
    forms.discard("")

    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "eu")
    return "|".join(table_to_forms(word, table))


handlers = {
    "flexion": lambda tpl_, parts, data_, word_: parts[0],
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
