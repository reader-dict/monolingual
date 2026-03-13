import re

adapters = {
    "Modèle:date": lambda _: "{{#ifeq:{{{1|}}}|?||{{#if:{{{1|}}}|<i>({{UCFIRST: {{{1}}} }})</i>|}}}}",
    **dict.fromkeys(
        {
            "Modèle:emploi",
            "Modèle:lexique",
            "Modèle:term",
        },
        lambda body: re.sub(r"\[\[Catégorie:[^\]]+\]\]", "", body),
    ),
    "Modèle:nom w pc": lambda body: body.removesuffix(
        """<sup style="color: red">Le modèle ''nom w pc'' est désuet. Supprimez-le de cette ligne, ou remplacez-le par le modèle w si un lien vers Wikipédia est nécessaire.</sup>"""
    ),
    "Modèle:radical de Kangxi": lambda _: (
        "Radical de Kangxi {{numéro|{{#expr: {{point de code|{{PAGENAME}}|format=%d}} - 12032 + 1}}}} [[{{str left|{{radical trait|{{PAGENAME}}}}|1}}]]. Unicode : U+{{point de code|{{PAGENAME}}}}."
    ),
    "Modèle:référence nécessaire": lambda _: "{{#if:{{{1|}}}|{{#ifeq:{{{1|}}}|nocat||{{{1}}}}}}}",
    "Modèle:siècle": lambda _: (
        """{{#ifeq:{{{1|}}}|?||{{#if:{{{1|}}}|<span class="siècle">''({{#invoke:date et heure|formate_un_siecle|{{{1|}}}|lang={{{lang|{{{langue|}}}}}}}}{{#if:{{{2|}}}|&#32;–&#32;{{#invoke:date et heure|formate_un_siecle|{{{2}}}}}}})''</span>|}}}}"""
    ),
    "Modèle:variante du radical de Kangxi": lambda _: (
        "Variante {{{1|}}} du radical de Kangxi [[{{str left|{{radical trait|{{PAGENAME}}}}|1}}]]. Unicode : U+{{point de code|{{PAGENAME}}}}."
    ),
}
