"""Bulgarian language."""

import re

from .variant_handlers import handlers as variant_handlers  # noqa: F401

LANG = __file__.rsplit("/", 2)[-2]

random_word_url = "https://bg.wiktionary.org/wiki/%D0%A1%D0%BF%D0%B5%D1%86%D0%B8%D0%B0%D0%BB%D0%BD%D0%B8:%D0%A1%D0%BB%D1%83%D1%87%D0%B0%D0%B9%D0%BD%D0%B0_%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"

module_trans = "Модул"
template_trans = "Шаблон"

section_level = 1
section_sublevels = (2, 3)
head_sections = ("{{-bg-}}",)
etyl_section = ("етимология",)
sections = (
    *etyl_section,
    # https://bg.wiktionary.org/wiki/Уикиречник:Шаблони
    "съкращение",  # abbreviation
    "abbr",
    "прилагателно име",  # adjective
    "adj",
    "наречие",  # adverb
    "adv",
    "съществително нарицателно име",  # common noun
    "член",  # article
    "art",
    "съюз",  # conjunction
    "con",
    "детерминатив",  # determiner
    "determiner",
    "израз",  # expression
    "expr",
    "идиоматичен израз",  # idiomatic expression
    "idiom",
    "междуметие",  # interjection
    "inter",
    "съществително име",  # noun
    "noun",
    "числително име",  # numeral
    "num",
    "частица",  # particle
    "part",
    "словосъчетание",  # phrase
    "phrase",
    "фразеологични изрази",  # phraseological expressions
    "представка",  # prefix
    "pref",
    "предлог",  # preposition
    "prep",
    "местоимение",  # pronoun
    "pron",
    "съществително собствено име",  # proper noun
    "prop",
    # "Буква",  # letter, see #2634
    # "letter",  # See #2634
    "значение",  # meaning
    "синоними",  # synonyms
    "наставка",  # suffix
    "suffix",
    "synonyms",
    "глагол",  # verb
    "verb",
)

variant_templates = ("{{flexion",)

definitions_to_ignore = (
    "Значението на думата все още не е въведено",  # definition missing
)

templates_ignored = (
    "{{бързо}",  # asked for removal
)


GENDERS = {
    "cp": "cp",
    "среден": "cp",
    "f": "ж",
    "m": "м",
    "м": "м",
    "мъжки": "м",
    "n": "cp",
    "женски": "ж",
    "ж": "ж",
}


def find_genders(code: str, locale: str) -> list[str]:
    r"""
    >>> find_genders("", LANG)
    []
    >>> find_genders("===род===\n==foo==", LANG)
    []
    >>> find_genders("===род===\n-", LANG)
    []
    >>> find_genders("===род===\nМ", LANG)
    ['м']
    >>> find_genders("===род===\nсреден", LANG)
    ['cp']
    >>> find_genders("===род===\nж", LANG)
    ['ж']
    >>> find_genders("===род===\nж\n===род===\nж", LANG)
    ['ж']
    """
    if (gender_raw := re.search(r"===род===\n(\w++)", code)) and (gender := GENDERS.get(gender_raw[1].lower().strip())):
        return [gender]
    return []


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("{{МФА|[ei]|bg}}", LANG)
    ['/ei/']
    >>> find_pronunciations("{{МФА|/ei/|bg}}", LANG)
    ['/ei/']
    """
    return sorted(f"/{pron}/" for pron in set(re.findall(rf"\{{\{{МФА\|.(.*?).\|{locale}\}}\}}", code)))


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # Change synonyms list type
    lines: list[str] = []
    in_section = False
    for line_ in code.splitlines():
        if not (line := line_.strip()):
            continue
        if line.startswith("==="):
            in_section = "синоними" in line or "synonyms" in line
        if in_section and line.startswith("*"):
            line = line.replace("*", "#", count=1)
        lines.append(line)
    code = "\n".join(lines)

    #
    # Variants
    #

    if "{{Форма|" in code:
        bases: set[str] = set()
        for base_form_raw in re.findall(r"ОСНОВНА ФОРМА =([^\n]++)", code):
            if base_form := base_form_raw.strip():
                bases.add(base_form)
        if bases:
            code += "\n===noun==="
            for base in bases:
                code += f"\n# {{{{flexion|{base}}}}}"

    return code
