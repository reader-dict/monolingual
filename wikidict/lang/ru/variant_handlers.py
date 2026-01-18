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

    raw_forms: list[str]
    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "ru")
    if table.startswith("{"):
        table = re.sub(r'^\| class="grey".+$', "", table, flags=re.MULTILINE)
        table = table.replace("<br>", "\n| ").replace("<br/>", "\n| ")
        raw_forms = [
            form[2:].strip() for form in table.splitlines() if form.startswith("| ") and not form.endswith("| ")
        ]
    else:
        table = table.replace("<br>", "</td><td>").replace("<br/>", "</td><td>").replace(' rowspan="2"', "")
        raw_forms = re.findall(r"<td>([^<]+)</td>", table)

    if not raw_forms:
        return ""

    first_variant = raw_forms[0]

    forms = {cleanup(form) for form in raw_forms}
    forms.discard("")

    if len(remove_diacritics(first_variant)) == len(remove_diacritics(word)) and first_variant != word:
        # When the base form is different than the template argument, we generate both.
        # Ex: the "подельник" word uses the "поде́льник" argument
        # Ex: the "типографский" word uses the "типогра́фск" argument
        current_forms = forms.copy()
        for base_idx in ["", "1", "2", "3"]:
            if not (provided_base := data[f"основа{base_idx}"]):
                break
            base_without_accents = remove_diacritics(provided_base)
            new_word_base = word[: len(base_without_accents)]
            for form in current_forms:
                forms.add(form.replace(provided_base, new_word_base, count=1))

    forms.discard(word)

    return "|".join(forms)


def remove_diacritics(text: str) -> str:
    """
    >>> remove_diacritics("типографск")
    'типографск'
    >>> remove_diacritics("типогра́фск")
    'типографск'
    """
    return "".join(c for c in list(text) if name(c) != "COMBINING ACUTE ACCENT")


handlers = {
    "прич.": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
