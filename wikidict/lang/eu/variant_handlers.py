import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form)


def table_to_forms(word: str, wikitext: str) -> list[str]:
    wikitext = wikitext.replace(" || ", "\n| ")
    wikitext = re.sub(r"\[//\w++.wiktionary.org[^ ]++ ([^\]]++)\]", r"[[\1]]", wikitext)
    lines = "\n".join(
        [
            line
            for line in wikitext.splitlines()
            if line.startswith("|")
            and not line.startswith(("|-", "|}"))
            and "background:" not in line
            and "bgcolor" not in line
        ]
    )

    forms = {
        cleanup(form)
        for form in re.findall(r"\[\[([^#|\]]++)", lines)
        or re.findall(r"^\|[ ]*+([^|=\n]++)$", lines, flags=re.MULTILINE)
    }
    forms.discard(word)
    forms.discard("―")
    forms.discard("-")
    forms.discard("")

    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "eu")
    return "|".join(table_to_forms(word, table))


handlers = {
    "flexion": lambda tpl_, parts, data_, word_: parts[0],
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
