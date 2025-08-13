from collections import defaultdict

from ...user_functions import extract_keywords_from, italic, strong
from .abk import abk

bibel_names = {
    "Gen": "Genesis",
    "1 Mos": "1. Buch Mose",
    "Ex": "Exodus",
    "2 Mos": "2. Buch Mose",
    "Lev": "Levitikus",
    "3 Mos": "3. Buch Mose",
    "Num": "Numeri",
    "4 Mos": "4. Buch Mose",
    "Dtn": "Deuteronomium",
    "5 Mos": "5. Buch Mose",
    "Jos": "Josua",
    "Ri": "Richter",
    "Rut": "Rut",
    "1 Sam": "1. Buch Samuel",
    "2 Sam": "2. Buch Samuel",
    "1 Kön": "1. Buch der Könige",
    "2 Kön": "2. Buch der Könige",
    "1 Chr": "1. Buch der Chronik",
    "2 Chr": "2. Buch der Chronik",
    "Esr": "Esra",
    "Neh": "Nehemia",
    "2 Esr": "2. Buch Esra ([[Nehemia]])",
    "Tob": "Tobit (Tobias)",
    "Jdt": "Judit",
    "Est": "Ester",
    "1 Makk": "1. Buch der Makkabäer",
    "2 Makk": "2. Buch der Makkabäer",
    "Ijob": "Ijob",
    "Ps": "Psalm",
    "Spr": "Sprichwörter",
    "Koh": "Kohelet",
    "Hld": "Hoheslied",
    "Weish": "Weisheit",
    "Sir": "Jesus Sirach",
    "Jes": "Jesaja",
    "Jer": "Jeremia",
    "Klgl": "Klagelieder",
    "Bar": "Baruch",
    "Ez": "Ezechiel",
    "Dan": "Daniel",
    "Hos": "Hosea",
    "Joel": "Joel",
    "Am": "Amos",
    "Obd": "Obadja",
    "Jona": "Jona",
    "Mi": "Micha",
    "Nah": "Nahum",
    "Hab": "Habakuk",
    "Zef": "Zefanja",
    "Hag": "Haggai",
    "Sach": "Sacharja",
    "Mal": "Maleachi",
    "Mt": "Matthäus",
    "Mk": "Markus",
    "Lk": "Lukas",
    "Joh": "Johannes",
    "Apg": "Apostelgeschichte",
    "Röm": "Römer",
    "1 Kor": "1. Korinther",
    "2 Kor": "2. Korinther",
    "Gal": "Galater",
    "Eph": "Epheser",
    "Phil": "Philipper",
    "Kol": "Kolosser",
    "1 Thess": "1. Thessalonicher",
    "2 Thess": "2. Thessalonicher",
    "1 Tim": "1. Timotheus",
    "2 Tim": "2. Timotheus",
    "Tit": "Titus",
    "Phlm": "Philemon",
    "Hebr": "Hebräer",
    "Jak": "Jakobus",
    "1 Petr": "1. Petrus",
    "2 Petr": "2. Petrus",
    "1 Joh": "1. Johannes",
    "2 Joh": "2. Johannes",
    "3 Joh": "3. Johannes",
    "Jud": "Judas",
    "Offb": "Offenbarung",
}

VORSILBE_DATA = [
    (
        14,
        {
            "hintereinander",
        },
    ),
    (
        13,
        {
            "durcheinander",
            "gegeneinander",
            "nebeneinander",
            "untereinander",
            "widereinander",
        },
    ),
    (
        12,
        {
            "übereinander",
        },
    ),
    (
        11,
        {
            "aufeinander",
            "auseinander",
            "beieinander",
            "miteinander",
            "voneinander",
        },
    ),
    (
        10,
        {
            "aneinander",
            "dazwischen",
            "hintenüber",
            "ineinander",
            "zueinander",
        },
    ),
    (
        9,
        {
            "gegenüber",
            "hernieder",
            "hinterher",
        },
    ),
    (
        8,
        {
            "aufwärts",
            "beiseite",
            "dahinter",
            "drauflos",
            "einwärts",
            "entgegen",
            "herunter",
            "hindurch",
            "hinunter",
            "vornüber",
            "vorwärts",
            "zunichte",
            "zusammen",
            "zwischen",
        },
    ),
    (
        7,
        {
            "abwärts",
            "dagegen",
            "daneben",
            "darüber",
            "entlang",
            "entzwei",
            "fürlieb",
            "herüber",
            "hierher",
            "hinüber",
            "instand",
            "schwarz",
            "trocken",
            "überein",
            "vorüber",
            "zurecht",
            "zuwider",
        },
    ),
    (
        6,
        {
            "bereit",
            "einher",
            "falsch",
            "fertig",
            "gerade",
            "gleich",
            "herauf",
            "heraus",
            "herbei",
            "herein",
            "hervor",
            "hinauf",
            "hinaus",
            "hinein",
            "hintan",
            "hinter",
            "hinweg",
            "kaputt",
            "nieder",
            "runter",
            "scharf",
            "schief",
            "schutz",
            "voraus",
            "vorbei",
            "vorher",
            "vorweg",
            "weiter",
            "wieder",
            "zugute",
            "zurück",
        },
    ),
    (
        5,
        {
            "abhin",
            "anhin",
            "bauch",
            "bevor",
            "blond",
            "breit",
            "dabei",
            "dafür",
            "daher",
            "dahin",
            "daran",
            "davon",
            "davor",
            "dicht",
            "drauf",
            "drein",
            "durch",
            "empor",
            "flach",
            "flott",
            "fremd",
            "gegen",
            "glatt",
            "herab",
            "heran",
            "herum",
            "hinab",
            "hinan",
            "hinzu",
            "klein",
            "krank",
            "näher",
            "offen",
            "reich",
            "rüber",
            "schön",
            "still",
            "übrig",
            "umher",
            "umhin",
            "unter",
            "voran",
            "weich",
            "wider",
            "zuvor",
        },
    ),
    (
        4,
        {
            "acht",
            "blau",
            "bloß",
            "dazu",
            "dort",
            "dran",
            "fehl",
            "feil",
            "fein",
            "fern",
            "fest",
            "fort",
            "frei",
            "gelb",
            "groß",
            "grün",
            "heim",
            "hier",
            "hoch",
            "kahl",
            "kalt",
            "klar",
            "kurz",
            "lieb",
            "leer",
            "mies",
            "miss",
            "nach",
            "nahe",
            "nass",
            "quer",
            "raus",
            "rein",
            "rück",
            "satt",
            "seil",
            "übel",
            "über",
            "voll",
            "wach",
            "wahr",
            "warm",
            "weis",
            "weiß",
            "wert",
            "wohl",
        },
    ),
    (
        3,
        {
            "auf",
            "aus",
            "bei",
            "dar",
            "ein",
            "ent",
            "gut",
            "her",
            "hin",
            "los",
            "mit",
            "out",
            "rum",
            "tot",
            "ver",
            "vor",
            "weg",
            "zer",
        },
    ),
    (
        2,
        {
            "ab",
            "an",
            "be",
            "da",
            "er",
            "re",
            "um",
            "zu",
        },
    ),
]


def render_bibel(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_bibel("Bibel", ["Mt", "1", "1"], defaultdict(str))
    'Matthäus 1,1'
    >>> render_bibel("Bibel", ["Mt", "1", "1-5", "HFA"], defaultdict(str))
    'Matthäus 1,1-5'
    >>> render_bibel("Bibel", ["Mt", "1", "1", "NIV"], defaultdict(str))
    'Matthäus 1,1'
    >>> render_bibel("Bibel", ["Mos", "18", "4", "LUT"], defaultdict(str))
    'Mos 18,4'
    """
    phrase = bibel_names.get(parts[0], parts[0])
    phrase += f" {parts[1]}"
    if len(parts) > 2:
        phrase += f",{parts[2]}"
    return phrase


def render_foreign_lang(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_foreign_lang("Hebr", ["בַּיִת כְּנֶסֶת"], defaultdict(str))
    'בַּיִת כְּנֶסֶת'
    >>> render_foreign_lang("Hebr", ["בַּיִת כְּנֶסֶת"], defaultdict(str, {"d-heb": "bayiṯ k<sup><small>e</small></sup>næsæṯ"}))
    'בַּיִת כְּנֶסֶת (CHA: bayiṯ k<sup><small>e</small></sup>næsæṯ)'
    >>> render_foreign_lang("Hebr", ["בַּיִת כְּנֶסֶת"], defaultdict(str, {"b": "Haus der Versammlung, Haus der Zusammenkunft", "d-heb": "bayiṯ k<sup><small>e</small></sup>næsæṯ"}))
    'בַּיִת כְּנֶסֶת (CHA: bayiṯ k<sup><small>e</small></sup>næsæṯ) ‚Haus der Versammlung, Haus der Zusammenkunft‘'
    >>> render_foreign_lang("Hebr", ["שבת", "Ü"], defaultdict(str, {"b": "Ruhetag; Schabbes", "d-yid": "shabes"}))
    'שבת, YIVO: shabes, „Ruhetag; Schabbes“'
    >>> render_foreign_lang("Hebr", ["אסנוגה"], defaultdict(str, {"b": "Synagoge, Gebetshaus", "d-lad": "esnoga"}))
    'אסנוגה (esnoga) ‚Synagoge, Gebetshaus‘'

    >>> render_foreign_lang("Paschto", ["طالب"], defaultdict(str, {"b": "Schüler", "d": "ṭā-lib", "v": "طَالِب"}))
    'طَالِب (DMG: ṭā-lib) ‚Schüler‘'
    >>> render_foreign_lang("Paschto", ["طالب", "Ü"], defaultdict(str, {"b": "Schüler", "d": "ṭā-lib", "v": "طَالِب"}))
    'طَالِب, DMG: ṭā-lib, „Schüler“'

    >>> render_foreign_lang("Urdu", ["فن"], defaultdict(str, {"b": "Kunst", "d": "fann", "v": "فَنّ"}))
    'فَنّ, DMG: fann, „Kunst“'
    """
    phrase = data["v"] or parts.pop(0)

    as_ü_template = "Ü" in parts
    if tpl == "Urdu":
        as_ü_template = not as_ü_template

    if tpl == "Hebr":
        if trans := data["d-heb"]:
            phrase += f", CHA: {trans}" if as_ü_template else f" (CHA: {trans})"
        elif trans := data["d-yid"]:
            phrase += f", YIVO: {trans}" if as_ü_template else f" (YIVO: {trans})"
        elif trans := data["d-lad"]:
            phrase += f", {trans}" if as_ü_template else f" ({trans})"
    elif trans := data["d"]:
        phrase += f", DMG: {trans}" if as_ü_template else f" (DMG: {trans})"

    if data["b"]:
        if as_ü_template:
            phrase += ","
        sep = ("„", "“") if as_ü_template else ("‚", "‘")
        phrase += f" {sep[0]}{data['b']}{sep[1]}"

    return phrase


def render_foreign_lang_simple(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_foreign_lang_simple("Arab", ["أَحْمَدُ بْنُ حَنْبَلٍ"], defaultdict(str))
    'أَحْمَدُ بْنُ حَنْبَلٍ'
    >>> render_foreign_lang_simple("Arab", ["أَحْمَدُ بْنُ حَنْبَلٍ"], defaultdict(str, {"d": "Aḥmadu bnu Ḥanbalin"}))
    'أَحْمَدُ بْنُ حَنْبَلٍ (DMG: Aḥmadu bnu Ḥanbalin)'
    >>> render_foreign_lang_simple("Arab", ["أَحْمَدُ بْنُ حَنْبَلٍ"], defaultdict(str, {"b": "Aḥmad, Sohn des Ḥanbal", "d": "Aḥmadu bnu Ḥanbalin"}))
    'أَحْمَدُ بْنُ حَنْبَلٍ (DMG: Aḥmadu bnu Ḥanbalin) ‚Aḥmad, Sohn des Ḥanbal‘'

    >>> render_foreign_lang_simple("Farsi", ["آیتالله"], defaultdict(str, {"b": "Geschöpf", "d" :"ǧānvar", "v": "جَانْوَر"}))
    'جَانْوَر (DMG: ǧānvar) ‚Geschöpf‘'
    """
    phrase = data["v"] or parts.pop(0)
    if data["d"]:
        phrase += f" (DMG: {data['d']})"
    if data["b"]:
        phrase += f" ‚{data['b']}‘"
    return phrase


no_commas = (
    "allg.",
    "allgemein",
    "ansonsten",
    "auch",
    "bei",
    "bes.",
    "besonders",
    "bis",
    "bisweilen",
    "das",
    "der",
    "die",
    "eher",
    "früher",
    "häufig",
    "hauptsächlich",
    "im",
    "in",
    "insbes.",
    "insbesondere",
    "leicht",
    "meist",
    "meistens",
    "mit",
    "mitunter",
    "noch",
    "noch in",
    "nur",
    "nur noch",
    "oder",
    "oft",
    "oftmals",
    "ohne",
    "respektive",
    "sehr",
    "seltener",
    "seltener auch",
    "sonst",
    "sowie",
    "später",
    "speziell",
    "teils",
    "teilweise",
    "über",
    "überwiegend",
    "und",
    "von",
    "vor allem",
    "vor allem in",
    "z. B.",
    "zum Beispiel",
    "z. T.",
    "zum Teil",
)


def render_K(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_K("K", ["Sport"], defaultdict(str))
    '<i>Sport:</i>'
    >>> render_K("K", ["trans."], defaultdict(str))
    '<i>transitiv:</i>'
    >>> render_K("K", ["trans.", "Linguistik", "Wortbildung"], defaultdict(str))
    '<i>transitiv, Linguistik, Wortbildung:</i>'
    >>> render_K("K", ["kPl.", "ugs."], defaultdict(str))
    '<i>kein Plural, umgangssprachlich:</i>'
    >>> render_K("K", [], defaultdict(str, {"ft": "kurz für"}))
    '<i>kurz für:</i>'
    >>> render_K("K", ["Astronomie"], defaultdict(str, {"ft": "kurz für"}))
    '<i>Astronomie, kurz für:</i>'
    >>> render_K("K", ["intrans.", "Nautik"], defaultdict(str, {"t7": "_", "ft": "(von Schiffen)"}))
    '<i>intransitiv, Nautik (von Schiffen):</i>'
    >>> render_K("K", ["intrans.", "Nautik"], defaultdict(str, {"t7": "_", "ft": "(von Schiffen)"}))
    '<i>intransitiv, Nautik (von Schiffen):</i>'
    >>> render_K("K", ["test", "Nautik"], defaultdict(str, {"t1": "_"}))
    '<i>test Nautik:</i>'
    >>> render_K("K", ["landschaftlich", ""], defaultdict(str))
    '<i>landschaftlich:</i>'
    >>> render_K("K", ["Süddeutschland", "und", "Österreich", "sonst", "veraltete Schreibweise"], defaultdict(str))
    '<i>Süddeutschland und Österreich, sonst veraltete Schreibweise:</i>'
    """
    conjonctions = ("oder", "respektive", "sowie", "und")
    conjonctions_start = (*conjonctions, *no_commas)
    phrase = ""
    parts = [p for p in parts if p]
    for i, p in enumerate(parts, start=1):
        t_index = f"t{i}"
        phrase += abk[p] if p in abk else p
        default_sep = ""
        if i != len(parts):
            default_sep = (
                "," if p not in conjonctions_start and i < len(parts) and parts[i] not in conjonctions else " "
            )
            sep = data.get(t_index, default_sep)
            if sep == "_":
                sep = " "
            elif sep.strip():
                sep = f"{sep} "
            phrase += sep

    if ft := data["ft"]:
        spacer = data.get("t7", ", " if parts else "")
        if spacer == "_":
            spacer = " "
        ft = spacer + ft

    return italic(f"{phrase}{ft}:")


def render_ref_dejure(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ref_dejure("Ref-dejure", ["", "54", "InsO"], defaultdict(str))
    '54 InsO'
    >>> render_ref_dejure("Ref-dejure", ["", "3", "EGGmbHG"], defaultdict(str))
    '3 EGGmbHG'
    >>> render_ref_dejure("Ref-dejure", ["", "3", "EGGmbHG"], defaultdict(str, {"Erg": "II Nr. 9"}))
    '3 II Nr. 9 EGGmbHG'
    >>> render_ref_dejure("Ref-dejure", ["§", "1004", "BGB"], defaultdict(str))
    '§ 1004 BGB'
    >>> render_ref_dejure("Ref-dejure", ["§", "1004", "BGB"], defaultdict(str, {"Erg": "II Nr. 9"}))
    '§ 1004 II Nr. 9 BGB'
    >>> render_ref_dejure("Ref-dejure", ["§§", "19", "InsO"], defaultdict(str))
    '§§ 19'
    >>> render_ref_dejure("Ref-dejure", ["§§", "2", "TKG"], defaultdict(str, {"Erg": "II Nr. 9"}))
    '§§ 2 II Nr. 9'
    >>> render_ref_dejure("Ref-dejure", ["Art.", "15", "GG"], defaultdict(str))
    'Art. 15 GG'
    >>> render_ref_dejure("Ref-dejure", ["Art.", "15", "GG"], defaultdict(str, {"Erg": "II Nr. 9"}))
    'Art. 15 II Nr. 9 GG'
    >>> render_ref_dejure("Ref-dejure", ["Artt.", "1", "EGGmbHG"], defaultdict(str))
    'Art. 1'
    >>> render_ref_dejure("Ref-dejure", ["Artt.", "1", "EGGmbHG"], defaultdict(str, {"Erg": "II Nr. 9"}))
    'Art. 1 II Nr. 9'
    >>> render_ref_dejure("Ref-dejure", ["Mitte", "27", "InsO"], defaultdict(str))
    '27'
    >>> render_ref_dejure("Ref-dejure", ["Mitte", "2", "EGGmbHG"], defaultdict(str))
    '2'
    >>> render_ref_dejure("Ref-dejure", ["Mitte", "2", "EGGmbHG"], defaultdict(str, {"Erg": "II Nr. 9"}))
    '2 II Nr. 9'
    >>> render_ref_dejure("Ref-dejure", ["Artikel", "36", "EuGVVO"], defaultdict(str, {"Erg": "Absatz&nbsp;1"}))
    'Artikel 36 Absatz&nbsp;1 EuGVVO'
    """
    article, number, name = parts
    complement = f" {data['Erg']}" if data["Erg"] else ""
    display_name = not any(
        [
            article in {"§§", "Mitte"},
            article.startswith("Art") and name == "EGGmbHG",
            article == "§§" and name == "InsO",
        ],
    )
    name = f" {name}" if display_name else ""
    match article:
        case "" | "Mitte":
            return f"{number}{complement}{name}"
        case "§" | "§§":
            return f"{article} {number}{complement}{name}"
        case "Art." | "Artt.":
            return f"Art. {number}{complement}{name}"
        case "Artikel":
            return f"{article} {number}{complement}{name}"
        case _:
            assert 0, parts


def render_lit_bahlow(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lit_bahlow("Lit-Bahlow", ["Namenlexikon"], defaultdict(str, {"V": "Gondrom"}))
    'Hans Bahlow: <i>Deutsches Namenlexikon</i>. Familien- und Vornamen nach Ursprung und Sinn erklärt. Gondrom Verlag, Bindlach 1991, 1993, 2004, ISBN 3-8112-0294-4'
    >>> render_lit_bahlow("Lit-Bahlow", ["Namenlexikon"], defaultdict(str, {"V": "Keyser"}))
    'Hans Bahlow: <i>Deutsches Namenlexikon</i>. Familien- und Vornamen nach Ursprung und Sinn erklärt. Keysersche Verlagsbuchhandlung, München 1967'
    >>> render_lit_bahlow("Lit-Bahlow", ["Namenlexikon"], defaultdict(str, {"V": "Suhrkamp", "A": "1"}))
    'Hans Bahlow: <i>Deutsches Namenlexikon</i>. Familien- und Vornamen nach Ursprung und Sinn erklärt. Suhrkamp, Frankfurt 1., 1972, ISBN 3-518-36565-7'
    >>> render_lit_bahlow("Lit-Bahlow", ["Namenlexikon"], defaultdict(str, {"V": "Suhrkamp", "A": "6"}))
    'Hans Bahlow: <i>Deutsches Namenlexikon</i>. Familien- und Vornamen nach Ursprung und Sinn erklärt. Suhrkamp, Frankfurt 2.-6., 1976-1981, ISBN 3-518-36565-7'
    """
    kwargs = {
        "Autor": "Hans Bahlow",
        "Titel": "Deutsches Namenlexikon",
        "TitelErg": "Familien- und Vornamen nach Ursprung und Sinn erklärt",
    }
    match data["V"]:
        case "Gondrom":
            kwargs |= {
                "Verlag": "Gondrom Verlag",
                "Ort": "Bindlach",
                "Jahr": "1991, 1993, 2004",
                "ISBN": "3-8112-0294-4",
            }
        case "Keyser":
            kwargs |= {"Verlag": "Keysersche Verlagsbuchhandlung", "Ort": "München", "Jahr": "1967"}
        case "Suhrkamp":
            # Note: We cannot add the "ISBN" key here, even if it's the same for both A=1 and A=6, because the order of items in the dict matters.
            kwargs |= {"Verlag": "Suhrkamp", "Ort": "Frankfurt"}
            match data["A"]:
                case "1":
                    kwargs |= {"Auflage": "1.", "Jahr": "1972", "ISBN": "3-518-36565-7"}
                case "6":
                    kwargs |= {"Auflage": "2.-6.", "Jahr": "1976-1981", "ISBN": "3-518-36565-7"}

    return render_literatur("Literatur", [], defaultdict(str, kwargs))


def render_lit_linnartz(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lit_linnartz("Lit-Linnartz", ["Unsere Familiennamen"], defaultdict(str, {"A": "1", "B": "1"}))
    'Kaspar Linnartz: <i>Unsere Familiennamen</i>. Zehntausend Berufsnamen im Abc erklärt. 1. Auflage. Band 1, Ferdinand Dümmler Verlag, Bonn und Berlin 1936'
    """
    return f"Kaspar Linnartz: {italic(parts[0])}. Zehntausend Berufsnamen im Abc erklärt. {data['A']}. Auflage. Band {data['B']}, Ferdinand Dümmler Verlag, Bonn und Berlin 1936"


def render_literatur(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_literatur("Literatur", [], defaultdict(str, {"Autor": "Max Mustermann", "Titel": "Aspekte modernen Wikipädisierens", "Herausgeber": "Bernd Beispiel", "Sammelwerk": "Soziologie der Wikipädianer", "Verlag": "Wikipedia-Press", "Ort": "Musterstadt", "Jahr": "2003", "ISBN": "978-3-9801412-1-5", "Seiten": "213–278"}))
    'Max Mustermann: <i>Aspekte modernen Wikipädisierens</i>. In: Bernd Beispiel (Herausgeber): <i>Soziologie der Wikipädianer</i>. Wikipedia-Press, Musterstadt 2003, ISBN 978-3-9801412-1-5, Seite 213–278'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Autor": "Max Mustermann", "Titel": "Semantischer Kollaps bei Löschdiskussionen", "Sammelwerk": "Journal of Wikipedianism", "Band": "Bd. 2", "Nummer": "3", "Jahr": "2006", "Seiten": "17-67"}))
    'Max Mustermann: <i>Semantischer Kollaps bei Löschdiskussionen</i>. In: <i>Journal of Wikipedianism</i>. Bd. 2, Nummer 3, 2006, Seite 17-67'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Autor": "Max Mustermann", "Titel": "Wikipedia wohin?", "Sammelwerk": "FAZ", "Tag": "1", "Monat": "Februar", "Jahr": "2003", "ISSN": "0174-4909", "Seiten": "3"}))
    'Max Mustermann: <i>Wikipedia wohin?</i>. In: <i>FAZ</i>. 1. Februar 2003, ISSN 0174-4909, Seite 3'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Autor": "Max Mustermann", "Titel": "Wikipedia wohin?", "Sammelwerk": "FAZ", "Tag": "1", "Monat": "02", "Jahr": "2003", "ISSN": "0174-4909", "Seiten": "3"}))
    'Max Mustermann: <i>Wikipedia wohin?</i>. In: <i>FAZ</i>. 1. Februar 2003, ISSN 0174-4909, Seite 3'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Herausgeber": "The Oriental Institute, Chicago", "Titel": "The Assyrian Dictionary of the Oriental Institute of the University of Chicago", "Verlag": "J. J. Augustin, Glückstadt", "Ort": "Chicago, Illinois", "Originalsprache": "en-US"}))
    'The Oriental Institute, Chicago (Herausgeber): <i>The Assyrian Dictionary of the Oriental Institute of the University of Chicago</i>. J. J. Augustin, Glückstadt, Chicago, Illinois'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Autor": "John Doe", "Titel": "Einführung in die Trollerei", "Originaltitel": "Introduction to Trolling", "Originalsprache": "en-US", "Verlag": "Wikipedia-Press", "Ort": "Musterstadt", "Jahr": "2003", "ISBN": "978-3-9801412-1-5"}))
    'John Doe: <i>Einführung in die Trollerei</i>. Wikipedia-Press, Musterstadt 2003 (Originaltitel: <i>Introduction to Trolling</i>), ISBN 978-3-9801412-1-5'
    >>> render_literatur("Literatur", [], defaultdict(str, {"Titel": "Augsburg", "Sammelwerk": "Die Chroniken der deutschen Städte vom vierzehnten bis in's sechzehnte Jahrhundert", "WerkErg": "Auf Veranlassung und mit Unterstützung Seiner Majestaet des Königs von Bayern, Maximilian II. hrsg. durch die Historische Commission bei der Königl. Academie der Wissenschaften", "Band": "LII", "Verlag": "Hirzel", "Ort": "Leipzig", "Jahr": "1866"}))
    "<i>Augsburg</i>. In: <i>Die Chroniken der deutschen Städte vom vierzehnten bis in's sechzehnte Jahrhundert</i>. Auf Veranlassung und mit Unterstützung Seiner Majestaet des Königs von Bayern, Maximilian II. hrsg. durch die Historische Commission bei der Königl. Academie der Wissenschaften. LII, Hirzel, Leipzig 1866"
    """
    phrase = ""

    keys_italic = {"Sammelwerk", "Titel"}
    keys_prefix = {"Herausgeber": "In:", "Nummer": "Nummer", "ISBN": "ISBN", "ISSN": "ISSN", "Seiten": "Seite"}
    keys_suffix = {"Herausgeber": "(Herausgeber)"}
    keys_eol = {
        "Autor": ":",
        "Herausgeber": ":",
        "Sammelwerk": ".",
        "Tag": ".",
        "Titel": ".",
        "TitelErg": ".",
        "WerkErg": ".",
    }
    keys_ignored = {"Online", "Originalsprache", "Originaltitel"}
    months = [
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]

    for key, value in data.items():
        if key in keys_ignored:
            continue
        if key == "Sammelwerk" and "Herausgeber" not in data:
            phrase += " In:"
        if prefix := keys_prefix.get(key):
            phrase += f" {prefix} {value}"
        elif key == "Monat" and data["Monat"].isdigit():
            phrase += f" {months[int(data['Monat']) - 1]}"
        else:
            phrase += f" {italic(value) if key in keys_italic else value}"
        if key == "Jahr" and "Originaltitel" in data:
            phrase += f" (Originaltitel: {italic(data['Originaltitel'])})"

        if suffix := keys_suffix.get(key):
            phrase += f" {suffix}"

        phrase += keys_eol.get(key, "" if key in {"Monat", "Ort"} and "Jahr" in data else ",")

    return phrase.strip(" ,").removeprefix("In: ")


def render_Ut(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_Ut("Üt", ["grc", "διάλογος", "diálogos"], defaultdict(str))
    '<i>διάλογος (diálogos)</i>'
    >>> render_Ut("Üt", ["grc", "διαλέγομαι", "dialégesthai", "διαλέγεσθαι"], defaultdict(str))
    '<i>διαλέγεσθαι (dialégesthai)</i>'

    TODO: enable back with #1746
    >> render_Ut("Üt", ["bg", "карам велосипед"], defaultdict(str))
    '<i>карам велосипед (karam velosiped)</i>'
    """
    lang = parts.pop(0)
    phrase = parts[0] if len(parts) < 3 else parts[2]

    def transliterate(a: str, b: str) -> str:
        return ""

    phrase += f" ({parts[1] if len(parts) > 1 else transliterate(lang, parts[0])})"
    return italic(phrase)


def render_Uxx4(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_Uxx4("Üxx4", ["ar", "مسجد"], defaultdict(str, {"v":"مَسْجِد", "d":"masğid", "b":"Moschee"}))
    'مَسْجِد (DMG: masğid) ‚Moschee‘'
    >>> render_Uxx4("Üxx4", ["ur"], defaultdict(str, {"2": "فن", "v":"فَنّ", "d":"fann", "b":"Kunst"}))
    'فَنّ (ALA-LC: fann) ‚Kunst‘'
    >>> render_Uxx4("Üxx4", ["he", "שבת"], defaultdict(str, {"v":"שַׁבָּת", "d":"šabāṯ", "b":"Ruhepause"}))
    'שַׁבָּת (CHA: šabāṯ) ‚Ruhepause‘'
    >>> render_Uxx4("Üxx4", ["yi", "רעגן־בױגן"], defaultdict(str, {"d":"regn-boygn", "b":"Regenbogen"}))
    'רעגן־בױגן (YIVO: regn-boygn) ‚Regenbogen‘'
    >>> render_Uxx4("Üxx4", ["syr", "ܡܫܝܚܐ"], defaultdict(str, {"v":"ܡܫܺܝܚܳܐ", "d":"mšiḥāʾ", "b":"Messias"}))
    'ܡܫܺܝܚܳܐ (ALA-LC: mšiḥāʾ) ‚Messias‘'
    >>> render_Uxx4("Üxx4", ["fr", "ܡܫܝܚܐ"], defaultdict(str, {"v":"ܡܫܺܝܚܳܐ", "d":"mšiḥāʾ", "b":"Messias"}))
    'ܡܫܺܝܚܳܐ (mšiḥāʾ) ‚Messias‘'
    >>> render_Uxx4("Üxx4?", ["fr", "ܡܫܝܚܐ"], defaultdict(str, {"v":"ܡܫܺܝܚܳܐ", "d":"mšiḥāʾ", "b":"Messias"}))
    '<b>?</b>&nbsp;ܡܫܺܝܚܳܐ (mšiḥāʾ) ‚Messias‘'
    """
    language = parts.pop(0)
    phrase = parts.pop(0) if parts else ""
    phrase = data.get("v", data.get("2", phrase))
    if tpl == "Üxx4?":
        phrase = f"{strong('?')}&nbsp;{phrase}"
    if "d" in data:
        if language in ("ar", "fa", "ha", "ota", "pnb"):
            phrase += f" (DMG: {data['d']})"
        elif language in ("he"):
            phrase += f" (CHA: {data['d']})"
        elif language in ("yi"):
            phrase += f" (YIVO: {data['d']})"
        elif language in ("jrb", "ps", "syr", "ur"):
            phrase += f" (ALA-LC: {data['d']})"
        else:
            phrase += f" ({data['d']})"

    if "b" in data:
        phrase += f" ‚{data['b']}‘"
    return phrase


def render_Uxx5(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_Uxx5("Üxx5", ["grc", "anḗr, andrós", "ἀνήρ, ἀνδρός", "ἀνήρ"], defaultdict(str))
    'ἀνήρ, ἀνδρός (anḗr, andrós)'
    """
    return f"{parts[2]} ({parts[1]})"


def vorsilbe(verb: str) -> str:
    """
    Source: https://de.wiktionary.org/w/index.php?title=Modul:Verb&oldid=10212947#L-123 (2025-01-30 21:13)

    >>> vorsilbe("")  # slang >= 14
    ''
    >>> vorsilbe("nebeneinanderstehen")  # slang >= 13
    'nebeneinander'
    >>> vorsilbe("übereinanderlegen")  # slang >= 12
    'übereinander'
    >>> vorsilbe("auseinanderbrechen")  # slang >= 11
    'auseinander'
    >>> vorsilbe("zueinanderstehen")  # slang >= 10
    'zueinander'
    >>> vorsilbe("gegenüberliegen")  # slang >= 9
    'gegenüber'
    >>> vorsilbe("vornüberfallen")  # slang >= 8
    'vornüber'
    >>> vorsilbe("schwarzmalen")  # slang >= 7
    'schwarz'
    >>> vorsilbe("hineintun")  # slang >= 6
    'hinein'
    >>> vorsilbe("übriglassen")  # slang >= 5
    'übrig'
    >>> vorsilbe("überzählen")  # slang >= 4
    'über'
    >>> vorsilbe("verbeugen")  # slang >= 3
    'ver'
    >>> vorsilbe("abfotografieren")  # slang >= 2
    'ab'
    >>> vorsilbe("bankrottieren")  # no slang condition taken
    'bankrottieren'
    """
    length = len(verb)
    slang = 0
    prefix = ""

    if verb.endswith("tun"):
        slang = length - 3
    elif length >= 7:
        slang = length - 4

    for prefix_len, prefixes in VORSILBE_DATA:
        if slang >= prefix_len and (prefix := verb[:prefix_len]) in prefixes:
            if prefix_len == 14:
                # TODO: remove when a use case is found and a doctest is added
                assert 0, f"slang >= {prefix_len}"
            return prefix

    return verb


def render_verbherkunft(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str), word="anflunkern")
    'gebildet aus dem Verbzusatz <i>an</i> und dem Verb <i>flunkern</i>'

    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"W": "Adjektiv", "V": "allein"}), word="alleinstehen")
    'gebildet aus dem Adjektiv <i>allein</i> als Verbzusatz und dem Verb <i>stehen</i>'
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"W": "Substantiv", "V": "Kopf"}), word="kopfstehen")
    'gebildet aus dem Substantiv <i>Kopf</i> als Verbzusatz und dem Verb <i>stehen</i>'
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"W": "Partikel"}), word="abaasen")
    'gebildet aus der Partikel <i>ab</i> als Verbzusatz und dem Verb <i>aasen</i>'
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"W": "Adverb"}), word="antragen")
    'gebildet aus der Partikel <i>an</i> als Verbzusatz und dem Verb <i>tragen</i>'
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"W": "Präposition"}), word="abflauen")
    'gebildet aus der Partikel <i>ab</i> als Verbzusatz und dem Verb <i>flauen</i>'

    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"2": "u"}), word="beruhen")
    'Derivation (Ableitung) zum Verb <i>ruhen</i> mit dem Derivatem (Ableitungsmorphem) <i>be-</i>'
    >>> render_verbherkunft("Verbherkunft", [], defaultdict(str, {"2": "u", "V": "de"}), word="defragmentieren")
    'Derivation (Ableitung) zum Verb <i>fragmentieren</i> mit dem Derivatem (Ableitungsmorphem) <i>de-</i>'
    """
    art = data["2"] or (parts[0] if parts else "t")
    wortart = data["W"]
    vorspann = data["V"]
    ableitung = data["A"]
    wortart2 = data["W2"]
    strlen = len(word)
    retp = ""
    partikel = ""
    dativ = "dem "

    partikel = vorspann if (vorspann and vorspann >= "A") else vorsilbe(word)
    vlen = len(partikel)
    verbname = word[vlen:strlen]

    if art == "t":
        retp += "gebildet aus "
        if wortart:
            if wortart in {"Präposition", "Adverb"}:
                wortart = "Partikel"
                dativ = "der "
            elif wortart in {"Partikel", "Partikelverb", "Interjektion"}:
                dativ = "der "
            retp += f"{dativ}{wortart} "
            retp += f"{italic(partikel)} als Verbzusatz"
        else:
            retp += f"dem Verbzusatz {italic(partikel)}"

        if wortart2:  # fiktives Verb
            retp += f" und der Ableitung zum {wortart2} "
            retp += f"{italic(ableitung)} durch Konversion"
        else:
            retp += f" und dem Verb {italic(verbname)}"
    elif art == "u":
        if not vorspann and ableitung:
            vorspann = ableitung
            vlen = len(vorspann)
            verbname = word[vlen:strlen]

        retp = "Derivation (Ableitung) "
        retp += (
            f"zum {wortart} {italic(ableitung)} mit "
            if wortart in {"Adjektiv", "Substantiv", "Verb"}
            else f"zum Verb {italic(verbname)} mit "
        )
        retp += "dem Derivatem (Ableitungsmorphem) "

        if verbname == "eln":
            retp += "-el und der Flexionsendung -n"
        elif verbname in {"en", "n"}:
            retp = "Derivation (Ableitung) "
            retp += f"vom {wortart} {italic(ableitung)} durch Konversion "
            retp += f"mit der Flexionsendung {italic(f'-{verbname}')}"
        elif verbname == "ifizieren":
            retp += "-ifizier und der Flexionsendung -en"
        elif verbname == "isieren":
            retp += "-isier und der Flexionsendung -en"
        elif verbname == "ieren":
            retp += "-ier und der Flexionsendung -en"
        else:
            if ableitung and word[:vlen].lower() == ableitung.lower():
                retp = f"untrennbare Zusammensetzung aus {dativ}"
                retp += f"{wortart} {italic(vorspann)} und dem Verb {italic(verbname)}"
            else:
                retp += italic(f"{partikel}-")

    return retp


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("flexion", ["dass", "Reform 1996"], defaultdict(str), word="daß")
    'dass'
    >>> render_variant("flexion", ["profilierend"], defaultdict(str), word="profilierende")
    'profilierend'
    >>> render_variant("flexion", [], defaultdict(str, {"1": "rauspumpen"}), word="pumpt raus")
    'rauspumpen'
    >>> render_variant("flexion", ["rauspumpen#rauspumpen_(Deutsch)"], defaultdict(str), word="pumpt raus")
    'rauspumpen'
    >>> render_variant("flexion", [], defaultdict(str, {"Verb": "ansprechen", "Partizip": "angesprochen"}), word="angesprochenen")
    'ansprechen'
    """
    variant = data["1"] or data["Verb"] or parts[0]
    return variant.split("#", 1)[0]


template_mapping = {
    "Arab": render_foreign_lang_simple,
    "Bibel": render_bibel,
    "Farsi": render_foreign_lang_simple,
    "Hebr": render_foreign_lang,
    "K": render_K,
    "Lit-Bahlow": render_lit_bahlow,
    "Lit-Linnartz": render_lit_linnartz,
    "Literatur": render_literatur,
    "Paschto": render_foreign_lang,
    "Ref-dejure": render_ref_dejure,
    "Urdu": render_foreign_lang,
    "Üt": render_Ut,
    "Ü?": render_Ut,
    "Üt?": render_Ut,
    "Üxx4": render_Uxx4,
    "Üxx4?": render_Uxx4,
    "Üxx5": render_Uxx5,
    "Verbherkunft": render_verbherkunft,
    #
    # Variants
    #
    "__variant__flexion": render_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
