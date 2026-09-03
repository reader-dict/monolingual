from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "pt"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "6",
            [],
            [],
            {
                "Pronome": ["(internetês) cês"],
                "Símbolo": ["algarismo indo-arábico que representa o numeral seis"],
            },
            [],
            [],
        ),
        (
            "-a",
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
            ["a", "as"],
        ),
        (
            "ababalhar",
            ["BR: /a.ba.ba.ˈʎaɾ/"],
            ["De baba."],
            {"Verbo": ["(popular) babar; conspurcar"]},
            [],
            [
                "ababalha",
                "ababalhado",
                "ababalhai",
                "ababalhais",
                "ababalham",
                "ababalhamos",
                "ababalhando",
                "ababalhara",
                "ababalharam",
                "ababalharas",
                "ababalhardes",
                "ababalharei",
                "ababalhareis",
                "ababalharem",
                "ababalharemos",
                "ababalhares",
                "ababalharia",
                "ababalhariam",
                "ababalharias",
                "ababalharmos",
                "ababalhará",
                "ababalharás",
                "ababalharão",
                "ababalharíamos",
                "ababalharíeis",
                "ababalhas",
                "ababalhasse",
                "ababalhassem",
                "ababalhasses",
                "ababalhaste",
                "ababalhastes",
                "ababalhava",
                "ababalhavam",
                "ababalhavas",
                "ababalhe",
                "ababalhei",
                "ababalheis",
                "ababalhem",
                "ababalhemos",
                "ababalhes",
                "ababalho",
                "ababalhou",
                "ababalhámos",
                "ababalháramos",
                "ababalháreis",
                "ababalhásseis",
                "ababalhássemos",
                "ababalhávamos",
                "ababalháveis",
            ],
        ),
        (
            "alguém",
            ["PT: /aɫ.ˈɡɐ̃j̃/", "BR: /aw.ˈgẽj/"],
            ["Do latim <i>alĭquem</i>."],
            {"Pronome": ["pessoa não identificada"]},
            [],
            ["alguéns"],
        ),
        (
            "algo",
            ["PT: /ˈaɫ.ɡu/", "BR: /ˈaw.gu/"],
            [],
            {"Advérbio": ["um pouco, de certo modo"], "Pronome": ["objeto (não-identificado) de que se fala"]},
            [],
            [],
        ),
        ("anões", [], [], {}, ["anão"], []),
        (
            "baiano",
            ["BR: /baj.ˈjã.nu/"],
            ["Derivado de Bahia, mais o sufixo ano, com perda do H."],
            {
                "Adjetivo": ["do Estado da Bahia, Brasil"],
                "Expressão": ["<b>alqueire baiano</b>:", "<b>rodar a baiana</b>:"],
                "Substantivo": [
                    "natural ou habitante do Estado da Bahia, Brasil",
                    "(São Paulo,&nbsp;Brasil,&nbsp;popular,&nbsp;pejorativo e&nbsp;racismo) pessoa que se veste de maneira incomum ou brega; fora da moda",
                ],
            },
            [],
            ["baiana", "baianas", "baianos"],
        ),
        (
            "cabrum",
            [],
            ["Do latim <i>caprunu</i>&nbsp;“cabra”."],
            {
                "Adjetivo|mf.": ["(Pecuária) de cabras:", "(Brasil) marido de mulher adúltera"],
                "Interjeição": ["indica estrondo"],
                "Sinónimo": ["caprídeo", "caprino"],
            },
            [],
            ["cabruns"],
        ),
        (
            "COPOM",
            ["BR: /ko.ˈpõ/"],
            [],
            {
                "Acrónimo|m.": [
                    "<b>C</b>entro de <b>O</b>perações da <b>Po</b>lícia <b>M</b>ilitar",
                    "(Brasil, governo) <b>Co</b>mitê de <b>Po</b>lítica <b>M</b>onetária",
                ]
            },
            [],
            [],
        ),
        (
            "dezassete",
            ["PT: /dɨ.zɐ.ˈsɛ.tɨ/"],
            ["Contração do latim vulgar <i>decem</i> + <i>ac</i> + <i>septem</i>."],
            {
                "Numeral": ["vide dezessete"],
                "Substantivo|m.": [
                    "o número dezassete (17, XVII)",
                    "nota correspondente a dezassete valores",
                    "pessoa ou coisa que apresenta o número dezassete numa ordenação",
                ],
            },
            [],
            ["dezassetes"],
        ),
        ("ensimesmariam", [], [], {}, ["ensimesmar"], []),
        (
            "etc",
            [],
            [],
            {
                "Abreviatura": [
                    'abreviação do latim <i>et cetera</i>, que significa "e outros", "e os restantes" e "e outras coisas mais"'
                ]
            },
            [],
            [],
        ),
        (
            "galium",
            [],
            [
                "Do nome do gênero ao que pertence a planta, <i>Galium</i>. Pelo grego γάλιον, (galion), (planta galião, <i>G. verum</i>), de γάλα, (gala), (leite, por ser usada para coalhar o leite)."
            ],
            {"Substantivo": ["planta do gênero <i>Galium</i>. De entre elas o amor-de-hortelão, (<i>G. aparine</i>)"]},
            [],
            ["galiuns"],
        ),
        (
            "giro-",
            [],
            ["Do grego antigo <i>γῦρος</i>&nbsp;<i>(gyros)</i>, pelo latim <i>gyrus</i>."],
            {"Afixo": ["círculo", "redondo"]},
            [],
            [],
        ),
        (
            "-ista",
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
            [],
        ),
        (
            "Ku",
            [],
            [],
            {"Substantivo": ["símbolo químico do kurtschatóvio"]},
            [],
            [],
        ),
        (
            "neo-",
            [],
            ["Do grego antigo <i>νέος</i>."],
            {
                "Prefixo": [
                    "exprime a ideia de <i>novo</i>",
                    "<b>Nota:</b> Liga-se por hífen ao morfema seguinte quando este começa por <b>vogal</b>, <b>h</b>, <b>r</b> ou <b>s</b>.",
                ],
                "Sinónimo": ["novi-"],
            },
            [],
            [],
        ),
        (
            "não tenho trocado",
            [],
            [],
            {
                "Frase": [
                    "usado por prestador de serviço para informar que não tem dinheiro amiúde que possa servir de troco ao valor pago por cliente",
                    "usado por cliente de serviço para informar que não tem dinheiro amiúde que possa servir de diferença ao valor maior pretendido para devolução pelo prestador de serviço quando este não tem o valor em moeda exato para devolver ao cliente",
                ]
            },
            [],
            [],
        ),
        (
            "nomenclaturar",
            [],
            [],
            {"Verbo": ["fazer a nomenclatura de"]},
            [],
            [
                "nomenclatura",
                "nomenclaturado",
                "nomenclaturai",
                "nomenclaturais",
                "nomenclaturam",
                "nomenclaturamos",
                "nomenclaturando",
                "nomenclaturara",
                "nomenclaturaram",
                "nomenclaturaras",
                "nomenclaturardes",
                "nomenclaturarei",
                "nomenclaturareis",
                "nomenclaturarem",
                "nomenclaturaremos",
                "nomenclaturares",
                "nomenclaturaria",
                "nomenclaturariam",
                "nomenclaturarias",
                "nomenclaturarmos",
                "nomenclaturará",
                "nomenclaturarás",
                "nomenclaturarão",
                "nomenclaturaríamos",
                "nomenclaturaríeis",
                "nomenclaturas",
                "nomenclaturasse",
                "nomenclaturassem",
                "nomenclaturasses",
                "nomenclaturaste",
                "nomenclaturastes",
                "nomenclaturava",
                "nomenclaturavam",
                "nomenclaturavas",
                "nomenclature",
                "nomenclaturei",
                "nomenclatureis",
                "nomenclaturem",
                "nomenclaturemos",
                "nomenclatures",
                "nomenclaturo",
                "nomenclaturou",
                "nomenclaturámos",
                "nomenclaturáramos",
                "nomenclaturáreis",
                "nomenclaturásseis",
                "nomenclaturássemos",
                "nomenclaturávamos",
                "nomenclaturáveis",
            ],
        ),
        (
            "objetiva",
            [],
            [],
            {
                "Substantivo|f.": [
                    "lente ou sistema de lentes de uma máquina fotográfica",
                    "lente que está voltada para o objeto que se quer ver ou examinar",
                ],
            },
            ["objetivar", "objetivo"],
            [],
        ),
        (
            "para",
            ["PT: /ˈpɐ.ɾɐ/"],
            ["Do latim <i>per</i> <i>ad</i>."],
            {
                "Preposição": ["exprime fim, destino, lugar, tempo, direção etc"],
            },
            ["parar"],
            [],
        ),
        (
            "paulista",
            ["BR: /paw.ˈlis.tə/"],
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
            ["paulistas"],
        ),
        (
            "quebrar galho",
            [],
            [],
            {"Expressão": ["resolver uma situação difícil ou complicada"]},
            [],
            [],
        ),
        (
            "sublist",
            [],
            [],
            {"Adjetivo": ["<b>Romanização</b>", ("<b>Pinyin</b>: duo1 shan1",), "montanhoso"]},
            [],
            [],
        ),
        (
            "tatu",
            ["PT: /ta.ˈtu/", "BR: /taˈtu/"],
            ["De substantivo¹ (animal):Do tupi <i>tatu</i>."],
            {
                "Substantivo|m.": [
                    "(zoologia) (<i>epiceno</i>) nome comum aos animais da ordem dos cingulados oriunda da América do Sul e desta tendo se espalhado até o sudeste da América do Norte, caracterizado por contar com uma carapaça dorsal articulada (que por vezes se estende até a parte superior do crânio) formada por placas justapostas, geralmente dispostas em fileiras transversais, com cauda comprida, membros curtos e garras longas e afiadas para cavar as tocas onde habita",
                    "(Brasil e&nbsp;alimentação) por extensão, prato feito com a carne desse animal",
                    "(Brasil e&nbsp;Folclore) tipo de dança folclórica de São Paulo e Rio Grande do Sul, modalidade de fandango, composta de apresentação curta mas onde o sapateado masculino, com o tilintar das esporas, contrasta com o bailado delicado feminino, com versos ligeiros à moda de uma caça ao tatu, tamanho variando de 13-15 centímetros de comprimento na menor espécie até cerca de 1,5 m na espécie canastra",
                    "(Brasil e&nbsp;Folclore) tipo de dança que existia no antigo estado de Mato Grosso",
                    "(Brasil e&nbsp;Pecuária) variedade do porco doméstico",
                    "(Amazonas) tipo de abrigo temporário feito com galhos e folhas durante as chuvas",
                    "(Rio Grande do Sul) cobertura usada para a secagem da erva-mate",
                    "(Brasil e&nbsp;Árvore) árvore de pequeno porte nativa do Brasil onde habita vários biomas (da amazônia ao cerrado), da família das opiliáceas (<i>Agonandra brasiliensis</i>), com madeira frequentemente usada para pisos e móveis, reflorestamento e até uso da casca para cortiça",
                    "(Brasil e&nbsp;coloquial) muco nasal",
                ],
                "Substantivo|f.": [
                    "o mesmo que tatuagem (desenho visível na pele humana resultado da aplicação subcutânea de pigmento]s introduzidos através de perfurações com agulhas)"
                ],
                "Expressão": [
                    "<b>arrancar um tatu</b>: atolar-se",
                    "<b>levar um tatu</b>: levar queda",
                    "<b>pegar um tatu</b>: levar queda",
                    "<b>mais ligeiro que tatu de kichute</b>: alguém que age ou foge de forma rápida (Rio Grande do Sul)",
                ],
                "Sinónimo": ["pau-marfim", "(estrangeirismo) <i>tattoo</i>", "tatuagem"],
            },
            [],
            ["tatus"],
        ),
        ("tenui-", [], [], {"Antepositivo": ["variante ortográfica de <b>tenu-</b>"]}, [], []),
        (
            "tique-taque",
            [],
            [],
            {
                "Onomatopeia": ["imitativa do som compassado do mecanismo de um relógio a trabalhar"],
                "Sinónimo": ["tic-tac"],
            },
            [],
            [],
        ),
        (
            "to",
            [],
            [],
            {
                "Contração|m.": [
                    "(antigo) contração do pronome pessoal te com o pronome pessoal ou demonstrativo o",
                ]
            },
            [],
            ["ta", "tas", "tos"],
        ),
        (
            "ũa",
            [],
            ["Do Latim <i>una-</i>: <i>una-</i> deu <b>ũa</b> por queda do <b>n</b> com a nasalação do <b>ũ</b>."],
            {"Artigo": ["ortografia antiga de uma"]},
            [],
            ["ũas", "ũu", "ũus"],
        ),
        ("UTC", [], [], {"Sigla": ["(estrangeirismo) ver TUC"]}, [], []),
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
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
