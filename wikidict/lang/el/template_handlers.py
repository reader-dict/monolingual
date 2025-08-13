from collections import defaultdict

from ...user_functions import concat, extract_keywords_from, italic, parenthesis, strong
from .langs import langs
from .topos.kind import kind
from .topos.where import where


def get_lang(lang: str) -> str:
    return italic(str(langs[lang]["frm"]))


def render_bor(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_bor("bor", ["fr", "en"], defaultdict(str))
    '(άμεσο δάνειο) <i>γαλλική</i>'
    >>> render_bor("bor", ["fr", "en", "Européen"], defaultdict(str))
    '(άμεσο δάνειο) <i>γαλλική</i> Européen'
    >>> render_bor("bor", ["pt", "en", "China"], defaultdict(str, {"τύπος": "τόπος"}))
    '(άμεσο δάνειο) <i>πορτογαλική</i> China'
    """
    text = f"(άμεσο δάνειο) {get_lang(parts.pop(0))}"
    if len(parts) > 1:
        text += f" {parts[1]}"
    return text


def render_ety(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ety("ety", ["ru", "el"], defaultdict(str))
    '<i>ρωσική</i>'
    >>> render_ety("ety", ["ru", "el", "Акопян"], defaultdict(str))
    '<i>ρωσική</i> Акопян'
    >>> render_ety("ety", ["ru", "el", "Акопян"], defaultdict(str, {"tr": "Akopján", "t": "Ακοπιάν", "τύπος": "επώνυμο"}))
    '<i>ρωσική</i> Акопян (Akopján, Ακοπιάν)'
    >>> render_ety("ety", ["ru", "el", "Акопян"], defaultdict(str, {"tnl": "Χακομπιάν, Ακοπιάν"}))
    '<i>ρωσική</i> Акопян (Χακομπιάν, Ακοπιάν)'
    """
    text = italic(str(langs[parts.pop(0)]["frm"]))
    parts.pop(0)  # Remove the other lang

    if parts:
        text += f" {parts[0]}"

        more: list[str] = []
        if tr := data["tr"]:
            more.append(tr)
        if t := data["t"]:
            more.append(t)
        if tnl := data["tnl"]:
            more.append(tnl)
        if more:
            text += f" ({', '.join(more)})"

    return text


def render_inh(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_inh("inh", ["ang", "en"], defaultdict(str))
    '<i>αγγλοσαξονική</i>'
    """
    return get_lang(parts[0])


def render_π(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_π("π", ["λέξη"], defaultdict(str))
    'λέξη'
    >>> render_π("π", ["επί-"], defaultdict(str, {".1": "επ"}))
    'επ'
    >>> render_π("π", ["-ism", "en", "imsss"], defaultdict(str))
    'imsss'
    >>> render_π("π", ["-ism", "en", "imsss"], defaultdict(str, {"000": "-"}))
    ''
    """
    if data["000"] == "-":
        return ""
    return data[".1"] or parts[2 if len(parts) == 3 else 0]


def render_γρ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_γρ("γρ", ["πολυπαλλόμενο σύμφωνο", "συνών"], defaultdict(str))
    '<i>συνώνυμο του</i> <b>πολυπαλλόμενο σύμφωνο</b>'
    >>> render_γρ("γρ", ["τραπεζομάντιλο"], defaultdict(str))
    '<i>άλλη γραφή του</i> <b>τραπεζομάντιλο</b>'
    >>> render_γρ("γρ", ["ελαιόδενδρο", "μορφή"], defaultdict(str))
    '<i>άλλη μορφή του</i> <b>ελαιόδενδρο</b>'
    >>> render_γρ("γρ", ["ελαιόδενδρο", "πολυ"], defaultdict(str, {"εμφ": "ελαιόδενδρο(ν)"}))
    '<i>πολυτονική γραφή του</i> <b>ελαιόδενδρο(ν)</b>'
    >>> render_γρ("γρ", ["ποιέω", "ασυν", "grc"], defaultdict(str))
    '<i>ασυναίρετη μορφή του</i> <b>ποιέω</b>'
    >>> render_γρ("γρ", ["ποιέω", "ασυν", "grc"], defaultdict(str, {"εμφ": "ποι-έω"}))
    '<i>ασυναίρετη μορφή του</i> <b>ποι-έω</b>'
    >>> render_γρ("γρ", ["colour", "", "en"], defaultdict(str))
    '<i>άλλη γραφή του</i> <b>colour</b>'
    >>> render_γρ("γρ", ["colour", "freestyle text", "en"], defaultdict(str))
    '<i>freestyle text</i> <b>colour</b>'
    """
    desc = parts[1] if len(parts) > 1 else ""
    desc = {
        "": "άλλη γραφή του",
        "απλοπ": "απλοποιημένη γραφή του",
        "μη απλοπ": "απλοποιημένη γραφή του",
        "ασυν": "ασυναίρετη μορφή του",
        "ετυμ": "ετυμολογική γραφή του",
        "μονο": "μονοτονική γραφή του",
        "μορφή": "άλλη μορφή του",
        "πολυ": "πολυτονική γραφή του",
        "πολ": "πολυτονική γραφή του",
        "παρωχ": "παρωχημένη γραφή του",
        "σνρ": "συνηρημένη μορφή του",
        "συνων": "συνώνυμο του",
        "συνών": "συνώνυμο του",
    }.get(desc, desc)
    return f"{italic(desc)} {strong(data['εμφ'] or parts[0])}"


def render_βλ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_βλ("βλ", [], defaultdict(str))
    '<i>→ δείτε τη λέξη</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"0": "-"}))
    '<i>→ δείτε</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"και": "1"}))
    '<i>→ και δείτε τη λέξη</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"και": "2"}))
    '<i>→ δείτε και τη λέξη</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"πθ": "1"}))
    '<i>→ δείτε παράθεμα στο</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"πθ": "1", "και": "2"}))
    '<i>→ δείτε και παράθεμα στο</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"όρος": "1"}))
    '<i>→ δείτε τους όρους</i>'
    >>> render_βλ("βλ", [], defaultdict(str, {"όρος": "..."}))
    '<i>→ δείτε ...</i>'
    >>> render_βλ("βλ", ["a", "b", "c"], defaultdict(str, {"όρος": "1", "γλ": "en"}))
    '<i>→ δείτε τους όρους</i> a, b<i> και </i>c'
    """
    text = "→"
    no_prefix = "πθ" not in data and "όρος" not in data and "0"

    if data["και"] == "1":
        text += " και"
    if data["0"] == "-":
        no_prefix = False
    text += " δείτε"
    if data["και"] == "2":
        text += " και"
    if no_prefix:
        text += " τις λέξεις" if len(parts) > 1 else " τη λέξη"

    if data["πθ"]:
        text += " παράθεμα στο"
    elif όρος := data["όρος"]:
        text += f" {'τους όρους' if όρος == '1' else όρος}"

    following = (" " + concat(parts, ", ", last_sep=italic(" και "))) if parts else ""
    return f"{italic(text)}{following}"


def render_μεγ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_μεγ("μεγ", [], defaultdict(str))
    '<i>μεγεθυντικό του</i>'
    >>> render_μεγ("μεγ", ["γυναίκα"], defaultdict(str))
    '<i>μεγεθυντικό του</i> γυναίκα'
    >>> render_μεγ("μεγ", ["casa", "ona", "es"], defaultdict(str))
    'casa + <i>μεγεθυντικό επίθημα</i> -ona'
    >>> render_μεγ("μεγ", ["casa", "ona", "es", "cas(a)"], defaultdict(str))
    'cas(a) + <i>μεγεθυντικό επίθημα</i> -ona'
    >>> render_μεγ("μεγ", ["casa", "ona", "es"], defaultdict(str, {"4": "cas(a)"}))
    'cas(a) + <i>μεγεθυντικό επίθημα</i> -ona'
    """
    if data["4"]:
        parts[0] = data["4"]
    elif len(parts) == 4:
        parts[0] = parts[3]

    prefix = suffix = ""
    try:
        prefix, suffix = parts[:2]
    except ValueError:
        if parts:
            prefix = parts[0]

    if suffix:
        return f"{prefix} + {italic('μεγεθυντικό επίθημα')} -{suffix}"

    return f"{italic('μεγεθυντικό του')} {prefix}".rstrip()


def render_υπο(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_υπο("μεγ", ["βουνό", "αλάκι"], defaultdict(str))
    'βουνό + <i>υποκοριστικό επίθημα</i> -αλάκι'
    >>> render_υπο("μεγ", ["βουνό", "αλάκι", "grc"], defaultdict(str))
    'βουνό + <i>υποκοριστικό επίθημα</i> -αλάκι'
    >>> render_υπο("μεγ", ["βουνό", "αλάκι", "", "βουν(ό)"], defaultdict(str))
    'βουν(ό) + <i>υποκοριστικό επίθημα</i> -αλάκι'
    >>> render_υπο("μεγ", ["βουνό", "αλάκι"], defaultdict(str, {"4": "βουν(ό)"}))
    'βουν(ό) + <i>υποκοριστικό επίθημα</i> -αλάκι'
    >>> render_υπο("μεγ", ["κουτάβι", "", "κουτάβ(ι)"], defaultdict(str), word="κουταβάκι")
    'κουτάβ(ι) + <i>υποκοριστικό επίθημα</i> -άκι'
    """
    if data["4"]:
        parts[0] = data["4"]
    elif len(parts) == 4:
        parts[0] = parts[3]

    prefix = suffix = ""
    try:
        prefix, suffix = parts[:2]
    except ValueError:
        if parts:
            prefix = parts[0]

    if not suffix and len(parts) > 2:
        prefix = parts[2]
        suffix = word[len(prefix.split("(", 1)[0]) :]

    return f"{prefix} + {italic('υποκοριστικό επίθημα')} -{suffix}"


def render_ελνστ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ελνστ("ελνστ", [], defaultdict(str))
    '(<i>ελληνιστική κοινή</i>)'
    >>> render_ελνστ("ελνστ", [], defaultdict(str, {"0": "-"}))
    '<i>ελληνιστική κοινή</i>'
    >>> render_ελνστ("ελνστ", [""], defaultdict(str), word="-ης")
    '(<i>ελληνιστική κοινή</i>) -ης'
    >>> render_ελνστ("ελνστ", ["πολυχρονία"], defaultdict(str))
    '(<i>ελληνιστική κοινή</i>) πολυχρονία'
    """
    text = italic("ελληνιστική κοινή")
    if not data["0"]:
        text = parenthesis(text)
    if parts:
        if not parts[0]:
            parts[0] = word
        text += f" {parts[0]}"
    return text


def render_etym(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etym("etym", ["grc", "el", "ἄλαστος"], defaultdict(str))
    '<i>αρχαία ελληνική</i> ἄλαστος'
    >>> render_etym("etym", ["enm", "en", "dene"], defaultdict(str, {"tnl": "κυριολεκτικά: κοιλάδα, τοπωνυμικό για αυτόν που έμενε στις περιοχές Dean, Deen ή Dean της Αγγλίας"}))
    '<i>μέση αγγλική</i> dene (κυριολεκτικά: κοιλάδα, τοπωνυμικό για αυτόν που έμενε στις περιοχές Dean, Deen ή Dean της Αγγλίας)'

    >>> render_etym("μτφδ", [], defaultdict(str))
    '(μεταφραστικό δάνειο)'
    >>> render_etym("μτφδ", ["en"], defaultdict(str))
    '(μεταφραστικό δάνειο) <i>αγγλική</i>'
    >>> render_etym("μτφδ", ["en", "el"], defaultdict(str))
    '(μεταφραστικό δάνειο) <i>αγγλική</i>'
    >>> render_etym("μτφδ", ["en", "el"], defaultdict(str, {"nodisplay": "1"}))
    ''
    >>> render_etym("μτφδ", ["en", "el"], defaultdict(str, {"000": "-"}))
    ''
    >>> render_etym("μτφδ", ["en", "el", "skyscraper"], defaultdict(str, {"00": "-"}))
    '(μεταφραστικό δάνειο) <i>αγγλική</i> skyscraper'
    >>> render_etym("μτφδ", ["fr", "el", "-culture"], defaultdict(str, {"text": "1"}))
    'μεταφραστικό δάνειο από <i>τη γαλλική</i> -culture'
    >>> render_etym("μτφδ", ["fr", "el", "-culture"], defaultdict(str, {"κειμ": "1"}))
    'μεταφραστικό δάνειο από <i>τη γαλλική</i> -culture'

    >>> render_etym("δαν", ["en", "el", "skyscraper"], defaultdict(str, {"00": "-"}))
    '(άμεσο δάνειο) <i>αγγλική</i> skyscraper'
    >>> render_etym("δαν", ["it", "el", "-are", "-ar(e)"], defaultdict(str))
    '(άμεσο δάνειο) <i>ιταλική</i> -ar(e)'
    >>> render_etym("δαν", ["ota", "el", "آجر"], defaultdict(str, {"tr": "âcürr"}))
    '(άμεσο δάνειο) <i>οθωμανική τουρκική</i> آجر (âcürr)'

    >>> render_etym("λδαν", ["en", "el", "skyscraper"], defaultdict(str))
    '(λόγιο δάνειο) <i>αγγλική</i> skyscraper'
    >>> render_etym("λδαν", ["en", "el", "skyscraper"], defaultdict(str, {"0": "-"}))
    '<i>αγγλική</i> skyscraper'

    >>> render_etym("κλη", ["en", "el", "skyscraper"], defaultdict(str))
    '(κληρονομημένο) <i>αγγλική</i> skyscraper'
    >>> render_etym("κλη", ["", "σκαμνί"], defaultdict(str, {"π": "οακ", "α": "εν"}))
    '(κληρονομημένο)'
    >>> render_etym("κλη", ["en", "el", "skyscraper"], defaultdict(str, {"text": "1"}))
    'κληρονομημένο από <i>την</i> <i>αγγλική</i> skyscraper'

    >>> render_etym("σμσδ", ["fr", "el", "-gène"], defaultdict(str))
    '(σημασιολογικό δάνειο) <i>γαλλική</i> -gène'
    >>> render_etym("σμσδ", ["fr", "el", "-gène"], defaultdict(str, {"text": "1"}))
    'σημασιολογικό δάνειο από <i>τη γαλλική</i> -gène'
    >>> render_etym("σμσδ", ["en", "el", "-genous"], defaultdict(str, {"text": "1"}))
    'σημασιολογικό δάνειο από <i>την αγγλική</i> -genous'
    """
    if data["000"] == "-" or data["nodisplay"] == "1":
        return ""

    phrase = (
        "μεταφραστικό δάνειο"
        if tpl == "μτφδ"
        else "άμεσο δάνειο"
        if tpl == "δαν"
        else "λόγιο δάνειο"
        if tpl in {"λδαν", "lbor"}
        else "κληρονομημένο"
        if tpl == "κλη"
        else "σημασιολογικό δάνειο"
        if tpl == "σμσδ"
        else "ορθογραφικό δάνειο"
        if tpl == "ορθδ"
        else ""
    )
    key = "frm"
    if tpl != "etym":
        if data["0"] == "-":
            phrase = ""
        elif data["text"] != "1" and data["κειμ"] != "1":
            phrase = f"({phrase})"
        else:
            phrase += " από"
            if tpl in {"σμσδ", "μτφδ", "ορθδ"}:
                key = "apo"
            else:
                phrase += f" {italic('την' if tpl == 'κλη' else 'τη')}"

    if parts:
        if ln := parts.pop(0):
            phrase = f"{phrase} {italic(str(langs[ln][key]))}"
    if parts:
        parts.pop(0)  # Remove the lang
    if parts:
        phrase += f" {parts[-1]}"

    if tnl := (data["tnl"] or data["tr"] or data["t"]):
        phrase += f" ({tnl})"

    return phrase.strip()


def render_παθ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_παθ("παθ", [], defaultdict(str))
    '<i>παθητική φωνή</i>'
    >>> render_παθ("παθ", [], defaultdict(str, {"μπ": "1"}))
    '<i>μεσοπαθητική φωνή</i>'
    >>> render_παθ("παθ", [], defaultdict(str, {"μ": "1"}))
    '<i>μέση φωνή</i>'
    >>> render_παθ("παθ", ["λύνω"], defaultdict(str))
    '<i>παθητική φωνή του ρήματος</i> <b>λύνω</b>'
    >>> render_παθ("παθ", ["λύω"], defaultdict(str, {"μπ": "1"}))
    '<i>μεσοπαθητική φωνή του ρήματος</i> <b>λύω</b>'
    >>> render_παθ("παθ", ["αἱρῶ", "grc"], defaultdict(str, {"μπ": "1", "τύπος": "σνρ"}))
    '<i>μεσοπαθητική φωνή του συνηρημένου ρήματος</i> <b>αἱρῶ</b>'
    """
    phrase = "παθητική φωνή"
    if data["μπ"] == "1":
        phrase = "μεσοπαθητική φωνή"
    elif data["μ"] == "1":
        phrase = "μέση φωνή"

    if parts:
        verb = parts[0]
        if verb:
            if data["τύπος"] in ("σνρ", "συνηρημένο", "contr", "contracted"):
                phrase += " του συνηρημένου ρήματος"
            else:
                phrase += " του ρήματος"
            phrase = italic(phrase)
            phrase += f" {strong(verb)}"
    else:
        phrase = italic(phrase)

    return phrase


def render_ουσεπ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ουσεπ("ουσεπ α", [], defaultdict(str))
    '<i>ουσιαστικοποιημένο αρσενικό</i>'
    >>> render_ουσεπ("ουσεπ α", ["καλός"], defaultdict(str))
    '<i>ουσιαστικοποιημένο αρσενικό του επιθέτου</i> καλός'
    >>> render_ουσεπ("ουσεπ α", ["καλός", "grc"], defaultdict(str))
    '<i>ουσιαστικοποιημένο αρσενικό του επιθέτου</i> καλός'
    >>> render_ουσεπ("ουσεπ α", ["καλός", "grc", "καλός (καλόν)"], defaultdict(str))
    '<i>ουσιαστικοποιημένο αρσενικό του επιθέτου</i> καλός (καλόν)'
    >>> render_ουσεπ("ουσεπ α", ["δεδομένος"], defaultdict(str, {"μτχ": "1"}))
    '<i>ουσιαστικοποιημένο αρσενικό της μετοχής</i> δεδομένος'

    >>> render_ουσεπ("ουσεπ ο", [], defaultdict(str))
    '<i>ουσιαστικοποιημένο ουδέτερο</i>'

    >>> render_ουσεπ("ουσεπ θ", [], defaultdict(str))
    '<i>ουσιαστικοποιημένο θηλυκό</i>'
    """
    text = "ουσιαστικοποιημένο "
    match tpl.split(" ", 1)[1]:
        case "θ":
            text += "θηλυκό"
        case "α":
            text += "αρσενικό"
        case "ο":
            text += "ουδέτερο"

    if parts:
        text += f" {'της μετοχής' if data['μτχ'] == '1' else 'του επιθέτου'}"
        return f"{italic(text)} {parts[2 if len(parts) > 2 else 0]}"

    return italic(text)


def render_γραπτήεμφ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str))
    '(<i>μαρτυρείται από το</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"0": "-"}))
    'μαρτυρείται από το'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"nostyle": "1"}))
    'μαρτυρείται από το'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"ήδη": "1"}))
    '(<i>ήδη από το</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", ["2025"], defaultdict(str))
    '(<i>μαρτυρείται από το 2025</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", ["2025"], defaultdict(str, {"+": "η έκφραση"}))
    '(<i>η έκφραση μαρτυρείται από το 2025</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"αι": "17"}))
    '(<i>μαρτυρείται από τον 17ο αιώνα</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"αι": "5", ".": "πκε"}))
    '(<i>μαρτυρείται από τον 5ο αιώνα πκε</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"δεκ": "2025"}))
    '(<i>μαρτυρείται από τη δεκαετία του 2025</i>)'
    >>> render_γραπτήεμφ("γραπτήεμφ", [], defaultdict(str, {"δεκ": "2025"}))
    '(<i>μαρτυρείται από τη δεκαετία του 2025</i>)'
    """
    text = f"{plus} " if (plus := data["+"]) else ""
    text += "ήδη" if data["ήδη"] else "μαρτυρείται"
    text += " από"
    if αι := data["αι"]:
        text += f" τον {αι}ο αιώνα"
    elif δεκ := data["δεκ"]:
        text += f" τη δεκαετία του {δεκ}"
    else:
        text += " το"
        if parts:
            text += f" {parts[0]}"
    if dot := data["."]:
        text += f" {dot}"

    return text if data["0"] or data["nostyle"] else f"({italic(text)})"


def render_οπτδ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_οπτδ("οπτδ", ["fr", "el", "Gargamel"], defaultdict(str, {"text": "1"}))
    'οπτικό δάνειο από <i>τη γαλλική</i> Gargamel'
    >>> render_οπτδ("φων", ["fr", "el", "Gargamel"], defaultdict(str, {"text": "1"}))
    'φωνητική απόδοση για <i>τη γαλλική</i> Gargamel'
    """
    lang = langs[parts.pop(0)]
    parts.pop(0)  # Remove the source lang

    text = ""
    lang_key = "frm"
    if data["notext"] != "1":
        text = "οπτικό δάνειο" if tpl == "οπτδ" else "φωνητική απόδοση"
        if data["text"] == "1":
            lang_key = "apo"
            text += " για " if tpl == "φων" else " από "
        else:
            text = f"({text}) "
    text += italic(str(lang[lang_key]))

    if parts:
        text += f" {parts[0]}"
    return text


def render_τ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_τ("τ", ["en"], defaultdict(str), word="FUBAR")
    'FUBAR <small><sup>(en)</sup></small>'
    >>> render_τ("τ", ["en", "FUBAR"], defaultdict(str))
    'FUBAR <small><sup>(en)</sup></small>'
    >>> render_τ("τ", ["en", "FUBAR"], defaultdict(str, {"alt": "alt"}))
    'alt <small><sup>(en)</sup></small>'
    >>> render_τ("τ", ["en", "FUBAR"], defaultdict(str, {"show": "show"}))
    'show <small><sup>(en)</sup></small>'
    >>> render_τ("τ", ["en", "FUBAR"], defaultdict(str, {"tr": "tr"}))
    'FUBAR <small><sup>(en)</sup></small> (tr)'
    """
    text = data["alt"] or data["show"] or (parts[1] if len(parts) > 1 else word)
    text += f" <small><sup>({parts[0]})</sup></small>"
    if tr := data["tr"]:
        text += f" ({tr})"
    return text


def render_άγν(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_άγν("άγν", [], defaultdict(str))
    '<i>άγνωστης ετυμολογίας</i>'
    >>> render_άγν("άγν", ["en", "αβεβ"], defaultdict(str))
    '<i>αβέβαιης ετυμολογίας</i>'
    >>> render_άγν("άγν", ["en", "αβεβ"], defaultdict(str, {"0": "-"}))
    'αβέβαιης ετυμολογίας'
    """
    text = "αβέβαιης ετυμολογίας" if parts else "άγνωστης ετυμολογίας"
    if data["0"] != "-":
        text = italic(text)
    return text


def render_επιθ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_επιθ("επιθ", [], defaultdict(str))
    '(<i>επιθετικοποιημένο</i>)'
    >>> render_επιθ("επιθ", [], defaultdict(str, {"μτχ": "1"}))
    '(<i>επιθετικοποιημένη μετοχή</i>)'
    >>> render_επιθ("επιθ", [], defaultdict(str, {"ως": "1"}))
    '(<i>ως επίθετο</i>)'
    >>> render_επιθ("επιθ", [], defaultdict(str, {"λειτ": "1"}))
    '(<i>σε επιθετική λειτουργία</i>)'
    >>> render_επιθ("επιθ", [], defaultdict(str, {"0": "-"}))
    '<i>επιθετικοποιημένο</i>'
    """
    if data["μτχ"]:
        text = "επιθετικοποιημένη μετοχή"
    elif data["ως"]:
        text = "ως επίθετο"
    elif data["λειτ"]:
        text = "σε επιθετική λειτουργία"
    else:
        text = "επιθετικοποιημένο"
    text = italic(text)
    if data["0"] != "-":
        text = parenthesis(text)
    return text


def render_υποκ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_υποκ("υποκ", [], defaultdict(str))
    '(<i>υποκοριστικό</i>)'
    >>> render_υποκ("υποκ", ["αβγό"], defaultdict(str))
    '<i>υποκοριστικό του</i> αβγό'
    """
    if parts:
        return f"<i>υποκοριστικό του</i> {parts[0]}"
    return "(<i>υποκοριστικό</i>)"


def render_επικ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_επικ("επικ", [], defaultdict(str))
    '<i>επικός τύπος</i>'
    >>> render_επικ("επικ", ["καταμύω"], defaultdict(str))
    '<i>επικός τύπος του</i> καταμύω'
    """
    if parts:
        return f"<i>επικός τύπος του</i> {parts[0]}"
    return "<i>επικός τύπος</i>"


def render_αποδ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_αποδ("αποδ", ["he", "el", "דניּאל"], defaultdict(str, {"tr": "daniyél", "τύπος": "όνομα"}))
    '(απόδοση) <i>εβραϊκή</i> דניּאל (daniyél)'
    >>> render_αποδ("αποδ", ["mul", "el"], defaultdict(str, {"text": "1"}))
    'απόδοση για <i>διαγλωσσικούς όρους</i>'
    >>> render_αποδ("αποδ", ["mul", "el"], defaultdict(str, {"notext": "1"}))
    '<i>διαγλωσσική ορολογία</i>'
    """
    if data["notext"] == "1":
        return italic(str(langs[parts[0]]["frm"]))

    text = "απόδοση"
    if data["text"] == "1":
        text += " για"
        lang_key = "apo"
    else:
        text = parenthesis(text)
        lang_key = "frm"
    text += f" {italic(str(langs[parts[0]][lang_key]))}"
    if len(parts) > 2:
        text += f" {parts[2]}"
    if tr := data["tr"]:
        text += f" ({tr})"
    return text


def render_ελνστκ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ελνστκ("ελνστκ", [], defaultdict(str))
    '(<i>ελληνιστική κοινή</i>)'
    >>> render_ελνστκ("ελνστκ", ["οψ"], defaultdict(str))
    '(<i>όψιμη ελληνιστική κοινή</i>)'
    >>> render_ελνστκ("ελνστκ", ["σημασία"], defaultdict(str))
    '(<i>ελληνιστική σημασία</i>)'

    >>> render_ελνστκ("ελνστκ", [], defaultdict(str, {"0": "-"}))
    '<i>ελληνιστική κοινή</i>'
    """
    text = "ελληνιστική κοινή"
    if parts:
        match part := parts[0]:
            case "οψ" | "όψ" | "όψιμη":
                text = "όψιμη ελληνιστική κοινή"
            case "όψ σημ" | "οψ σημ":
                text = "όψιμη ελληνιστική σημασία"
            case "σημ" | "σημασία":
                text = "ελληνιστική σημασία"
            case "συνταγματικός":
                pass
            case _:
                raise ValueError(f"Unhandled ελνστκ {part!r}")

    text = italic(text)
    if data["0"] != "-":
        text = parenthesis(text)
    return text


def render_προέλ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_προέλ("προέλ", ["fr"], defaultdict(str))
    '<i>γαλλικής προέλευσης</i>'
    >>> render_προέλ("προέλ", ["tr", "fr"], defaultdict(str))
    '<i>τουρκικής προέλευσης γαλλικό</i>'
    >>> render_προέλ("προέλ", ["", "fr"], defaultdict(str))
    '<i>γαλλικό</i>'
    """
    text = ""
    lang1 = parts.pop(0)
    if parts:
        lang2 = parts[0]
        if lang1:
            text = f"{langs[lang1]['from']} {langs[lang2]['name']}"
        else:
            text = str(langs[lang2]["name"])
        # It seems the last letter of the lang name is always changed to "ό"
        text = f"{text[:-1]}ό"
    else:
        text = str(langs[lang1]["from"])
    return italic(text)


def render_ΔΦΑ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ΔΦΑ("ΔΦΑ", ["as.tʁa.kɑ̃"], defaultdict(str))
    ''
    >>> render_ΔΦΑ("ΔΦΑ", ["fr", "as.tʁa.kɑ̃"], defaultdict(str))
    'ΔΦΑ : /as.tʁa.kɑ̃/'
    """
    return "" if len(parts) < 2 else f"ΔΦΑ : /{parts[1]}/"


def render_ταξ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ταξ("ταξ", [""], defaultdict(str))
    '<i>ταξινομικός όρος -</i>'
    >>> render_ταξ("ταξ", ["", "ζ", "γένος"], defaultdict(str))
    '<i>ταξινομικός όρος - γένος:</i>'
    """
    text = "ταξινομικός όρος -"
    if len(parts) > 2:
        text += f" {parts[2]}:"
    return italic(text)


def render_γραφή(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_γραφή("γραφή", [], defaultdict(str))
    ''
    >>> render_γραφή("γραφή", ["λατ"], defaultdict(str))
    '<i>λατινικοί χαρακτήρες:</i>'
    """
    if not parts:
        return ""
    match part := parts[0]:
        case "αρα":
            text = "αραβικοί"
        case "ελλ":
            text = "ελληνικοί"
        case "κυρ":
            text = "κυριλλικοί"
        case "λατ":
            text = "λατινικοί"
        case _:
            raise ValueError(f"Unhandled γραφή {part=}")
    return italic(f"{text} χαρακτήρες:")


def render_ενεργ(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ενεργ("ενεργ", [], defaultdict(str))
    '<i>ενεργητική φωνή</i>'
    >>> render_ενεργ("ενεργ", ["αἱρέομαι"], defaultdict(str))
    '<i>ενεργητική φωνή</i> του ρήματος αἱρέομαι'
    """
    text = "<i>ενεργητική φωνή</i>"
    if parts:
        text += f" του ρήματος {parts[0]}"
    return text


def render_τόπος(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_τόπος("τόπος", ["el", "αρχαία πόλη", "Τουρκία"], defaultdict(str))
    'αρχαία πόλη της Τουρκίας'
    >>> render_τόπος("τόπος", ["el", "αρχαία πόλη", "Τουρκία"], defaultdict(str, {"0": "-"}))
    'αρχαία πόλη'
    >>> render_τόπος("τόπος", ["el", "αρχαία πόλη", "Τουρκία"], defaultdict(str, {"000": "-"}))
    ''

    >>> render_τόπος("τόπος", ["", "αεροδρόμιο", "Ελλάδα"], defaultdict(str))
    'αεροδρόμιο της Ελλάδας'
    >>> render_τόπος("τόπος", ["el", "", "Ελλάδα"], defaultdict(str, {"0": "-"}))
    'τοπωνύμιο'
    """
    # Source: https://el.wiktionary.org/w/index.php?title=Module:topos&oldid=6912182
    topos = parts[1] or "τοπωνύμιο"

    area = parts[2] if len(parts) > 2 else ""
    area_show = data["area_show"] or data["πού_εμφ"] or data["που_εμφ"]
    area_show_not = data["0"]
    nodisplay = data["nodisplay"] or data["000"]
    show = data["show"] or data["εμφ"]
    plural = data["pl"] or data["πλ"]

    if nodisplay:
        return ""

    if show:
        output = kind[topos]["word_pl"] if plural else show
    else:
        output = kind[topos]["word_pl" if plural else "word"]

    if (label := data["ετικ"]) == "1":
        output = f"(<i>{output}</i>)"
    elif label == "+":
        output = f"(<i>τοπωνύμιο, {output}</i>)"
    elif area and (area_show == "0" or not area_show_not):
        output = f"{output} {where[area]}"
    if label == "τοπ":
        output = f"(<i>τοπωνύμιο</i>) {output}"

    return output


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("ουδ του-πτώσειςΟΑΚεν", ["επίπεδος"], defaultdict(str), word="επίπεδο")
    'επίπεδος'
    >>> render_variant("ουδ του-πτώσειςΟΑΚπλ", ["-άδικος"], defaultdict(str), word="-άδικο")
    '-άδικος'
    >>> render_variant("ουδ του-πτώσηΓεν", ["έβδομος"], defaultdict(str), word="έβδομου")
    'έβδομος'
    >>> render_variant("ουδ του-πτώσηΓπλ", ["έβδομος"], defaultdict(str), word="έβδομου")
    'έβδομος'

    >>> render_variant("αρσ του-πτώσηΓεν", ["έβδομος"], defaultdict(str), word="έβδομου")
    'έβδομος'
    >>> render_variant("αρσ του-πτώσηΓπλ", ["έβδομος"], defaultdict(str), word="έβδομων")
    'έβδομος'

    >>> render_variant("πτώσειςΟΑΚπλ", ["Ελληνούπολη"], defaultdict(str), word="Ελληνουπόλεις")
    'Ελληνούπολη'

    >>> render_variant("πτώσηΑεν", ["επίπεδος"], defaultdict(str), word="επίπεδο")
    'επίπεδος'

    >>> render_variant("θηλ του", ["τσιγγάνος"], defaultdict(str), word="τσιγγάνα")
    'τσιγγάνος'
    >>> render_variant("θηλ του-πτώσειςΟΑΚπλ", ["έγγαμος"], defaultdict(str), word="έγγαμες")
    'έγγαμος'

    >>> render_variant("απαρ", ["ενεστώτα", "miror"], defaultdict(str), word="Μιρέλλα")
    'miror'
    >>> render_variant("απαρ", ["ενεστώτα", "miror", "en", "foo"], defaultdict(str), word="Μιρέλλα")
    'miror'
    """
    return parts[1] if tpl == "απαρ" else parts[-1] if parts else word


template_mapping = {
    "bor": render_bor,
    "ety": render_ety,
    "ετυ": render_ety,
    "inh": render_inh,
    "π": render_π,
    "p": render_π,
    "γρ": render_γρ,
    "βλ": render_βλ,
    "etym": render_etym,
    "σμσδ": render_etym,
    "κλη": render_etym,
    "δαν": render_etym,
    "λδαν": render_etym,
    "lbor": render_etym,
    "μτφδ": render_etym,
    "μεγ": render_μεγ,
    "υπο": render_υπο,
    "dim": render_υπο,
    "ετυμ-υποκ": render_υπο,
    "ελνστ": render_ελνστ,
    "παθ": render_παθ,
    "ουσεπ θ": render_ουσεπ,
    "ουσεπ α": render_ουσεπ,
    "ουσεπ ο": render_ουσεπ,
    "γραπτήεμφ": render_γραπτήεμφ,
    "οπτδ": render_οπτδ,
    "φων": render_οπτδ,
    "τ": render_τ,
    "t": render_τ,
    "επιθ": render_επιθ,
    "υποκ": render_υποκ,
    "άγν": render_άγν,
    "αγν": render_άγν,
    "επικ": render_επικ,
    "αποδ": render_αποδ,
    "απόδ": render_αποδ,
    "ελνστκ": render_ελνστκ,
    "προέλ": render_προέλ,
    "ΔΦΑ": render_ΔΦΑ,
    "ταξ": render_ταξ,
    "ορθδ": render_etym,
    "γραφή": render_γραφή,
    "ενεργ": render_ενεργ,
    "τόπος": render_τόπος,
    #
    # Variants
    #
    "__variant__ρημ τύπος": render_variant,
    "__variant__ρημ_τύπος": render_variant,
    "__variant__θηλ του": render_variant,
    "__variant__θηλ_του": render_variant,
    "__variant__θηλυκό του": render_variant,
    "__variant__θηλυκό_του": render_variant,
    "__variant__θηλ του-πτώσειςΟΑΚεν": render_variant,
    "__variant__θηλ_του-πτώσειςΟΑΚεν": render_variant,
    "__variant__θηλ του-πτώσηΓπλ": render_variant,
    "__variant__θηλ_του-πτώσηΓπλ": render_variant,
    "__variant__θηλ του-πτώσειςΟΑΚπλ": render_variant,
    "__variant__θηλ_του-πτώσειςΟΑΚπλ": render_variant,
    "__variant__θηλ του-πτώσηΓεν": render_variant,
    "__variant__θηλ_του-πτώσηΓεν": render_variant,
    "__variant__θηλ του-πτώσειςΟΚεν": render_variant,
    "__variant__θηλ_του-πτώσειςΟΚεν": render_variant,
    "__variant__ουδ του": render_variant,
    "__variant__ουδ_του": render_variant,
    "__variant__ουδ του-πτώσειςΟΑΚεν": render_variant,
    "__variant__ουδ_του-πτώσειςΟΑΚεν": render_variant,
    "__variant__ουδ του-πτώσειςΟΑΚπλ": render_variant,
    "__variant__ουδ_του-πτώσειςΟΑΚπλ": render_variant,
    "__variant__ουδ του-πτώσηΓπλ": render_variant,
    "__variant__ουδ_του-πτώσηΓπλ": render_variant,
    "__variant__ουδ του-πτώσηΓεν": render_variant,
    "__variant__ουδ_του-πτώσηΓεν": render_variant,
    "__variant__αρσ του": render_variant,
    "__variant__αρσ_του": render_variant,
    "__variant__αρσ του-πτώσηΓεν": render_variant,
    "__variant__αρσ_του-πτώσηΓεν": render_variant,
    "__variant__αρσ του-πτώσηΓπλ": render_variant,
    "__variant__αρσ_του-πτώσηΓπλ": render_variant,
    "__variant__αρσ του-πτώσηΑεν": render_variant,
    "__variant__αρσ_του-πτώσηΑεν": render_variant,
    "__variant__πτώση": render_variant,
    "__variant__πτώσηΔεν": render_variant,
    "__variant__πτώσηΑπλ": render_variant,
    "__variant__πτώσηΓπλ": render_variant,
    "__variant__πτώσηΑεν": render_variant,
    "__variant__πτώσηΚεν": render_variant,
    "__variant__πτώσεις": render_variant,
    "__variant__πτώσειςΟΑΚπλ": render_variant,
    "__variant__πτώσειςΟΚπλ": render_variant,
    "__variant__πτώσειςΓΑΚεν": render_variant,
    "__variant__πτώσειςΟΑΚεν": render_variant,
    "__variant__πληθ_του": render_variant,
    "__variant__πληθυντικός του": render_variant,
    "__variant__κλ": render_variant,
    "__variant__απαρ": render_variant,
    "__variant__πλ": render_variant,
    "__variant__infl": render_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
