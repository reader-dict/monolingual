from collections import defaultdict


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("flexion", ["foo"], defaultdict(str), "")
    'foo'

    >>> render_variant("fr-accord-ain", ["a.me.ʁi.k"], defaultdict(str), "américain")
    'américain'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), "animaux")
    'animal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), "animal")
    'animal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), "bucco-anale")
    'bucco-anal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), "bucco-anales")
    'bucco-anal'
    >>> render_variant("fr-accord-al", ["anim", "a.ni.m"], defaultdict(str), "bucco-anaux")
    'bucco-anal'
    >>> render_variant("fr-accord-an", [], defaultdict(str, {"ms": "Birman"}), "")
    'Birman'
    >>> render_variant("fr-accord-comp", ["Saint-Martinois", "Longovicien", "sɛ̃.maʁ.ti.nwa", "lɔ̃.ɡɔ.vi.sjɛ̃"], defaultdict(str), "")
    'Saint-Martinois-Longovicien'
    >>> render_variant("fr-accord-comp-mf", ["capital", "risque", "ka.pi.tal", "ʁisk"], defaultdict(str, {"p1": "capitaux", "pp1": "ka.pi.to"}), "")
    'capital-risque'
    >>> render_variant("fr-accord-cons", ["ɑ̃.da.lu", "z", "s"], defaultdict(str, {"ms": "andalou"}), "")
    'andalou'
    >>> render_variant("fr-accord-cons", ["ɑ̃.da.lu", "z", "s"], defaultdict(str), "")
    ''
    >>> render_variant("fr-accord-eau", ["cham", "ʃa.m"], defaultdict(str, {"inv": "de Bactriane", "pinv": ".də.bak.tʁi.jan"}), "")
    'chameau de Bactriane'
    >>> render_variant("fr-accord-el", ["ɔp.sjɔ.n"], defaultdict(str, {"ms": "optionnel"}), "")
    'optionnel'
    >>> render_variant("fr-accord-en", ["bu.le."], defaultdict(str, {"ms": "booléen"}), "")
    'booléen'
    >>> render_variant("fr-accord-er", ["bouch", "bu.ʃ"], defaultdict(str, {"ms": "boucher"}), "")
    'boucher'
    >>> render_variant("fr-accord-et", ["kɔ.k"], defaultdict(str, {"ms": "coquet"}), "")
    'coquet'
    >>> render_variant("fr-accord-eur", ["ambl", "ɑ̃.bl"], defaultdict(str), "")
    'ambleur'
    >>> render_variant("fr-accord-eux", ["malheur", "ma.lœ.ʁ"], defaultdict(str), "")
    'malheureux'
    >>> render_variant("fr-accord-f", ["putati", "py.ta.ti"], defaultdict(str), "")
    'putatif'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), "mallouinnes")
    'mallouin'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), "mallouins")
    'mallouin'
    >>> render_variant("fr-accord-in", ["ma.lw"], defaultdict(str, {"deux_n": "1"}), "mallouinne")
    'mallouin'
    >>> render_variant("fr-accord-ind", [], defaultdict(str, {"m": "chacun", "pf": "ʃa.kyn", "pm": "ʃa.kœ̃"}), "chacune")
    'chacun'
    >>> render_variant("fr-accord-mf", [], defaultdict(str, {"s": "bail"}), "")
    'bail'
    >>> render_variant("fr-accord-mf-ail", ["aspir"], defaultdict(str), "aspirail")
    'aspirail'
    >>> render_variant("fr-accord-mf-ail", ["aspir"], defaultdict(str), "aspiraux")
    'aspirail'
    >>> render_variant("fr-accord-mf-al", ["anim", "a.ni.m"], defaultdict(str), "")
    'animal'
    >>> render_variant("fr-accord-mixte", [], defaultdict(str, {"ms": "bourré comme un coing"}), "")
    'bourré comme un coing'
    >>> render_variant("fr-accord-mixte-rég", ["Fénassol"], defaultdict(str), "Fénassol")
    'Fénassol'
    >>> render_variant("fr-accord-oin", [], defaultdict(str, {"pron": "sɑ̃.ta.lw"}), "santaloines")
    'santaloine'
    >>> render_variant("fr-accord-ol", [], defaultdict(str), "palmassolles")
    'palmassol'
    >>> render_variant("fr-accord-ol", [], defaultdict(str, {"ms": "martin"}), "martinols")
    'martinol'
    >>> render_variant("fr-accord-on", [""], defaultdict(str), "ambellon")
    'ambellon'
    >>> render_variant("fr-accord-ot", ["", "t"], defaultdict(str, {"s": "Grammoniot"}), "ambellon")
    'Grammoniot'
    >>> render_variant("fr-accord-oux", ["r", "ʁ"], defaultdict(str, {"suff": "ss"}), "roux")
    'roux'
    >>> render_variant("fr-accord-oux", ["r", "ʁ"], defaultdict(str, {"suff": "ss"}), "rouss")
    'roux'
    >>> render_variant("fr-accord-personne", ["Son Altesse"], defaultdict(str), "")
    'Son Altesse'
    >>> render_variant("fr-accord-rég", ["ka.ʁɔt"], defaultdict(str), "aïeuls")
    'aïeul'
    >>> render_variant("fr-accord-rég", ["a.ta.ʃe də pʁɛs"], defaultdict(str, {"inv": "de presse", "ms": "attaché"}), "")
    'attaché de presse'
    >>> render_variant("fr-accord-s", [], defaultdict(str, {"ms": "Lumbrois"}), "")
    'Lumbrois'
    >>> render_variant("fr-accord-t-avant1835", ["bruyan", "bʁɥi.jɑ̃"], defaultdict(str), "bruyans")
    'bruyant'

    >>> render_variant("fr-rég", ["ka.ʁɔt"], defaultdict(str), "carottes")
    'carotte'
    >>> render_variant("fr-rég", ["ʁy"], defaultdict(str, {"s": "ru"}), "")
    'ru'
    >>> render_variant("fr-rég", ["ɔm d‿a.fɛʁ"], defaultdict(str, {"inv": "d’affaires", "s": "homme"}), "hommes d’affaires")
    'homme d’affaires'
    >>> render_variant("fr-rég-al", ["avion spati", "a.vjɔ̃ spa.sj"], defaultdict(str, {"radp": "avions spati"}), "")
    'avion spatial'
    >>> render_variant("fr-rég-x", [], defaultdict(str, {"s": "bail"}), "")
    'bail'

    >>> render_variant("fr-verbe-flexion", ["colliger"], defaultdict(str, {"ind.i.3s": "oui"}), "")
    'colliger'
    >>> render_variant("fr-verbe-flexion", [], defaultdict(str, {"1": "dire"}), "")
    'dire'
    """
    if tpl.endswith("flexion"):
        return data["1"] or (parts[0] if parts else "")

    if tpl.endswith("-ail"):
        suffix = tpl.split("-")[-1]
        if not word.endswith(suffix):
            return f"{parts[0]}{suffix}"

    if tpl.endswith("-t-avant1835"):
        return f"{parts[0]}t"

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


handlers = {
    **dict.fromkeys(
        {
            "fr-accord-ain",
            "fr-accord-al",
            "fr-accord-an",
            "fr-accord-comp",
            "fr-accord-comp-mf",
            "fr-accord-cons",
            "fr-accord-eau",
            "fr-accord-el",
            "fr-accord-en",
            "fr-accord-er",
            "fr-accord-et",
            "fr-accord-eur",
            "fr-accord-eux",
            "fr-accord-f",
            "fr-accord-in",
            "fr-accord-ind",
            "fr-accord-mf",
            "fr-accord-mf-al",
            "fr-accord-mf-ail",
            "fr-accord-mixte",
            "fr-accord-mixte-rég",
            "fr-accord-oin",
            "fr-accord-ol",
            "fr-accord-on",
            "fr-accord-ot",
            "fr-accord-oux",
            "fr-accord-personne",
            "fr-accord-rég",
            "fr-accord-s",
            "fr-accord-t-avant1835",
            "fr-accord-un",
            "fr-rég",
            "fr-rég-al",
            "fr-rég-x",
            "fr-verbe-flexion",
            "flexion",
        },
        render_variant,
    ),
}
