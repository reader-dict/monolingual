import re
from collections import defaultdict
from itertools import chain


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
    if tpl == "rev-flexion":
        variant = parts[0].strip(" ()")
        return "" if variant.isdigit() else variant

    variants: set[str] = set()
    for part in chain(parts, data.values()):
        if not part:
            continue
        if "<br" in part:
            variants.update(re.sub(r"<br\s*/?>", "|", part).split("|"))
        else:
            variants.add(part)

    first_char = word[0]
    res: set[str] = set()
    for variant in variants:
        variant = re.sub(r"\b\s*\([^)]+\),?$", "", variant, flags=re.MULTILINE)  # `VARIANT(something)`
        variant = variant.split(" <i>(", 1)[0]  # VARIANT <i>(something)</i>
        variant = variant.split(")</i> ", 1)[-1]  # <i>(something)</i> VARIANT
        variant = variant.strip(" ()[].*,")
        variant = variant.replace("<i>(", "").replace(")</i>", "")
        if variant and variant[0] == first_char and variant != word:
            res.add(variant)

    return "|".join(sorted(res))


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


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
