import re
from collections import defaultdict

from ... import context, utils


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["tale"], defaultdict(str), "")
    'tale'

    >>> render_variant("{{form of", ["imperative form", "bjerge"], defaultdict(str, {"lang": "da"}), "")
    'bjerge'
    """
    return parts[-1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    forms: set[str] = set()
    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "da")
    if "verb" in tpl:
        for form in re.findall(r"<b>\[\[([^\]]+)\]\]</b>", table):
            if "/" in form:
                forms.update(form.split("/"))
            else:
                forms.add(form)
    elif "infl" in tpl:
        forms = set(re.findall(r'\| style="background-color:#f9f9f9;"\|\s*\[\[(.*?)\]\]', table))
    else:
        forms = set(re.findall(r"\[\[(.+)#\w+\|\1\]\]", table))
    return "|".join(utils.remove_parens(form.strip()) for form in forms if "{" not in form if form and form != "-")


handlers = {
    **dict.fromkeys(
        {
            "alternativ stavemåde af",
            "flexion",
            "form of",
            "imperativ af",
            "imperativ form af",
        },
        render_variant,
    ),
    **dict.fromkeys(
        {"rev-flexion", "da-noun", "da-noun-infl", "da-verb"},
        render_reverse_variant,
    ),
}
