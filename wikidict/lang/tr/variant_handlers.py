import re
from collections import defaultdict

from ... import context, utils

RE_CLEANUP = re.compile(r"""(?m)^\| style=["'][^"']++["']\s*+""")
RE_LOOP = re.compile(r"(?m)\|.+Template loop detected:.+\]\](.*)")
RE_FIND_FORMS1 = re.compile(r"\[\[([^#\]]++)\]\]")  # `[[foo]]` or `[[föo|foo]]`
RE_FIND_FORMS2 = re.compile(r"(?m)^\|[ ]*+([^\n]++)")
RE_FIND_FORMS3 = re.compile(r"\[\[[^#]++[^|]++\|([^\]]++)\]\]")  # `[[foö#Türkçe|foo]]``


def table_to_forms(word: str, wikitext: str) -> list[str]:
    lines = RE_CLEANUP.sub("", wikitext)

    if "Template loop detected" in lines:
        # `| (...) Template loop detected: [[&#x3a;Template&#x3a;SAYFAADI#Türkçe|:Template:SAYFAADI]]es` → `| [[WORDes]]`
        lines = RE_LOOP.sub(rf"| [[{word}\1]]", lines)

    lines = "\n".join(
        line
        for raw_line in lines.splitlines()
        if (line := raw_line.strip())
        and (
            line[0] == "|"
            and not line.startswith(("|-", "|+", "| —", "| '''", "|}"))
            and "rowspan" not in line
            and "colspan" not in line
        )
    )
    lines = lines.replace("]]<br>[[", "]]\n| [[")

    forms: set[str] = set()
    for form in RE_FIND_FORMS1.findall(lines):
        if "|" in form:
            forms.update(utils.cleanup_rev_variant(f_) for f_ in form.split("|"))
        else:
            forms.add(utils.cleanup_rev_variant(form))

    if not forms:
        forms.update(utils.cleanup_rev_variant(form) for form in RE_FIND_FORMS2.findall(lines))

    if "#" in lines:
        for form in RE_FIND_FORMS3.findall(lines):
            forms.add(utils.cleanup_rev_variant(form))

    forms.discard(word)

    return sorted(forms)


RE_VARIANT = re.compile(r"<i>\[\[[^|]++\|([^\]]++)\]\]</i>")


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["bulmaca"], defaultdict(str), "bulmacamda")
    'bulmaca'

    >>> render_variant("çekim", ["payandalamak", "", "2t", "imp", "neg"], defaultdict(str, {"dil": "tr"}), "payandalama")
    'payandalamak'

    >>> render_variant("hâl", ["Avusturyalılık", "ğın"], defaultdict(str), "Avusturyalılık'ın")
    'Avusturyalılık'
    >>> render_variant("hâl", [], defaultdict(str), "Avusturyalılık'ın")
    'Avusturyalılık'

    >>> render_variant("mastarı", ["payandalamak"], defaultdict(str, {"dil": "tr"}), "payandalama")
    'payandalamak'

    >>> _ = context.reset("tr")

    >>> context.new_word("yüz")
    >>> render_variant("fiil", ["yüz", ""], defaultdict(str), "yüz")
    'yüzmek'
    """
    if tpl == "flexion":
        return parts[0].strip()

    if tpl != "fiil":
        return parts[0] if parts else word.split("'", 1)[0]

    expanded = context.expand(utils.reconstruct_tpl(tpl, parts, data), "tr")
    if base := RE_VARIANT.search(expanded):
        return base[1]
    return ""


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["iğne yapraklarda"], defaultdict(str), "iğne yaprak")
    'iğne yapraklarda'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "tr")
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(
        {
            "ad-hâl",
            "çekim",
            "fiil",
            "flexion",
            "hâl",
            "mastarı",
        },
        render_variant,
    ),
    "rev-flexion": render_reverse_variant,
    # This is not useful to keep that data since it changes the previous words only, not the current one
    # Ex: https://tr.wiktionary.org/wiki/ketum
    "çekim-sıfat": lambda *_: "",
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
