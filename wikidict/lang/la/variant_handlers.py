import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form)


def table_to_forms(word: str, wikitext: str) -> list[str]:
    lines = "\n".join(
        [
            line
            for raw_line in wikitext.splitlines()
            if (line := raw_line.strip()) and line.startswith("|") and not line.startswith(("|-", "|}"))
        ]
    )
    forms = {cleanup(form) for form in re.findall(r"\[\[([^|]+)", lines)}

    forms.discard(word)
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "la")
    return "|".join(table_to_forms(word, table))


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("coniug", ["la", "agitandus", "agitō", "", "", "", "gndv", "pas", "(agitāre)"], defaultdict(str, {"casu": "nom"}), "agitandus")
    'agito'
    """
    if tpl == "flexion":
        return parts[0].strip()

    expanded = context.expand(utils.reconstruct_tpl(tpl, parts, data), "la")
    return str(re.findall(r"\[\[([^#]+)", expanded.splitlines()[-1])[0])


handlers = {
    **dict.fromkeys(
        {
            "coniug",
            "flexion",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
