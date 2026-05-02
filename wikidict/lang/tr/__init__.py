"""Turkish language."""

import re

from mediawiki_langcodes import get_all_names

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://tr.wiktionary.org/wiki/%C3%96zel:Rastgele"

langs = {k: v.lower() for k, v in get_all_names("tr") if len(k) == 2}

module_trans = "Modül"
template_trans = "Şablon"

float_separator = ","
thousands_separator = "."

section_sublevels = (3, 4, 5)
head_sections = ("türkçe",)
etyl_section = ("köken",)
sections = (
    *etyl_section,
    "ad",  # noun
    "belirteç",  # adverb
    "çekimleme",  # inflections
    # "çeviriler",  # translations
    # "deyimler",  # derived terms
    "eylem",  # action (?)
    # "kaynakça",  # bibliography
    "ön ad",  # first name
    "özel ad",  # proper noun
    "söyleniş",  # pronunciation
    "yazılışlar",  # spellings
)

variant_titles = sections
variant_templates = (
    "{{ad-hâl",
    "{{çekim",
    "{{hâl",
    "{{mastarı",
    "{{fiil",
    "{{flexion",
)

reverse_variant_titles = (
    "{{tr-ad-tablo",
    "{{tr-çekim",
    # "{{tr-eylem-tablo",
    # "{{tr-kıyaslanamayan-tablo",
)
reverse_variant_templates = ("{{rev-flexion",)

definitions_to_ignore = (
    "{{kökenisteniyor",  # etymology not provided
    "{{tanımisteniyor",  # incomplete definition
)

templates_ignored = (
    "{{audio",
    "{{clear",
    "{{özel ad",
    "{{ses",  # audio
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "tr")
    []

    >>> find_pronunciations("{{IPA|dil=tr|[ɪ‿.ˈnɛ jɑp.ɾɑc]}}", "tr")
    ['/ɪ‿.ˈnɛ jɑp.ɾɑc/']

    >>> find_pronunciations("{{IPA-Telaffuz|dil=tr|bacca:li'je|bacca:lijeˈleɾ}}", "tr")
    ["/bacca:li'je/", '/bacca:lijeˈleɾ/']
    """
    for tpl in re.findall(r"(\{\{IPA(?:-Telaffuz)?\|[^}]+}})", code):
        parts = tpl[2:-2].split("|")[1:]
        utils.extract_keywords_from(parts)
        for idx in range(len(parts)):
            parts[idx] = f"/{parts[idx].strip('[/]')}/"
        return sorted(parts)

    return []


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >> adjust_wikicode('==Türkçe==\n===Eylem===\n# ''[[kenetlemek]]'' [[eylem]]inin [[bildirme kipi]] [[öğrenilen geçmiş zaman]] 2. [[çokluk]] şahıs [[olumlu]] çekimi', "tr")
    '==Türkçe==\n===Eylem===\n# {{flexion|kenetlemek}}'

    >>> _ = context.reset("tr")

    >>> context.new_word("bulmacamda")
    >>> adjust_wikicode('==Türkçe==\n===Ad===\n# {{tr-ünlü-çekimi}}', "tr")
    '==Türkçe==\n===Ad===\n# {{flexion|bulmaca}}'

    >>> context.new_word("duyulmaya")
    >>> adjust_wikicode('==Türkçe==\n===Ad===\n# {{tr-ma/me-çekim}}', "tr")
    '==Türkçe==\n===Ad===\n# {{flexion|duyulma}}'

    >>> context.new_word("sarman")
    >>> adjust_wikicode('==Türkçe==\n{{tr-çekim-ad-1|a|d}}', "tr")
    '==Türkçe==\n# {{rev-flexion|sarmana}}\n# {{rev-flexion|sarmanda}}\n# {{rev-flexion|sarmandan}}\n# {{rev-flexion|sarmanlar}}\n# {{rev-flexion|sarmanlara}}\n# {{rev-flexion|sarmanlarda}}\n# {{rev-flexion|sarmanlardan}}\n# {{rev-flexion|sarmanları}}\n# {{rev-flexion|sarmanlarım}}\n# {{rev-flexion|sarmanlarıma}}\n# {{rev-flexion|sarmanlarımda}}\n# {{rev-flexion|sarmanlarımdan}}\n# {{rev-flexion|sarmanlarımı}}\n# {{rev-flexion|sarmanlarımın}}\n# {{rev-flexion|sarmanlarımız}}\n# {{rev-flexion|sarmanlarımıza}}\n# {{rev-flexion|sarmanlarımızda}}\n# {{rev-flexion|sarmanlarımızdan}}\n# {{rev-flexion|sarmanlarımızı}}\n# {{rev-flexion|sarmanlarımızın}}\n# {{rev-flexion|sarmanların}}\n# {{rev-flexion|sarmanlarına}}\n# {{rev-flexion|sarmanlarında}}\n# {{rev-flexion|sarmanlarından}}\n# {{rev-flexion|sarmanlarını}}\n# {{rev-flexion|sarmanlarının}}\n# {{rev-flexion|sarmanlarınız}}\n# {{rev-flexion|sarmanlarınıza}}\n# {{rev-flexion|sarmanlarınızda}}\n# {{rev-flexion|sarmanlarınızdan}}\n# {{rev-flexion|sarmanlarınızı}}\n# {{rev-flexion|sarmanlarınızın}}\n# {{rev-flexion|sarmanı}}\n# {{rev-flexion|sarmanım}}\n# {{rev-flexion|sarmanıma}}\n# {{rev-flexion|sarmanımda}}\n# {{rev-flexion|sarmanımdan}}\n# {{rev-flexion|sarmanımı}}\n# {{rev-flexion|sarmanımın}}\n# {{rev-flexion|sarmanımız}}\n# {{rev-flexion|sarmanımıza}}\n# {{rev-flexion|sarmanımızda}}\n# {{rev-flexion|sarmanımızdan}}\n# {{rev-flexion|sarmanımızı}}\n# {{rev-flexion|sarmanımızın}}\n# {{rev-flexion|sarmanın}}\n# {{rev-flexion|sarmanına}}\n# {{rev-flexion|sarmanında}}\n# {{rev-flexion|sarmanından}}\n# {{rev-flexion|sarmanını}}\n# {{rev-flexion|sarmanının}}\n# {{rev-flexion|sarmanınız}}\n# {{rev-flexion|sarmanınıza}}\n# {{rev-flexion|sarmanınızda}}\n# {{rev-flexion|sarmanınızdan}}\n# {{rev-flexion|sarmanınızı}}\n# {{rev-flexion|sarmanınızın}}'

    >>> context.new_word("payandalama")
    >>> adjust_wikicode('==Türkçe==\n{{tr-çekim-ad-2|a}}', "tr")
    '==Türkçe==\n# {{rev-flexion|payandalamada}}\n# {{rev-flexion|payandalamadan}}\n# {{rev-flexion|payandalamalar}}\n# {{rev-flexion|payandalamalara}}\n# {{rev-flexion|payandalamalarda}}\n# {{rev-flexion|payandalamalardan}}\n# {{rev-flexion|payandalamaları}}\n# {{rev-flexion|payandalamalarım}}\n# {{rev-flexion|payandalamalarıma}}\n# {{rev-flexion|payandalamalarımda}}\n# {{rev-flexion|payandalamalarımdan}}\n# {{rev-flexion|payandalamalarımı}}\n# {{rev-flexion|payandalamalarımın}}\n# {{rev-flexion|payandalamalarımız}}\n# {{rev-flexion|payandalamalarımıza}}\n# {{rev-flexion|payandalamalarımızda}}\n# {{rev-flexion|payandalamalarımızdan}}\n# {{rev-flexion|payandalamalarımızı}}\n# {{rev-flexion|payandalamalarımızın}}\n# {{rev-flexion|payandalamaların}}\n# {{rev-flexion|payandalamalarına}}\n# {{rev-flexion|payandalamalarında}}\n# {{rev-flexion|payandalamalarından}}\n# {{rev-flexion|payandalamalarını}}\n# {{rev-flexion|payandalamalarının}}\n# {{rev-flexion|payandalamalarınız}}\n# {{rev-flexion|payandalamalarınıza}}\n# {{rev-flexion|payandalamalarınızda}}\n# {{rev-flexion|payandalamalarınızdan}}\n# {{rev-flexion|payandalamalarınızı}}\n# {{rev-flexion|payandalamalarınızın}}\n# {{rev-flexion|payandalamam}}\n# {{rev-flexion|payandalamama}}\n# {{rev-flexion|payandalamamda}}\n# {{rev-flexion|payandalamamdan}}\n# {{rev-flexion|payandalamamı}}\n# {{rev-flexion|payandalamamın}}\n# {{rev-flexion|payandalamamız}}\n# {{rev-flexion|payandalamamıza}}\n# {{rev-flexion|payandalamamızda}}\n# {{rev-flexion|payandalamamızdan}}\n# {{rev-flexion|payandalamamızı}}\n# {{rev-flexion|payandalamamızın}}\n# {{rev-flexion|payandalaman}}\n# {{rev-flexion|payandalamana}}\n# {{rev-flexion|payandalamanda}}\n# {{rev-flexion|payandalamandan}}\n# {{rev-flexion|payandalamanı}}\n# {{rev-flexion|payandalamanın}}\n# {{rev-flexion|payandalamanız}}\n# {{rev-flexion|payandalamanıza}}\n# {{rev-flexion|payandalamanızda}}\n# {{rev-flexion|payandalamanızdan}}\n# {{rev-flexion|payandalamanızı}}\n# {{rev-flexion|payandalamanızın}}\n# {{rev-flexion|payandalaması}}\n# {{rev-flexion|payandalamasına}}\n# {{rev-flexion|payandalamasında}}\n# {{rev-flexion|payandalamasından}}\n# {{rev-flexion|payandalamasını}}\n# {{rev-flexion|payandalamasının}}\n# {{rev-flexion|payandalamaya}}\n# {{rev-flexion|payandalamayı}}'
    """

    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if line.startswith("#") and line.endswith(("-çekimi}}", "-çekim}}")):
            expanded = context.expand(line.removeprefix("#").strip(), "tr")
            if "too deep recursion" in expanded:
                context.clear_errors()
            if variants := re.findall(r"<i>\[\[[^\|]+\|([^\]]+)\]\]</i>", expanded):
                line = f"# {{{{flexion|{variants[-1]}}}}}"
        lines.append(line)
    code = "\n".join(lines)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]*\}}\}})"
        cleaned: list[str] = []

        for line in code.splitlines():
            if not any(tpl in line for tpl in interesting_reverse_variant_titles):
                cleaned.append(line)
                continue

            for tpl in re.findall(pattern, line):
                tpl_name = tpl[2 : max(0, tpl.find("|")) or tpl.find("}")].strip(" \u200e")
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(cleaned)

    return code
