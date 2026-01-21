"""Lithuanian language."""

import re
from collections import defaultdict

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
from .template_adapters import adapters as template_adapters  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://lt.wiktionary.org/wiki/Specialus:Atsitiktinis_puslapis"

template_trans = "Šablonas"

float_separator = ","

section_sublevels = (3, 4)
head_sections = ("{{ltv}}",)
etyl_section = ("etimologija",)
sections = (
    *etyl_section,
    "artikelis",  # article
    "būdvardis",  # adjective
    "būdinys",  # adverb
    "daiktavardis",  # noun
    "dalyvis",  # participle
    "dalelytė",  # particle
    # "išraiškos arba posakiai",  # expressions or sayings
    "įvardis",  # pronoun
    "jungtukas",  # connector
    "jaustukas",  # emoticon
    "padalyvis",  # participle
    "prielinksnis",  # preposition
    "priešdėlis",  # prefix
    "prieveiksmis",  # adverb
    "pusdalyvis",  # participle
    "raidė",  # letter
    "santrumpa",  # abbreviation
    "simboliai",  # symbols
    "simbolis",  # symbol
    "skaitvardis",  # numerical
    "veiksmažodis",  # verb
    "žodžių junginys",  # phrase
)

variant_titles = sections
variant_templates = ("{{flexion",)

reverse_variant_titles = (
    "{{ltbdv",
    "{{ltbdn",
    "{{ltdkt",
    "{{ltdlv",
    "{{ltpdlv",
    "{{ltpsdlv",
    "{{ltvks",
)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{bot-entry",
    "{{etimologija-stub",
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "lt")
    []

    >>> find_genders("{{ltdkt}} {{f}}", "lt")
    ['f']
    >>> find_genders("{{ltdkt}} {{m}}", "lt")
    ['m']

    >>> find_genders("(<i>mot. g.</i>)", "lt")
    ['f']
    >>> find_genders("(<i>vyr. g.</i>)", "lt")
    ['m']
    """
    res: list[str] = re.compile(r"\{\{([fm]+)\}\}").findall(code)
    if "(<i>mot. g.</i>)" in code:
        res.append("f")
    if "(<i>vyr. g.</i>)" in code:
        res.append("m")
    return utils.unique(res)


def find_pronunciations(
    code: str, locale: str, *, pattern: re.Pattern[str] = re.compile(r"\{IPA\|([^}]+)")
) -> list[str]:
    """
    >>> find_pronunciations("", "lt")
    []
    >>> find_pronunciations("{{IPA|[ˈsʲæːnɐs]}}", "lt")
    ['[ˈsʲæːnɐs]']
    """
    return utils.unique(utils.flatten(pattern.findall(code)))


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("<br clear=all>", "lt")
    ''
    >>> adjust_wikicode("<br clear=all >", "lt")
    ''
    >>> adjust_wikicode("<br clear=all/>", "lt")
    ''
    >>> adjust_wikicode("<br clear=all />", "lt")
    ''

    >>> adjust_wikicode("----", "lt")
    ''

    >>> adjust_wikicode("'''[[foo]]'''", "lt", word="foo")
    ''

    >>> adjust_wikicode("== {{ltv}} ==\n=== ''Daiktavardis'' ===\n==== Etimologija ====\n{{Žodžiai|jung}}\n*[[Antigva]]\n*[[Barbuda]]", "lt", word="foo")
    "== {{ltv}} ==\n=== ''Daiktavardis'' ===\n==== Etimologija ===="

    >>> adjust_wikicode("== {{ltv}} ==\n=== ''Daiktavardis'' ===\n'''Žodžių junginį sudaro žodžiai:'''\n* {{t+|lt|būtasis}}\n* {{t+|lt|laikas}}", "lt", word="foo")
    "== {{ltv}} ==\n=== ''Daiktavardis'' ==="

    >>> from ... import context
    >>> _ = context.reset("lt")

    >>> context.new_word("Kvietkauskas")
    >>> adjust_wikicode("== {{ltv}} ==\n=== ''Daiktavardis'' ===\n{{ltdkt|forma=f-{{{forma|vyr-1l-as}}}|tikr=tikr|šakn=Kvietkausk|šakn2={{{sakn2}}}}}", "lt", word="Kvietkauskas")
    "== {{ltv}} ==\n=== ''Daiktavardis'' ===\n# {{rev-flexion|Kvietkauskai}}\n# {{rev-flexion|Kvietkauskais}}\n# {{rev-flexion|Kvietkauskams}}\n# {{rev-flexion|Kvietkauske}}\n# {{rev-flexion|Kvietkausko}}\n# {{rev-flexion|Kvietkausku}}\n# {{rev-flexion|Kvietkauskui}}\n# {{rev-flexion|Kvietkauskuose}}\n# {{rev-flexion|Kvietkauskus}}\n# {{rev-flexion|Kvietkauską}}\n# {{rev-flexion|Kvietkauskų}}\n{{m}}"
    """

    # Drop "see also" inline text
    lines: list[str] = []
    in_section = False
    for line in code.splitlines():
        if "{{Žodžiai" in line or "Žodžių junginį" in line or "Santrumpą sudaro" in line:
            in_section = True
            continue
        if in_section:
            if line.startswith("*"):
                continue
            in_section = False
        lines.append(line)
    code = "\n".join(lines)

    # Remove uninteresting sections that would mess with genders finding
    lines.clear()
    in_section = False
    for line in code.splitlines():
        if line.startswith("==== "):
            in_section = "Sinonimai" in line or "Vertimai" in line or "Išraiškos" in line or "Antonimai" in line
        elif line.startswith("<br clear"):
            in_section = False
        if not in_section:
            lines.append(line)
    code = "\n".join(lines)

    # More clean-up
    code = re.sub(r"<br clear=all[ ]*/?>", "", code)
    code = code.replace("----", "")
    code = code.replace(f"'''[[{word}]]'''", "")

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    interesting_reverse_variant_titles_alone = tuple(f"{t}}}}}" for t in interesting_reverse_variant_titles)
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_tpl = False
        tpl_code = ""
        table_count = 0

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles) and not line.startswith(
                interesting_reverse_variant_titles_alone
            ):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code = tpl_code.rsplit("}}", 1)[0]
                    tpl_code += "}}"

                    if "{{{" in tpl_code:
                        forms = variant_handlers_mod.render_reverse_variant(tpl_code, [], defaultdict(str), word)
                    else:
                        tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip()
                        variant_handlers_mod.append_to_reverse_variants(tpl_name)
                        forms = utils.process_templates(
                            word,
                            tpl_code,
                            locale,
                            templates_status=templates_status,
                            variant_only=True,
                        )

                    if forms:
                        # The gender can be derived from the reverse variants table
                        cleaned.extend(
                            form
                            if "g.</i>" in form or form.startswith("{{") or form == "SKIP WORD"
                            else f"# {{{{rev-flexion|{form}}}}}"
                            for form in sorted(forms.split("|"))
                        )
                    tpl_code = ""
                    table_count += 1
            else:
                cleaned.append(line)

        # We do not want to keep variants since they all are copy-paste of the base form
        if table_count > 0 and cleaned.count("SKIP WORD") == table_count:
            return ""

        code = "\n".join(cleaned)

    return code
