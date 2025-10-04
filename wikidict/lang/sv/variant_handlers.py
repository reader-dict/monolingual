from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("böjning", ["sv", "subst", "boll"], defaultdict(str), "")
    'boll'
    >>> render_variant("avledning", ["sv", "abnorm", "adj"], defaultdict(str), "")
    'abnorm'
    """
    return parts[1 if tpl.endswith("avledning") else -1]


handlers = {
    **dict.fromkeys(
        {
            "avledning",
            "böjning",
        },
        render_variant,
    )
}
