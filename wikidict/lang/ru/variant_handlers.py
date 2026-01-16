import re
from collections import defaultdict
from unicodedata import name

from ... import context, utils


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form)


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("прич.", ["зыбить"], defaultdict(str), "")
    'зыбить'
    >>> render_variant("прич.", ["находить (наталкиваться)", "наст"], defaultdict(str), "")
    'находить'
    >>> render_variant("прич.", ["<small>?</small>"], defaultdict(str), "")
    ''
    """
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

    if need_to_dedup_forms(word, data["основа"]):
        # When the base form is different than the template argument, we generate both.
        # Ex: the "подельник" word uses the "поде́льник" argument
        provided_base = data["основа"]
        for form in forms.copy():
            forms.add(form.replace(provided_base, word))
        forms.add(provided_base)

    forms.discard(word)

    return "|".join(forms)


def need_to_dedup_forms(orginal_base: str, provided_base: str) -> bool:
    if not orginal_base or not provided_base:
        return False

    normalized_1 = [c for c in list(orginal_base) if name(c) != "COMBINING ACUTE ACCENT"]
    normalized_2 = [c for c in list(provided_base) if name(c) != "COMBINING ACUTE ACCENT"]
    return len(normalized_1) == len(normalized_2) and orginal_base != provided_base


handlers = {
    "прич.": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
