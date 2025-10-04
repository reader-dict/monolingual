from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("bøyingsform", ["no", "verb", "uttrykke"], defaultdict(str), "")
    'uttrykke'
    >>> render_variant("no-adj-bøyningsform", ["b", "vis"], defaultdict(str, {"nb": "ja", "nrm": "ja", "nn": "ja"}), "")
    'vis'
    """
    return parts[-1]


handlers = {
    **dict.fromkeys(
        {
            "bøyingsform",
            "bøyningsform",
            "no-adj-bøyningsform",
            "no-sub-bøyningsform",
            "no-verb-bøyningsform",
            "no-verbform av",
        },
        render_variant,
    ),
}
