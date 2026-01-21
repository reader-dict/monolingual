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
        assert context.reset("fr")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "5E",
            [],
            [],
            [],
            {
                "Symbole": [
                    "Code AITA de la compagnie d’aviation SGA Airlines <i>(Siam General Aviation Company Limited</i>, บริษัท สยาม เจนเนอรัล เอวิเอชั่น จำกัด)."
                ]
            },
            [],
        ),
        (
            "-eresse",
            ["\\(ə).ʁɛs\\"],
            ["f"],
            [
                "Ce suffixe est né d’une coupe erronée du suffixe des mots comme <i>enchanteresse</i> et <i>pécheresse</i>. En effet, ces derniers sont en fait le cas sujet de mots en <i>-eur</i> auquel on a ajouté le suffixe féminisant <i>-esse</i> sous le schéma suivant :",
                '<table style="border: 1px solid black; border-collapse: collapse; font-size: inherit;"><tr><th style="border: 1px solid black; padding: 0.2em 0.4em;">cas sujet</th><th style="border: 1px solid black; padding: 0.2em 0.4em;">cas régime</th><th style="border: 1px solid black; padding: 0.2em 0.4em;">cas sujet + <i>-esse</i></th></tr><tr><td style="border: 1px solid black; padding: 0.2em 0.4em;">pechere</td><td style="border: 1px solid black; padding: 0.2em 0.4em;">pecheur</td><td style="border: 1px solid black; padding: 0.2em 0.4em;">pecheresse</td></tr><tr><td style="border: 1px solid black; padding: 0.2em 0.4em;">enchantere</td><td style="border: 1px solid black; padding: 0.2em 0.4em;">enchanteur</td><td style="border: 1px solid black; padding: 0.2em 0.4em;">enchanteresse</td></tr></table>',
                "Le suffixe a alors été confondu avec <i>-erece</i>, suffixe ancien français féminin de <i>-erez</i>, qui n’a rien laissé en français moderne directement (indirectement, on note <i>couperet</i> et <i>guilleret</i>, issus de confusions avec d’autres suffixes).",
                "<b>-eresse</b> a été très productif au Moyen Âge mais il subit depuis le XVI<sup>e</sup> siècle la concurrence du suffixe <i>-euse</i> qui l’a presque entièrement remplacé.",
            ],
            {
                "Suffixe": [
                    "Suffixe servant à former des mots féminins.<br/><b>Note : </b> Voir aussi au suffixe <i>-esse</i>."
                ]
            },
            [],
        ),
        (
            "a",
            ["\\a\\", "\\ɑ\\"],
            ["m"],
            [
                "<i>(Symbole 2)</i> Abréviation de <i><b>a</b>tto-</i>.",
                "<i>(Symbole 3)</i> Abréviation de <i><b>a</b>re</i>.",
                "<i>(Symbole 4)</i> <i>(Abréviation)</i> du latin <i><b>a</b>nnum</i> («&nbsp;année&nbsp;»).",
                "<i>(Symbole 6)</i> Abréviation de <i><b>a</b>ccélération</i>.",
            ],
            {
                "Caractère": [
                    "Première lettre et première voyelle de l’alphabet latin (minuscule). Unicode&nbsp;:&#32;U+0061.",
                    "Chiffre hexadécimal dix (minuscule).",
                ],
                "Symbole": [
                    "<i>(Linguistique)</i> Symbole de l’alphabet phonétique international pour la voyelle (ou vocoïde) ouverte antérieure non arrondie \\a\\.",
                    (
                        "<q><i>La voyelle /<b>a</b>/ est celle de l’article « la » dans la quasi-totalité des dialectes du français.</i></q>",
                    ),
                    "<i>(Métrologie)</i> Symbole du Système international (SI) pour le préfixe <b>atto-</b> (&times;10<sup>&minus;18</sup>).",
                    "<i>(Métrologie)</i> Symbole de l’<b>are</b>, une unité de mesure de surface en dehors SI. Elle prend souvent le préfixe h pour former ha (hectare).",
                    "<i>(Métrologie)</i> Symbole (dérivé du système SI) de l’<b>année</b> (365,25 jours de 86,4 ks), du latin <i>annum</i>.",
                    ("<q><i>Cette roche a été formée il y a 4 G<b>a</b>.</i></q>",),
                    "<i>(Chimie)</i> Symbole de l’activité chimique d’un composant.",
                    ("<i>a<sub>i</sub></i> : l'activité du corps <i>i</i>.",),
                    "<i>(Physique, Mécanique)</i> Symbole de l’accélération en tant que grandeur physique (uSI : mètre par seconde carré, m/s², m⋅s⁻² ; unité usuelle : g).",
                ],
                "Lettre": [
                    "Première lettre et première voyelle de l’alphabet français.",
                    (
                        "<q><i>Ceci est un <b>a</b> minuscule.</i></q>",
                        "<q><i>Le mot <i>anaérobie</i> contient deux <b>a</b>.</i></q>",
                        "<q><i>Je détestais, de même, que le <i><b>a</b></i> fût la première lettre de l’alphabet. Commencer par lui, c’était partir sur de mauvaises bases : le <i><b>a</b></i> constituait un être fermé, replié sur lui-même, qui ne se ressemblait en rien dès lors qu’il accédait au statut de majuscule, où sa prétention éclatait. Sa manière de poser, en tour Eiffel, son anguleuse hauteur, méprisante, annonçait que l’apprentissage de la lecture se ferait sous son magistère et dépendait de son bon vouloir. Je n’aimais pas, non plus, le mouvement de glotte qui correspondait à la prononciation du <i><b>a</b></i> ; bref, je l’avais pris en grippe et m’avisai que la bonne lettre, pour entrer en matière, était le <i>z</i>.</i></q> —&#160;(Yann Moix, <i>Orléans</i>, Grasset, « Le livre de poche », 2019, page 138)",
                    ),
                    "Le son \\a\\ ou \\ɑ\\ de cette lettre. <b>Note : </b> Le français parisien a perdu la distinction entre les deux.",
                    (
                        "<q><i><b>A</b> est antérieur dans <i>glace [ɡlas]</i> et postérieur dans <i>blâme [blɑm]</i>.</i></q>",
                    ),
                ],
                "Pronom": [
                    "<i>(Familier)</i> Pronom personnel (indéterminé en genre et en personne : première, deuxième ou troisième).",
                    (
                        "<q><i>D’abord, je m’en fous des araignées ! Ça me fait pas peur, j’en fait la collection, j’en ai plein un bocal, <b>a</b> se bouffent entre elles, je rigole !..</i></q> —&#160;(Jean-Marc Lelong, <i>Carmen Cru # 2 - La dame de fer</i>, 1985, éditions France Loisirs, Paris, page 30)",
                        "<i>Quoi qu’<b>a</b> dit ? – <b>A</b> dit rin.<br />Quoi qu’<b>a</b> fait ? – <b>A</b> fait rin.<br />À quoi qu’<b>a</b> pense ? – <b>A</b> pense à rin.<br/>Pourquoi qu’<b>a</b> dit rin ?<br />Pourquoi qu’<b>a</b> fait rin ?<br />Pourquoi qu’<b>a</b> pense à rin ?<br/>- <b>A</b>’xiste pas.</i>",
                    ),
                    "<i>(Québec)</i> <i>(Familier)</i> Elle.",
                    (
                        "<i>C’est lui qui, appréciant sa mère, d’un ton de médiocrité satisfaite, disait à Louise Guittard, en se frottant une bosse au front :<br/>— Pendant qu’<b>a</b> m’bat, on a la paix.</i>",
                        "<q><i>— Une môme, les mecs… Une môme ! Visez ! <b>A</b> l’est presque à poil !</i></q> —&#160;(Yves Gibeau, <i>Allons z’enfants</i>, 1952)",
                        "<i>C’était pendant l’congé d’Noël<br/>J’voulais déjà m’marier avec elle<br/><b>A</b> m’a appelé tantôt après les nouvelles.</i>",
                        "<q><i>Quand <b>a</b> l’ouvre la porte pis qu'<b>a</b> sort d’la scène, <b>a</b> l’arrête d’exister pour toi pis tu t’en sacres, d’abord que t’as écrit des belles scènes!</i></q> —&#160;(Michel Tremblay, <i>Le Vrai Monde?</i>, 1987)",
                        "<q><i>Ta mère est venue me voir en catastrophe. Au début, <b>a</b> voulait te laisser aller, mais ç’a pas été long qu’<b>a</b> l’a regretté.</i></q> —&#160;(Éric St-Pierre, <i>Rabaskabarnak</i>, Québec Amérique, 2019, page 100)",
                    ),
                ],
            },
            ["avoir"],
        ),
        (
            "π",
            [],
            [],
            [],
            {
                "Caractère": [
                    "Lettre minuscule grecque pi. Seizième lettre et onzième consonne de l’alphabet grec. Unicode : U+03C0."
                ],
                "Symbole": [
                    "<i>(Mathématiques)</i> Symbole représentant le rapport constant entre la circonférence d’un cercle et son diamètre, aussi appelé en français la <i>constante d’Archimède</i>.",
                    ("<q><b>π</b> &equals; 3,1415926…</q>",),
                    "<i>(Bases de données)</i> Symbole de la projection.",
                ],
            },
            [],
        ),
        (
            "42",
            ["\\ka.ʁɑ̃t.dø\\"],
            ["m", "s"],
            [],
            {
                "Numéral": [
                    "Numéral en chiffres arabes du nombre quarante-deux, en notation décimale. Selon la base utilisée, ce numéral peut représenter d’autres nombres. En notation hexadécimale, par exemple, ce numéral représente le nombre soixante-six ; en octal, le nombre trente-quatre.",
                    "<i>(Par ellipse)</i> <i>(Dans la plupart des langues)</i> Une année qui se termine par <b>42</b>.",
                ],
                "Nom": [
                    "Quarante-deux.",
                    ("<q><i>Le numéro gagnant est le <b>42</b>.</i></q>",),
                    "<i>(Par ellipse)</i> Une année qui se termine par <b>42</b>.",
                    ("<q><i>Elle a eu son bac en <b>42</b> (sous-entendu en 1942).</i></q>",),
                    "<i>(France)</i> <i>(Familier)</i> Habitant du département de la Loire.",
                    (
                        "<q><i>Les <b>42</b> de l’année dernière sont arrivés au camping et ont repris le même emplacement.</i></q>",
                    ),
                ],
                "Nom Propre": [
                    "<i>(France)</i> Département de la Loire.",
                    ("<q><i>J’habite dans le <b>42</b>.</i></q>",),
                ],
            },
            [],
        ),
        (
            "accueil",
            ["\\a.kœj\\"],
            ["m"],
            ["<i>(<small>XII</small><sup>e</sup> siècle)</i> Déverbal de <i>accueillir</i>."],
            {
                "Nom": [
                    "Cérémonie ou prestation réservée à un nouvel arrivant, consistant généralement à lui souhaiter la bienvenue et à l’aider dans son intégration ou ses démarches.",
                    (
                        "<q><i>Nous réservâmes aux nouveaux venus un <b>accueil</b> qui fut cordial et empressé, mais le temps n’était pas aux effusions et d’un commun avis, il fallait agir vite.</i></q> —&#160;(Jean-Baptiste Charcot, <i>Dans la mer du Groenland</i>, 1928)",
                        "<q><i>Partout elle avait trouvé bon <b>accueil</b>, prompt assentiment, mais elle se propose d’aller plus outre.</i></q> —&#160;(Jean Rogissart, <i>Passantes d’Octobre</i>, Librairie Arthème Fayard, Paris, 1958)",
                        "<q><i>Notre hôte, absent au moment de notre arrivée, ne tarde pas à paraître et me fait l’<b>accueil</b> auquel je m'attendais de sa part.</i></q> —&#160;(Frédéric Weisgerber, <i>Trois mois de campagne au Maroc : étude géographique de la région parcourue</i>, Paris : Ernest Leroux, 1904, page 38)",
                    ),
                    "Lieu où sont accueillies les personnes.",
                    ("<q><i>À l’<b>accueil</b>, ils t’expliqueront comment aller à son bureau.</i></q>",),
                    "<i>(Vieilli)</i> Fait d’accueillir ou héberger.",
                    (
                        "<q><i>Le Maire rappelle au conseil municipal que l’<b>accueil</b> périscolaire aura lieu à la rentrée de septembre 2008–2009 dans la salle de réunions et le petit local attenant.</i></q> —&#160;(Le Chesne, Conseil municipal du 27 juin 2008)",
                    ),
                    "Page d’accès ou d’accueil (lieu ci-dessus) à un site web.",
                    "Manière dont une œuvre a été acceptée lors de sa sortie par le public et les critiques.",
                ]
            },
            [],
        ),
        (
            "acrologie",
            ["\\a.kʁɔ.lɔ.ʒi\\"],
            ["f"],
            [
                "Du grec ancien ἄκρος, <i>akros</i> («&nbsp;extrémité&nbsp;»), voir <i>acro-</i>, avec le suffixe <i>-logie</i>."
            ],
            {
                "Nom": [
                    "<i>(Linguistique)</i> <i>(Rare)</i> Système graphique qui consiste à peindre, pour représenter les idées, l’image des objets dont le nom commence par la même lettre que celui par lequel ces idées sont exprimées dans le langage ordinaire.",
                    (
                        "<q><i>Le disque désigne donc le SOLEIL, le sceptre à tête de chacal, l’idée de GARDIEN, et le scarabée avec les trois traits au dessous, les MONDES. Or en égyptien, le chacal s’appelle ouônch et un gardien ourit. Ces deux mots commencent par la même lettre, ainsi il y a <b>acrologie</b>.</i></q> —&#160;(Julius Klaproth, <i>Lettre sur la découverte des hiéroglyphes acrologiques</i>, 1827, page 80)",
                    ),
                    "<i>(Linguistique)</i> <i>(Par extension)</i> <i>(Rare)</i> Se dit lorsque deux termes commencent par la même lettre et qu’ils sont apparentés par le sens.",
                    ("<q><i>Nature et Nèfle sont une <b>acrologie</b>.</i></q>",),
                    "<i>(Philosophie)</i> <i>(Très rare)</i> Recherche ou exposition des principes suprêmes, ou du mieux absolu.",
                    "<i>(Sport)</i> Étude ou pratique de l’acrobatie.",
                ]
            },
            [],
        ),
        (
            "-aux",
            ["\\o\\"],
            [],
            [
                "Ayant dans le passé la forme « -als », au cours du XII<sup>e</sup> siècle, le « l » précédant une autre consonne se modifia en « u », comme dans « colp – coup, altre – autre ». Étant suivi d'une consonne uniquement au pluriel, la terminaison « -als » pris la forme de « aus ». Le « x » provient des manuscrits, qui étaient extrêmement chers à l'époque, il va de soi qu'on voulut y mettre le plus de texte possible. S'inspirant du latin où « us » s'écrivait « x », on obtint ainsi la forme « -ax ». Le « u » vient s'ajouter plus tard pour s'accorder à la prononciation [o]."
            ],
            {"Suffixe": ["<i>Forme courante du pluriel de</i> -al."]},
            [],
        ),
        (
            "base",
            ["\\bɑz\\"],
            ["f"],
            ["Du latin <i>basis</i> («&nbsp;id.&nbsp;»), du grec ancien βάσις, <i>básis</i> («&nbsp;marche&nbsp;»)."],
            {
                "Nom": [
                    "Partie inférieure d’un corps quelconque qui lui sert de soutien.",
                    (
                        "<q><i>Si un édifice se renverse, n’essayez pas de le maintenir debout en jetant sur les murs une couche de ciment, mais empêchez-le de s’écrouler en renforçant la <b>base</b>.</i></q> —&#160;(Jean Déhès, <i>Essai sur l’amélioration des races chevalines de la France</i>, École impériale vétérinaire de Toulouse, Thèse de médecine vétérinaire, 1868)",
                        "<q><i>Les <b>bases</b> des tours visigothes sont carrées ou ont été grossièrement arrondies pour recevoir les défenses du V<sup>e</sup> siècle.</i></q> —&#160;(Eugène Viollet-le-Duc, <i>La Cité de Carcassonne, 1888</i>)",
                        "<q><i>Rarement un édifice plus laid fut élevé sur une place publique. […]. Il avait trop peu de <b>base</b> et trop de couronnement.</i></q> —&#160;(Pierre Louÿs, <i>La Ville plus belle que le monument</i>, dans <i>Archipel</i>, 1932)",
                    ),
                    "<i>(En particulier)</i> <i>(Architecture)</i> Ce qui soutient le fût de la colonne.",
                    (
                        "<q><i><b>Base</b> dorique.</i></q>",
                        "<q><i><b>Base</b> ionique.</i></q>",
                        "<q><i><b>Base</b> corinthienne.</i></q>",
                        "<q><i>Poser une colonne sur sa <b>base</b>.</i></q>",
                        "<i>Exemple d’utilisation manquant.</i> (Ajouter)",
                    ),
                    "<i>(Héraldique)</i> Désigne le piédestal d’une colonne surtout quand il est d’un émail différent de la colonne.",
                    (
                        "<q><i>De gueules flanqué en pal à dextre d’argent, à la rivière d’azur mouvant de la pointe brochant sur laquelle est posé un pont de trois arches mouvant du flanc dextre, ne laissant ainsi apparaître que les deux arches senestres, prolongé jusqu’au flanc senestre d’un empierrement, le tout d’or maçonné de sable, sommé d’une colonne aussi d’argent, la <b>base</b> et le chapiteau aussi d’or, le pont surmonté, sur le champ de gueules, de trois lionceaux d’or armés, lampassés et couronnés d’azur, qui est de Petit-Bersac</i></q>",
                    ),
                    "<i>(Géométrie)</i> Surface sur laquelle on conçoit que certains corps solides sont appuyés.",
                    (
                        "<q><i>La <b>base</b> d’une pyramide, d’un cylindre, d’un cône.</i></q>",
                        "<i>(Par extension)</i> Côté du triangle opposé à l’angle qui est regardé comme le sommet.",
                        ("<q><i>La <b>base</b> du triangle.</i></q>",),
                        "Côté d’une figure géométrique naturellement choisi comme côté principal.",
                        (
                            "<q><i>Pour trouver l’aire d’un parallélogramme, on multiplie sa <b>base</b> par sa hauteur.</i></q> —&#160;(aire d’un parallélogramme)",
                        ),
                    ),
                    "<i>(Arithmétique)</i> Nombre de chiffres utilisé pour dénombrer.",
                    (
                        "<q><i>Donnez la méthode pour passer de la <b>base</b> décimale à la <b>base</b> hexadécimale.</i></q> —&#160;(changement de base)",
                    ),
                    "<i>(Algèbre linéaire)</i> Famille libre de vecteurs, génératrice d’un espace vectoriel.",
                    (
                        "<q><i>On appelle <b>base</b> d’un espace vectoriel E, toute famille de vecteurs libre et génératrice de E</i></q> —&#160;(définition)",
                        "<q><i>La démonstration de l’existence d’une <b>base</b> pour un espace vectoriel de dimension infinie nécessite l’utilisation de l’axiome de choix.</i></q>",
                    ),
                    "<i>(Mathématiques)</i> Nombre réel élevé à une puissance.",
                    (
                        "<q><i>Fonction exponentielle de x, dans la <b>base</b> a</i></q> —&#160;(André Warin, « Fonction exponentielle de x, dans la base a » sur unisciel.fr)",
                    ),
                    "<i>(Par analogie)</i> <i>(Anatomie, Botanique)</i> Côté opposé à la partie la plus pointue d’un organe.",
                    (
                        "<q><i>La <b>base</b> du cœur, des poumons, etc.,</i></q>",
                        "<q><i>La <b>base</b> d’une feuille, d’un pétale, etc.</i></q>",
                    ),
                    "<i>(Géodésie)</i> Côté initial mesuré directement sur le terrain.",
                    (
                        "<q><i>Les <b>bases</b> qui ont servi à la triangulation de la France sont de douze kilomètres environ.</i></q>",
                    ),
                    "<i>(Militaire)</i> Ensemble des points de ravitaillement avec lesquels une armée en campagne se tient en relations constantes.",
                    ("<q><i><b>base</b> d’opérations.</i></q>", "<q><i>Couper une armée de ses <b>bases</b>.</i></q>"),
                    "<i>(Marine)</i> Port de ravitaillement ou de refuge des navires en temps de guerre.",
                    (
                        "<i>Faire des essais sur la <b>base</b>, courir sur la <b>base</b>,</i> se dit d’un Bâtiment qui doit parcourir dans un temps donné une distance déterminée à l’avance.",
                    ),
                    "<i>(Chimie)</i> Toute matière qui a la propriété de réagir aux acides et de les neutraliser, du moins en partie. Solution ayant un pH supérieur à 7.",
                    (
                        "<q><i>La plupart des <b>bases</b> ne sont que des oxydes métalliques.</i></q>",
                        "<q><i>La potasse la soude sont les deux <b>bases</b> les plus énergiques.</i></q>",
                        "<q><i>La <b>base</b> d’un sel.</i></q>",
                    ),
                    "<i>(Médecine)</i> Ce qui entre comme ingrédient principal dans un mélange.",
                    (
                        "<q><i>La <b>base</b> d’un médicament, d’une composition.</i></q>",
                        "<q><i>La <b>base</b> de ces pilules est l’aloès.</i></q>",
                    ),
                    "<i>(Génétique)</i> Base nucléique.",
                    ("<i>Exemple d’utilisation manquant.</i> (Ajouter)",),
                    "<i>(Télécommunications)</i> Appareil relié à une ligne fixe permettant le fonctionnement de téléphones sans fil à usage domestique.",
                    (
                        "<q><i>Les <b>bases</b> des téléphones sans fil offrent une couverture radio assez restreinte.</i></q>",
                    ),
                    "<i>(Électronique, Chimie des matériaux)</i> Nom d’une des électrodes d’un transistor bipolaire.",
                    (
                        "<q><i>Le transistor bipolaire est composé de trois zones appelées: émetteur, <b>base</b> et collecteur.La <b>base</b> est une fine zone dopée prise en sandwich entre deux zones dopées inversement.(…)L’émetteur (plus fortement dopé) envoie des charges électriques qui sont récupérées par le collecteur après avoir traversé la <b>base</b>.</i></q> —&#160;(Paolo Zanella, Yves Ligier, Emmanuel Lazard, <i>Architecture et technologie des ordinateurs</i>, 2018, page 139)",
                    ),
                    "<i>(Baseball)</i> Une des trois zones où le coureur peut rester sans être mis hors jeu.",
                    "<i>(Sports hippiques)</i> Cheval ou groupe de chevaux que l’on retient dans toutes ses combinaisons de paris hippiques pour une course donnée, car on estime qu’ils ont de très bonnes chances de figurer parmi les premiers.",
                    (
                        "<q><i>A 170 euros du recul, elle constitue une <b>base</b> incontournable.</i></q> —&#160;(<i>Le pronostic du Quinté PRIX PARIS TURF (PRIX DES LANDES)</i>, canalturf.com, 27/11/2008)",
                        "<q><i>Gagnez vos paris sur le Quinté avec nos <b>bases</b> de 2 chevaux et notre synthèse de 6 chevaux.</i></q> —&#160;(lesleaders.com)",
                    ),
                    "<i>(Politique)</i> Ensemble des électeurs, des soutiens d’un politique ou d’un parti.",
                    (
                        "<q><i>Ainsi Trump parlait-il à sa <b>base</b> quand il a joué la carte du « retour au boulot pour Pâques ». Tout comme il essayait de convaincre Wall Street et les grandes entreprises que le « business as usual » n’était pas loin.</i></q> —&#160;(Douglas Kennedy,&#32;<i>Douglas Kennedy : « Le capitalisme américain s’effondrera-t-il comme un château de cartes quand le Covid-19 sera dompté ? »</i>, <i>Le Monde</i>. Mis en ligne le 1<sup>er</sup>&nbsp;avril 2020)",
                    ),
                    "<i>(Sens figuré)</i> Ce qui est le principe, la donnée fondamentale d’une chose ou ce sur quoi elle repose.",
                    (
                        "<q><i>Ray, Montius, Scheuchzer, Micheli se sont les premiers occupés de l’<i>Agrostographie</i>. Tous ont à peu près suivi le même plan, et travaillé d’après les mêmes principes et sur les mêmes <b>bases</b>.</i></q> —&#160;(Ambrose-Marie-François-Joseph Palisot de Beauvois, <i>Essai d’une nouvelle agrostographie ou Nouveaux genres des graminées;</i>, 1812, page LI)",
                        "<q><i>Toute l’histoire classique est dominée par la guerre conçue héroï\xadquement ; les institutions des républiques grecques eurent, à l’origine, pour <b>base</b> l’organisation d’armées de citoyens ; […].</i></q> —&#160;(Georges Sorel, <i>Réflexions sur la violence</i>, chapitre V, <i>La grève générale politique</i>, 1908, page 231)",
                        "<q><i>La vaseline est la <b>base</b> la plus courante des pommades : on la rend plus adhésive en l’additionnant de lanoline […] qui absorbe plusieurs fois son poids d’eau.</i></q> —&#160;(Marcel Hégelbacher, <i>La Parfumerie et la Savonnerie</i>, 1924, page 134)",
                        "<q><i>En tant que concept politique, l’État-nation se caractérise par une autorité à <b>base</b> territoriale, et non par des conceptions universalistes, extra-territoriales.</i></q> —&#160;(Panayiotis Jerasimof Vatikiotis, <i>L’Islam et l’État</i>, 1987, traduction d’Odette Guitard, 1992, 1992)",
                        "<q><i>Quelques mois plus tard, […], ce mémorandum fut complété par un travail plus exhaustif qui pouvait servir de <b>base</b> à l’analyse gouvernementale de l’ensemble des relations entre le Chili et les USA.</i></q> —&#160;(Armando Uribe, <i>Le Livre noir de l’intervention américaine au Chili</i>, traduction de Karine Berriot et Françoise Campo, Seuil, 1974)",
                        "<q><i>Nous insistons sur les possibilités multi-plateformes de Python et présentons les <b>bases</b> pour étendre Python et l’intégrer dans d’autres applications en utilisant C ou Java.</i></q> —&#160;(Alex Martelli, <i>Python en concentré</i>, traduit par Éric Jacoboni, Paris : éditions O’Reilly, janvier 2004, page XI)",
                    ),
                    "<i>(Argot)</i> Cocaïne base.",
                ]
            },
            ["baser"],
        ),
        (
            "bath",
            ["\\bat\\"],
            ["m"],
            [
                "(<i>Adjectif, nom 1</i>) <i>(1846)</i> Origine discutée :",
                (
                    "soit de <i>Bath</i>, station thermale anglaise très prisée par la haute société au XVIII<sup>e</sup> siècle ; pour rendre compte de la forme <i>bath</i> ;",
                    "soit forme apocopée de l’argot <i>batif</i> (« joli ») , lui-même composé de <i>bat</i>, <i>battant</i>&#32;et <i>-if</i> dans le syntagme <i>battant neuf</i>, « fraîchement battu, tout neuf » ;",
                    "soit emploi adjectival de l’interjection onomatopéique <i>bath, bah</i> exprimant l’étonnement.",
                ),
                "Le nom du papier semble dérivé du sens « beau » plus que du nom de <i>Bath</i>, ville où l’on aurait fabriqué cette sorte de papier.",
                "(<i>Nom 2</i>) De l’hébreu בת, <i>bat</i>.",
            ],
            {
                "Adjectif": [
                    "<i>(Argot)</i> <i>(Désuet)</i> Super ; bon ; agréable.",
                    (
                        "<i>– C’est rien <b>bath</b> !<br/>– Mince alors, on en a de la chance !</i>",
                        "<i>– Je suis content… Et toi, Polyte, t’as plus mal au pied ?<br/>– Ah ! non ! … C’est trop <b>bath</b> !</i>",
                        "<q><i>T’es <b>bath</b>, la Caille. Ta peau, c’est du satin. J’suis folle ! Ta peau me brûle et tes mirettes… Oh ! tes mirettes !…</i></q> —&#160;(Francis Carco, <i>Jésus-la-Caille</i>, Deuxième partie, Le\xa0Mercure de\xa0France, Paris,\xa01914)",
                        "<q><i>— Pige-moi cet horizon, si c’est <b>bath</b> !</i></q> —&#160;(Jules Romains, <i>Les Copains</i>, 1922, réédition Le Livre de Poche, page 104)",
                        "<q><i>Vous êtes bien <b>bath</b>. Ça me plairait drôlement d’être comme vous. Vzêtes drôlement bien roulée. Et d’une élégance avec ça.</i></q> —&#160;(Raymond Queneau, <i>Zazie dans le métro</i>, Gallimard, 1959, chapitre 13)",
                        "<q><i>Pour tout bagage on a sa gueule<br/>Quand elle est <b>bath</b> ça va tout seul<br/>Quand elle est moche on s'habitue<br/>On s' dit qu'on est pas mal foutu</i></q> —&#160;(Léo Ferré, extrait de la chanson <i>Vingt ans</i>, 1961)",
                        "<i>Ainsi, défilèrent consécutivement les qualificatifs de </i>dément<i>, </i>délirant<i>, </i>chouette<i>, </i><b>bath</b><i>, et </i>pas mal<i>. On pouvait tout aussi bien dire d'une fille qu'elle était </i>chouette<i> et d'une capitale étrangère visitée à Pâques que c'était </i>pas mal.",
                        "<q><i>T'es OK, t'es <b>bath</b>, t'es in</i></q> —&#160;(Ottawan, <i>T'es OK</i>)",
                        "<q><i>Moi, j'adore les acteurs. J'adore les acteurs. C'est chouette les acteurs. C'est <b>bath</b> les acteurs. C'est eux qui traduisent tout quand même.</i></q> —&#160;(Jean Gabin, interviewé par Robert Chazal pour l'émission télévisée <i>Pour le cinéma</i>, 6 décembre 1970)",
                        "<q><i>Alors, la Marne, c’est <i><b>bath</b></i> ? » <b>Bath</b>, un mot des années 60 qu’on n’emploie plus. Peut-être l’a-t-il entendu prononcer par son père. Milan répond : « Oui, c’est très <b>bath</b>. »</i></q> —&#160;(Jean-Paul Kauffmann, <i>Remonter la Marne</i>, Fayard, 2013, Le Livre de Poche, page 197)",
                    ),
                ],
                "Nom": [
                    "Papier à lettre de provenance anglaise, de belle qualité, qui a joui d’une grande vogue au XIX<sup>e</sup> siècle.",
                    "Mesure des liquides chez les Hébreux, valant 18,08 litres puis plus tard environ 38,88 litres.",
                    (
                        "<i>Le <b>bath</b> représentait le cube de la demi-coudée royale, et était égal à l’épha, mesure de grains. On prétend qu’il y avait en outre un </i>petit <b>bath</b><i>, égal au cube de la demi-coudée naturelle = 2.507 gallons = 11.39 litres.<br/>Dans la suite, cette mesure augmenta de valeur, et, d’après le système philétérien, établi en Égypte sous les Ptolémées, le <b>bath</b> philétérien, ou petit artaba d’Alexandrie (qui était égal aux ¾ du métrétès ou grand artaba) forma la dixième partie du cor philétérien et se divisa en 3 sat ou séa = 6 hin = 72 log = 96 cadaa = 288 rébiites = 432 cos = 7.703 gallons = 35 litres. Mais la valeur de cette mesure paraît ne pas avoir été constante, et diffère d’après les divers auteurs qui en font mention. Fannius, dans son poème sur les mesures, dit que l’artaba est égal à 3 fois et ⅓ le modius romain, ce qui ferait seulement 28.8 litres. Josèphe, Apollinaire, saint Jérôme, etc., assignent au hin la capacité de 2 conges, ce qui fait pour le <b>bath</b> 12 conges ou 38.88 litres. Saint Épiphane dit que le hin est de 9 xestès, ce qui fait pour le <b>bath</b> 54 xestès ou 29.16 litres.</i>",
                    ),
                ],
            },
            [],
        ),
        (
            "Bogotanais",
            ["\\bɔ.ɡɔ.ta.nɛ\\"],
            ["m", "sp"],
            ["Du nom Bogota avec le préfixe -ais."],
            {
                "Nom": [
                    "Habitant de Bogota.",
                    (
                        "<q><i>Tous font le plein. Notamment le week-end, lors des mariages célébrés dans l’église baroque Santa Barbara et lors du traditionnel marché aux puces, rendez-vous dominical des <b>Bogotanais</b>.</i></q> —&#160;(« Bogota, capitale en or », <i>LePoint.fr</i>, 25 novembre 2011)",
                    ),
                ]
            },
            [],
        ),
        (
            "chacune",
            ["\\ʃa.kyn\\"],
            ["s"],
            [],
            {},
            ["chacun"],
        ),
        (
            "colligeait",
            ["\\kɔ.li.ʒɛ\\"],
            [],
            [],
            {},
            ["colliger"],
        ),
        (
            "corps portant",
            ["\\kɔʁ pɔʁ.tɑ̃\\"],
            ["m"],
            ["Locution composée de <i>corps</i>&#32;et de <i>portant</i>."],
            {
                "Nom": [
                    "<i>(Astronautique)</i> Aéronef à fuselage porteur, sur lequel la portance est produite par le fuselage, destiné aux usages spatiaux ou hypersoniques, afin de limiter l'effet de traînée ou la surface de friction.",
                    "<i>(Astronautique)</i> <i>(Aérodynamique)</i> Engin aérospatial possédant, à vitesse hypersonique, une portance qui lui assure une bonne manœuvrabilité lors de la rentrée atmosphérique.",
                ]
            },
            [],
        ),
        (
            "DES",
            [],
            ["m"],
            [
                "<i>(Commerce international)</i> <i>(1936)</i> Terme créé par la Chambre de commerce internationale. Sigle de l’anglais <i>delivered ex ship</i>; « rendu par navire ».",
                "<i>(Nom commun 1)</i> Sigle pour <b>d</b>i<b>é</b>thyl<b>s</b>tilbestrol.",
                "<i>(Nom commun 2)</i> Sigle.",
            ],
            {
                "Adverbe": [
                    "<i>(Commerce international)</i> Incoterm qui signifie que le vendeur a dûment livré sa marchandise dès lors que celle-ci, dédouanée à l’exportation et non à l’importation, est mise à disposition de l’acheteur à bord du navire, au port de destination convenu. Les frais de déchargement sont à la charge de l’acheteur."
                ],
                "Nom": [
                    "<i>(Biochimie)</i> Diéthylstilbestrol, un œstrogène de synthèse, source de graves complications chez les filles de ses utilisatrices.",
                    "<i>(Québec)</i> Diplôme d’études secondaires, un diplôme obtenu après cinq années d’études secondaires au Québec ; anciennement <i>Certificat d’études secondaires</i> (CES ou CÉS).",
                    "<i>(France)</i> Diplôme d’études spécialisées, un diplôme de troisième cycle médical, pharmaceutique, vétérinaire ou odontologique en France, d’une durée de 3 à 5 ans correspondant à l’Internat.",
                    "<i>(Belgique)</i> Diplôme d’études spécialisées, un diplôme de troisième cycle universitaire en Belgique.",
                    "<i>(France)</i> Diplôme d’études supérieures, un diplôme français.",
                    "<i>(Mathématiques)</i> Décomposition en éléments simples, une méthode de calcul mathématique.",
                ],
                "Symbole": ["<i>(Aviation)</i> Code AITA de l’aéroport de Desroches, aux Seychelles."],
            },
            [],
        ),
        (
            "dubitatif",
            ["\\dy.bi.ta.tif\\"],
            [],
            ["Du latin <i>dubitativus</i>."],
            {
                "Adjectif": [
                    "Qui sert à exprimer le doute.",
                    (
                        "<q><i>M. Cavard se réserve en donnant à sa phrase une forme <b>dubitative</b> qui ne trompe pas son auditeur.</i></q> —&#160;(Joseph Caillaux,&#32;<i>Mes Mémoires, I, Ma jeunesse orgueilleuse</i>,&#32;1942)",
                        "<q><i>Gui, se détournant à peine, entrevit les sourires de Berry et de Bourgogne, la lippe <b>dubitative</b> d'Orléans —&nbsp;qu'on n'avait guère vu car la rumeur courait qu'il fréquentait les bordeaux de la ville&nbsp;—, les lèvres pincées d'Olivier de Clisson.</i></q> —&#160;(Pierre Naudin,&#32;<i>Les fureurs de l'été</i>, éditions Aubéron,&#32;1999, page 328)",
                    ),
                    "Qui éprouve un doute.",
                    (
                        "<q><i>À Acy-Romance (Ardennes), la découverte de trois corps momifiés, inhumés en position dite de Boudha dans des petites fosses profondes de 80&nbsp;cm laissent les archéologues <b>dubitatifs</b>.</i></q> —&#160;(Bernard Rio,&#32;<i>L'arbre philosophal</i>, L’Age d’Homme,&#32;2001, page 267)",
                        "<q><i>Si je partage, pour une large part, le tableau de notre situation actuelle qui est présentée dans cet essai, je demeure en revanche plus circonspect, voire franchement <b>dubitatif</b>, devant certaines solutions proposées au problèmes de l’injustice.</i></q> —&#160;(Daniel D. Jacques,&#32;« Justice et liberté », dans <i>Argument</i>, n<sup>o</sup>&nbsp;1, automne-hiver 2017, vol.&nbsp;19, pages&nbsp;138)",
                        "<q><i>Si j’étais un artiste, je serais, disons, <b>dubitatif</b>.<br/>Pourquoi François Legault a refusé de rouvrir les salles de spectacle en novembre, alors que le directeur de la Santé publique disait qu’il n’y avait aucun problème à le faire ?</i></q> —&#160;(Richard Martineau,&#32;« Le bon flic Arruda et le mauvais flic Legault », dans <i>Le Journal de Québec</i>, 24 février 2021)",
                    ),
                ]
            },
            [],
        ),
        (
            "effluve",
            ["\\e.flyv\\"],
            ["mf"],
            [
                "Du latin <i>effluvium</i>, du préfixe <i>ex-</i> indiquant la séparation et de <i>fluxus</i> (« écoulement »)."
            ],
            {
                "Nom": [
                    "<i>(Médecine)</i> <i>(Vieilli)</i> Substances organiques altérées, tenues en suspension dans l’air, principalement aux endroits marécageux, et donnant particulièrement lieu à des fièvres intermittentes, rémittentes et continues.",
                    "Émanation qui se dégage d’un corps quelconque.",
                    (
                        "<q><i>Il ne reste qu’un tableau de Lebrun représentant la Pentecôte d’une façon qui étonnerait l’auteur des <i>Actes des apôtres</i>. La Vierge y est au centre et reçoit pour son compte tout l’<b>effluve</b> du Saint-Esprit, qui, d’elle, se répand sur les apôtres.</i></q> —&#160;(Ernest Renan, <i>Souvenirs d’enfance et de jeunesse</i>, 1883, collection Folio, page 153.)",
                        "<q><i>On entendait partout des chants d’oiseaux. Alors ma compagne se mit à courir en gambadant, enivrée d’air et d’<b>effluves</b> champêtres. Et moi je courais derrière en sautant comme elle. Est-on bête, monsieur, par moments !</i></q> —&#160;(Guy de Maupassant, <i>Au printemps</i>, dans <i>La maison Tellier</i>, 1891, collection Le Livre de Poche, page 213)",
                        "<q><i>Elle pourrait demeurer ici, l’assaillir d’invites, de chatteries, toute la nuit provoquer son désir, répandre ses <b>effluves</b>.</i></q> —&#160;(Jean Rogissart, <i>Passantes d’Octobre</i>, Librairie Arthème Fayard, Paris, 1958)",
                        "<q><i>Lors des manifestations au foyer rural, il traînait toujours dans les environs de la salle, les <b>effluves</b> festives l'ayant averti qu'il se tramait quelque chose d'intéressant et, aussitôt les gens ou les invités partis, il entrait prêter ses mains noires pour aider à débarrasser.</i></q> —&#160;(José Herbert, <i>La vie privée de Joint de Culasse</i>, dans <i>L'instituteur impertinent: récits</i>, Atria Témoignages/Primento, 2014)",
                        "<q><i>De chaque côté de la place, il y avait des tilleuls, qui pleuraient au printemps en nous arrosant de leurs <b>effluves</b> apaisants.</i></q> —&#160;(José Herbert, <i>L’instituteur impertinent: Récit de vie</i>, 2016)",
                    ),
                    "<i>(Physique)</i> Décharge électrique à faible dégagement de chaleur ayant lieu entre deux conducteurs dont la différence de potentiel n’est pas assez élevée pour engendrer un arc électrique. → voir <i>effluveur</i>",
                    (
                        "<q><i>Dans la plupart des cas, on observe une similitude d'effets entre les actions chimique dues à l’<b>effluve</b> et celles dues à l’étincelle.</i></q> —&#160;(Sous la direction de Ch. Friedel, <i>Dictionnaire de chimie pure et appliquée</i>, éd. Hachette, 1897.)",
                    ),
                ]
            },
            ["effluver"],
        ),
        (
            "employer",
            ["\\ɑ̃.plwa.je\\"],
            [],
            ["Du latin <i>implicāre</i> («&nbsp;impliquer&nbsp;»)."],
            {
                "Verbe": [
                    "Utiliser ; user ; se servir de.",
                    (
                        "<q><i>Le sucre était connu des anciens qui ne l’<b>employaient</b> qu'en très-petite quantité et comme médicament ; il y a 200 ans à peine, il se vendait seulement chez les pharmaciens, à un prix très-élevé.</i></q> —&#160;(Edmond Nivoit, <i>Notions élémentaires sur l’industrie dans le département des Ardennes</i>, E. Jolly, Charleville, 1869, page 119)",
                        "<q><i>On sait que l’emploi du fer fut inconnu de toute l’Amérique avant l’arrivée de Colomb. […]. Parfois cependant le fer météorique <b>est employé</b> accidentellement.</i></q> —&#160;(René Thévenin & Paul Coze, <i>Mœurs et Histoire des Indiens Peaux-Rouges</i>, Payot, 1929, 2<sup>e</sup>&nbsp;éd., p.18)",
                        "<q><i>Tant qu’il n’était pas appelé au loin par la guerre contre les Saxons, les Bretons, ou les Goths de la Septimanie, Chlother <b>employait</b> son temps à se promener d’un domaine à l’autre.</i></q> —&#160;(Augustin Thierry, <i>Récits des temps mérovingiens</i>, 1<sup>er</sup>&nbsp;récit : <i>Les quatre fils de Chlother Ier — Leur caractère — Leurs mariages — Histoire de Galeswinthe (561-568)</i>, 1833–1837)",
                        "<q><i>Ces cartouches sont destinées à remplacer les fortes charges de poudre-éclair qu'il serait nécessaire d’<b>employer</b> pour l’éclairage intensif d'intérieurs, de grottes, de mines, etc., […].</i></q> —&#160;(<i>Agenda Lumière 1930</i>, Paris : Société Lumière & librairie Gauthier-Villars, page 413)",
                        "<q><i>La Sandaraque impure des marchés arabes provient du Thuya et de divers Juniperus. On l’<b>emploie</b> en poudre pour arrêter les petites hémorragies de l’épistaxis.</i></q> —&#160;(<i>Bulletin des sciences pharmacologiques</i>, 1921, vol. 28, page 23)",
                    ),
                    "<i>(Spécialement)</i> <i>(Grammaire)</i> S’en servir en parlant ou en écrivant, en parlant d'une phrase, d'un mot ou d'une locution.",
                    (
                        "<q><i>Hervé de Scaër n’<b>employait</b> pas souvent les grands mots et s'il se servait d'une formule d’invocation presque solennelle, c'est que la situation l'y avait poussé.</i></q> —&#160;(Fortuné du Boisgobey, <i>Double-Blanc</i>, Paris : chez Plon & Nourrit, 1889, p. 173)",
                        "<q><i>La dernière fois cette salope de prof m'a retiré cinq points sous prétexte que j’<b>avais employé</b> le mot « très » sept fois dans la même phrase et que je le plaçais à des endroits inappropriés.</i></q> —&#160;(Shani Boianjiu, <i>Nous faisions semblant d'être quelqu'un d'autre</i>, traduit de l'anglais par Annick Le Goyat, Éditions Robert Laffont, 2014)",
                    ),
                    "Pourvoir d’une occupation ou d’un travail pour son usage ou pour son profit.",
                    (
                        "<q><i>Une seule usine, <b>employant</b> une vingtaine d'ouvriers, existe à Vatan et la main-d’œuvre masculine, hormis celle du bâtiment, se voit contrainte d'aller travailler dans les villes voisines.</i></q> —&#160;(Marc Michon, <i>Petite histoire de Vatan</i>, impr. Lecante, 1971, page 57)",
                        "<q><i>On l’a employé dans de grandes affaires, à de grandes négociations.</i></q>",
                        "<q><i>C’est un homme qui mérite d’être employé.</i></q>",
                        "<q><i>Il est employé dans les bureaux de tel ministère.</i></q>",
                    ),
                ]
            },
            [],
        ),
        (
            "encyclopædie",
            ["\\ɑ̃.si.klɔ.pe.di\\"],
            ["f"],
            ["→ voir <i>encyclopédie</i>"],
            {
                "Nom": [
                    "<i>(Archaïsme)</i> <i>Variante orthographique&#32;de</i>&nbsp;encyclopédie.",
                    (
                        "<q><i>Oint qu’on ne peut rien ſçavoir ſolidement ſans ſçavoir vn peu de tout\u2009, qui eſt cette <b>encyclopædie</b> : ne plus ni moins qu’on ne peut ſçavoir vne charte particuliere ſans avoir connoiſſance de la generale\u2009, & meſmes les païs voiſins.</i></q> —&#160;(auteur incertain, <i>Premiere Centvrie des Qvestions Traitees ez Conferences</i>, 1638)",
                        "<q><i>Ainſi\u200a, la Logique leur rend le reciproque par vne correſpondance mutuelle,\u2009comme l’on pourra encore mieux remarquer dans l’obſeruation generale de noſtre <b>Encyclopædie</b>.</i></q> —&#160;(auteur incertain, <i>La Science vniverselle de Sorel</i>, 1647)",
                        "<q><i>Nous ne doutons point qu’il n’y en ayt eu aſſez qui\u2009ont ſçeu qu’il faloit tenir vn compte exact de toutes les Diſciplines\u200a, afin que les Hommes viſſe\u200ant en peu de temps quelles pouuoient eſtre les richeſſes de leur Eſpirit, & qui pour y donner plus de facilité\u200a, ont taſché de reduire tant les Sciences que les Arts dans leurs\u200adependances & leurs limites, mais ils n’ont pas tous reuſſi à trouuer leurs correſpondances & leurs iuſteſſes : Voyons quels ſont ceux qui ayans donné vne eſtenduẽ generalle à leur ouurage\u200a, ont trouué la vraye forme d’vne <b>Encyclopædie</b>.</i></q> —&#160;(Charles Sorel, <i>De la Perfection de l’Homme</i>, 1655)",
                    ),
                ]
            },
            [],
        ),
        (
            "éperon",
            ["\\e.pʁɔ̃\\"],
            ["m"],
            [
                "De l’ancien français <i>esperon</i>, du vieux-francique <i>sporo</i>\xa0; apparenté notamment, dans les langues germaniques, à l’allemand <i>Sporn</i>, l’anglais <i>spur</i>, le néerlandais <i>spoor</i> et le suédois <i>sporre</i>."
            ],
            {
                "Nom": [
                    "<i>(Équitation)</i> Pièce de métal à deux branches, qui s’adapte au talon du cavalier et dont l’extrémité pointue ou portant une molette sert à piquer les flancs du cheval pour le stimuler.",
                    (
                        "<q><i>En effet, […], le cheval releva la tête et hennit comme pour annoncer son arrivée, et, cette fois, sans que son maître eût besoin de l’exciter ni de la parole ni de l’<b>éperon</b>, il redoubla d’ardeur, ….</i></q> —&#160;(Alexandre Dumas, <i>Othon l’archer</i>, 1839)",
                        "<q><i>Et, enfonçant les <b>éperons</b> dans les flancs de sa monture qui hennit de douleur, il partit à fond de train.</i></q> —&#160;(Gustave Aimard, <i>Les Trappeurs de l’Arkansas</i>, Éditions\xa0Amyot, Paris,\xa01858)",
                        "<q><i>Or çà, sans plus discourir, donnons de l’<b>éperon</b> à nos montures et dévorons ce ruban de queue qui s’étend devant nous, ennuyeux et grisâtre, entre deux rangées de manches à balai, sous la lueur froide de la lune.</i></q> —&#160;(Théophile Gautier, <i>Le capitaine Fracasse</i>, 1863)",
                        "<q><i>Toute proportion gardée, je pourrais comparer ce mouvement à celui du cheval qui vient de prendre, tout-à-coup, un violent coup d’<b>éperon</b> près de la sous-ventrière.</i></q> —&#160;(Dieudonné Costes & Maurice Bellonte, <i>Paris-New-York</i>, 1930)",
                    ),
                    "<i>(Botanique)</i> Prolongement en forme de tube de la corolle ou du calice (ne concerne parfois qu’un pétale ou sépale particulier).",
                    "<i>(Marine)</i> Partie de la proue d’un bâtiment qui se termine en pointe et qui a plus ou moins de saillie en avant.",
                    (
                        "<q><i>L’<b>éperon</b> supportait la figure qui donnait son nom au vaisseau.</i></q>",
                        "<q><i>L’<b>éperon</b> des galères antiques était armé de fer.</i></q>",
                    ),
                    "<i>(Maçonnerie)</i>",
                    (
                        "Sorte de fortification en angle saillant qu’on élève au milieu des courtines, ou devant des portes, pour les défendre.",
                        "Ouvrage en pointe qui sert à rompre le cours de l’eau, devant les piles des ponts, ou sur les bords des rivières.",
                        "Tout pilier qu’on construit extérieurement d’un mur de terrasse de distance en distance, et qui se lie avec le corps du mur pour tenir la poussée des terres (Contrefort, anciennement contre-fort).",
                    ),
                    "<i>(Géographie)</i> Partie d’un contrefort, d’une chaîne de collines ou de montagnes qui se termine en pointe.",
                    "<i>(Héraldique)</i> Meuble représentant l’objet du même nom dans les armoiries. Il est composé d’une branche en métal en U avec une tige au bout de laquelle se trouve une molette à six rais mais le nombre peut varier d'un illustrateur à l’autre. Il est représenté en pal, la molette vers le chef (haut). Dans les représentations anciennes, il est parfois muni d’une sangle en cuir. À rapprocher de molette d’éperon.",
                    (
                        "<q><i>D’azur, à trois <b>éperons</b> d’or, qui est de la commune de Lécluse du Nord</i></q> —&#160;(→ voir illustration « armoiries avec 3 éperons »)",
                    ),
                ]
            },
            [],
        ),
        (
            "greffier",
            ["\\ɡʁe.fje\\", "\\ɡʁɛ.fje\\"],
            ["m"],
            [
                "(<i>Nom commun 1</i>) Du latin <i>graphiarius</i> («&nbsp;d’écriture, de style, de poinçon&nbsp;») ou dérivé de <i>greffe</i>, avec le suffixe <i>-ier</i>.",
                "(<i>Nom commun 2</i>) Sans doute par jeu de mot avec <i>griffes</i> → voir <i>chat-fourré</i>.",
            ],
            {
                "Nom": [
                    "<i>(Droit)</i> Officier public préposé au greffe.",
                    (
                        "<q><i>Le <b>greffier</b> d’une juridiction qui rend une décision impliquant l’obligation pour une personne de s’immatriculer doit notifier cette décision au <b>greffier</b> du tribunal de commerce dans le ressort duquel l’intéressé a son siège ou son établissement principal.</i></q> —&#160;(Article L123-3, Code de commerce français)",
                        "<q><i>Le <b>greffier</b> est la personne responsable des services administratifs d'un tribunal. À ce titre, il remplit principalement des fonctions administratives qui vont de la préparation des audiences à la planification des agendas de la cour, la transcription des témoignages et la formation des jurés.</i></q> —&#160;(André Émond et Lucie Lauzière, <i>Introduction à l'étude du droit</i>, éditions Wilson & Lafleur, Montréal, 2005, page 198)",
                    ),
                    "<i>(Sens figuré)</i> Celui qui prend note et tient le registre de ses notes.",
                    (
                        "<q><i>L’Académie […] était partagée intellectuellement, comme elle l’a toujours été, entre la pensée de n’être que le <b>greffier</b> de l’usage, qui est sa pensée maîtresse, et un certain désir sourd d’en être un peu le guide, ce qui est, à mon avis, parfaitement légitime.</i></q> —&#160;(Émile Faguet, Simplification simple de l’orthographe, 1905)",
                    ),
                    "<i>(Populaire)</i> Chat.",
                    (
                        "<q><i>Dans le quartier même le mois le plus doux<br>Tu ne risques pas d’entendre miaou<br>Des <b>greffiers</b> mignons y en a plus bezef<br>Ils sont tous devenus terrine du chef.</i></q> —&#160;(Pierre Perret, <i>Le Tord-Boyaux</i>, 1963)",
                        "<i>Et là, c’est juste la grimace<br/>D’un matou sénile et pelé<br/>Mais ses yeux sont tellement zarbis<br/>Et son agonie si tranquille<br/>Que même les <b>greffiers</b>, par ici,<br/>Donnent l’impression d’être en exil.</i>",
                    ),
                    "Sexe de la femme, minou, chatte, etc.",
                    (
                        "<q><i>Elle avait pas tellement le choix, faut dire, question homme pour se faire encore régaler à son âge avec sa patte folle. Depuis qu'Albert faisait la fête à son <b>greffier</b>, elle s'efforçait de réparer l'outrage des ans sur sa frime...[...] toute la panoplie séductrice.</i></q> —&#160;(Alphonse Boudard, <i>Les combattants du petit bonheur</i>, La Table Ronde, 1977, réédition Le Livre de Poche, 1990, page 83.)",
                    ),
                    "Poisson-chat commun (poisson).",
                    ("<i>Exemple d’utilisation manquant.</i> (Ajouter)",),
                ]
            },
            [],
        ),
        (
            "ich",
            [],
            [],
            [],
            {"Symbole": ["<i>(Linguistique)</i> Code ISO 639-3 de l’etkywan."]},
            [],
        ),
        (
            "koro",
            ["\\kɔ.ʁo\\"],
            ["m"],
            [],
            {
                "Nom": [
                    "Langue tibéto-birmane parlée dans l’Arunachal Pradesh (Inde)",
                    "Langue malayo-polynésienne parlée dans les îles de l'Amirauté (Papouasie-Nouvelle-Guinée)",
                    "Forme d'hystérie de nature sexuelle propre aux humains mâles.",
                    (
                        "<q><i>Elles présentent la particularité de toucher exclusivement un sexe : l’amok ne touche que les hommes, et le latah que les femmes. Quant au <b>koro</b>, il est aussi réservé aux hommes, pour une raison évidente cette fois : il se définit par des troubles de la perception du pénis.</i></q> —&#160;(La Recherche, vol. 5, Société d'éditions scientifiques, 1974, p. 1058)",
                        "<q><i>A Singapour, en 1967, au moment même où la chute de la fécondité atteint sa vitesse maximale, se déclenche une épidemie de <i><b>Koro</b></i>, manifestation hystérique spécifiquement masculine. Les individus touchés craignent et perçoivent une rétraction de leur pénis, qui menace, disent-ils, de disparaître dans l'abdomen.</i></q> —&#160;(Emmanuel Todd, <i>Le Fou et le Prolétaire</i>, 1979, réédition revue et augmentée, Paris : Le Livre de Poche, 1980, page 22)",
                        "<q><i>Érigé en syndrome psychiatrique, le <i><b>koro</b></i> rassemble une nébuleuse de troubles que l'on retrouve très largement en Asie du Sud sous différentes variantes. […]. En Asie du Sud-Est, le <i><b>koro</b></i> donne lieu à de véritables épidémies collectives qui sévissent de manière périodique en Thaïlande, en Indonésie ou encore à Singapour.</i></q> —&#160;(Julien Bonhomme, <i>Les voleurs de sexe: anthropologie d'une rumeur africaine</i>, éd. du Seuil, 2009, chap.1, page 25)",
                    ),
                ]
            },
            [],
        ),
        (
            "mutiner",
            ["\\my.ti.ne\\"],
            [],
            ["Dénominal de <i>mutin</i>."],
            {
                "Verbe": [
                    "Se porter à la sédition, à la révolte.",
                    (
                        "<q><i>Des troupes <b>mutinées</b>.</i></q>",
                        "<i>(Absolument)</i> <i>Le peuple se <b>mutinait</b>.</i>",
                        "<q><i>Cet ordre rigoureux fit <b>mutiner</b> le peuple.</i></q>",
                    ),
                    "Enfant qui se dépite et manque à l’obéissance.",
                    ("<q><i>Cet enfant se <b>mutine</b> à chaque instant.</i></q>",),
                    "<i>(Poétique)</i> …",
                    ("<i>Les flots, les vents <b>mutinés</b>,</i> Les flots agités, les vents impétueux.",),
                ]
            },
            [],
        ),
        (
            "naguère",
            ["\\na.ɡɛʁ\\"],
            [],
            [
                "De <i>il n’y a guère</i> (de temps). À comparer avec le wallon «\xa0nawaire\xa0» (même sens). Voir aussi <i>na</i>."
            ],
            {
                "Adverbe": [
                    "<i>(Désuet)</i> Récemment ; il y a peu.",
                    (
                        "<q><i>A ce spectacle, tous les assistans attendris, émus, électrisés, quoique tous de différens cultes, volèrent dans les bras les uns des autres, et des larmes fraternelles coulèrent où <b>naguère</b> le fanatisme enflammoit tous les esprits et divisoit tous les cœurs.</i></q> —&#160;(« <i>Progrès de la tolérance</i> », dans <i>La Feuille villageoise</i>, n<sup>o</sup>&nbsp;32, du jeudi 3 mai 1792, Paris : Imprimerie Desenne, page 133)",
                        "<q><i>Le long de la route, notre conducteur nous dit avoir <b>naguère</b> rencontré un ours, le matin, dans la vallée d'Ossau.</i></q> —&#160;(Michelet, <i>Journal</i>, 1835, page 191)",
                    ),
                    "<i>(Désuet)</i> Peu de temps auparavant ; auparavant.",
                    (
                        "<q><i>Pons réchauffé reprit forme humaine : la couleur vitale revint aux yeux, la chaleur extérieure rappela le mouvement dans les organes, Schmucke fit boire à Pons de l’eau de mélisse mêlée à du vin, l’esprit de la vie s’infusa dans ce corps, l’intelligence rayonna de nouveau sur ce front <b>naguère</b> insensible comme une pierre.</i></q> —&#160;(Honoré de Balzac, <i>Le Cousin Pons</i>, 1847)",
                        "<q><i>Cette gamine vicieuse et prétentieuse est la fille d’une grosse commère qui tenait, <b>naguère</b>, une fruiterie dans les environs de Barbès.</i></q> —&#160;(Victor Méric, <i>Les Compagnons de l’Escopette</i>, Éditions de\xa0l’Épi, Paris,\xa01930, page\xa0198)",
                    ),
                    "Il y a longtemps. <b>Note : </b> contrairement à l’étymologie qui implique un temps passé récent, l’usage moderne consacre le sens d’un temps antérieur, lointain, révolu – possiblement par litote.",
                    (
                        "<q><i>Cette gamine vicieuse et prétentieuse est la fille d'une grosse commère qui tenait, <b>naguère</b>, une fruiterie dans les environs du Barbès.</i></q> —&#160;(Victor Méric, <i>Les Compagnons de l’Escopette</i>, Éditions de\xa0l’Épi, Paris,\xa01930, page\xa0198)",
                        "<q><i><b>Naguère</b>, la masse populaire, résignée à sa vie primitive, obscure, souvent sordide, n’avait point conscience d’être malheureuse.</i></q> —&#160;(Ludovic Naudeau, <i>La France se regarde&nbsp;: Le Problème de la natalité</i>, Librairie Hachette, Paris, 1931)",
                        "<q><i>En rentrant dans le giron de la nation française, Bordeaux, <b>naguère</b> capitale continentale du royaume d'Angleterre, subissait un dommage considérable.</i></q> —&#160;(Léon Berman, <i>Histoire des Juifs de France des origines à nos jours</i>, 1937)",
                        "<i>Un des slogans des </i>économies autarciques<i> (on disait <b>naguère</b> </i>économies fermées<i>) est :</i> Ne rien perdre.",
                        "<q><i>Car les écrits modernes sont beaucoup plus nombreux que <b>naguère</b>, et on les trouve dans beaucoup plus de styles.</i></q> —&#160;(Anne-Marie Beaudouin-Bégin, <i>La langue affranchie, se raccommoder avec l’évolution linguistique</i>, Québec, Éditions Somme toute, 2017, page 100.)",
                    ),
                ]
            },
            [],
        ),
        (
            "pinyin",
            ["\\pin.jin\\"],
            ["m"],
            [
                "<i>(Nom 1)</i> (Vers 1950) Du chinois 拼音, <i>pīnyīn</i>, composé de 拼, <i>pīn</i> («&nbsp;épeler&nbsp;»)&#32;et de 音, <i>yīn</i> («&nbsp;son&nbsp;»).",
                "<i>(Nom 2)</i> De l’anglais <i>Pinyin</i>.",
            ],
            {
                "Nom": [
                    "Systèmes de transcription de différentes langues, permettant de romaniser les sons des sinogrammes, et d’indiquer le ton utilisé lors de la prononciation. Le hanyu pinyin sert à la transcription du mandarin standard.",
                    "<i>(Linguistique)</i> Langue bantoïde parlée dans la Région du Nord-Ouest au Cameroun.",
                ]
            },
            [],
        ),
        (
            "précepte",
            ["\\pʁe.sɛpt\\"],
            ["m"],
            [
                "Emprunté au latin <i>praeceptum</i> («&nbsp;précepte, leçon, règle&nbsp;»), dérivé de <i>praecipere</i> signifiant « prendre avant, prendre le premier » ou encore « recommander », « conseiller », « prescrire »."
            ],
            {
                "Nom": [
                    "Règle ; leçon ; enseignement.",
                    "Règle morale ou religieuse.",
                    "<i>(Philosophie)</i> Ce qui ne peut pas ne pas être autrement.",
                    "<i>(Religion)</i> Commandement et, surtout, commandement de Dieu, ou commandement de l’Église, etc.",
                ]
            },
            [],
        ),
        (
            "rance",
            ["\\ʁɑ̃s\\"],
            ["mf", "m"],
            ["Du latin <i>rancidus</i> par l’intermédiaire de l’ancien occitan."],
            {
                "Adjectif": [
                    "Se dit des corps gras qui, laissés au contact de l’air, ont pris une odeur forte et un goût désagréable.",
                    "<i>(Sens figuré)</i> Qui s’est encore envenimé.",
                    "<i>(Sens figuré)</i> <i>(Péjoratif)</i> Méprisable.",
                ],
                "Nom": ["Goût et odeur désagréable, en parlant de corps gras.", "<i>Variante&#32;de</i>&nbsp;ranche."],
            },
            ["rancer"],
        ),
        (
            "sapristi",
            ["\\sa.pʁis.ti\\"],
            [],
            ["Déformation de <i>sacristi</i>, afin de ne pas blasphémer ouvertement."],
            {
                "Interjection": [
                    "<i>(Familier)</i> <i>(Par euphémisme)</i> <i>(Vieilli)</i> Pour marquer l’étonnement ou l'énervement."
                ]
            },
            [],
        ),
        (
            "silicone",
            ["\\si.li.kon\\"],
            ["f", "m"],
            [
                "<i>(1863)</i> De l’allemand <i>Silikon</i>, mot créé par Friedrich Wöhler et, pour les équivalents français du mot allemand, dérivé de <i>silicium</i>, avec le suffixe <i>-one</i>."
            ],
            {
                "Nom": [
                    "<i>(Chimie)</i> Composé inorganique formés d’une chaine silicium-oxygène (ou siloxane) […-Si-O-Si-O-Si-O-…] dans laquelle des groupes [R] se fixent, sur les atomes de silicium.",
                    "<i>(Par extension)</i> Mastic à base de ce composé et vendu généralement en cartouche.",
                    (
                        "<i>(Par extension)</i> Toutes sortes de mastics vendu en cartouche et ce indépendamment de sa composition.",
                    ),
                ]
            },
            ["siliconer"],
        ),
        (
            "suis",
            ["\\sɥi\\"],
            [],
            [],
            {},
            ["suivre", "être"],
        ),
        (
            "venoient",
            [],
            [],
            [],
            {
                "Verbe": [
                    "<i>Ancienne forme de la troisième personne du pluriel de l’indicatif imparfait du verbe</i> venir (on écrit maintenant <i>venaient</i>)."
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
    code = page(word, "fr")
    details = parse_word(word, code, "fr", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert definitions == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants
