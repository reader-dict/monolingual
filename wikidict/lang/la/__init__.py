"""Latin language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __file__.rsplit("/", 2)[-2]

random_word_url = "https://la.wiktionary.org/wiki/Specialis:Pagina_fortuita"

module_trans = "Modulus"
template_trans = "Formula"

head_sections = (
    "{{-la-",
    "{{-lingua-|la|",
    "{{-lingua-|la}",
    "latice",
    "{{mul",
)
section_sublevels = (3, 4)
etyl_section = ("Notatio",)
# https://la.wiktionary.org/w/index.php?title=Modulus:partes_orationis/data&oldid=195652
_sections = [
    "abbr",
    "adi",
    "adv",
    "aff",
    "art",
    "aux",
    "card",
    "circ",
    "con",
    "decl",
    "dep",
    "dis",
    "encl",
    "gerund",
    "inf",
    "int:",
    "inter",
    "intr",
    "locut",
    "nomen",
    "nota",
    "num",
    "ord",
    "ono",
    "part",
    "post",
    "praef",
    "praep",
    "pron",
    "prop",
    "prov",
    "refl",
    "semi",
    "signum",
    "sino",
    "suff",
    "subs",
    "symb",
    "syn",
    "trans",
    "verbum",
]
_sections.extend(f"{{{{{s}" for s in _sections.copy())
sections = tuple(_sections)

variant_templates = ("{{flexion", "{{coniug|la|")

reverse_variant_titles = (
    "{{coniugatio",
    "{{declinatio",
    "{{la-coniugatio",
    "{{la-declinatio",
)
reverse_variant_templates = ("{{rev-flexion",)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", LANG)
    []
    >>> find_genders("'''ger'''|'''ō, -ōnis''' ''{{m}}''", LANG)
    ['m']
    """
    return sorted(set(re.findall(r"\{\{([cfmn])\}\}", code)))


def find_pronunciations(code: str, locale: str, word: str) -> list[str]:
    r"""
    >>> find_pronunciations("", LANG, "")
    []

    >>> _ = context.reset(LANG)
    >>> context.new_word("foo")

    >> find_pronunciations("==={{appellatio}}===\n:{{Audio|La-cls-gero.ogg|//|{{la-cls-appellatio}}|la|gerō}}", LANG, "gero")
    []

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio|La-cls-gero.ogg||{{la-cls-appellatio}}|la|gerō}}", LANG, "gero")
    []

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio|La-cls-gero.ogg|/ˈgeroː/|{{la-cls-appellatio}}|la|gerō}}", LANG, "gero")
    ['Class.: /ˈgeroː/']

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio||/ˈgeroː/|{{la-cls-appellatio}}|la|gerō}}", LANG, "gero")
    ['Class.: /ˈgeroː/']

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio||[ˈgeroː]|{{la-cls-appellatio}}|la|gerō}}", LANG, "gero")
    ['Class.: /ˈgeroː/']

    >>> find_pronunciations("==={{appellatio}}===\n{{Audio|api=/ˈgeroː/}}", LANG, "gero")
    ['/ˈgeroː/']

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio|La-cls-amarus.ogg|/aˈmaːrus/|{{la-cls-appellatio}}|la|amārus}}\n:{{Audio|La-ecc-amarus.ogg|/aˈmarus/|{{la-ecc-appellatio}}|la}}", LANG, "amarus")
    ['Class.: /aˈmaːrus/', 'Eccl.: /aˈmarus/']

    >>> find_pronunciations("==={{appellatio}}===\n:{{Audio|La-cls-lacuna.ogg| /laˈkuːna/, [ɫaˈkuːna]|{{la-cls-appellatio}}|la|lacūna}}", LANG, "lacuna")
    ['Class.: /laˈkuːna/']

    >>> find_pronunciations("==={{appellatio}}===\n::{{Audio|La-cls-abscedo, abscedere, abscessi, abscessum.ogg|/absˈkeːdoː/|{{la-cls-appellatio}} restitute|la|abscēdō}}\n:{{Audio|La-ecc-abscedo, abscedere, abscessi, abscessum.ogg|/apˈʃedo apˈʃedere apˈʃessi apˈʃessum/|{{la-ecc-appellatio}}|la|abscedo, abscedere, abscessi, abscessum}}\n:{{Audio|||nipa=(əb-sēʹ-dō əb-sĕdʹ-ər-ē əb-sĕsʹ-ē əb-sĕsʹ-əm)|{{la-eng-appellatio}}|la}}", LANG, "abscedo")
    ['Class.: /absˈkeːdoː/', 'Eccl.: /apˈʃedo/']
    """

    lines: list[str] = []
    in_section = False
    was_in_section = False
    for line in code.splitlines():
        if line.startswith(("==={", "=== {")):
            in_section = "appellatio" in line.lower()
        elif in_section:
            was_in_section = True
            if "{Audio" in line:
                lines.append(line.strip())
        elif was_in_section:
            break

    if not lines:
        return []

    prons = []
    for line in lines:
        expanded = context.expand(line, LANG)
        expanded = re.sub("<[^>]+>", "", expanded)
        if expanded.startswith(":[[Auxilium"):
            continue

        expanded = expanded.split(" ", 1)[1].strip()
        sep_start, sep_end = ("/", "/") if expanded[0] == "/" else (r"\[", r"\]")
        if not (pronunciations := re.findall(rf"{sep_start}([^{sep_end}]+){sep_end}", expanded)):
            continue

        pron = pronunciations[0]
        if " " in pron and " " not in word:
            pron = pron.split(" ", 1)[0]

        if "(classice)" in expanded:
            prons.append(f"Class.: /{pron}/")
        elif "(ecclesiastice)" in expanded:
            prons.append(f"Eccl.: /{pron}/")
        elif "Auxilium:Appellatio" in expanded and locale == LANG:
            continue
        else:
            prons.append(f"/{pron}/")
    return prons


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("==={{collatae}}===\n*{{la-nx|hilaritās}}\n{{synon}}\n#{{la-nx|hilarē}}", LANG, word="hilariter")
    '==={{collatae}}===\n*{{la-nx|hilaritās}}\n==={{synon}}===\n#{{la-nx|hilarē}}'

    >>> adjust_wikicode("===={{collatae}}====\n{{synon|5}}\n*{{la-nx|labor}}, {{la-nx|labōrātiō}}\n\n===={{trans}}====\n* Anglice: {{t+|en|labour}}", LANG, word="laboratus")
    '===={{collatae}}====\n==={{synon}}===\n#{{la-nx|labor}}, {{la-nx|labōrātiō}}\n===={{trans}}====\n* Anglice: {{t+|en|labour}}'

    >>> adjust_wikicode("==={{collatae}}===\n{{synon}}\n#{{la-nx|exsistō}}\n{{colloc}}\n*[[cogito|Cogito]] [[ergo]] '''sum'''", LANG, word="sum")
    "==={{collatae}}===\n==={{synon}}===\n#{{la-nx|exsistō}}\n==={{colloc}}===\n*[[cogito|Cogito]] [[ergo]] '''sum'''"

    >>> adjust_wikicode("{{caput|la|Quum}}\n=={{-la-|Quum}}==\n\n==={{int:wikt-affines}}===\n* {{la}}: '''quum''' — Alia forma vocis '''[[cum]]''', q.v.", LANG, word="quum")
    '{{caput|la|Quum}}\n=={{-la-|Quum}}==\n==={{int:wikt-affines}}===\n# {{flexion|cum}}'

    >>> _ = context.reset(LANG)

    >>> context.new_word("gero")
    >>> adjust_wikicode("{{la-coniugatio-3|ger|gess|gest|3plPerfIndAct2=gessēre}}", LANG, word="gero")
    '# {{rev-flexion|geram}}\n# {{rev-flexion|geramini}}\n# {{rev-flexion|geramur}}\n# {{rev-flexion|geramus}}\n# {{rev-flexion|gerant}}\n# {{rev-flexion|gerantur}}\n# {{rev-flexion|gerar}}\n# {{rev-flexion|geraris}}\n# {{rev-flexion|geras}}\n# {{rev-flexion|gerat}}\n# {{rev-flexion|geratis}}\n# {{rev-flexion|geratur}}\n# {{rev-flexion|gere}}\n# {{rev-flexion|gerebam}}\n# {{rev-flexion|gerebamini}}\n# {{rev-flexion|gerebamur}}\n# {{rev-flexion|gerebamus}}\n# {{rev-flexion|gerebant}}\n# {{rev-flexion|gerebantur}}\n# {{rev-flexion|gerebar}}\n# {{rev-flexion|gerebaris}}\n# {{rev-flexion|gerebas}}\n# {{rev-flexion|gerebat}}\n# {{rev-flexion|gerebatis}}\n# {{rev-flexion|gerebatur}}\n# {{rev-flexion|geremini}}\n# {{rev-flexion|geremur}}\n# {{rev-flexion|geremus}}\n# {{rev-flexion|gerendi}}\n# {{rev-flexion|gerendus}}\n# {{rev-flexion|gerens}}\n# {{rev-flexion|gerent}}\n# {{rev-flexion|gerentur}}\n# {{rev-flexion|gerere}}\n# {{rev-flexion|gererem}}\n# {{rev-flexion|gereremini}}\n# {{rev-flexion|gereremur}}\n# {{rev-flexion|gereremus}}\n# {{rev-flexion|gererent}}\n# {{rev-flexion|gererentur}}\n# {{rev-flexion|gererer}}\n# {{rev-flexion|gerereris}}\n# {{rev-flexion|gereres}}\n# {{rev-flexion|gereret}}\n# {{rev-flexion|gereretis}}\n# {{rev-flexion|gereretur}}\n# {{rev-flexion|gereris}}\n# {{rev-flexion|geres}}\n# {{rev-flexion|geret}}\n# {{rev-flexion|geretis}}\n# {{rev-flexion|geretur}}\n# {{rev-flexion|geri}}\n# {{rev-flexion|gerimini}}\n# {{rev-flexion|gerimur}}\n# {{rev-flexion|gerimus}}\n# {{rev-flexion|geris}}\n# {{rev-flexion|gerit}}\n# {{rev-flexion|gerite}}\n# {{rev-flexion|geritis}}\n# {{rev-flexion|gerito}}\n# {{rev-flexion|geritor}}\n# {{rev-flexion|geritote}}\n# {{rev-flexion|geritur}}\n# {{rev-flexion|geror}}\n# {{rev-flexion|gerunt}}\n# {{rev-flexion|gerunto}}\n# {{rev-flexion|geruntor}}\n# {{rev-flexion|geruntur}}\n# {{rev-flexion|gesseram}}\n# {{rev-flexion|gesseramus}}\n# {{rev-flexion|gesserant}}\n# {{rev-flexion|gesseras}}\n# {{rev-flexion|gesserat}}\n# {{rev-flexion|gesseratis}}\n# {{rev-flexion|gessere}}\n# {{rev-flexion|gesserim}}\n# {{rev-flexion|gesserimus}}\n# {{rev-flexion|gesserint}}\n# {{rev-flexion|gesseris}}\n# {{rev-flexion|gesserit}}\n# {{rev-flexion|gesseritis}}\n# {{rev-flexion|gessero}}\n# {{rev-flexion|gesserunt}}\n# {{rev-flexion|gessi}}\n# {{rev-flexion|gessimus}}\n# {{rev-flexion|gessisse}}\n# {{rev-flexion|gessissem}}\n# {{rev-flexion|gessissemus}}\n# {{rev-flexion|gessissent}}\n# {{rev-flexion|gessisses}}\n# {{rev-flexion|gessisset}}\n# {{rev-flexion|gessissetis}}\n# {{rev-flexion|gessisti}}\n# {{rev-flexion|gessistis}}\n# {{rev-flexion|gessit}}\n# {{rev-flexion|gestu}}\n# {{rev-flexion|gestum}}\n# {{rev-flexion|gesturum}}\n# {{rev-flexion|gesturus}}\n# {{rev-flexion|gestus}}'

    >>> context.new_word("gero")
    >>> adjust_wikicode("{{la-declinatio-3|ger|ō|genus=m}}", LANG, word="gero")
    '# {{rev-flexion|gerone}}\n# {{rev-flexion|geronem}}\n# {{rev-flexion|gerones}}\n# {{rev-flexion|geroni}}\n# {{rev-flexion|geronibus}}\n# {{rev-flexion|geronis}}\n# {{rev-flexion|geronum}}'
    """
    lines: list[str] = []

    # Workaround for "quick words" (to not say "malformed")
    if "==={{int:wikt-affines}}===\n* {{la}}:" in code:
        in_section = False
        for raw_line in code.splitlines():
            if not (line := raw_line.strip()):
                continue
            if line == "==={{int:wikt-affines}}===":
                in_section = True
            if in_section and line.startswith("*"):
                line = re.sub(r".+\[\[([^\]]+).+", r"# {{flexion|\1}}", line)
            lines.append(line)
        code = "\n".join(lines)

    # Proper section for synonyms + adapt list type
    if "{{synon" in code:
        lines.clear()
        in_section = False
        for raw_line in code.splitlines():
            if not (line := raw_line.strip()):
                continue
            if line.startswith("{{synon"):
                in_section = True
                line = "==={{synon}}==="
            elif in_section:
                if line.startswith("="):
                    in_section = False
                elif line.startswith("{{"):
                    in_section = False
                    line = f"==={line}==="
                elif line.startswith("*"):
                    line = line.replace("*", "#", count=1)
            lines.append(line)
        code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]+\}}\}})"
        lines.clear()

        # Drop the collapsable tables template (`{{collabi|{{la-declinatio-comp|amāri|or}}|caput=''amarus'' comparativus}}`)
        code = code.replace("{{collabi|", "")

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
