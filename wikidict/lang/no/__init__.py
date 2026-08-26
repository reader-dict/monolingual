"""Norwegian language."""

import re

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://no.wiktionary.org/wiki/Spesial:Tilfeldig_rotside"

module_trans = "Modul"
template_trans = "Mal"

float_separator = ","
thousands_separator = " "

head_sections = ("norsk",)
section_sublevels = (3, 4)
etyl_section = ("etymologi",)
sections = (
    *etyl_section,
    "adjektiv",
    "adverb",
    "artikkel",
    "egennavn",
    "forklaring",
    "forkortelse",
    "frase",
    "grammatikk",
    "idiom",
    "initialord",
    "interjeksjon",
    "konjunksjon",
    "ordklasse",
    "ordtak",
    "prefiks",
    "preposisjon",
    "pronomen",
    "subjektiv",
    "subjunksjon",
    "substantiv",
    "suffiks",
    "synonymer",
    "tallord",
    "verb",
)

variant_templates = (
    "{{bøyingsform",
    "{{bøyningsform",
    "{{no-adj-bøyningsform",
    "{{no-sub-bøyningsform",
    "{{no-verbform av",
    "{{no-verb-bøyningsform",
)

reverse_variant_titles = (
    "{{Adj-",
    "{{nb-adj-",
    "{{nn-adj-",
    "{{no-adj-",
    "{{nb-sub-",
    "{{nn-sub-",
    "{{no-sub-",
    "{{nb-verb-",
    "{{nn-verb-",
    "{{no-verb-",
)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{?",
    "{{audio",
    "{{definisjon mangler",
    "{{etymologi mangler",
    "{{Etymologi mangler",
    "{{mangler definisjon",
    "{{mangler etymologi",
    "{{o-ennå",  # translation table
    "{{opprydning",  # to clean
    "{{sitat",  # quote
    "{{trenger referanse",  # reference needed
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "no")
    []
    >>> find_genders("{{no-sub|m}}", "no")
    ['m']
    >>> find_genders("{{no-sub|mf}}", "no")
    ['mf']
    >>> find_genders("{{nn-sub|f}}", "no")
    ['f']
    >>> find_genders("{{nb-sub|m}}", "no")
    ['m']
    >>> find_genders("{{no-sub|nb=f|nn=f}}", "no")
    ['f']
    """
    for pattern in [
        re.compile(r"{{n[bon]-sub\|(\w+)}}"),
        re.compile(r"{{n[bon]-sub\|\w+=(\w+)"),
    ]:
        if genders := pattern.findall(code):
            return utils.unique(utils.flatten(genders))
    return []


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "no")
    []
    >>> find_pronunciations("{{IPA|/ɡrœn/|[grøn:]|språk=no}}", "no")
    ['/ɡrœn/', '[grøn:]']
    >>> find_pronunciations("{{IPA|[anomali:´]|språk=no}}", "no")
    ['[anomali:´]']
    >>> find_pronunciations("{{IPA|['klɑɾ]||['kɽɑɾ] (tykk ''L'' (østnorsk)|språk=no}}", "no")
    ["['klɑɾ]"]
    """
    pattern = re.compile(r"{{\s*IPA\s*\|[^\}]*}}")
    result: list[str] = []
    for f in pattern.findall(code):
        fsplit = f.split("|")
        for fs in fsplit:
            if not fs:
                continue
            if (fs[0] == "[" and fs[-1] == "]") or (fs[0] == "/" and fs[-1] == "/"):
                result.append(fs)
    return result


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: assign-if-exp, inline-immediately-returned-variable, reintroduce-else
    r"""
    >>> adjust_wikicode("==Norsk==\n----", "no")
    '==Norsk==\n'

    >>> adjust_wikicode("==Norsk==\n<includeonly>\n{{rfscript|und|sc=Deva}}, <br /></includeonly>", "no")
    '==Norsk==\n'

    >>> adjust_wikicode("====Synonymer====\n{{topp|Synonymer}}\n*[[utgave]]\n*[[tapning]]\n*[[variant]] (særlig språk)\n{{midt}}\n*[[type]]\n*[[tolkning]]\n{{bunn}}", "no", word="versjon")
    '====Synonymer====\n#[[utgave]]\n#[[tapning]]\n#[[variant]] (særlig språk)\n#[[type]]\n#[[tolkning]]'

    >>> from ... import context
    >>> _ = context.reset("no")

    >>> context.new_word("sinn")
    >>> adjust_wikicode("{{no-sub-n1}}", "no", word="sinn")
    '# {{rev-flexion|sinna}}\n# {{rev-flexion|sinnene}}\n# {{rev-flexion|sinnet}}'

    >>> context.new_word("økning")
    >>> adjust_wikicode("{{nb-sub-f1}}", "no", word="økning")
    '# {{rev-flexion|økninga}}\n# {{rev-flexion|økningen}}\n# {{rev-flexion|økningene}}\n# {{rev-flexion|økninger}}'

    >>> context.new_word("smøre")
    >>> adjust_wikicode("{{nb-verb-rad||smører|smurte|smurt|imperativ=smør|presp=smørende|passiv=smøres}}", "no", word="smøre")
    '# {{rev-flexion|smurt}}\n# {{rev-flexion|smurte}}\n# {{rev-flexion|smør}}\n# {{rev-flexion|smørende}}\n# {{rev-flexion|smører}}\n# {{rev-flexion|smøres}}'

    >>> context.new_word("daud")
    >>> adjust_wikicode("{{Adj-rad-generisk|daud|daud|daudt|daude|daude|kontekst=nynorsk}}", "no", word="daud")
    '# {{rev-flexion|daude}}\n# {{rev-flexion|daudt}}'

    >>> context.new_word("daud")
    >>> adjust_wikicode("{{nn-adj-grad-normal}}", "no", word="daud")
    '# {{rev-flexion|daudare}}\n# {{rev-flexion|daudast}}'

    >>> context.new_word("ete")
    >>> adjust_wikicode("{{nn-verb-rad|infinitiv=eta|presens=et|perfektum=ete}}", "no", word="ete")
    '# {{rev-flexion|et}}\n# {{rev-flexion|eta}}'
    """
    code = code.replace("----", "")

    # <includeonly>...</includeonly> → ''
    code = re.sub(r"(<includeonly>.+</includeonly>)", "", code, flags=re.DOTALL | re.MULTILINE)

    # Synonyms
    if "Synonymer" in code:
        lines: list[str] = []
        in_section = False
        code = code.replace("{{topp|Synonymer}}", "").replace("{{midt}}", "").replace("{{bunn}}", "")
        for raw_line in code.splitlines():
            if not (line := raw_line.strip()):
                continue
            if line.startswith("===") and "Synonymer" in line:
                in_section = True
            elif in_section:
                if line.startswith("{{"):
                    line = f"# {line}".rstrip("<br>")
                elif line.startswith("*"):
                    line = line.replace("*", "#", count=1)
                else:
                    in_section = False
            lines.append(line)
        code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code = tpl_code.rsplit("}}", 1)[0]
                    tpl_code += "}}"
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip()
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)
                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
