"""Romanian language."""

import re
from functools import lru_cache

from ... import lang, utils
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://ro.wiktionary.org/wiki/Special:RandomRootpage"

module_trans = "Modul"
template_trans = "Format"

section_patterns = ("#", r"\*")
section_sublevels = (3,)
head_sections = ("{{limba|ron}}", "{{limba|ro}}", "{{limba|conv}}")
etyl_section = ("{{etimologie}}",)
core_sections = (
    "abr",
    "abreviere",
    "adjectiv",
    "adjective",
    "adverb",
    "articol",
    "comp",
    "conjuncție",
    "cuvânt compus",
    "expr",
    "expresie",
    "interjecție",
    "locuțiune adjectivală",
    "locuțiune adverbială",
    "locuțiune",
    "numeral colectiv",
    "numeral",
    "nume propriu",
    "nume taxonomic",
    "participiu",
    "prefix",
    "prepoziție",
    "pronume",
    "sin",
    "substantiv",
    "sufix",
    "simbol",
    "unități",
    "verb auxiliar",
    "verb copulativ",
    "verb predicativ",
    "verb tranzitiv",
    "verb",
)
sections = (
    *etyl_section,
    *[f"{{{{{section}}}" for section in core_sections],
    *[f"{{{{{section}|" for section in core_sections],
)

variant_templates = (
    "{{adj form of",
    "{{flexion",
)

reverse_variant_titles = (
    "{{adjectiv-",
    "{{substantiv-",
    "{{verb-",
)
reverse_variant_templates = ("{{rev-flexion",)

RE_GENDERS = re.compile(r"gen=\{\{([fmsingp]++)(?: \?\|)*\}")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", LANG)
    []
    >>> find_genders("{{substantiv-ron|gen={{m}}|nom-sg=câine|nom-pl=câini", LANG)
    ['m']
    >>> find_genders("{{substantiv-ron|gen={{n}}}}", LANG)
    ['n']
    """
    return utils.unique(utils.flatten(RE_GENDERS.findall(code)))


@lru_cache
def cache_patterns(locale: str) -> list[re.Pattern[str]]:
    return [
        re.compile(r"\{AFI\|(/[^/\n]++\/)(?:\|(/[^/\n]++\/))*+"),
        re.compile(rf"\{{IPA\|{locale}\|([^}}\n]++)"),
    ]


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", LANG)
    []
    >>> find_pronunciations("{{AFI|/ka.priˈmulg/}}", LANG)
    ['/ka.priˈmulg/']
    >>> find_pronunciations("{{IPA|ro|[fruˈmoʃʲ]}}", LANG)
    ['[fruˈmoʃʲ]']
    """
    res = []
    for pattern in cache_patterns(locale):
        res.extend(pattern.findall(code))

    return utils.flatten(res)


REV_VARIANTS_IGNORED = {"-", "I", "II", "III", "IV", "V", "VI"}
RE_CLEANUPS = [
    # `{{-avv-|ANY|ANY}}` → === `{{avv|ANY|ANY}} ===`
    (re.compile(r"(?m)^\{\{-([^-\n]++)-\|(\w++)\|(\w++)\}\}"), r"=== {{\1|\2|\3}} ==="),
    # `====Verb tranzitiv====` → `=== {{Verb tranzitiv}} ===`
    (re.compile(r"(?m)====([^=\n]++)===="), r"=== {{\1}} ==="),
    # `{{-avv-|ANY}}` → `=== {{avv|ANY}} ===`
    (re.compile(r"(?m)^\{\{-([^-\n]++)-\|(\w++)\}\}"), r"=== {{\1|\2}} ==="),
    # `{{-avv-}}` → `=== {{avv}} ===`
    # `{{-nume propriu-}}` → `=== {{nume propriu}} ===`
    (re.compile(r"(?m)^\{\{-([\w \n]++)-\}\}"), r"=== {{\1}} ==="),
]
RE_VARIANTS = re.compile(r"(?m)^#\s*+'++(?:forma de|formă) [^']++'++\s*+'*+\[\[([^\]]+)\]\]'*+\.?")
RE_REV_VARIANTS = re.compile(r"=([^|{}\n]++)")
RE_SPLIT_BR = re.compile(r"<br\s*+/?+>")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("=={{limba|ron}}==\n{{(|adept al liberalismului}}\n*{{eng}}: {{trad|en|liberal}}\n{{-}}\n{{)}}\nfoo\n{{bar}}#foo\n{{(|baz}}\n*sdf\n{{)}}", LANG)
    '=={{limba|ron}}==\nfoo\n{{bar}}#foo'

    >>> adjust_wikicode("=={{limba|ron}}==\n{{-avv-|ANY|ANY}}", LANG)
    '=={{limba|ron}}==\n=== {{avv|ANY|ANY}} ==='

    >>> adjust_wikicode("=={{limba|ron}}==\n{{-avv-|ANY}}", LANG)
    '=={{limba|ron}}==\n=== {{avv|ANY}} ==='

    >>> adjust_wikicode("=={{limba|ron}}==\n{{-avv-}}", LANG)
    '=={{limba|ron}}==\n=== {{avv}} ==='

    >>> adjust_wikicode("=={{limba|ron}}==\n{{-nume propriu-}}", LANG)
    '=={{limba|ron}}==\n=== {{nume propriu}} ==='

    >>> adjust_wikicode("=={{limba|ron}}==\n#''forma de feminin singular pentru'' [[frumos]].", LANG)
    '=={{limba|ron}}==\n# {{flexion|frumos}}'
    >>> adjust_wikicode("=={{limba|ron}}==\n#''formă alternativă pentru'' [[fântânioară]].", LANG)
    '=={{limba|ron}}==\n# {{flexion|fântânioară}}'

    >>> adjust_wikicode("=={{limba|ron}}==\n{{substantiv-ron\n|gen={{f}}\n|nom-sg=piatră\n|nom-pl=pietre\n|art-sg=piatra\n|art-pl=pietrele\n|dat-sg=pietrei\n|dat-pl=pietrelor\n|voc-sg=piatră\n|voc-pl=pietrelor\n}}", LANG)
    '=={{limba|ron}}==\n# {{rev-flexion|piatra}}\n# {{rev-flexion|piatră}}\n# {{rev-flexion|pietre}}\n# {{rev-flexion|pietrei}}\n# {{rev-flexion|pietrele}}\n# {{rev-flexion|pietrelor}}'
    >>> adjust_wikicode("=={{limba|ron}}==\n{{adjectiv-ron\n|m-sg=interocular\n|m-pl=[[interoculari]]\n|f-sg=[[interoculară]]\n|f-pl=interoculare/roof (2)\n|voc-pl=\n|voc-sg=electronică<br />electronico\n}}", LANG)
    '=={{limba|ron}}==\n# {{rev-flexion|electronico}}\n# {{rev-flexion|electronică}}\n# {{rev-flexion|interocular}}\n# {{rev-flexion|interoculare}}\n# {{rev-flexion|interoculari}}\n# {{rev-flexion|interoculară}}\n# {{rev-flexion|roof}}'
    >>> adjust_wikicode("=={{limba|ron}}==\n{{adjectiv-ron|m-sg=interocular|m-pl=[[interoculari]]|f-sg=[[interoculară]]|f-pl=[[interoculare]]|voc-pl={{inv}}|voc-sg=}}# părul", LANG)
    '=={{limba|ron}}==\n# {{rev-flexion|interocular}}\n# {{rev-flexion|interoculare}}\n# {{rev-flexion|interoculari}}\n# {{rev-flexion|interoculară}}\n# părul'
    """
    # Wipe out `{{(|...}}...{{)}}`
    if "{{(|" in code:
        cleaned: list[str] = []
        in_unwanted_section = False
        for line in code.splitlines():
            if line.startswith("{{(|"):
                in_unwanted_section = True
            elif line.startswith("{{)}}"):
                in_unwanted_section = False
            elif not in_unwanted_section:
                cleaned.append(line)
        code = "\n".join(cleaned)

    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    #
    # Variants
    #

    # `#''forma de feminin singular pentru'' [[frumos]].` → `# {{flexion|frumos}}`
    # `#''formă alternativă pentru'' [[fântânioară]].` → `# {{flexion|fântânioară}}`
    code = RE_VARIANTS.sub(r"# {{flexion|\1}}", code)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code, rest = tpl_code.rsplit("}}", 1)
                    forms: set[str] = set()
                    for form in RE_REV_VARIANTS.findall(tpl_code):
                        if "(" in form:
                            form = form.split("(", 1)[0]
                        if "<br" in form:
                            form = RE_SPLIT_BR.sub("/", form)
                        if "/" in form:
                            for sform in form.split("/"):
                                forms.add(sform.strip("[]").strip())
                        else:
                            forms.add(form.strip("[]").strip())
                    for discard in REV_VARIANTS_IGNORED:
                        forms.discard(discard)
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms))
                    if rest:
                        cleaned.append(rest)
                    tpl_code = ""
                continue

            cleaned.append(line)

        code = "\n".join(cleaned)

    return code
