import re
from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["isolatiebedrijf"], defaultdict(str), "isolatiebedrijven")
    'isolatiebedrijf'
    >>> render_variant("flexion", ["[B] cokes"], defaultdict(str), "cokes")
    'cokes'
    """
    return re.sub(r"^\[\w\] ", "", parts[-1].strip())


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["stints"], defaultdict(str), "stint")
    'stints'
    >>> render_reverse_variant("rev-flexion", ["(veiligheidsketting)"], defaultdict(str), "veiligheidskettinkje")
    'veiligheidsketting'
    >>> render_reverse_variant("rev-flexion", ["2"], defaultdict(str), "veiligheidskettinkje")
    ''
    """
    variant = parts[0].strip(" ()")
    return "" if variant.isdigit() else variant


handlers = {
    **dict.fromkeys(
        {
            "flexion",
            "noun-dim",
            "noun-dim-pl",
            "noun-pl",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
}
