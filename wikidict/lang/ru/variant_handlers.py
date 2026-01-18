import re
import unicodedata
from collections import defaultdict

from ... import context, utils


def strip_accents(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn")


def cleanup(form: str) -> str:
    return strip_accents(utils.cleanup_rev_variant(form))


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("Форма-гл", [], defaultdict(str, {'база': 'выбирать', 'время': 'пр', 'род': '', 'лицо': '123', 'число': 'мн', 'накл': '', 'деепр': '', 'прич': '', 'кр': '', 'помета': '', 'знач': '', 'язык': 'ru', 'слоги': 'выбирали', 'МФА': '', 'аудио': '', 'омофоны': '', 'коммент': '', 'дореф': ''}), "выбирали")
    'выбирать'

    >>> render_variant("прич.", ["зыбить"], defaultdict(str), "")
    'зыбить'
    >>> render_variant("прич.", ["находить (наталкиваться)", "наст"], defaultdict(str), "")
    'находить'
    >>> render_variant("прич.", ["<small>?</small>"], defaultdict(str), "")
    ''
    """
    if tpl == "Форма-гл" and (base := data["база"]):
        return base

    if (variant := parts[0]) == "<small>?</small>":
        variant = ""
    if " (" in variant:
        variant = variant.split(" (", 1)[0]
    return variant


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["коро́ль"], defaultdict(str), "")
    'коро́ль'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    forms: set[str]
    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "ru")
    if table.startswith("{"):
        table = re.sub(r'^\| class="grey".+$', "", table, flags=re.MULTILINE)
        table = table.replace("<br>", "\n| ").replace("<br/>", "\n| ")
        forms = {form[2:].strip() for form in table.splitlines() if form.startswith("| ") and not form.endswith("| ")}
    else:
        table = table.replace("<br>", "</td><td>").replace("<br/>", "</td><td>").replace(' rowspan="2"', "")
        forms = set(re.findall(r"<td>([^<]+)</td>", table))

    if not forms:
        return ""

    forms = {cleanup(form) for form in forms}
    forms.discard("")
    forms.discard(word)

    return "|".join(forms)


handlers = {
    "прич.": render_variant,
    "Форма-гл": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
