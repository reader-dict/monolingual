"""Czesh language."""

import re

from ... import lang
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://cs.wiktionary.org/wiki/Speci%C3%A1ln%C3%AD:N%C3%A1hodn%C3%A1_str%C3%A1nka"

module_trans = "Modul"
template_trans = "Šablona"

float_separator = ","
thousands_separator = " "

section_sublevels = (3, 4)
head_sections = ("čeština",)
etyl_section = ("etymologie",)
sections = (
    *etyl_section,
    "časování",  # timing? (for reverse variants)
    "částice",  # particle
    "číslo",  # number
    "číslovka",  # numeral
    "citoslovce",  # interjection
    "idiom",
    "předložka",  # preposition
    "předpona",  # prefix
    "přídavné jméno",  # adjective
    "přípona",  # suffix
    "příslovce",  # adverb
    "přísloví",  # proverb
    "skloňování",  # declension (for reverse variants)
    "sloveso",  # verb
    "spojka",  # conjunction
    "stupňování",  # gradation (for reverse variants)
    "symbol",
    "synonyma",
    "význam",  # meaning
    "zájmeno",  # pronoun
    "zkratka",  # abbreviation
    "značka",  # mark
)

variant_templates = ("{{flexion",)

reverse_variant_templates = ("{{rev-flexion",)
reverse_variant_titles = (
    "{{Adjektivum (cs)",
    "{{Zájmeno (cs)",
    "{{Sloveso (cs)",
    "{{Stupňování (cs)",
    "{{Substantivum (cs)",
)

templates_ignored = (
    "{{chybí zdroj",  # source missing
    "{{Doplnit zdroj",  # source missing
    "{{Doplňte zdroj",  # source missing
    "{{Nedostupný zdroj",  # source unavailable
    "{{Pracuje se",  # work in progress
    "{{Překlady",  # translations
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "cs")
    []
    >>> find_pronunciations("{{IPA|patɔliːzaluːf}}", "cs")
    ['[patɔliːzaluːf]']
    """
    res = set(re.findall(r"\{\{IPA\|([^}]+)", code))
    return sorted(f"[{pron}]" for pron in res)


VAR_PATTERNS = [
    re.compile(r"^#[ ']*.+ (?:plurálu|singuláru) substantiva \[\[([^\]#]+).*", flags=re.IGNORECASE),
    re.compile(
        r"^#[ ']*.+ (?:čísla|číslo).+(?:adjektiva|číslovky|jména|jnéna|podstata|přídavného|propria|psoun|rodu|slova|slovesa|sloveso|spojení|substantiva|zájmena|způsobu)'* \[\[([^\]#]+).*",
        flags=re.IGNORECASE,
    ),
]

REV_VAR_RPL = {
    "{{f}}",
    "(hov.)",
    "(hovor.)",
    "(hovorově)",
    "{{m}}",
    "(nářečně)",
    "(nářečně na Moravěé)(neživotný)",
    "pouze životný",
    "(ve funkci předmětu)",
    "(zastarale)",
    "(životný)",
    "(zřídka)",
    "<sup>*</sup>",
    "<sup>**</sup>",
}


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("# ''vokativ jednotného čísla podstatného jména [[mela]]''", "cs")
    '# {{flexion|mela}}'
    >>> adjust_wikicode("# ''genitiv množného čísla podstatného jména [[mela]]''", "cs")
    '# {{flexion|mela}}'
    >>> adjust_wikicode("# ''rozkazovací způsob druhé osoby jednotného čísla slovesa [[mela]]''", "cs")
    '# {{flexion|mela}}'
    >>> adjust_wikicode("# ''akuzativ plurálu substantiva [[mela]]''", "cs")
    '# {{flexion|mela}}'
    >>> adjust_wikicode("# ''první osoba jednotného čísla budoucího času oznamovacího způsobu slovesa [[vypadat#sloveso (2)|vypadat]] (2)''", "cs")
    '# {{flexion|vypadat}}'
    >>> adjust_wikicode("# ''nominativ množného čísla rodu mužského životného přídavného jména [[popřený]]''", "cs")
    '# {{flexion|popřený}}'
    >>> adjust_wikicode("# ''vokativ množného čísla rodu mužského životného přídavného jména [[popřený]]''", "cs")
    '# {{flexion|popřený}}'
    >>> adjust_wikicode("# ''množné číslo mužského životného rodu minulého činného příčestí slovesa [[mrskat]]", "cs")
    '# {{flexion|mrskat}}'
    >>> adjust_wikicode("# ''dativ množného čísla podstatného jména'' [[bor]]", "cs")
    '# {{flexion|bor}}'

    >>> adjust_wikicode("{{Substantivum (cs)\n  | snom = [[skanzen]] / [[skanzen2]]\n  | pins = [[skanzeny]]\n}}", "cs")
    '# {{rev-flexion|skanzen}}\n# {{rev-flexion|skanzen2}}\n# {{rev-flexion|skanzeny}}'
    >>> adjust_wikicode("{{Substantivum (cs)\n  | snom = skanzen / skanzen2\n  | pins = (zastarale) skanzeny<sup>*</sup>\n}}", "cs")
    '# {{rev-flexion|skanzen}}\n# {{rev-flexion|skanzen2}}\n# {{rev-flexion|skanzeny}}'
    >>> adjust_wikicode("{{Substantivum (cs)\n  | snom = skanzen (''hovorově:'' skanzen2)\n  | pins = [[skanzeny]]\n}}", "cs")
    '# {{rev-flexion|skanzen}}\n# {{rev-flexion|skanzen2}}\n# {{rev-flexion|skanzeny}}'
    >>> adjust_wikicode("{{Substantivum (cs)\n  | snom = skanzen / skanzen2\n  | pins = skanzeny\n  | mtra = skrýt\n}}", "cs")
    '# {{rev-flexion|skanzen}}\n# {{rev-flexion|skanzen2}}\n# {{rev-flexion|skanzeny}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | spre1 = [[vopiju se]] /<br /> {{Příznak2|spis. skl.|okaz.}} {{Potenciálně|vopiji se}}\n}}", "cs")
    '# {{rev-flexion|vopiju se}}\n# {{rev-flexion|vopiji se}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | sloc = samopalníku <br /> samopalníkovi\n}}", "cs")
    '# {{rev-flexion|samopalníku}}\n# {{rev-flexion|samopalníkovi}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | mtram = utrh(nuv)\n  | mtraf = utrh(nuv)ši\n}}", "cs")
    '# {{rev-flexion|utrh}}\n# {{rev-flexion|utrhnuv}}\n# {{rev-flexion|utrhši}}\n# {{rev-flexion|utrhnuvši}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | pgen = [[kaleb]] ([[kalb]])\n}}", "cs")
    '# {{rev-flexion|kaleb}}\n# {{rev-flexion|kalb}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | sloc = [[Londýně]] / (ve funkci předmětu) [[Londýnu]]\n}}", "cs")
    '# {{rev-flexion|Londýně}}\n# {{rev-flexion|Londýnu}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | pgen = [[kameníček#podstatné jméno (3)|kameníček]]\n}}", "cs")
    '# {{rev-flexion|kameníček}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | pnom = Singapuřané / (''hovorově:'' Singapuřani)\n}}", "cs")
    '# {{rev-flexion|Singapuřané}}\n# {{rev-flexion|Singapuřani}}'
    >>> adjust_wikicode("{{Sloveso (cs)\n  | acc = [[toho]] {{Upřesnění|životný}}/<br />ten {{Upřesnění|neživotný}}\n}}", "cs", word="ten")
    '# {{rev-flexion|toho}}'
    """
    # Delete empty synonyms
    code = re.sub(r"^#[ ]*(?:—|–|-|\?)[ ]*$", "", code, flags=re.MULTILINE)

    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if line.startswith("#"):
            for pattern in VAR_PATTERNS:
                line, count = pattern.subn(r"# {{flexion|\1}}", line, count=1)
                if count:
                    break
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_tpl = False

        for raw_line in code.splitlines():
            if (line := raw_line.strip()).startswith(interesting_reverse_variant_titles):
                in_tpl = True
            elif in_tpl:
                if line == "}}":
                    in_tpl = False
                    continue
                elif "=" not in line or "= skrýt" in line or "= ano" in line:
                    continue

                line = re.sub(r"\{\{(?:Doplňte|Příznak|#tag|Upřesnění)[^}]+\}\}", "", line)
                line = re.sub(r"<br[ ]+/>", "<br/>", line)

                _, rest = line.split("=", 1)
                for rpl in REV_VAR_RPL:
                    rest = rest.replace(rpl, "")

                if "<br/>" in rest:
                    rest, count = re.subn(r"<br/> +\{\{Potenciálně\|([^}]+)\}\}", r"\1", rest, count=1)
                    if not count:
                        rest = rest.replace("<br/>", "/")

                if "(nuv)" in rest:
                    rest = "/".join([rest.replace("(nuv)", ""), rest.replace("(", "").replace(")", "")])
                elif "(ještě)" in rest:
                    rest = "/".join([rest.replace("(ještě)", ""), rest.replace("(", "").replace(")", "")])

                if "/" in rest:
                    raw_forms = rest.split("/")
                elif "hovorově:" in line:
                    raw_forms = rest.split("(''hovorově:''", 1)
                else:
                    raw_forms = [rest]

                forms = []
                for raw_form in raw_forms:
                    form = raw_form.strip(" {}[]()':")
                    if not form or form == "—":
                        continue
                    if "]] ([[" in form:
                        forms.extend(form.split("]] ([["))
                    elif "#" in form:
                        forms.append(form.split("#", 1)[0])
                    elif "hovorově:" in form:
                        forms.append(form.split(" ", 1)[1])
                    else:
                        forms.append(form)

                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in forms if form != word)
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
