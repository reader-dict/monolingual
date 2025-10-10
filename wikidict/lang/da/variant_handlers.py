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


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()
    # da-noun-infl
    forms: set[str]
    table = context.expand(f"{{{{{tpl}|{'|'.join(parts)}|{'|'.join(f'{k}={v}' for k, v in data.items())}}}}}", "da")
    pattern = r'^\|\s*style="background-color:[^"]*"\|\s*\[\[(.*?)\]\]'
    forms = set(re.findall(pattern, table, flags=re.MULTILINE))
    return "|".join(form.strip() for form in forms if "{" not in form if form)


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
        {"rev-flexion", "da-noun-infl"},
        render_reverse_variant,
    ),
}
