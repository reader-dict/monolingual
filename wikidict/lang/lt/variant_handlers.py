import re
from collections import defaultdict

from ... import context, utils


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

    # We might pass the whole template code in `tpl` from `adjust_wikicode()` to workaround brackets parsing
    template = tpl if tpl.startswith("{{") else utils.reconstruct_tpl(tpl, parts, data)

    table = context.expand(template, "lt")
    table = table.replace(",<br/>", "\n| ")
    table = table.replace("| colspan=2 ", "")

    forms: set[str] = set()
    for line in table.splitlines():
        # Guess the gender, when available
        if line.startswith("'''"):
            if "[[mot. g.]]" in line:
                forms.add("{{f}}")
            if "[[vyr. g.]]" in line:
                forms.add("{{m}}")

        if line.startswith("* žr."):
            # We want reverse variants for the original word only
            if not line[line.find("'''") :].startswith(f"'''{word}'''"):
                return "SKIP WORD"
        elif line.startswith("* taip pat žr."):
            forms.update(re.findall(r"\[\[([^\]]+)\]\]", line.split("'''")[1]))
        elif line.startswith("| ") and "style=" not in line:
            if "[[" in line:
                forms.update(re.findall(r"\| \[\[([^\]]+)\]\]", line))
            else:
                forms.add(line.lstrip("| "))

    forms.discard(word)
    forms.discard("-")

    return "|".join(sorted(forms))


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
