import re
from collections import defaultdict

from ... import context


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

    forms: set[str]
    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "pt")
    if tpl.startswith("flex."):
        forms = set(re.findall(r"\[\[(.+)#\w+\|\1\]\]", table))
    else:
        lines = "\n".join(line for line in table.splitlines() if line.startswith("| "))
        lines = re.sub(r"<sup>\d+</sup>", "", lines)
        lines = lines.replace("<br>", "\n| ").replace("<br/>", "\n| ")
        forms = {form[2:].strip().removeprefix("não ").removesuffix(" /") for form in lines.splitlines()}
    return "|".join(form.strip() for form in forms if "{" not in form if form)


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
