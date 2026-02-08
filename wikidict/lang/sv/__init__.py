"""Swedish language."""

import re

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://sv.wiktionary.org/wiki/Special:RandomRootpage"

module_trans = "Modul"
template_trans = "Mall"

float_separator = ","
thousands_separator = " "

# https://sv.wiktionary.org/wiki/Wiktionary:Stilguide#Ordklassrubriken
head_sections = ("svenska",)
sections = (
    "adjektiv",
    "adverb",
    "affix",
    "artikel",
    "efterled",
    "förkortning",
    "förled",
    "interjektion",
    "konjunktion",
    "possessivt pronomen",
    "postposition",
    "prefix",
    "preposition",
    "pronomen",
    "substantiv",
    "suffix",
    "verb",
    "verbpartikel",
)

variant_titles = (
    "adjektiv",
    "adverb",
    "substantiv",
    "verb",
)
variant_templates = (
    "{{avledning",
    "{{böjning",
)

reverse_variant_titles = (
    "{{sv-adj",
    "{{sv-adv",
    "{{sv-subst",
    "{{sv-verb",
)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{?",
    "{{citat",
    "{{inget uppslag",  # nospread
    "{{fakta",  # facts
    "{{källa-so",  # missing source
    "{{konstr",  # incomplete construction
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "sv")
    []
    >>> find_pronunciations("{{uttal|sv|ipa=eːn/, /ɛn/, /en}}", "sv")
    ['/eːn/, /ɛn/, /en/']
    >>> find_pronunciations("{{uttal|sv|ipa=en|uttalslänk=-|tagg=vissa dialekter}}", "sv")
    ['/en/']
    >>> find_pronunciations("{{uttal|sv|ipa=ɛn|uttalslänk=-}}", "sv")
    ['/ɛn/']
    """
    pattern = re.compile(rf"\{{uttal\|{locale}\|(?:[^\|]+\|)?ipa=([^}}|]+)}}?\|?")
    return [f"/{p}/" for p in utils.unique(pattern.findall(code))]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> from ... import context
    >>> _ = context.reset("sv")

    >>> context.new_word("dribbla")
    >>> adjust_wikicode("{{sv-verb-ar|perfpart=(av)[[dribblad]]}}", "sv", word="dribbla")
    '# {{rev-flexion|dribblad}}\n# {{rev-flexion|dribblade}}\n# {{rev-flexion|dribblades}}\n# {{rev-flexion|dribblande}}\n# {{rev-flexion|dribblandes}}\n# {{rev-flexion|dribblar}}\n# {{rev-flexion|dribblas}}\n# {{rev-flexion|dribblat}}\n# {{rev-flexion|dribblats}}'

    >>> context.new_word("parentestecken")
    >>> adjust_wikicode("{{sv-subst-t-0|rot=parentesteckn}}", "sv", word="parentestecken")
    '# {{rev-flexion|parentesteckens}}\n# {{rev-flexion|parentestecknen}}\n# {{rev-flexion|parentestecknens}}\n# {{rev-flexion|parentestecknet}}\n# {{rev-flexion|parentestecknets}}'

    >>> context.new_word("SM")
    >>> adjust_wikicode("{{sv-subst-t-0|grundform=:SM|:=:}}", "sv", word="SM")
    ''
    """
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

            if not in_tpl:
                cleaned.append(line)
                continue

            tpl_code += line
            if tpl_code.count("{") == tpl_code.count("}"):
                in_tpl = False
                tpl_code = tpl_code.rsplit("}}", 1)[0]
                tpl_code += "}}"

                tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip()
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                if forms := utils.process_templates(
                    word,
                    tpl_code,
                    locale,
                    templates_status=templates_status,
                    variant_only=True,
                ):
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                tpl_code = ""

        code = "\n".join(cleaned)

    return code
