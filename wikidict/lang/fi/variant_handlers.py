import re
from collections import defaultdict

from ... import context, utils

VAR_TEMPLATES = {
    "flexion",
    "fi-komp",
    "fi-pass",
    "fi-pron-taivm",
    "fi-sup",
    "fi-v-taivm",
    "imp.y2",
    "ind.",
    "kond.",
    "taivm-",
    "taivutusmuoto",
    "v-taivm",
}


def cleanup(form: str) -> str:
    """
    >>> cleanup("kreppeine-")
    ''
    """
    cleaned = utils.cleanup_rev_variant(form)
    return "" if cleaned.endswith("-") else cleaned


def table_to_forms(word: str, wikitext: str) -> list[str]:
    lines = "\n".join(
        [
            line
            for raw_line in wikitext.splitlines()
            if (line := raw_line.strip()) and line.startswith("|") and not line.startswith(("|-", "|}"))
        ]
    )
    forms = {cleanup(form) for form in re.findall(r"\[\[([^#]+)#", lines)}
    forms.update(cleanup(form) for form in re.findall(r"#\w+\|([^\]]+)\]\]", lines))

    forms.discard(word)
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> _ = context.reset("fi")

    >>> context.new_word("taiten")
    >>> render_variant("fi-v-taivm", ["t", "aiten}} "], defaultdict(str), "")
    ''

    >>> context.new_word("taon")
    >>> render_variant("fi-v-taivm", ["t", "aon", "takoa", "ind", "p", "y", "1"], defaultdict(str), "")
    'takoa'

    >>> context.new_word("monista")
    >>> render_variant("fi-v-taivm1", ["53", "m", "onist", "a"], defaultdict(str), "")
    'monistaa'
    """
    expanded = context.expand(utils.reconstruct_tpl(tpl, parts, data), "fi")
    return bases[0] if (bases := re.findall(r"\[\[([^#]+)#", expanded)) else ""


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "fi")
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(VAR_TEMPLATES, render_variant),
    "rev-flexion": render_reverse_variant,
}


def append_to_variants(tpl: str) -> None:
    """Dynamically append a template to variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_variant


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
