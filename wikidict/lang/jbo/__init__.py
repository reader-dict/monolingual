"""Lojban language."""

import re

from ... import lang, utils
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://jbo.wiktionary.org/wiki/rirci:Random"

template_trans = "termo'a"

float_separator = ","
thousands_separator = " "

head_sections = ("lojbo", "{{jbo}}", "{{bau|jbo}}", "sorbau", "{{mul}}", "{{bau|mul}}")
etyl_section = ("vlakra",)
sections = (
    *etyl_section,
    "cmavo",  # particle?
    "cmebasti",  # ?
    "cmene",  # name
    "daivla",  # foreign word?
    "fasnyvla",  # example?
    "gismu",  # root?
    "jdima'o",  # ?
    "lujvo",  # word?
    "rafsi",  # abbreviation?
    "skivla",  # adjective
    "smudu'i",  # ?
    "snile'u",  # ?
    "sumtcita",  # ?
    "sumvla",  # ?
)

reverse_variant_titles = ("{{jbo-gismu",)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = ("{{???}}",)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "jbo")
    []
    >>> find_pronunciations("{{gykyvysym.|/ˈfor.ʃa/|bau=jbo}}", "jbo")
    ['/ˈfor.ʃa/']
    """
    pattern = re.compile(r"\{\{gykyvysym.\|/([^/]+)/")
    return [f"/{pron}/" for pron in utils.unique(pattern.findall(code))]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    #
    # Reverse variants
    #

    lines: list[str] = []
    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    lines.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                lines.append(line)

        code = "\n".join(lines)

    return code
