import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form, rpl={"não "}, skip={"plural", "singular", "subjuntivo"})


def table_to_forms(word: str, wikitext: str) -> list[str]:
    wikitext = re.sub(r'(?:class|colspan|rowspan)="[^"]+"', "", wikitext)
    wikitext = re.sub(r"<sup>\d+</sup>", "", wikitext)
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
            and (line := re.sub(r'\|style="([^\|]+)', "", line))
            and line != "|"
        )
    ]

    forms: set[str] = set()
    for line in lines:
        if "]], [[" in line:
            for subline in line.split("]], [["):
                form = (re.findall(r"\[\[([^#]+)#[^|]+\|", subline) or [subline.strip(" '")])[0]
                if "''" not in form:
                    forms.add(cleanup(form))
        elif "<br/>" in line:
            for subline in line.split("<br/>"):
                form = (re.findall(r"\[\[([^#]+)#[^|]+\|", subline) or [subline.strip(" '")])[0]
                if "''" not in form:
                    forms.add(cleanup(form))
        else:
            form = (re.findall(r"\[\[([^#]+)#[^|]+\|", line) or [line.strip(" '|")])[0]
            if "''" not in form:
                forms.add(cleanup(form))

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
    """
    return parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "pt")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table))


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
