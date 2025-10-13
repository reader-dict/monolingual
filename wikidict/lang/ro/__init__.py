"""Romanian language."""

import re

from ... import lang, utils
from .langs import langs
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://ro.wiktionary.org/wiki/Special:RandomRootpage"

module_trans = "Modul"
template_trans = "Format"

float_separator = ","
thousands_separator = "."

section_patterns = ("#", r"\*")
section_sublevels = (3,)
head_sections = ("{{limba|ron}}", "{{limba|ro}}", "{{limba|conv}}")
etyl_section = ("{{etimologie}}",)
sections = (
    *etyl_section,
    "{{abr}}",
    "{{abreviere}",
    "{{adjectiv}",
    "{{adjective}",
    "{{adverb}",
    "{{articol}",
    "{{conjuncție}",
    "{{cuvânt compus}",
    "{{expr}}",
    "{{expresie}",
    "{{expresie|ro",
    "{{interjecție}",
    "{{locuțiune adjectivală}",
    "{{locuțiune adverbială}",
    "{{locuțiune}",
    "{{numeral colectiv}",
    "{{numeral}",
    "{{nume propriu}",
    "{{nume propriu|ro",
    "{{nume taxonomic|conv}",
    "{{participiu}",
    "{{prefix}",
    "{{prepoziție}",
    "{{pronume}",
    "{{pronume|ro",
    "{{substantiv}",
    "{{sufix}",
    "{{simbol|conv}",
    "{{unități}}",
    "{{verb auxiliar}",
    "{{verb copulativ}",
    "{{verb predicativ}",
    "{{verb tranzitiv}",
    "{{verb}",
)

variant_titles = tuple(section for section in sections if section not in etyl_section)
variant_templates = (
    "{{adj form of",
    "{{flexion",
)

reverse_variant_titles = (
    "{{adjectiv-",
    "{{substantiv-",
    "{{verb-",
)
reverse_variant_templates = ("{{rev-flexion",)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ro")
    []
    >>> find_genders("{{substantiv-ron|gen={{m}}|nom-sg=câine|nom-pl=câini", "ro")
    ['m']
    >>> find_genders("{{substantiv-ron|gen={{n}}}}", "ro")
    ['n']
    """
    pattern = re.compile(r"gen={{([fmsingp]+)(?: \?\|)*}")
    return utils.unique(utils.flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ro")
    []
    >>> find_pronunciations("{{AFI|/ka.priˈmulg/}}", "ro")
    ['/ka.priˈmulg/']
    >>> find_pronunciations("{{IPA|ro|[fruˈmoʃʲ]}}", "ro")
    ['[fruˈmoʃʲ]']
    """
    res = []
    for pattern in (
        re.compile(r"\{AFI\|(/[^/]+/)(?:\|(/[^/]+/))*"),
        re.compile(rf"\{{IPA\|{locale}\|([^}}]+)"),
    ):
        res.extend(pattern.findall(code))

    return utils.unique(utils.flatten(res))


REV_VARIANTS_IGNORED = {"-", "I", "II", "III", "IV", "V", "VI"}


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{(|adept al liberalismului}}\\n*{{eng}}: {{trad|en|liberal}}\\n{{-}}\\n{{)}}\\nfoo\\n{{bar}}#foo\\n{{(|baz}}\\n*sdf\\n{{)}}", "ro")
    'foo\\n{{bar}}#foo'

    >>> adjust_wikicode("{{-avv-|ANY|ANY}}", "ro")
    '=== {{avv|ANY|ANY}} ==='

    >>> adjust_wikicode("====Verb tranzitiv====", "ro")
    '=== {{Verb tranzitiv}} ==='

    >>> adjust_wikicode("{{-avv-|ron}}", "ro")
    '=== {{avv}} ==='
    >>> adjust_wikicode("{{-avv-|ro}}", "ro")
    '=== {{avv}} ==='

    >>> adjust_wikicode("{{-avv-|ANY}}", "ro")
    '=== {{avv|ANY}} ==='

    >>> adjust_wikicode("{{-avv-}}", "ro")
    '=== {{avv}} ==='

    >>> adjust_wikicode("{{-nume propriu-}}", "ro")
    '=== {{nume propriu}} ==='

    >>> adjust_wikicode("==Romanian==", "ro")
    '== {{limba|ron}} =='

    >>> adjust_wikicode("==Romanian==\\n===Adjective===", "ro")
    '== {{limba|ron}} ==\\n=== {{Adjective}} ==='

    >>> adjust_wikicode("#''forma de feminin singular pentru'' [[frumos]].", "ro")
    '# {{flexion|frumos}}'
    >>> adjust_wikicode("#''formă alternativă pentru'' [[fântânioară]].", "ro")
    '# {{flexion|fântânioară}}'

    >>> adjust_wikicode("{{substantiv-ron\\n|gen={{f}}\\n|nom-sg=piatră\\n|nom-pl=pietre\\n|art-sg=piatra\\n|art-pl=pietrele\\n|dat-sg=pietrei\\n|dat-pl=pietrelor\\n|voc-sg=piatră\\n|voc-pl=pietrelor\\n}}", "ro")
    '# {{rev-flexion|piatra}}\\n# {{rev-flexion|piatră}}\\n# {{rev-flexion|pietre}}\\n# {{rev-flexion|pietrei}}\\n# {{rev-flexion|pietrele}}\\n# {{rev-flexion|pietrelor}}'
    >>> adjust_wikicode("{{adjectiv-ron\\n|m-sg=interocular\\n|m-pl=[[interoculari]]\\n|f-sg=[[interoculară]]\\n|f-pl=interoculare/roof (2)\\n|voc-pl=\\n|voc-sg=electronică<br />electronico\\n}}", "ro")
    '# {{rev-flexion|electronico}}\\n# {{rev-flexion|electronică}}\\n# {{rev-flexion|interocular}}\\n# {{rev-flexion|interoculare}}\\n# {{rev-flexion|interoculari}}\\n# {{rev-flexion|interoculară}}\\n# {{rev-flexion|roof}}'
    >>> adjust_wikicode("{{adjectiv-ron|m-sg=interocular|m-pl=[[interoculari]]|f-sg=[[interoculară]]|f-pl=[[interoculare]]|voc-pl={{inv}}|voc-sg=}}# părul", "ro")
    '# {{rev-flexion|interocular}}\\n# {{rev-flexion|interoculare}}\\n# {{rev-flexion|interoculari}}\\n# {{rev-flexion|interoculară}}\\n# părul'
    """
    locale_3_chars, lang_name = langs[locale]

    # Wipe out `{{(|...}}...{{)}}`
    if "{{(|" in code:
        cleaned: list[str] = []
        in_unwanted_section = False
        for line in code.splitlines():
            if line.startswith("{{(|"):
                in_unwanted_section = True
            elif line.startswith("{{)}}"):
                in_unwanted_section = False
            elif not in_unwanted_section:
                cleaned.append(line)
        code = "\n".join(cleaned)

    # `{{-avv-|ANY|ANY}}` → === `{{avv|ANY|ANY}} ===`
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\|(\w+)\}\}", r"=== {{\1|\2|\3}} ===", code, flags=re.MULTILINE)

    # `====Verb tranzitiv====` → `=== {{Verb tranzitiv}} ===`
    code = re.sub(r"====([^=]+)====", r"=== {{\1}} ===", code)

    # `{{-avv-|ron}}` → `=== {{avv}} ===`
    code = re.sub(rf"^\{{\{{-(.+)-\|({locale}|{locale_3_chars})\}}\}}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # `{{-avv-|ANY}}` → `=== {{avv|ANY}} ===`
    code = re.sub(r"^\{\{-(.+)-\|(\w+)\}\}", r"=== {{\1|\2}} ===", code, flags=re.MULTILINE)

    # `{{-avv-}}` → `=== {{avv}} ===`
    # `{{-nume propriu-}}` → `=== {{nume propriu}} ===`
    code = re.sub(r"^\{\{-([\w ]+)-\}\}", r"=== {{\1}} ===", code, flags=re.MULTILINE)

    # Try to convert old Wikicode
    if f"=={lang_name}==" in code:
        # `==Romanian==` → `== {{limba|ron}} ==`
        code = code.replace(f"=={lang_name}==", f"== {{{{limba|{locale_3_chars}}}}} ==")

        # `===Adjective===` → `=== {{Adjective}} ===`
        code = re.sub(r"===(\w+)===", r"=== {{\1}} ===", code)

    #
    # Variants
    #

    # `#''forma de feminin singular pentru'' [[frumos]].` → `# {{flexion|frumos}}`
    # `#''formă alternativă pentru'' [[fântânioară]].` → `# {{flexion|fântânioară}}`
    code = re.sub(
        r"^#\s*'+(?:forma de|formă) [^']+'+\s*'*\[\[([^\]]+)\]\]'*\.?",
        r"# {{flexion|\1}}",
        code,
        flags=re.MULTILINE,
    )

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            line = line.strip()
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code, rest = tpl_code.rsplit("}}", 1)
                    forms: set[str] = set()
                    for form in re.findall(r"=([^|{}]+)", tpl_code):
                        if "(" in form:
                            form = form.split("(", 1)[0]
                        if "<br" in form:
                            form = re.sub(r"<br\s?/?>", "/", form)
                        if "/" in form:
                            for sform in form.split("/"):
                                forms.add(sform.strip("[]").strip())
                        else:
                            forms.add(form.strip("[]").strip())
                    for discard in REV_VARIANTS_IGNORED:
                        forms.discard(discard)
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms))
                    if rest:
                        cleaned.append(rest)
                    tpl_code = ""
                continue

            cleaned.append(line)

        code = "\n".join(cleaned)

    return code
