import re
from collections import defaultdict
from functools import partial

import wikitextparser as wtp

from ... import context, utils

cleanup = partial(utils.cleanup_rev_variant, skip={"akkusativ", "bestemt", "dativ", "genitiv", "nominativ", "ubestemt"})


def table_to_forms(word: str, wikitext: str) -> list[str]:
    forms: set[str] = set()
    tables = wtp.parse(wikitext).get_tables(recursive=True)

    # Try 1
    for table in tables:
        line = str(table).splitlines()[2]
        for form in re.findall(r"<b>\[\[([^\]#]+)", line):
            if "<br />" in form:
                forms.update([cleanup(f) for f in form.split("<br />")])
            elif "/" in form:
                forms.update([cleanup(f) for f in form.split("/")])
            else:
                forms.add(cleanup(form))

    # Try 2
    if not forms:
        for table in tables:
            data = table.data(span=False)
            for lines in data[1:]:
                for line in lines:
                    if not line or "''" in line:
                        continue
                    if form := re.findall(r"\[\[([^\]#]+)", line):
                        forms.add(cleanup(form[0]))
                    # Try 3
                    elif line.strip("[]()"):
                        if ",<br>" in line:
                            forms.update([cleanup(f) for f in line.split(",<br>")])
                        else:
                            forms.add(cleanup(line))

    forms.discard(word)
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    if "s" in forms:
        forms.discard("s")
        forms.add(f"{word}s")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["tale"], defaultdict(str), "")
    'tale'

    >>> render_variant("{{form of", ["imperative form", "bjerge"], defaultdict(str, {"lang": "da"}), "")
    'bjerge'
    """
    return parts[-1]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    template = "|".join((*parts, *[f"{k}={v}" for k, v in data.items()]))
    table = context.expand(f"{{{{{tpl}|{template}}}}}", "da")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(
        {
            "alternativ stavemåde af",
            "flexion",
            "form of",
            "imperativ af",
            "imperativ form af",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
