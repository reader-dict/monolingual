import re
from collections import defaultdict

from wikidict import context, utils

REPLACEMENTS: list[str] = []
RE_NUMBER = re.compile(r"\{\{\{\d\}\}\}")


def cleanup(form: str) -> str:
    cleaned = RE_NUMBER.sub("", form)
    return utils.cleanup_rev_variant(cleaned, rpl=REPLACEMENTS)


RE_BR = re.compile(r"<br[^>]*+>")
RE_FORMS1 = re.compile(r"\[\[([^#|]++)[^|]++\|([^\]]++)")
RE_FORMS2 = re.compile(r"\[\[([^#|\]]++)")


def table_to_forms(word: str, wikitext: str) -> list[str]:
    if "<br" in wikitext:
        wikitext = RE_BR.sub("\n| ", wikitext)

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
    just_the_word = re.compile(rf"'''({word})'''")
    for line in lines:
        if form := RE_FORMS1.search(line) or RE_FORMS2.search(line) or just_the_word.search(line):
            findings = form.groups()
            cleaned = cleanup(findings[0])
            # We want reverse variants for the base word only (the first occurrence in the table)
            if not forms and cleaned != word:
                return []
            forms.add(cleaned)
            if len(findings) > 1:
                forms.add(cleanup(findings[1]))

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
