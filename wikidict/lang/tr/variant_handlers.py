import re
from collections import defaultdict

from ... import context, utils


def table_to_forms(word: str, wikitext: str) -> list[str]:
    lines = re.sub(r"""^\| style=["'][^"']+["']\s*""", "", wikitext, flags=re.MULTILINE)

    if "Template loop detected" in lines:
        # `| (...) Template loop detected: [[&#x3a;Template&#x3a;SAYFAADI#Türkçe|:Template:SAYFAADI]]es` → `| [[WORDes]]`
        lines = re.sub(r"\|.+Template loop detected:.+\]\](.+)", rf"| [[{word}\1]]", lines, flags=re.MULTILINE)

    lines = "\n".join(line for line in lines.splitlines() if line.startswith("| ["))
    lines = lines.replace("]]<br>[[", "]]\n| [[")

    forms = set(re.findall(r"\[\[([^#\]]+)\]\]", lines))  # `[[foo]]`
    if "#" in lines:
        forms.update(re.findall(r"#[^|]+\|([^\]]+)\]\]", lines))  # `[[foö#Türkçe|foo]]`

    forms.discard(word)

    return sorted(forms)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["bulmaca"], defaultdict(str), "bulmacamda")
    'bulmaca'

    >>> render_variant("çekim", ["payandalamak", "", "2t", "imp", "neg"], defaultdict(str, {"dil": "tr"}), "payandalama")
    'payandalamak'

    >>> render_variant("hâl", ["Avusturyalılık", "ğın"], defaultdict(str), "Avusturyalılık'ın")
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
        return parts[0]

    expanded = context.expand(utils.reconstruct_tpl(tpl, parts, data), "tr")
    return str(re.findall(r"<i>\[\[[^\|]+\|([^\]]+)\]\]</i>", expanded)[0])


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
