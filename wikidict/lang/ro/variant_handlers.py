from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("adj form of", ["ro", "frumos", "", "m", "p"], defaultdict(str), "")
    'frumos'
    >>> render_variant("forma de vocativ singular pentru", ["a", "word"], defaultdict(str), "")
    'word'
    """
    return parts[1] if "adj form of" in tpl else parts[-1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["pietrele"], defaultdict(str), "piatră")
    'pietrele'
    """
    return parts[0]


handlers = {
    **dict.fromkeys(
        {
            "adj form of",
            "flexion",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
}
