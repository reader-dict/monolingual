import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("прич.", ["зыбить"], defaultdict(str), "")
    'зыбить'
    >>> render_variant("прич.", ["находить (наталкиваться)", "наст"], defaultdict(str), "")
    'находить'
    >>> render_variant("прич.", ["<small>?</small>"], defaultdict(str), "")
    ''
    """
    if (variant := parts[0]) == "<small>?</small>":
        variant = ""
    if " (" in variant:
        variant = variant.split(" (", 1)[0]
    return variant


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["коро́ль"], defaultdict(str), "")
    'коро́ль'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    forms: set[str]
    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "ru")
    if table.startswith("{"):
        table = table.replace("<br>", "\n| ").replace("<br/>", "\n| ")
        forms = {form[2:].strip() for form in table.splitlines() if form.startswith("| ") and not form.endswith("| ")}
    else:
        table = table.replace("<br>", "</td><td>").replace("<br/>", "</td><td>").replace(' rowspan="2"', "")
        forms = set(re.findall(r"<td>([^<]+)</td>", table))

    if forms:
        forms = {cleanup(form) for form in forms}
        forms.discard(word)
        forms.discard("")

    return "|".join(forms)


handlers = {
    "прич.": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
