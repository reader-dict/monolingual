"""Greek language."""

import re

from ... import lang, utils
from ...lang.pl import extract_templates
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __file__.rsplit("/", 2)[-2]

random_word_url = "https://el.wiktionary.org/wiki/%CE%95%CE%B9%CE%B4%CE%B9%CE%BA%CF%8C:RandomRootpage"

template_trans = "Πρότυπο"

head_sections = ("{{-el-}}",)
etyl_section = ("{{ετυμολογία}}",)
section_sublevels = (3, 4)
section_patterns = ("#", r"\*")
sublist_patterns = ("#", ":")
sections = (
    *head_sections,
    *etyl_section,
    "{{κλίση|",  # inclination
    "{{κλίση}",  # inclination
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

reverse_variant_titles = ("{{el-κλίσ",)
reverse_variant_templates = ("{{rev-flexion",)

definitions_to_ignore = (
    "{{μορφή ουσιαστικού",
    "{{μορφή ρήματος",
    "{{μορφή επιθέτου}",
)

templates_ignored = (
    "{{audio",
    "{{cf",
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
    "θ": "θ",
    "α": "α",
    "αθ": "αθ",
    "αθο": "αθο",
    "ακλ": "ακλ",
    "καθ": "καθ",
    "ο": "ο",
    "θο": "θο",
    "αο": "αο",
    "ακρ": "ακρ",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "el")
    []
    >>> find_genders("'''{{PAGENAME}}''' {{αθ}}", "el")
    ['αθ']
    >>> find_genders("'''{{PAGENAME}}''' {{αθ}}, {{ακλ|αθ}}", "el")
    ['αθ', 'ακλ']
    >>> find_genders("'''{{PAGENAME}}''' {{ακλ|αθ}}, {{αθ}}", "el")
    ['ακλ', 'αθ']
    >>> find_genders("'''{{PAGENAME}}''' {{θο}} {{ακλ}}", "el")
    ['θο', 'ακλ']
    >>> find_genders("'''{{PAGENAME}}''' {{αο}} {{ακλ}} {{ακρ}}", "el")
    ['αο', 'ακλ', 'ακρ']
    >>> find_genders("'''{{PAGENAME}}''' {{α}} ({{ετ|ιδιωματικό|0=-}}, Κάλυμνος)", "el")
    ['α']
    """
    pattern = re.compile(r"\{\{([^{}]*+)\}\}")
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
    for tpl in re.findall(r"\{\{(ΔΦΑ\|[^\}]++)\}\}", code):
        parts = [part.strip() for part in tpl.split("|")]
        if f"γλ={locale}" not in parts and locale not in parts:
            continue
        if parts := [part for part in parts if "=" not in part and part not in {"ΔΦΑ", locale}]:
            res.append(f"/{parts[-1]}/")
    return res


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> from ... import context
    >>> _ = context.reset(LANG)

    >>> context.new_word("όποιος")
    >>> adjust_wikicode("{{el-κλίσ-'ποιος'‎|όποι|γεα=οποιανού|γεθ=οποιανής|γεο=οποιανού|γπα=οποιανών|γπθ=οποιανών|γπο=οποιανών|απα=οποιανούς}}", LANG, word="όποιος")
    '===={{κλίση}====\n# {{rev-flexion|οποιανής}}\n# {{rev-flexion|οποιανού}}\n# {{rev-flexion|οποιανούς}}\n# {{rev-flexion|οποιανών}}\n# {{rev-flexion|όποια}}\n# {{rev-flexion|όποιες}}\n# {{rev-flexion|όποιο}}\n# {{rev-flexion|όποιοι}}\n# {{rev-flexion|όποιον}}'

    >>> context.new_word("μουράγιο")
    >>> adjust_wikicode("{{el-κλίση-'πεύκο'|κατ=πεύκο|όπως=ουδέτερα#πεύκο{{!}}πεύκο}}", LANG, word="μουράγιο")
    '===={{κλίση}====\n# {{rev-flexion|μουράγια}}\n# {{rev-flexion|μουράγιου}}\n# {{rev-flexion|μουράγιων}}'

    >>> context.new_word("αναμένω")
    >>> adjust_wikicode("{{el-κλίσ-'δροσίζω'|αναμέν|ανέμεν|αναμείν|ανέμειν|πρ1=ανάμενε|πρ3=ανάμεινε|πρ4=αναμείνετε<br>(αναμείνατε)}}", LANG, word="αναμένω")
    '===={{κλίση}====\n# {{rev-flexion|ανάμεινε}}\n# {{rev-flexion|ανάμενε}}\n# {{rev-flexion|ανέμεινα}}\n# {{rev-flexion|ανέμειναν}}\n# {{rev-flexion|ανέμεινε}}\n# {{rev-flexion|ανέμεινες}}\n# {{rev-flexion|ανέμενα}}\n# {{rev-flexion|ανέμεναν}}\n# {{rev-flexion|ανέμενε}}\n# {{rev-flexion|ανέμενες}}\n# {{rev-flexion|αναμέναμε}}\n# {{rev-flexion|αναμέναν}}\n# {{rev-flexion|αναμένανε}}\n# {{rev-flexion|αναμένατε}}\n# {{rev-flexion|αναμένει}}\n# {{rev-flexion|αναμένεις}}\n# {{rev-flexion|αναμένετε}}\n# {{rev-flexion|αναμένοντας}}\n# {{rev-flexion|αναμένουμε}}\n# {{rev-flexion|αναμένουν}}\n# {{rev-flexion|αναμένουνε}}\n# {{rev-flexion|αναμείναμε}}\n# {{rev-flexion|αναμείναν}}\n# {{rev-flexion|αναμείνανε}}\n# {{rev-flexion|αναμείνατε}}\n# {{rev-flexion|αναμείνει}}\n# {{rev-flexion|αναμείνεις}}\n# {{rev-flexion|αναμείνετε}}\n# {{rev-flexion|αναμείνουμε}}\n# {{rev-flexion|αναμείνουν}}\n# {{rev-flexion|αναμείνουνε}}\n# {{rev-flexion|αναμείνω}}'

    >>> context.new_word("ζυγός")
    >>> adjust_wikicode("{{el-κλίση-'καλός'}}", LANG, word="ζυγός")
    '===={{κλίση}====\n# {{rev-flexion|ζυγά}}\n# {{rev-flexion|ζυγέ}}\n# {{rev-flexion|ζυγές}}\n# {{rev-flexion|ζυγή}}\n# {{rev-flexion|ζυγής}}\n# {{rev-flexion|ζυγοί}}\n# {{rev-flexion|ζυγού}}\n# {{rev-flexion|ζυγούς}}\n# {{rev-flexion|ζυγό}}\n# {{rev-flexion|ζυγών}}'

    >>> context.new_word("ανακατεύω")
    >>> adjust_wikicode("{{el-κλίσ-'παντρεύω'|παρακΒ=1}}", LANG, word="ανακατεύω")
    '===={{κλίση}====\n# {{rev-flexion|ανακάτευα}}\n# {{rev-flexion|ανακάτευαν}}\n# {{rev-flexion|ανακάτευε}}\n# {{rev-flexion|ανακάτευες}}\n# {{rev-flexion|ανακάτεψα}}\n# {{rev-flexion|ανακάτεψαν}}\n# {{rev-flexion|ανακάτεψε}}\n# {{rev-flexion|ανακάτεψες}}\n# {{rev-flexion|ανακατέψαμε}}\n# {{rev-flexion|ανακατέψαν}}\n# {{rev-flexion|ανακατέψανε}}\n# {{rev-flexion|ανακατέψατε}}\n# {{rev-flexion|ανακατέψει}}\n# {{rev-flexion|ανακατέψεις}}\n# {{rev-flexion|ανακατέψετε}}\n# {{rev-flexion|ανακατέψουμε}}\n# {{rev-flexion|ανακατέψουν}}\n# {{rev-flexion|ανακατέψουνε}}\n# {{rev-flexion|ανακατέψτε}}\n# {{rev-flexion|ανακατέψω}}\n# {{rev-flexion|ανακατεμένο}}\n# {{rev-flexion|ανακατεύαμε}}\n# {{rev-flexion|ανακατεύαν}}\n# {{rev-flexion|ανακατεύανε}}\n# {{rev-flexion|ανακατεύατε}}\n# {{rev-flexion|ανακατεύει}}\n# {{rev-flexion|ανακατεύεις}}\n# {{rev-flexion|ανακατεύετε}}\n# {{rev-flexion|ανακατεύοντας}}\n# {{rev-flexion|ανακατεύουμε}}\n# {{rev-flexion|ανακατεύουν}}\n# {{rev-flexion|ανακατεύουνε}}'

    >>> context.new_word("αρσενικό")
    >>> adjust_wikicode("{{el-κλίση-'βουνό'|α2=εν}}", LANG, word="αρσενικό")
    '===={{κλίση}====\n# {{rev-flexion|αρσενικού}}'

    >>> context.new_word("βάτος")
    >>> adjust_wikicode("{{el-κλίση-'ναύλος'|υποκατ=αρσενικά}}", LANG, word="βάτος")
    '===={{κλίση}====\n# {{rev-flexion|βάτα}}\n# {{rev-flexion|βάτε}}\n# {{rev-flexion|βάτο}}\n# {{rev-flexion|βάτοι}}\n# {{rev-flexion|βάτου}}\n# {{rev-flexion|βάτους}}\n# {{rev-flexion|βάτων}}'

    >>> context.new_word("κοντραστάρω")
    >>> adjust_wikicode("{{el-κλίσ-'ξέρω'|2=κοντράσταρ}}", LANG, word="κοντραστάρω")
    '===={{κλίση}====\n# {{rev-flexion|κοντράσταρα}}\n# {{rev-flexion|κοντράσταραν}}\n# {{rev-flexion|κοντράσταρε}}\n# {{rev-flexion|κοντράσταρες}}\n# {{rev-flexion|κοντραστάραμε}}\n# {{rev-flexion|κοντραστάραν}}\n# {{rev-flexion|κοντραστάρανε}}\n# {{rev-flexion|κοντραστάρατε}}\n# {{rev-flexion|κοντραστάρε}}\n# {{rev-flexion|κοντραστάρει}}\n# {{rev-flexion|κοντραστάρεις}}\n# {{rev-flexion|κοντραστάρετε}}\n# {{rev-flexion|κοντραστάροντας}}\n# {{rev-flexion|κοντραστάρουμε}}\n# {{rev-flexion|κοντραστάρουν}}\n# {{rev-flexion|κοντραστάρουνε}}'

    >>> context.new_word("φακός επαφής")
    >>> adjust_wikicode("{{el-κλίση-όρος|αρσ=1|τύπος=ναός|κοινό=[[επαφή|{{χθ|επαφής}}]]|[[φακός|{{χθ|φακός}}]]|φακού|αεΛ=φακό|κεΛ=φακέ|φακοί|φακών|απΛ=φακούς}}", LANG, word="φακός επαφής")
    '===={{κλίση}====\n# {{rev-flexion|φακέ επαφής}}\n# {{rev-flexion|φακοί επαφής}}\n# {{rev-flexion|φακού επαφής}}\n# {{rev-flexion|φακούς επαφής}}\n# {{rev-flexion|φακό επαφής}}\n# {{rev-flexion|φακών επαφής}}'
    """

    if f"{{{locale}-κλίσ" in code:
        code = code.replace(f"{{{{{locale}-κλίσ", f"===={{{{κλίση}}====\n{{{{{locale}-κλίσ")

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        lines: list[str] = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    for tpl_sub in extract_templates(tpl_code):
                        tpl_name = tpl_sub[2 : max(0, tpl_sub.find("|")) or tpl_sub.find("}")].strip(" \u200e")
                        variant_handlers_mod.append_to_reverse_variants(tpl_name)
                        forms = utils.process_templates(
                            word,
                            tpl_sub,
                            locale,
                            templates_status=templates_status,
                            variant_only=True,
                        )
                        lines.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                lines.append(line)
        code = "\n".join(lines)

    return code
