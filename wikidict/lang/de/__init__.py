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
    "{{variant}",
)

variant_titles = (
    "",  # Empty for simple redirection words (ex: https://de.wiktionary.org/wiki/daß) # TODO remove with #2534?
    "konjugierte form",
)
variant_templates = ("{{flexion",)

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
    return [f"[{p}]" for p in utils.unique(pattern.findall(code))]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{Grundformverweis Konj|tragen}}", "de")
    '==== {{Variant}} ====\\n# {{flexion|tragen}}'

    >>> adjust_wikicode("== CIA ({{Sprache|Deutsch}}) ==", "de")
    '== {{Sprache|Deutsch}} =='

    >>> adjust_wikicode("{{Bedeutungen}}\\n:[1] \\n\\n{{Herkunft}}\\n:[[Abkürzung]] von [[Sturmkanone]]", "de")
    '==== {{Bedeutungen}} ====\\n# \\n\\n==== {{Herkunft}} ====\\n:[[Abkürzung]] von [[Sturmkanone]]'
    >>> adjust_wikicode("{{Bedeutungen}}\\n:[1] {{K|Handwerk|Architektur|ft=[[defektives Verb{{!}}defektiv]]}}", "de")
    '==== {{Bedeutungen}} ====\\n# {{K|Handwerk|Architektur|ft=[[defektives Verb{{!}}defektiv]]}}'
    """
    # `{{Grundformverweis Konj|tragen}}` → `{{flexion|tragen}}`
    code = re.sub(
        r"^\{\{(?:Alte Schreibweise|Grundformverweis)[^|]*\|([^}]+)\}\}",
        r"==== {{Variant}} ====\n# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    # `== CIA ({{Sprache|Deutsch}}) ==` → `== {{Sprache|Deutsch}} ==`
    code = re.sub(r"^==\s*.*\((\{\{Sprache\|[^}]+\}\})\)\s*==", r"== \1 ==", code, flags=re.MULTILINE)

    # `{{Bedeutungen}}` → `==== {{Bedeutungen}} ====`
    code = re.sub(r"^\{\{(.+)\}\}", r"==== {{\1}} ====", code, flags=re.MULTILINE)

    # Definition lists are not well supported by the parser, replace them by numbered lists.
    # Note: using `[ ]*` rather than `\s*` to bypass issues when a section above another one
    #       contains an empty item.
    code = re.sub(r":\[\d+\][ ]*", "# ", code)

    return code
