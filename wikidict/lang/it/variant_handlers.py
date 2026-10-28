from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["foo"], defaultdict(str), "")
    'foo'
    >>> render_variant("flexion", ["salumiere#Sostantivo", "salumiere"], defaultdict(str), "")
    'salumiere'
    """
    return parts[-1]


handlers = {
    **dict.fromkeys({"flexion"}, render_variant),
}
