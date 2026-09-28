import re
from collections import defaultdict

from wikidict import context, utils


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("ουδ του-πτώσειςΟΑΚεν", ["επίπεδος"], defaultdict(str), "επίπεδο")
    'επίπεδος'
    >>> render_variant("ουδ του-πτώσειςΟΑΚπλ", ["-άδικος"], defaultdict(str), "-άδικο")
    '-άδικος'
    >>> render_variant("ουδ του-πτώσηΓεν", ["έβδομος"], defaultdict(str), "έβδομου")
    'έβδομος'
    >>> render_variant("ουδ του-πτώσηΓπλ", ["έβδομος"], defaultdict(str), "έβδομου")
    'έβδομος'

    >>> render_variant("αρσ του-πτώσηΓεν", ["έβδομος"], defaultdict(str), "έβδομου")
    'έβδομος'
    >>> render_variant("αρσ του-πτώσηΓπλ", ["έβδομος"], defaultdict(str), "έβδομων")
    'έβδομος'

    >>> render_variant("πτώσειςΟΑΚπλ", ["Ελληνούπολη"], defaultdict(str), "Ελληνουπόλεις")
    'Ελληνούπολη'

    >>> render_variant("πτώσηΑεν", ["επίπεδος"], defaultdict(str), "επίπεδο")
    'επίπεδος'

    >>> render_variant("θηλ του", ["τσιγγάνος"], defaultdict(str), "τσιγγάνα")
    'τσιγγάνος'
    >>> render_variant("θηλ του-πτώσειςΟΑΚπλ", ["έγγαμος"], defaultdict(str), "έγγαμες")
    'έγγαμος'

    >>> render_variant("απαρ", ["ενεστώτα", "miror"], defaultdict(str), "Μιρέλλα")
    'miror'
    >>> render_variant("απαρ", ["ενεστώτα", "miror", "en", "foo"], defaultdict(str), "Μιρέλλα")
    'miror'

    >>> render_variant("μτχα", ["förklara", "sv"], defaultdict(str), "förklarad")
    'förklara'
    """
    match tpl:
        case "απαρ":
            return parts[1]
        case "μτχα":
            return parts[0]
        case _:
            return parts[-1] if parts else word


def cleanup(form: str) -> str:
    return utils.cleanup_rev_variant(form)


def table_to_forms(word: str, wikitext: str) -> list[str]:
    kept_lines: list[str] = []
    for raw_line in wikitext.splitlines():
        if not (line := raw_line.strip()) or not line.startswith("|") or line.startswith(("|-", "| style", "|}")):
            continue

        if "rowspan" in line:
            line = re.sub(r"\s*+rowspan[^|]++\|", "", line)
        if line == "|":
            continue

        if "<br />" in line:
            kept_lines.extend(l_.strip(" |") for l_ in line.split("<br />"))
        else:
            kept_lines.append(line.strip(" |"))

    for idx in range(len(kept_lines)):
        line = kept_lines[idx]
        if "(" in line:
            kept_lines[idx] = re.sub(r"[()]", "", line)
            kept_lines.append(re.sub(r"\([^)]++\)", "", line))

    word_spaces_count = word.count(" ")
    for idx in range(len(kept_lines)):
        line = kept_lines[idx]
        if line.count(" ") > word_spaces_count:
            kept_lines[idx] = line.rsplit(" ", word_spaces_count + 1)[-1]

    forms = {cleanup(form) for form in kept_lines}

    forms.discard(word)
    forms.discard("-")
    forms.discard("—")
    forms.discard("")

    return sorted(forms)


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["baskylen"], defaultdict(str), "baskyle")
    'baskylen'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "el")
    return "|".join(table_to_forms(word, table))


handlers = {
    **dict.fromkeys(
        {
            "ρημ τύπος",
            "ρημ_τύπος",
            "θηλ του",
            "θηλ_του",
            "θηλυκό του",
            "θηλυκό_του",
            "θηλ του-πτώσειςΟΑΚεν",
            "θηλ_του-πτώσειςΟΑΚεν",
            "θηλ του-πτώσηΓπλ",
            "θηλ_του-πτώσηΓπλ",
            "θηλ του-πτώσειςΟΑΚπλ",
            "θηλ_του-πτώσειςΟΑΚπλ",
            "θηλ του-πτώσηΓεν",
            "θηλ_του-πτώσηΓεν",
            "θηλ του-πτώσειςΟΚεν",
            "θηλ_του-πτώσειςΟΚεν",
            "ουδ του",
            "ουδ_του",
            "ουδ του-πτώσειςΟΑΚεν",
            "ουδ_του-πτώσειςΟΑΚεν",
            "ουδ του-πτώσειςΟΑΚπλ",
            "ουδ_του-πτώσειςΟΑΚπλ",
            "ουδ του-πτώσηΓπλ",
            "ουδ_του-πτώσηΓπλ",
            "ουδ του-πτώσηΓεν",
            "ουδ_του-πτώσηΓεν",
            "αρσ του",
            "αρσ_του",
            "αρσ του-πτώσηΓεν",
            "αρσ_του-πτώσηΓεν",
            "αρσ του-πτώσηΓπλ",
            "αρσ_του-πτώσηΓπλ",
            "αρσ του-πτώσηΑεν",
            "αρσ_του-πτώσηΑεν",
            "πτώση",
            "πτώσηΔεν",
            "πτώσηΑπλ",
            "πτώσηΓπλ",
            "πτώσηΑεν",
            "πτώσηΚεν",
            "πτώσηΓεν",
            "πτώσεις",
            "πτώσειςΟΑΚπλ",
            "πτώσειςΟΚπλ",
            "πτώσειςΓΑΚεν",
            "πτώσειςΟΑΚεν",
            "πληθ_του",
            "πληθυντικός του",
            "κλ",
            "απαρ",
            "πλ",
            "μτχα",
            "infl",
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
