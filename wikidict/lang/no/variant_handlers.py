import re
from collections import defaultdict

from ... import context, utils


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "no")
    lines = [
        line for line in table.splitlines() if re.match(r"^\|[ ]*(?:å |eit |har |'*)?\[+", line, flags=re.MULTILINE)
    ]
    forms: set[str] = set()
    for line in lines:
        forms.update(re.findall(r"\[\[([^#\]]+)", line))

    forms.discard(word)
    forms.discard("-")
    return "|".join(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("bøyingsform", ["no", "verb", "uttrykke"], defaultdict(str), "")
    'uttrykke'
    >>> render_variant("no-adj-bøyningsform", ["b", "vis"], defaultdict(str, {"nb": "ja", "nrm": "ja", "nn": "ja"}), "")
    'vis'
    """
    return parts[-1]


handlers = {
    **dict.fromkeys(
        {
            "bøyingsform",
            "bøyningsform",
            "no-adj-bøyningsform",
            "no-sub-bøyningsform",
            "no-verb-bøyningsform",
            "no-verbform av",
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
