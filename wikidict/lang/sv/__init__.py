"""Swedish language."""

import re

from ...user_functions import unique

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
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

# Variants
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

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "?",
    "citat",
    "inget uppslag",
    "fakta",
    "källa-so",
    "konstr",
    "struktur",
    "sv-adj-alt-okomp",
    "synonymer",
)

# Templates that will be completed/replaced using italic style.
templates_italic = {
    "oböjl": "oböjligt",
    "oräkn": "oräknebart",
}

# Templates more complex to manage.
templates_multi = {
    # {{f}}
    "f": "italic('f')",
    # {{färg|#80FF80|light green}}
    "färg": "color(parts[1])",
    # {{fpl}}
    "fpl": "italic('f pl')",
    # {{ipa|/f/}}
    "ipa": "parts[-1]",
    # {{länk|sv|alfa, beta}}
    "länk": "parts[-1]",
    # {{länk-ar|عَنَى}}
    "länk-ar": "parts[-1]",
    # {{länka|etansyra}}
    "länka": "parts[1]",
    # {{led|sv|f|gata}}
    "led": "italic(('förled' if parts[2] == 'f' else 'efterled') + ' tillhörigt ordet') + ' ' + parts[-1]",
    # {{m}}
    "m": "italic('m')",
    # {{n}}
    "n": "italic('n')",
    # {{npl}}
    "npl": "italic('n pl')",
    # {{ö|en|test}}
    "ö": "parts[-1]",
    # {{ö+|en|test}}
    "ö+": "f\"{parts[-1]} {superscript('(' + parts[1] + ')')}\"",
    # {{ö-inte|en|test}}
    "ö-inte": "f\"{strong('inte')} {italic(strike(parts[-1]))}\"",
    # {{övrigatecken|kolon|:}}
    "övrigatecken": 'f\'"<code>{parts[-1].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")}</code>"\'',
    # {{övrigauppslagsord|n:te}}
    "övrigauppslagsord": "parts[-1]",
    # {{p}}
    "p": "italic('pl')",
    # {{u}}
    "u": "italic('u')",
    # {{uttal|sv|ipa=mɪn}}
    "uttal": "f\"{strong('uttal:')} /{parts[-1].lstrip('ipa=')}/\"",
}

# Templates that will be completed/replaced using custom style.
templates_other = {
    "=": "=",
    "dödform": "†",
}


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
    return [f"/{p}/" for p in unique(pattern.findall(code))]


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

        >>> last_template_handler(["foo"], "sv")
        '##opendoublecurly##foo##closedoublecurly##'

        >>> last_template_handler(["belagt", "sv", "2025"], "sv")
        'Belagt i språket sedan 2025.'
        >>> last_template_handler(["belagt", "sv", "2025", "n"], "sv")
        'belagt i språket sedan 2025'
        >>> last_template_handler(["belagt", "sv", "2025", "nt"], "sv")
        'belagt i språket sedan 2025-talet'

        >>> last_template_handler(["härledning", "sv", "gmq-fsv", "nokot sin, nokon sin"], "sv")
        'fornsvenska <i>nokot sin, nokon sin</i>'
        >>> last_template_handler(["härledning", "sv", "grc", "ἱππόδρομος", "kapplöpningsbana, rännarbana"], "sv")
        'grekiska <i>ἱππόδρομος</i> (”kapplöpningsbana, rännarbana”)'
        >>> last_template_handler(["härledning", "sv", "grc", "ἱππόδρομος", "tr=hippodromos", "kapplöpningsbana, rännarbana"], "sv")
        'grekiska <i>ἱππόδρομος</i> (<i>hippodromos</i>, ”kapplöpningsbana, rännarbana”)'

        >>> last_template_handler(["kognat", "en", "hippodrome"], "sv")
        'engelska <i>hippodrome</i>'
        >>> last_template_handler(["kognat", "gmq-bot", "tíðend"], "sv")
        'okänt språk <i>tíðend</i>'
        >>> last_template_handler(["kognat", "grc", "μηχανή", "verktyg"], "sv")
        'grekiska <i>μηχανή</i> (”verktyg”)'

        >>> last_template_handler(["tagg", "historia", ""], "sv")
        '<i>(historia)</i>'
        >>> last_template_handler(["tagg", "biologi", "allmänt"], "sv")
        '<i>(biologi, allmänt)</i>'
        >>> last_template_handler(["tagg", "politik", "formellt", "språk=tyska"], "sv")
        '<i>(politik, formellt)</i>'
        >>> last_template_handler(["tagg", "kat=nedsättande", "text=något nedsättande"], "sv")
        '<i>(något nedsättande)</i>'
        >>> last_template_handler(["tagg", "text=substantivistiskt slutled", "samhällsvetenskap"], "sv")
        '<i>(samhällsvetenskap, substantivistiskt slutled)</i>'
        >>> last_template_handler(["tagg", "reflexivt"], "sv", word="försäga")
        '<i>(reflexivt: <b>försäga sig</b>)</i>'
        >>> last_template_handler(["tagg", "bildligt", "reflexivt"], "sv", word="etsa")
        '<i>(bildligt, reflexivt: <b>etsa sig</b>)</i>'

        >>> last_template_handler(["tr", "ru", "Пётр Ильи́ч Чайко́вский"], "sv")
        'Pjotr Iljítj Tjajkóvskij'

    """
    from ...user_functions import extract_keywords_from, italic, strong, term
    from .. import defaults
    from .langs import langs
    from .template_handlers import lookup_template, render_template
    from .transliterator import transliterate

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

    if tpl == "avledning":
        if len(parts) == 3:
            parts.pop(2)
        if data["partikel"]:
            # Delete superfluous letters (till + lada = tilllada, but we need tillada)
            return re.sub(r"(.)(?:\1){2,}", r"\1\1", f"{data['partikel']}{parts[-1]}")
        return parts[-1]

    if tpl == "belagt":
        year = parts[1]
        if len(parts) > 2:
            first_letter = "b"
            suffix = "-talet" if "t" in parts[2] else ""
        else:
            first_letter = "B"
            suffix = "."
        return f"{first_letter}elagt i språket sedan {year}{suffix}"

    if tpl == "härledning":
        parts.pop(0)  # Remove the source lang
        lang = parts.pop(0)
        # Special cases (https://sv.wiktionary.org/w/index.php?title=Modul:h%C3%A4rledning&oldid=3932208#L-36--L-44)
        phrase = {"grc": "grekiska", "gd": "gäliska", "el": "nygrekiska", "la": "latinska"}.get(lang) or langs[lang]
        phrase += f" {italic(parts.pop(0))}"
        if (tr := data["tr"]) or parts:
            phrase += " ("
            if tr:
                phrase += italic(tr)
            if parts:
                phrase += ", " if tr else ""
                phrase += f"”{parts.pop(0)}”"
            phrase += ")"
        return phrase

    if tpl == "kognat":
        lang = parts.pop(0)
        # Special cases (https://sv.wiktionary.org/w/index.php?title=Mall:kognat&oldid=3521836#Observera)
        phrase = {"grc": "grekiska", "gd": "gäliska", "el": "nygrekiska", "la": "latinska"}.get(lang) or langs[lang]
        phrase += f" {italic(parts.pop(0))}"
        if parts:
            phrase += f" (”{parts[0]}”)"
        return phrase

    if tpl == "tagg":
        words = [f"{part}: {strong(f'{word} sig')}" if part == "reflexivt" else part for part in parts if part]
        if data["text"]:
            words.append(data["text"])
        return term(", ".join(words))

    if tpl == "tr":
        return transliterate(parts[0], parts[1])

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://sv.wiktionary.org/wiki/Special:RandomRootpage"
