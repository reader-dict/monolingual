from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("ca-forma-conj", ["abacallanar", "1", "pres", "ind"], defaultdict(str), "abacallan")
    'abacallanar'
    >>> render_variant("forma-conj", ["ca", "abacallanar", "1", "pres", "ind"], defaultdict(str), "abacallan")
    'abacallanar'
    >>> render_variant("forma-f", ["ca", "-à"], defaultdict(str), "-ana")
    '-à'
    >>> render_variant("forma-p", ["ca", "-alla"], defaultdict(str), "-alles")
    '-alla'
    """
    return parts[0 if "-forma-conj" in tpl else 1]


handlers = {
    **dict.fromkeys(
        {
            "ca-forma-conj",
            "forma-conj",
            "forma-f",
            "forma-p",
        },
        render_variant,
    ),
}
