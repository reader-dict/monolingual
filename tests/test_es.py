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
            ["[ˈa.t͡ʃo]"],
            ["Del latín <i>-acĕus</i>. De allí también <i>-áceo</i>."],
            {"Sufijo": ["Forma aumentativos, a veces despectivos, a partir de adjetivos y sustantivos."]},
            [],
            [],
        ),
        (
            "bicicleta",
            ["[bi.siˈkle.t̪a]", "[bi.θiˈkle.t̪a]"],
            [
                "Del francés <i>bicyclette</i> y este diminutivo del francés <i>bicycle</i>, formado sobre el modelo del francés <i>tricycle</i>, del latín <i>bis</i>) y -cycle ( del latín <i>cyclus</i>, del griego κύκλος&nbsp;(kýklos,&nbsp;'círculo; rueda'))."
            ],
            {
                "Sustantivo": [
                    "Vehículos, ciclismo: Vehículo, comúnmente de dos ruedas iguales, propulsado mediante la aplicación de la fuerza de las piernas sobre los pedales que la transmiten hacia los piñones y una cadena moviendo la rueda trasera."
                ]
            },
            [],
            [],
        ),
        (
            "buque_mercante",
            ["[bu.ke_.meɾˈkan̪.t̪e]"],
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
                    "Política: Escrito anónimo que se fija sobre un cartel y se deja en un lugar público con mensajes satíricos hacia algún político.",
                    "Escrito que se fija sobre un cartel en un lugar público, en donde se invita a otra persona a una contienda.",
                    "Escrito que se fija sobre un cartel en un lugar público, en donde se extorsiona al enemigo en una negociación, por ejemplo, en lo que respecta a la liberación de prisioneros.",
                    "Prestigio.",
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
                "Se documenta por primera vez en 1140. Del latín <i>comedĕre</i>, infinitivo del latín <i>comedo</i>, formado a partir cum&nbsp;('con') y edō&nbsp;('comer')."
            ],
            {
                "Verbo": [
                    "Ingerir o tomar alimentos.",
                    "Tomar la principal comida del día.",
                    "Malgastar bienes o recursos.",
                    "Corroer o consumir.",
                    "Producir comezón.",
                    "Juegos: En los juegos de mesa, eliminar una pieza del contrario.",
                    "Omitir elementos de información cuando se habla o escribe.",
                    "Llevar encogidas algunas prendas de ropa, como los calcetines.",
                    "Tener relaciones sexuales con alguien.",
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
            ["[en̪ˈt̪ɾa.ð̞a]"],
            ["De <i>entrado</i> (<i>participio de <i>entrar</i></i>) y el sufijo flexivo -a para el femenino."],
            {
                "Sustantivo": [
                    "Ticket o boleto; credencial, billete o documento que autoriza a entrar en un evento, espectáculo o lugar.",
                    "Gastronomía: Plato que se sirve al comienzo de la comida.",
                    "Lingüística:",
                    (
                        "Vocablo que titula un artículo de diccionario.",
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
            ["[eks.t̪eˈnwa.ð̞o]"],
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
            ["[fuˈtu.ɾo]"],
            [
                'Del latín <i>futūrus</i>, participio activo futuro irregular de esse&nbsp;(\'ser\'), y este el protoindoeuropeo bhū-, bʰew- ("existir", "llegar a ser").'
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
            ["[ˈɡɾa.sjas]", "[ˈɡɾa.θjas]"],
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
            ["[ɡuˈʃa.na]", "[ɡuˈʒa.na]", "[ɡuˈʝa.na]"],
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
            "hasta",
            ["[ˈas.t̪a]"],
            [
                "Del castellano antiguo <i>fasta</i>, del castellano antiguo <i>hata</i>, fata, del árabe حتى (<i>ḥattā</i>), influido por el latín ad&nbsp;('a') ista&nbsp;('esta').",
            ],
            {
                "Adverbio": [
                    "Indica que pese a las circunstancias ocurre el hecho.",
                    "Indica que una situación eventual o hipotética no impide que ocurra el hecho.",
                    "Indica el comienzo de una acción o cuando ocurrirá.",
                ],
                "Preposición": [
                    "Preposición que indica el fin o término de una actividad, sea en sentido locativo, cronológico o cuantitativo.",
                    "Seguida de <i>cuando</i> o de un gerundio, preposición que indica valor inclusivo.",
                    "Seguida de <i>que</i>, preposición que indica valor exclusivo.",
                ],
                "Sustantivo": ["Grafía obsoleta de&nbsp;asta."],
            },
            [],
            [],
        ),
        (
            "hocico",
            ["[oˈsi.ko]", "[oˈθi.ko]"],
            ["De hocicar."],
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
            "hala",  # Important, it is mostly used to check for infinite loop in the Lua interpreter
            ["[ˈa.la]"],
            ["Incierta. Voz expresiva."],
            {"Interjección": ["Expresión para demandar prisa o sorpresa."]},
            ["halar"],
            [],
        ),
        (
            "los",
            ["[los]"],
            ["Del latín <i>illōs</i>, acusativo masculino plural del latín <i>ille</i>."],
            {
                "Artículo": ["Artículo determinado masculino plural. El singular es lo."],
                "Pronombre": [
                    "<i>Pronombre personal masculino de objeto directo (acusativo), tercera persona del plural.</i>."
                ],
            },
            [],
            ["le", "les", "se"],
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
            ["[ˈrwe.ɣ̞o]"],
            [],
            {"Sustantivo": ["Súplica, petición hecha con el fin de alcanzar lo que se pide."]},
            ["rogar"],
            [],
        ),
        (
            "también",
            ["[t̪amˈbjen]"],
            ["Compuesto de <i>tan</i> y <i>bien</i>"],
            {
                "Adverbio": [
                    "Utilizado para especificar que una o varias cosas son similares, o que comparten atributos con otra previamente nombrada.",
                    "Usado para añadir algo a lo anteriormente mencionado.",
                ]
            },
            [],
            [],
        ),
        (
            "uni-",
            ["[ˈu.ni]"],
            ["Del latín <i>uni-</i>, del latín <i>unus</i>."],
            {"Prefijo": ["Elemento compositivo que significa uno. un único, relativo a uno solo."]},
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
    definitions: list[Definitions],
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, "es")
    details = parse_word(word, code, "es", force=True)
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
