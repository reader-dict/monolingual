import re
from collections import defaultdict

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form, rpl=["haber ", "(о) "])


def table_to_forms(word: str, wikitext: str) -> list[str]:
    lines = "\n".join(
        [line for line in wikitext.splitlines() if line.startswith("|") and not line.startswith(("|-", "|}"))]
    )

    forms = {
        cleanup(form)
        for form in re.findall(r"\[\[([^#|]++)", lines)
        or re.findall(r"^\|[ ]*+([^|=\n]++)$", lines, flags=re.MULTILINE)
    }
    forms.discard(word)
    forms.discard("―")
    forms.discard("-")
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

        table = re.sub(r"<sup>[^<]+</sup>", "", table)

        # Prevent keeping the "haber" auxiliary
        # `[[habrías|habrías]][[ superscripto| superscripto]]` → `[[superscripto|superscripto]]`
        table = re.sub(r"\[\[(h[^|]++)\|\1\]\]\[\[ ([^|]++)\| \2\]\]", r"[[\2|\2]]", table)

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
