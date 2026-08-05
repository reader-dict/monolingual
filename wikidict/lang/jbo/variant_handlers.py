from collections import defaultdict


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    >>> render_reverse_variant("jbo-gismu", ["mun"], defaultdict(str), "smuni")
    'mun'
    >>> render_reverse_variant("jbo-gismu", ["mun", "smu"], defaultdict(str), "smuni")
    'mun|smu'
    """
    if tpl == "rev-flexion":
        return parts[0]

    return "|".join(sorted(parts))


handlers = {
    "rev-flexion": render_reverse_variant,
    "jbo-gismu": render_reverse_variant,
}
