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
        assert context.reset("ca")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "-ass-",
            [],
            [],
            ["Del sufix <i>-às</i> amb valor augmentatiu."],
            {"Infix": ["Infix que afegeix un matís augmentatiu."]},
            [],
        ),
        (
            "-itzar",
            [],
            [],
            ["Del llatí <i>-izare</i>, del grec antic <i>-ίζειν</i> &lrm;(-ízein)."],
            {
                "Sufix": [
                    "Aplicat a un substantiu o adjectiu forma un verb que expressa la seva realització o convertir-se'n.",
                ]
            },
            [],
        ),
        (
            "AFI",
            [],
            [],
            [],
            {
                "Sigles": [
                    "(<i>masculí</i>) <i>Sigles de</i> <b>Alfabet Fonètic Internacional</b>.",
                    "(<i>femení</i>) <i>Sigles de</i> <b>Associació Fonètica Internacional</b>.",
                ]
            },
            [],
        ),
        (
            "avui",
            [],
            [],
            [],
            {"Adverbi": ["En el dia actual.", "Metafòricament, en el present."]},
            [],
        ),
        (
            "bio-",
            [],
            [],
            [],
            {"Prefix": ["Element que entra en la composició de paraules amb el sentit de <i>vida</i>."]},
            [],
        ),
        (
            "bot",
            [],
            ["m"],
            [
                "[1] Per la forma de bóta: del llatí vulgar <i>buttis</i> &lrm;(‘bóta’), segle XIII.",
                "[2] Per l’acció de botar: de <i>botar</i> i la desinència <i>Ø</i>, segle XV.",
                "[3] Nàutica: del francès antic <i>bot</i>, segle XVII, de l'anglès antic <i>bat</i> &lrm;(‘barca petita’), actualment <i>boat</i>.",
                "[4] Informàtica: afèresi de <i>robot</i>, calc de l’anglès <i>bot</i>, segle XX.",
            ],
            {
                "Nom": [
                    "Recipient de cuir, originalment de boc per a contenir vi.",
                    "sac de gemecs",
                    "Reclam a manera d'ocell.",
                    "Peix (<i>Mola mola</i>) de la família els mòlids, de color gris i textura aspra, de cos discoïdal aplanat, però que s'unfla com un globus com a sistema de defensa.",
                    "Peix subtropical de la família dels diodòntids. (<i>Chilomycterus reticulatus</i>)",
                    "(<i>peixos</i>) ballesta",
                    "Salt enlaire amb un impuls ràpid.",
                    "Moviment elàstic d’un cos que en topar és llançat enlaire.",
                    "Embarcació petita sense coberta.",
                    "(<i>informàtica</i>) Programa informàtic dissenyat per a completar tasques d’assistència, especialment quan opera com un usuari.",
                ]
            },
            ["botar", "botre"],
        ),
        (
            "cap",
            [],
            ["m", "mf"],
            [
                "Del llatí vulgar <i>*capu(m)</i>, variant de l’acusatiu <i>caput</i>, segle XIII. Com a adjectiu pel sentit d’«extrem, punta». Com a preposició pel sentit de «part anterior (vers un lloc)»."
            ],
            {
                "Adjectiu": [
                    "(<i>negatiu</i>) Ni un.",
                    "(interrogatiu,&#32;condicional) Algun.",
                    "(<i>negatiu</i>) Gens de.",
                    "(interrogatiu,&#32;condicional) Alguna mena de.",
                ],
                "Nom": [
                    "(<i>anatomia</i>) Part superior i anterior del cos d'un animal.",
                    "Part superior del cos de l'ésser humà, considerada com a seu del pensament, l'intel·lecte, judici, talent, seny.",
                    "Lloc de preferència, central.",
                    "Localitat principal d'un territori; capital.",
                    "La part més alta d'una cosa.",
                    "Individu considerat com a membre d’una col·lectivitat.",
                    "Extremitat en general.",
                    (
                        "Part anterior, per on comença una cosa.",
                        "Part final, per on acaba una cosa.",
                    ),
                    "Part de terra que s'endinsa en la mar.",
                    "(<i>nàutica</i>) corda",
                    "En un repartiment, cadascun dels participants.",
                    "(<i>golf</i>) Part final d'un bastó, que impacta en la bola en executar el colp.",
                    "(<i>pilota basca</i>) Part més ampla d'una eina.",
                    "(<i>bàdminton</i>) base",
                    "Persona que ocupa el primer lloc, que mana o que dirigeix quelcom; capitost.",
                    "Grau militar.",
                ],
                "Preposició": ["cap a"],
            },
            ["cabre", "capar"],
        ),
        (
            "cas",
            [],
            ["m"],
            ["Del llatí <i>casus</i> &lrm;(‘caiguda, cas fortuït’), de <i>cadere</i> &lrm;(‘caure’), segle XIV."],
            {
                "Contracció": [
                    "Contracció entre el nom <i>casa</i> i l'article salat <i>es</i> quan és usat com un article personal. S'utilitza tant per referir-se a un habitatge com a una família. Sempre s'escriu davant de nom o de sobrenom."
                ],
                "Nom": [
                    "Situació particular que es produeix entre les diverses possibles.",
                    "Objecte d'estudi d'alguna disciplina.",
                    "(<i>lingüística</i>) Categoria gramatical que marca la funció sintàctica d’un mot.",
                    "Atenció, cura.",
                ],
            },
            ["ca", "casar"],
        ),
        (
            "Castell",
            [],
            [],
            ["De <i>castell</i>."],
            {
                "Nom Propi": [
                    "Diversos topònims, especialment:",
                    (
                        "Es Castell&#x202F;, municipi de Menorca.",
                        "Castell de l'Areny&#x202F;, municipi del Berguedà.",
                        "Castell de Cabres&#x202F;, municipi del Baix Maestrat.",
                        "Castell de Castells&#x202F;, municipi de la Marina Alta.",
                        "El Castell de Guadalest&#x202F;, municipi de la Marina Baixa.",
                        "Castell de Mur&#x202F;, municipi del Pallars Jussà.",
                        "Castell i Platja d'Aro&#x202F;, municipi del Baix Empordà.",
                        "Castell de Vernet&#x202F;, municipi del Conflent.",
                        "El Castell de Vilamalefa&#x202F;, municipi de l’Alt Millars.",
                    ),
                    "Cognom&nbsp;d’origen d’habitatge",
                ]
            },
            [],
        ),
        (
            "català",
            [],
            ["m"],
            [
                "D’origen incert, paral·lel al de <i>Catalunya</i>, segle XII. Potser de <i>*catelanos</i>, metàtesi del llatí <i>Lacetanōs</i>, acusatiu de <i>Lacetani</i> &lrm;(‘lacetans’), poble ibèric de la regió central de Catalunya i que podria relacionar-se amb la menció de Ptolomeu dels <i>Καστελανοι</i> &lrm;(Kastelanoi) o <i>Κατελανοι</i> &lrm;(Katelanoi). Vegeu més informació a <i>Catalunya</i>."
            ],
            {
                "Adjectiu": [
                    "Relatiu o pertanyent a Catalunya, als seus habitants o a la llengua catalana.",
                    "Relatiu o pertanyent als Països Catalans o als seus habitants.",
                ],
                "Nom": [
                    "Natural de Catalunya.",
                    "Natural dels Països Catalans.",
                    "(<i>masculí singular</i>) Llengua històricament parlada a Catalunya, Andorra, País Valencià, les illes Balears, la Catalunya Nord, l'Alguer i la Franja de Ponent.",
                    "catalanoparlant",
                ],
            },
            [],
        ),
        (
            "ch",
            [],
            [],
            [],
            {
                "Símbol": ["Codi de llengua ISO 639-1 del chamorro."],
                "Lletra": [
                    "(<i>arcaisme</i>) Especialment a final de mot, dígraf amb una consonant muda per remarcar la grafia d’una oclusiva velar sorda [k] i no pas una de sonora [ɡ]."
                ],
            },
            [],
        ),
        (
            "compte",
            [],
            ["m"],
            ["Del llatí <i>compŭtus</i>, segle XIII."],
            {
                "Nom": [
                    "Acte de comptar.",
                    "Cura, atenció.",
                    "Suma de la quantitat a pagar.",
                    "(<i>beisbol</i>) Acció i efecte de l'àrbitre principal de determinar el nombre de boles i strikes d'un batedor en un temps de bat.",
                ],
                "Interjecció": ["atenció"],
            },
            ["comptar"],
        ),
        (
            "disset",
            [],
            ["m", "f"],
            [
                "Contracció de l’antic <i>*deïsset</i>, evolució fonètica del català antic <i>deesset</i> per la pronúncia /ɛe/, de <i>desesset</i>, del llatí <i>decem et septem</i> &lrm;(literalment ‘deu i set’), segle XVIII. Compareu amb <i>divuit</i> i <i>dinou</i>."
            ],
            {
                "Numeral": [
                    "(<i>cardinal</i>) Nombre enter situat entre el setze i el divuit.",
                    "(<i>valor ordinal</i>) dissetè, dissetena.",
                ],
                "Nom": ["Xifra i nombre 17.", "Dissetena hora."],
            },
            [],
        ),
        (
            "el",
            ["/əɫ/"],
            ["f"],
            [
                "Del català antic <i>lo</i>, per fals tall sil·làbic de <i>·l</i>, forma reduïda darrere d’una <i>e</i>, segle XIV. Per exemple: <i>que lo &gt; que·l &gt; qu’el &gt; que el; de lo &gt; del; e lo &gt; e·l &gt; i el</i>."
            ],
            {
                "Símbol": ["Codi de llengua ISO 639-1 del grec modern."],
                "Article": [
                    "Article determinat masculí singular que serveix per actualitzar i concretar el contingut del substantiu que acompanya."
                ],
                "Pronom": [
                    'Acusatiu del masculí singular del pronom personal "ell".',
                    'Substitueix el complement directe quan aquest porta l\'article "el".',
                ],
                "Nom": ["(<i>obsolet</i>) <i>Forma alternativa de</i> <b>ela</b>."],
            },
            [],
        ),
        (
            "expertes",
            [],
            [],
            [],
            {},
            ["experta"],
        ),
        ("halloweeniana", [], [], [], {}, ["halloweenià"]),
        (
            "hivernacle",
            [],
            ["m"],
            ["Del llatí <i>hībernāculum</i>, de <i>hībernō</i> &lrm;(‘hivernar’)."],
            {"Nom": ["Cobert per a protegir plantes del vent o del fred extrem."]},
            [],
        ),
        ("Mn.", [], [], [], {"Abreviatura": ["mossèn com a tractament davant el nom"]}, []),
        ("PMF", [], [], [], {"Sigles": ["<i>Sigles de</i> <b>preguntes més freqüents</b>."]}, []),
        (
            "pen",
            [],
            [],
            [],
            {},
            ["penar"],
        ),
        (
            "si",
            [],
            ["m"],
            [
                "[1] Conjunció: del llatí <i>sī</i>, segle XII.",
                "[2] Nom: del llatí <i>sĭnus</i>, segle XIII. Doblet del cultisme <i>sinus</i>.",
                "[3] Nota musical: de les inicials llatines <i>Sancte</i> <i>Ioannes</i> de l'himne <i>Ut queant laxis</i> de Pau el Diaca d'on es va extraure l'escala musical, segle XIII.",
                "[4] Pronom: del llatí <i>sibī</i>, datiu de <i>ille</i> &lrm;(‘ell’).",
            ],
            {
                "Símbol": ["Codi de llengua ISO 639-1 del singalès."],
                "Conjunció": ["Nexe condicional que introdueix un supòsit, una premissa."],
                "Nom": [
                    "Cavitat interna del cos.",
                    "(<i>per extensió</i>) Part interna d'una cosa.",
                    "Setena nota musical de l'escala.",
                ],
                "Pronom": ["Forma del pronom reflexiu de tercera persona quan s'usa darrere de preposicions."],
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
    code = page(word, "ca")
    details = parse_word(word, code, "ca", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert definitions == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants
