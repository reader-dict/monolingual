import re
from collections import defaultdict

from ...user_functions import (
    capitalize,
    concat,
    extract_keywords_from,
    int_to_roman,
    italic,
    number,
    small_caps,
    strong,
    superscript,
    term,
    underline,
)
from ...utils import clean, process_special_pipe_template
from .ar import arabiser, racines_arabes
from .ar import pronunciation as ar_pron
from .langs import langs
from .transliterator import transliterate


def word_tr_sens(w: str, tr: str, sens: str, use_italic: bool = True) -> str:
    r = w if tr else (f"{italic(w)}" if use_italic else w)
    if tr:
        r += f", {italic(tr)}"
    if sens:
        r += f" («&nbsp;{sens}&nbsp;»)"
    return r


def render_1e_attestation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_1e_attestation("1e attestation", [], defaultdict(str, {"date": "1950", "titre": "Les Hirondelles", "lang": "fr"}))
    '<i>(1950)</i> Attesté dans <i>Les Hirondelles</i>'
    >>> render_1e_attestation("1e attestation", [], defaultdict(str, {"date": "1950", "titre": "Les Hirondelles", "lang": "fr", "auteur": "Pierre Dupont"}))
    '<i>(1950)</i> Attesté dans <i>Les Hirondelles</i> de Pierre Dupont'
    >>> render_1e_attestation("1e attestation", [], defaultdict(str, {"date": "1950", "titre": "Hirondelles", "lang": "fr", "déterminant": "les"}))
    '<i>(1950)</i> Attesté dans les <i>Hirondelles</i>'
    """
    phrase = f"{term(data['date'])} Attesté dans "
    if data["déterminant"]:
        phrase += f"{data['déterminant']} "
    phrase += italic(data["titre"])
    if data["auteur"]:
        phrase += f" de {data['auteur']}"
    return phrase


def render_2e(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_2e("2e", [], defaultdict(str))
    '2<sup>e</sup>'
    >>> render_2e("2e", ["partie"], defaultdict(str))
    '2<sup>e</sup> partie'
    >>> render_2e("3e", [], defaultdict(str))
    '3<sup>e</sup>'
    >>> render_2e("3e", ["partie"], defaultdict(str))
    '3<sup>e</sup> partie'
    """
    start = tpl[0]
    phrase = f"{start}{superscript('e')}"
    if parts:
        phrase += f" {parts[0]}"
    return phrase


def render_abreviation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_abreviation("abréviation", [], defaultdict(str))
    '<i>(Abréviation)</i>'
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str))
    '<i>(Abréviation)</i>'
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str, {"de": "dirham marocain"}))
    'Abréviation de <i>dirham marocain</i>'
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str, {"de": "accusatif", "texte": "'''acc'''usatif"}))
    "Abréviation de <i>'''acc'''usatif</i>"
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str, {"de": "accusatif", "texte": "'''acc'''usatif", "nolien": "oui"}))
    'Abréviation de <i>accusatif</i>'
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str, {"nolien": "oui"}))
    '<i>(Abréviation)</i>'
    >>> render_abreviation("abréviation", ["fr"], defaultdict(str, {"de": "engin spatial de maintenance", "lang": "fr", "m": "1"}))
    'abréviation de <i>engin spatial de maintenance</i>'
    """
    if not parts and not data:
        return italic("(Abréviation)")

    phrase = "abréviation" if "m" in data else "Abréviation"
    if data["texte"] and data["nolien"] not in ("1", "oui"):
        phrase += f" de {italic(data['texte'])}"
    elif data["de"]:
        phrase += f" de {italic(data['de'])}"
    else:
        phrase = term("Abréviation")
    return phrase


def render_acronyme(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_acronyme("acronyme", ["fr"], defaultdict(str))
    '<i>(Acronyme)</i>'
    >>> render_acronyme("acronyme", ["en"], defaultdict(str, {"de":"light-emitting diode"}))
    'Acronyme de <i>light-emitting diode</i>'
    >>> render_acronyme("acronyme", ["en", "fr"], defaultdict(str, {"de":"light-emitting diode", "texte":"Light-Emitting Diode"}))
    'Acronyme de <i>Light-Emitting Diode</i>'
    """
    if data["texte"] or data["de"]:
        return f"Acronyme de {italic(data['texte'] or data['de'])}"
    return italic("(Acronyme)")


def render_ar_ab(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_ab("ar-ab", ["lubné"], defaultdict(str))
    'لُبْنَى'
    """
    return arabiser.arabiser(parts[0])


def render_ar_cf(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_cf("ar-cf", ["ar-*i*â*ũ", "ar-ktb"], defaultdict(str))
    '<span style="line-height: 0px;"><span style="font-size:larger">كِتَابٌ</span></span> <small>(kitâbũ)</small> («&nbsp;livre, écriture ; pièce écrite&nbsp;»)'
    >>> render_ar_cf("ar-cf", ["ar-*i*a*ũ", "ar-jnn"], defaultdict(str))
    '<span style="line-height: 0px;"><span style="font-size:larger">جِنَنٌ</span></span> <small>(jinanũ)</small>'
    """
    scheme = arabiser.appliquer(parts[0], parts[1], var=parts[2] if len(parts) > 2 else "")
    w = arabiser.arabiser(scheme)

    racines_schemes_arabes = racines_arabes.racines_schemes_arabes

    sens = (
        f"ici, «&nbsp;{data['ici']}&nbsp;»"
        if data["ici"]
        else f"«&nbsp;{clean(racines_schemes_arabes[parts[1]][parts[0]][1])}&nbsp;»"
        if parts[1] in racines_schemes_arabes and parts[0] in racines_schemes_arabes[parts[1]]
        else ""
    )
    sens = f" ({sens})" if sens else ""

    return (
        f'<span style="line-height: 0px;"><span style="font-size:larger">{w}</span></span>'
        f" <small>({scheme})</small>"
        f"{sens}"
    )


def render_ar_mot(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_mot("ar-mot", ["elHasan_"], defaultdict(str))
    '<span style="line-height: 0px;"><span style="font-size:larger">الحَسَن</span></span> <small>(elHasan_)</small>'
    """
    return f'<span style="line-height: 0px;"><span style="font-size:larger">{arabiser.arabiser(parts[0])}</span></span> <small>({parts[0]})</small>'


def render_ar_root(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_root("ar-racine/nom", ["ar-ktb"], defaultdict(str))
    "كتب: relatif à l'action d'écrire, relier"
    """
    return f"{arabiser.arabiser(parts[0].split('-')[1])}: {racines_arabes.racines_schemes_arabes[parts[0]]['aa_sens']}"


def render_ar_sch(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_sch("ar-sch", ["ar-*â*a*a"], defaultdict(str))
    'زَارَزَ'
    """
    return arabiser.arabiser(arabiser.appliquer(parts[0], parts[1] if len(parts) > 1 else "ar-zrzr"))


def render_ar_terme(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ar_terme("ar-terme", ["mu'ad²ibũ"], defaultdict(str))
    "مُؤَدِّبٌ (<i>mu'ad²ibũ</i>) /mu.ʔad.di.bun/"
    """
    arab = arabiser.arabiser(parts[0])
    return f"{arab} ({italic(parts[0])}) /{ar_pron.toIPA(arabic=arab)}/"


def render_modele_etym(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_modele_etym("agglutination", [], defaultdict(str, {"m":"1"}))
    'Agglutination'
    >>> render_modele_etym("agglutination", ["fr"], defaultdict(str, {"de":"harbin", "texte":"l'harbin", "m":"1"}))
    "Agglutination de <i>l'harbin</i>"

    >>> render_modele_etym("contraction", ["fr"], defaultdict(str, {"de":"du", "de2":"quel"}))
    'contraction de <i>du</i> et de <i>quel</i>'

    >>> render_modele_etym("dénominal", [], defaultdict(str))
    'dénominal'
    >>> render_modele_etym("dénominal",[], defaultdict(str, {"de":"psychoanalyze", "m":"1"}))
    'Dénominal de <i>psychoanalyze</i>'
    >>> render_modele_etym("dénominal",["fr"], defaultdict(str, {"de": "buse", "sens": "trompette"}))
    'dénominal de <i>buse</i> (« trompette »)'

    >>> render_modele_etym("déverbal", [], defaultdict(str))
    'déverbal'
    >>> render_modele_etym("déverbal", [], defaultdict(str, {"de":"peko", "lang":"eo", "m":"0"}))
    'déverbal de <i>peko</i>'
    >>> render_modele_etym("déverbal", [], defaultdict(str, {"de":"accueillir", "m":"1"}))
    'Déverbal de <i>accueillir</i>'
    >>> render_modele_etym("déverbal sans suffixe", [], defaultdict(str))
    'déverbal'
    >>> render_modele_etym("déverbal sans suffixe", [], defaultdict(str, {"de":"réserver", "m":"1"}))
    'Déverbal de <i>réserver</i>'

    >>> render_modele_etym("syncope", ["fr"], defaultdict(str, { "m":"1"}))
    'Syncope'
    >>> render_modele_etym("syncope", ["fr"], defaultdict(str, {"de":"ne voilà-t-il pas"}))
    'syncope de <i>ne voilà-t-il pas</i>'
    >>> render_modele_etym("parataxe", ["fr"], defaultdict(str, {"de":"administrateur", "de2":"réseau"}))
    'parataxe de <i>administrateur</i> et de <i>réseau</i>'
    >>> render_modele_etym("déglutination", ["fr"], defaultdict(str, {"de":"agriote", "texte":"l’agriote", "m":"1"}))
    'Déglutination de <i>l’agriote</i>'

    >>> render_modele_etym("univerbation", ["fr"], defaultdict(str, {"m":"1", "de":"gens", "de2":"armes"}))
    'Univerbation de <i>gens</i> et de <i>armes</i>'
    >>> render_modele_etym("univerbation", ["fr"], defaultdict(str, {"m":"1", "de":"gens", "texte":"les gens", "de2":"armes", "texte2":"les armes"}))
    'Univerbation de <i>les gens</i> et de <i>les armes</i>'
    """
    phrase = tpl.removesuffix(" sans suffixe")
    if data["m"] in ("1", "oui"):
        phrase = capitalize(phrase)

    if data["de"]:
        phrase += " de "
        if data["nolien"] != "1" and data["texte"]:
            phrase += italic(data["texte"])
        else:
            phrase += italic(data["de"])

    if tpl in {"univerbation", "parataxe", "contraction"} and data["de2"]:
        phrase += " et de "
        if data["nolien"] != "1" and data["texte2"]:
            phrase += italic(data["texte2"])
        else:
            phrase += italic(data["de2"])

    if sens := data["sens"]:
        phrase += f" (« {sens} »)"

    return phrase


def render_apherese(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    render aphérèse and apocope

    >>> render_apherese("aphérèse", [], defaultdict(str))
    'aphérèse'
    >>> render_apherese("aphérèse", ["fr"], defaultdict(str))
    'aphérèse'
    >>> render_apherese("aphérèse", ["fr"], defaultdict(str, {"de": "enfant", "m": "1"}))
    'Aphérèse de <i>enfant</i>'
    >>> render_apherese("aphérèse", ["fr"], defaultdict(str, {"de": "enfant"}))
    'aphérèse de <i>enfant</i>'
    >>> render_apherese("aphérèse", ["fr"], defaultdict(str, {"de": "enfant", "texte": "minot"}))
    'aphérèse de <i>minot</i>'
    >>> render_apherese("aphérèse", ["fr"], defaultdict(str, {"de": "enfant", "texte": "minot", "nolien": "oui"}))
    'aphérèse de <i>enfant</i>'
    """
    if not parts and not data:
        return tpl

    auto_cap = data["m"] in ("1", "oui")
    phrase = capitalize(tpl) if auto_cap else tpl
    if data["texte"] and data["nolien"] not in ("1", "oui"):
        phrase += f" de {italic(data['texte'])}"
    elif data["de"]:
        phrase += f" de {italic(data['de'])}"
    return phrase


def render_argot(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_argot("argot", ["fr"], defaultdict(str))
    '<i>(Argot)</i>'
    >>> render_argot("argot", ["fr", "militaire"], defaultdict(str))
    '<i>(Argot militaire)</i>'
    >>> render_argot("argot", ["argot", "fr"], defaultdict(str, {"spéc":"militaire"}))
    '<i>(Argot militaire)</i>'
    """
    phrase = "Argot"
    if data["spéc"]:
        phrase += f" {data['spéc']}"
    elif len(parts) == 2:
        phrase += f" {parts[1]}"
    return term(phrase)


def render_au_masculin(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_au_masculin("au masculin", [], defaultdict(str))
    '<i>(Au masculin)</i>'
    >>> render_au_masculin("au masculin", ["p"], defaultdict(str))
    '<i>(Au masculin pluriel)</i>'
    >>> render_au_masculin("au masculin", ["s"], defaultdict(str))
    '<i>(Au masculin singulier)</i>'
    """
    phrase = "Au masculin"
    if parts:
        if parts[0] == "p":
            phrase += " pluriel"
        elif parts[0] == "s":
            phrase += " singulier"
    return term(phrase)


def render_caractere_unicode(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_caractere_unicode("caractère Unicode", ["à"], defaultdict(str))
    'Unicode : U+00E0'
    >>> render_caractere_unicode("caractère Unicode", ["a̋"], defaultdict(str))
    'Unicode : U+0061 U+030B'
    >>> render_caractere_unicode("caractère Unicode", ["266D"], defaultdict(str))
    'Unicode : U+266D'
    >>> render_caractere_unicode("caractère Unicode", ["à"], defaultdict(str, {"texte": "Code :"}))
    'Code : U+00E0'
    >>> render_caractere_unicode("caractère Unicode", [], defaultdict(str), word="🪐")
    'Unicode : U+1FA90'
    """
    char = parts[0] if parts else word
    if len(char) == 4:
        encoded = [f"U+{char}"]
    else:
        encoded = [f"U+{hex(ord(c)).upper()[2:].rjust(4, '0')}" for c in char]
    return f"{data['texte'] or 'Unicode :'} {' '.join(encoded)}"


def render_cf(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cf("cf", [], defaultdict(str))
    '→ voir'
    >>> render_cf("cf", ["immortelle"], defaultdict(str))
    '→ voir <i>immortelle</i>'
    >>> render_cf("cf", ["triner"], defaultdict(str, {"lang": "fr"}))
    '→ voir <i>triner</i>'
    >>> render_cf("cf", ["in-", "extinguible"], defaultdict(str, {"lang": "fr"}))
    '→ voir <i>in-</i> et <i>extinguible</i>'
    >>> render_cf("cf", ["enfant", "de", "vierge##pipe##!##pipe##vierge Marie"], defaultdict(str, {"lang": "fr"}))
    '→ voir <i>enfant</i>, <i>de</i> et <i>vierge Marie</i>'
    >>> render_cf("cf", [":Catégorie:Bruits en français"], defaultdict(str))
    ''
    """
    phrase = "→ voir"
    if parts:
        if parts[0].startswith(":"):
            return ""

        s_array = []
        for p in parts:
            s_phrase = p
            s_phrase = process_special_pipe_template(s_phrase)
            s_array.append(italic(s_phrase))
        phrase += f" {concat(s_array, ', ', last_sep=' et ')}"
    return phrase


def render_cit_ref(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cit_ref("cit_réf", ["Dictionnaire quelconque", "2007"], defaultdict(str))
    '<i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", [], defaultdict(str,{"titre":"Dictionnaire quelconque", "date":"2007"}))
    '<i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", ["Dictionnaire quelconque"], defaultdict(str, {"date":"2007"}))
    '<i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", ["Dictionnaire quelconque", "2007", "Certain auteur"], defaultdict(str))
    'Certain auteur, <i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", ["Dictionnaire quelconque", "2007", "Certain auteur", "Certain article"], defaultdict(str))
    '«&nbsp;Certain article&nbsp;», dans Certain auteur, <i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", ["2007"], defaultdict(str, {"titre":"Dictionnaire quelconque", "auteur":"Certain auteur", "article":"Certain article"}))
    '«&nbsp;Certain article&nbsp;», dans Certain auteur, <i>Dictionnaire quelconque</i>, 2007'
    >>> render_cit_ref("cit_réf", ["Nephilologus", "1934"], defaultdict(str, {"auteur_article":"Marius", "article":"Certain article", "pages":"pp. 241-259"}))
    'Marius, «&nbsp;Certain article&nbsp;», dans <i>Nephilologus</i>, 1934, pp. 241-259'
    """
    i = 0
    if data["titre"]:
        phrase = italic(data["titre"])
    else:
        phrase = italic(parts[i])
        i += 1
    phrase += ", "
    if data["date"]:
        phrase += data["date"]
    elif i < len(parts):
        phrase += parts[i]
        i += 1
    if data["auteur"]:
        phrase = data["auteur"] + ", " + phrase
    elif i < len(parts):
        phrase = f"{parts[i]}, {phrase}"
        i += 1
    if data["article"]:
        phrase = f"«&nbsp;{data['article']}&nbsp;», dans {phrase}"
    elif i < len(parts):
        phrase = f"«&nbsp;{parts[i]}&nbsp;», dans {phrase}"
        i += 1
    phrase += f", {data['pages']}" if data["pages"] else ""
    phrase = f"{data['auteur_article']}, {phrase}" if data["auteur_article"] else phrase
    return phrase


def render_contexte(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_contexte("C", [], defaultdict(str))
    '(Pas de contexte)'
    >>> render_contexte("C", [""], defaultdict(str))
    '(Pas de contexte)'
    >>> render_contexte("C", ["familier", "France"], defaultdict(str))
    '<i>(Familier, France)</i>'
    >>> render_contexte("C", ["familier", "France"], defaultdict(str))
    '<i>(Familier, France)</i>'
    >>> render_contexte("C", ["zoologie"], defaultdict(str))
    '<i>(Zoologie)</i>'
    >>> render_contexte("C", ["mythologie"], defaultdict(str, {"spéc": "romaine"}))
    '<i>(Mythologie romaine)</i>'
    """
    parts = [part for part in parts if part.strip()]
    if not parts:
        return "(Pas de contexte)"
    spec = f" {data['spéc']}" if data["spéc"] else ""
    return term(capitalize(", ".join(parts)) + spec)


def render_compose_de(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_compose_de("composé de", ["longus", "aevum"], defaultdict(str, {"lang":"la"}))
    'composé de <i>longus</i> et de <i>aevum</i>'
    >>> render_compose_de("composé de", ["longus", "aevum"], defaultdict(str, {"lang":"la", "f":"1"}))
    'composée de <i>longus</i> et de <i>aevum</i>'
    >>> render_compose_de("composé de", ["longus", "aevum"], defaultdict(str, {"sens1":"long", "sens2":"temps", "lang":"la", "m":"1"}))
    'Composé de <i>longus</i> («&nbsp;long&nbsp;») et de <i>aevum</i> («&nbsp;temps&nbsp;»)'
    >>> render_compose_de("composé de", ["longus", "aevum"], defaultdict(str, {"sens":"long temps", "lang":"la"}))
    'composé de <i>longus</i> et de <i>aevum</i>, littéralement «&nbsp;long temps&nbsp;»'
    >>> render_compose_de("composé de", ["δῆμος", "ἀγωγός"], defaultdict(str, {"tr1":"dêmos", "sens1":"peuple", "tr2":"agōgós", "sens2":"guide", "sens":"celui qui guide le peuple", "lang":"grc", "m":"1"}))
    'Composé de δῆμος, <i>dêmos</i> («&nbsp;peuple&nbsp;») et de ἀγωγός, <i>agōgós</i> («&nbsp;guide&nbsp;»), littéralement «&nbsp;celui qui guide le peuple&nbsp;»'
    >>> render_compose_de("composé de", ["aux", "mains", "de"], defaultdict(str, {"m":"1"}))
    'Composé de <i>aux</i>, <i>mains</i> et <i>de</i>'
    >>> render_compose_de("composé de", ["anti-", "quark"], defaultdict(str, {"lang":"en"}))
    'dérivé de <i>quark</i>, avec le préfixe <i>anti-</i>'
    >>> render_compose_de("composé de", ["anti-", "quark"], defaultdict(str, {"sens":"quarks au rebut"}))
    'dérivé de <i>quark</i>, avec le préfixe <i>anti-</i>, littéralement «&nbsp;quarks au rebut&nbsp;»'
    >>> render_compose_de("composé de", ["anti-", "quark"], defaultdict(str, {"lang":"en", "m":"1", "f":"1"}))
    'Dérivée de <i>quark</i>, avec le préfixe <i>anti-</i>'
    >>> render_compose_de("composé de", ["clear", "-ly"], defaultdict(str, {"lang":"en", "m":"1"}))
    'Dérivé de <i>clear</i>, avec le suffixe <i>-ly</i>'
    >>> render_compose_de("composé de", ["느낌", "표"], defaultdict(str, {"tr1":"neukkim", "sens1":"sensation", "tr2":"-pyo", "sens2":"symbole", "lang":"ko", "m":"1"}))
    'Dérivé de 느낌, <i>neukkim</i> («&nbsp;sensation&nbsp;»), avec le suffixe 표, <i>-pyo</i> («&nbsp;symbole&nbsp;»)'
    >>> render_compose_de("composé de", ["zone", "convergence"], defaultdict(str, {"m": "1"}))
    'Composé de <i>zone</i> et de <i>convergence</i>'
    >>> render_compose_de("composé de", ["Marcilly", "sur", "Tille"], defaultdict(str, {"lang": "fr", "m": "oui"}))
    'Composé de <i>Marcilly</i>, <i>sur</i> et <i>Tille</i>'
    >>> render_compose_de("composé de", ["faire", "boutique", "cul"], defaultdict(str, {"m": "1", "lang": "fr"}))
    'Composé de <i>faire</i>, <i>boutique</i> et <i>cul</i>'
    >>> render_compose_de("composé de", ["arthro-", "-logie"], defaultdict(str, {"lang": "fr", "m": "oui"}))
    'Dérivé du préfixe <i>arthro-</i>, avec le suffixe <i>-logie</i>'
    >>> render_compose_de("composé de", ["morin", "morine", "-elle"], defaultdict(str, {"lang": "fr", "m": "1"}))
    'Composé de <i>morin</i>, <i>morine</i> et <i>-elle</i>'
    >>> render_compose_de("composé de", ["bi-", "mensis"], defaultdict(str, {"lang": "fr", "sens1": "deux", "sens2":"mois"}))
    'dérivé de <i>mensis</i> («&nbsp;mois&nbsp;»), avec le préfixe <i>bi-</i> («&nbsp;deux&nbsp;»)'
    >>> render_compose_de("composé de", ["im-", "brouiller", "-able"], defaultdict(str, {"lang": "fr", "m": "oui"}))
    'Dérivé de <i>brouiller</i>, avec le préfixe <i>im-</i> et le suffixe <i>-able</i>'
    >>> render_compose_de("composé de", ["bloc", "d’", "obturation", "de", "puits"], defaultdict(str, {"lang": "fr", "m": "1", "f": "1"}))
    'Composée de <i>bloc</i>, <i>d’</i>, <i>obturation</i>, <i>de</i> et <i>puits</i>'
    >>> render_compose_de("composé de", ["an-", "", "-onyme"], defaultdict(str, {"lang": "fr", "m": "1"}))
    'Dérivé du préfixe <i>an-</i> et le suffixe <i>-onyme</i>'
    >>> render_compose_de("composé de", ["an-"], defaultdict(str))
    'dérivé du préfixe <i>an-</i>'
    >>> render_compose_de("composé de", ["garde", "enfant", ""], defaultdict(str))
    'composé de <i>garde</i> et de <i>enfant</i>'
    >>> render_compose_de("composé de", ["élever", "-able", ""], defaultdict(str, {"lang": "fr", "m": "1"}))
    'Dérivé de <i>élever</i>, avec le suffixe <i>-able</i>'
    >>> render_compose_de("composé de", ["litura", "funus"], defaultdict(str, {"lang": "la", "sens1": "", "sens2":"mort au génitif", "sens": ""}))
    'composé de <i>litura</i> et de <i>funus</i> («&nbsp;mort au génitif&nbsp;»)'
    >>> render_compose_de("composé de", ["au-dessus de", "", "soupçon"], defaultdict(str, {"m": "1"}))
    'Composé de <i>au-dessus de</i> et <i>soupçon</i>'
    >>> render_compose_de("composé de", ["＜"], defaultdict(str, {"2": "=", "lang": "conv"}))
    'composé de <i>＜</i> et de <i>=</i>'
    """

    # algorithm from https://fr.wiktionary.org/w/index.php?title=Mod%C3%A8le:compos%C3%A9_de&action=edit
    p1 = data.get("tr1", "") or parts[0] if parts else ""
    b1 = "1" if p1.endswith("-") else "0"
    p2 = data.get("tr2", "") or parts[1] if len(parts) > 1 else ""
    b2 = "1" if p2.startswith("-") else "0"
    b3 = "0"

    if len(parts) > 2:
        p3 = data.get("tr3", "") or parts[2] if len(parts) > 2 else ""
        if p3:
            b3 = "2" if p3.startswith("-") else "1"
    b4 = "1" if len(parts) > 3 else "0"

    b = b1 + b2 + b3 + b4
    is_derived = b in ["1000", "0100", "1020", "1100"]

    if is_derived:
        # Dérivé
        phrase = ("D" if data["m"] else "d") + ("érivée" if data["f"] in ("1", "oui", "o", "i") else "érivé")

        if b == "0100":
            phrase += " de " + word_tr_sens(parts[0], data.get("tr1", ""), data.get("sens1", ""))
            phrase += ", avec le suffixe " + word_tr_sens(parts[1], data.get("tr2", ""), data.get("sens2", ""))
        elif b == "1000":
            phrase += (
                (" de " + word_tr_sens(parts[1], data.get("tr2", ""), data.get("sens2", "")) + ", avec le")
                if len(parts) > 1 and parts[1]
                else " du"
            )
            phrase += " préfixe " + word_tr_sens(parts[0], data.get("tr1", ""), data.get("sens1", ""))
        elif b == "1020":
            phrase += (
                (" de " + word_tr_sens(parts[1], data.get("tr2", ""), data.get("sens2", "")) + ", avec le")
                if len(parts) > 1 and parts[1]
                else " du"
            )
            phrase += " préfixe " + word_tr_sens(parts[0], data.get("tr1", ""), data.get("sens1", ""))
            phrase += " et le suffixe " + word_tr_sens(parts[2], data.get("tr3", ""), data.get("sens3", ""))
        elif b == "1100":
            phrase += f" du préfixe {word_tr_sens(parts[0], data.get('tr1', ''), data.get('sens1', ''))},"
            phrase += f" avec le suffixe {word_tr_sens(parts[1], data.get('tr2', ''), data.get('sens2', ''))}"

        if data["sens"]:
            phrase += f", littéralement «&nbsp;{data['sens']}&nbsp;»"
        return phrase

    # Composé
    for i in range(1, 10):
        if dt := data[f"{i}"]:
            parts.insert(i, dt)
    # remove empty parts at the end.
    while parts and not parts[-1].strip():
        parts.pop()
    phrase = ("C" if data["m"] else "c") + ("omposée de " if data["f"] in ("1", "oui", "o", "i") else "omposé de ")
    if s_array := [
        word_tr_sens(part, data[f"tr{number}"], data[f"sens{number}"]) for number, part in enumerate(parts, 1) if part
    ]:
        phrase += concat(
            s_array,
            ", ",
            last_sep=" et de " if len(parts) < 3 else " et ",
        )

    if data["sens"]:
        phrase += f", littéralement «&nbsp;{data['sens']}&nbsp;»"

    return phrase


def render_composé_alpheratz(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_composé_alpheratz("composé double-flexion", [], defaultdict(str, {"r": "administrat", "sf": "rice", "sm": "eur", "s": "aire"}))
    '<b>Note :</b> D’après une proposition d’Alpheratz, il est possible d’analyser l’origine de ce mot comme étant dérivé d’une base agenre *<i>administrat</i>- (formée par réanalyse de <i>administrateur</i> et <i>administratrice</i> en tant que <i>administrat</i>- + -<i>eur</i> et <i>administrat</i>- + -<i>rice</i>) et du suffixe -<i>aire</i>.'
    """
    racine = data["r"]
    suff_n = data["s"]
    suff_m = data["sm"]
    suff_f = data["sf"]
    masculin = f"{racine}{suff_m}"
    féminin = f"{racine}{suff_f}"

    return (
        f"{strong('Note :')} D’après une proposition d’Alpheratz, il est possible d’analyser l’origine de ce mot comme étant dérivé d’une base agenre *{italic(racine)}-"
        f" (formée par réanalyse de {italic(masculin)} et {italic(féminin)} en tant que {italic(racine)}- + -{italic(suff_m)}"
        f" et {italic(racine)}- + -{italic(suff_f)}) et du suffixe -{italic(suff_n)}."
    )


def render_compose_double_flexion(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_compose_double_flexion("composé double-flexion", [], defaultdict(str, {"1": "auteur", "2": "autrice"}))
    'Double-flexion figée formée par contraction de <i>auteur</i> et <i>autrice</i>.'
    >>> render_compose_double_flexion("composé double-flexion", [], defaultdict(str, {"1": "auteur", "2": "autrice", "c": "·"}))
    'Double-flexion abrégée formée par contraction de <i>auteur</i> et <i>autrice</i> en utilisant <i>·</i>.'
    >>> render_compose_double_flexion("composé double-flexion", [], defaultdict(str, {"1": "auteur", "2": "auteure", "c": "(", "c2": ")"}))
    'Double-flexion abrégée formée par contraction de <i>auteur</i> et <i>auteure</i> en utilisant <i>(</i> et <i>)</i>.'
    """
    phrase = f"Double-flexion {'abrégée' if 'c' in data else 'figée'} formée par contraction de {italic(data['1'])} et {italic(data['2'])}"
    if char1 := data["c"]:
        phrase += f" en utilisant {italic(char1)}"
        if char2 := data["c2"]:
            phrase += f" et {italic(char2)}"
    return f"{phrase}."


def render_composé_neutre(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_composé_neutre("composé neutre", ["agenré", "-æ"], defaultdict(str, {"lang": "fr", "mot2": "agenrée"}))
    'composé de <i>agenré</i>&thinsp;/&thinsp;<i>agenrée</i> et du suffixe <i>-æ</i>, marqueur de genre neutre.'
    >>> render_composé_neutre("composé neutre", ["agenré", "-æ"], defaultdict(str, {"lang": "fr", "mot2": "agenrée", "f": "1", "m": "1"}))
    'Composée de <i>agenré</i>&thinsp;/&thinsp;<i>agenrée</i> et du suffixe <i>-æ</i>, marqueur de genre neutre.'
    """
    phrase = "Composé" if data["m"] == "1" else "composé"
    if data["f"] == "1":
        phrase += "e"
    phrase += f" de {italic(parts[0])}"
    if mot2 := data["mot2"]:
        phrase += f"&thinsp;/&thinsp;{italic(mot2)}"
    phrase += f" et du suffixe {italic(parts[1])}"
    return f"{phrase}, marqueur de genre neutre."


def render_cs(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cs("CS", [], defaultdict(str, {"char": " 黶 ", "c1": " 厭 ", "c2": " 黑 ", "sens": "tache noire sur la peau, gain de beauté "}))
    '黶 tache noire sur la peau, gain de beauté, de 厭 et 黑.'
    >>> render_cs("CS", [], defaultdict(str, {"char": " 黶 ", "c1": " 厭 ", "s1": "dégoût, dégoûtant ", "c2": " 黑 ", "s2": "noir ", "sens": "tache noire sur la peau, gain de beauté "}))
    '黶 tache noire sur la peau, gain de beauté, de 厭 (dégoût, dégoûtant) et 黑 (noir).'
    """
    text = f"{data['char'].strip()} {data['sens'].strip()}, de {data['c1'].strip()}"
    if s1 := data["s1"].strip():
        text += f" ({s1})"
    text += f" et {data['c2'].strip()}"
    if s2 := data["s2"].strip():
        text += f" ({s2})"
    return f"{text}."


def render_date(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_date("date", [""], defaultdict(str))
    '<i>(Date à préciser)</i>'
    >>> render_date("date", ["?"], defaultdict(str))
    '<i>(Date à préciser)</i>'
    >>> render_date("date", [], defaultdict(str))
    '<i>(Date à préciser)</i>'
    >>> render_date("date", ["1957"], defaultdict(str))
    '<i>(1957)</i>'
    >>> render_date("date", ["vers l'an V"], defaultdict(str))
    "<i>(Vers l'an V)</i>"
    >>> render_date("date", ["", "fr"], defaultdict(str))
    '<i>(Date à préciser)</i>'
    """
    date = parts[0] if parts and parts[0] not in ("", "?") else "Date à préciser"
    return term(capitalize(date))


def render_equiv_pour(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_equiv_pour("équiv-pour", ["un homme", "maître"], defaultdict(str))
    '<i>(pour un homme, on dit</i>&nbsp: maître<i>)</i>'
    >>> render_equiv_pour("équiv-pour", ["le mâle", "lion"], defaultdict(str))
    '<i>(pour le mâle, on dit</i>&nbsp: lion<i>)</i>'
    >>> render_equiv_pour("équiv-pour", ["une femme", "autrice", "auteure", "auteuse"], defaultdict(str))
    '<i>(pour une femme, on peut dire</i>&nbsp: autrice, auteure, auteuse<i>)</i>'
    >>> render_equiv_pour("équiv-pour", ["une femme", "professeure", "professeuse", "professoresse", "professrice"], defaultdict(str, {"texte":"certains disent"}))
    '<i>(pour une femme, certains disent</i>&nbsp: professeure, professeuse, professoresse, professrice<i>)</i>'
    >>> render_equiv_pour("équiv-pour", ["un homme", "auteur"], defaultdict(str, {"2egenre":"une personne non-binaire", "2egenre1":"autaire", "2egenre2":"auteurice"}))
    '<i>(pour un homme, on dit</i>&nbsp: auteur<i> ; pour une personne non-binaire, on peut dire</i>&nbsp: autaire, auteurice<i>)</i>'
    """
    phrase = f"(pour {parts.pop(0)}, "
    phrase += data.get("texte", "on dit" if len(parts) == 1 else "on peut dire")
    phrase = f"{italic(phrase)}&nbsp: {', '.join(parts)}"
    if "2egenre" in data:
        phrase2 = f" ; pour {data['2egenre']}, "
        phrase2 += data.get("texte", "on peut dire" if "2egenre2" in data else "on dit")
        parts2: list[str] = []
        for i in range(1, 7):
            if genre := data.get(f"2egenre{i}", ""):
                parts2.append(genre)
        phrase2 = f"{italic(phrase2)}&nbsp: {', '.join(parts2)}"
        phrase += phrase2
    phrase += italic(")")
    return phrase


def render_etyl(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etyl("calque", ["la", "fr"], defaultdict(str))
    'latin'
    >>> render_etyl("calque", ["en", "fr"], defaultdict(str, {"mot":"to date", "sens":"à ce jour"}))
    'anglais <i>to date</i> («&nbsp;à ce jour&nbsp;»)'
    >>> render_etyl("calque", ["sa", "fr"], defaultdict(str, {"mot":"वज्रयान", "tr":"vajrayāna", "sens":"véhicule du diamant"}))
    'sanskrit वज्रयान, <i>vajrayāna</i> («&nbsp;véhicule du diamant&nbsp;»)'
    >>> render_etyl("étyl", ["grc", "fr"], defaultdict(str))
    'grec ancien'
    >>> render_etyl("étyl", ["it", "fr", "Majella"], defaultdict(str, {"mot": ""}))
    'italien'
    >>> render_etyl("étyl", ["he", "fr", "tr", "sarabe"], defaultdict(str, {"mot": "", "sens": "se révolter"}))
    'hébreu <i>sarabe</i> («&nbsp;se révolter&nbsp;»)'
    >>> render_etyl("étyl", ["la", "fr", "dithyrambicus"], defaultdict(str))
    'latin <i>dithyrambicus</i>'
    >>> render_etyl("étyl", ["no", "fr"], defaultdict(str, {"mot":"ski"}))
    'norvégien <i>ski</i>'
    >>> render_etyl("étyl", ["la", "fr", "sequor"], defaultdict(str, {"dif": "sequi"}))
    'latin <i>sequi</i>'
    >>> render_etyl("étyl", ["la", "fr"], defaultdict(str, {"mot":"invito", "type":"verb"}))
    'latin <i>invito</i>'
    >>> render_etyl("étyl", ["grc", "fr"], defaultdict(str, {"mot":"λόγος", "tr":"lógos", "type":"nom", "sens":"étude"}))
    'grec ancien λόγος, <i>lógos</i> («&nbsp;étude&nbsp;»)'
    >>> render_etyl("étyl", ["grc", "fr", "λόγος", "lógos", "étude"], defaultdict(str, {"type":"nom", "lien":"1"}))
    'grec ancien λόγος, <i>lógos</i> («&nbsp;étude&nbsp;»)'
    >>> render_etyl("étyl", ["la", "fr"], defaultdict(str, {"mot":"jugulum", "sens":"endroit où le cou se joint aux épaules = la gorge"}))
    'latin <i>jugulum</i> («&nbsp;endroit où le cou se joint aux épaules = la gorge&nbsp;»)'
    >>> render_etyl("étyl", ["la", "fr", "tr"], defaultdict(str, {"mot":"subgrunda", "sens":"même sens"}))
    'latin <i>subgrunda</i> («&nbsp;même sens&nbsp;»)'
    >>> render_etyl("étyl", ["grc", "fr"], defaultdict(str, {"mot":""}))
    'grec ancien'
    >>> render_etyl('étyl', ['grc'], defaultdict(str, {"mot":"ὑπόθεσις", "tr":"hupóthesis", "sens":"action de mettre dessous", "nocat":"1"}))
    'grec ancien ὑπόθεσις, <i>hupóthesis</i> («&nbsp;action de mettre dessous&nbsp;»)'
    >>> render_etyl("étyl", ["grc", "fr"], defaultdict(str, {"tr":"leipein", "sens":"abandonner"}))
    'grec ancien <i>leipein</i> («&nbsp;abandonner&nbsp;»)'
    >>> render_etyl("étyl", [], defaultdict(str, {"1":"grc", "2":"es", "mot":"νακτός", "tr":"naktós", "sens":"dense"}))
    'grec ancien νακτός, <i>naktós</i> («&nbsp;dense&nbsp;»)'
    >>> render_etyl("étyl", ["la", "fr", "ortivus", "", "qui se lève"], defaultdict(str))
    'latin <i>ortivus</i> («&nbsp;qui se lève&nbsp;»)'
    >>> render_etyl("étyl", ["proto-indo-européen", "fr"], defaultdict(str))
    'indo-européen commun'
    >>> render_etyl("étyl", ["néolatin", "fr"], defaultdict(str))
    'néolatin'
    >>> render_etyl("étylp", ["la", "fr"], defaultdict(str, {"mot":"Ladon"}))
    'latin <i>Ladon</i>'
    >>> render_etyl("étylp", ["br", "fr"], defaultdict(str, {"tr":"qui est digne de posséder un bon cheval, chevalier"}))
    'breton, <i>qui est digne de posséder un bon cheval, chevalier</i>'
    """
    # The lang name
    lang = data["1"] or parts.pop(0)
    phrase = langs.get(lang, lang)
    if parts and parts[0] in langs:
        parts.pop(0)
    mot = data.get("mot", data["3"] or (parts[0] if parts else ""))
    mot = "" if mot == "tr" else mot
    tr = data["tr"] or data["R"] or data["4"] or (parts[1] if len(parts) > 1 else "")
    sens = data["sens"] or data["5"] or (parts[2] if len(parts) > 2 else "")
    if data["dif"]:
        mot = data["dif"]
    if mot:
        # italic for latin script only
        phrase += f" {mot}" if max(mot) > "\u0370" else f" {italic(mot)}"
    if tr:
        if tpl == "étylp":
            phrase += f", {italic(tr)}"
        else:
            phrase += f", {italic(tr)}" if mot else f" {italic(tr)}"
    if sens:
        phrase += f" («&nbsp;{sens}&nbsp;»)"
    return phrase


def render_etym_chinoise(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etym_chinoise("Étymologie graphique chinoise", [], defaultdict(str, {"racine": "殳", "caractère": "𣪘", "type":  "déformation", "explication": "Ne dérive pas de 皀. Ses formes antiques sont inexpliquées, on les rapproche de 叀.", "sens": "Se rapporte à l’élevage des animaux domestiques."}))
    'Se rapporte à l’élevage des animaux domestiques.'
    >>> render_etym_chinoise("Étymologie graphique chinoise", [], defaultdict(str, {"racine": "殳", "caractère": "𣪘", "type":  "déformation", "composition": "Se rapporte à l’élevage des animaux domestiques."}))
    'Se rapporte à l’élevage des animaux domestiques.'
    """
    return data["sens"] or data["composition"] or data["explication"]


def render_hypercorrection(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_hypercorrection("hypercorrection", ["fr"], defaultdict(str))
    'hypercorrection'
    >>> render_hypercorrection("hypercorrection", ["en", "la"], defaultdict(str, {"de": "stilus"}))
    'hypercorrection de <i>stilus</i>'
    >>> render_hypercorrection("hypercorrection", ["en", "la"], defaultdict(str, {"de": "stilus", "m": "1"}))
    'Hypercorrection de <i>stilus</i>'
    """
    texte = f"{'H' if data['m'] == '1' else 'h'}ypercorrection"
    if de := (data["texte"] or data["de"]):
        texte += f" de {italic(de)}"
    return texte


def render_ko_pron(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ko_pron("ko-pron", ["서울"], defaultdict(str))
    '[sʌ.uɭ]'
    >>> render_ko_pron("ko-pron", ["아이"], defaultdict(str, {"phon": 1}))
    '/a.i/'
    >>> render_ko_pron("ko-pron", ["아이"], defaultdict(str))
    '[a.i]'
    >>> render_ko_pron("ko-pron", ["한국말"], defaultdict(str, {"phon": 1}))
    '/han.kuŋ.mal/'
    >>> render_ko_pron("ko-pron", ["한국말"], defaultdict(str))
    '[han.ɡuŋ.maɭ]'
    >>> render_ko_pron("ko-pron", ["같이"], defaultdict(str, {"phon": 1}))
    '/ka.tɕʰi/'
    >>> render_ko_pron("ko-pron", ["같이"], defaultdict(str))
    '[ka.tɕʰi]'
    >>> render_ko_pron("ko-pron", ["전화"], defaultdict(str, {"phon": 1}))
    '/tɕʌ.nhwa/'
    >>> render_ko_pron("ko-pron", ["전화"], defaultdict(str))
    '[tɕʌ.nʱʷa]'
    >>> render_ko_pron("ko-pron", ["계셨어요."], defaultdict(str, {"phon": 1}))
    '/ke.sjʌ.ˀsʌ.jo/'
    >>> render_ko_pron("ko-pron", ["계셨어요."], defaultdict(str))
    '[ke̞.ɕʌ.ˀsʌ.jo̞]'
    >>> render_ko_pron("ko-pron", ["한'자"], defaultdict(str, {"phon": 1}))
    '/han.ˀtɕa/'
    >>> render_ko_pron("ko-pron", ["한'자"], defaultdict(str))
    '[han.ˀtɕa]'
    >>> render_ko_pron("ko-pron", ["꽃'잎"], defaultdict(str, {"phon": 1}))
    '/ˀkon.nip/'
    >>> render_ko_pron("ko-pron", ["꽃'잎"], defaultdict(str))
    '[ˀkon.nip̚]'
    >>> render_ko_pron("ko-pron", ["맛있다"], defaultdict(str, {"phon": 1}))
    '/ma.si.ˀta/'
    >>> render_ko_pron("ko-pron", ["맛있다"], defaultdict(str))
    '[ma.ɕi.ˀta]'
    >>> render_ko_pron("ko-pron", ["맛-없다"], defaultdict(str, {"phon": 1}))
    '/ma.tʌp.ˀta/'
    >>> render_ko_pron("ko-pron", ["맛-없다"], defaultdict(str))
    '[ma.dʌp̚.ˀta]'
    >>> render_ko_pron("ko-pron", ["뜻-하다"], defaultdict(str, {"phon": 1}))
    '/ˀtɯ.tʰa.ta/'
    >>> render_ko_pron("ko-pron", ["뜻-하다"], defaultdict(str))
    '[ˀtɯ.tʰa.da]'
    >>> render_ko_pron("ko-pron", ["떫'다"], defaultdict(str, {"phon": 1}))
    '/ˀtʌl.ˀta/'
    >>> render_ko_pron("ko-pron", ["떫'다"], defaultdict(str))
    '[ˀtʌɭ.ˀta]'
    >>> render_ko_pron("ko-pron", ["쉽다"], defaultdict(str, {"phon": 1}))
    '/swip.ˀta/'
    >>> render_ko_pron("ko-pron", ["쉽다"], defaultdict(str))
    '[ʃɥip̚.ˀta]'
    >>> render_ko_pron("ko-pron", ["신라"], defaultdict(str, {"phon": 1}))
    '/sil.la/'
    >>> render_ko_pron("ko-pron", ["신라"], defaultdict(str))
    '[ɕiɭ.ɭa]'
    >>> render_ko_pron("ko-pron", ["향신-료"], defaultdict(str, {"phon": 1}))
    '/hjaŋ.sin.njo/'
    >>> render_ko_pron("ko-pron", ["향신-료"], defaultdict(str))
    '[çaŋ.ɕin.njo]'
    >>> render_ko_pron("ko-pron", ["의의"], defaultdict(str, {"phon": 1}))
    '/ɯj.i/'
    >>> render_ko_pron("ko-pron", ["의의"], defaultdict(str))
    '[ɯj.i]'
    >>> render_ko_pron("ko-pron", ["외국인"], defaultdict(str, {"phon": 1}))
    '/we.ku.kin/'
    >>> render_ko_pron("ko-pron", ["외국인"], defaultdict(str))
    '[we̞.ɡu.ɡin]'
    >>> render_ko_pron("ko-pron", ["괜찮다"], defaultdict(str, {"phon": 1}))
    '/kwɛn.tɕʰan.tʰa/'
    >>> render_ko_pron("ko-pron", ["괜찮다"], defaultdict(str))
    '[kʷe̞n.tɕʰan.tʰa]'
    >>> render_ko_pron("ko-pron", ["있습니다"], defaultdict(str, {"phon": 1}))
    '/i.ˀsɯm.ni.ta/'
    >>> render_ko_pron("ko-pron", ["있습니다"], defaultdict(str))
    '[i.ˀsɯm.ni.da]'
    >>> render_ko_pron("ko-pron", ["역시"], defaultdict(str, {"phon": 1}))
    '/jʌk.ˀsi/'
    >>> render_ko_pron("ko-pron", ["역시"], defaultdict(str))
    '[jʌk.ˀɕi]'
    >>> render_ko_pron("ko-pron", ["ㅂ니다"], defaultdict(str, {"phon": 1}))
    '/m.ni.ta/'
    >>> render_ko_pron("ko-pron", ["ㅂ니다"], defaultdict(str))
    '[m.ni.da]'
    >>> render_ko_pron("ko-pron", ["가"], defaultdict(str, {"phon": 1, "sonore": 1}))
    '/ka/'
    >>> render_ko_pron("ko-pron", ["가"], defaultdict(str, {"sonore": 1}))
    '[ɡa]'
    >>> render_ko_pron("ko-pron", ["독일 '연방 공화국"], defaultdict(str, {"phon": 1}))
    '/to.kil.ljʌn.paŋ.ko.ŋhwa.kuk/'
    >>> render_ko_pron("ko-pron", ["독일 '연방 공화국"], defaultdict(str))
    '[to.ɡiɭ.ɭjʌn.baŋ.ɡo.ŋʱʷa.ɡuk̚]'
    """
    from .ko_hangeul import phoneme

    phrase = phoneme(parts[0], not bool(data["phon"]), bool(data["sonore"]))
    return f"/{phrase}/" if data["phon"] else f"[{phrase}]"


def render_ko_translit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ko_translit("hangeul unicode", ["힣"], defaultdict(str))
    'Caractère hangeul <i>hih</i>.'
    >>> render_ko_translit("hangeul unicode", [], defaultdict(str), word="힣")
    'Caractère hangeul <i>hih</i>.'
    """
    from .ko_hangeul import translit

    return f"Caractère hangeul {italic(translit(parts[0] if parts else word))}."


def render_la_verb(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_la_verb("la-verb", ["amō", "amare", "amāre", "amavi", "amāvi", "amatum", "amātum"], defaultdict(str))
    '<b>amō</b>, <i>infinitif</i> : amāre, <i>parfait</i> : amāvi, <i>supin</i> : amātum'
    >>> render_la_verb("la-verb", ["vŏlo", "velle", "velle", "volui", "vŏlŭi"], defaultdict(str, {"2ps":"vis", "2ps2":"vīs", "pattern":"irrégulier"}))
    '<b>vŏlo</b>, vīs, <i>infinitif</i> : velle, <i>parfait</i> : vŏlŭi <i>(irrégulier)</i>'
    >>> render_la_verb("la-verb", ["horrĕo", "horrere", "horrēre", "horrui", "horrŭi"], defaultdict(str, {"pattern":"sans passif"}))
    '<b>horrĕo</b>, <i>infinitif</i> : horrēre, <i>parfait</i> : horrŭi <i>(sans passif)</i>'
    >>> render_la_verb("la-verb", ["sum", "es", "esse", "esse", "fui", "fui", "futurus", "futurus"], defaultdict(str, {"2ps":"es", "2ps2":"es", "pattern":"irrégulier", "44":"participe futur"}))
    '<b>sum</b>, es, <i>infinitif</i> : esse, <i>parfait</i> : fui, <i>participe futur</i> : futurus <i>(irrégulier)</i>'
    """
    phrase = f"{strong(parts[0])},"
    if data["2ps"]:
        phrase += f" {data.get('2ps2', data['2ps'])},"
    phrase += f" {italic('infinitif')} : {parts[2]}"
    if parts[3] != "-":
        phrase += f", {italic('parfait')} : {parts[4]}"
    if data["44"]:
        phrase += f", {italic(data['44'])} : {parts[6]}"
    elif len(parts) > 5:
        phrase += f", {italic('supin')} : {parts[6]}"
    if data["pattern"]:
        phrase += " " + italic(f"({data['pattern']})")
    return phrase


def render_lae(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lae("laé", ["fr", "adv"], defaultdict(str))
    '<i>(Adverbe)</i>'
    >>> render_lae("laé", ["fr", "nom", "1"], defaultdict(str))
    '<i>(Nom commun 1)</i>'
    >>> render_lae("laé", ["conv", "symb", "1"], defaultdict(str))
    '<i>(Symbole 1)</i>'
    """
    labels = {
        "adj": "Adjectif",
        "adj-indéf": "Adjectif indéfini",
        "adj-pos": "Adjectif possessif",
        "adjectif indéfini": "Adjectif indéfini",
        "adjectif numéral": "Adjectif numéral",
        "adjectif possessif": "Adjectif possessif",
        "adjectif": "Adjectif",
        "adv": "Adverbe",
        "adverbe": "Adverbe",
        "adverbe interrogatif": "Adverbe interrogatif",
        "art": "Article",
        "art-déf": "Article défini",
        "article défini": "Article défini",
        "article indéfini": "Article indéfini",
        "article": "Article",
        "conj": "Conjonction",
        "conjonction": "Conjonction",
        "conj-coord": "Conjonction de coordination",
        "interj": "Interjection",
        "interjection": "Interjection",
        "lettre": "Lettre",
        "nom": "Nom commun",
        "nom commun": "Nom commun",
        "nom de famille": "Nom de famille",
        "nom-fam": "Nom de famille",
        "nom-pr": "Nom propre",
        "nom propre": "Nom propre",
        "num": "Numéral",
        "numéral": "Numéral",
        "onom": "Onomatopée",
        "onoma": "Onomatopée",
        "onomatopée": "Onomatopée",
        "part": "Particule",
        "particule": "Particule",
        "phrase": "Locution-phrase",
        "préf": "Préfixe",
        "préfixe": "Préfixe",
        "prénom": "Prénom",
        "prép": "Préposition",
        "préposition": "Préposition",
        "pronom": "Pronom",
        "pronom-pers": "Pronom personnel",
        "pronom personnel": "Pronom personnel",
        "pronom possessif": "Pronom possessif",
        "pronom relatif": "Pronom relatif",
        "suf": "Suffixe",
        "suff": "Suffixe",
        "suffixe": "Suffixe",
        "symb": "Symbole",
        "symbole": "Symbole",
        "verb": "Verbe",
        "verbe": "Verbe",
    }
    phrase = labels[parts[1]] if len(parts) > 1 else ""
    if len(parts) > 2:
        phrase += f" {parts[2]}"
    return term(phrase)


def render_lang(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lang("Lang", ["la", "sine qua non"], defaultdict(str, {"sens": "sans quoi non"}))
    '<i>sine qua non</i> («&nbsp;sans quoi non&nbsp;»)'
    >>> render_lang("Lang", [], defaultdict(str, {"texte": "sine qua non", "sens": "sans quoi non"}))
    '<i>sine qua non</i> («&nbsp;sans quoi non&nbsp;»)'
    """
    if parts:
        parts.pop(0)  # language
    texte = data["texte"] or data["2"] or (parts.pop(0) if parts else "")
    tr = data["tr"] or data["3"] or (parts.pop(0) if parts else "")
    sens = data["sens"] or data["4"] or (parts.pop(0) if parts else "")
    return word_tr_sens(texte, tr, sens)


def render_lien(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lien("l", ["dies Lunae", "la"], defaultdict(str))
    'dies Lunae'
    >>> render_lien("lien", ["渦", "zh-Hans"], defaultdict(str))
    '渦'
    >>> render_lien("lien", ["フランス", "ja"], defaultdict(str, {"sens":"France"}))
    'フランス («&nbsp;France&nbsp;»)'
    >>> render_lien("lien", ["フランス", "ja"], defaultdict(str, {"tr":"Furansu", "sens":"France"}))
    'フランス, <i>Furansu</i> («&nbsp;France&nbsp;»)'
    >>> render_lien("lien", ["camara", "la"], defaultdict(str, {"sens":"voute, plafond vouté"}))
    'camara («&nbsp;voute, plafond vouté&nbsp;»)'
    >>> render_lien("lien", ["sto", "la"], defaultdict(str, {"dif": "stare"}))
    'stare'
    """
    phrase = data["dif"] or parts.pop(0)
    if data["tr"]:
        phrase += f", {italic(data['tr'])}"
    if data["sens"]:
        phrase += f" («&nbsp;{data['sens']}&nbsp;»)"
    return phrase


def render_lien_rouge(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lien_rouge("LienRouge", [], defaultdict(str, {"fr":"Comité", "trad":"United Nations", "texte":"COPUOS"}))
    '<i>COPUOS</i>'
    >>> render_lien_rouge("LienRouge", ["Comité"], defaultdict(str, {"trad":"Ausschuss", "texte":"COPUOS"}))
    '<i>COPUOS</i>'
    >>> render_lien_rouge("LienRouge", [], defaultdict(str, {"fr":"Comité", "trad":"United Nations"}))
    '<i>Comité</i>'
    >>> render_lien_rouge("LienRouge", ["Comité"], defaultdict(str, {"trad":"Ausschuss"}))
    '<i>Comité</i>'
    >>> render_lien_rouge("LienRouge", [], defaultdict(str, {"fr":"Comité"}))
    '<i>Comité</i>'
    >>> render_lien_rouge("LienRouge", ["Comité"], defaultdict(str))
    '<i>Comité</i>'
    >>> render_lien_rouge("LienRouge", [], defaultdict(str, {"trad":"United Nations"}))
    '<i>United Nations</i>'
    """
    res = ""
    if data["texte"]:
        res = italic(data["texte"])
    elif data["fr"]:
        res = italic(data["fr"])
    elif parts:
        res = italic(parts[0])
    elif data["trad"]:
        res = italic(data["trad"])
    return res


def render_lien_web(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_lien_web("Lien web", [], defaultdict(str, {"titre":"The Weasel-Lobster Race"}))
    '<i>The Weasel-Lobster Race</i>'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"langue":"en", "titre":"Toho sues Cosmo Contents for selling DVDs of Kurosawa’s early works", "année":"2007", "en ligne le":"2 avril 2007"}))
    '<i>(anglais)</i> <i>Toho sues Cosmo Contents for selling DVDs of Kurosawa’s early works</i>, 2007. Mis en ligne le 2 avril 2007'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"langue":"en", "titre":"Translation Movements in Iran; Sassanian Era to Year 2000, Expansion, Preservation and Modernization", "prénom":"Massoumeh", "nom":"Price", "année":"2000", "éditeur":"Iran Chamber", "consulté le":"13 octobre 2006"}))
    '<i>(anglais)</i> Massoumeh Price, <i>Translation Movements in Iran; Sassanian Era to Year 2000, Expansion, Preservation and Modernization</i>, Iran Chamber, 2000. Consulté le 13 octobre 2006'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"langue":"en", "titre":"Islam, Women and Civil Rights: the Religious debate in the Iran of the 1990s", "prénom":"Ziba", "nom":"Mir-Hosseini", "coauteurs":"Azadeh Kian-Thiébaut", "année":"2002", "site":"Abstracta Iranica", "éditeur":"Curzon Press et Royal Asiatic Society, Londres", "série":"dans Sarah Ansari et Vanessa Martin (dir.), Women, Religion and Culture in Iran", "isbn":"1234567890123", "page":"169-188", "citation":"Les femmes et leurs droits se trouvent désormais au cœur des débats jurisprudentiels où s’affrontent les visions réformatrices et conservatrices.", "en ligne le":"15 mars 2006", "consulté le":"2 octobre 2006"}))
    '<i>(anglais)</i> Ziba Mir-Hosseini, Azadeh Kian-Thiébaut, <i>Islam, Women and Civil Rights: the Religious debate in the Iran of the 1990s</i>, dans Sarah Ansari et Vanessa Martin (dir.), Women, Religion and Culture in Iran sur <i>Abstracta Iranica</i>, Curzon Press et Royal Asiatic Society, Londres, 2002, ISBN 1234567890123. Mis en ligne le 15 mars 2006, consulté le 2 octobre 2006. «&nbsp;Les femmes et leurs droits se trouvent désormais au cœur des débats jurisprudentiels où s’affrontent les visions réformatrices et conservatrices.&nbsp;», page 169-188'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"titre":"The Weasel-Lobster Race", "auteur":"auteur", "auteur2": "auteur2" }))
    'auteur, auteur2, <i>The Weasel-Lobster Race</i>'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"titre":"The Weasel-Lobster Race", "nom":"nom", "prénom": "prénom", "nom2":"nom2", "prénom2": "prénom2"}))
    'prénom nom, prénom2 nom2, <i>The Weasel-Lobster Race</i>'
    >>> render_lien_web("Lien web", [], defaultdict(str, {"url":"URL", "titre": "TITRE", "site": "SITE", "date": "DATE", "consulté le": "CONSULTATION"}))
    '<i>TITRE</i> sur <i>SITE</i>, DATE. Consulté le CONSULTATION'
    """
    phrase = ""
    if data["langue"]:
        phrase += term(langs[data["langue"]]) + " "
    if data["auteur"]:
        phrase += data["auteur"]
    elif data["prénom"]:
        phrase += data["prénom"] + " " + data["nom"]
    if data["auteur2"]:
        phrase += ", " + data["auteur2"]
    elif data["prénom2"]:
        phrase += ", " + data["prénom2"] + " " + data["nom2"]
    if data["coauteurs"]:
        phrase += ", " + data["coauteurs"]
    if phrase and phrase[-1] != " ":
        phrase += ", "
    phrase += italic(data["titre"])
    if data["série"]:
        phrase += ", " + data["série"]
    if data["site"]:
        phrase += " sur " + italic(data["site"])
    if data["éditeur"]:
        phrase += ", " + data["éditeur"]
    if data["année"]:
        phrase += ", " + data["année"]
    if data["date"]:
        phrase += ", " + data["date"]
    if data["isbn"]:
        phrase += ", ISBN " + data["isbn"]
    if data["en ligne le"]:
        phrase += ". Mis en ligne le " + data["en ligne le"]
        if data["consulté le"]:
            phrase += ", consulté le " + data["consulté le"]
    elif data["consulté le"]:
        phrase += ". Consulté le " + data["consulté le"]
    if data["citation"]:
        phrase += ". «&nbsp;" + data["citation"] + "&nbsp;»"
    if data["page"]:
        phrase += ", page " + data["page"]
    return phrase


def render_mot_valise(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_mot_valise("mot-valise", ["fr"], defaultdict(str, {"m":"1"}))
    'Mot-valise'
    >>> render_mot_valise("mot-valise", ["fr"], defaultdict(str, {"de":"abandonné", "de2": "logiciel"}))
    'mot-valise formé de <i>abandonné</i> et de <i>logiciel</i>'
    >>> render_mot_valise("mot-valise", ["fr"], defaultdict(str, {"de":"abandonné", "de2": "logiciel", "texte": "a", "texte2":"software"}))
    'mot-valise formé de <i>a</i> et de <i>software</i>'
    >>> render_mot_valise("mot-valise", ["fr"], defaultdict(str, {"de":"abandonné", "de2": "logiciel", "texte2":"software", "nolien":"1"}))
    'mot-valise formé de <i>abandonné</i> et de <i>logiciel</i>'
    """
    phrase = "Mot-valise" if data["m"] in ("oui", "1") else "mot-valise"
    if data["de"] or data["texte"]:
        if data["nolien"] in ("", "non", "0") and data["texte"]:
            phrase += f" formé de {italic(data['texte'])}"
        elif data["de"]:
            phrase += f" formé de {italic(data['de'])}"
    if data["de2"] or data["texte2"]:
        if data["nolien"] in ("", "non", "0") and data["texte2"]:
            phrase += f" et de {italic(data['texte2'])}"
        elif data["de2"]:
            phrase += f" et de {italic(data['de2'])}"

    return phrase


def render_mn_lien(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_mn_lien("mn-lien", ["далай", "dalai", "ᠲᠠᠯᠠᠢ"], defaultdict(str))
    'далай (MNS : <i>dalai</i>), ᠲᠠᠯᠠᠢ'
    >>> render_mn_lien("mn-lien", ["хаган", "khagan", "ᠬᠠᠭᠠᠨ", "qaɣan"], defaultdict(str))
    'хаган (MNS : <i>khagan</i>), ᠬᠠᠭᠠᠨ (VPMC : <i>qaɣan</i>)'
    """
    phrase = f"{parts[0]} (MNS : {italic(parts[1])})"
    if len(parts) > 2:
        phrase += f", {parts[2]}"
    if len(parts) > 3:
        phrase += f" (VPMC : {italic(parts[3])})"
    return phrase


def render_nom_langue(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_nom_langue("nom_langue", ["ky"], defaultdict(str))
    'kirghiz'
    """
    return langs.get(parts[0], parts[0])


def render_polytonique(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_polytonique("polytonique", ["μηρóς", "mêrós", "cuisse"], defaultdict(str))
    'μηρóς, <i>mêrós</i> («&nbsp;cuisse&nbsp;»)'
    >>> render_polytonique("polytonique", ["φόβος", "phóbos"], defaultdict(str, {"sens":"effroi, peur"}))
    'φόβος, <i>phóbos</i> («&nbsp;effroi, peur&nbsp;»)'
    >>> render_polytonique("Polytonique",["नामन्", "nā́man"], defaultdict(str))
    'नामन्, <i>nā́man</i>'
    >>> render_polytonique("Polytonique", ["هند", "hend", "Inde"], defaultdict(str))
    'هند, <i>hend</i> («&nbsp;Inde&nbsp;»)'
    >>> render_polytonique("polytonique", ["κακοθάνατος", "kakothánatos", ""], defaultdict(str))
    'κακοθάνατος, <i>kakothánatos</i>'
    """
    phrase = parts.pop(0)
    tr = data["tr"] or (parts.pop(0) if parts else "")
    sens = data["sens"] or (parts.pop(0) if parts else "")
    if tr:
        phrase += f", {italic(tr)}"
    if sens:
        phrase += f" («&nbsp;{sens}&nbsp;»)"
    return phrase


def render_ps(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ps("PS", [], defaultdict(str, {"de": "亘", "clef": "口", "char": "咺"}))
    'Dérive de 亘, spécifié par 口.'
    >>> render_ps("PS", [], defaultdict(str, {"de": "亘", "clef": "口", "char": "咺", "pinyin": "xuān", "sens": "enfant qui pleure sans cesse ; être dans l'affliction, pleurer amèrement", "ici": " tout le temps"}))
    "Dérive de 亘 (tout le temps), spécifié par 口 : enfant qui pleure sans cesse ; être dans l'affliction, pleurer amèrement."
    """
    text = f"Dérive de {data['de'].strip()}"
    if ici := data["ici"].strip():
        text += f" ({ici})"
    text += f", spécifié par {data['clef'].strip()}"
    if sens := data["sens"].strip():
        text += f" : {sens}"
    return f"{text}."


def render_radical_de_kangxi(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_radical_de_kangxi("radical de Kangxi", [], defaultdict(str), word="⼀")
    'Radical de Kangxi 一. Unicode : U+2F00.'
    """
    from .ko_hangeul.sinogramme import radical_trait

    char = re.sub(r"\d+", "", radical_trait(word))  # Remove trailing numbers
    return f"Radical de Kangxi {char}. Unicode : U+{hex(ord(word))[2:].upper()}."


def render_recons(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_recons("recons", ["maruos"], defaultdict(str))
    '*<i>maruos</i>'
    >>> render_recons("recons", ["maruos", "gaul"], defaultdict(str))
    '*<i>maruos</i>'
    >>> render_recons("recons", ["maruos", "gaul"], defaultdict(str, {"sens":"mort"}))
    '*<i>maruos</i> («&nbsp;mort&nbsp;»)'
    >>> render_recons("recons", ["sporo"], defaultdict(str, {"lang-mot-vedette":"fr", "sc":"Latn"}))
    '*<i>sporo</i>'
    >>> render_recons("recons", [], defaultdict(str, {"lang-mot-vedette":"fr"}))
    '*'
    """
    phrase = italic(parts.pop(0)) if parts else ""
    if data["sens"]:
        phrase += f" («&nbsp;{data['sens']}&nbsp;»)"
    return f"*{phrase}"


def render_refnec(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_refnec("recons", [], defaultdict(str, {"lang": "fr"}))
    ''
    >>> render_refnec("recons", ["phrase difficile à avaler"], defaultdict(str))
    '<u>phrase difficile à avaler</u>'
    """
    return underline(parts[0]) if parts else ""


def render_shuowen(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_shuowen("ShuoWen", ["一"], defaultdict(str))
    'Ce caractère 一 est une clef du ShuoWen.'
    >>> render_shuowen("ShuoWen", ["一 ", " 元, 天, 丕, 吏."], defaultdict(str))
    'Ce caractère 一 est une clef du ShuoWen. Composés mentionnés : 元, 天, 丕, 吏.'
    """
    text = f"Ce caractère {parts[0].strip()} est une clef du ShuoWen."
    if len(parts) > 1:
        text += f" Composés mentionnés : {parts[1].strip()}"
    return text


def render_siecle(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_siecle("siècle", [], defaultdict(str))
    '<i>(Siècle à préciser)</i>'
    >>> render_siecle("siècle", ["?"], defaultdict(str))
    '<i>(Siècle à préciser)</i>'
    >>> render_siecle("siècle", [""], defaultdict(str))
    '<i>(Siècle à préciser)</i>'
    >>> render_siecle("siècle", ["XVIII"], defaultdict(str))
    '<i>(XVIII<sup>e</sup> siècle)</i>'
    >>> render_siecle("siècle", ["XVIII", "XIX"], defaultdict(str))
    '<i>(XVIII<sup>e</sup> siècle – XIX<sup>e</sup> siècle)</i>'
    >>> render_siecle("siècle", ["1957"], defaultdict(str))
    '<i>(1957)</i>'
    >>> render_siecle("siècle", ["Vers le XI av. J.-C."], defaultdict(str))
    '<i>(Vers le XI<sup>e</sup> siècle av. J.-C.)</i>'
    >>> render_siecle("siècle", ["XVIII"], defaultdict(str, {"doute":"oui"}))
    '<i>(XVIII<sup>e</sup> siècle ?)</i>'
    >>> render_siecle("siècle", ["I", "III"], defaultdict(str))
    '<i>(I<sup>er</sup> siècle – III<sup>e</sup> siècle)</i>'
    >>> render_siecle("siècle", ["II - III"], defaultdict(str))
    '<i>(II<sup>e</sup> siècle - III)</i>'
    >>> render_siecle("siècle", ["XVIII?"], defaultdict(str))
    '<i>(XVIII<sup>e</sup> siècle?)</i>'
    >>> render_siecle("siècle", ["2<sup>e</sup> moitié du X<sup>e</sup> siècle"], defaultdict(str))
    '<i>(2<sup>e</sup> moitié du X<sup>e</sup> siècle)</i>'
    """
    parts = [part for part in parts if part.strip() and part != "?"]
    if not parts:
        return term("Siècle à préciser")

    def repl(x: re.Match[str]) -> str:
        sup = "er" if x.group()[:-1] == "I" else "e"
        return f"{x.group()[:-1]}{superscript(sup)} siècle{x.group()[-1]}"

    parts = [re.sub(r"([IVX]+)([^\s\w<]|\s)", repl, f"{part} ", count=1).strip() for part in parts]

    return term(" – ".join(parts) + (" ?" if data["doute"] else ""))


def render_siecle2(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_siecle2("siècle2", ["1"], defaultdict(str))
    "<span style='font-variant:small-caps'>i</span><sup>er</sup>"
    >>> render_siecle2("siècle2", ["I"], defaultdict(str))
    'I<sup>er</sup>'
    >>> render_siecle2("siècle2", ["i"], defaultdict(str))
    'I<sup>er</sup>'
    >>> render_siecle2("siècle2", ["18"], defaultdict(str))
    "<span style='font-variant:small-caps'>xviii</span><sup>e</sup>"
    >>> render_siecle2("siècle2", ["XVIII"], defaultdict(str))
    'XVIII<sup>e</sup>'
    >>> render_siecle2("siècle2", ["xviii"], defaultdict(str))
    'XVIII<sup>e</sup>'
    """
    number = parts[0]
    number_string = small_caps(int_to_roman(int(number)).lower()) if number.isnumeric() else number.upper()
    suffix = "er" if number in ("1", "I", "i") else "e"
    return f"{number_string}{superscript(suffix)}"


def render_sigle(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sigle("sigle", ["fr"], defaultdict(str))
    '<i>(Sigle)</i>'
    >>> render_sigle("sigle", ["en"], defaultdict(str, {"de": "United Nations"}))
    'Sigle de <i>United Nations</i>'
    >>> render_sigle("sigle", ["en"], defaultdict(str, {"de": "sens anti-horaire", "texte": "Sens Anti-Horaire", "m": "1"}))
    'Sigle de <i>Sens Anti-Horaire</i>'
    """
    phrase = "Sigle"
    if data["texte"]:
        phrase += f" de {italic(data['texte'])}"
    elif data["de"]:
        phrase += f" de {italic(data['de'])}"
    else:
        phrase = term(phrase)
    return phrase


def render_sinogram_noimg(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sinogram_noimg("sinogram-noimg", ["它"], defaultdict(str, {"clefhz1": "宀", "clefhz2": "2", "nbthz1": "1-5", "nbthz2": "5", "m4chz1": "3", "m4chz2": "3071<sub>1</sub>", "unihz": "5B83", "gbhz1": " ", "gbhz2": "-", "b5hz1": "A1", "b5hz2": "A5A6", "cjhz1": "J", "cjhz2": "十心", "cjhz3": "JP"}))
    'Codage informatique : <b>Unicode</b> : U+5B83 - <b>Big5</b> : A5A6 - <b>Cangjie</b> : 十心 (JP) - <b>Quatre coins</b> : 3071<sub>1</sub>'
    """
    text = "Codage informatique :"
    codages = []

    if unihz := data["unihz"]:
        codages.append(f"{strong('Unicode')} : U+{unihz}")

    if b5hz2 := data["b5hz2"]:
        codage = f"{strong('Big5')} : {b5hz2}"
        if b5hz3 := data["b5hz3"]:
            codage += f" ({b5hz3})"
        codages.append(codage)

    if cjhz2 := data["cjhz2"]:
        codage = f"{strong('Cangjie')} : {cjhz2}"
        if cjhz3 := data["cjhz3"]:
            codage += f" ({cjhz3})"
        codages.append(codage)

    if m4chz2 := data["m4chz2"]:
        codage = f"{strong('Quatre coins')} : {m4chz2}"
        if m4chz3 := data["m4chz3"]:
            codage += f" ({m4chz3})"
        codages.append(codage)

    return f"{text} {' - '.join(codages)}"


def render_subst(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_subst("subst", [], defaultdict(str, {"char": "劋", "de": "剿", "char1": "巢", "char2": "喿"}))
    '劋 : de 剿 où 喿 remplace 巢'
    >>> render_subst("subst", [], defaultdict(str, {"char": "劋", "de": "剿", "ici": "retrancher, détruire", "char1": "巢", "char2": "喿", "sens": "retrancher, détruire ; rusé"}))
    '劋 : de 剿 (ici : retrancher, détruire) où 喿 remplace 巢 : retrancher, détruire ; rusé'
    """
    text = f"{data['char']} : de {data['de']}"
    if ici := data["ici"]:
        text += f" (ici : {ici})"
    text += f" où {data['char2']} remplace {data['char1']}"
    if sens := data["sens"]:
        text += f" : {sens}"
    return text


def render_substantivation_de(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str))
    'Substantivation de <i>mot</i>'
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str, {"type": "adjectif"}))
    'Substantivation de l’adjectif <i>mot</i>'
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str, {"type": "infinitif"}))
    'Substantivation de l’infinitif <i>mot</i>'
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str, {"type": "participe"}))
    'Substantivation du participe du verbe <i>mot</i>'
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str, {"type": "locution verbale"}))
    'Substantivation de la locution verbale <i>mot</i>'
    >>> render_substantivation_de("substantivation de", ["mot", "fr"], defaultdict(str, {"type": "locution verbale", "sens": "verbeux"}))
    'Substantivation de la locution verbale <i>mot</i> (« verbeux »)'
    """
    text = "Substantivation"

    match type_ := data["type"]:
        case "adjectif" | "infinitif":
            text += f" de l’{type_}"
        case "locution verbale":
            text += f" de la {type_}"
        case "participe":
            text += f" du {type_} du verbe"
        case _:
            text += " de"

    text += f" {italic(parts[0])}"

    if sens := data["sens"]:
        text += f" (« {sens} »)"

    return text


def render_suisse(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_suisse("Suisse", ["fr"], defaultdict(str, {"précision":"Fribourg, Valais, Vaud"}))
    '<i>(Suisse : Fribourg, Valais, Vaud)</i>'
    >>> render_suisse("Suisse", ["it"], defaultdict(str))
    '<i>(Suisse)</i>'
    """
    if data["précision"]:
        return term(f"Suisse : {data['précision']}")
    else:
        return term("Suisse")


def render_suppletion(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_suppletion("supplétion", ["aller"], defaultdict(str))
    'Cette forme dénote une supplétion car son étymologie est distincte de celle de <i>aller</i>'
    >>> render_suppletion("supplétion", ["un"], defaultdict(str, {"mot":"oui"}))
    'Ce mot dénote une supplétion car son étymologie est distincte de celle de <i>un</i>'
    >>> render_suppletion("supplétion", ["better", "best"], defaultdict(str, {"lang":"en", "mot":"oui"}))
    'Ce mot dénote une supplétion car son étymologie est distincte de celles de <i>better</i> et de <i>best</i>'
    >>> render_suppletion("supplétion", ["am", "are", "was"], defaultdict(str, {"lang":"en", "mot":"oui"}))
    'Ce mot dénote une supplétion car son étymologie est distincte de celles de <i>am</i>, de <i>are</i> et de <i>was</i>'
    """
    if data["mot"]:
        phrase = "Ce mot dénote une supplétion car son étymologie est distincte de "
    else:
        phrase = "Cette forme dénote une supplétion car son étymologie est distincte de "
    if len(parts) > 1:
        phrase += "celles de "
        phrase += ", de ".join(f"{italic(p)}" for p in parts[:-1])
        phrase += f" et de {italic(parts[-1])}"
    else:
        phrase += f"celle de {italic(parts[0])}"
    return phrase


def render_t(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_t("T", ["oc"], defaultdict(str))
    'Occitan'
    >>> render_t("T", ["anglais"], defaultdict(str))
    'anglais'
    """
    lang = parts[0]
    return capitalize(langs[lang]) if lang in langs else lang


def render_temps_geologiques(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_temps_geologiques("Temps géologiques", ["givétien"], defaultdict(str))
    '387,7 ± 0,8'
    >>> render_temps_geologiques("supplétion", ["crétacé"], defaultdict(str))
    '~145,0'
    """
    from .temps_geologiques import times

    return times[parts[0]]


def render_term(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_term("term", ["ne … guère que"], defaultdict(str))
    '<i>(Ne … guère que)</i>'
    >>> render_term("terme", ["Astrophysique"], defaultdict(str))
    '<i>(Astrophysique)</i>'
    >>> render_term("terme", ["saules"], defaultdict(str, {"libellé": "arbres"}))
    '<i>(Arbres)</i>'
    >>> render_term("terme", [], defaultdict(str, {"1": "tératologie"}))
    '<i>(Tératologie)</i>'
    >>> render_term("terme", [], defaultdict(str, {"cat": "Saisons"}))
    ''
    """
    return term(capitalize(data["libellé"] or data["1"] or (parts[0] if parts else "")))


def render_trad(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_trad("trad-", ["la", "fiducia"], defaultdict(str))
    'fiducia'
    >>> render_trad("trad+", ["conv", "Sitophilus granarius"], defaultdict(str))
    'Sitophilus granarius'
    >>> render_trad("trad+", ["es", "bisojo"], defaultdict(str, {"dif": "bis-ojo"}))
    'bis-ojo'
    """
    return data["dif"] or parts[-1]


def render_transitif(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_transitif("transitif+", ["fr"], defaultdict(str, {"a1": "de"}))
    '<i>(Transitif avec le complément d’objet introduit par </i><b>de</b><i>)</i>'
    >>> render_transitif("transitif+", ["fr"], defaultdict(str, {"c1": "de"}))
    '<i>(Transitif avec le complément d’objet </i><b>de</b><i>)</i>'
    """
    phrase = "(Transitif avec le complément d’objet "
    if complement := data["a1"]:
        phrase += "introduit par "
    else:
        complement = data["c1"]
    return f"{italic(phrase)}{strong(complement)}{italic(')')}"


def render_transliterator(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_transliterator("transliterator", ["ar", "سم"], defaultdict(str))
    'sm'
    >>> render_transliterator("transliterator", ["ar"], defaultdict(str), word="زب")
    'zb'
    """
    text = parts[1] if len(parts) == 2 else word
    return transliterate(parts[0], text)


def render_unite(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_unite("unité", ["1234567"], defaultdict(str, {}))
    '1 234 567'
    >>> render_unite("unité", ["1234567.89"], defaultdict(str, {}))
    '1 234 567,89'
    >>> render_unite("unité", ["10.5", "m"], defaultdict(str, {}))
    '10,5 m'
    >>> render_unite("unité", ["10000", "km"], defaultdict(str, {}))
    '10 000 km'
    >>> render_unite("unité", ["10000", "km/h"], defaultdict(str, {}))
    '10 000 km/h'
    >>> render_unite("unité", ["10000", "km", "2"], defaultdict(str, {}))
    '10 000 km<sup>2</sup>'
    >>> render_unite("unité", ["10000", "km", "3"], defaultdict(str, {}))
    '10 000 km<sup>3</sup>'
    >>> render_unite("unité", ["10000", "kilomètres par heure"], defaultdict(str, {}))
    '10 000 kilomètres par heure'
    >>> render_unite("unité", ["10000", "km", "", "h", "-1"], defaultdict(str, {}))
    '10 000 km⋅h<sup>-1</sup>'
    >>> render_unite("unité", ["10000", "J", "2", "K", "3", "s", "-1"], defaultdict(str, {}))
    '10 000 J<sup>2</sup>⋅K<sup>3</sup>⋅s<sup>-1</sup>'
    >>> render_unite("unité", ["10000", "J", "", "kg", "", "m", "-2"], defaultdict(str, {}))
    '10 000 J⋅kg⋅m<sup>-2</sup>'
    >>> render_unite("unité", ["−40.234", "°C"], defaultdict(str, {}))
    '−40,234 °C'
    >>> render_unite("unité", ["1.23456", "J", "2", "K", "3", "s", "-1"], defaultdict(str, {"e": "9"}))
    '1,23456×10<sup>9</sup> J<sup>2</sup>⋅K<sup>3</sup>⋅s<sup>-1</sup>'
    >>> render_unite("unité", ["1", "m<sup>2</sup>"], defaultdict(str, {}))
    '1 m<sup>2</sup>'

    >>> # Spaces are not well handled in the decimal part:
    >>> # render_unite("unité", ["1,23456789"], defaultdict(str, {"e": 15}))
    >>> # '1,23 456 789×10<up>15</sup>'
    >>> # The rounding is not good here:
    >>> # render_unite("unité", ["1234567890.12345678", "¤"], defaultdict(str, {}))
    >>> # '1 234 567 890,12345678 ¤'
    >>> render_unite("unité", ["1.30", "m"], defaultdict(str, {}))
    '1,30 m'

    >>> # Non-numeric value
    >>> render_unite("unité", ["8 à 12", "cm"], defaultdict(str, {}))
    '8 à 12 cm'
    """
    from . import float_separator, thousands_separator

    sep = "⋅"
    value = parts.pop(0)
    try:
        phrase = number(value, float_separator, thousands_separator)
    except ValueError:
        phrase = value
    if data["e"]:  # exposant
        phrase += "×10" + superscript(data["e"])
    if parts:  # symbol
        phrase += f" {parts.pop(0)}"

    # Alternate exposant > symbol > exposant > symbol > ...
    is_exposant = True
    while parts:
        part = parts.pop(0)
        if is_exposant:
            phrase += superscript(part) if part else sep
        else:  # symbol
            phrase += sep + part if phrase[-1] != sep else part
        is_exposant = not is_exposant

    return phrase


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("flexion", ["foo"], defaultdict(str))
    'foo'

    >>> render_variant("fr-accord-ain", ["a.me.ʁi.k"], defaultdict(str), word="américain")
    'américain'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), word="animaux")
    'animal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), word="animal")
    'animal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), word="bucco-anale")
    'bucco-anal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), word="bucco-anales")
    'bucco-anal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), word="bucco-anaux")
    'bucco-anal'
    >>> render_variant("fr-accord-an", [], defaultdict(str, {"ms": "Birman"}))
    'Birman'
    >>> render_variant("fr-accord-comp", ["Saint-Martinois", "Longovicien", "sɛ̃.maʁ.ti.nwa", "lɔ̃.ɡɔ.vi.sjɛ̃"], defaultdict(str))
    'Saint-Martinois-Longovicien'
    >>> render_variant("fr-accord-comp-mf", ["capital", "risque", "ka.pi.tal", "ʁisk"], defaultdict(str, {"p1": "capitaux", "pp1": "ka.pi.to"}))
    'capital-risque'
    >>> render_variant("fr-accord-cons", ["ɑ̃.da.lu", "z", "s"], defaultdict(str, {"ms": "andalou"}))
    'andalou'
    >>> render_variant("fr-accord-cons", ["ɑ̃.da.lu", "z", "s"], defaultdict(str))
    ''
    >>> render_variant("fr-accord-eau", ["cham", "ʃa.m"], defaultdict(str, {"inv": "de Bactriane", "pinv": ".də.bak.tʁi.jan"}))
    'chameau de Bactriane'
    >>> render_variant("fr-accord-el", ["ɔp.sjɔ.n"], defaultdict(str, {"ms": "optionnel"}))
    'optionnel'
    >>> render_variant("fr-accord-en", ["bu.le."], defaultdict(str, {"ms": "booléen"}))
    'booléen'
    >>> render_variant("fr-accord-er", ["bouch", "bu.ʃ"], defaultdict(str, {"ms": "boucher"}))
    'boucher'
    >>> render_variant("fr-accord-et", ["kɔ.k"], defaultdict(str, {"ms": "coquet"}))
    'coquet'
    >>> render_variant("fr-accord-eur", ["ambl", "ɑ̃.bl"], defaultdict(str))
    'ambleur'
    >>> render_variant("fr-accord-eux", ["malheur", "ma.lœ.ʁ"], defaultdict(str))
    'malheureux'
    >>> render_variant("fr-accord-f", ["putati", "py.ta.ti"], defaultdict(str))
    'putatif'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), word="mallouinnes")
    'mallouin'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), word="mallouins")
    'mallouin'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), word="mallouinne")
    'mallouin'
    >>> render_variant("fr-accord-ind", [], defaultdict(str, {"m": "chacun", "pf": "ʃa.kyn", "pm": "ʃa.kœ̃"}), word="chacune")
    'chacun'
    >>> render_variant("fr-accord-mf", [], defaultdict(str, {"s": "bail"}))
    'bail'
    >>> render_variant("fr-accord-mf-ail", ["aspir"], defaultdict(str), word="aspirail")
    'aspirail'
    >>> render_variant("fr-accord-mf-ail", ["aspir"], defaultdict(str), word="aspiraux")
    'aspirail'
    >>> render_variant("fr-accord-mf-al", ["anim", "a.ni.m"], defaultdict(str))
    'animal'
    >>> render_variant("fr-accord-mixte", [], defaultdict(str, {"ms": "bourré comme un coing"}))
    'bourré comme un coing'
    >>> render_variant("fr-accord-mixte-rég", ["Fénassol"], defaultdict(str), word="Fénassol")
    'Fénassol'
    >>> render_variant("fr-accord-oin", [], defaultdict(str, {"pron": "sɑ̃.ta.lw"}), word="santaloines")
    'santaloine'
    >>> render_variant("fr-accord-ol", [], defaultdict(str), word="palmassolles")
    'palmassol'
    >>> render_variant("fr-accord-ol", [], defaultdict(str, {"ms": "martin"}), word="martinols")
    'martinol'
    >>> render_variant("fr-accord-on", [""], defaultdict(str), word="ambellon")
    'ambellon'
    >>> render_variant("fr-accord-ot", ["", "t"], defaultdict(str, {"s": "Grammoniot"}), word="ambellon")
    'Grammoniot'
    >>> render_variant("fr-accord-personne", ["Son Altesse"], defaultdict(str))
    'Son Altesse'
    >>> render_variant("fr-accord-rég", ["ka.ʁɔt"], defaultdict(str), word="aïeuls")
    'aïeul'
    >>> render_variant("fr-accord-rég", ["a.ta.ʃe də pʁɛs"], defaultdict(str, {"inv": "de presse", "ms": "attaché"}))
    'attaché de presse'
    >>> render_variant("fr-accord-s", [], defaultdict(str, {"ms": "Lumbrois"}))
    'Lumbrois'

    >>> render_variant("fr-rég", ["ka.ʁɔt"], defaultdict(str), word="carottes")
    'carotte'
    >>> render_variant("fr-rég", ["ʁy"], defaultdict(str, {"s": "ru"}))
    'ru'
    >>> render_variant("fr-rég", ["ɔm d‿a.fɛʁ"], defaultdict(str, {"inv": "d’affaires", "s": "homme"}), word="hommes d’affaires")
    'homme d’affaires'
    >>> render_variant("fr-rég-al", ["avion spati", "a.vjɔ̃ spa.sj"], defaultdict(str, {"radp": "avions spati"}))
    'avion spatial'
    >>> render_variant("fr-rég-x", [], defaultdict(str, {"s": "bail"}))
    'bail'

    >>> render_variant("fr-verbe-flexion", ["colliger"], defaultdict(str, {"ind.i.3s": "oui"}))
    'colliger'
    >>> render_variant("fr-verbe-flexion", [], defaultdict(str, {"1": "dire"}))
    'dire'
    """
    if tpl.endswith("flexion"):
        return data["1"] or (parts[0] if parts else "")

    if tpl.endswith("-ail"):
        suffix = tpl.split("-")[-1]
        if not word.endswith(suffix):
            return f"{parts[0]}{suffix}"

    if tpl.endswith("-al"):
        suffix = tpl.split("-")[-1]
        if not word.endswith(suffix):
            if word.endswith("e"):
                return word.removesuffix("e")
            if word.endswith("es"):
                return word.removesuffix("es")
            if word.endswith("aux"):
                return f"{word.removesuffix('ux')}l"
            return f"{parts[0]}{suffix}"

    if tpl.endswith("-ol"):
        suffix = tpl.split("-")[-1]
        if not word.endswith(suffix):
            if word.endswith("lle"):
                return word.removesuffix("le")
            if word.endswith("lles"):
                return word.removesuffix("les")
            if word.endswith("e"):
                return word.removesuffix("e")
            if word.endswith("es"):
                return word.removesuffix("es")
            return f"{data['ms'] or parts[0]}{suffix}"

    if "-rég" in tpl:
        if not (singular := data["s"] or data["m"] or data["ms"]):
            singular = word.rstrip("s")
        if data["inv"]:
            singular += f" {data['inv']}"
        return singular

    if "-cons" in tpl:
        singular = data["ms"] or ""
    elif "-comp" in tpl:
        singular = "-".join(parts[: len(parts) // 2])
    elif not (singular := data["s"] or data["m"] or data["ms"]):
        singular = word.rstrip("s") if len(parts) < 2 else f"{parts[0]}{tpl.split('-')[-1]}"
        if "-accord-in" in tpl and singular == word.rstrip("s"):
            singular = singular.removesuffix("ne" if data["deux_n"] else "e")
    if data["inv"]:
        singular += f" {data['inv']}"

    if not singular and tpl.endswith("-personne"):
        singular = parts[0] if parts else word

    return singular


def render_variante_du_radical_de_kangxi(
    tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = ""
) -> str:
    """
    >>> render_variante_du_radical_de_kangxi("variante du radical de Kangxi", ["⺁"], defaultdict(str), word="⺁")
    'Variante du radical de Kangxi 厂. Unicode : U+2E81.'
    >>> render_variante_du_radical_de_kangxi("variante du radical de Kangxi", [], defaultdict(str), word="⺁")
    'Variante du radical de Kangxi 厂. Unicode : U+2E81.'
    >>> render_variante_du_radical_de_kangxi("variante du radical de Kangxi", ["à droite"], defaultdict(str, {"var": "* &#x4e5a; sinogramme"}), word="⺃")
    'Variante à droite du radical de Kangxi 乙. Unicode : U+2E83.'
    """
    from .ko_hangeul.sinogramme import radical_trait

    if parts and parts[0] == word:
        parts.pop(0)

    text = "Variante"
    if parts:
        text += f" {parts[0]}"
    char = re.sub(r"\d+", "", radical_trait(word))  # Remove trailing numbers
    return f"{text} du radical de Kangxi {char}. Unicode : U+{hex(ord(word))[2:].upper()}."


def render_variante_ortho(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variante_ortho("Variante de", ["acupuncture", "fr"], defaultdict(str))
    '<i>Variante de</i> acupuncture'
    >>> render_variante_ortho("variante de", ["zêta"], defaultdict(str, {"sens": "lettre grecque ζ, Ζ"}))
    '<i>Variante de</i> zêta («&nbsp;lettre grecque ζ, Ζ&nbsp;»)'
    >>> render_variante_ortho("variante ortho de", ["acupuncture", "fr"], defaultdict(str))
    '<i>Variante orthographique de</i> acupuncture'
    >>> render_variante_ortho("Variante ortho de", ["Me"], defaultdict(str, {"dif": "M<sup>e</sup>"}))
    '<i>Variante orthographique de</i> M<sup>e</sup>'
    >>> render_variante_ortho("Variante ortho de", ["kwanliso"], defaultdict(str, {"sens": "camp de travail en Corée du Nord"}))
    '<i>Variante orthographique de</i> kwanliso («&nbsp;camp de travail en Corée du Nord&nbsp;»)'
    >>> render_variante_ortho("Variante ortho de", [], defaultdict(str))
    ''
    """
    if not parts:
        return ""
    phrase = italic("Variante orthographique de" if "ortho" in tpl else "Variante de")
    w = data["dif"] or parts.pop(0)
    phrase += f" {word_tr_sens(w, data['tr'], data['sens'], use_italic=False)}"
    return phrase


def render_wikisource(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_wikisource("ws", ["Les Grenouilles qui demandent un Roi"], defaultdict(str))
    'Les Grenouilles qui demandent un Roi'
    >>> render_wikisource("ws", ["Bible Segond 1910/Livre de Daniel", "Livre de Daniel"], defaultdict(str))
    'Livre de Daniel'
    >>> render_wikisource("ws", ["ADB:Emmerling, Ludwig August", "Ludwig August Emmerling"], defaultdict(str, {"lang":"de"}))
    'Ludwig August Emmerling'
    >>> render_wikisource("ws", ["ADB:Emmerling, Ludwig August"], defaultdict(str, {"lang":"de", "Ludwig August <span style": "'font-variant:small-caps'>Emmerling</span>"}))
    "Ludwig August <span style='font-variant:small-caps'>Emmerling</span>"
    """
    phrase = parts[-1]
    if data:
        # Possible imbricated templates: {{ws| {{pc|foo bar}} }}
        if potential_phrase := "".join(f"{k}={v}" for k, v in data.items() if k != "lang"):
            phrase = potential_phrase
    return phrase


def render_zh_lien(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_lien("zh-lien", ["人", "rén"], defaultdict(str))
    '人 (<i>rén</i>)'
    >>> render_zh_lien("zh-lien", ["马", "mǎ", "馬"], defaultdict(str))
    '马 (馬, <i>mǎ</i>)'
    >>> render_zh_lien("zh-lien", ["骨", "gǔ", "骨"], defaultdict(str))
    '骨 (骨, <i>gǔ</i>)'
    """
    simple = parts.pop(0)
    pinyin = italic(parts.pop(0))
    traditional = parts[0] if parts else ""
    return f"{simple} ({traditional}, {pinyin})" if traditional else f"{simple} ({pinyin})"


template_mapping = {
    "1e attestation": render_1e_attestation,
    "2e": render_2e,
    "3e": render_2e,
    "4e": render_2e,
    "abréviation": render_abreviation,
    "acronyme": render_acronyme,
    "agglutination": render_modele_etym,
    "ar-cf": render_ar_cf,
    "ar-mot": render_ar_mot,
    "ar-racine/nom": render_ar_root,
    "ar-sch": render_ar_sch,
    "ar-terme": render_ar_terme,
    "antonomase": render_modele_etym,
    "aphérèse": render_apherese,
    "apocope": render_apherese,
    "argot": render_argot,
    "au masculin": render_au_masculin,
    "C": render_contexte,
    "calque": render_etyl,
    "caractère Unicode": render_caractere_unicode,
    "cf": render_cf,
    "chunom": render_sinogram_noimg,
    "cit_réf": render_cit_ref,
    "cit réf": render_cit_ref,
    "contexte": render_contexte,
    "contraction": render_modele_etym,
    "compos": render_compose_de,
    "composé Alpheratz": render_composé_alpheratz,
    "composé de": render_compose_de,
    "composé_de": render_compose_de,
    "composé double-flexion": render_compose_double_flexion,
    "composé neutre": render_composé_neutre,
    "CS": render_cs,
    "date": render_date,
    "deet": render_compose_de,
    "déglutination": render_modele_etym,
    "dénominal": render_modele_etym,
    "déverbal": render_modele_etym,
    "déverbal sans suffixe": render_modele_etym,
    "équiv-pour": render_equiv_pour,
    "étyl": render_etyl,
    "étylp": render_etyl,
    "Étymologie graphique chinoise": render_etym_chinoise,
    "Etymologie graphique chinoise": render_etym_chinoise,
    "forme reconstruite": render_recons,
    "hangeul unicode": render_ko_translit,
    "hypercorrection": render_hypercorrection,
    "ko-pron": render_ko_pron,
    "ko-translit": render_ko_translit,
    "la-verb": render_la_verb,
    "laé": render_lae,
    "lang": render_lang,
    "Lang": render_lang,
    "lien": render_lien,
    "lien-ancre-étym": render_lae,
    "lien web": render_lien_web,
    "Lien web": render_lien_web,
    "l": render_lien,
    "LienRouge": render_lien_rouge,
    "mot-valise": render_mot_valise,
    "mn-lien": render_mn_lien,
    "nom_langue": render_nom_langue,
    "parataxe": render_modele_etym,
    "polytonique": render_polytonique,
    "Polytonique": render_polytonique,
    "PS": render_ps,
    "radical de Kangxi": render_radical_de_kangxi,
    "recons": render_recons,
    "réf?": render_refnec,
    "réf ?": render_refnec,
    "refnec": render_refnec,
    "réfnéc": render_refnec,
    "réfnec": render_refnec,
    "réfsou": render_refnec,
    "référence nécessaire": render_refnec,
    "Référence nécessaire": render_refnec,
    "reverlanisation": render_modele_etym,
    "ShuoWen": render_shuowen,
    "siècle": render_siecle,
    "siècle2": render_siecle2,
    "sigle": render_sigle,
    "sinogram-noimg": render_sinogram_noimg,
    "source?": render_refnec,
    "source ?": render_refnec,
    "subst": render_subst,
    "substantivation de": render_substantivation_de,
    "Suisse": render_suisse,
    "supplétion": render_suppletion,
    "syncope": render_modele_etym,
    "T": render_t,
    "Temps géologiques": render_temps_geologiques,
    "term": render_term,
    "terme": render_term,
    "term lien": render_term,
    "trad-": render_trad,
    "trad+": render_trad,
    "transitif+": render_transitif,
    "transliterator": render_transliterator,
    "Variante de": render_variante_ortho,
    "variante de": render_variante_ortho,
    "variante du radical de Kangxi": render_variante_du_radical_de_kangxi,
    "Variante ortho de": render_variante_ortho,
    "variante ortho de": render_variante_ortho,
    "variante orthographique de": render_variante_ortho,
    "Unité": render_unite,
    "unité": render_unite,
    "univerbation": render_modele_etym,
    "ws": render_wikisource,
    "zh-lien": render_zh_lien,
    **dict.fromkeys({"ar-ab", "ar-mo"}, render_ar_ab),
    #
    # Variants
    #
    "__variant__fr-accord-ain": render_variant,
    "__variant__fr-accord-al": render_variant,
    "__variant__fr-accord-an": render_variant,
    "__variant__fr-accord-comp": render_variant,
    "__variant__fr-accord-comp-mf": render_variant,
    "__variant__fr-accord-cons": render_variant,
    "__variant__fr-accord-eau": render_variant,
    "__variant__fr-accord-el": render_variant,
    "__variant__fr-accord-en": render_variant,
    "__variant__fr-accord-er": render_variant,
    "__variant__fr-accord-et": render_variant,
    "__variant__fr-accord-eur": render_variant,
    "__variant__fr-accord-eux": render_variant,
    "__variant__fr-accord-f": render_variant,
    "__variant__fr-accord-in": render_variant,
    "__variant__fr-accord-ind": render_variant,
    "__variant__fr-accord-mf": render_variant,
    "__variant__fr-accord-mf-al": render_variant,
    "__variant__fr-accord-mf-ail": render_variant,
    "__variant__fr-accord-mixte": render_variant,
    "__variant__fr-accord-mixte-rég": render_variant,
    "__variant__fr-accord-oin": render_variant,
    "__variant__fr-accord-ol": render_variant,
    "__variant__fr-accord-on": render_variant,
    "__variant__fr-accord-ot": render_variant,
    "__variant__fr-accord-personne": render_variant,
    "__variant__fr-accord-rég": render_variant,
    "__variant__fr-accord-s": render_variant,
    "__variant__fr-accord-un": render_variant,
    "__variant__fr-rég": render_variant,
    "__variant__fr-rég-al": render_variant,
    "__variant__fr-rég-x": render_variant,
    "__variant__fr-verbe-flexion": render_variant,
    "__variant__flexion": render_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
