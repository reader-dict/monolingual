from collections import defaultdict

from ...user_functions import extract_keywords_from


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("adj form of", ["ro", "frumos", "", "m", "p"], defaultdict(str))
    'frumos'
    >>> render_variant("forma de vocativ singular pentru", ["a", "word"], defaultdict(str))
    'word'
    """
    return parts[1] if "adj form of" in tpl else parts[-1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["pietrele"], defaultdict(str), word="piatră")
    'pietrele'
    """
    return parts[0]


template_mapping = {
    #
    # Variants
    #
    "__variant__adj form of": render_variant,
    "__variant__flexion": render_variant,
    #
    # Reverse variants
    #
    "__variant__rev-flexion": render_reverse_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
