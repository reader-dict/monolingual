"""Greek language."""

import re
from collections import defaultdict

from ...user_functions import italic, unique
from .aliases import aliases
from .labels import labels
from .langs import langs

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = "."

# Markers for sections that contain interesting text to analyse.
head_sections = ("{{-el-}}",)
etyl_section = ("{{ετυμολογία}}",)
section_sublevels = (3, 4)
section_patterns = ("#", r"\*")
sections = (
    *head_sections,
    *etyl_section,
    "{{ουσιαστικό}",
    "{{ουσιαστικό|",
    "{{ρήμα}",
    "{{ρήμα|",
    "{{επίθετο}",
    "{{επίθετο|",
    "{{κύριο όνομα}",
    "{{κύριο όνομα|",
    "{{μορφή ουσιαστικού}",
    "{{μορφή ουσιαστικού|",
    "{{μορφή ρήματος}",
    "{{μορφή ρήματος|",
    "{{μορφή επιθέτου}",
    "{{μορφή επιθέτου|",
    "{{επίρρημα}",
    "{{επίρρημα|",
    "{{επίθημα}",
    "{{επίθημα|",
    "{{σύνδεσμος}",
    "{{σύνδεσμος|",
    "{{συντομομορφή}",
    "{{συντομομορφή|",
    "{{αριθμητικό}",
    "{{αριθμητικό|",
    "{{άρθρο}",
    "{{άρθρο|",
    "{{μετοχή}",
    "{{μετοχή|",
    "{{μόριο}",
    "{{μόριο|",
    "{{αντωνυμία}",
    "{{αντωνυμία|",
    "{{επιφώνημα}",
    "{{επιφώνημα|",
    "{{ρηματική έκφραση}",
    "{{ρηματική έκφραση|",
    "{{επιρρηματική έκφραση}",
    "{{επιρρηματική έκφραση|",
    "{{φράση}",
    "{{φράση|",
    "{{έκφραση}",
    "{{έκφραση|",
    "{{παροιμία}",
    "{{παροιμία|",
    "{{πρόθημα}",
    "{{πρόθημα|",
    "{{πολυλεκτικός όρος}",
    "{{πολυλεκτικός όρος|",
)

# Variants
variant_titles = sections
variant_templates = (
    "{{infl",
    "{{θηλ του",
    "{{θηλ_του",
    "{{θηλυκό του",
    "{{θηλυκό_του",
    "{{ουδ του",
    "{{ουδ_του",
    "{{αρσ του",
    "{{αρσ_του",
    "{{κλ|",
    "{{πληθυντικός του|",
    "{{πτώση",
    "{{πτώσηΑεν",
    "{{πτώσηΓπλ",
    "{{πτώσηΑπλ",
    "{{πτώσηΚεν",
    "{{πτώσηΔεν",
    "{{πτώσεις",
    "{{πτώσειςΟΚπλ",
    "{{πτώσειςΟΑΚπλ",
    "{{πτώσειςΓΑΚεν",
    "{{πτώσειςΟΑΚεν",
    "{{πληθ_του",
    "{{απαρ",
    "{{πλ|",
    "{{ρημ τύπος",
    "{{ρημ_τύπος",
)

# Some definitions are not good to keep
definitions_to_ignore = (
    "{{μορφή ουσιαστικού",
    "{{μορφή ρήματος",
    "{{μορφή επιθέτου}",
)

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "!",
    "anchor",
    "ARchar",
    "audio",
    "cat",
    "cf",
    "clear",
    "el-κλίσ",
    "el-κλίσ-'μανάβης'",
    "el-κλίσ-'ναύτης'",
    "el-κλίσ-'ωραίος'",
    "el-κλίση-'ναός'",
    "el-κλίση-'γιατρός'",
    "el-κλίση-'σοφία'",
    "el-κλίση-'παιδί'",
    "el-κλίση-'όμορφος'",
    "el-κλίση-'νίκη'",
    "el-κλίση-'ναύτης'",
    "el-κλίση-'μανάβης'",
    "el-κλίση-'ωραίος'",
    "el-ρήμα",
    "ety+",
    "Q",
    "quote",
    "quotation",
    "R:TELETERM",
    "wlogo",
    "ΒΠ",
    "ΠΘ",
    "παράθεμα",
    "κλείδα-ελλ",
    "επέκταση-ετυ",
    "λείπει η ετυμολογία",
    "περίοδος",
    "από",
    "ετυ+",
    "λείπει ο ορισμός",
    "Βικιπαίδεια",
    "βλ συζ",
    "π-κατ",
    "βλ κατ",
    "κατ",
    "λείπει η κλίση",
    "χρειάζεται παράθεμα",
    "χρειάζεται προσοχή",
    "χρειάζεται τεκμηρίωση",
    "λείπει η μετάφραση",
    "χρειάζεται",
    "πολυτ γραφή",
    "ονομαΓ",
    "παρωχ-ονομαΓ",
    "επώνυμο",
    "ζητ",
    "ήχος",
    "Π",
)

# Templates that will be completed/replaced using italic style.
templates_italic = {
    "θρησκεία": "θρησκεία",
    "κρητ": "κρητικά",
    "λαϊκ": "λαϊκότροπο",
    "προφορ": "προφορικό",
    "ηχομ": "ηχομιμητική λέξη",
    "κυπρ": "κυπριακά",
    "καθ": "καθαρεύουσα",
    "ουσιαστικοπ": "ουσιαστικοποιημένο",
    "ικαρ": "ικαριώτικα",
    "μεταλ": "μεταλλουργία",
    "ορθοπ": "ορθοπαιδική",
    "καππαδ": "καππαδοκικά",
    "κόμπ": "κόμπος",
    "μτβ-αμτβ": "μεταβατικό και αμετάβατο",
    "συνθ βιολ": "συνθετική βιολογία",
    "περιπαιχτ": "περιπαιχτικό",
    "καλιαρντά": "στα καλιαρντά",
}
templates_italic["θρησκ"] = templates_italic["θρησκεία"]
templates_italic["καθ αρχ"] = templates_italic["καθ"]

# Templates more complex to manage.
templates_multi: dict[str, str] = {
    "enWIKT": "f'{parts[-1] if len(parts) > 1 else word} στο αγγλικό Βικιλεξικό'",
    # {{IPAchar|/ˈsɛləteɪp/}}
    "IPAchar": "parts[1]",
    # {{IPAstyle|ˈɑɹ.kən.sɔ}}
    "IPAstyle": "parts[1]",
    # {{resize|Βικιλεξικό|140}}
    "resize": "f'<span style=\"font-size:{parts[2]}%;\">{parts[1]}</span>'",
    # {{uni-script|ΛVΛV}}
    "uni-script": "parts[1]",
    # {{κνε}}
    "κνε": "italic('κοινή νεοελληνική')",
    # {{ιε}}
    "ιε": "italic('πρωτοϊνδοευρωπαϊκή ρίζα')",
    # {{νε}}
    "νε": "italic('νέα ελληνική')",
    # {{αιτ}}
    "αιτ": "italic(strong('αιτιατική'))",
    # {{θηλ ισσα|Αβαριτσιώτης|Αβαριτσιώτ(ης)}}
    "θηλ ισσα": 'f"{parts[-1]} + κατάληξη θηλυκού -ισσα"',
    # {{θηλ τρια|διευθυντής|διευθυντ(ής)}}
    "θηλ τρια": 'f"{parts[-1]} + κατάληξη θηλυκού -τρια"',
    # {{θηλ τρα|ψεύτης|ψεύ(της)}}
    "θηλ τρα": 'f"{parts[-1]} + κατάληξη θηλυκού -τρα"',
    # {{θηλ α|Κερκυραίος|Κερκυραί(ος)}}
    "θηλ α": "f\"{parts[-1] if len(parts) > 1 else ''} + κατάληξη θηλυκού -α\"",
    # {{θηλ ιστρια|εγωιστής|εγω(ιστής)}}
    "θηλ ιστρια": 'f"{parts[-1]} + κατάληξη θηλυκού -ίστρια"',
    # {{θηλ ού|μερακλής|μερακλ(ής)}}
    "θηλ ού": 'f"{parts[-1]} + κατάληξη θηλυκού -ού"',
    # {{θηλ ίνα|μερακλής|μερακλ(ής)}}
    "θηλ ίνα": 'f"{parts[-1]} + κατάληξη θηλυκού -ίνα"',
    # {{θηλ ιδα|προστάτης|προστάτ(ης)}}
    "θηλ ιδα": 'f"{parts[-1]} + κατάληξη θηλυκού -ιδα"',
    # {{υποκοριστικό του|Ann}}
    # {{υποκοριστικό του|Ann|κατ=-άκι}}
    "υποκοριστικό του": 'f"υποκοριστικό του {italic(parts[1])}"',
    # {{ο-πλ}}
    "ο-πλ": "italic('ουδέτερο στον πληθυντικό')",
    # {{οπλ}}
    "οπλ": "italic('ουδέτερο, μόνο στον πληθυντικό')",
    # {{υπερθ|aa|bb}}
    "υπερθ": "f\"{italic('υπερθετικός βαθμός του')} {strong(parts[1])}\"",
    # {{συγκρ|aa|bb}}
    "συγκρ": "f\"{italic('συγκριτικός βαθμός του')} {strong(parts[1])}\"",
    # {{πληθ του|aa|bb}}
    "πληθ του": "f\"{italic('πληθυντικός αριθμός του')} {strong(parts[1])}\"",
    # {{πτώσηΓεν|δρόμος}}
    "πτώσηΓεν": "f\"{italic('γενική ενικού')} του {strong(parts[1])}\"",
    # {{πρώτη γραπτή εμφάνιση|1792}}
    "πρώτη γραπτή εμφάνιση": "term(f'μαρτυρείται από το {parts[1]}')",
    # {{συλλ|Σαβ|βα|το|κύ|ρια|κο}}
    "συλλ": "f'<i>τυπογραφικός συλλαβισμός:</i> {concat(parts[1:], '‐')}'",
    # {{ύφος|λαϊκότροπος|λαϊκότροπο}}
    "ύφος": "parenthesis(parts[1])",
    # {{συντμ του|κατά την ταπεινή μου γνώμη}}
    "συντμ του": "f'σύντμηση του {parts[1]}'",
    # {{θηλ ά|Σμυρνιός|Σμυρνι(ός)}}
    "θηλ ά": "f'{parts[-1]} + κατάληξη θηλυκού -ά'",
    # {{λατιν|Histonium}}
    "λατιν": "f'(<i>λατινική γραφή: {parts[0]}</i>)'",
    # {{vertical-lr|ᠮᠣᠩᠭᠤᠯ}}
    "vertical-lr": "f'<span style=\"writing-mode:vertical-lr\">{parts[-1]}</span>'",
    # {{χρωμ|b80049}}
    "χρωμ": "color(parts[-1])",
    # {{έλλ|πολυπαλλόμενο σύμφωνο}}
    "έλλ": "f'<i>έλλειψη του</i> <b>{parts[1]}</b>'",
}
# Alias
templates_multi["συντμ_του"] = templates_multi["συντμ του"]

# Templates that will be completed/replaced using custom style.
templates_other = {
    "*": "*",
    "θ": "<i>θηλυκό</i>",
    "θο": "<i>θηλυκό ή ουδέτερο</i>",
    "gag": "γκαγκαούζ",
    "odt": "παλαιά ολλανδικά",
    "orv": "αρχαία ανατολική σλαβική γλώσσα",
    "osp": "παλαιά ισπανική",
    "oty": "αρχαία ταμίλ",
    "αθο": "<i>αρσενικό, θηλυκό, ουδέτερο</i>",
    "άκλ": "<i>άκλιτο</i>",
    "απόγονοι": "Απόγονοι",
    "παρωχ-ονομαΑ": "ανδρικό όνομα",
    "απόγονοι2": "ΑΠΟΓΟΝΟΙ:",
    "τοπ": "<b><i>τοπική</i></b>",
    "θηλυκό": "<b><i>θηλυκό</i></b>",
    "θπλ": "<i>θηλυκό, μόνο στον πληθυντικό</i>",
    "μορφ": "<i>άλλες μορφές:</i>",
    "πχ": "⮡",
    "μορφολογικά": "Μορφολογικά αναλύεται σε",
    "πληθυντικός": "<b><i>πληθυντικός</i></b>",
    "γεν": "<b><i>γενική</i></b>",
    "ποιητ": "ποιητικός τύπος",
    "πολυτ γραφή": "<i>πολυτονική γραφή:</i>",
    "ροδέλα": "<i>ροδέλα</i>",
    "βιβ": "⌘",
    "αντων": "≠ <i>αντώνυμα:</i>",
    "βοιωτ": "<i>βοιωτικός τύπος</i>",
    "αεν": "<i>αρσενικό, μόνο στον ενικό</i>",
    "προφορά": "Προφορά",
    "εν": "<i>ενικός</i>",
    "πβ": "<i>πβ.</i>",
    # It would require to support full transliterations, but as this template is used only once in Κνωσός, lets cheat!
    # cf. https://el.wiktionary.org/wiki/Module:Linb-translit/data
    "gmy-tr": "𐀒𐀜𐀰 (ko-no-so)",
}
templates_other["bib"] = templates_other["βιβ"]
templates_other["f"] = templates_other["θ"]
templates_other["ονομαΑ"] = templates_other["παρωχ-ονομαΑ"]
templates_other["πληθ"] = templates_other["πληθυντικός"]
templates_other["πολυ"] = templates_other["πολυτ γραφή"]

_genders = {
    "θ": "θηλυκό",
    "α": "αρσενικό",
    "αθ": "αρσενικό ή θηλυκό",
    "αθο": "αρσενικό, θηλυκό, ουδέτερο",
    "ακλ": "άκλιτο",
    "καθ": "(καθαρεύουσα)",
    "ο": "ουδέτερο",
    "θο": "θηλυκό ή ουδέτερο",
    "αο": "αρσενικό ή ουδέτερο",
    "ακρ": "ακρωνύμιο",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "el")
    []
    >>> find_genders("'''{{PAGENAME}}''' {{αθ}}", "el")
    ['αρσενικό ή θηλυκό']
    >>> find_genders("'''{{PAGENAME}}''' {{αθ}}, {{ακλ|αθ}}", "el")
    ['αρσενικό ή θηλυκό', 'άκλιτο']
    >>> find_genders("'''{{PAGENAME}}''' {{ακλ|αθ}}, {{αθ}}", "el")
    ['άκλιτο', 'αρσενικό ή θηλυκό']
    >>> find_genders("'''{{PAGENAME}}''' {{θο}} {{ακλ}}", "el")
    ['θηλυκό ή ουδέτερο', 'άκλιτο']
    >>> find_genders("'''{{PAGENAME}}''' {{αο}} {{ακλ}} {{ακρ}}", "el")
    ['αρσενικό ή ουδέτερο', 'άκλιτο', 'ακρωνύμιο']
    >>> find_genders("'''{{PAGENAME}}''' {{α}} ({{ετ|ιδιωματικό|0=-}}, Κάλυμνος)", "el")
    ['αρσενικό']
    """
    pattern = re.compile(r"{{([^{}]*)}}")
    line_pattern = "'''{{PAGENAME}}''' "
    return [
        g
        for line in code.splitlines()
        for gender in pattern.findall(line[len(line_pattern) :])
        if line.startswith(line_pattern) and (g := _genders.get(gender.split("|")[0]))
    ]


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "el")
    []
    >>> find_pronunciations("{{ΔΦΑ|tɾeˈlos|γλ=el}}", "el")
    ['/tɾeˈlos/']
    >>> find_pronunciations("{{ΔΦΑ|γλ=el|ˈni.xta}}", "el")
    ['/ˈni.xta/']
    >>> find_pronunciations("{{ΔΦΑ|el|ˈni.ði.mos}}", "el")
    ['/ˈni.ði.mos/']
    >>> find_pronunciations("{{ΔΦΑ|0=-|el|ˈni.ði.mos}}", "el")
    ['/ˈni.ði.mos/']
    """
    res: list[str] = []
    for tpl in re.findall(r"\{\{(ΔΦΑ\|[^\}]+)\}\}", code):
        parts = [part.strip() for part in tpl.split("|")]
        if f"γλ={locale}" not in parts and locale not in parts:
            continue
        if parts := [part for part in parts if "=" not in part and part not in {"ΔΦΑ", locale}]:
            res.append(f"/{parts[-1]}/")
    return unique(res)


def text_language(lang_iso: str, *, args: dict[str, str] = defaultdict(str)) -> str:
    """
    see https://el.wiktionary.org/w/index.php?title=Module:%CE%B5%CF%84%CF%85%CE%BC%CE%BF%CE%BB%CE%BF%CE%B3%CE%AF%CE%B1&oldid=6368956 link_language function
    """
    lang: dict[str, str | bool] = langs[lang_iso]
    lang_name = str(lang["name"])  # neuter plural γαλλικά (or fem.sing. μέση γερμανκή)
    lang_frm = str(lang["frm"])  # feminine accusative singular γαλλική
    text = ""
    if lang_name and lang_frm:
        # feminine article + accusative singular τη γαλλική
        lang_donor_apo = str(lang["apo"])
        # προέλευσης από +apota -- FOR FAMILIES: σημιτικής προέλευσης
        lang_donor_from = str(lang["from"])
        if args["root"] == "1" or args["ρίζα"] == "1":
            text = f"{italic(lang_frm)} <i>ρίζα</i>"
        elif lang["family"]:
            text = italic(lang_donor_from)
        elif args["text"] == "1" or args["κειμ"] == "1":
            text = italic(lang_donor_apo)
        else:
            text = italic(lang_frm)

    return text


def labels_output(text_in: str, *, args: dict[str, str] = defaultdict(str)) -> str:
    """
    from https://el.wiktionary.org/w/index.php?title=Module:labels&oldid=5634715
    """
    mytext = ""

    label = args.get("label") or args.get("topic") or args.get("ετικέτα") or ""
    label = aliases.get(label, label)

    text = text_in or args["1"]
    term = args["όρος"] or args["term"]
    show = args["εμφ"] or args["show"]
    noparenthesis = args["0"]
    if not label or label is None:
        return ""
    nodisplay = args["nodisplay"] or args["000"]

    # Special cases (look for the "special" term in https://el.wiktionary.org/wiki/Module:labels/data)
    special = {"αφετικός", "περικοπή", "συμφυρμός"}

    if not nodisplay:
        if term:
            mytext = term
        elif text:
            mytext = text
        else:
            label_info = labels[label]
            if label_info.get("link") not in {None, "πατρότητα"}:
                mytext = show or f"{italic(label_info['link' if label in special and noparenthesis else 'linkshow'])}"
        mytext = mytext if noparenthesis or label in special else f"({mytext})"
    return mytext


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be call in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["γραπτηεμφ", "1889"], "el")
        '<i>(η λέξη μαρτυρείται από το 1889)</i>'
        >>> last_template_handler(["γραπτηεμφ", "1889", "0=-"], "el")
        'η λέξη μαρτυρείται από το 1889'

        >>> last_template_handler(["λενδ", "el", "fr"], "el")
        'λόγιο ενδογενές δάνειο:'
        >>> last_template_handler(["λενδ", "el", "fr", "0=-"], "el")
        'λόγιο ενδογενές δάνειο'

        >>> last_template_handler(["λδδ", "grc", "el", "νήδυμος"], "el")
        '(διαχρονικό δάνειο) <i>αρχαία ελληνική</i> νήδυμος'
        >>> last_template_handler(["λδδ", "grc-koi", "el"], "el")
        '(διαχρονικό δάνειο) <i>ελληνιστική κοινή</i>'
        >>> last_template_handler(["λδδ", "0=-", "grc-koi", "el", "τεχνικός"], "el")
        '<i>ελληνιστική κοινή</i> τεχνικός'
        >>> last_template_handler(["λδδ", "kath", "el", "αἰτιότης", "αἰτι(ότης)"], "el")
        '(διαχρονικό δάνειο) <i>καθαρεύουσα</i> αἰτι(ότης)'

        >>> last_template_handler(["λ", "ἡδύς", "grc"], "el")
        'ἡδύς'
        >>> last_template_handler(["λ"], "el", word="Ινδία")
        'Ινδία'
        >>> last_template_handler(["λ", "", "grc"], "el", word="Ινδία")
        'Ινδία'
        >>> last_template_handler(["λ", "", "", "κάτι"], "el", word="Ινδία")
        'κάτι'
        >>> last_template_handler(["λ", "κοινωνών", "grc", "t=σύντροφος"], "el")
        'κοινωνών (σύντροφος)'
        >>> last_template_handler(["l", "Иваново", "ru", "lang=4", "tnl=Ιβάνοβο -του Ιβάν-, πόλη της Ρωσίας"], "el")
        '<i>ρωσική</i> Иваново (Ιβάνοβο -του Ιβάν-, πόλη της Ρωσίας)'
        >>> last_template_handler(["l", "acur", "tr=", "lang=4"], "el")
        '<i>νέα ελληνική</i> acur'
        >>> last_template_handler(["l", "inspection", "fr", "d'inspection"], "el")
        "d'inspection"

        >>> last_template_handler(["ετ"], "el")
        ''
        >>> last_template_handler(["ετ", "περικοπή"], "el")
        '<i>περικοπή του</i>'
        >>> last_template_handler(["ετ", "περικοπή", "0=-"], "el")
        '<i>περικοπή</i>'
        >>> last_template_handler(["ετ", "ιατρική"], "el")
        '(<i>ιατρική</i>)'
        >>> last_template_handler(["ετ", "ιατρική", "0=-"], "el")
        '<i>ιατρική</i>'
        >>> last_template_handler(["ετ", "ιατρική", "en"], "el")
        '(<i>ιατρική</i>)'
        >>> last_template_handler(["ετ", "ιατρική", "", "ιατρικών όρων", "0=-"], "el")
        'ιατρικών όρων'

        >>> last_template_handler(["λόγιο"], "el")
        '(<i>λόγιο</i>)'

        >>> last_template_handler(["ουσ"], "el")
        '<i>(ουσιαστικοποιημένο)</i>'

        >>> last_template_handler(["ετυμ", "ine-pro"], "el")
        '<i>πρωτοϊνδοευρωπαϊκή</i>'
        >>> last_template_handler(["ετυμ", "gkm"], "el")
        '<i>μεσαιωνική ελληνική</i>'
        >>> last_template_handler(["ετυμ", "μσν"], "el")
        '<i>μεσαιωνική ελληνική</i>'
        >>> last_template_handler(["ετυμ", "grc", "el", "ἔλαιον"], "el")
        '<i>αρχαία ελληνική</i> ἔλαιον'
        >>> last_template_handler(["ετυμ", "sla"], "el")
        '<i>σλαβικής προέλευσης</i>'
        >>> last_template_handler(["ετυμ", "yua"], "el")
        ''
        >>> last_template_handler(["ετυμ", "ar", "el", "آجُرّ", "tr=ʾājurr"], "el")
        '<i>αραβική</i> آجُرّ (ʾājurr)'
        >>> last_template_handler(["ετυμ", "la", "el", "Civitas Vaticana", "Cīvitās Vāticāna"], "el")
        '<i>λατινική</i> Cīvitās Vāticāna'
        >>> last_template_handler(["der", "sa", "el","बलि-द्वीप", "tr=bali-dvīpa", "tnl=νησιά προσφορών"], "el")
        '<i>σανσκριτική</i> बलि-द्वीप (bali-dvīpa, νησιά προσφορών)'

        >>> last_template_handler(["πρόσφ", "μαλλί", "-ης"], "el")
        'μαλλί + -ης'
        >>> last_template_handler(["πρόσφ", "μαλλί", ".1=μαλλ(ί)", "-ης"], "el")
        'μαλλ(ί) + -ης'

        >>> last_template_handler(["αρχ"], "el")
        '<i>αρχαία ελληνική</i>'
        >>> last_template_handler(["αρχ", "ὅπου"], "el")
        '<i>αρχαία ελληνική</i> ὅπου'

        >>> last_template_handler(["μσν"], "el")
        '<i>μεσαιωνική ελληνική</i>'
        >>> last_template_handler(["μσν", "ὅπου"], "el")
        '<i>μεσαιωνική ελληνική</i> ὅπου'

        >>> last_template_handler(["fr"], "el")
        'γαλλικά'

        >>> last_template_handler(["γραφή του", "άσος"], "el")
        '<i>άλλη γραφή του</i> <b>άσος</b>'
        >>> last_template_handler(["γραφή του", "αγάρ", "μορφ"], "el")
        '<i>άλλη μορφή του</i> <b>αγάρ</b>'

        >>> last_template_handler(["ετικ", "γαστρονομία", "τρόφιμα", "γλυκά"], "el")
        '(<i>γαστρονομία</i>, <i>τρόφιμο</i>, <i>γλυκό</i>)'
        >>> last_template_handler(["ετικ", "βιολ", "ιατρ"], "el")
        '(<i>βιολογία</i>, <i>ιατρική</i>)'

        >>> last_template_handler(["desc", "el", "πάρτι", "δαν"], "el")
        '↷ <i>νέα ελληνικά:</i> πάρτι'
        >>> last_template_handler(["απόγ", "el", "πάρτι", "δαν"], "el")
        '↷ <i>νέα ελληνικά:</i> πάρτι'
        >>> last_template_handler(["απόγ", "σύμβολο=δαν"], "el")
        '↷'

        >>> last_template_handler(["μονο"], "el")
        '<i>μονοτονική γραφή</i>:'
        >>> last_template_handler(["μονο", "ἀπολωλώς"], "el")
        '<i>μονοτονική γραφή της λέξης</i> <b>ἀπολωλώς</b>'

        >>> last_template_handler(["μεγεθ"], "el")
        '<i>(μεγεθυντικό)</i>'
        >>> last_template_handler(["μεγεθ", "φωνή"], "el")
        '<i>μεγεθυντικό του</i> <b>φωνή</b>'

        >>> last_template_handler(["βλ αρχαία κλίση"], "el")
        '(<i>κλιτικοί τύποι από την αρχαία κλίση</i>)'
        >>> last_template_handler(["βλ αρχαία κλίση", "ἄρχων"], "el")
        '(<i>κλιτικοί τύποι από την αρχαία κλίση στο</i> ἄρχων)'
        >>> last_template_handler(["βλ αρχαία κλίση", "ἄρχων", "0=-"], "el")
        '<i>κλιτικοί τύποι από την αρχαία κλίση στο</i> ἄρχων'

        >>> last_template_handler(["ιων"], "el")
        '<i>ιωνικός τύπος</i>'
        >>> last_template_handler(["ιων", "foo"], "el")
        '<i>ιωνικός τύπος του</i> <b>foo</b>'
        >>> last_template_handler(["ιων", "-"], "el")
        '<i>ιωνικός</i>'

        >>> last_template_handler(["αιτ του", "abako", "eo"], "el")
        '<i>αιτιατική</i> του <b>abako</b>'
    """
    from ...user_functions import concat, extract_keywords_from, italic, strong, term
    from .. import defaults
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        return render_template(word, template)

    data = extract_keywords_from(parts)

    if tpl in {
        "l2",
        "nobr",
        "s",
        "Wikispecies",
        "Wspecies",
        "wsp",
        "β",
        "βθ",
        "λ2",
        "φόντο",
    }:
        return parts[-1]

    if tpl == "ΒΦ":
        return f"{parts[-1]} στα Βικιφθέγματα"

    if tpl == "γραφή του":
        if len(parts) == 1:
            parts.append("γραφ")
        return f"{italic(f'άλλη {parts[1]}ή του')} {strong(parts[0])}"

    if tpl in {"λδδ", "dlbor"}:
        phrase = "" if data["0"] else "(διαχρονικό δάνειο) "
        phrase += text_language(parts[0], args=data)
        if rest_ := data["1"] or parts[-1] if len(parts) > 2 else "":
            phrase += f" {rest_}"
        return phrase

    if tpl in {"λ", "l", "link"}:
        text = ""
        if data["lang"]:
            text += f"{text_language(parts[1]) if len(parts) > 1 else italic('νέα ελληνική')} "

        empty_parts = len([p for p in parts if not p])
        if empty_parts == 1:
            text += word
        elif empty_parts >= 2:
            text += parts[2]
        elif parts:
            text += parts[0] if parts[-1] in langs else parts[-1]
        else:
            text += word

        if tnl := data["tnl"] or data["t"]:
            text += f" ({tnl})"
        return text

    if tpl in {"απόγ", "desc"}:
        text = "↷"
        if data["σύμβολο"] == "δαν":
            return text
        text += f" {italic(str(langs[parts[0]]['name']) + ':')} {parts[1]}"
        return text

    if tpl in {"ετ", "ετικέτα"}:
        if not parts:
            return ""
        if len(parts) <= 2:
            data["label"] = parts[0]
        else:
            data["label"] = parts[2]
            data["text"] = parts[2]
        return labels_output(data["text"], args=data)

    if tpl == "ετικ":
        return f"({', '.join(italic(labels[aliases.get(part, part)]['linkshow']) for part in parts if part)})"

    if tpl in {"ετυμ", "der"}:
        text = text_language(parts[0])
        if len(parts) > 2:
            text += f" {parts[-1]}"
        more: list[str] = []
        if tr := data["tr"]:
            more.append(tr)
        if tnl := data["tnl"]:
            more.append(tnl)
        if more:
            text += f" ({', '.join(more)})"
        return text

    if tpl == "λόγιο":
        data["label"] = tpl
        return labels_output("", args=data)

    if tpl == "μονο":
        if not parts:
            return f"{italic('μονοτονική γραφή')}:"
        return f"{italic('μονοτονική γραφή της λέξης')} {strong(parts[0])}"

    if tpl == "μεγεθ":
        if not parts:
            return term("μεγεθυντικό")
        return f"{italic('μεγεθυντικό του')} {strong(parts[0])}"

    if text := {
        "σνρ": "συνηρημένη μορφή",
    }.get(tpl, ""):
        if not parts:
            return italic(text)
        return f"{italic(f'{text} του')} {parts[0]}"

    if tpl == "βλ αρχαία κλίση":
        text = "κλιτικοί τύποι από την αρχαία κλίση"
        if parts:
            text = italic(f"{text} στο")
            text += f" {parts[0]}"
        else:
            text = italic(text)
        return text if data["0"] else f"({text})"

    if text := {
        "ιων": "ιωνικός τύπος",
        "αιολ": "αιολικός τύπος",
        "λοκ": "λοκρικός τύπος",
        "αττ": "αττικός τύπος",
        "δωρ": "δωρικός τύπος",
        "κρητ αρχ": "κρητικός τύπος",
        "μακεδ": "μακεδονικός τύπος",
    }.get(tpl, ""):
        if not parts:
            return italic(text)
        if (part := parts[0]) == "-":
            return italic(text.removesuffix(" τύπος"))
        return f"{italic(f'{text} του')} {strong(part)}"

    if text := {
        "λενδ": "λόγιο ενδογενές δάνειο",
        "βλφρ": "δείτε την έκφραση",
    }.get(tpl, ""):
        if not data["0"]:
            text += ":"
        return text

    if text := {
        "αιτ του": "αιτιατική",
        "αιτ_του": "αιτιατική",
        "αιτιατική του": "αιτιατική",
        "ουδέτερο του": "ουδέτερο",
    }.get(tpl, ""):
        return f"{italic(text)} του {strong(parts[0])}"

    if text := {
        "αρχ": "αρχαία ελληνική",
        "μσν": "μεσαιωνική ελληνική",
    }.get(tpl, ""):
        phrase = italic(text)
        if parts:
            phrase += f" {parts[0]}"
        return phrase

    if text := {
        "μτχεε": "μετοχή ενεργητικού ενεστώτα",
        "μτχα": "μετοχή παθητικού αορίστου",
        "μτχπα": "μετοχή παθητικού αορίστου",
        "μτχε": "μετοχή παθητικού ενεστώτα",
        "μτχπε": "μετοχή παθητικού ενεστώτα",
        "μτχεα": "μετοχή ενεργητικού αορίστου",
        "μτχεμ": "μετοχή ενεργητικού μέλλοντα",
        "μτχεπ": "μετοχή ενεργητικού παρακειμένου",
        "μτχμα": "μετοχή μέσου αορίστου",
        "μτχπ": "μετοχή παρακειμένου",
        "μτχπμ": "μετοχή παθητικού μέλλοντα",
        "μτχπp": "μετοχή παθητικού παρακειμένου",
        "μτχππ": "μετοχή παθητικού παρακειμένου",
        "μτχππαναδ": "μετοχή παθητικού παρακειμένου",
        "μτχχρ": "μετοχή παθητικού παρακειμένου",
        "γερουνδιακ": "γερουνδιακό",
    }.get(tpl, ""):
        phrase = italic(text)
        if parts:
            phrase += f" του ρήματος {strong(parts[0])}"
        return phrase

    if text := {
        "γραπτηεμφ": f"η λέξη μαρτυρείται από το {parts[0] if parts else ''}",
        "μτφρ": "μεταφορικά",
        "κτεπε": "κατ’ επέκταση",
        "μτβ": "μεταβατικό",
        "αμτβ": "αμετάβατο",
        "ουσ": "ουσιαστικοποιημένο",
        "νεολ": "νεολογισμός",
        "μπφ": "μέση-παθητική φωνή του ρήματος",
        "μτβ+αμτβ": "μεταβατικό και αμετάβατο",
        "μτγν": "ελληνιστική",
        "μτγρ": "μεταγραφή",
        "μυθολ": "μυθολογία",
        "παρετυμολογία": "παρετυμολογία",
        "συνηθ": "πιο συνηθισμένο",
        "σπαν": "σπάνιο",
        "σπάν": "σπάνιο",
        "καταχρ": "καταχρηστικά",
        "σνκδ": "συνεκδοχικά",
        "μειωτ": "μειωτικό",
        "ορθοδ": "ορθοδοξία",
        "θρησκεία": "θρησκεία",
        "χυδαίο": "χυδαίο",
        "λαϊκότροπο": "λαϊκότροπο",
        "οεν": "ουδέτερο",
        "οικ": "οικείο",
        "απρόσωπο": "απρόσωπο",
        "αργκ": "αργκό",
        "αργκό": "αργκό",
        "παρωχ": "παρωχημένο",
        "ειδικ": "ειδικότερα",
        "ειδικότερα": "ειδικότερα",
        "ειρων": "ειρωνικό",
        "ειρωνικά": "ειρωνικό",
        "ειρωνικό": "ειρωνικό",
        "κυριολ": "κυριολεκτικά",
        "κυριολ+μτφρ": "κυριολεκτικά και μεταφορικά",
        "κυριολ+μτφ": "κυριολεκτικά και μεταφορικά",
        "ετυμ en": "αγγλική",
        "ετυμ fr": "γαλλική",
        "ετυμ_en": "αγγλική",
        "ετυμ_fr": "γαλλική",
        "κυριολεκτικά": "κυριολεκτικά",
        "καθ κοινή": "καθαρεύουσα",
        "καθ μεσ": "καθαρεύουσα",
        "καθαρεύουσα": "καθαρεύουσα",
        "κατ' επέκταση": "κατ' επέκταση",
        "γενικότερα": "γενικότερα",
        "αρχαιοπρεπές": "αρχαιοπρεπές",
        "δημοτική": "δημοτική",
        "δοτική": "δοτική",
        "επτανησιακά": "επτανησιακά",
        "καταχρηστικά": "καταχρηστικά",
        "κεφαλονίτικα": "κεφαλονίτικα",
        "ετυμολογία": "ετυμολογία",
        "σπάνιο": "σπάνιο",
        "συγγενή": "συγγενή",
        "σημειώσεις συντακτών": "σημειώσεις συντακτών",
        "σημειώσεις": "σημειώσεις",
        "σημείωση": "σημείωση",
        "προσφώνηση": "προσφώνηση",
        "προσχέδιο": "προσχέδιο",
        "προφορικό": "προφορικό",
        "μεταβατικό": "μεταβατικό",
        "μεταφορικά": "μεταφορικά",
        "νεολογισμός": "νεολογισμός",
        "οικείο": "οικείο",
        "όνομα": "όνομα",
        "παιδιά": "παιδιά",
        "παράθεμα": "παράθεμα",
        "παρωχημένο": "παρωχημένο",
        "αρχαιοπρ": "αρχαιοπρεπές",
        "συνεκδοχικά": "συνεκδοχικά",
        "ταυτόσημα": "ταυτόσημα",
        "δημοτ": "δημοτική",
        "χυδ": "χυδαίο",
        "US": "ΗΠΑ",
        "ΗΠΑ": "ΗΠΑ",
        "UK": "ΗΒ",
        "USA": "ΗΠΑ",
        "λογοτ": "λογοτεχνικό",
        "ανθρωπολ": "ανθρωπολογία",
        "αντιδάνειο": "αντιδάνειο",
        "Γαλλία": "Γαλλία",
    }.get(tpl, ""):
        return text if data["0"] else term(text)

    if text := {
        "αθ": "αρσενικό ή θηλυκό",
        "ταυτ": "ταυτόσημα",
        "αναδρομικός": "αναδρομικός σχηματισμός",
        "λατ": "λατινικά",
        "υστερο la": "υστερολατινική",
        "δημ la": "δημώδης λατινική",
        "συνων": "συνώνυμα",
        "συνών": "συνώνυμα",
        "ακλ": "άκλιτο",
        "ακρ": "ακρωνύμιο",
        "α": "αρσενικό",
        "ο": "ουδέτερο",
        "αρκτ": "αρκτικόλεξο",
        "συντ": "συντομογραφία",
    }.get(tpl, ""):
        return text if data["0"] else italic(text)

    if text := {
        "καθαρ": "καθαρεύουσα",
        "γενικ": "γενικότερα",
        "μετων": "μετωνυμία",
    }.get(tpl, ""):
        return italic(text) if data["0"] else term(text)

    if tpl in {"πρόσφ", "προσφ"}:
        words = [data[f".{idx}"] or part for idx, part in enumerate(parts, 1)]
        return concat(words, " + ")

    # This is a country in the current locale
    if lang := langs.get(tpl):
        return str(lang["name"])

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://el.wiktionary.org/wiki/%CE%95%CE%B9%CE%B4%CE%B9%CE%BA%CF%8C:RandomRootpage"
