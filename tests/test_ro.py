from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("ro")


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "aventurierul",
            ["/a.ven.tu.riˈe.rul/"],
            [],
            {},
            ["aventurier"],
            [],
        ),
        (
            "cânta",
            ["/kɨnˈta/"],
            ["Din latină <i>cantare</i>."],
            {
                "Verb": [
                    "(<i>v.intranz. și tranz.</i>) a emite cu vocea sau cu un instrument un șir de sunete muzicale care se rânduiesc într-o melodie, într-un acord etc.",
                    ("<i>A <b>cânta</b> o melodie, o doină.</i>", "<i><b>Cântă</b> din fluier.</i>"),
                    "(<i>despre păsări, insecte etc.</i>) a scoate sunete plăcute la auz. caracteristice speciei.",
                    "(<i>v.intranz. și tranz.</i>) a scrie versuri în cinstea cuiva sau a ceva, a elogia (în versuri) pe cineva sau ceva; a descrie, a povesti ceva în versuri.",
                    "(<i>v.tranz.</i>) (<i>fam.</i>) a îndruga, a înșira vorbe goale.",
                ],
                "Expresie": ["<i><b>Joacă cum îi cântă</b> = face întocmai cum îi poruncește altul</i>"],
            },
            [],
            ["cânt", "cântat", "cânte"],
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
                    ("<i>Cartea <b>este</b> roșie.</i>",),
                    "(<i>construit cu dativul; împreună cu un nume predicativ, exprimă o stare sau o acțiune arătate de numele predicativ respectiv</i>)",
                    ("<i>Mi-<b>e</b> amic.</i>",),
                    "(<i>în construcții impersonale, cu subiectul logic în dativ; în legătură cu noțiuni exprimând un sentiment, o senzație, o stare sufletească</i>) a simți",
                    ("<i>Mi-<b>e</b> foame.</i>",),
                    "(<i>impers.; urmat de un verb la infinitiv sau la conjunctiv sau urmat ori precedat de o noțiune temporală</i>) a urma (să se facă), a trebui (să se facă).",
                    ("<i>Când i-a <b>fost</b> să moară</i>.",),
                    "(<i>de obicei impers.; la imperfect și urmat de un verb la conjunctiv</i>) a avea putința, posibilitatea, ocazia să...; a se afla pe punctul de a..., a nu mai lipsi mult până să...",
                    ("<i><b>Era</b> să cadă.</i>",),
                    "(<i>impers.; urmat de un suspin</i>) a putea, a trebui, a considera că este cazul să..., a se cuveni.",
                    ("<i><b>E</b> de mers acasă.</i>",),
                    "(<i>construit cu un participiu, servește la formarea diatezei pasive</i>)",
                    ("<i>El a <b>fost</b> chemat.</i>",),
                    "(<i>construit cu un participiu invariabil, formează timpuri compuse ale diatezei active</i>)",
                    (
                        "(<i>cu viitorul I formează viitorul anterior</i>)",
                        ("<i>Eu voi <b>fi</b> plecat.</i>",),
                        "(<i>cu condiționalul prezent formează perfectul optativ-condițional</i>)",
                        ("<i>Ne-ar <b>fi</b> ajutat.</i>",),
                        "(<i>cu conjunctivul prezent formează perfectul conjunctivului</i>)",
                        ("<i>Să <b>fi</b> spus adevărul.</i>",),
                        "(<i>cu infinitivul formează perfectul infinitivului</i>)",
                        ("<i>Se laudă a <b>fi</b> scris cartea.</i>",),
                        "(<i>cu viitorul I sau cu perfectul conjunctivului formează prezumtivul prezent și perfect</i>)",
                        ("<i>Să se <b>fi</b> ducând mulți acolo?</i>",),
                    ),
                    "(<i>construit cu un participiu invariabil sau cu un gerunziu, servește la alcătuirea unor forme perifrastice de perfect compus, mai mult ca perfect sau imperfect</i>)",
                    ("<i>Te-ai <b>fost</b> dus.</i>",),
                ]
            },
            [],
            ["fie", "fost", "sunt"],
        ),
        ("frumoasă", ["/fru'mo̯a.sə/"], [], {}, ["frumos"], []),
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
            [],
        ),
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
            ["paronime", "paronimele", "paronimelor", "paronimul", "paronimului"],
        ),
        (
            "MHz",
            [],
            [],
            {"Simbol": ["simbol pentru megahertz"]},
            [],
            [],
        ),
        ("portocale", ["/por.toˈka.le/"], [], {}, ["portocală"], []),
        (
            "temperatură",
            ["/tem.pe.raˈtu.rə/"],
            ["Din franceză <i>température</i> &lt; latină <i>temperatura</i>."],
            {
                "Substantiv": [
                    "gradul, starea de căldură a unui mediu, a unui corp etc.",
                    ("<i>A se păstra la o <b>temperatură</b> de maxim 5 grade Celsius.</i>",),
                    "stare fiziologică constantă a corpului animal, reprezentând echilibrul dintre căldura produsă și cea pierdută.",
                    "gradul de căldură ridicată a corpului omenesc, reprezentând un simptom patologic; fierbințeală, febră.",
                    ("<i>Ai <b>temperatură</b>; cred că ai răcit.</i>",),
                ],
                "Unități": [
                    "Metric (Sistemul Internațional): grad Celsius/centigrade (°C), kelvin (K).",
                    "Imperial: grade Fahrenheit (°F), grade Rankine (°R).",
                ],
            },
            [],
            ["temperatura", "temperaturi", "temperaturii", "temperaturile", "temperaturilor"],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "ro")
    details = parse_word(word, code, "ro", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
