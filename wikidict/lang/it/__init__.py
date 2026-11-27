"""Italian language."""

import re

from ... import utils
from ...lang import defaults
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://it.wiktionary.org/wiki/Speciale:RandomRootpage"

module_trans = "Modulo"

section_patterns = ("#", r"\*")
head_sections = ("{{-it-}}",)
etyl_section = ("{{etim}}",)
sections = (
    *head_sections,
    *etyl_section,
    "{{abbr}",
    "{{acron}",
    "{{agg}",
    "{{agg dim}",
    "{{agg form}",
    "{{agg num}",
    "{{avv}",
    "{{art}",
    "{{chat}",
    "{{cong}",
    "{{espr}",
    "{{inter}",
    "{{loc agg}",
    "{{loc avv}",
    "{{loc cong}",
    "{{loc nom}",
    "{{loc prep}",
    "{{loc verb}",
    "{{nome}",
    "{{ord}",
    "{{pref}",
    "{{prep}",
    "{{pron dim}",
    "{{pron poss}",
    "{{pronome}",
    "{{sin}",
    "{{sost}",
    "{{sost form}",
    "{{suff}",
    "{{verb}",
    "{{verb form}",
)

variant_templates = ("{{flexion",)

definitions_to_ignore = (
    "{{Nodef",
    "{{Noetim",
    "{{Noref",
)


RE_GENDER = re.compile(r"\{\{Pn\|?w?\}\} ''([fm])[singvol ]*+''")


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", LANG)
    []
    >>> find_genders("{{Pn}} ''m sing''", LANG)
    ['m']
    """
    return utils.unique(RE_GENDER.findall(code))


RE_PRON = re.compile(r"\{\{IPA\|/([^}]+)/\}\}")


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", LANG)
    []
    >>> find_pronunciations("{{IPA|/kondiˈvidere/}}", LANG)
    ['/kondiˈvidere/']
    >>> find_pronunciations("{{IPA|/əˈtʃì:vəb<sup>lə</sup>/}}", LANG)
    ['/əˈtʃì:vəb<sup>lə</sup>/']
    >>> find_pronunciations("{{IPA|/ undiˈt͡ʃɛzimo/}} o {{IPA|/uniˈt͡ʃezimo/}}", LANG)
    ['/undiˈt͡ʃɛzimo/']
    """
    return [f"/{pron[1].strip()}/"] if (pron := RE_PRON.search(code)) else []


START = rf"^(?:{'|'.join(defaults.section_patterns)})\s*"
PATTERNS = [
    # plurale di [[-ectomia]]
    # terza persona plurale del congiuntivo presente di [[brillantare]]
    # gerundio presente di [[abalienare]
    re.compile(rf"(?i){START}.*?(?:femminile|gerundio|singolare|plurale)[^\n]+(?:di|del verbo) \[\[([^#\]]++).*"),
    # participio presente di [[amare]]
    # participio passato di [[amare]]
    re.compile(rf"(?i){START}participio (?:passato|presente)[^\n]+di \[\[([^#\]]++).*"),
]
RE_CLEANUPS = [
    # [[en:foo]] → ''
    (re.compile(r"(\[\[:?\w++:\w++\]\])"), ""),
    # ` ([[:it:foo|italian]])` → ''
    (re.compile(r"[ ]*+\(?\[\[:\w++:[^|]++\|[^\]]++\]\]\)?"), ""),
    # {{-verb form-}} → === {{verb form}} ===
    (re.compile(r"(?m)^\{\{[ ]*+-(.+)-[ ]*+\}\}"), r"=== {{\1}} ==="),
    # {{-avv-|ANY}} → === {{avv}} ===
    (re.compile(r"(?m)^\{\{[ ]*+-(.+)-[ ]*+\|[ ]*+(\w++)[ ]*+\}\}"), r"=== {{\1}} ==="),
    # {{-avv-}} → === {{avv}} ===
    (re.compile(r"(?m)^\{\{[ ]*+-(\w++)-[ ]*+\}\}"), r"=== {{\1}} ==="),
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
    >>> adjust_wikicode("== {{-it-}} ==\n[[w:A|B]]", LANG)
    '== {{-it-}} ==\n[[A|B]]'

    >>> adjust_wikicode("== {{-it-}} ==\n[[en:foo]]", LANG)
    '== {{-it-}} =='

    >>> adjust_wikicode("== {{-it-}} ==\n ([[:it:foo|italian]])", LANG)
    '== {{-it-}} =='
    >>> adjust_wikicode("== {{-it-}} ==\n([[:it:foo|italian]])", LANG)
    '== {{-it-}} =='
    >>> adjust_wikicode("== {{-it-}} ==\n[[:it:foo|italian]]", LANG)
    '== {{-it-}} =='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-verb form- }}", LANG)
    '== {{-it-}} ==\n=== {{verb form}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{-avv- |it }}", LANG)
    '== {{-it-}} ==\n=== {{avv}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{ -avv-| ANY }}", LANG)
    '== {{-it-}} ==\n=== {{avv}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n{{ -avv- }}", LANG)
    '== {{-it-}} ==\n=== {{avv}} ==='

    >>> adjust_wikicode("== {{-it-}} ==\n#plurale di [[infermiera]]", LANG)
    '== {{-it-}} ==\n# {{flexion|infermiera}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# plurale di [[-ectomia]]", LANG)
    '== {{-it-}} ==\n# {{flexion|-ectomia}}'

    >>> adjust_wikicode("== {{-it-}} ==\n#participio presente di [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n#participio passato di [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# participio presente di [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n#2ª pers. singolare indicativo presente del verbo [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# {{3}} singolare imperativo presente del verbo [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# {{1}}, 2ª pers. e {{3}} singolare congiuntivo presente del verbo [[amare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|amare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# prima persona singolare dell'indicativo presente di [[ducere#Italiano|ducere]]", LANG)
    '== {{-it-}} ==\n# {{flexion|ducere}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# gerundio presente di [[abalienare]", LANG)
    '== {{-it-}} ==\n# {{flexion|abalienare}}'
    >>> adjust_wikicode("== {{-it-}} ==\n# seconda persona plurale dell'[[indicativo]] [[presente]] di [[abalienare]]", LANG)
    '== {{-it-}} ==\n# {{flexion|abalienare}}'
    """

    for pattern, rpl in RE_CLEANUPS:
        code = pattern.sub(rpl, code)

    # [[w:A|B]] → [[A|B]]
    code = code.replace("[[w:", "[[")

    # Synonyms
    lines: list[str] = []
    if "{{sin}}" in code:
        in_section = False
        for line in code.splitlines():
            if line.startswith("=== {{sin}"):
                in_section = True
            elif in_section:
                if line.startswith("*"):
                    line = line.replace("*", "#")
                else:
                    in_section = False
            lines.append(line)
        code = "\n".join(lines)

    #
    # Variants
    #

    lines.clear()
    for line in code.splitlines():
        if re.match(START, line):
            for pattern in PATTERNS:
                line, count = pattern.subn(r"# {{flexion|\1}}", line, count=1)
                if count:
                    break
        lines.append(line)

    return "\n".join(lines)
