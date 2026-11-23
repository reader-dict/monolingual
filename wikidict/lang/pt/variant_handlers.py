import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    cleaned = utils.cleanup_rev_variant(form, rpl=["não "], skip={"plural", "singular", "subjuntivo"})
    if "''" in cleaned or "=" in cleaned:
        return ""
    return cleaned


RE_CLEANUPS = [
    re.compile(r'(?:class|colspan|rowspan)="[^"]*+"'),
    re.compile(r"<sup>\d++</sup>"),
    re.compile(r'\|style="([^|]++)'),
]
RE_FIND_FORMS = re.compile(r"\[\[([^#]++)#[^|]++\|")


def table_to_forms(word: str, wikitext: str, *, is_tpl_flex: bool = False) -> list[str]:
    for pattern in RE_CLEANUPS:
        wikitext = pattern.sub("", wikitext)
    wikitext = wikitext.replace("|| ", "\n| ")
    lines = [
        line
        for raw_line in wikitext.splitlines()
        if (
            (line := raw_line.strip())
            and line.startswith("|")
            and not line.startswith(("|-", "|+", "|}"))
            and "lightgray" not in line
            and "#CEE3F6" not in line
            and "#CEF6CE" not in line
            and "#F5ECCE" not in line
            and "#F6CECE" not in line
            and "background-color: white" not in line
            and line != "|"
        )
    ]

    # We want reverse variants for the base form only
    if is_tpl_flex and not (f"'''{word}'''" in lines[0] or f"'''{word}'''" in lines[1]):
        return []

    forms: set[str] = set()
    for line in lines:
        if "]], [[" in line:
            for subline in line.split("]], [["):
                forms.add(cleanup((RE_FIND_FORMS.findall(subline) or [subline.strip(" '")])[0]))
        elif "<br/>" in line:
            for subline in line.split("<br/>"):
                forms.add(cleanup((RE_FIND_FORMS.findall(subline) or [subline.strip(" '")])[0]))
        else:
            forms.add(cleanup((RE_FIND_FORMS.findall(line) or [line.strip(" '|")])[0]))

    forms.discard(word)
    forms.discard("&ndash;")
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["ensimesmar"], defaultdict(str), "")
    'ensimesmar'
    >>> render_variant("flexion", ["ensimesmar#Substantivo1"], defaultdict(str), "")
    'ensimesmar'
    """
    return parts[0].split("#", 1)[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "pt")
    is_tpl_flex = tpl.startswith("flex.")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table, is_tpl_flex=is_tpl_flex))


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
