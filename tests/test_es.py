from collections import OrderedDict
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
        assert context.reset("es")


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "-acho",
            ["[ˈat͡ʃo]"],
            ["Del latín <i>-acĕus</i>. De allí también <i>-áceo</i>."],
            {"Sufijo": ["Forma aumentativos, a veces despectivos, a partir de adjetivos y sustantivos."]},
            [],
            [],
        ),
        (
            "bicicleta",
            ["Esp.: [biθiˈklet̪a]", "Am.: [bisiˈklet̪a]"],
            [
                "Del francés <i>bicyclette</i> y este diminutivo del francés <i>bicycle</i>, formado sobre el modelo del francés <i>tricycle</i>, del latín <i>bis</i>) y <i>-cycle</i> ( del latín <i>cyclus</i>, del griego <i>κύκλος</i>&nbsp;(<i>kýklos</i>,&nbsp;'círculo; rueda'))."
            ],
            {
                "Sustantivo": [
                    "Vehículos, ciclismo: Vehículo, comúnmente de dos ruedas iguales, propulsado mediante la aplicación de la fuerza de las piernas sobre los pedales que la transmiten hacia los piñones y una cadena moviendo la rueda trasera.",
                    ("<b>Sinónimos:</b> bici, velocípedo.",),
                ]
            },
            [],
            [],
        ),
        (
            "buque_mercante",
            ["[buke&#95;meɾˈkãn̪t̪e]"],
            [],
            {
                "Locución": [
                    "Náutica, comercio: Buque que pertenece a persona o empresa particular, y que se emplea en la conducción de pasajeros y mercancías."
                ]
            },
            [],
            [],
        ),
        (
            "cartel",
            ["[kaɾˈt̪el]"],
            ["Del occitano <i>cartel</i>."],
            {
                "Sustantivo": [
                    "Lámina en donde se imprime algún mensaje, ya sea con palabras, símbolos o imágenes, y se deja a la vista para difundir información.",
                    ("<b>Sinónimos:</b> póster, lámina, afiche, pasquín.",),
                    "Política: Escrito anónimo que se fija sobre un cartel y se deja en un lugar público con mensajes satíricos hacia algún político.",
                    ("<b>Sinónimos:</b> pasquín, cedulón.",),
                    "Escrito que se fija sobre un cartel en un lugar público, en donde se invita a otra persona a una contienda.",
                    "Escrito que se fija sobre un cartel en un lugar público, en donde se extorsiona al enemigo en una negociación, por ejemplo, en lo que respecta a la liberación de prisioneros.",
                    "Prestigio.",
                    ("<b>Sinónimos:</b> prestigio, reputación, credibilidad, renombre, nombradía.",),
                    "Pesca: Red que se usa para la pesca de la sardina.",
                    "Variante de&nbsp;cártel.",
                ]
            },
            [],
            [],
        ),
        (
            "comer",
            ["[koˈmeɾ]"],
            [
                "Se documenta por primera vez en 1140. Del latín <i>comedĕre</i>, infinitivo del latín <i>comedo</i>, formado a partir <i>cum</i>&nbsp;('con') y <i>edō</i>&nbsp;('comer')."
            ],
            {
                "Verbo": [
                    "Ingerir o tomar alimentos.",
                    ("<b>Sinónimo:</b> meterse entre pecho y espalda&nbsp;(coloquial)..",),
                    "Tomar la principal comida del día.",
                    ("<b>Sinónimos:</b> yantar&nbsp;(anticuado), almorzar..",),
                    "Malgastar bienes o recursos.",
                    "Corroer o consumir.",
                    "Producir comezón.",
                    ("<b>Sinónimos:</b> carcomer, picar..",),
                    "Juegos: En los juegos de mesa, eliminar una pieza del contrario.",
                    "Omitir elementos de información cuando se habla o escribe.",
                    "Llevar encogidas algunas prendas de ropa, como los calcetines.",
                    "Tener relaciones sexuales con alguien.",
                    ("<b>Sinónimos:</b> coger, cachar&nbsp;(Perú), follar, hacer el amor..",),
                ]
            },
            [],
            [
                "coma",
                "comamos",
                "coman",
                "comas",
                "come",
                "comed",
                "comemos",
                "comen",
                "comeremos",
                "comerá",
                "comerán",
                "comerás",
                "comeré",
                "comeréis",
                "comería",
                "comeríais",
                "comeríamos",
                "comerían",
                "comerías",
                "comes",
                "comido",
                "comiendo",
                "comiera",
                "comierais",
                "comieran",
                "comieras",
                "comiere",
                "comiereis",
                "comieren",
                "comieres",
                "comieron",
                "comiese",
                "comieseis",
                "comiesen",
                "comieses",
                "comimos",
                "comiste",
                "comisteis",
                "comiéramos",
                "comiéremos",
                "comiésemos",
                "comió",
                "como",
                "comáis",
                "comás",
                "comé",
                "coméis",
                "comés",
                "comí",
                "comía",
                "comíais",
                "comíamos",
                "comían",
                "comías",
            ],
        ),
        (
            "entrada",
            ["[ẽn̪ˈt̪ɾað̞a]"],
            ["De <i>entrado</i> (<i>participio de <i>entrar</i></i>) y el sufijo flexivo -a para el femenino."],
            {
                "Sustantivo": [
                    "Ticket o boleto; credencial, billete o documento que autoriza a entrar en un evento, espectáculo o lugar.",
                    "Gastronomía: Plato que se sirve al comienzo de la comida.",
                    ("<b>Sinónimo:</b> entrante..",),
                    "Lingüística:",
                    (
                        "Vocablo que titula un artículo de diccionario.",
                        "<b>Sinónimo:</b> lema.",
                        "Artículo de un diccionario, enciclopedia u obra de referencia.",
                    ),
                    "Espacio por donde se tiene acceso a un lugar, especialmente algún edificio o propiedad.",
                    "Acción o efecto de entrar a un lugar.",
                    "Evento o acto que se realiza para recibir a un nuevo miembro en alguna institución, organización, empresa, cargo, empleo o dignidad.",
                    "Salón, sala o estancia que se encuentra junto a la puerta principal de un edificio, especialmente un hotel o una vivienda.",
                    "Oportunidad para hacer o lograr algo.",
                    "Conjunto de personas que pagan por entrar a un espectáculo o evento y, por extensión, cantidad de dinero recaudado en tal evento.",
                    "Comienzo de una obra de literatura, de música, etc.",
                    "Amistad o acogida que recibe alguien en una familia.",
                    "En ciertos juegos de naipes, acción de indicar qué cartas se guardan y por qué.",
                    "Autorización para ingresar en ciertos recintos reservados, tales como oficinas, recámaras, etc., en especial de palacios o sitios de gobierno.",
                    "Anatomía: Zona sin cabello en la parte superior de la frente.",
                    "Comercio: Cantidad de dinero que ingresa en una caja o cuenta.",
                    "Comercio: Anotación o partida en el haber que indica dinero entrante (el aumento de un activo o la disminución de un pasivo).",
                    "Comercio: Cuota inicial; primer pago que se hace en la compra de algo a crédito o a plazos.",
                    "Milicia: Ingreso inicial de una tropa, un enemigo, etc., en el proceso de invadir un territorio.",
                    "Días iniciales de un periodo (un año, un mes, una temporada, una estación, etc.).",
                    "Deporte: Enfrentamiento o pase inicial entre contrarios.",
                    "Béisbol: Cada división de un partido, en que uno de los equipos tiene el turno para batear.",
                    "Arquitectura: Extremo o punta de un travesaño o madero que está metido en una pared o asentado sobre una solera.",
                    "Ingeniería: Turno o periodo en que trabaja un grupo de operarios.",
                    "Música: Momento en que una voz o instrumento comienza a intervenir en una pieza musical.",
                    "Castigo con golpes; tunda, zurra, pela.",
                    "Información que se recibe en un mensaje o proceso de recibirla.",
                ]
            },
            ["entrar"],
            [],
        ),
        (
            "extenuado",
            ["[ekst̪eˈnwað̞o]"],
            [],
            {
                "Adjetivo": [
                    "Cansado, debilitado.",
                    "Se dice de un individuo: sin energía, debido a un gran esfuerzo físico o mental.",
                ]
            },
            ["extenuar"],
            [],
        ),
        (
            "futuro",
            ["[fuˈt̪uɾo]"],
            [
                'Del latín <i>futūrus</i>, participio activo futuro irregular de <i>esse</i>&nbsp;(\'ser\'), y este el protoindoeuropeo <i>*bhū-</i>, <i>*bʰew-</i> ("existir", "llegar a ser").'
            ],
            {
                "Adjetivo": ["Que está aún por ocurrir o hacerse efectivo."],
                "Sustantivo": [
                    "Tiempo que aún no ha llegado.",
                    "Lingüística: Tiempo verbal que expresa una acción que aún no ha sido realizada.",
                    "Novio o prometido de una mujer a la que va a desposar.",
                ],
            },
            [],
            [],
        ),
        (
            "gracias",
            ["Esp.: [ˈgɾaθjas]", "Am.: [ˈgɾasjas]"],
            [],
            {
                "Interjección": [
                    "Úsase para expresar agradecimiento.",
                    "Irónicamente expresa desagrado, desprecio o enfado.",
                ]
            },
            [],
            [],
        ),
        (
            "Guyana",
            ["[guˈʝana]"],
            [],
            {
                "Sustantivo": [
                    "Países: País ubicado al noreste de Sudamérica. Limita al oeste con Venezuela, al norte con el océano Atlántico, al este con Surinam y al sur Brasil.",
                ],
            },
            [],
            [],
        ),
        (
            "hala",  # Important, it is mostly used to check for infinite loop in the Lua interpreter
            ["[ˈala]"],
            ["De origen incierto. Voz expresiva."],
            {"Interjección": ["Expresión para demandar prisa o sorpresa.", ("<b>Sinónimos:</b> ala, alá.",)]},
            ["halar"],
            [],
        ),
        (
            "hasta",
            ["[ˈast̪a]"],
            [
                "Del castellano antiguo <i>fasta</i>, del castellano antiguo <i>hata</i>, <i>fata</i>, del árabe حتى (<i>ḥattā</i>), influido por el latín <i>ad</i>&nbsp;('a') <i>ista</i>&nbsp;('esta').",
            ],
            {
                "Preposición": [
                    "Preposición que indica el fin o término de una actividad, sea en sentido locativo, cronológico o cuantitativo.",
                    ("<b>Sinónimos:</b> a, entro, enta..",),
                    "Seguida de <i>cuando</i> o de un gerundio, preposición que indica valor inclusivo.",
                    "Seguida de <i>que</i>, preposición que indica valor exclusivo.",
                ],
                "Adverbio": [
                    "Indica que pese a las circunstancias ocurre el hecho.",
                    ("<b>Sinónimos:</b> aun, inclusive, incluso..",),
                    "Indica que una situación eventual o hipotética no impide que ocurra el hecho.",
                    "Indica el comienzo de una acción o cuando ocurrirá.",
                    ("<b>Sinónimo:</b> desde., no antes de, recién",),
                ],
                "Sustantivo": ["Grafía obsoleta de&nbsp;asta."],
            },
            [],
            [],
        ),
        (
            "hocico",
            ["Esp.: [oˈθiko]", "Am.: [oˈsiko]"],
            ["De <i>hocicar</i>."],
            {
                "Sustantivo": [
                    "Zootomía: Parte más o menos prolongada de la cabeza de algunos animales en que están la boca y las narices.",
                    "Anatomía: Hocico de una persona cuando tiene muy abultados los labios.",
                    "Cara.",
                    "Gesto que denota enojo o enfado.",
                    "Forma despectiva para referirse a la boca de alguien.",
                    "Boca de una persona, especialmente de la que dice malas palabras.",
                ]
            },
            [],
            [],
        ),
        (
            "los",
            ["[los]"],
            ["Del latín <i>illōs</i>, acusativo masculino plural del latín <i>ille</i>."],
            {
                "Artículo": ["Artículo determinado masculino plural. El singular es lo."],
                "Pronombre": [
                    "<i>Pronombre personal masculino de objeto directo (acusativo), tercera persona del plural.</i>"
                ],
            },
            [],
            [],
        ),
        (
            "Mús.",
            ["[ˈmus]"],
            [],
            {"Abreviatura": ["<i>Abreviatura lexicográfica convencional de la palabra</i> música."]},
            [],
            [],
        ),
        (
            "ruego",
            ["[ˈrweɣ̞o]"],
            [],
            {"Sustantivo": ["Súplica, petición hecha con el fin de alcanzar lo que se pide."]},
            ["rogar"],
            [],
        ),
        (
            "también",
            ["[t̪ãmˈbjẽn]"],
            ["Compuesto de <i>tan</i> y <i>bien</i>"],
            {
                "Adverbio": [
                    "Utilizado para especificar que una o varias cosas son similares, o que comparten atributos con otra previamente nombrada.",
                    (
                        "<b>Sinónimos:</b> igualmente, asimismo, de igual modo, incluso, al igual, paralelamente, encima..",
                    ),
                    "Usado para añadir algo a lo anteriormente mencionado.",
                    ("<b>Sinónimos:</b> además, en añadidura..",),
                ]
            },
            [],
            [],
        ),
        (
            "uni-",
            ["[ˈuni]"],
            ["Del latín <i>uni-</i>, del latín <i>unus</i>."],
            {
                "Prefijo": [
                    "Elemento compositivo que significa uno. un único, relativo a uno solo.",
                    ("<b>Sinónimo:</b> mono-&nbsp;(griego).",),
                ]
            },
            [],
            [],
        ),
        (
            "zzz",
            [],
            ["Onomatopéyica."],
            {
                "Onomatopeya": [
                    "Onomatopeya que representa el sonido de la respiración durante el sueño. Se usa para indicar que alguien está dormido."
                ]
            },
            [],
            [],
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
    code = page(word, "es")
    details = parse_word(word, code, "es", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
