"""Greek language."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://el.wiktionary.org/wiki/%CE%95%CE%B9%CE%B4%CE%B9%CE%BA%CF%8C:RandomRootpage"

template_trans = "Πρότυπο"

float_separator = ","
thousands_separator = "."

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
    "{{μτχα}",
    "{{μτχα|",
)

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
    "{{πτώσηΓεν",
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

definitions_to_ignore = (
    "{{μορφή ουσιαστικού",
    "{{μορφή ρήματος",
    "{{μορφή επιθέτου}",
)

templates_ignored = (
    "{{audio",
    "{{cf",
    "{{el-κλίσ",
    "{{el-ρήμα",
    "{{Q",
    "{{quot",
    "{{R:",
    "{{wlogo",
    "{{λείπει ",  # missing etymology/definition
    "{{Βικιπαίδεια",  # Wikipedia
    "{{βλ ",  # see talk/category
    "{{χρειάζεται",  # reference/attention/doc/etc required
    "{{ονομαΓ",  # name
    "{{παρωχ-ονομαΓ",  # first name
    "{{επώνυμο",  # last name
    "{{ζητ",  # request
    "{{ήχος",  # audio
)


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
    return utils.unique(res)
