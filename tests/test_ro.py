from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants",
    [
        (
            "aventurierul",
            ["/a.ven.tu.riˈe.rul/"],
            [],
            {},
            ["aventurier"],
        ),
        (
            "cânta",
            ["/kɨnˈta/"],
            ["Din latină <i>cantare</i>."],
            {
                "Expresie": ["<i><b>Joacă cum îi cântă</b> = face întocmai cum îi poruncește altul</i>"],
                "Verb": [
                    "(<i>v.intranz. și tranz.</i>) a emite cu vocea sau cu un instrument un șir de sunete muzicale care se rânduiesc într-o melodie, într-un acord etc.",
                    "(<i>despre păsări, insecte etc.</i>) a scoate sunete plăcute la auz. caracteristice speciei.",
                    "(<i>v.intranz. și tranz.</i>) a scrie versuri în cinstea cuiva sau a ceva, a elogia (în versuri) pe cineva sau ceva; a descrie, a povesti ceva în versuri.",
                    "(<i>v.tranz.</i>) (<i>fam.</i>) a îndruga, a înșira vorbe goale.",
                ],
            },
            [],
        ),
        (
            "fi",
            ["/fi/"],
            ["Din latină <i>sum, esse, fui, fire</i>."],
            {
                "Verb": [
                    "a exista, a avea ființă.",
                    "a se afla, a se găsi într-un anumit loc, la o anumită persoană.",
                    "a-și avea originea, obârșia, a se trage, a proveni.",
                    "a trăi, a viețui, a o duce; (<i>despre lucruri, situații, acțiuni etc.</i>) a dura, a dăinui, a ține.",
                    "a se îndeplini, a se întâmpla, a se petrece, a avea loc.",
                    "a avea prețul...; a costa, a valora.",
                    "(<i>în superstiții, ghicitori etc.</i>) a însemna, a prevesti, a fi semn că...",
                    "(<i>formează, împreună cu numele predicativ, predicatul</i>)",
                    "(<i>construit cu dativul; împreună cu un nume predicativ, exprimă o stare sau o acțiune arătate de numele predicativ respectiv</i>)",
                    "(<i>în construcții impersonale, cu subiectul logic în dativ; în legătură cu noțiuni exprimând un sentiment, o senzație, o stare sufletească</i>) a simți",
                    "(<i>impers.; urmat de un verb la infinitiv sau la conjunctiv sau urmat ori precedat de o noțiune temporală</i>) a urma (să se facă), a trebui (să se facă).",
                    "(<i>de obicei impers.; la imperfect și urmat de un verb la conjunctiv</i>) a avea putința, posibilitatea, ocazia să...; a se afla pe punctul de a..., a nu mai lipsi mult până să...",
                    "(<i>impers.; urmat de un suspin</i>) a putea, a trebui, a considera că este cazul să..., a se cuveni.",
                    "(<i>construit cu un participiu, servește la formarea diatezei pasive</i>)",
                    "(<i>construit cu un participiu invariabil, formează timpuri compuse ale diatezei active</i>)",
                    (
                        "(<i>cu viitorul I formează viitorul anterior</i>)",
                        "(<i>cu condiționalul prezent formează perfectul optativ-condițional</i>)",
                        "(<i>cu conjunctivul prezent formează perfectul conjunctivului</i>)",
                        "(<i>cu infinitivul formează perfectul infinitivului</i>)",
                        "(<i>cu viitorul I sau cu perfectul conjunctivului formează prezumtivul prezent și perfect</i>)",
                    ),
                    "(<i>construit cu un participiu invariabil sau cu un gerunziu, servește la alcătuirea unor forme perifrastice de perfect compus, mai mult ca perfect sau imperfect</i>)",
                ]
            },
            [],
        ),
        ("frumoasă", ["/fru'mo̯a.sə/"], [], {}, ["frumos"]),
        ("frumoși", ["[fruˈmoʃʲ]"], [], {}, ["frumos"]),
        (
            "paronim",
            ["/pa.ro'nim/"],
            [
                "Din franceză <i>paronyme</i>, latină <i>paronymon</i>, originar format din greacă παρα + <b>ονομα</b> -onym"
            ],
            {
                "Substantiv": [
                    "cuvânt asemănător cu altul din punctul de vedere al formei, dar deosebit de acesta ca sens (și ca origine).",
                    "cuvânt care se aseamănă parțial cu altul din punctul de vedere al formei, dar se deosebește ca sens de acesta.",
                ]
            },
            [],
        ),
        (
            "Lama",
            [],
            [],
            {
                "Nume Taxonomic": [
                    "(<i>zool.</i>) gen de animale din familia <i>Camelidae</i>; (<i>spec.</i>) lamă, guanaco"
                ]
            },
            [],
        ),
        (
            "MHz",
            [],
            [],
            {"Simbol": ["simbol pentru megahertz"]},
            [],
        ),
        ("portocale", ["/por.toˈka.le/"], [], {}, ["portocală"]),
        (
            "temperatură",
            ["/tem.pe.raˈtu.rə/"],
            ["Din franceză <i>température</i> &lt; latină <i>temperatura</i>."],
            {
                "Substantiv": [
                    "gradul, starea de căldură a unui mediu, a unui corp etc.",
                    "stare fiziologică constantă a corpului animal, reprezentând echilibrul dintre căldura produsă și cea pierdută.",
                    "gradul de căldură ridicată a corpului omenesc, reprezentând un simptom patologic; fierbințeală, febră.",
                ],
                "Unități": [
                    "Metric (Sistemul Internațional): grad Celsius/centigrade (°C), kelvin (K).",
                    "Imperial: grade Fahrenheit (°F), grade Rankine (°R).",
                ],
            },
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "ro")
    details = parse_word(word, code, "ro", force=True)
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{n}}", "<i>n.</i>"),
        ("{{p}}", "<i>pl.</i>"),
        ("{{trad|el|παρα}}", "παρα"),
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "ro") == expected
