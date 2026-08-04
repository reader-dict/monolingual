import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    """
    >>> cleanup("najbardziej rozpowszechnionemu")
    'rozpowszechnionemu'
    """
    return utils.cleanup_rev_variant(
        form,
        rpl={"najbardziej ", "bardziej ", " się"},
    )


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["jeść"], defaultdict(str), "jesz")
    'jeść'
    """
    return parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "pl")
    table = table.replace(' colspan="2"', "")

    forms = {cleanup(form) for form in re.findall(r"<td[ ]*>([^<]+)</td>", table)}
    forms.discard(word)

    return "|".join(sorted(forms))


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
