"""Finnish language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __file__.rsplit("/", 2)[-2]

random_word_url = "https://fi.wiktionary.org/wiki/Toiminnot:Satunnainen_sivu"

module_trans = "Moduuli"
template_trans = "Malline"

section_patterns = ("#", r"\*")
section_sublevels = (3, 4, 5)
head_sections = (
    "suomi",  # Finnish
    "kansainvälinen",  # international
)
etyl_section = ("etymologia",)
sections = (
    *etyl_section,
    # "aakkonen",  # alphabet, see #2634
    "adjektiivi",
    "adverbi",
    "adpositio",
    "affiksi",
    "artikkeli",
    "erisnimi",  # proper noun
    "fraasi",
    "idiomi",  # idom
    "interjektio",
    "lyhenne",  # abbreviation
    # "kirjoitusmerkki",  # character, see #2624
    # "kirjain",  # letter, see #2634
    "konjunktio",
    "numeraali",
    "partikkeli",
    "postpositio",
    "prefiksi",
    "prepositio",
    "pronomini",
    "substantiivi",
    "suffiksi",
    "supistuma",  # contraction
    "symboli",
    "synonyymi",
    "taivutus",  # inflection
    "verbi",
    "välimerkki",  # punctuation mark
)

variant_templates = tuple(f"{{{{{tpl}" for tpl in variant_handlers_mod.VAR_TEMPLATES)

reverse_variant_titles = (
    "{{fi-subs",
    "{{fi-verbi",
)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{esim?",  # source
    "{{lainaus?",  # to be verified
    "{{määritelmä/korjattava",  # definition to repair
    "{{tarkistettava/lainaus",  # to be verified
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("{{IPA|[ʃɑtobriã]}}", LANG)
    ['/ʃɑtobriã/']

    >>> find_pronunciations("{{IPA|'e̞n̪(t̪).t̪e̞(.)r(i)}}", LANG)
    ['/e̞n̪t̪.t̪e̞.ri/']

    >>> find_pronunciations("{{IPA|/{{l|kans|ʋ}}/}}", LANG)
    ['/ʋ/']

    >>> _ = context.reset(LANG)

    >>> context.new_word("kreppi")
    >>> find_pronunciations("", LANG)
    ['/ˈkrepːi/']

    >>> context.new_word("marssia")
    >>> find_pronunciations("{{fi-äänt|*}}", LANG)
    ['/ˈmɑrsːiɑˣ/']
    """
    res: list[str] = []
    if prons := re.findall(r"\{\{IPA\|.([^/\]}]+)", code):
        pron = prons[0]
        if "{{" in pron:
            pron = pron.split("|")[-1]
        res.append(pron)
    else:
        if not (templates := re.findall(rf"({{{{{locale}-äänt[^}}]*}}}})", code)):
            templates = [f"{{{{{locale}-äänt}}}}"]

        expanded = context.expand(templates[0], LANG, skip_cache=True)
        if line := next((l_ for l_ in expanded.splitlines() if "|IPA" in l_), ""):
            res.extend(re.findall(r"/([^/]+)/", line))

    return [re.sub(r"[()]", "", f"/{pron}/") for pron in res]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("==Suomi==\n{{subs-taivm|Suomen|p|ojan}}\n# {{taivm-y-gen|fi|poika|luok=s}}", LANG)
    '==Suomi==\n===Substantiivi===\n# {{taivm-y-gen|fi|poika|luok=s}}'

    >>> adjust_wikicode("# {{taivm}} ''akkusatiivin monikko sanasta'' '''[[yrittävä]]'''", LANG)
    '# {{flexion|yrittävä}}'
    >>> adjust_wikicode("# {{taivm}} ''aktiivin partisiipin preesensin monikon nominatiivi verbistä'' '''[[yrittää]]'''", LANG)
    '# {{flexion|yrittää}}'
    >>> adjust_wikicode("# {{taivm}} {{taivm-teksti|aktiivin indikatiivin preesensin konnegaatiomuoto verbistä}} '''{{l|fi|tuntea}}'''", LANG)
    '# {{flexion|tuntea}}'
    >>> adjust_wikicode("# {{taivm}} {{taivm-teksti|aktiivin indikatiivin preesensin konnegaatiomuoto verbistä}} '''{{l|fi|tuntea|tuntea se}}'''", LANG)
    '# {{flexion|tuntea}}'
    """
    # Fix POS-less words
    if "{{subs-taivm|Suomen|" in code:
        code = re.sub(r"^\{\{subs-taivm\|Suomen\|.+", r"===Substantiivi===", code, flags=re.MULTILINE)

    #
    # Variants
    #

    lines: list[str] = []

    if "{{taivm}}" in code or "(''taivutusmuoto'')" in code:
        for raw_line in code.splitlines():
            if not (line := raw_line.strip()):
                continue
            elif line.startswith(("# {{taivm}}", "#{{taivm}}", "# (''taivutusmuoto'')", "#(''taivutusmuoto'')")) and (
                forms_ := (
                    re.findall(r"'+\[\[([^\]]+)\]\]'+$", line) or re.findall(rf"'+\{{\{{l\|{locale}\|([^|}}]+)", line)
                )
            ):
                line = f"# {{{{flexion|{forms_[0]}}}}}"
            lines.append(line)
        code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)}).+)"
        lines.clear()

        for line in code.splitlines():
            if not any(tpl in line for tpl in interesting_reverse_variant_titles):
                lines.append(line)
                continue

            for tpl in re.findall(pattern, line):
                tpl_name = tpl[2 : max(0, tpl.find("|")) or tpl.find("}")].strip(" \u200e")
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                lines.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(lines)

    return code
