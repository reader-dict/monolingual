from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["foo"], defaultdict(str), "")
    'foo'
    >>> render_variant("flexion", ["salumiere#Sostantivo", "salumiere"], defaultdict(str), "")
    'salumiere'

    >>> render_variant("tabs", ["muratore", "muratori", "muratrice", "muratore"], defaultdict(str, {"f2": "muratora", "fp2": "muratrici"}), "")
    'muratore'
    >>> render_variant("Tabs", [], defaultdict(str, {"f": "tradotta", "m": "tradotto", "mp": "tradotti", "fp": "tradotte"}), "")
    'tradotto'
    """
    return parts[-1] if tpl == "flexion" else data["m"] or parts[0]


handlers = {
    **dict.fromkeys(
        {
            "flexion",
            "tabs",
            "Tabs",
        },
        render_variant,
    ),
}
