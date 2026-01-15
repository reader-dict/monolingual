import re
from collections import defaultdict

import wikitextparser as wtp

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form, rpl={"<sup>†</sup>"})


def table_to_forms(word: str, wikitext: str) -> list[str]:
    forms: set[str] = set()
    tables = wtp.parse(wikitext).get_tables(recursive=True)

    # Try 1
    for table in tables:
        cells = table.data(span=False)
        for lines in cells:
            for line in lines:
                if "[[" not in line:
                    continue
                if "&ensp;" in line:
                    line = line.split("&ensp;", 1)[1]
                line = re.sub(r"\[\[([^|]+)\|\1\]\]", r"\1", line)
                forms.update(cleanup(form) for form in line.split(","))

        forms.discard("")

        # Try 2
        if not forms:
            for lines in cells:
                for line in lines[1:]:  # Skip the header
                    if not line.endswith("]]"):
                        continue
                    forms.update(cleanup(form) for form in re.findall(r"\[\[([^#]+)#", line))

    forms.discard(word)
    forms.discard("―")
    forms.discard("")

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("forma participio", ["apropiado", "femenino"], defaultdict(str), "")
    'apropiado'
    >>> render_variant("forma participio", ["gastado", "femenino"], defaultdict(str, {"v": "gastar"}), "")
    'gastar'
    """
    return data["v"] or parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["foo"], defaultdict(str), "")
    'foo'
    """
    if tpl == "rev-flexion":
        return parts[0]

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "es")
    if not table.startswith("{|"):
        if (idx := table.find("{|")) == -1:
            return ""
        table = table[idx:]
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(
        {
            "enclítico",
            "f.adj2",
            "f.s.p",
            "forma adjetiva",
            "forma adjetivo",
            "forma adjetivo 2",
            "forma artículo",
            "forma diminutivo",
            "forma participio",
            "forma pronombre",
            "forma sustantivo",
            "forma sustantivo plural",
            "forma verbo",
            "f.v",
            "gerundio",
            "infinitivo",
            "participio",
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
