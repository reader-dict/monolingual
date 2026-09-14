import re
from collections import defaultdict

from ... import context, utils

VAR_TEMPLATES = {
    "flexion",
    "fi-komp",
    "fi-pass-ppe",
    "fi-sup",
    "fi-v-taivm1",
    "fi-v-taivm",
    "imp.y2",
    "ind.kon",
    "ind.i.y3",
    "kond.y3",
    "taivm-3inf-abess",
    "taivm-3inf-ablat",
    "taivm-3inf-adess",
    "taivm-3inf-elat",
    "taivm-3inf-illat",
    "taivm-3inf-iness",
    "taivm-3inf-ins",
    "taivm-agpart",
    "taivm-agpart-kielt",
    "taivm-akt-pperf",
    "taivm-akt-pprees",
    "taivm-ind.kon",
    "taivm-imp.y2",
    "taivm-imp.y2.kon",
    "taivm-komp",
    "taivm-mon",
    "taivm-mon-abess",
    "taivm-mon-adess",
    "taivm-mon-aak",
    "taivm-mon-abl",
    "taivm-mon-all",
    "taivm-mon-akk",
    "taivm-mon-elat",
    "taivm-mon-ess",
    "taivm-mon-gen",
    "taivm-mon-ill",
    "taivm-mon-iness",
    "taivm-mon-ins",
    "taivm-mon-kom",
    "taivm-mon-nom",
    "taivm-mon-part",
    "taivm-mon-tr",
    "taivm-nomini",
    "taivm-pass-pperf",
    "taivm-pass-pprees",
    "taivm-superl",
    "taivm-y-abess",
    "taivm-y-abl",
    "taivm-y-adess",
    "taivm-y-akk",
    "taivm-y-all",
    "taivm-y-elat",
    "taivm-y-ess",
    "taivm-y-gen",
    "taivm-y-ill",
    "taivm-y-iness",
    "taivm-y-ins",
    "taivm-y-lok",
    "taivm-y-nom",
    "taivm-y-part",
    "taivm-y-tr",
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
    >>> render_variant("flexion", ["tale"], defaultdict(str), "")
    'tale'

    >>> render_variant("taivm-nomini", [], defaultdict(str, {"k": "fi", "perusmuoto": "se", "luok": "dempron", "sija": "ess"}), "")
    'se'
    >>> render_variant("taivutusmuoto", ["yrittää", "fi", "verbi"], defaultdict(str), "")
    'yrittää'

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
    if tpl == "flexion":
        return parts[-1]

    if tpl.endswith(("taivm", "taivm1")):
        expanded = context.expand(utils.reconstruct_tpl(tpl, parts, data), "fi")
        return bases[0] if (bases := re.findall(r"\[\[([^#]+)#", expanded)) else ""

    return data["perusmuoto"] or parts[0 if tpl == "taivutusmuoto" else -1]


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


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
