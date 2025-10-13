import re
from collections import defaultdict

from ... import context


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["tale"], defaultdict(str), "")
    'tale'

    >>> render_variant("{{form of", ["imperative form", "bjerge"], defaultdict(str, {"lang": "da"}), "")
    'bjerge'
    """
    return parts[-1]


def remove_parens(text: str) -> str:
    if "(" in text:
        # atlase(r)ne
        text = re.sub(r"(\w+)\b\((\w+)\)\b(\w+)", r"\1\2\3", text)
    if "(" in text:
        # atlas(ser)
        text = re.sub(r"(\w+)\b\((\w+)\)", r"\1\2", text)
    return text


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    forms: set[str]
    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "da")
    if "verb" in tpl:
        forms = set(re.findall(r"<b>\[\[([^\]]+)\]\]</b>", table))
    elif "infl" in tpl:
        forms = set(re.findall(r'\| style="background-color:#f9f9f9;"\|\s*\[\[(.*?)\]\]', table))
    else:
        forms = set(re.findall(r"\[\[(.+)#\w+\|\1\]\]", table))
    return "|".join(remove_parens(form.strip()) for form in forms if "{" not in form if form and form != "-")


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
