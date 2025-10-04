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
        assert context.reset("pt")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "6",
            [],
            [],
            [],
            {
                "Pronome": ["(<i>internetês</i>) cês"],
                "Símbolo": ["algarismo indo-arábico que representa o numeral seis"],
            },
            [],
        ),
        (
            "-a",
            [],
            [],
            [
                "De <b>1</b>: desinência nominal feminina acrescentada no português moderno a palavras anteriormente comuns-de-dois, como portuguesa (e praticamente o padrão <i>-ês</i> [masculino]:-esa [feminino]), espanhol(a), senhor(a).",
                "De <b>4</b>: da vogal temática da 1ª conjugação latina.",
                "De <b>5</b>: da desinência do plural neutro latino",
            ],
            {
                "Pospositivo": [
                    "desinência nominal feminina",
                    "desinência nominal masculina",
                    "desinência nominal comuns-de-dois",
                    "vogal temática da primeira conjugação portuguesa",
                    "desinência plural masculina em português de latinismos como ultimatum (os ultimata), o corpus (os corpora), o genus (os genera) etc.",
                ]
            },
            [],
        ),
        ("ababalhar", [], [], ["De baba."], {"Verbo": ["(<i>popular</i>) babar; conspurcar"]}, []),
        (
            "alguém",
            ["/aɫ.ˈɡɐ̃j̃/"],
            [],
            ["Do latim <i>alĭquem</i>."],
            {"Pronome": ["pessoa não identificada"]},
            [],
        ),
        (
            "algo",
            ["/ˈaɫ.ɡu/"],
            [],
            [],
            {"Advérbio": ["um pouco, de certo modo"], "Pronome": ["objeto (não-identificado) de que se fala"]},
            [],
        ),
        ("anões", [], [], [], {}, ["anão"]),
        (
            "baiano",
            [],
            [],
            ["Derivado de Bahia, mais o sufixo ano, com perda do H."],
            {
                "Adjetivo": ["do Estado da Bahia, Brasil"],
                "Substantivo": [
                    "natural ou habitante do Estado da Bahia, Brasil",
                    "(<i>São Paulo,&nbsp;Brasil,&nbsp;popular,&nbsp;pejorativo e&nbsp;racismo</i>) pessoa que se veste de maneira incomum ou brega; fora da moda",
                ],
            },
            [],
        ),
        (
            "cabrum",
            [],
            ["mf"],
            ["Do latim <i>caprunu</i>&nbsp;“cabra”."],
            {
                "Adjetivo": ["(<i>Pecuária</i>) de cabras:", "(<i>Brasil</i>) marido de mulher adúltera"],
                "Interjeição": ["indica estrondo"],
            },
            [],
        ),
        (
            "COPOM",
            ["/ko.ˈpõ/"],
            ["m"],
            [],
            {
                "Acrónimo": [
                    "<b>C</b>entro de <b>O</b>perações da <b>Po</b>lícia <b>M</b>ilitar",
                    "(Brasil, governo) <b>Co</b>mitê de <b>Po</b>lítica <b>M</b>onetária",
                ]
            },
            [],
        ),
        (
            "dezassete",
            ["/dɨ.zɐ.ˈsɛ.tɨ/"],
            [],
            ["Contração do latim vulgar <i>decem</i> + <i>ac</i> + <i>septem</i>."],
            {
                "Numeral": ["vide dezessete"],
                "Substantivo": [
                    "o número dezassete (17, XVII)",
                    "nota correspondente a dezassete valores",
                    "pessoa ou coisa que apresenta o número dezassete numa ordenação",
                ],
            },
            [],
        ),
        ("ensimesmariam", [], [], [], {}, ["ensimesmar"]),
        (
            "etc",
            [],
            [],
            [],
            {
                "Abreviatura": [
                    'abreviação do latim <i>et cetera</i>, que significa "e outros", "e os restantes" e "e outras coisas mais"'
                ]
            },
            [],
        ),
        (
            "galium",
            [],
            [],
            [
                "Do nome do gênero ao que pertence a planta, <i>Galium</i>. Pelo grego γάλιον, (galion), (planta galião, <i>G. verum</i>), de γάλα, (gala), (leite, por ser usada para coalhar o leite)."
            ],
            {"Substantivo": ["planta do gênero <i>Galium</i>. De entre elas o amor-de-hortelão, (<i>G. aparine</i>)"]},
            [],
        ),
        (
            "giro-",
            [],
            [],
            ["Do grego antigo <i>γῦρος</i>&nbsp;<i>(gyros)</i>, pelo latim <i>gyrus</i>."],
            {"Afixo": ["círculo", "redondo"]},
            [],
        ),
        (
            "-ista",
            [],
            [],
            [
                "Do grego antigo <i>-ιστεσ</i> (<i>-istes</i>) através do latim <i>-ista</i> através do francês antigo <i>-iste</i>."
            ],
            {
                "Sufixo": [
                    "que segue um princípio",
                    "que é estudioso ou profissional de um assunto",
                    "que usa algo",
                    "que tem uma visão preconceituosa",
                ]
            },
            [],
        ),
        (
            "Ku",
            [],
            [],
            [],
            {"Substantivo": ["símbolo químico do kurtschatóvio"]},
            [],
        ),
        (
            "neo-",
            [],
            [],
            ["Do grego antigo <i>νέος</i>."],
            {
                "Prefixo": [
                    "exprime a ideia de <i>novo</i>",
                    "<b>Nota:</b> Liga-se por hífen ao morfema seguinte quando este começa por <b>vogal</b>, <b>h</b>, <b>r</b> ou <b>s</b>.",
                ]
            },
            [],
        ),
        (
            "não tenho trocado",
            [],
            [],
            [],
            {
                "Frase": [
                    "usado por prestador de serviço para informar que não tem dinheiro amiúde que possa servir de troco ao valor pago por cliente",
                    "usado por cliente de serviço para informar que não tem dinheiro amiúde que possa servir de diferença ao valor maior pretendido para devolução pelo prestador de serviço quando este não tem o valor em moeda exato para devolver ao cliente",
                ]
            },
            [],
        ),
        (
            "nomenclaturar",
            [],
            [],
            [],
            {"Verbo": ["fazer a nomenclatura de"]},
            [],
        ),
        (
            "objetiva",
            [],
            ["f"],
            [],
            {
                "Substantivo": [
                    "lente ou sistema de lentes de uma máquina fotográfica",
                    "lente que está voltada para o objeto que se quer ver ou examinar",
                ],
            },
            ["objetivar", "objetivo"],
        ),
        (
            "para",
            ["/ˈpɐ.ɾɐ/"],
            [],
            [],
            {
                "Preposição": ["exprime fim, destino, lugar, tempo, direção etc"],
            },
            ["parar"],
        ),
        (
            "paulista",
            [],
            [],
            [],
            {
                "Adjetivo": [
                    "diz-se de pessoa de origem do Estado de São Paulo, Brasil",
                    "diz-se de artigo ou objeto do Estado de São Paulo",
                ],
                "Substantivo": [
                    "pessoa de origem do Estado de São Paulo, Brasil",
                    "artigo ou objeto do Estado de São Paulo",
                ],
            },
            [],
        ),
        (
            "quebrar galho",
            [],
            [],
            [],
            {"Expressão": ["resolver uma situação difícil ou complicada"]},
            [],
        ),
        (
            "sublist",
            [],
            [],
            [],
            {"Adjetivo": ["<b>Romanização</b>", ("<b>Pinyin</b>: duo1 shan1",), "montanhoso"]},
            [],
        ),
        ("tenui-", [], [], [], {"Antepositivo": ["variante ortográfica de <b>tenu-</b>"]}, []),
        (
            "tique-taque",
            [],
            [],
            [],
            {"Onomatopeia": ["imitativa do som compassado do mecanismo de um relógio a trabalhar"]},
            [],
        ),
        (
            "to",
            [],
            [],
            [],
            {
                "Contração": [
                    "(<i>antigo</i>) contração do pronome pessoal te com o pronome pessoal ou demonstrativo o",
                ]
            },
            [],
        ),
        (
            "ũa",
            [],
            [],
            ["Do Latim <i>una-</i>: <i>una-</i> deu <b>ũa</b> por queda do <b>n</b> com a nasalação do <b>ũ</b>."],
            {"Artigo": ["ortografia antiga de uma"]},
            [],
        ),
        ("UTC", [], [], [], {"Sigla": ["(<i>estrangeirismo</i>) ver TUC"]}, []),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    genders: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "pt")
    details = parse_word(word, code, "pt", force=True)
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
