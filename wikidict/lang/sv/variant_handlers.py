import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form, rpl={"(av)", "(?)"})


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("böjning", ["sv", "subst", "boll"], defaultdict(str), "")
    'boll'
    >>> render_variant("avledning", ["sv", "abnorm", "adj"], defaultdict(str), "")
    'abnorm'
    """
    return parts[1 if tpl.endswith("avledning") else -1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    template = utils.reconstruct_tpl(tpl, parts, data)
    table = context.expand(template, "sv")

    forms: set[str] = set()
    for line in table.splitlines():
        if not line.startswith("|") or line.startswith(("|-", "|}", '|colspan="2" rowspan="5"')):
            continue
        forms.update(cleanup(form) for form in re.findall(r"\[\[([^\]#]+)", line))

    forms.discard(word)

    return "|".join(sorted(forms))


handlers = {
    **dict.fromkeys(
        {
            "avledning",
            "böjning",
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
