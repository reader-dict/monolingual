"""Catalan language."""

import re

from ...user_functions import unique
from .transliterator import transliterate

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = "."

# Markers for sections that contain interesting text to analyse.
head_sections = ("{{-ca-}}", "{{-mul-}}")
etyl_section = ("{{-etimologia-", "{{-etim-", "{{etim-lang")
sections = (
    *etyl_section,
    "abreviatura",
    "acrònim",
    "adjectiu",
    "adverbi",
    "article",
    "caràcter",
    "conjunció",
    "contracció",
    "desinència",
    "forma verbal",
    "frase feta",
    "infix",
    "interjecció",
    "lletra",
    "nom",
    "numeral",
    "prefix",
    "preposició",
    "pronom",
    "proverbi",
    "sigles",
    "sufix",
    "símbol",
    "verb",
)

# Variants                                                                                  │    │
variant_titles = sections
variant_templates = (
    "{{ca-forma-conj",
    "{{forma-conj",
    "{{forma-f|",
    "{{forma-p|",
)

# Some definitions are not good to keep
definitions_to_ignore = (
    "ex-cit",
    "ex-us",
)

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "categoritza",
    "catllengua",
    "CN",
    "falten accepcions",
    "manquen accepcions",
    "sense accepcions",
    "-etimologia-",
    "-etim-",
)

# Templates more complex to manage.
templates_multi = {
    # {{AFI|/ˈwujt/}}
    "AFI": "parts[-1]",
    # {{claudàtors|[[milliarum]]}}
    "claudàtors": 'f"[{parts[1]}]"',
    # {{color|#E01010}}
    "color": "color(parts[1])",
    # {{def-meta|Utilitzat en l'expressió tros de quòniam.}}
    "def-meta": "italic(parts[-1])",
    # {{e-propi|ca|grèvol}}
    "e-propi": "strong(parts[2])",
    # {{etim-s|ca|XIV}}
    # {{etim-s|ca|XVII|1617}}
    "etim-s": "('segle ' + parts[2]) if len(parts) == 3 else parts[-1]",
    # {{IPAchar|[θ]}}
    "IPAchar": "parts[-1]",
    # {{pron|hi|/baːzaːr/}}
    "pron": "', '.join(parts[2:])",
    # {{q|tenir bona planta}}
    "q": "term(concat(parts[1:], ', '))",
    # {{romanes|XIX}}
    "romanes": "small_caps(parts[-1].lower())",
}


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ca")
    []
    >>> find_genders("{{ca-nom|m}}", "ca")
    ['m']
    >>> find_genders("{{ca-nom|m}} {{ca-nom|m}}", "ca")
    ['m']
    """
    pattern = re.compile(rf"\{{{locale}-\w+\|([fm]+)")
    return unique(pattern.findall(code))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ca")
    []
    >>> find_pronunciations("{{ca-pron|/as/}}", "ca")
    ['/as/']
    >>> find_pronunciations("{{ca-pron|or=/əɫ/}}", "ca")
    ['/əɫ/']
    >>> find_pronunciations("{{ca-pron|or=/əɫ/|occ=/eɫ/}}", "ca")
    ['/əɫ/']
    >>> find_pronunciations("{{ca-pron|q=àton|or=/əɫ/|occ=/eɫ/|rima=}}", "ca")
    ['/əɫ/']
    """
    pattern = re.compile(rf"\{{\{{\s*{locale}-pron\s*\|(?:q=\S*\|)?(?:\s*or\s*=\s*)?(/[^/]+/)")
    return unique(pattern.findall(code))


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be called in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["default-test-xyz"], "ca")
        '##opendoublecurly##default-test-xyz##closedoublecurly##'

        >>> last_template_handler(["calc semàntic", "es", "ca", "pueblo"], "ca")
        'calc semàntic del castellà <i>pueblo</i>'
        >>> last_template_handler(["calc semàntic", "es", "ca", "pueblo", "maj=1"], "ca")
        'Calc semàntic del castellà <i>pueblo</i>'

        >>> last_template_handler(["doblet", "ca", "Castellar"], "ca")
        '<i>Castellar</i>'
        >>> last_template_handler(["doblet", "ca", "mèdic", "pos=adjectiu"], "ca")
        '<i>mèdic</i> (adjectiu)'

        >>> last_template_handler(["e", "grc", "υ", "tr=-"], "ca")
        'υ'
        >>> last_template_handler(["e", "el", "δ"], "ca")
        'δ (<i>d</i>)'
        >>> last_template_handler(["l", "egy", "wšbtj"], "ca")
        'wšbtj'

        >>> last_template_handler(["epònim", "ca", "w=Niels Henrik Abel"], "ca")
        'Niels Henrik Abel'
        >>> last_template_handler(["epònim", "ca", "André-Marie Ampère", "w=Niels Henrik Abel"], "ca")
        'André-Marie Ampère'

        >>> last_template_handler(["etim-lang", "oc", "ca", "cabèco"], "ca")
        "De l'occità <i>cabèco</i>"
        >>> last_template_handler(["etim-lang", "la", "ca", "verba"], "ca")
        'Del llatí <i>verba</i>'
        >>> last_template_handler(["etim-lang", "en", "ca"], "ca")
        "De l'anglès"
        >>> last_template_handler(["etim-lang", "grc", "ca", "φαιός", "trad=gris"], "ca")
        'Del grec antic <i>φαιός</i> (<i>phaiós</i>, «gris»)'
        >>> last_template_handler(["etim-lang", "ar", "ca", "برج", "alt=البرج", "trans=al-burj", "trad=la torre"], "ca")
        "De l'àrab <i>البرج</i> (<i>al-burj</i>, «la torre»)"

        >>> last_template_handler(["del-lang", "la", "ca", "verba"], "ca")
        'del llatí <i>verba</i>'
        >>> last_template_handler(["del-lang", "la", "ca", "exemplar", "pos=substantiu"], "ca")
        'del llatí <i>exemplar</i>'
        >>> last_template_handler(["Del-lang", "xib", "ca", "baitolo"], "ca")  # doctest: +ELLIPSIS
        'De l\\'ibèric <i>baitolo</i> (<svg ...'
        >>> last_template_handler(["Del-lang", "grc", "ca", "ῡ̔οειδής", "trad=en forma d’ípsilon"], "ca")
        'Del grec antic <i>ῡ̔οειδής</i> (<i>hȳoeidḗs</i>, «en forma d’ípsilon»)'
        >>> last_template_handler(["del-lang", "la", "ca"], "ca")
        ''
        >>> last_template_handler(["del-lang", "la", "ca", "-"], "ca")
        ''
        >>> last_template_handler(["del-lang", "ar", "ca", "مَمْلُوك", "tr=mamlūk", "t=esclau"], "ca")
        "de l'àrab <i>مَمْلُوك</i> (<i>mamlūk</i>, «esclau»)"
        >>> last_template_handler(["del-lang", "zh", "ca", "sc=Hant", "圍棋"], "ca")
        'del xinès <i>圍棋</i> (<i>围棋, wéiqí</i>)'
        >>> last_template_handler(["Del-lang", "gem", "ca", "Adroar"], "ca")
        "D'un germànic <i>Adroar</i>"

        >>> last_template_handler(["Fals tall", "ca", "Far", "el Far"], "ca")
        'Fals tall sil·làbic de <i>el Far</i>'
        >>> last_template_handler(["fals tall", "ca", "s'endemà", "trad=l’endemà"], "ca")
        "fals tall sil·làbic de <i>s'endemà</i> («l’endemà»)"

        >>> last_template_handler(["la"], "ca")
        'Llatí'

        >>> last_template_handler(["m", "ca", "tardanies", "t=fruits tardans"], "ca")
        '<i>tardanies</i> («fruits tardans»)'
        >>> last_template_handler(["m", "grc", "ὖ"], "ca")
        'ὖ (<i>ŷ</i>)'
        >>> last_template_handler(["m", "grc", "ἄνῑσον", "ánison"], "ca")
        'ánison (<i>ánīson</i>)'
        >>> last_template_handler(["m", "el", "Δ"], "ca")
        'Δ (<i>D</i>)'
        >>> last_template_handler(["m", "grc", "", "Καστελανοι"], "ca")
        'Καστελανοι (<i>Kastelanoi</i>)'
        >>> last_template_handler(["m", "ar", "مَلَكَ", "", "tr=malaka", "t=posseir, adquirir"], "ca")
        '<i>مَلَكَ</i> (<i>malaka</i>, «posseir, adquirir»)'
        >>> last_template_handler(["m", "grc", "αἰτία", "t=aitía", "trad=causa"], "ca")
        'αἰτία (<i>aitía</i>, «aitía»)'
        >>> last_template_handler(["m", "la", "*fūricāre", "trad=furgar"], "ca")
        '<i>*fūricāre</i> («furgar»)'
        >>> last_template_handler(["m", "xib", "*Icosia"], "ca")
        '<i>*Icosia</i>'

        >>> last_template_handler(["lleng", "la", "√ⵎⵣⵖ"], "ca")
        '√ⵎⵣⵖ'
        >>> last_template_handler(["lleng", "la", "tipus=terme", "Agnus Dei qui tollis peccata mundi..."], "ca")
        '<i>Agnus Dei qui tollis peccata mundi...</i>'
        >>> last_template_handler(["lleng", "la", "tipus=lema", "Agnus Dei qui tollis peccata mundi..."], "ca")
        '<b>Agnus Dei qui tollis peccata mundi...</b>'
        >>> last_template_handler(["lleng", "la", "tipus=negreta", "Agnus Dei qui tollis peccata mundi..."], "ca")
        '<b>Agnus Dei qui tollis peccata mundi...</b>'

        >>> last_template_handler(["terme", "it", "come"], "ca")
        '<i>come</i>'
        >>> last_template_handler(["terme", "ca", "seu", "el seu"], "ca")
        '<i>el seu</i>'
        >>> last_template_handler(["terme", "la", "diēs Iovis", "trad=dia de Júpiter"], "ca")
        '<i>diēs Iovis</i> («dia de Júpiter»)'
        >>> last_template_handler(["terme", "grc", "λόγος", "trans=lógos"], "ca")
        'λόγος (<i>lógos</i>)'
        >>> last_template_handler(["terme", "grc", "λόγος", "trans=lógos", "trad=paraula"], "ca")
        'λόγος (<i>lógos</i>, «paraula»)'
        >>> last_template_handler(["terme", "grc", "λόγος", "trans=lógos", "trad=paraula", "pos=gentilici"], "ca")
        'λόγος (<i>lógos</i>, «paraula», gentilici)'
        >>> last_template_handler(["terme", "en", "[[cheap]] as [[chips]]", "lit=tant [[barat]] com les [[patates]]"], "ca")
        '<i>[[cheap]] as [[chips]]</i> (literalment «tant [[barat]] com les [[patates]]»)'

        >>> last_template_handler(["trad", "es", "manzana"], "ca")
        'manzana <sup>(es)</sup>'
        >>> last_template_handler(["trad", "es", "tr=manzana"], "ca")
        'manzana <sup>(es)</sup>'
        >>> last_template_handler(["trad", "sc=es", "manzana"], "ca")
        'manzana <sup>(es)</sup>'

        >>> last_template_handler(["xib-trans", "ś1i1ka1ŕ5a3"], "ca")  # doctest: +ELLIPSIS
        '<svg ...'
        >>> last_template_handler(["xib-trans", "*uŕki"], "ca")
        '<i>*uŕki</i>'
    """
    from ...user_functions import concat, extract_keywords_from, italic, strong, superscript
    from .. import defaults
    from . import general
    from .langs import grups, langs
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        return render_template(word, template)

    data = extract_keywords_from(parts)
    phrase = ""

    def parse_other_parameters(lang: str = "", word: str = "") -> str:
        toadd = []
        trad_added = False

        if "tr" in data and not data["tr"] and data["trad"] and data["trans"]:
            toadd.append(f"«{data['trad']}»")
            trad_added = True
        elif data["trans"]:
            toadd.append(italic(data["trans"]))
        elif lang and word and data["tr"] != "-" and (trans := transliterate(lang, word)):
            toadd.append(trans if lang == "xib" else italic(trans))
        elif (tr := data["tr"]) and tr != "-":
            toadd.append(italic(tr))

        if data["t"]:
            toadd.append(f"«{data['t']}»")
        elif not trad_added and data["trad"]:
            toadd.append(f"«{data['trad']}»")
        if data["glossa"]:
            toadd.append(f"«{data['glossa']}»")
        if data["pos"] and tpl not in {"del-lang", "Del-lang"}:
            toadd.append(data["pos"])
        if data["lit"]:
            toadd.append(f"literalment «{data['lit']}»")

        return f" ({concat(toadd, ', ')})" if toadd else ""

    def format_source(lang: str, lang_name: str, nocap: bool) -> str:
        if lang in grups:
            return "d'un " if nocap else "D'un "
        phrase = "d" if nocap else "D"
        phrase += "e l'" if general.cal_apostrofar(lang_name) else "el "
        return phrase

    if tpl == "calc semàntic":
        phrase = "Calc semàntic " if data["maj"] == "1" else "calc semàntic "
        lang = langs[parts[0]]
        phrase += format_source(parts[0], lang, True)
        phrase += f"{lang} "
        phrase += f"{italic(parts[-1])}{parse_other_parameters()}"
        return phrase

    if tpl == "doblet":
        text = italic(parts[-1])
        return f"{text}{parse_other_parameters()}"

    if tpl == "epònim":
        return parts[1] if len(parts) > 1 else (data["w"] if "w" in data else "")

    if tpl in {"e", "l"}:
        return f"{parts[-1]}{parse_other_parameters(parts[0], parts[1])}"

    if tpl in ("del-lang", "Del-lang") and (len(parts) <= 2 or parts[2] == "-"):
        return ""

    if tpl in ("etim-lang", "del-lang", "Del-lang"):
        if parts[0] in langs:
            lang = langs[parts[0]]
            phrase += format_source(parts[0], lang, tpl == "del-lang")
            phrase += lang
            word = ""
            if len(parts) > 2:
                word = data["alt"] or parts[2]
                phrase += f" {italic(parts[3] if len(parts) > 3 else word)}"
        phrase += parse_other_parameters(parts[0], word)
        return phrase

    if tpl in ("fals tall", "Fals tall"):
        return f"{tpl} sil·làbic de {italic(parts[-1])}{parse_other_parameters()}"

    if tpl == "lleng":
        phrase = parts[-1]
        if data["tipus"] == "terme":
            phrase = italic(phrase)
        elif data["tipus"] in ("lema", "negreta"):
            phrase = strong(phrase)
        return phrase

    if tpl in {"m", "terme"}:
        word = parts[2] if len(parts) > 2 and parts[2] else parts[1]
        text = word if parts[0] in {"el", "grc"} else italic(word)
        return f"{text}{parse_other_parameters(parts[0], next((part for part in parts[1:] if part), ''))}"

    if tpl == "calc":
        return f"{italic(parts[-1])}{parse_other_parameters(parts[0], parts[-1])}"

    if tpl == "sinònim":
        # text = {sinònim|mul|Miathyria|glossa=gènere de libèl·lules}}
        text = f"{italic('sinònim de')} {strong(parts[1])}"
        if glossa := data["glossa"]:
            text += f" («{glossa}»)"
        return text

    if tpl == "trad":
        src = data["sc"] or parts.pop(0)
        trans = data["tr"] or parts.pop(0)
        return f"{trans} {superscript(f'({src})')}"

    if tpl == "xib-trans":
        if parts[0].startswith("*"):
            return italic(parts[0])
        return transliterate("xib", parts[0])

    # This is a country in the current locale
    if lang := langs.get(tpl, ""):
        return lang.capitalize()

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://ca.wiktionary.org/wiki/Especial:RandomRootpage"
