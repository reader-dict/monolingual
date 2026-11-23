import re
from collections import defaultdict
from itertools import chain

RE_VARIANT = re.compile(r"(?m)^\[\w\] ")


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["isolatiebedrijf"], defaultdict(str), "isolatiebedrijven")
    'isolatiebedrijf'
    >>> render_variant("flexion", ["[B] cokes"], defaultdict(str), "cokes")
    'cokes'
    """
    return RE_VARIANT.sub("", parts[0].strip())


RE_PARTS = re.compile(r"\s\[\d\]")
RE_SPLIT1 = re.compile(r"<br\s*+\/?>")
RE_SPLIT2 = re.compile(r",\s*+")
RE_VARIANT2 = re.compile(r"(?m)\b\s*+\([^)]++\),?$")  # `VARIANT(something)`


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
        part = RE_PARTS.sub("", part)
        if "<br" in part:
            variants.update(RE_SPLIT1.sub("|", part).split("|"))
        elif "," in part:
            variants.update(RE_SPLIT2.sub("|", part).split("|"))
        else:
            variants.add(part)

    first_char = word[0]
    res: set[str] = set()
    for variant in variants:
        variant = RE_VARIANT2.sub("", variant)
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
            "1ps",
            "1ps-bijz",
            "1ps-ij",
            "2ps",
            "2ps-bijz",
            "2ps-ij",
            "flexion",
            "nl-adjc-form",
            "noun-dim",
            "noun-dim-pl",
            "noun-pl",
            "ovt-enk",
            "ovt-enk-bijz",
            "ovt-mv",
            "ovt-mv-bijz",
            "tps",
            "tps-bijz",
            "volt-d",
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
