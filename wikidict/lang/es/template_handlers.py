from collections import defaultdict

from ...user_functions import (
    capitalize,
    concat,
    extract_keywords_from,
    italic,
    small,
    strong,
    subscript,
)
from .langs import langs

articulos: dict[str, str] = {
    "def.f.pl": "las",
    "indef.f.pl": "unas",
    "def.f.sg": "la",
    "indef.f.sg": "una",
    "def.m.pl": "los",
    "indef.m.pl": "unos",
    "def.m.sg": "el",
    "def.m.sg.prep": "l",
    "indef.m.sg": "un",
}

catgrams: dict[str, dict[str, str]] = {
    "adjetivo": {
        "sg": "adjetivo",
        "gen": "m",
        "adj_f_sg": "adjetiva",
    },
    "pronombre": {
        "sg": "pronombre",
        "gen": "m",
        "adj_f_sg": "pronombre",
    },
    "sustantivo": {
        "sg": "sustantivo",
        "gen": "m",
        "adj_f_sg": "sustantiva",
    },
    "verbo": {
        "sg": "verbo",
        "gen": "m",
        "adj_f_sg": "verbo",
    },
}


def catgram(catgram: str, variation: str = "gen") -> str:
    return catgrams[catgram][variation]


def inflect_articulo(genero: str = "m", tipo: str = "def", numero: str = "sg", prep: bool = False) -> str:
    key = f"{tipo}.{genero}.{numero}"
    if prep:
        if key != "def.m.sg":
            return " "
        key += ".prep"
    return articulos[key]


def normalizar_nombre(to_normalize: str) -> str:
    """
    >>> normalizar_nombre("en")
    'inglés'
    >>> normalizar_nombre("")
    ''
    """
    return langs.get(to_normalize, to_normalize)


def render_adjetivo_de_verbo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_adjetivo_de_verbo("adjetivo de verbo", ["gorjear", "gorjea"], defaultdict(str))
    'Que gorjea'
    >>> render_adjetivo_de_verbo("adjetivo de verbo", ["gorjear", "gorjea","unificar", "unifica"], defaultdict(str))
    'Que gorjea o que unifica'
    """
    result = ""
    if len(parts) > 1:
        result += f"Que {parts[1]}"
    if len(parts) > 3:
        result += f" o que {parts[3]}"
    return result


def render_nimo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_nimo("antónimo", ["estatal", "público"], defaultdict(str))
    'Antónimos: estatal, público'
    >>> render_nimo("antónimo", ["público"], defaultdict(str))
    'Antónimo: público'
    >>> render_nimo("sinónimos", ["estatal", "público"], defaultdict(str))
    'Sinónimos: estatal, público'
    >>> render_nimo("sinónimo", ["público"], defaultdict(str))
    'Sinónimo: público'
    """
    result = "Antónimo" if tpl.startswith("ant") else "Sinónimo"
    if len(parts) > 1:
        result += "s"
    result += ": "
    result += concat(parts, ", ")
    return result


def render_afi(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_afi("AFI", ["/oː/", "/aː/"], defaultdict(str))
    '/oː/, /aː/ <small>(AFI)</small>'
    >>> render_afi("IPA", ["/oː/"], defaultdict(str))
    '/oː/ <small>(AFI)</small>'
    """
    return concat(parts, ", ") + f" {small('(AFI)')}"


def render_aumentativo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_aumentativo("aumentativo", ["perro"], defaultdict(str))
    '<i>Aumentativo de</i> perro'
    >>> render_aumentativo("aumentativo", ["azada"], defaultdict(str, {"tipo" : "sustantivo"}))
    '<i>Aumentativo del sustantivo</i> azada'
    >>> render_aumentativo("aumentativo", ["perro"], defaultdict(str, {"i": "x", "tipo" : "sustantivo"}))
    '<i>Aumentativo irregular del sustantivo</i> perro'
    >>> render_aumentativo("diminutivo", ["perro"], defaultdict(str))
    '<i>Diminutivo de</i> perro'
    """
    if tpl in {"diminutivo", "forma diminutivo"}:
        start = "Diminutivo "
    else:
        start = "Aumentativo "
    if data["irregular"] or data["irreg"] or data["irr"] or data["i"]:
        start += "irregular "
    start += "de"
    if data["tipo"]:
        start += f"l {data['tipo']}"
    phrase = f"{italic(start)}"
    phrase += f" {render_l('l', [data['alt'] or parts[0]], data)}"
    return phrase


def render_adverbio_de_adjetivo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_adverbio_de_adjetivo("adverbio_de_adjetivo", ["accidental"], defaultdict(str))
    'De un modo accidental'
    >>> render_adverbio_de_adjetivo("adverbio_de_adjetivo", ["completo", "pleno"], defaultdict(str))
    'De un modo completo o pleno'
    >>> render_adverbio_de_adjetivo("adverbio_de_adjetivo", ["completo", "pleno", "total"], defaultdict(str))
    'De un modo completo, pleno o total'
    """
    result = ""
    if parts:
        result += "De un modo "
    result += concat(parts, ", ", last_sep=" o ")
    return result


def render_adverbio_de_sustantivo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_adverbio_de_sustantivo("adverbio de sustantivo", ["escabrosidad"], defaultdict(str))
    'Con escabrosidad'
    """
    result = ""
    if parts:
        result += "Con "
    result += concat(parts, ", ", last_sep=" o ")
    return result


def render_comparativo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_comparativo("comparativo", ["bueno", "es"], defaultdict(str, {"irr": "s"}))
    '<i>Comparativo irregular de</i> bueno'
    >>> render_comparativo("comparativo", ["bueno", "es"], defaultdict(str, {"tipo": "regular"}))
    '<i>Comparativo regular de</i> bueno'
    """
    word = parts[0] if parts else ""
    start = "Comparativo"
    if data["tipo"]:
        start += f" {data['tipo']}"
    if data["i"] or data["irr"] or data["irreg"] or data["irregular"]:
        start += " irregular"
    start += " de"
    phrase = f"{italic(start)} "
    phrase += render_l("l", [data["alt"] or word], data)
    return phrase


def render_contraccion(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_contraccion("contracción", ["de", "ellas"], defaultdict(str, {"leng": "es"}))
    '<i>Contracción de</i> de <i>y</i> ellas'
    >>> render_contraccion("contracción", ["mi", "hija", "adjetivo", "sustantivo"], defaultdict(str, {"leng": "es"}))
    '<i>Contracción del adjetivo</i> mi <i>y el sustantivo</i> hija'
    >>> render_contraccion("contracción", ["give", "me", "verbo", "pronombre"], defaultdict(str, {"leng": "en"}))
    '<i>Contracción del verbo</i> give <i>y el pronombre</i> me'
    """
    typo1 = data["typo1"] or parts[2] if len(parts) > 2 else ""
    typo2 = data["typo2"] or parts[3] if len(parts) > 3 else ""
    phrase = "Contracción de"
    phrase += f"{inflect_articulo(catgram(typo1), prep=True)} {typo1}" if typo1 else ""
    phrase = italic(phrase)
    phrase += f" {parts[0]} "
    phrase2 = "y"
    phrase2 += f" {inflect_articulo(catgram(typo2))} {typo2}" if typo2 else ""
    phrase += italic(phrase2)
    phrase += f" {parts[1]}"
    return phrase


def render_dle(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_dle("DLE", [], defaultdict(str), word="raulí")
    '«raulí» en <i>Diccionario de la lengua española</i>. Editorial: Real Academia Española, Asociación de Academias de la Lengua Española y Espasa. 23.ª ed, Madrid, 2014.'
    >>> render_dle("DLE", ["titulo"], defaultdict(str, {"fc" : "2024-10-23"}), word="raulí")
    '«titulo» en <i>Diccionario de la lengua española</i>. Editorial: Real Academia Española, Asociación de Academias de la Lengua Española y Espasa. 23.ª ed, Madrid, 2014. Consultado: 23 oct 2024.'
    """
    phrase = (
        f"«{parts[0] if parts else word}» en {italic('Diccionario de la lengua española')}. "
        "Editorial: Real Academia Española, Asociación de Academias de la Lengua Española y Espasa. "
        "23.ª ed, Madrid, 2014."
    )
    if consulted := data["fc"]:
        year, month, day = consulted.split("-")
        month = {
            "01": "ene",
            "02": "feb",
            "03": "mar",
            "04": "abr",
            "05": "may",
            "06": "jun",
            "07": "jul",
            "08": "ago",
            "09": "set",
            "10": "oct",
            "11": "noc",
            "12": "dic",
        }[month]
        phrase += f" Consultado: {day} {month} {year}."
    return phrase


def render_etim(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etim("etim", ["la", "folia"], defaultdict(str))
    'del latín <i>folia</i>'
    >>> render_etim("etim", ["grc", "φάσηλος"], defaultdict(str, {"tr": "phásēlos"}))
    'del griego antiguo <i>φάσηλος</i> (<i>phásēlos</i>)'
    >>> render_etim("etim", ["ar", "كنية"], defaultdict(str, {"tr": "kunyah", "glosa":"sobrenombre", "glosa-alt": "sobrenombre honorífico"}))
    "del árabe <i>كنية</i> (<i>kunyah</i>, 'sobrenombre honorífico')"
    >>> render_etim("etim", ["grc", "ἱδρώς", "sudor"], defaultdict(str))
    "del griego antiguo <i>ἱδρώς</i> ('sudor')"
    >>> render_etim("etim", ["acuñado", "Johann A. Wagner"], defaultdict(str))
    'acuñado por Johann A. Wagner'
    >>> render_etim("etim", ["grc", "κομψος", "elegante", "grc", "γναθος", "mandíbula", ""], defaultdict(str))
    "del griego antiguo <i>κομψος</i> ('elegante') y <i>γναθος</i> ('mandíbula')"
    >>> render_etim("etim", ["nan", "日本"], defaultdict(str, {"tr": "Ji̍t-pún", "d": "hokkien"}))
    'del min nan (hokkien) <i>日本</i> (<i>Ji̍t-pún</i>)'
    """
    if parts[0] == "acuñado":
        return f"{parts[0]} por {parts[1]}"

    result = f"del {normalizar_nombre(parts.pop(0))}"
    if d := data["d"]:
        result += f" ({d})"
    more: list[str] = []
    while parts:
        lplus = render_l(
            "l+",
            [data.pop("diacrítico", "") or data.pop("alt", "") or (parts.pop(0) if parts else "")],
            defaultdict(
                str,
                {
                    "glosa": data.pop("glosa", "") or (parts.pop(0) if parts else ""),
                    "glosa-alt": data.pop("glosa-alt", ""),
                    "núm": data.pop("núm", "") or data.pop("num", ""),
                    "tr": data.pop("tr", "") or data.pop("transcripción", ""),
                },
            ),
        )
        if lplus:
            more.append(lplus)
        if parts:
            parts.pop(0)  # Remove the destination lang
    if more:
        result += f" {' y '.join(more)}"
    return result


def render_etimologia(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_etimologia("etimología", [], defaultdict(str))
    ''
    >>> render_etimologia("etimología", [""], defaultdict(str))
    ''
    >>> render_etimologia("etimología", ["apócope", "Natalia"], defaultdict(str))
    'Acortamiento de <i>Natalia</i>'
    >>> render_etimologia("etimología", ["calco", "en", "plastiglomerate"], defaultdict(str, {"por": "por"}))
    'por calco del inglés <i>plastiglomerate</i>'
    >>> render_etimologia("etimología", ["compuesto", "sacar", "punta"], defaultdict(str))
    'Compuesto de <i>sacar</i> y <i>punta</i>'
    >>> render_etimologia("etimología", ["compuesto", "regio", "monte", "-ano"], defaultdict(str))
    'Compuesto de <i>regio</i>, <i>monte</i> y <i>-ano</i>'
    >>> render_etimologia("etimología", ["compuesto", "-ónimo", "-iae"], defaultdict(str, {"e":"e"}))
    'Compuesto de <i>-ónimo</i> e <i>-iae</i>'
    >>> render_etimologia("etimología", ["confijo", "anglo", "filo"], defaultdict(str, {"tilde":"sí"}))
    'Del prefijo <i>anglo-</i> y el sufijo <i>-́filo</i>'
    >>> render_etimologia("etimología", ["confijo", "des", "garra", "ar"], defaultdict(str))
    'Del prefijo <i>des-</i>, <i>garra</i> y el sufijo <i>-ar</i>'
    >>> render_etimologia("etimología", ["confijo", "en", "furia", "ecer"], defaultdict(str, {"tr2":"ira, cólera"}))
    'Del prefijo <i>en-</i>, <i>furia</i> (<i>ira, cólera</i>) y el sufijo <i>-ecer</i>'
    >>> render_etimologia("etimología", ["epónimo", "de Adelita, protagonista de un corrido mexicano"], defaultdict(str))
    'Epónimo: de Adelita, protagonista de un corrido mexicano'
    >>> render_etimologia("etimología", ["femenino", "topógrafo"], defaultdict(str))
    'De <i>topógrafo</i> y el sufijo flexivo <i>-a</i> para el femenino'
    >>> render_etimologia("etimología", ["femenino", "Jesús", "a"], defaultdict(str))
    'De <i>Jesús</i> y el sufijo flexivo <i>a</i> para el femenino'
    >>> render_etimologia("etimología", ["metátesis", "rigoroso"], defaultdict(str))
    'Por metátesis de <i>rigoroso</i>'
    >>> render_etimologia("etimología", ["fone", "-mos"], defaultdict(str))
    'Alteración fonética de <i>-mos</i>'
    >>> render_etimologia("etimología", ["fonética", "empeller"], defaultdict(str))
    'Por alteración fonética de <i>empeller</i>'
    >>> render_etimologia("etimología", ["japonés", "片仮名"], defaultdict(str, {"transcripción":"カタカナ, katakana"}))
    'Del japonés <i>片仮名</i> (<i>カタカナ, katakana</i>)'
    >>> render_etimologia("etimología", ["la", "incertus"], defaultdict(str))
    'Del latín <i>incertus</i>'
    >>> render_etimologia("etimología", ["la", "piscis", "pez"], defaultdict(str))
    "Del latín <i>piscis</i> ('pez')"
    >>> render_etimologia("etimología", ["la", "-aceus"], defaultdict(str, {"alt":"-acĕus"}))
    'Del latín <i>-acĕus</i>'
    >>> render_etimologia("etimología", ["la", "illos"], defaultdict(str, {"diacrítico":"illōs", "sig":"no"}))
    'Del latín <i>illōs</i>'
    >>> render_etimologia("etimología", ["la", "villus", "vello"], defaultdict(str))
    "Del latín <i>villus</i> ('vello')"
    >>> render_etimologia("etimología", ["la", "villus", "vello", ""], defaultdict(str))
    "Del latín <i>villus</i> ('vello')"
    >>> render_etimologia("etimología", ["bajo latín", "capitanus", "principal"], defaultdict(str))
    "Del bajo latín <i>capitanus</i> ('principal')"
    >>> render_etimologia("etimología", ["osp", "fasta"], defaultdict(str))
    'Del castellano antiguo <i>fasta</i>'
    >>> render_etimologia("etimología", ["grc", "ἄκανθα", "espina", "grc","πτερύγιον", "aleta"], defaultdict(str, {"tr":"akntha", "tr2": "pterúgion"}))
    "Del griego antiguo <i>ἄκανθα</i> (<i>akntha</i>, 'espina') y <i>πτερύγιον</i> (<i>pterúgion</i>, 'aleta')"
    >>> render_etimologia("etimología", ["osp", "foja", "", "osp","foia"], defaultdict(str))
    'Del castellano antiguo <i>foja</i> y <i>foia</i>'
    >>> render_etimologia("etimología", ["osp", "foja", "", "la","sed"], defaultdict(str))
    'Del castellano antiguo <i>foja</i> y el latín <i>sed</i>'
    >>> render_etimologia("etimología", ["rmq", "lumí", "concubina"], defaultdict(str, {"glosa-alt":"concubina, manceba, querida"}))
    "Del caló <i>lumí</i> ('concubina, manceba, querida')"
    >>> render_etimologia("etimología", ["ONOM"], defaultdict(str))
    'Onomatopéyica'
    >>> render_etimologia("etimología", ["plural", "vista"], defaultdict(str))
    'De <i>vista</i> y el sufijo flexivo <i>-s</i>'
    >>> render_etimologia("etimología", ["plural", "vacación", "-es"], defaultdict(str))
    'De <i>vacación</i> y el sufijo flexivo <i>-es</i>'
    >>> render_etimologia("etimología", ["pronominal", "agrupar"], defaultdict(str))
    'De <i>agrupar</i> con el pronombre reflexivo átono'
    >>> render_etimologia("etimología", ["pronominal", "espinar"], defaultdict(str, {"num": "1"}))
    'De <i>espinar<sub>1</sub></i> con el pronombre reflexivo átono'
    >>> render_etimologia("etimología", ["regresiva", "controvertido"], defaultdict(str))
    'Por derivación regresiva de <i>controvertido</i>'
    >>> render_etimologia("etimología", ["sánscrito", "गुरू", "maestro"], defaultdict(str, {"transcripción":"gūru"}))
    "Del sánscrito <i>गुरू</i> (<i>gūru</i>, 'maestro')"
    >>> render_etimologia("etimología", ["sufijo", "átomo", "ico"], defaultdict(str))
    'De <i>átomo</i> y el sufijo <i>-ico</i>'
    >>> render_etimologia("etimología", ["sufijo", "mantener", "-ncia"], defaultdict(str))
    'De <i>mantener</i> y el sufijo <i>-ncia</i>'
    >>> render_etimologia("etimología", ["sufijo", "ferrojo", "ar"], defaultdict(str, {"tr":"anticuado por cerrojo e influido por fierro"}))
    'De <i>ferrojo</i> (<i>anticuado por cerrojo e influido por fierro</i>) y el sufijo <i>-ar</i>'
    >>> render_etimologia("etimología", ["sufijo", "espumar", "ero"], defaultdict(str, {"alt":"espumado", "alt2":"era"}))
    'De <i>espumado</i> y el sufijo <i>-era</i>'
    >>> render_etimologia("etimología", ["sufijo", "héroe", "ficar"], defaultdict(str, {"tr2":"en su variante -ificar"}))
    'De <i>héroe</i> y el sufijo <i>-ficar</i> (<i>en su variante -ificar</i>)'
    >>> render_etimologia("etimología", ["sufijo", "bullicio", "ar"], defaultdict(str, {"glosa":"bullicio"}))
    "De <i>bullicio</i> ('bullicio') y el sufijo <i>-ar</i>"
    >>> render_etimologia("etimología", ["prefijo", "a", "contecer"], defaultdict(str))
    'Del prefijo <i>a-</i> y <i>contecer</i>'
    >>> render_etimologia("etimología", ["prefijo", "a-", "contecer"], defaultdict(str))
    'Del prefijo <i>a-</i> y <i>contecer</i>'
    >>> render_etimologia("etimología", ["incierta"], defaultdict(str))
    'Incierta'
    >>> render_etimologia("etimología", ["EPON", "de la ciudad alemana de Berlín"], defaultdict(str))
    'Epónimo: de la ciudad alemana de Berlín'
    >>> render_etimologia("etimología", ["endo", "chocoano"], defaultdict(str))
    'De <i>chocoano</i>'
    >>> render_etimologia("etimología", ["dimi", "cata"], defaultdict(str))
    'Diminutivo de <i>cata</i>'
    >>> render_etimologia("etimología", ["marca", "Chapadur"], defaultdict(str))
    'De la marca registrada <i>Chapadur</i>®'
    >>> render_etimologia("etimología", ["véase", "toto"], defaultdict(str))
    'Véase <i>toto</i>'
    >>> render_etimologia("etimología", ["masculino", "fonomímica"], defaultdict(str))
    'De <i>fonomímica</i> y el sufijo flexivo -o para el masculino'
    """

    def call_l_single_part(part: str, index: int) -> str:
        sindex = str(index) if index > 1 else ""
        return render_l(
            "l+",
            [data[f"diacrítico{sindex}"] or data[f"alt{sindex}"] or part],
            defaultdict(
                str,
                {
                    "glosa": data[f"glosa{sindex}"],
                    "glosa-alt": data[f"glosa-alt{sindex}"],
                    "núm": data[f"núm{sindex}"] or data[f"num{sindex}"],
                    "tr": data[f"tr{sindex}"],
                },
            ),
        )

    if not parts:
        return ""

    glue = data.get("e", "y")
    word = data.get("alt", data.get("diacrítico", parts[1] if len(parts) > 1 else parts[-1]))
    phrase = ""

    cat = parts.pop(0)
    if cat in (
        "acortamiento",
        "apócope",
        "síncopa",
        "aféresis",
        "abreviación",
        "supresión",
        "acort",
        "ACORT",
    ):
        phrase = "Acortamiento"
        phrase += f" {data['nota']}" if data["nota"] else ""
        if parts:
            phrase += " de "
            phrase += call_l_single_part(parts[0], 1)
    elif cat in ("calco", "CALC"):
        phrase = (data["por"] or "Por") + " calco"
        phrase += f" {data['nota']}" if data["nota"] else ""
        phrase += " del "
        phrase += normalizar_nombre(parts[0])
        phrase += " "
        phrase += render_l(
            "l+",
            [
                data["diacrítico"] or data["alt"] or (parts[1] if len(parts) > 1 else ""),
            ],
            defaultdict(
                str,
                {
                    "glosa": data["glosa"] or (parts[2] if len(parts) > 2 else ""),
                    "glosa-alt": data["glosa-alt"],
                    "núm": data["núm"] or data["num"],
                    "tr": data["tr"] or data["transcripción"],
                },
            ),
        )
    elif cat in ("compuesto", "compuesta", "COMP"):
        phrase = capitalize(data["otro"] or "compuesto") + " de "
        phrase += concat(
            list(map(call_l_single_part, parts, range(1, len(parts) + 1))),
            ", ",
            last_sep=f" {glue} ",
        )
    elif cat in ("confijo", "circunfijo", "CIRCUNF", "CONF"):
        texto_prefijo = data.get("texto-prefijo", "prefijo")
        phrase = f"Del {texto_prefijo} "
        part = parts.pop(0)
        phrase += render_l("l+", [f"{data['diacrítico'] or data['alt'] or part}-"], data)
        index = 2
        for part in parts[:-1]:
            localphrase = call_l_single_part(part, index)
            phrase += f", {localphrase}"
            index = index + 1
        suffix = "-́" if data.get("tilde", "") in ("sí", "s", "x") else "" if parts[-1].startswith("-") else "-"
        phrase += f" y el sufijo {call_l_single_part(suffix + parts[-1], index)}"
    elif cat == "dimi":
        phrase = f"Diminutivo de {italic(parts[0])}"
    elif cat == "endo":
        phrase = f"De {italic(parts[0])}"
    elif cat in {"epónimo", "EPON"}:
        phrase = "Epónimo:"
        if parts:
            phrase += f" {parts[-1]}"
    elif cat in ("incierta", "incierto", "INC"):
        return "Incierta"
    elif cat in ("femenino", "FEM"):
        data["alt"] = data["diacrítico"] or data["alt"] or parts[0]
        phrase1 = render_l("l+", [parts[0]], data)
        phrase2 = parts[1] if len(parts) > 1 else "-a"
        phrase = f"De {phrase1} y el sufijo flexivo {italic(phrase2)} para el femenino"
    elif cat in ("metátesis", "trasposición", "MET"):
        data["alt"] = data["diacrítico"] or data["alt"] or parts[0]
        phrase1 = render_l("l+", [parts[0]], data)
        phrase = f"Por metátesis de {phrase1}"
    elif cat in (
        "fonética",
        "alteración fonética",
        "adición",
        "epéntesis",
        "prótesis",
        "metaplasmo",
    ):
        nota = f" {data['nota']}" if data["nota"] else ""
        phrase = f"Por alteración fonética{nota} de {call_l_single_part(parts[0], 1)}"
    elif cat == "fone":
        phrase = f"Alteración fonética de {call_l_single_part(parts[0], 1)}"
    elif cat in ("onomatopeya", "onomatopéyico", "onomatopéyica", "ONOM"):
        phrase = "Onomatopéyica"
    elif cat == "marca":
        phrase = f"De la marca registrada {italic(parts[0])}®"
    elif cat == "masculino":
        phrase = f"De {italic(parts[0])} y el sufijo flexivo -o para el masculino"
    elif cat == "plural":
        plural = "-s" if len(parts) == 1 else parts[-1]
        data["alt"] = data["diacrítico"] or data["alt"] or parts[0]
        phrase1 = render_l("l+", [parts[0]], data)
        phrase = f"De {phrase1} y el sufijo flexivo {italic(plural)}"
    elif cat in ("prefijo", "PREF"):
        texto_prefijo = data.get("texto-prefijo", "prefijo")
        phrase = f"Del {texto_prefijo} "
        part = parts.pop(0)
        prefix = data["diacrítico"] or data["alt"] or part
        if not prefix.endswith("-"):
            prefix += "-"
        phrase += render_l("l+", [prefix], data)
        if parts:
            phrase += f" {glue}"
            phrase += f" {call_l_single_part(parts.pop(0), 2)}"
    elif cat == "pronominal":
        data["alt"] = data["diacrítico"] or data["alt"] or parts[0]
        phrase1 = render_l("l+", [parts[0]], data)
        phrase = f"De {phrase1} con el pronombre reflexivo átono"
    elif cat in ("derivación regresiva", "regresiva", "REG"):
        phrase = "Por derivación regresiva de "
        word = data["diacrítico"] or data["alt"] or (parts[0] if parts else "")
        phrase += render_l("l+", [word], data)
    elif cat in ("sufijo", "SUF"):
        texto_sufijo = data.get("texto-sufijo", "sufijo")
        word = data["diacrítico"] or data["alt"] or (parts[0] if parts else "")
        word2 = data["diacrítico2"] or data["alt2"] or (parts[1] if len(parts) > 1 else "")
        phrase1 = render_l("l+", [word], data)
        suffix = "-́" if data.get("tilde", "") in ("sí", "s", "x") else "" if word2.startswith("-") else "-"
        phrase2 = render_l(
            "l+",
            [suffix + word2],
            defaultdict(
                str,
                {
                    "glosa": data["glosa2"],
                    "glosa-alt": data["glosa-alt2"],
                    "núm": data["núm2"] or data["num2"],
                    "tr": data["tr2"] or data["transcripción2"],
                },
            ),
        )
        phrase = f"De {phrase1} y el {texto_sufijo} {phrase2}"
    elif cat == "véase":
        phrase = f"Véase {italic(parts[0])}"
    elif parts:
        phrase = f"Del {normalizar_nombre(cat)} " if cat else ""
        parts.insert(0, cat)
        phrase_array = []
        index = 0
        while parts and (parts[0] or len(parts) != 1):
            sindex = str(index + 1) if index != 0 else ""
            local_phrase = ""
            if index > 0 and parts[0] != cat:
                local_phrase = f"el {normalizar_nombre(parts[0])} "
            local_phrase += render_l(
                "l+",
                [data[f"diacrítico{sindex}"] or data[f"alt{sindex}"] or (parts[1] if len(parts) > 1 else "")],
                defaultdict(
                    str,
                    {
                        "glosa": data[f"glosa{sindex}"] or (parts[2] if (len(parts) > 2 and parts[2] != "-") else ""),
                        "glosa-alt": data[f"glosa-alt{sindex}"],
                        "núm": data[f"núm{sindex}"] or data[f"num{sindex}"],
                        "tr": data[f"tr{sindex}"] or data[f"transcripción{sindex}"],
                    },
                ),
            )
            if local_phrase:
                phrase_array.append(local_phrase)
            for x in range(3):
                if parts:
                    parts.pop(0)
            index = index + 1

        if phrase_array:
            phrase += concat(phrase_array, ", ", last_sep=f" {glue} ")

    return phrase


def render_forma(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_forma("forma", ["-acho", "Forma del femenino de"], defaultdict(str))
    '<i>Forma del femenino de</i> -acho'
    >>> render_forma("forma sustantivo", ["ala", "plural"], defaultdict(str))
    '<i>Forma del plural de</i> ala'
    >>> render_forma("forma sustantivo plural", ["ala"], defaultdict(str))
    '<i>Forma del plural de</i> ala'
    """
    start = "forma de"
    if tpl == "forma sustantivo plural":
        tpl = "forma sustantivo"
        data["numero"] = "plural"
    if tpl == "forma":
        start = data["texto"] or (parts[1] if len(parts) > 1 else "forma de")
    elif tpl == "forma sustantivo":
        caso = data["caso"] or (parts[1] if len(parts) > 1 else "")
        numero = data["número"] or data["numero"] or (parts[2] if len(parts) > 2 else "")
        genero = data["género"] or data["genero"] or (parts[3] if len(parts) > 3 else "")
        start = f"Forma del {concat([caso, numero, genero], ' ')} de"
    phrase = f"{italic(capitalize(start))} {parts[0]}"
    if data["texto_pos"]:
        phrase += f"{data['texto_pos']}"
    return phrase


def render_gentilicio(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_gentilicio("gentilicio", ["Alemania"], defaultdict(str))
    'Originario, relativo a, o propio de Alemania'
    >>> render_gentilicio("gentilicio", ["pueblo guajiro"], defaultdict(str, {"contracción":"1"}))
    'Originario, relativo a, o propio del pueblo guajiro'
    """
    return f"Originario, relativo a, o propio {'del' if data['contracción'] else 'de'} {parts[0]}"


def render_gentilicio2(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_gentilicio2("gentilicio2", ["Alemania"], defaultdict(str))
    'Persona originaria de Alemania'
    >>> render_gentilicio2("gentilicio2", ["pueblo guajiro"], defaultdict(str, {"contracción":"del"}))
    'Persona originaria del pueblo guajiro'
    """
    return f"Persona originaria {data['contracción'] or 'de'} {parts[0]}"


def render_gentilicio3(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_gentilicio3("gentilicio3", ["Alemania"], defaultdict(str))
    'Mujer originaria de Alemania'
    >>> render_gentilicio3("gentilicio3", ["pueblo guajiro"], defaultdict(str, {"contracción":"del"}))
    'Mujer originaria del pueblo guajiro'
    """
    return f"Mujer {data['adjetivo'] or 'originaria'} {data['contracción'] or 'de'} {parts[0]}"


def render_grafia(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_grafia("grafía", ["psicológico"], defaultdict(str))
    '<i>Grafía alternativa de</i> psicológico'
    >>> render_grafia("grafía informal", ["al tiro"], defaultdict(str))
    '<i>Grafía informal de</i> al tiro'
    >>> render_grafia("grafía obsoleta", ["asta"], defaultdict(str))
    '<i>Grafía obsoleta de</i> asta'
    >>> render_grafia("grafía rara", ["exudar"], defaultdict(str))
    '<i>Grafía poco usada de</i> exudar'
    >>> render_grafia("grafía subestándar", ["ah re"], defaultdict(str))
    '<i>Grafía subestándar de</i> ah re'
    >>> render_grafia("grafía", ["psicológico"], defaultdict(str, {"texto": "Grafía rara de", "texto_pos": "(por ejemplo)"}))
    '<i>Grafía rara de</i> psicológico <i>(por ejemplo)</i>'
    """
    if data["texto"]:
        start = data["texto"]
    else:
        start = "Grafía"
        if tpl in {"grafía", "grafia"}:
            start += " alternativa "
        elif tpl == "grafía anticuada":
            start += " anticuada "
        elif tpl == "grafía informal":
            start += " informal "
        elif tpl == "grafía obsoleta":
            start += " obsoleta "
        elif tpl == "grafía rara":
            start += " poco usada "
        elif tpl == "grafía subestándar":
            start += " subestándar "
        start += "de"
    phrase = f"{italic(start)} "
    phrase += render_l("l", [data["alt"] or parts[0]], data)
    if data["texto_pos"]:
        phrase += f" {italic(data['texto_pos'])}"
    return phrase


def render_hipocoristico(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_hipocoristico("hipocorístico", ["Antonio"], defaultdict(str))
    '<i>Hipocorístico de</i> Antonio'
    >>> render_hipocoristico("hipocorístico", ["Antoine", "Antonio"], defaultdict(str))
    '<i>Hipocorístico de</i> Antoine, equivalente del español Antonio'
    """
    phrase = f"{italic('Hipocorístico de')} {parts[0]}"
    if len(parts) > 1:
        phrase += f", equivalente del español {parts[1]}"
    return phrase


def render_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_l("l+", ["la", "impello", "impellō, impellere"], defaultdict(str, {"glosa":"empujar"}))
    "<i>impellō, impellere</i> ('empujar')"
    >>> render_l("l+", ["grc", "ἀράχνη"], defaultdict(str, {"tr":"aráchnē", "glosa":"araña"}))
    "<i>ἀράχνη</i> (<i>aráchnē</i>, 'araña')"
    >>> render_l("l+", ["ar", "حتى"], defaultdict(str, {"tr":"ḥatta"}))
    '<i>حتى</i> (<i>ḥatta</i>)'
    >>> render_l("l+", ["es", "morro"], defaultdict(str, {"num":"2"}))
    '<i>morro<sub>2</sub></i>'
    >>> render_l("l+", ["la", "rogo", "rogō, rogāre", "pedir"], defaultdict(str))
    '<i>rogō, rogāre</i>'
    """
    trans = data["tr"]
    glosa = data["glosa-alt"] or data["glosa"]
    phrase = data["3"] or data["2"] or (parts[2] if len(parts) > 2 else parts[-1])
    if num := data["núm"] or data["num"]:
        phrase += subscript(num)
    if tpl == "l+":
        phrase = italic(phrase)
    if trans or glosa:
        phrase += " ("
        if trans:
            phrase += f"{italic(trans)}"
        if glosa:
            if trans:
                phrase += ", "
            phrase += f"'{glosa}'"
        phrase += ")"

    return phrase


def render_prep_conj(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_prep_conj("preposición conjugada", ["con", "primera", "singular"], defaultdict(str))
    '<i>Forma combinada de la preposición</i> con <i>y el pronombre personal de primera persona singular</i>'
    """
    texto_pos = "y el pronombre personal de "
    texto_pos += data["subtipo"] or (parts[1] if len(parts) > 1 else "")
    texto_pos += " persona "
    texto_pos += data["número"] or data["numero"] or (parts[2] if len(parts) > 2 else "")
    return render_forma(
        "forma",
        [parts[0], "forma combinada de la preposición"],
        defaultdict(str, {"texto_pos": f" {italic(texto_pos)}"}),
    )


def render_superlativo(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_superlativo("superlativo", ["abundante"], defaultdict(str))
    '<i>Superlativo de</i> abundante:&nbsp;sumamente abundante'
    >>> render_superlativo("superlativo", ["pobre"], defaultdict(str, {"i":"s"}))
    '<i>Superlativo irregular de</i> pobre:&nbsp;sumamente pobre'
    >>> render_superlativo("superlativo", ["pobre"], defaultdict(str, {"i":"s", "alt":"alt"}))
    '<i>Superlativo irregular de</i> alt:&nbsp;sumamente pobre'
    >>> render_superlativo("superlativo", ["pobre"], defaultdict(str, {"def":"x"}))
    '<i>Superlativo de</i> pobre'
    >>> render_superlativo("superlativo", ["pobre"], defaultdict(str, {"tr":"tr", "glosa":"glosa"}))
    '<i>Superlativo de</i> pobre (<i>tr</i>, "glosa"):&nbsp;sumamente pobre'
    >>> render_superlativo("superlativo", ["ásperamente", "es", "x"], defaultdict(str, {"adv":"x"}))
    '<i>Superlativo de</i> ásperamente'
    """
    word = parts.pop(0) if parts else ""
    start = "Superlativo"
    if data["i"] or data["irr"] or data["irreg"] or data["irregular"]:
        start += " irregular"
    start += " de"
    phrase = italic(start)
    phrase += f" {data['alt']}" if data["alt"] else f" {word}"
    local_phrase = []
    if data["tr"]:
        local_phrase.append(italic(data["tr"]))
    if data["glosa"]:
        local_phrase.append(f'"{data["glosa"]}"')
    if local_phrase:
        phrase += f" ({concat(local_phrase, ', ')})"
    if not data["def"] and not parts:
        phrase += f":&nbsp;sumamente {word}"
    return phrase


def render_sustantivo_de(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_sustantivo_de("sustantivo de verbo", ["circular"], defaultdict(str))
    'Acción o efecto de circular'
    >>> render_sustantivo_de("sustantivo de verbo", ["sublevar", "sublevarse"], defaultdict(str))
    'Acción o efecto de sublevar o de sublevarse'
    >>> render_sustantivo_de("sustantivo de adjetivo", ["urgente"], defaultdict(str))
    'Condición o carácter de urgente'
    >>> render_sustantivo_de("sustantivo de adjetivo", ["abad", "abadesa"], defaultdict(str))
    'Condición o carácter de abad o abadesa'
    """
    # sustantivo de adjetivo
    start = "Condición o carácter de"
    connector = " o "
    if tpl == "sustantivo de verbo":
        start = "Acción o efecto de"
        connector = " o de "
    phrase = f"{start} "
    phrase += render_l("l", [parts[0]], data)
    if len(parts) > 1:
        phrase += connector
        phrase += render_l(
            "l",
            [parts[1]],
            defaultdict(
                str,
                {
                    "glosa": data["glosa2"],
                    "glosa-alt": data["glosa-alt2"],
                    "núm": data["núm2"] or data["num2"],
                },
            ),
        )
    return phrase


def render_variante(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variante("variante", ["atiesar"], defaultdict(str))
    '<i>Variante de</i> atiesar'
    >>> render_variante("variante", ["diezmo"], defaultdict(str, {"texto":"variante anticuada de"}))
    '<i>variante anticuada de</i> diezmo'
    """
    return f"{italic(data['texto'] or 'Variante de')} " + render_l("l", [parts[0]], data)


def render_variantes(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variantes("variantes", ["acrótera", "acroteria"], defaultdict(str))
    '<b>Variantes:</b> acrótera, acroteria'
    >>> render_variantes("variantes", ["moerus"], defaultdict(str, {"nota1":"arcaica", "alt1": "moerǔs"}))
    '<b>Variante:</b> moerǔs (arcaica)'
    >>> render_variantes("variantes", ["adestrador"], defaultdict(str, {"nota":"poco frecuente"}))
    '<b>Variante:</b> adestrador (poco frecuente)'
    """
    starter = "Variante" + ("s:" if len(parts) > 1 else ":")
    a_phrase: list[str] = []
    for i in range(10):
        if i == 0:
            phrase = data["alt"] or data[f"alt{i + 1}"] or (parts[i] if len(parts) > i else "")
        else:
            phrase = data[f"alt{i + 1}"] or (parts[i] if len(parts) > i else "")
        if i == 0 and data["nota"]:
            phrase += f" ({data['nota']})"
        elif data[f"nota{i + 1}"]:
            phrase += f" ({data[f'nota{i + 1}']})"
        if phrase:
            a_phrase.append(phrase)

    return f"{strong(starter)} {concat(a_phrase, ', ')}"


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_variant("forma participio", ["apropiado", "femenino"], defaultdict(str))
    'apropiado'
    >>> render_variant("forma participio", ["gastado", "femenino"], defaultdict(str, {"v": "gastar"}))
    'gastar'
    """
    return data["v"] or parts[0]


template_mapping = {
    "adjetivo de verbo": render_adjetivo_de_verbo,
    "AFI": render_afi,
    "antónimo": render_nimo,
    "antónimos": render_nimo,
    "aumentativo": render_aumentativo,
    "adverbio de adjetivo": render_adverbio_de_adjetivo,
    "adverbio de sustantivo": render_adverbio_de_sustantivo,
    "comparativo": render_comparativo,
    "contracción": render_contraccion,
    "diminutivo": render_aumentativo,
    "DLE": render_dle,
    "etim": render_etim,
    "etimología": render_etimologia,
    "forma": render_forma,
    "gentilicio": render_gentilicio,
    "gentilicio1": render_gentilicio,
    "gentilicio2": render_gentilicio2,
    "gentilicio3": render_gentilicio3,
    "grafia": render_grafia,
    "grafía": render_grafia,
    "grafía anticuada": render_grafia,
    "grafía informal": render_grafia,
    "grafía obsoleta": render_grafia,
    "grafía rara": render_grafia,
    "grafía subestándar": render_grafia,
    "hipocorístico": render_hipocoristico,
    "IPA": render_afi,
    "l": render_l,
    "l+": render_l,
    "preposición conjugada": render_prep_conj,
    "sinónimo": render_nimo,
    "sinónimos": render_nimo,
    "superlativo": render_superlativo,
    "sustantivo de adjetivo": render_sustantivo_de,
    "sustantivo de verbo": render_sustantivo_de,
    "variante": render_variante,
    "variantes": render_variantes,
    #
    # Variants
    #
    "__variant__enclítico": render_variant,
    "__variant__f.adj2": render_variant,
    "__variant__f.s.p": render_variant,
    "__variant__forma adjetiva": render_variant,
    "__variant__forma adjetivo": render_variant,
    "__variant__forma adjetivo 2": render_variant,
    "__variant__forma diminutivo": render_variant,
    "__variant__forma participio": render_variant,
    "__variant__forma pronombre": render_variant,
    "__variant__forma sustantivo": render_variant,
    "__variant__forma sustantivo plural": render_variant,
    "__variant__forma verbo": render_variant,
    "__variant__f.v": render_variant,
    "__variant__gerundio": render_variant,
    "__variant__infinitivo": render_variant,
    "__variant__participio": render_variant,
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
