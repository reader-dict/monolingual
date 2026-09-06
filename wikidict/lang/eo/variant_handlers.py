import re
from collections import defaultdict

from ... import context, utils


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


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    template = utils.reconstruct_tpl(tpl, parts, data)
    table = context.expand(template, "eo", skip_cache=True)

    forms: set[str] = set()
    for line in table.splitlines():
        if not line.startswith("|") or line[1] in {"-", "}"}:
            continue
        forms.update(re.findall(r"\[\[([^\]]+)\]\]", line))

    forms.discard(word)

    return "|".join(sorted(forms))


handlers = {
    "form-eo": render_variant,
    "rev-flexion": render_reverse_variant,
}
