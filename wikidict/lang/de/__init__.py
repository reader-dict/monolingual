"""German language (Deutsch)."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://de.wiktionary.org/wiki/Spezial:Zuf%C3%A4llige_Stammseite"

module_trans = "Modul"
template_trans = "Vorlage"

section_sublevels = (3, 4)
head_sections = ("{{sprache|deutsch}}", "{{sprache|international}}")
etyl_section = ("{{herkunft}}",)
sections = (
    *etyl_section,
    "{{aussprache}",
    "{{bedeutungen}",
    "{{nebenformen}",
    "{{synonyme}",
    "{{variant}",
)

variant_templates = ("{{flexion",)

reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{Audio",
    "{{Fremdsprachige Beispiele",  # foreign examples
    "{{Herkunft fehlt",  # missing origin
    "{{Herkunft unbelegt",  # unverfied origin
    "{{Hörbeispiele",  # audio sample
    "{{Q",
    "{{Ref",
    "{{Wikipedia",
)

RE_FIND_GENDERS = re.compile(r",\s++\{\{([fmnu]++)\}\}")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "de")
    []
    >>> find_genders("=== {{Wortart|Abkürzung|Deutsch}}, {{mf}}, {{Wortart|Substantiv|Deutsch}} ===", "de")
    ['f', 'm']
    """
    res: set[str] = set()
    for gender in RE_FIND_GENDERS.findall(code):
        if "".join(sgen := sorted(gender)) in {"fm", "fmn"}:
            res.update(sgen)
        else:
            res.add(gender)
    return utils.unique(sorted(res))


RE_FIND_PRONS = re.compile(r"\{\{Lautschrift\|([^=}]++)}")


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "de")
    []
    >>> find_pronunciations(":{{IPA}} {{Lautschrift||spr=de}}", "de")
    []
    >>> find_pronunciations(":{{IPA}} {{Lautschrift|ˈʁɪndɐˌsteːk}}", "de")
    ['[ˈʁɪndɐˌsteːk]']
    >>> find_pronunciations(":{{IPA}} {{Lautschrift|ˈʁɪndɐˌsteːk}}, {{Lautschrift|ˈʁɪndɐˌʃteːk}}, {{Lautschrift|ˈʁɪndɐˌsteɪ̯k}}", "de")
    ['[ˈʁɪndɐˌsteːk]', '[ˈʁɪndɐˌʃteːk]', '[ˈʁɪndɐˌsteɪ̯k]']
    """
    for line in code.splitlines():
        if "{{IPA}}" not in line:
            continue
        return [f"[{p}]" for p in RE_FIND_PRONS.findall(line)]
    return []


RE_CLEANUPS = [
    # `{{Grundformverweis Konj|tragen}}` → `{{flexion|tragen}}`
    (
        re.compile(r"(?m)^\{\{(?:Alte Schreibweise|Grundformverweis)[^|]*+\|([^}]++)\}\}"),
        r"==== {{Variant}} ====\n# {{flexion|\1}}",
    ),
    # `{{Bedeutungen}}` → `==== {{Bedeutungen}} ====`
    (re.compile(r"(?m)^\{\{(.+)\}\}"), r"==== {{\1}} ===="),
]
RE_NUMBERED_LIST = re.compile(r":\[\d++\][ ]*+")
RE_REV_VARIANTS1 = re.compile(r"(?sm)^=++[ ]*+\{\{Nebenformen\}\}[ ]*+=++([^=]++)")
RE_REV_VARIANTS2 = re.compile(r"\[\[([^\]]++)\]\]")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("{{Grundformverweis Konj|tragen}}", "de")
    '==== {{Variant}} ====\n# {{flexion|tragen}}'

    >>> adjust_wikicode("{{Bedeutungen}}\n:[1] \n\n{{Herkunft}}\n:[[Abkürzung]] von [[Sturmkanone]]", "de")
    '==== {{Bedeutungen}} ====\n# \n\n==== {{Herkunft}} ====\n:[[Abkürzung]] von [[Sturmkanone]]'
    >>> adjust_wikicode("{{Bedeutungen}}\n:[1] {{K|Handwerk|Architektur|ft=[[defektives Verb{{!}}defektiv]]}}", "de")
    '==== {{Bedeutungen}} ====\n# {{K|Handwerk|Architektur|ft=[[defektives Verb{{!}}defektiv]]}}'

    >>> adjust_wikicode("{{Bedeutungen}}\n=== {{Wortart|Konjugierte Form|Deutsch}} ===\n{{Nebenformen}}\n:''2. Person Plural Konjunktiv I Präsens Aktiv:'' [[kartlet]]", "de")
    '==== {{Bedeutungen}} ====\n=== {{Wortart|Konjugierte Form|Deutsch}} ===\n==== {{Nebenformen}} ====\n# {{rev-flexion|kartlet}}\n'
    >>> adjust_wikicode("{{Bedeutungen}}\n==== {{Nebenformen}} ====\n:[[rev var 1]], [[rev var 2]]", "de")
    '==== {{Bedeutungen}} ====\n==== {{Nebenformen}} ====\n# {{rev-flexion|rev var 1}}\n# {{rev-flexion|rev var 2}}\n'
    """
    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    # Synonyms go under their meaning: `:[1, 2] [[flink]]` as a sub-definition of the meanings 1 and 2
    code = utils.attach_numbered_synonyms(
        code, "{{bedeutungen}}", "{{synonyme}}", "Syn.", number=r":\[([^\]]*+)\][ ]*+"
    )

    # Definition lists are not well supported by the parser, replace them by numbered lists.
    # Note: using `[ ]*` rather than `\s*` to bypass issues when a section above another one
    #       contains an empty item.
    code = RE_NUMBERED_LIST.sub("# ", code)

    #
    # Reverse variants
    #

    if "{{Nebenformen}" in code:
        for section_code in RE_REV_VARIANTS1.findall(code):
            new_code = "\n".join(
                f"# {{{{rev-flexion|{form.split('#', 1)[0]}}}}}" for form in RE_REV_VARIANTS2.findall(section_code)
            )
            code = code.replace(section_code, f"\n{new_code}\n", count=1)

    return code
