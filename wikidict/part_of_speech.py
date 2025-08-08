"""
Modifiers used to uniformize, and clean-up, POS (Part Of Speech).
"""

import re

# Clean-up POS using regexp(s), they are executed in order
PATTERNS = {
    "da": [
        # `{{verbum}}` → `verbum`
        re.compile(r"\{\{([^|}]+).*").sub,
        # `verbum 1` → `verbum`
        re.compile(r"(.+)\s+\d+.*").sub,
    ],
    "de": [
        # `{{bedeutungen}}` → `bedeutungen`
        re.compile(r"\{\{([^|}]+).*").sub,
    ],
    "el": [
        # `{{έκφραση|el}}` → `έκφραση`
        re.compile(r"\{\{([^|}]+).*").sub,
    ],
    "en": [
        # `proper noun 1` → `proper noun`
        re.compile(r"(proper noun).+").sub,
    ],
    "eo": [
        # `{{vortospeco|adverbo, vortgrupo|eo}}` → `adverbo, vortgrupo`
        re.compile(r"\{\{vortospeco\|([^|]+).*").sub,
        # `{{signifoj}}` → `signifoj`
        re.compile(r"\{\{([^}]+).*").sub,
    ],
    "es": {
        # `{{verbo transitivo|es|terciopersonal}}` → `verbo transitivo`
        re.compile(r"\{\{([^|}]+).*").sub,
        # `verbo transitivo` → `verbo`
        re.compile(r"([^\s]+)\s+.*").sub,
    },
    "fr": [
        # `{{s|verbe|fr}}` → `verbe`
        re.compile(r"\{\{s\|([^|}]+).*").sub,
        # `adjectif démonstratif` → `adjectif`
        re.compile(r"(adjectif|adverbe|article|déterminant|pronom)\s+.*").sub,
    ],
    "it": [
        # `{{nome}}` → `nome`
        re.compile(r"\{\{([^}]+).*").sub,
    ],
    "no": [
        # `verb 1` → `verb`
        re.compile(r"([^\s,]+),?\s+.*").sub,
    ],
    "pt": [
        # `{{forma de locução substantiva 1|pt}}` → `forma de locução substantiva 1`
        re.compile(r"\{\{([^|}]+).*").sub,
        # `forma de locução substantiva 1` → `locução substantiva 1`
        re.compile(r"forma de (.+)").sub,
        # `substantivo³` → `substantivo`
        # `substantivo2` → `substantivo`
        # `substantivo 2` → `substantivo`
        # `substantivo <small>''Feminino''</small>` → `substantivo`
        re.compile(r"([^\d¹²³<,]+),?\s*.*").sub,
        # `pronome pessoal` → `pronome`
        re.compile(r"(adjetivo|caractere|expressão|expressões|frase|locução|numeral|pronome|verbo)\s+.*").sub,
    ],
    "ro": [
        # `{{nume taxonomic|conv}}` → `nume taxonomic`
        re.compile(r"\{\{([^|}]+).*").sub,
        # `verb auxiliar` → `verb`
        re.compile(r"(locuțiune|numeral|verb)\s+.*").sub,
    ],
    "zh": [
        # `發音1` → `發音`
        # `發音 1` → `發音`
        # `發音①` → `發音`
        re.compile(r"([^\s\d①②③]+).*").sub,
    ],
}

# Uniformize POS
# Note: "top" must be defined for every locale: it is the default value when definitions are not under a subsection right below the top section;
#       and by default we move those definitions to the "noun" POS.
MERGE = {
    "ca": {
        "top": "nom",
    },
    "da": {
        "abbr": "forkortelsf",
        "abr": "forkortelsf",
        "ad": "adjektiv",
        "adj": "adjektiv",
        "adjektive": "adjektiv",
        "adv": "adverbium",
        "art": "artikel",
        "car-num": "mængdetal",
        "conj": "konjunktion",
        "dem-pronom": "pronomen",
        "end": "endelse",
        "expr": "udtryk",
        "fast udtryk": "udtryk",
        "frase": "sætning",
        "interj": "interjektion",
        "lyd": "lydord",
        "noun": "substantiv",
        "num": "talord",
        "part": "mærke",
        "pers-pronom": "pronomen",
        "phr": "sætning",
        "possessivt pronomen": "pronomen",
        "possessivt pronomen (ejestedord)": "pronomen",
        "pp": "pronomen",
        "pref": "prefix",
        "prep": "præposition",
        "pron": "pronomen",
        "prop": "proprium",
        "prov": "ordsprog",
        "seq-num": "ordenstal",
        "substantivisk ordforbindelse": "substantiv",
        "symb": "symbol",
        "top": "substantiv",
        "ubest-pronon": "pronomen",
        "verb": "verbum",
    },
    "el": {
        "μορφή επιθέτου": "επιθέτου",
        "μορφή ουσιαστικού": "ουσιαστικό",
        "μορφή ρήματος": "ρήμα",
        "top": "ουσιαστικό",
    },
    "en": {
        "adverbial phrase": "adverb",
        "prepositional phrase": "preposition",
        "top": "noun",
        "verb form": "verb",
        "verb phrase": "verb",
    },
    "eo": {
        "adverbo, vortgrupo": "adverbo",
        "difinoj": "difino",
        "liternomo": "litero",
        "literoparo": "litero",
        "mallongigoj": "mallongigo",
        "signifoj": "signifo",
        "substantiva formo": "substantivo",
        "substantivo, vortgrupo": "substantivo",
        "top": "substantivo",
        "verba formo": "verbo",
        "verbo, vortgrupo": "verbo",
    },
    "fr": {
        "abréviations": "abréviation",
        "adj": "adjectif",
        "conjonction de coordination": "conjonction",
        "locution-phrase": "phrase",
        "locution phrase": "phrase",
        "nom commun": "nom",
        "nom de famille": "nom",
        "top": "nom",
    },
    "it": {
        "acron": "abbreviazione",
        "agg form": "aggettivo",
        "agg": "aggettivo",
        "art": "articolo",
        "avv": "avverbio",
        "cong": "congiunzione",
        "inter": "interiezione",
        "loc nom": "nome",
        "pref": "prefisso",
        "prep": "preposizione",
        "pron poss": "pronome possessivo",
        "sost form": "sostantivo",
        "sost": "sostantivo",
        "suff": "suffisso",
        "top": "sostantivo",
        "verb form": "verb",
    },
    "no": {
        "forkortelser": "forkortelse",
        "top": "substantiv",
    },
    "pt": {
        "abreviação": "abreviatura",
        "acrônimo": "acrónimo",
        "adjetivo/substantivo": "adjetivo",
        "expressões": "expressão",
        "forma verbal": "verbo",
        "locução substantiva": "substantivo",
        "pepb": "acrónimo",
        "siglas": "sigla",
        "substantivo comum": "substantivo",
        "top": "substantivo",
        "verbal": "verbo",
    },
    "ro": {
        "abr": "abreviere",
        "expr": "expresie",
        "top": "substantiv",
    },
    "sv": {
        "förkortningar": "förkortning",
        "prepositionsfras": "preposition",
        "top": "substantiv",
        "verbpartikel": "verb",
    },
    "zh": {
        "词源": "名詞",  # etymology → noun
        "詞源": "名詞",  # etymology → noun
        "名词": "名詞",  # noun
        "名詞詞": "名詞",  # noun words → noun
        "發音": "讀音",  # pronunciation
        "动词": "動詞",  # verb
    },
}
