"""Ukranian language."""

import re

from ... import lang, utils
from ..ru import extract_templates
from . import variant_handlers as variant_handlers_mod
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://uk.wiktionary.org/wiki/%D0%A1%D0%BF%D0%B5%D1%86%D1%96%D0%B0%D0%BB%D1%8C%D0%BD%D0%B0:%D0%92%D0%B8%D0%BF%D0%B0%D0%B4%D0%BA%D0%BE%D0%B2%D0%B0_%D1%81%D1%82%D0%BE%D1%80%D1%96%D0%BD%D0%BA%D0%B0"

module_trans = "Модуль"
template_trans = "Шаблон"

float_separator = ","
thousands_separator = " "

section_level = 1
section_sublevels = (3, 4)
head_sections = ("uk", "mul")
etyl_section = ("етимологія",)
sections = (
    *etyl_section,
    "значення",  # meaning
    "морфосинтаксичні ознаки",  # morphosyntactic features
    "синоніми",  # synonyms
)

variant_templates = ("{{змп",)

reverse_variant_templates = ("{{rev-flexion",)
reverse_variant_titles = (
    "{{дієсл uk",
    "{{дієприкм uk",
    "{{імен uk",
)

templates_ignored = (
    "{{приклад",  # example
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "uk")
    []
    >>> find_genders("{{імен uk 3a m una|склади={{склади|аль|бо́м|чик}}|альбо́мчик|альбо́мчик|альбо́мчик}}", "uk")
    ['ч']
    >>> find_genders("{{імен uk 4a pl una|склади={{склади|аль|бо́м|чик}}|альбо́мчик|альбо́мчик|альбо́мчик}}", "uk")
    ['мн']
    """
    # https://uk.wiktionary.org/wiki/Категорія:Шаблони_словозміни/uk/Іменники
    pattern = re.compile(rf"\{{\{{імен.{locale}.\w+.([fmnplмжс]+)")
    return utils.unique(
        [
            {
                "f": "ж",
                "m": "ч",
                "n": "c",
                "pl": "мн",
            }.get(gender, gender)
            for gender in utils.flatten(pattern.findall(code))
        ]
    )


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from ... import context
    >>> _ = context.reset("uk")

    >>> find_pronunciations("", "uk")
    []

    >>> context.new_word("Бобрик")
    >>> find_pronunciations("{{transcription-uk|Бо́брик}}", "uk")
    ['[ˈbɔbrek]']
    >>> find_pronunciations("{{transcription|ˈbɔbrek}}", "uk")
    ['[ˈbɔbrek]']
    >>> find_pronunciations("{{transcriptions-uk|}}", "uk")
    ['[bɔbrek]']
    """
    from ... import context

    pattern = re.compile(rf"(\{{\{{transcriptions?(?:-{locale})?[^}}]+}}}})")
    res: set[str] = set()
    for tpl in pattern.findall(code):
        res.update(re.findall(r"&#91;([^&]+)&#93;", context.expand(tpl, "uk")))
    return sorted(f"[{pron}]" for pron in res)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("=uk=\n'''Адсóрбція''': ракцією.", "uk")
    '=uk=\n====значення====\n# ракцією.'
    >>> adjust_wikicode("=uk=\n'''Адсóрбція''' — ракцією.", "uk")
    '=uk=\n====значення====\n# ракцією.'
    >>> adjust_wikicode("=uk=\n'''Адсóрбція''' – ракцією.", "uk")
    '=uk=\n====значення====\n# ракцією.'
    >>> adjust_wikicode("=uk=\n'''Адсóрбція''' - ракцією.", "uk")
    '=uk=\n====значення====\n# ракцією.'

    >>> adjust_wikicode("=uk=\n==== Значення ====\n# [[пристрій]]\n==== Синоніми ====\n# —\n# —", "uk")
    '=uk=\n==== Значення ====\n# [[пристрій]]\n==== Синоніми ====\n\n'
    """
    # Delete empty synonyms
    code = re.sub(r"^#[ ]*(?:—|-|\?)[ ]*$", "", code, flags=re.MULTILINE)

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
                    tpl_code = extract_templates(tpl_code)[0]
                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip().replace("''", "")
                    tpl_name = re.sub(r"[ ]{2,}", " ", tpl_name).rstrip("\u200e")
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)

                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    cleaned.append(f"{{{{{tpl_name}|}}}}")  # This is required for genders finding
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    if "#" not in code:
        lines = [line for raw_line in code.strip().splitlines() if (line := raw_line.strip())]
        if len(lines) > 1 and lines[0].startswith("=") and not lines[1].startswith(("#", "=")):
            code = "\n".join(
                [
                    lines[0],
                    "====значення====",
                    f"""# {re.sub(r"^'+[^']+'+[: –—\-]*", "", lines[1], flags=re.MULTILINE)}""",
                ]
            )

    return code
