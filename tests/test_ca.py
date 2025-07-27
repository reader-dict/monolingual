from collections.abc import Callable

import pytest

from wikidict.render import parse_word
from wikidict.stubs import Definitions
from wikidict.utils import process_templates


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
            ["Del llatí <i>-izare</i>, del grec antic <i>-ίζειν</i> (<i>-ízein</i>)."],
            {
                "Sufix": [
                    "<i>Aplicat a un substantiu o adjectiu forma un verb que expressa la seva realització o convertir-se'n.</i>",
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
                    "<i>(masculí)</i> <i>Sigles de</i> <b>Alfabet Fonètic Internacional</b>",
                    "<i>(femení)</i> <i>Sigles de</i> <b>Associació Fonètica Internacional</b>",
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
                "[1] Per la forma de bóta: del llatí vulgar <i>buttis</i> («bóta»), segle XIII.",
                "[2] Per l’acció de botar: de <i>botar</i> i la desinència <i>Ø</i>, segle XV.",
                "[3] Nàutica: del francès antic <i>bot</i>, segle XVII, de l'anglès antic <i>bat</i> («barca petita»), actualment <i>boat</i>.",
                "[4] Informàtica: afèresi de <i>robot</i>, calc de l’anglès <i>bot</i>, segle XX.",
            ],
            {
                "Nom": [
                    "Recipient de cuir, originalment de boc per a contenir vi.",
                    "sac de gemecs",
                    "Reclam a manera d'ocell.",
                    "Peix (<i>Mola mola</i>) de la família els mòlids, de color gris i textura aspra, de cos discoïdal aplanat, però que s'unfla com un globus com a sistema de defensa.",
                    "Peix subtropical de la família dels diodòntids. (<i>Chilomycterus reticulatus</i>)",
                    "<i>(peixos)</i> ballesta",
                    "Salt enlaire amb un impuls ràpid.",
                    "Moviment elàstic d’un cos que en topar és llançat enlaire.",
                    "Embarcació petita sense coberta.",
                    "<i>(informàtica)</i> Programa informàtic dissenyat per a completar tasques d’assistència, especialment quan opera com un usuari.",
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
                    "<i>(negatiu)</i> Ni un.",
                    "<i>(interrogatiu, condicional)</i> Algun.",
                    "<i>(negatiu)</i> Gens de.",
                    "<i>(interrogatiu, condicional)</i> Alguna mena de.",
                ],
                "Nom": [
                    "<i>(anatomia)</i> Part superior i anterior del cos d'un animal.",
                    "Part superior del cos de l'ésser humà, considerada com a seu del pensament, l'intel·lecte, judici, talent, seny.",
                    "Lloc de preferència, central.",
                    "Localitat principal d'un territori; capital.",
                    "La part més alta d'una cosa.",
                    "Individu considerat com a membre d’una col·lectivitat.",
                    "Extremitat en general.",
                    ("Part anterior, per on comença una cosa.", "Part final, per on acaba una cosa."),
                    "Part de terra que s'endinsa en la mar.",
                    "<i>(nàutica)</i> corda",
                    "En un repartiment, cadascun dels participants.",
                    "<i>(golf)</i> Part final d'un bastó, que impacta en la bola en executar el colp.",
                    "<i>(pilota basca)</i> Part més ampla d'una eina.",
                    "<i>(bàdminton)</i> base",
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
            ["Del llatí <i>casus</i> («caiguda, cas fortuït»), de <i>cadere</i> («caure»), segle XIV."],
            {
                "Contracció": [
                    "Contracció entre el nom <i>casa</i> i l'article salat <i>es</i> quan és usat com un article personal. S'utilitza tant per referir-se a un habitatge com a una família. Sempre s'escriu davant de nom o de sobrenom."
                ],
                "Nom": [
                    "Situació particular que es produeix entre les diverses possibles.",
                    "Objecte d'estudi d'alguna disciplina.",
                    "<i>(lingüística)</i> Categoria gramatical que marca la funció sintàctica d’un mot.",
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
                        "Es Castell, municipi de Menorca.",
                        "Castell de l'Areny, municipi del Berguedà.",
                        "Castell de Cabres, municipi del Baix Maestrat.",
                        "Castell de Castells, municipi de la Marina Alta.",
                        "El Castell de Guadalest, municipi de la Marina Baixa.",
                        "Castell de Mur, municipi del Pallars Jussà.",
                        "Castell i Platja d'Aro, municipi del Baix Empordà.",
                        "Castell de Vernet, municipi del Conflent.",
                        "El Castell de Vilamalefa, municipi de l’Alt Millars.",
                    ),
                    "<i>Cognom d’origen d’habitatge</i>",
                ]
            },
            [],
        ),
        (
            "català",
            [],
            ["m"],
            [
                "D’origen incert, paral·lel al de <i>Catalunya</i>, segle XII. Potser de <i>*catelanos</i>, metàtesi del llatí <i>Lacetanōs</i>, acusatiu de <i>Lacetani</i> («lacetans»), poble ibèric de la regió central de Catalunya i que podria relacionar-se amb la menció de Ptolomeu dels Καστελανοι (<i>Kastelanoi</i>) o Κατελανοι (<i>Katelanoi</i>). Vegeu més informació a <i>Catalunya</i>.",
            ],
            {
                "Adjectiu": [
                    "Relatiu o pertanyent a Catalunya, als seus habitants o a la llengua catalana.",
                    "Relatiu o pertanyent als Països Catalans o als seus habitants.",
                ],
                "Nom": [
                    "Natural de Catalunya.",
                    "Natural dels Països Catalans.",
                    "<i>(masculí singular)</i> Llengua històricament parlada a Catalunya, Andorra, País Valencià, les illes Balears, la Catalunya Nord, l'Alguer i la Franja de Ponent.",
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
                    "<i>(arcaisme)</i> Especialment a final de mot, dígraf amb una consonant muda per remarcar la grafia d’una oclusiva velar sorda [k] i no pas una de sonora [ɡ]."
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
                    "<i>(beisbol)</i> Acció i efecte de l'àrbitre principal de determinar el nombre de boles i strikes d'un batedor en un temps de bat.",
                ],
                "Interjecció": ["atenció"],
            },
            ["comptar"],
        ),
        (
            "disset",
            [],
            ["m", "f"],
            ["Del llatí <i>decem et septem</i> (literalment «deu i set»)."],
            {
                "Numeral": [
                    "<i>(cardinal)</i> Nombre enter situat entre el setze i el divuit.",
                    "<i>(valor ordinal)</i> Dissetè, dissetena.",
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
                    "<i>Article determinat masculí singular que serveix per actualitzar i concretar el contingut del substantiu que acompanya.</i>"
                ],
                "Pronom": [
                    'Acusatiu del masculí singular del pronom personal "ell".',
                    'Substitueix el complement directe quan aquest porta l\'article "el".',
                ],
                "Nom": ["<i>(obsolet)</i> <i>Forma alternativa de</i> <b>ela</b>"],
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
            ["Del llatí <i>hībernāculum</i>, de <i>hībernō</i> («hivernar»)."],
            {"Nom": ["Cobert per a protegir plantes del vent o del fred extrem."]},
            [],
        ),
        ("Mn.", [], [], [], {"Abreviatura": ["mossèn com a tractament davant el nom"]}, []),
        ("PMF", [], [], [], {"Sigles": ["<i>Sigles de</i> <b>preguntes més freqüents</b>"]}, []),
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
                "[4] Pronom: del llatí <i>sibī</i>, datiu de <i>ille</i> («ell»).",
            ],
            {
                "Símbol": ["Codi de llengua ISO 639-1 del singalès."],
                "Conjunció": ["<i>Nexe condicional que introdueix un supòsit, una premissa.</i>"],
                "Nom": [
                    "Cavitat interna del cos.",
                    "<i>(per extensió)</i> Part interna d'una cosa.",
                    "Setena nota musical de l'escala.",
                ],
                "Pronom": ["<i>Forma del pronom reflexiu de tercera persona quan s'usa darrere de preposicions.</i>"],
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
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert definitions == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants


@pytest.mark.parametrize(
    "wikicode, expected",
    [
        ("{{AFI|/ˈwujt/}}", "/ˈwujt/"),
        ("{{claudàtors|[[milliarum]]}}", "[milliarum]"),
        ("{{color|#E01010}}", "[RGB #E01010]"),
        ("{{comp|ca|-oma}}", "sufix <i>-oma</i>"),
        ("{{doblet|ca|Castellar}}", "<i>Castellar</i>"),
        ("{{e|la|longifolius|longifolia}}", "longifolia"),
        ("{{e-propi|ca|grèvol}}", "<b>grèvol</b>"),
        ("{{IPAchar|[θ]}}", "[θ]"),
        ("{{pron|ca|/kənˈta/}}", "/kənˈta/"),
        ("{{pron|en|/əˈkrɔs/|/əˈkrɑs/}}", "/əˈkrɔs/, /əˈkrɑs/"),
        ("{{q|tenir bona planta}}", "<i>(tenir bona planta)</i>"),
        (
            "{{q|una planta|una cosa del terra}}",
            "<i>(una planta, una cosa del terra)</i>",
        ),
        ("{{romanes|XIX}}", "<span style='font-variant:small-caps'>xix</span>"),
        ("{{etim-s|ca|XIV}}", "segle XIV"),
        ("{{etim-s|ca|XVII|1617}}", "1617"),
    ],
)
def test_process_templates(wikicode: str, expected: str) -> None:
    """Test templates handling."""
    assert process_templates("foo", wikicode, "ca") == expected
