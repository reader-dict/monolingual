from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    Souce: https://eo.wiktionary.org/w/index.php?title=Modulo:meoformo&oldid=1027456
    Date : 2021-12-19 22:43

    >>> render_variant("form-eo", [], defaultdict(str), "ekamus")
    'ekami'
    >>> render_variant("form-eo", [], defaultdict(str), "hispanan")
    'hispana'
    >>> render_variant("form-eo", [], defaultdict(str), "surdaj")
    'surda'
    >>> render_variant("form-eo", [], defaultdict(str), "inexistant")
    'inexistant'
    """
    return next(
        (
            f"{word.removesuffix(suffix)}{last_char}"
            for suffix, last_char in [
                ("on", "o"),
                ("oj", "o"),
                ("ojn", "o"),
                ("an", "a"),
                ("aj", "a"),
                ("ajn", "a"),
                ("as", "i"),
                ("is", "i"),
                ("os", "i"),
                ("us", "i"),
                ("u", "i"),
            ]
            if word.endswith(suffix)
        ),
        word,
    )


handlers = {
    "form-eo": render_variant,
}
