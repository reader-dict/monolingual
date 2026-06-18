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
        assert context.reset("it")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "brillantino",
            [],
            ["m"],
            [
                "da brillare",
                "vedi brillantare",
            ],
            {
                "Sostantivo": [
                    "piccolo foglietto di materiale lucido e riflettente usato come ornamento per abiti",
                    "<small>(<i>per estensione</i>)</small> glitter",
                ]
            },
            ["brillantare"],
        ),
        (
            "condividere",
            ["/kondiˈvidere/"],
            [],
            [
                "dal latino <i>cum</i> e <i>dividere</i>; l'attuale uso improprio del verbo <i>condividere</i> è dovuto alla diffusione dei social network negli anni 2000 e 2010",
            ],
            {
                "Sinonimi": [
                    "aderire, appoggiare, approvare, concordare esprimere adesione, "
                    "essere solidale, essere d’accordo, partecipare, sostenere,",
                    "avere in comune, compartecipare possedere, dividere, spartire",
                    "<small>(<i>per estensione</i>)</small> <small>(<i>senso "
                    "figurato</i>)</small> accettare, accogliere",
                ],
                "Verb": [
                    "spartire con altri",
                    "avere qualcosa in comune con qualcun altro",
                    "essere d'accordo con altri su un punto di vista",
                    "<small>(<i>filosofia</i>)</small> <small>(<i>economia</i>)</small> mettere spazi e risorse in comune con altri",
                    "<small>(<i>informatica</i>)</small> ricevere o mettere un'informazione in comune con altri utenti",
                ],
            },
            [],
        ),
        (
            "debolmente",
            ["/debolˈmente/"],
            [],
            ["composto dall'aggettivo debole e dal suffisso -mente"],
            {
                "Avverbio": ["in maniera debole, con debolezza"],
                "Sinonimi": ["fragilmente, fiaccamente, mollemente", "lievemente, scarsamente", "stancamente"],
            },
            [],
        ),
        (
            "lettore",
            ["/letˈtore/"],
            ["m"],
            ['dal latino <i>lector</i>, derivazione di <i>legĕre</i> ossia "leggere"'],
            {
                "Sinonimi": ["riproduttore", "<i>(in informatica)</i> decodificatore, interprete"],
                "Sostantivo": [
                    "chi legge un libro, un giornale o una rivista",
                    "<small>(<i>religione</i>)</small> persona che in alcune chiese cristiane, come la Chiesa cattolica, la Chiesa anglicana e quella ortodossa, è incaricata di proclamare la parola di Dio e altri testi nelle celebrazioni liturgiche e di esercitare altri compiti in campo pastorale",
                    "<small>(<i>elettronica</i>)</small> <small>(<i>informatica</i>)</small> <small>(<i>tecnologia</i>)</small> <small>(<i>ingegneria</i>)</small> dispositivo elettronico che decodifica e riceve informazioni da un supporto",
                ],
            },
            [],
        ),
        (
            "modalità Goblin",
            ["/modali'ta 'go blin/"],
            ["f"],
            [],
            {
                "Nome": [
                    "modalità Goblin, oppure in modalità Goblin è un tipo di comportamento autoindulgente, pigro, sciatto o avido, che rifiuta le norme o le aspettative sociali. Questo comportamento si deve anche all'influsso del covid nell'ambiente fisico sulla mente e la socialità delle persone"
                ]
            },
            [],
        ),
        (
            "muratrici",
            [],
            [],
            [],
            {},
            ["muratore"],
        ),
        (
            "rimpannucciare",
            ["/rimpannutˈʧare/"],
            [],
            ["deriva da panno"],
            {
                "Sinonimi": [
                    "rivestire, vestire",
                    "<small>(<i>senso figurato</i>)</small> rimettere in arnese, rimettere in sesto",
                ]
            },
            [],
        ),
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
    code = page(word, "it")
    details = parse_word(word, code, "it", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
