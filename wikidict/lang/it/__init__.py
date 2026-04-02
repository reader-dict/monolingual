"""Italian language."""

import re

from ... import utils
from ...lang import defaults
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://it.wiktionary.org/wiki/Speciale:RandomRootpage"

module_trans = "Modulo"

float_separator = ","
thousands_separator = " "

head_sections = ("{{-it-}}",)
etyl_section = ("{{etim}}",)
sections = (
    *head_sections,
    *etyl_section,
    "{{acron}",
    "{{agg}",
    "{{agg form}",
    "{{avv}",
    "{{art}",
    "{{cong}",
    "{{inter}",
    "{{loc nom}",
    "{{nome}",
    "{{pref}",
    "{{prep}",
    "{{pron poss}",
    "{{suff}",
    "{{sost}",
    "{{sost form}",
    "{{verb}",
    "{{verb form}",
)

variant_titles = (
    "{{agg form",
    "{{sost",
    "{{suff",
    "{{verb form",
)
variant_templates = (
    "{{flexion",
    "{{Tabs",
)

definitions_to_ignore = (
    "{{Nodef",
    "{{Noetim",
    "{{Noref",
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "it")
    []
    >>> find_genders("{{Pn}} ''m sing''", "it")
    ['m']
    """
    pattern = re.compile(r"{{Pn\|?w?}} ''([fm])[singvol ]*''")
    return utils.unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "it")
    []
    >>> find_pronunciations("{{IPA|/kondiˈvidere/}}", "it")
    ['/kondiˈvidere/']
    >>> find_pronunciations("{{IPA|/əˈtʃì:vəb<sup>lə</sup>/}}", "it")
    ['/əˈtʃì:vəb<sup>lə</sup>/']
    """
    pattern = re.compile(r"{IPA\|(/(.+)/)}")
    return [prons[0][0]] if (prons := pattern.findall(code)) else []


START = rf"^(?:{'|'.join(defaults.section_patterns)})\s*"
PATTERNS = [
    # plurale di [[-ectomia]]
    # terza persona plurale del congiuntivo presente di [[brillantare]]
    # gerundio presente di [[abalienare]
    r".+(?:femminile|gerundio|singolare|plurale)[^\n]+(?:di|del verbo) \[\[([^#\]]+)",
    # participio presente di [[amare]]
    # participio passato di [[amare]]
    r"participio (?:passato|presente)[^\n]+di \[\[([^#\]]+)",
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("== {{-it-}} ==\n[[w:A|B]]", "it")
    '== {{-it-}} ==\n[[A|B]]'

    >>> adjust_wikicode("== {{-it-}} ==\n[[en:foo]]", "it")
    '== {{-it-}} =='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-verb form-}}", "it")
    '== {{-it-}} ==\n=== {{verb form}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-avv-|it}}", "it")
    '== {{-it-}} ==\n=== {{avv}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-avv-|ANY}}", "it")
    '== {{-it-}} ==\n=== {{avv|ANY}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-avv-}}", "it")
    '== {{-it-}} ==\n=== {{avv}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n# plurale di [[-ectomia]]", "it")
    '== {{-it-}} ==\n# {{flexion|-ectomia}}'

    >>> adjust_wikicode("== {{-it-}} ==\n#participio presente di [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n#participio passato di [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# participio presente di [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n#2ª pers. singolare indicativo presente del verbo [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# {{3}} singolare imperativo presente del verbo [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# {{1}}, 2ª pers. e {{3}} singolare congiuntivo presente del verbo [[amare]]", "it")
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# prima persona singolare dell'indicativo presente di [[ducere#Italiano|ducere]]", "it")
    '== {{-it-}} ==\n# {{flexion|ducere}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# gerundio presente di [[abalienare]", "it")
    '== {{-it-}} ==\n# {{flexion|abalienare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# seconda persona plurale dell'[[indicativo]] [[presente]] di [[abalienare]]", "it")
    '== {{-it-}} ==\n# {{flexion|abalienare}}'
    """

    # [[en:foo]] → ''
    code = re.sub(r"(\[\[\w+:\w+\]\])", "", code)

    # {{-verb form-}} → === {{verb form}} ===
    code = re.sub(r"^\{\{-(.+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # {{-avv-|it}} → === {{avv}} ===
    code = re.sub(rf"^\{{\{{-(.+)-\|{locale}\}}\}}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # {{-avv-|ANY}} → === {{avv|ANY}} ===
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

    # {{-avv-}} → === {{avv}} ===
    code = re.sub(r"^\{\{-(\w+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # [[w:A|B]] → [[A|B]]
    code = code.replace("[[w:", "[[")

    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(START, line):
            for pattern in PATTERNS:
                line, count = re.subn(rf"{START}{pattern}.*", r"# {{flexion|\1}}", line, count=1, flags=re.IGNORECASE)  # noqa: PLW2901
                if count:
                    break
        lines.append(line)

    return "\n".join(lines)
