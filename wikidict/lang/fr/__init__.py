"""French language."""

import re
from itertools import product

from ... import utils
from .template_adapters import adapters as template_adapters  # noqa: F401
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "http://tools.wmflabs.org/anagrimes/hasard.php?langue=fr"

template_trans = "Modèle"

float_separator = ","
thousands_separator = " "

# https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_des_sections_de_types_de_mots
section_patterns = ("#", r"\*")
head_sections = ("{{langue|fr}}", "{{langue|conv}}", "{{caractère}}")
etyl_section = ("{{s|étymologie}}",)
core_sections = [
    "abréviations",
    "adjectif démonstratif",
    "adjectif exclamatif",
    "adjectif indéfini",
    "adjectif interrogatif",
    "adjectif numéral",
    "adjectif possessif",
    "adjectif relatif",
    "adjectif",
    "adj",
    "adverbe interrogatif",
    "adverbe relatif",
    "adverbe",
    "article",
    "article défini",
    "article indéfini",
    "article partitif",
    "conjonction de coordination",
    "conjonction",
    "déterminant démonstratif",
    "erreur",
    "infixe",
    "interfixe",
    "interjection",
    "lettre",
    "locution-phrase",
    "locution phrase",
    "nom commun",
    "nom de famille",
    "nom propre",
    "nom scientifique",
    "nom",
    "numéral",
    "onomatopée",
    "particule",
    "phrase",
    "postposition",
    "pronom démonstratif",
    "pronom indéfini",
    "pronom interrogatif",
    "pronom personnel",
    "pronom possessif",
    "pronom relatif",
    "pronom",
    "proverbe",
    "préfixe",
    "prénom",
    "préposition",
    "substantif",
    "suffixe",
    "symbole",
    "variante typographique",
    "vocabulaire",
    "verbe",
]
sections = (
    *etyl_section,
    *[f"{{{{s|{section}|conv" for section in core_sections],
    *[f"{{{{s|{section}|fr|" for section in core_sections],
    *[f"{{{{s|{section}|fr}}" for section in core_sections],
    *[f"{{{{s|{section}|num" for section in core_sections],
    "{{s|caractère}",
)

variant_titles = (
    *[f"{{{{s|{section}|fr}}" for section in core_sections],
    *[f"{{{{s|{section}|fr|flexion" for section in core_sections],
    *[f"{{{{s|{section}|fr|num={idx}|flexion" for section, idx in product(["adjectif", "nom"], range(1, 4))],
)
variant_templates = (
    "{{fr-accord-",
    "{{fr-rég",
    "{{fr-verbe-flexion",
    "{{flexion",
)

definitions_to_ignore = (
    "{doute",
    "{ébauche",
    "{exemple|",
)

# https://fr.wiktionary.org/wiki/Wiktionnaire:Liste_de_tous_les_mod%C3%A8les/Bandeaux
templates_ignored = (
    "{{?",
    "{{créer-séparément",
    "{{ébauche",
    "{{écouter",
    "{{étymologie-chinoise-SVG",
    "{{lire en ligne",
    "{{préciser",
    "{{R:",
    "{{RÉF",
    "{{réf",
    "{{source",
    "{{Source-wikt",
    "{{trier",
    "{{vérifier",
    "{{voir",
    "{{Wikisource",
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "fr")
    []
    >>> find_genders("'''-eresse''' {{pron|(ə).ʁɛs|fr}} {{f}}", "fr")
    ['f']
    >>> find_genders("'''42''' {{msing}}", "fr")
    ['msing']
    """
    pattern = re.compile(rf"\{{([fmsingp]+)(?: \?\|{locale})*}}")
    return utils.unique(utils.flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "fr")
    []
    >>> find_pronunciations("{{pron|ɑ|fr}}", "fr")
    ['\\\\ɑ\\\\']
    >>> find_pronunciations("{{pron|ɑ|fr}}, {{pron|a|fr}}", "fr")
    ['\\\\ɑ\\\\', '\\\\a\\\\']
    """
    pattern = re.compile(rf"\{{pron(?:\|lang={locale})?\|([^}}\|]+)")
    if not (match := pattern.search(code)):
        return []

    # There is at least one match, we need to get whole line
    # in order to be able to find multiple pronunciations
    line = code[match.start() : code.find("\n", match.start())]
    return [f"\\{p}\\" for p in utils.unique(pattern.findall(line))]


ALL_FORMS = [
    "féminin de",
    "féminin singulier",
    "masculin singulier",
    "masculin et féminin pluriel",
    "masculin ou féminin pluriel",
    "participe présent",
    "pluriel d",
    "pluriel habituel",
    "pluriel inhabituel",
]
FORMS = "|".join(ALL_FORMS)
START = rf"^(?:{'|'.join(section_patterns)})\s*'*"
PATTERNS = [
    # ''Agglutination du participe présent au féminin singulier du verbe'' {{lien|interpolare|it}} ''avec le pronom'' {{lien|mi|it|sens=me}}
    r".+(?:(?:masculin|féminin) \(?(?:pluriel|singulier)\)?) du verbe''\s*\{\{lien\|([^\|}]+)",
    # ''Féminin singulier de'' {{lien|terne|fr}}.
    # ''Féminin (singulier) de'' {{lien|terne|fr}}.
    r".+(?:(?:masculin|féminin) \(?(?:pluriel|singulier)\)?).*'\s*\{\{lien\|([^\|}]+)",
    # ''Participe passé masculin singulier du verbe'' [[pouvoir]].
    # ''Participe passé masculin (singulier) du verbe'' [[pouvoir]].
    r".+(?:(?:masculin|féminin) \(?(?:pluriel|singulier)\)?).*'\s*\[\[([^\]#]+)(?:#.+)?]]",
    # ''Pluriel de ''[[anisophylle]]''.''
    rf"(?:{FORMS}).*'\s*\[\[([^\]#]+)(?:#.+)?]]",
    # ''Pluriel de'' {{lien|anisophylle|fr}}.
    rf"(?:{FORMS}).*'\s*\{{\{{lien\|([^\|\}}]+)",
    # ''Pluriel'' ''de ''[[nécrophage]].
    r"(?:féminin|masculin|pluriel)'+\s+'+de.*'\s*\[\[([^\]#]+)(?:#.+)?]]",
    # ''Troisième personne du pluriel de l’indicatif imparfait du verbe'' [[venir]].
    # ''Forme de la deuxième personne du singulier de l’impératif [[mange]], de'' [[manger]], employée devant [[en]] et [[y]].
    r"(?:(?:Forme de la )?(?:première|deuxième|troisième) personne du (?:pluriel|singulier)).*'\s*\[\[([^\]#]+)(?:#.+)?]]",
    # ''Troisième personne du singulier du subjonctif présent du verbe'' {{lien|venir|fr}}.
    r"(?:(?:Forme de la )?(?:première|deuxième|troisième) personne du (?:pluriel|singulier)).*'\s*\{\{lien\|([^\|}]+)",
]


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode('== {{langue|fr}} =\n<li value="2"> Qui a rapport avec un type de [[discours]].', "fr")
    '== {{langue|fr}} =\n Qui a rapport avec un type de [[discours]].'

    >>> adjust_wikicode("== {{langue|fr}} =\n{{sinogram-noimg|它|\\nclefhz1=宀|clefhz2=2|\\nnbthz1=1-5|nbthz2=5|\\nm4chz1=3|m4chz2=3071<sub>1</sub>|\\nunihz=5B83|\\ngbhz1= |gbhz2=-|\\nb5hz1=A1|b5hz2=A5A6|\\ncjhz1=J|cjhz2=十心|cjhz3=JP}}", "fr")
    '== {{langue|fr}} =\n# {{sinogram-noimg|它|\\nclefhz1=宀|clefhz2=2|\\nnbthz1=1-5|nbthz2=5|\\nm4chz1=3|m4chz2=3071<sub>1</sub>|\\nunihz=5B83|\\ngbhz1= |gbhz2=-|\\nb5hz1=A1|b5hz2=A5A6|\\ncjhz1=J|cjhz2=十心|cjhz3=JP}}'

    >>> adjust_wikicode("== {{caractère}} ==", "fr")
    '== {{caractère}} ==\n=== {{s|caractère}} ==='

    >>> adjust_wikicode("== {{langue|fr}} =\n=== {{s|caractère}} ===\n{{hangeul unicode}}", "fr")
    '== {{langue|fr}} =\n=== {{s|caractère}} ===\n# {{hangeul unicode}}'

    >>> adjust_wikicode("== {{langue|fr}} =\n* ''Féminin (singulier) de'' {{lien|terne|fr}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|terne}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Féminin singulier de'' {{lien|terne|fr}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|terne}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n#''Féminin singulier de l’[[adjectif]]'' [[pressant]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|pressant}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n#''Féminin (singulier) de '' [[chacun]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|chacun}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Pluriel de ''[[anisophylle]]''.''", "fr")
    '== {{langue|fr}} =\n# {{flexion|anisophylle}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Pluriel de'' [[antiproton#fr|antiproton]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|antiproton}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Pluriel de'' {{lien|anisophylle|fr}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|anisophylle}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Pluriel'' ''de ''[[nécrophage]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|nécrophage}}'

    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Troisième personne du pluriel de l’indicatif imparfait du verbe'' [[venir#fr|venir]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|venir}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Troisième personne du pluriel de l’indicatif imparfait du verbe'' [[venir]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|venir}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Participe passé masculin singulier du verbe'' [[pouvoir]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|pouvoir}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Participe passé masculin singulier du verbe'' [[pouvoir#fr|pouvoir]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|pouvoir}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Forme de la deuxième personne du singulier de l’impératif [[mange]], de'' [[manger]], employée devant [[en]] et [[y]].", "fr")
    '== {{langue|fr}} =\n# {{flexion|manger}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Troisième personne du singulier du subjonctif présent du verbe'' {{lien|manger|fr}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|manger}}'
    >>> adjust_wikicode("== {{langue|fr}} =\n#''Ancienne forme de la troisième personne du pluriel de l’indicatif imparfait du verbe'' [[venir]] (on écrit maintenant ''[[venaient]]'').", "fr")
    "== {{langue|fr}} =\n#''Ancienne forme de la troisième personne du pluriel de l’indicatif imparfait du verbe'' [[venir]] (on écrit maintenant ''[[venaient]]'')."

    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Pluriel de'' {{lien|anisophylle|fr}}.\n*''Pluriel de'' {{lien|anisophylle|fr}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|anisophylle}}\n# {{flexion|anisophylle}}'

    >>> adjust_wikicode("== {{langue|fr}} =\n# ''Agglutination du participe présent au féminin singulier du verbe'' {{lien|interpolare|it}} ''avec le pronom'' {{lien|mi|it|sens=me}}.", "fr")
    '== {{langue|fr}} =\n# {{flexion|interpolare}}'
    """

    # Keep interesting sections only
    if not (code := utils.extract_relevant_sections(code, locale)):
        return ""

    # == {{caractère}} == → '== {{caractère}} ==\n=== {{s|caractère}} ==='
    code = re.sub(r"(==\s*{{caractère}}\s*==)", r"\1\n=== {{s|caractère}} ===", code)

    # === {{s|caractère}} ===\n{{hangeul unicode}} → '=== {{s|caractère}} ===\n# {{hangeul unicode}}'
    code = re.sub(r"=== \{\{s\|caractère}} ===\n\s*\{\{", "=== {{s|caractère}} ===\n# {{", code, flags=re.MULTILINE)

    # <li value="2"> → ''
    code = re.sub(r"<li [^>]+>", "", code)

    # {{sinogram-noimg|... → '# {{sinogram-noimg|...'
    code = re.sub(r"^\{\{sinogram-noimg", "# {{sinogram-noimg", code, flags=re.MULTILINE)

    #
    # Variants
    #

    lines: list[str] = []
    for line in code.splitlines():
        if re.match(START, line):
            for pattern in PATTERNS:
                line, count = re.subn(rf"{START}{pattern}.*", r"# {{flexion|\1}}", line, count=1, flags=re.IGNORECASE)  # noqa: PLW2901
                if count:
                    break
        lines.append(line)

    return "\n".join(lines)
