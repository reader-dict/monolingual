from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["dass", "Reform 1996"], defaultdict(str), "daß")
    'dass'
    >>> render_variant("flexion", ["profilierend"], defaultdict(str), "profilierende")
    'profilierend'
    >>> render_variant("flexion", [], defaultdict(str, {"1": "rauspumpen"}), "pumpt raus")
    'rauspumpen'
    >>> render_variant("flexion", ["rauspumpen#rauspumpen_(Deutsch)"], defaultdict(str), "pumpt raus")
    'rauspumpen'
    >>> render_variant("flexion", [], defaultdict(str, {"Verb": "ansprechen", "Partizip": "angesprochen"}), "angesprochenen")
    'ansprechen'
    """
    variant = data["1"] or data["Verb"] or parts[0]
    return variant.split("#", 1)[0]


handlers = {
    "flexion": render_variant,
}
