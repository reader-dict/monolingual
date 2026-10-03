import re
from collections import defaultdict

from wikidict import context, utils

REPLACEMENTS: list[str] = []


def cleanup(form: str) -> str:
    cleaned = re.sub(r"\{\{\{\d\}\}\}", r"", form)
    return utils.cleanup_rev_variant(cleaned, rpl=REPLACEMENTS)


def table_to_forms(word: str, wikitext: str) -> list[str]:
    if "<br" in wikitext:
        wikitext = re.sub(r"<br[^>]*+>", "\n| ", wikitext)

    lines = [
        line
        for raw_line in wikitext.splitlines()
        if (
            (line := raw_line.strip())
            and line.startswith("|")
            and not line.startswith(("|-", "|+", "|}"))
            and "Annexe:Prononciation" not in line
        )
    ]

    forms: set[str] = set()
    for line in lines:
        if form := re.search(r"\[\[([^#\]]++)", line) or re.search(rf"'''({word})'''", line):
            cleaned = cleanup(form[1])
            # We want reverse variants for the base word only (the first occurrence in the table)
            if not forms and cleaned != word:
                return []
            forms.add(cleaned)

    forms.discard(word)
    forms.discard("-")
    forms.discard("—")
    forms.discard("+")
    forms.discard("")

    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    if not parts and not (tpl.endswith("-nom") or "décl" in tpl):
        parts.append(word)

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "fr")
    return "|".join(table_to_forms(word, table))


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["foo"], defaultdict(str), "")
    'foo'

    >>> render_variant("fr-verbe-flexion", ["colliger"], defaultdict(str, {"ind.i.3s": "oui"}), "")
    'colliger'
    >>> render_variant("fr-verbe-flexion", [], defaultdict(str, {"1": "dire"}), "")
    'dire'
    """
    return data["1"] or (parts[0] if parts else "")


handlers = {
    "fr-verbe-flexion": render_variant,
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
