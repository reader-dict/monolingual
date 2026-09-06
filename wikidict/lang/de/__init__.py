"""German language (Deutsch)."""

import re

from ... import utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://de.wiktionary.org/wiki/Spezial:Zuf%C3%A4llige_Stammseite"

module_trans = "Modul"
template_trans = "Vorlage"

float_separator = ","
thousands_separator = "."

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


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "de")
    []
    >>> find_genders("=== {{Wortart|Abkürzung|Deutsch}}, {{mf}}, {{Wortart|Substantiv|Deutsch}} ===", "de")
    ['mf']
    """
    pattern = re.compile(r",\s+{{([fmnu]+)}}")
    return utils.unique(pattern.findall(code))


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
    pattern = re.compile(r"{Lautschrift\|([^=}]+)}")
    return sorted(f"[{p}]" for p in utils.unique(pattern.findall(code)))


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
    # `{{Grundformverweis Konj|tragen}}` → `{{flexion|tragen}}`
    code = re.sub(
        r"^\{\{(?:Alte Schreibweise|Grundformverweis)[^|]*\|([^}]+)\}\}",
        r"==== {{Variant}} ====\n# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    # `{{Bedeutungen}}` → `==== {{Bedeutungen}} ====`
    code = re.sub(r"^\{\{(.+)\}\}", r"==== {{\1}} ====", code, flags=re.MULTILINE)

    # Definition lists are not well supported by the parser, replace them by numbered lists.
    # Note: using `[ ]*` rather than `\s*` to bypass issues when a section above another one
    #       contains an empty item.
    code = re.sub(r":\[\d+\][ ]*", "# ", code)

    #
    # Reverse variants
    #

    if "{{Nebenformen}" in code:
        for section_code in re.findall(r"^=+[ ]*{{Nebenformen}}[ ]*=+([^=]+)", code, flags=re.DOTALL | re.MULTILINE):
            new_code = "\n".join(
                f"# {{{{rev-flexion|{form.split('#', 1)[0]}}}}}"
                for form in re.findall(r"\[\[([^\]]+)\]\]", section_code)
            )
            code = code.replace(section_code, f"\n{new_code}\n", count=1)

    return code
