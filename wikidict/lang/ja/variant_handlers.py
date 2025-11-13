from collections import defaultdict

import wikitextparser as wtp

from ... import context, utils


def cleanup(form: str) -> str:
    return form.removesuffix("<small>(古)</small>")


def table_to_forms(word: str, wikitext: str) -> list[str]:
    forms: set[str] = set()
    tables = wtp.parse(wikitext).get_tables(recursive=True)

    for table in tables[1:]:  # skip the information table
        data = table.data(span=False)
        for line in data[1:]:  # skip headers
            form = str(line[1])

            if "<br" in form:
                forms.update(cleanup(f) for f in form.split("<br />"))
            else:
                forms.add(cleanup(form))

    forms.discard(word)
    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["顧眄せず"], defaultdict(str), "顧眄")
    '顧眄せず'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "ja")
    return "|".join(table_to_forms(word, table))


handlers = {
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
