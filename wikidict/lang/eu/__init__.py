"""Basque language."""

import re

from ... import context, lang, utils
from ..fr import find_genders  # noqa: F401
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __name__.rsplit(".", 1)[-1]

random_word_url = "https://eu.wiktionary.org/wiki/Berezi:Ausazkoa"

module_trans = "Modulu"
template_trans = "Txantiloi"

section_patterns = (":#", r":\*", "#", r"\*")
section_sublevels = (3, 4)
head_sections = (LANG,)
etyl_section = ("jatorria", "Jatorria")
sections = (
    *etyl_section,
    "adberbio",  # adverb, adverbial phrase
    "aditz",  # verb
    "adizlaguna",  # adverb
    "adjektibo",  # adjective
    "artikulua",  # article
    "atsotitza",  # proverb
    "atzizkia",  # suffix
    "aurrizkia",  # prefix
    "deklinabidea",  # declension
    "erakuslea",  # demonstrative
    "esaldi-lokuzioa",  # sentence
    "interjekzioa",  # interjection
    "izen",  # several POS
    "jokabidea",  # behavior?
    "juntagailua",  # conjunction
    "lokailua",  # conjunction
    "partikula",  # particle
    "preposizio-lokuzioa",  # prepositional phrase
    "sinonimoak",  # synonym
    "zenba",  # quantifier, numerator
)

variant_templates = ("{{flexion",)

reverse_variant_titles = (
    "{{Izen ",
    "{{Hizkuntzen ",
    "{{eu-dekl-izen",
    "{{eu-izen",
    "{{eu-jokab-",
)
reverse_variant_templates = ("{{rev-flexion",)

definitions_to_ignore = (
    "'''Adibidea",  # example
    "Oraindik ez daukagu",  # missing details
    "Zehaztasunak eman",  # provide details
)

PRON_PATTERNS = [
    re.compile(r"(?m)^:\*[ ]*+\{\{IPA\|([^|}]++)"),
    re.compile(r"(?m)^:\*[ ]*+\[\[International Phonetic Alphabet\|IPA\]\]:[ ']*+(?:\{\{Azpimarratu\|)?/([^/]++)"),
    re.compile(r"(?m)^:?\*[ ]*+\[\[International Phonetic Alphabet\|IPA\]\]:[ ]*+/'++([^']++)'''/"),
]


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", LANG)
    []
    >>> find_pronunciations(":* {{IPA|ˈpɔlak}}", LANG)
    ['/ˈpɔlak/']
    >>> find_pronunciations(":* [[International Phonetic Alphabet|IPA]]: '''/ˈpɔlak/'''", LANG)
    ['/ˈpɔlak/']
    >>> find_pronunciations(":* [[International Phonetic Alphabet|IPA]]: /'''ˈpɔlak'''/", LANG)
    ['/ˈpɔlak/']
    >>> find_pronunciations(":* [[International Phonetic Alphabet|IPA]]: '''{{Azpimarratu|/ˈpɔlak/}}'''", LANG)
    ['/ˈpɔlak/']
    """
    pron = next(
        (f"/{item.strip("/'")}/" for pattern in PRON_PATTERNS for item in pattern.findall(code)),
        "",
    )
    return [pron] if pron else []


RE_BASE_FORM = re.compile(r"\[\[([^\]]++)\]\]")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if "hitzaren deklinabide forma" in line and (base_form_raw := RE_BASE_FORM.search(line)):
            base_form = context.expand(base_form_raw[1], LANG).strip().lower()
            line = f"# {{{{flexion|{base_form}}}}}"
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        lines.clear()
        in_tpl = False
        tpl_code = ""
        current_section = ""

        for line in code.splitlines():
            if line.startswith("==="):
                current_section = line

            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

                # Handle cases when the template is in the etymology section:
                # since we do not yet look for variants in those sections, we need to add a falsy one
                if not current_section or any(etyl in current_section for etyl in etyl_section):
                    lines.append("===jokabidea===")

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip().strip("\u200e")
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)
                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    lines.extend(f":# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                lines.append(line)

        code = "\n".join(lines)

    return code
