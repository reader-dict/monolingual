from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("forma participio", ["apropiado", "femenino"], defaultdict(str), "")
    'apropiado'
    >>> render_variant("forma participio", ["gastado", "femenino"], defaultdict(str, {"v": "gastar"}), "")
    'gastar'
    """
    return data["v"] or parts[0]


handlers = {
    **dict.fromkeys(
        {
            "enclítico",
            "f.adj2",
            "f.s.p",
            "forma adjetiva",
            "forma adjetivo",
            "forma adjetivo 2",
            "forma diminutivo",
            "forma participio",
            "forma pronombre",
            "forma sustantivo",
            "forma sustantivo plural",
            "forma verbo",
            "f.v",
            "gerundio",
            "infinitivo",
            "participio",
        },
        render_variant,
    ),
}
