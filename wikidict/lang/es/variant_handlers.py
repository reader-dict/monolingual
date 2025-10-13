import re
from collections import defaultdict

from ... import context


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("forma participio", ["apropiado", "femenino"], defaultdict(str), "")
    'apropiado'
    >>> render_variant("forma participio", ["gastado", "femenino"], defaultdict(str, {"v": "gastar"}), "")
    'gastar'
    """
    return data["v"] or parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    forms: set[str]
    expanded = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "es")
    if tpl.endswith(".v"):
        forms = set(re.findall(r"\[\[([^\]]+)\|\1\]\]", expanded))
    else:
        table = "\n".join(line for line in expanded.splitlines() if line.lstrip().startswith("|[["))
        forms = set(re.findall(r"\[\[([^#]+)#", table))
    return "|".join(form.strip() for form in sorted(forms) if "{" not in form if form)


handlers = {
    **dict.fromkeys(
        {
            "enclítico",
            "f.adj2",
            "f.s.p",
            "forma adjetiva",
            "forma adjetivo",
            "forma adjetivo 2",
            "forma diminutivo",
            "forma participio",
            "forma pronombre",
            "forma sustantivo",
            "forma sustantivo plural",
            "forma verbo",
            "f.v",
            "gerundio",
            "infinitivo",
            "participio",
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
