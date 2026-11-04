from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = __name__.split("_", 1)[1]


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "alemanera",
            ["/a.l̻e̻.ma.ne.ɾa/"],
            [],
            {"Izena": ["Indoeuropar hizkuntza bat da, germaniar hizkuntzen taldekoa."], "Sinonimoak": ["aleman"]},
            [],
            [
                "alemanerak",
                "alemaneran",
                "alemanerarekin",
                "alemaneraren",
                "alemanerarengatik",
                "alemanerarentzat",
                "alemanerari",
                "alemanerarik",
                "alemaneratzat",
                "alemaneraz",
            ],
        ),
        (
            "baremo",
            [],
            [
                "XVII. mendeko François Barrême frantziar matematikariarengandik, zeinaren kontabilitate liburu batek zabalkuntza handia izan zuen bere garaian, <i>Barême universel</i> izenaz."
            ],
            {"Izena": ["Zerbait baloratzeko eratutako taula edo koadroa."]},
            [],
            [
                "baremoa",
                "baremoak",
                "baremoarekin",
                "baremoaren",
                "baremoarengatik",
                "baremoarentzat",
                "baremoari",
                "baremoaz",
                "baremoean",
                "baremok",
                "baremoko",
                "baremora",
                "baremoraino",
                "baremorako",
                "baremorantz",
                "baremorekin",
                "baremoren",
                "baremorengatik",
                "baremorentzat",
                "baremori",
                "baremorik",
                "baremotako",
                "baremotan",
                "baremotara",
                "baremotaraino",
                "baremotarako",
                "baremotarantz",
                "baremotatik",
                "baremotik",
                "baremotzat",
                "baremoz",
            ],
        ),
        (
            "donostiar",
            [],
            [],
            {"Izenlaguna": ["Jatorriz edo hiritartasunez Donostiakoa."]},
            [],
            [
                "donostiarra",
                "donostiarrak",
                "donostiarrarekin",
                "donostiarraren",
                "donostiarrarengan",
                "donostiarrarengana",
                "donostiarrarenganaino",
                "donostiarrarenganako",
                "donostiarrarenganantz",
                "donostiarrarengandik",
                "donostiarrarengatik",
                "donostiarrarentzat",
                "donostiarrari",
                "donostiarraz",
                "donostiarrek",
                "donostiarrekin",
                "donostiarren",
                "donostiarrengan",
                "donostiarrengana",
                "donostiarrenganaino",
                "donostiarrenganako",
                "donostiarrenganantz",
                "donostiarrengandik",
                "donostiarrengatik",
                "donostiarrentzat",
                "donostiarrez",
                "donostiarri",
                "donostiarrik",
                "donostiartzat",
            ],
        ),
        (
            "hogeita hamaikarenganaino",
            ["/ogei.´tamaikaɾenganaɲo/"],
            [],
            {},
            ["hogeita hamaika"],
            [],
        ),
        (
            "kosmo-",
            [],
            [
                "Latinezko <i>cosmos</i> (« mundu ») hitzetik; bere aldetik greziera zaharrezko <i>κόσμος</i>, kosmos (« ordena »), erabilera batzuetan « unibertsoa », « mundu » eta « zeru » ere adierazten duena."
            ],
            {"Aurrizkia": ["Kosmos eta unibertsoarekin loturiko hitzak sortzeko."]},
            [],
            [],
        ),
        (
            "limburgera",
            ["/lim'buR.geɾa/"],
            [],
            {"Izena": ["Belgika eta Herbehereetako Limburg eskualdean hitz egiten den hizkuntza multzoa."]},
            [],
            [
                "limburgerak",
                "limburgeran",
                "limburgerarekin",
                "limburgeraren",
                "limburgerarengatik",
                "limburgerarentzat",
                "limburgerari",
                "limburgerarik",
                "limburgeratzat",
                "limburgeraz",
            ],
        ),
        (
            "monarka",
            ["/mo.´narka/"],
            [],
            {"Izena": ["Monarkia baten burua."], "Sinonimoak": ["errege", "erregina"]},
            [],
            [
                "monarkak",
                "monarkarekin",
                "monarkaren",
                "monarkarengan",
                "monarkarengana",
                "monarkarenganaino",
                "monarkarenganako",
                "monarkarenganantz",
                "monarkarengandik",
                "monarkarengatik",
                "monarkarentzat",
                "monarkari",
                "monarkarik",
                "monarkatzat",
                "monarkaz",
                "monarkei",
                "monarkek",
                "monarkekin",
                "monarken",
                "monarkengan",
                "monarkengana",
                "monarkenganaino",
                "monarkenganako",
                "monarkenganantz",
                "monarkengandik",
                "monarkengatik",
                "monarkentzat",
                "monarkez",
            ],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants

    assert not context.get_then_clear_errors()
