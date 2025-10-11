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

    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "pt")
    forms = set(re.findall(r"\[\[(.+)#Português\|\1\]\]", table))
    return "|".join(form.strip() for form in forms if "{" not in form if form)


handlers = {
    "flexion": render_variant,
    **dict.fromkeys({"rev-flexion", "flex.pt"}, render_reverse_variant),
}
