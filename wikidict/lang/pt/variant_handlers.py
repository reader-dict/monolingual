import re
from collections import defaultdict

import wikitextparser as wtp

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form, rpl={"não "}, skip={"plural", "singular", "subjuntivo"})


def table_to_forms(word: str, wikitext: str) -> list[str]:
    wikitext = re.sub(r"<sup>\d+</sup>", "", wikitext)
    wikitext = wikitext.replace("<br>", "\n| ").replace("<br/>", "\n| ")

    forms: set[str] = set()
    tables = wtp.parse(wikitext).get_tables(recursive=True)

    for table in tables:
        cells = table.data(span=False)
        for lines in cells:
            for item in lines:
                if not item or "''" in item:
                    continue
                raw_forms = re.findall(r"\[\[(.+)#\w+\|\1\]\]", item) or [item]
                forms.update([cleanup(form) for form in raw_forms])

    forms.discard(word)
    forms.discard("&ndash;")
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["ensimesmar"], defaultdict(str), "")
    'ensimesmar'
    """
    return parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "pt")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table))


handlers = {
    "flexion": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
