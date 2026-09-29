import re
from collections import defaultdict

import wikitextparser as wtp

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
    """
    >>> cleanup("παρακΒ=1")
    ''
    """
    cleaned = utils.cleanup_rev_variant(form)
    return "" if "=" in cleaned else cleaned


def escape(value: str) -> str:
    """
    >>> escape("ζυγός")
    'ζυγός'
    >>> escape("[[ζυγός|ζυγός]]")
    'ζυγός'
    >>> escape("[[ζυγός#Νέα ελληνικά (el)|ζυγός]]")
    'ζυγός'
    >>> escape("διαγραφ(τ)ούν(ε)")
    'διαγραφτούνε'
    """
    res = value.split("|")[-1].rstrip("]")
    if "(" in res:
        res = re.sub(r"[()]", "", res)
    return res


def add_form(form: str | None, forms: set[str], word_spaces_count: int) -> None:
    if not form or not (form := form.strip()):
        return

    if form.count(" ") > word_spaces_count:  # `έχουμε ανακατέψει` → `ανακατέψει`
        form = form.rsplit(" ", word_spaces_count + 1)[-1]

    forms.add(cleanup(escape(form)))

    if "(" in form:
        forms.add(cleanup(escape(re.sub(r"\([^)]++\)", "", form))))


def table_to_forms(word: str, wikitext: str) -> list[str]:
    word_spaces_count = word.count(" ")
    forms: set[str] = set()

    if "<br />" in wikitext:
        wikitext = wikitext.replace("<br />", "\n| ")
    if "<br/>" in wikitext:
        wikitext = wikitext.replace("<br/>", "\n| ")

    for table in wtp.parse(wikitext).get_tables():
        data = table.data(span=not True)
        rows_len = len(data[0])
        idx = 1
        match rows_len:
            case 1:  # ανακατεύω
                idx = 0
                while idx < len(data):
                    row = data[idx]
                    if len(row) == 1:
                        idx += 1
                    elif len(row) > 2:
                        for form in row[1:]:
                            add_form(form, forms, word_spaces_count)
                    idx += 1

            case 2:  # ζυγός, αρσενικό
                while idx < len(data):
                    row = data[idx]
                    if len(row) == 3:  # αρσενικό
                        add_form(row[-1], forms, word_spaces_count)
                    elif len(row) == 4:  # όποιος
                        if "&rarr;" in str(row[0]):
                            idx += 1
                            continue
                        for form in row[1:]:
                            add_form(form, forms, word_spaces_count)
                    elif len(row) == 7:  # ζυγός
                        for cidx in (2, 4, 6):
                            add_form(row[cidx], forms, word_spaces_count)
                    idx += 1

            case 3:  # επίπεδο
                while idx < len(data):
                    row = data[idx]
                    if len(row) == 5:
                        for cidx in (2, 4):
                            add_form(row[cidx], forms, word_spaces_count)
                    elif len(row) == 6:
                        for cidx in (2, 3, 5):
                            add_form(row[cidx], forms, word_spaces_count)
                    idx += 1

            case 4:  # βάτος
                while idx < len(data):
                    row = data[idx]
                    if len(row) == 7:
                        for cidx in (2, 4, 6):
                            add_form(row[cidx], forms, word_spaces_count)
                    idx += 1

            case 7:  # κοντραστάρω
                while idx < len(data):
                    row = data[idx]
                    for form in row[1:]:
                        add_form(form, forms, word_spaces_count)
                    idx += 1

            case _:
                msg = f"Unhandled rows length: {rows_len}"
                raise RuntimeError(msg)

    forms.discard(word)
    forms.discard("&mdash;")
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
