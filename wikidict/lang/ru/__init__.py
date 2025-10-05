"""Russian language."""

import re

from ... import utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://ru.wiktionary.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:RandomRootpage"

module_trans = "Модуль"
template_trans = "Шаблон"

float_separator = ","
thousands_separator = " "

section_level = 1
section_sublevels = (3, 4)
head_sections = ("{{-ru-}}",)
etyl_section = ("этимология",)
sections = (
    *etyl_section,
    "значение",
    "{{значение}}",
    "семантические свойства",
    "{{семантические свойства}}",
    "морфологические и синтаксические свойства",
    "как самостоятельный глагол",  # for verbs with aux
    "в значении вспомогательного глагола или связки",  # for verbs with aux
)

variant_titles = ("значение", "морфологические и синтаксические свойства")
variant_templates = ("{{прич.",)

reverse_variant_templates = ("{{rev-flexion",)
reverse_variant_titles = ("{{сущ ru", "{{прил ru")

templates_ignored = (
    "{{?",
    "{{anim",
    "{{DEFAULTSORT",
    "{{improve",
    "{{Lacuna",
    "{{lacuna",
    "{{offensive",
    "{{unfinished",
    "{{wikipedia",
    "{{пример",  # example
    "{{Цитата",  # citation
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ru")
    []
    >>> find_genders("{{сущ ru f ina 5a|основа=страни́ц|слоги={{по-слогам|стра|ни́|ца}}}}", "ru")
    ['ж']
    """
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    pattern: re.Pattern[str] = re.compile(rf"(?:\{{сущ.{locale}.)([fmnмжс])|(?:\{{сущ.{locale}.*\|)([fmnмжс])")
    return utils.unique(
        [
            {
                "f": "ж",
                "m": "м",
                "n": "cp",
            }.get(gender, gender)
            for gender in utils.flatten(pattern.findall(code))
        ]
    )


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from ... import context
    >>> _ = context.reset("ru")
    >>> context.new_word("word")

    >>> find_pronunciations("", "ru")
    []
    >>> find_pronunciations("{{transcriptions-ru|страни́ца|страни́цы|Ru-страница.ogg}}", "ru")
    ['[strɐˈnʲit͡sə]', '[strɐˈnʲit͡sɨ]']
    """
    from ... import context

    pattern = re.compile(rf"(\{{\{{transcriptions-{locale}[^}}]+}}}})")
    res: set[str] = set()
    for tpl in pattern.findall(code):
        res.update(re.findall(r"&#91;([^&]+)&#93;", context.expand(tpl, locale)))
    return sorted(f"[{pron}]" for pron in res)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> from ... import context
    >>> _ = context.reset("ru")
    >>> context.new_word("word")

    >>> adjust_wikicode("= {{-ru-}} =\\n{{сущ ru m a 2b|основа=коро́л|основа1=корол}}", "ru")
    '= {{-ru-}} =\\n{{сущ ru m a 2b|}}\\n# {{rev-flexion|коро́ль}}\\n# {{rev-flexion|короле́}}\\n# {{rev-flexion|короле́й}}\\n# {{rev-flexion|короли́}}\\n# {{rev-flexion|королю́}}\\n# {{rev-flexion|короля́}}\\n# {{rev-flexion|короля́м}}\\n# {{rev-flexion|короля́ми}}\\n# {{rev-flexion|короля́х}}\\n# {{rev-flexion|королём}}'
    >>> adjust_wikicode("= {{-ru-}} =\\n{{сущ ru m a 2b\\n|основа=коро́л\\n|основа1=корол\\n|слоги={{по-слогам|ко|ро́ль}}\\n}}", "ru")
    '= {{-ru-}} =\\n{{сущ ru m a 2b|}}\\n# {{rev-flexion|коро́ль}}\\n# {{rev-flexion|короле́}}\\n# {{rev-flexion|короле́й}}\\n# {{rev-flexion|короли́}}\\n# {{rev-flexion|королю́}}\\n# {{rev-flexion|короля́}}\\n# {{rev-flexion|короля́м}}\\n# {{rev-flexion|короля́ми}}\\n# {{rev-flexion|короля́х}}\\n# {{rev-flexion|королём}}'
    >>> adjust_wikicode("= {{-ru-}} =\\n{{прил ru 1*a\\n|основа=бессу́дорожн\\n|основа1=\\n|тип=\\n|слоги={{по-слогам|бес|су́|до|рож|ный}}\\n|степень=\\n|краткая=\\n|коммент=\\n|дореф=\\n}}\\n\\n{{слобр|ru|судорожный|{{выдел|бес}} + судорожный|п|и=}}\\n{{морфо-ru|бес-|судорож|-н|+ый}}", "ru")
    '= {{-ru-}} =\\n{{прил ru 1*a|}}\\n# {{rev-flexion|бессу́дорожна}}\\n# {{rev-flexion|бессу́дорожная}}\\n# {{rev-flexion|бессу́дорожно}}\\n# {{rev-flexion|бессу́дорожного}}\\n# {{rev-flexion|бессу́дорожное}}\\n# {{rev-flexion|бессу́дорожной}}\\n# {{rev-flexion|бессу́дорожном}}\\n# {{rev-flexion|бессу́дорожному}}\\n# {{rev-flexion|бессу́дорожною}}\\n# {{rev-flexion|бессу́дорожную}}\\n# {{rev-flexion|бессу́дорожны}}\\n# {{rev-flexion|бессу́дорожные}}\\n# {{rev-flexion|бессу́дорожный}}\\n# {{rev-flexion|бессу́дорожным}}\\n# {{rev-flexion|бессу́дорожными}}\\n# {{rev-flexion|бессу́дорожных}}\\n\\n{{слобр|ru|судорожный|{{выдел|бес}} + судорожный|п|и=}}\\n{{морфо-ru|бес-|судорож|-н|+ый}}'
    """

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = (
        reverse_variant_titles
        if locale == "ru"
        else tuple(tpl.replace(" ru", f" {locale}") for tpl in reverse_variant_titles)
    )
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_expected_section = False
        expected_section = (f"= {{{{-{locale}-}}", f"={{{{-{locale}-}}")
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            line = line.strip()
            if not in_expected_section:
                if line.startswith(expected_section):
                    in_expected_section = True
            elif line.startswith(("= {", "={")):
                in_expected_section = False

            if not in_expected_section:
                continue

            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    tpl_code, rest = tpl_code.rsplit("}}", 1)
                    if not rest:
                        tpl_code += "}}"
                    tpl_name = tpl_code[2 : tpl_code.find("|")].strip()
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
                    if rest:
                        cleaned.append(rest)
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code
