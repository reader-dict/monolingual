"""
Arabiser: manual conversion of Module:arabe from
https://fr.wiktionary.org/wiki/Module:arabe

Current version: 12 juillet 2025 07:43
    https://fr.wiktionary.org/w/index.php?title=Module:arabe&oldid=38396854

"""

import re
import unicodedata

from .racines_arabes import racines_schemes_arabes

U = chr

en_arabe = {
    "0": U(0x660),
    "1": U(0x661),
    "2": U(0x662),
    "M": U(0x663),  # 3 est pris par le 3ain... avec imagination on bascule le 3 pour faire un m
    "4": U(0x664),
    "5": U(0x665),
    "6": U(0x666),
    "7": U(0x667),
    "8": U(0x668),
    "9": U(0x669),
    " ": " ",  # blancs entre mots
    "(": "(",  # parenthèse
    ")": ")",  # parenthèse
    "_": "",  # underscore ignoré pour décontextualisation éventuelle
    U(0x61B): U(0x61B),  # point virgule arabe
    ";": U(0x61B),
    U(0x60C): U(0x60C),  # virgule inversée
    ",": U(0x60C),
    U(0x61E): U(0x61E),  # trois points
    U(0x61F): U(0x61F),  # point d'interrogation
    "?": U(0x61F),
    "!": "!",  # exclamation
    U(0x621): U(0x621),  # Hamza
    "ò": U(0x654),  # Hamza suscrite
    "`": U(0x621),
    "'": U(0x621),
    "‘": U(0x621),
    "ʾ": U(0x621),
    "ʼ": U(0x621),
    "ˈ": U(0x621),
    U(0x671): U(0x671),  # Alif wasla
    "^": U(0x671),
    U(0x622): U(0x622),  # Alif madda
    "~": U(0x622),
    U(0x623): U(0x623),  # Alif hamza
    "à": U(0x623),
    U(0x624): U(0x624),  # Waw hamza
    "ù": U(0x624),
    U(0x625): U(0x625),  # Alif hamza souscrite
    "è": U(0x625),
    U(0x626): U(0x626),  # Ya hamza
    "ì": U(0x626),
    U(0x627): U(0x627),  # Alif
    "A": U(0x627),
    "â": U(0x64E) + U(0x627),  # diacritique intégré
    "ā": U(0x64E) + U(0x627),  # diacritique intégré
    "e": U(0x627),  # permet d'écrire "el-"
    U(0x628): U(0x628),  # Ba
    "b": U(0x628),
    U(0x629): U(0x629),  # Ta marbouta
    "@": U(0x629),
    U(0x62A): U(0x62A),  # Té
    "t": U(0x62A),
    U(0x62B): U(0x62B),  # Thé
    "θ": U(0x62B),
    "ṯ": U(0x62B),
    "F": U(0x62B),
    U(0x62C): U(0x62C),  # Djim
    "ʒ": U(0x62C),
    "ǧ": U(0x62C),
    "j": U(0x62C),
    "g": U(0x62C),
    U(0x62D): U(0x62D),  # Ha
    "ḥ": U(0x62D),
    "ħ": U(0x62D),
    "ḩ": U(0x62D),
    "H": U(0x62D),
    U(0x62E): U(0x62E),  # Kha
    "ḵ": U(0x62E),
    "ẖ": U(0x62E),
    "ḫ": U(0x62E),
    "x": U(0x62E),
    "X": U(0x62E),
    "K": U(0x62E),
    U(0x62F): U(0x62F),  # Dal
    "d": U(0x62F),
    U(0x630): U(0x630),  # Dhal
    "ð": U(0x630),
    "ḏ": U(0x630),
    "V": U(0x630),
    U(0x631): U(0x631),  # Ra
    "r": U(0x631),
    U(0x632): U(0x632),  # Zain
    "z": U(0x632),
    U(0x633): U(0x633),  # Sîn
    "s": U(0x633),
    U(0x634): U(0x634),  # Chîn
    "ʃ": U(0x634),
    "š": U(0x634),
    "c": U(0x634),
    "C": U(0x634),
    U(0x635): U(0x635),  # Çad
    "ṣ": U(0x635),
    "ş": U(0x635),
    "S": U(0x635),
    "ç": U(0x635),
    "Ç": U(0x635),
    U(0x636): U(0x636),  # Dad
    "ḍ": U(0x636),
    "ḑ": U(0x636),
    "D": U(0x636),
    U(0x637): U(0x637),  # Ta
    "ṭ": U(0x637),
    "ţ": U(0x637),
    "T": U(0x637),
    U(0x638): U(0x638),  # Zza
    "ẓ": U(0x638),
    "Z": U(0x638),
    U(0x639): U(0x639),  # Rain
    "ʕ": U(0x639),
    "ʿ": U(0x639),
    "ʻ": U(0x639),
    "3": U(0x639),
    U(0x63A): U(0x63A),  # Ghain
    "ɣ": U(0x63A),
    "ḡ": U(0x63A),
    "ğ": U(0x63A),
    "ġ": U(0x63A),
    # "g": U(0x63A),
    "R": U(0x63A),
    U(0x640): U(0x640),  # tiret
    "-": U(0x640),
    U(0x641): U(0x641),  # Fa
    "f": U(0x641),
    U(0x642): U(0x642),  # Qaf
    "q": U(0x642),
    U(0x643): U(0x643),  # Kaf
    "k": U(0x643),
    U(0x644): U(0x644),  # Lam
    "l": U(0x644),
    U(0x645): U(0x645),  # Mîm
    "m": U(0x645),
    U(0x646): U(0x646),  # Noun
    "n": U(0x646),
    U(0x647): U(0x647),  # Hé
    "h": U(0x647),
    U(0x648): U(0x648),  # Waw
    "U": U(0x648),
    "w": U(0x648),
    "W": U(0x648),
    "û": U(0x64F) + U(0x648),  # préfixage du diacritique
    "ū": U(0x64F) + U(0x648),  # préfixage du diacritique
    U(0x649): U(0x649),  # Alif maksoura
    "é": U(0x649),
    U(0x64A): U(0x64A),  # Ya
    "I": U(0x64A),
    "y": U(0x64A),
    "Y": U(0x64A),
    "î": U(0x650) + U(0x64A),
    "ī": U(0x650) + U(0x64A),
    U(0x64B): U(0x64B),  # Fathatan
    "ã": U(0x64B),
    U(0x64C): U(0x64C),  # Dammatan
    "ũ": U(0x64C),
    "õ": U(0x64C),
    U(0x64D): U(0x64D),  # Kasratan
    "ĩ": U(0x64D),
    "ñ": U(0x64D),
    U(0x64E): U(0x64E),  # Fatha
    "a": U(0x64E),
    U(0x64F): U(0x64F),  # Damma
    "u": U(0x64F),
    U(0x650): U(0x650),  # Kasra
    "i": U(0x650),
    U(0x651): U(0x651),  # Chadda
    "²": U(0x651),
    U(0x652): U(0x652),  # Soukoun
    "°": U(0x652),
    U(0x66D): U(0x66D),  # *
    "*": U(0x66D),
    U(0x670): U(0x670),  # Alif suscrit
    "E": U(0x670),
    # Lettres additionnelles diverses
    "p": U(0x67E),  # pa
    "v": U(0x06A4),  # ve
    "B": U(0x06A5),  # ve algérien
    "J": U(0x0686),  # tch perse
    "£": U(0x0653),  # madda arabe en chef
}


def arabiser(texte: str) -> str:
    """
    >>> arabiser("rajulâã")
    'رَجُلَاًا'

    >>> arabiser("mu'ad²ibũ")
    'مُؤَدِّبٌ'
    >>> arabiser("ad²aba")
    'أَدَّبَ'
    >>> arabiser("elHasan_")
    'الحَسَن'
    >>> arabiser("zabala")
    'زَبَلَ'
    >>> arabiser("izballa")
    'إِزْبَلَّ'
    >>> arabiser("d")
    'د'
    >>> arabiser("qanTara")
    'قَنْطَرَ'

    >>> arabiser("qur'ân")
    'قُرْآنْ'
    >>> arabiser("a'mana")
    'آمَنَ'
    >>> arabiser("aelVakarayni")
    'أَالْذَكَرَيْنِ'
    >>> arabiser("hay'@")
    'هَيْءَة'
    >>> arabiser("cifâ'ã")
    'شِفَاءًا'

    >>> arabiser("ra''asa")
    'رَأَّسَ'
    >>> arabiser("ru''isa")
    'رُئِّسَ'

    >>> arabiser("katabâ")
    'كَتَبَا'
    >>> arabiser("maktûb")
    'مَكْتُوبْ'
    >>> arabiser("kattaba")
    'كَتَّبَ'
    >>> arabiser("katabû")
    'كَتَبُو'
    >>> arabiser("katabûA")
    'كَتَبُوا'
    >>> arabiser("elkalb")
    'الكَلْبْ'

    # FIXME: The test below should output 'الرُّمْ'
    >>> arabiser("elrum")
    'الرُمْ'

    # FIXME: The test below should output 'اللَّمَدْ'
    >>> arabiser("ellamad")
    'الَّمَدْ'

    # FIXME: The test below should output 'الأَمَدْ'
    >>> arabiser("elamad")
    'الَمَدْ'

    >>> arabiser("Xalîfâ@")
    'خَلِيفَاة'
    >>> arabiser("kitabũ")
    'كِتَبٌ'
    >>> arabiser("kitabã")
    'كِتَبًا'
    >>> arabiser("kitabĩ")
    'كِتَبٍ'
    >>> arabiser("zawé")
    'زَوَى'

    >>> arabiser("'ir")
    'إِرْ'
    >>> arabiser("arbi")
    'أَرْبِ'
    >>> arabiser("'arbi")
    'أَرْبِ'

    >>> arabiser("cuìûn")
    'شُئُونْ'
    >>> arabiser("cu'ûn")
    'شُؤُونْ'

    >>> arabiser("k_t_b_")
    'كتب'
    >>> arabiser("ktb")
    'كتب'

    >>> arabiser("elmubdi'u wa elmu3îdu")
    'المُبْدِئُ وَ المُعِيدُ'

    >>> arabiser("famu ^lHûti")
    'فَمُ ٱلحُوتِ'
    """
    # translittération en arabe du paramètre, suivant l'assoc-liste en_arabe.
    texte = f" {texte} "

    # on rajoute un blanc devant et derrière pour uniformiser les tests de début et fin de mot
    transcription = ""
    a_traiter = ""

    # à faire un jour : transformer tous les ² en redoublements explicites avant traitement
    # à faire un jour : reporter sur la lettre attendue toutes les lettres équivalentes admissibles
    diacritiques = any(char in texte for char in {"a", "i", "u", "â", "î", "û", "ã", "ĩ", "ũ", "°"})
    for curseur in range(1, len(texte) - 1):
        a_traiter = texte[curseur]
        # orthographe différente suivant qu'on est en "début" ou en milieu de mot.
        # début de mot
        if (
            # précédé d'un blanc = début de mot
            texte[curseur - 1] == " "
            # blanc souligné précédé d'un blanc = début de mot
            or texte[curseur - 1 : curseur] == " _"
            # derrière el- il faut écrire comme en début de mot malgré la liaison :
            # idem derrière particules inséparables
            or (
                curseur > 1
                # pb spécifique de bi'r
                and texte[curseur - 3 : curseur + 1] != "bi'r"
                # On regarde ce qu'il y avait trois caractères avant
                and texte[curseur - 2 : curseur] == "el"  # normalement le "e" n'apparaît que pour le "el" préfixe
                and texte[curseur - 3 : curseur] in {" ^l", " bi", " fa", " ka", " la", " li", " sa", " wa"}
            )
            # idem si plusieurs particules séparées par un blanc souligné
            or (
                curseur > 1
                and texte[curseur - 3 : curseur] in {"_el", "_^l", "_bi", "_fa", "_ka", "_la", "_li", "_sa", "_wa"}
            )
            # -- un blanc souligné permet de couper le mot s'il faut forcer un fa'tu en fa_'tu par exemple
            or (
                curseur > 1
                and texte[curseur - 3 : curseur] in {"el_", "^l_", "bi_", "fa_", "ka_", "la_", "li_", "sa_", "wa_"}
            )
        ):
            # le curseur est en début de mot, indépendamment du préfixe
            # Si le début du mot est une voyelle il faut insérer en amont une hamza préfixe
            # Mais il faut intercepter en amont les cas du alif madda,
            # Mais c'est plus facile à traiter si on traite d'abord normalement les cas de type a & hamza & voyelle :
            # Pour ça, on regarde les trois premiers caractères à partir du courant :
            debut = texte[curseur : curseur + 3]
            if debut in {"a'i", "a'î", "a'u", "a'û", "a'a", "a'â"}:
                # il y aura superposition d'une hamza instable et d'une hamza structurelle portant voyelle
                transcription += U(0x623) + U(0x64E)  # alif hamza + fatha
                # ... et la hamza suivante sera traitée par le cas général.

            # Traitement à présent des cas où il faut un alif madda
            # débuts de la forme a & hamza (donc sans voyelle, puisque interceptées précédemment), ou hamza & â, ou â :
            elif texte[curseur : curseur + 2] in {"a'", "'â"} or a_traiter == "â":
                transcription += U(0x622)  # alif madda

            # Traitement de la hamza explicite en début de mot
            elif a_traiter == "'":  # hamza explicite en début de mot
                suivant = texte[curseur + 1]
                if suivant == "â":
                    transcription += U(0x622)  # alif madda
                elif suivant in {"a", "u", "û"}:
                    transcription += U(0x623)  # support en haut
                elif suivant in {"i", "î"}:
                    transcription += U(0x625)  # support en bas
                elif suivant == " ":
                    transcription += U(0x621)  # hamza isolée
                else:
                    transcription += U(0x627)  # par défaut, alif
                # hamza explicite en début de mot, la hamza préfixe a été insérée, la voyelle suivante sera transcrite ensuite

            # Il faut rajouter la lettre courante à la transcription.
            else:
                # Mais d'abord si c'est une voyelle, on met une hamza préfixe
                if a_traiter in {"a", "u", "û"}:
                    # le â est un cas à part traité précédemment
                    transcription += U(0x623)  # support en haut
                elif a_traiter in {"i", "î"}:
                    transcription += U(0x625)  # support en bas
                # la hamza préfixe a été insérée, le reste suit.

                # Ensuite si on est sur le "e" d'une structure de type "liel" en début de mot,
                # elle s'écrit sans alif donc il faut sauter le "e" et passer à la lettre suivante :
                if texte[curseur - 3 : curseur + 1] != "liel":
                    transcription += en_arabe[a_traiter]

            # end cas hamza préfixe à insérer.

            # post-traitement : si la consonne est derrière el (ou ^l) il faut rajouter un chadda aux lettres solaires
            # il faut que le "el" soit collé au mot, donc une forme comme el_sadatu supprime le chadda. Faut pas pousser.
            if (
                texte[curseur - 1] == "l"
                and texte[curseur - 2] in {"e", "^"}
                # faire le test solaire
                and (
                    a_traiter in {"t", "F", "d", "V", "r", "z", "s", "C", "S", "D", "T", "Z", "l", "n"} and diacritiques
                )
            ):
                transcription += en_arabe["²"]

        # on n'est pas en début de mot
        else:
            # Ne présentent jamais de redoublement :
            if a_traiter in {"a", "i", "u", "e", "^", "î", "A", "I", "U", "E", "É", "ĩ", "ũ", "õ", "_"}:
                transcription += en_arabe[a_traiter]

            elif a_traiter == "é":
                if texte[curseur - 1] not in {"ã", "_", "E", "~"} and diacritiques:
                    transcription += en_arabe["a"]
                transcription += en_arabe[a_traiter]

            # cas particulier d'un u final : alif muet
            elif a_traiter == "û":
                # plus simple de ne pas le mettre.
                transcription += en_arabe[a_traiter]
                # if (mw.ustring.sub( texte, curseur+1, curseur+1 ) == " ")
                # then transcription = transcription .. en_arabe["e"] end

            # ne pas rajouter un "a" s'il y en a déjà un avant.
            elif a_traiter == "~":
                if diacritiques and texte[curseur - 1] != "a":
                    transcription += en_arabe["a"]
                transcription += en_arabe["~"]

            # Traitement des différents cas particuliers dépendants du contexte
            elif a_traiter == "ã":
                # le ã est suivi d'un alif muet, mais pas derrière ât et @ :
                transcription += en_arabe[a_traiter]
                if (
                    texte[curseur - 1] == "@"
                    or texte[curseur - 2 : curseur] == "ât"
                    or texte[curseur + 1]
                    in {
                        "é",
                        # ni devant une hamza précédé d'une voyelle longue
                        "â'",
                        "î'",
                        "û'",
                        # et si on veut le neutraliser on met un blanc souligné
                        "_",
                    }
                ):  # skip
                    pass
                else:
                    transcription += en_arabe["A"]

            elif a_traiter == "â":
                if (
                    # pas de nouvel alif derrière une hammza portée par alif
                    texte[curseur - 1] == "'"
                    # mais si un petit malin a codé deux hamza de suite...
                    and texte[curseur - 2] != "'"
                ):
                    avant = texte[curseur - 2]
                    if avant == "'":
                        avant = texte[curseur - 3]
                    if avant in {"i", "î", "I", "y", "u", "û", "w", "â"}:
                        transcription += en_arabe["â"]
                    # sinon : la hamza a déjà inséré un alif madda et on ne fait rien
                else:
                    transcription += en_arabe["â"]

            elif a_traiter == "@":
                # ta arbouta : précédé de 'a' implicite, sauf quand derrière une voyelle longue
                if texte[curseur - 1] not in {"â", "î", "û", "_"} and diacritiques:
                    transcription += en_arabe["a"]
                transcription += en_arabe["@"]

            elif a_traiter == "é":
                # alif maksoura : précédé de 'a' implicite, sauf quand devant un 'ã' ou quand on efface les voyelles
                if texte[curseur + 1] != "ã" and texte[curseur - 1] != "_":
                    transcription += en_arabe["a"]
                transcription += en_arabe["é"]

            # Quelques cas où on ne veut pas examiner la présence d'un ²
            elif a_traiter == "°":  # Sukun explicite
                transcription += en_arabe["°"]

            elif a_traiter in {"*", "."}:
                transcription += en_arabe["*"]

            # Lettre redoublée de la précédente :
            elif a_traiter == texte[curseur - 1] and a_traiter != "-" and diacritiques:
                # pas de gemmination sur les tirets
                # Pas de gemmination si on est derrière un el- préfixe (el-lah)
                # mais dans ce cas le second l est traité comme début de mot : pas cette branche.
                transcription += en_arabe["²"]

            elif a_traiter == "'":  # hamza
                # Hamza : problème du support
                avant = texte[curseur - 1]
                apres = texte[curseur + 1]

                # insertion d'un sukun si nécessaire
                if (
                    avant
                    not in {
                        "a",
                        "e",
                        "i",
                        "u",
                        "â",
                        "î",
                        "û",
                        "é",
                        "ã",
                        "ĩ",
                        "ñ",
                        "É",
                        "A",
                        "I",
                        "U",
                        "E",
                        "ñ",
                        "õ",
                        "-",
                        "~",
                        ",",
                        "_",
                        "°",
                        "^",
                        "(",
                        ")",
                        "!",
                        " ",
                        ",",
                        "0",
                        "1",
                        "2",
                        "M",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                    }
                    and texte[curseur - 3 : curseur]
                    not in {
                        # pas de sukun après el- en début de mot
                        " el",
                        " ^l",
                        "_el",
                        "_^l",  # cas du alif wasla
                    }
                    and diacritiques
                ):
                    transcription += en_arabe["°"]

                # Traitement différent suivant qu'on est en fin de mot ou en milieu :
                if (
                    curseur > len(texte) - 3
                    or apres == " "
                    or (
                        texte[curseur + 2] == " "
                        and apres
                        not in {
                            # il ne faut pas de lettre de prolongation non plus
                            "â",
                            "î",
                            "û",
                            "é",
                            "A",
                            "I",
                            "U",
                            "E",
                            # et piège, après un a̋ le alif orthographique compte comme lettre, donc ce n'est pas une fin de mot...
                            "ã",
                        }
                    )
                ):
                    # hamza en fin de mot
                    if avant == "i":
                        transcription += en_arabe["ì"]
                    elif avant == "u":
                        transcription += en_arabe["ù"]
                    elif avant == "a":
                        transcription += en_arabe["à"]
                    else:
                        transcription += en_arabe["'"]
                    # fin de mot

                # hamza en milieu de mot
                else:
                    double = False
                    if apres in {"'", "²"}:
                        double = True
                        apres = texte[curseur + 2]

                    # derrière un i, support ya sans point
                    if avant in {"i", "î", "I", "y"}:
                        transcription += en_arabe["ì"]

                    # derrière un waw, hamza en ligne
                    elif avant in {"û", "w"}:
                        transcription += en_arabe["'"]

                    # derrière un u faut voir après
                    elif avant == "u":
                        if apres in {"i", "î"}:
                            transcription += en_arabe["ì"]
                        else:
                            transcription += en_arabe["ù"]

                    # derrière un a faut voir après
                    elif avant == "a":
                        if apres in {"i", "î"}:
                            transcription += en_arabe["ì"]
                        elif apres in {"û", "u"}:
                            transcription += en_arabe["ù"]
                        elif apres == "â":
                            # cas particulier : si la hamza est double il faut la mettre en ligne
                            if double:
                                transcription += en_arabe["`"]  # en ligne
                            else:
                                transcription += en_arabe["~"]  # madda, et â sera omis
                        # dans les autres cas, support alif, sauf le cas a' initial déjà traité avec le a initial
                        elif texte[curseur - 2] != " ":
                            transcription += en_arabe["à"]

                    # derrière un â, on risque de trouver une hamza en ligne pour ā’a, ū’a & aw’a
                    elif avant == "â":
                        # il y a nécessairement une consonne après
                        if apres in {"i", "î"}:
                            transcription += en_arabe["ì"]
                        elif apres == "u":
                            transcription += en_arabe["ù"]
                        else:
                            transcription += en_arabe["'"]  # en ligne
                    else:  # pas de voyelle avant, donc sukun
                        if apres in {"i", "î"}:
                            transcription += en_arabe["ì"]
                        elif apres in {"û", "u"}:
                            transcription += en_arabe["ù"]
                        elif apres == "â":
                            transcription += en_arabe["~"]
                        else:
                            transcription += en_arabe["à"]
                    # traitement milieu de mot
                # fin ou pas
            # fin du cas de la hamza

            # Ici il faut isoler le traitement des caractères sur lesquels il n'y aura jamais de sukkun
            elif a_traiter == ",":
                transcription += en_arabe[","]
            elif a_traiter == "-":
                transcription += en_arabe["-"]
            elif a_traiter == "²":
                transcription += en_arabe["²"]
            elif a_traiter == "^":
                transcription += en_arabe["^"]
            elif a_traiter == "?":
                transcription += en_arabe["?"]
            elif a_traiter == "!":
                transcription += en_arabe["!"]

            # dans les autres cas, translittération de la consonne, mais avec sukun éventuel
            else:
                avant = texte[curseur - 1]
                # on ne met pas de sukun après...
                if (
                    avant
                    not in {
                        "a",
                        "e",
                        "i",
                        "u",
                        "â",
                        "î",
                        "û",
                        "é",
                        "ã",
                        "ĩ",
                        "ñ",
                        "É",
                        "A",
                        "I",
                        "U",
                        "E",
                        "ñ",
                        "õ",
                        "-",
                        "~",
                        "_",
                        "°",
                        "^",
                        "?",
                        "0",
                        "1",
                        "2",
                        "M",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        "(",
                        ")",
                        ",",
                        " ",
                    }
                    and a_traiter != " "
                    and texte[curseur - 3 : curseur]
                    not in {
                        # pas de sukun après el- en début de mot
                        " el",
                        " ^l",
                        "_el",
                        "_^l",  # pas de sukun sur un alif wasla
                        " a'",  # pas de sukun sur un alif madda
                    }
                    and diacritiques
                ):
                    transcription += en_arabe["°"]

                if en_arabe.get(a_traiter) is not None:
                    transcription += en_arabe[a_traiter]

                # cas d'une consonne en fin de mot - rajouter un sukun final
                if (
                    texte[curseur + 1] == " "
                    and diacritiques
                    and avant not in {"0", "1", "2", "M", "4", "5", "6", "7", "8", "9"}
                ):
                    transcription += en_arabe["°"]

    return unicodedata.normalize("NFC", transcription)


def est_voyelle(char: str) -> bool:
    """La voyelle peut être tout ce qui permet à une consonne d'être une initiale de syllabe : courte ou longue, tanwîn, ou ta marbuta."""
    return char in {"a", "e", "i", "u", "â", "î", "û", "ã", "ĩ", "ũ", "@", "ñ", "õ"}


def est_voyelle_courte(scheme: str, position: int) -> bool:
    """Détecte la presence d'une voyelle courte à cette position comme ci-dessus mais sans les voyelles longues."""
    return len(scheme) > position and scheme[position] in {"a", "e", "i", "u", "ã", "ĩ", "ũ", "@", "ñ", "õ"}


def nature(scheme: str, position: int) -> str:
    """
    Renvoit la nature de la lettre du schème=scheme située à la position=position (retranscrit par `char` ici).
    Ce peut être :
            (voyelles)
    "vo" = voyelle courte dans une syllable ouverte ;
    "vf" = voyelle courte dans une syllable fermée ;
    "vl" = voyelle longue (dans une syllable longue) ;
            (consonnes initiales)
    "io" = consonne initiale d'une syllable ouverte ;
    "if" = consonne initiale d'une syllable fermée ;
    "il" = consonne initiale d'une syllable longue ;
            (consonnes doubles)
    "do" = consonne double, fermant une syllable et debutant une syllable ouverte ;
    "df" = consonne double debutant une syllable fermée ;
    "dl" = consonne double, debutant une syllable longue ;
            (consonnes de fermeture)
    "fo" = fin de syllable fermée suivie d'une autre consonne ;
    "ff" = fin de syllable fermée et fin de mot (imperatif).
    """
    char = scheme[position]

    if est_voyelle(char):
        # voyelle longue
        if char in {"â", "î", "û"}:
            return "vl"

        # par convention ; une consonne précédente sera toujours "ouverte"
        if char in {"ã", "ĩ", "ũ", "@", "ñ", "õ"}:
            return "vo"

        # voyelle courte finale donc ouverte
        if not scheme[position + 1]:
            return "vo"

        # voyelle courte + consonne finale donc fermée
        if not scheme[position + 2]:
            return "vf"

        # voyelle courte + consonne + voyelle donc ouverte
        if est_voyelle(scheme[position + 2]):
            return "vo"

        return "vf"

    # cas consonne
    # la consonne est la dernière lettre, donc finale fermée
    if not scheme[position + 1]:
        return "ff"

    # consonne double, voir la nature de la voyelle nécessairement présente à pos+2
    if scheme[position + 1] in {"²", char}:
        return f"d{nature(scheme, position + 2)[1]}"

    # 2ème de double, voir la nature de la voyelle nécessairement présente à pos+1
    if scheme[position - 1] == char:
        return f"d{nature(scheme, position + 1)[1]}"

    # 2ème de deux consonnes, idem
    if not est_voyelle(scheme[position - 1]):
        return f"i{nature(scheme, position + 1)[1]}"

    # precede de voyelle et suivie de consonne
    if not est_voyelle(scheme[position + 1]):
        return "fo"

    return f"i{nature(scheme, position + 1)[1]}"


def appliquer(scheme: str, racine: str, *, var: str = "") -> str:
    """
    >>> appliquer("ar-*a*i*iy²ũ", "ar-3lw")
    '3aliyyũ'
    >>> appliquer("ar-ma**û*ũ", "ar-ktb")
    'maktûbũ'

    # FIXME: The test below should output "'abé"
    >>> appliquer("ar-*a*a*a-a", "ar-'by")
    "'aba"
    """

    # Note: no need to use `pagename_interne()` on `scheme` & `racine` because the code is unescaped at a higher level.

    if not var:
        try:
            var = racines_schemes_arabes[racine][scheme][0]
        except KeyError:
            pass

    scheme = scheme[3:]
    racine = racine[3:]

    # Dans les modèles de la forme ar-*a*a*a-i, les deux dernières lettres indiquent conventionnellement la voyelle
    # de l'inaccompli et doivent être supprimées dans un affichage normal
    if scheme[-2] == "-":  # avant-dernière lettre = "-" ?
        scheme = scheme[:-2]  # supprimer les deux dernières, donc limiter au rang -3.

    # voyelle préfixe mobile éventuelle
    mobile = "u" if scheme[2] in {"u", "û"} else "i"

    # Dans le schème, les lettres radicales sont symbolisées par des *, sauf si elles sont répétées, auquel cas elles
    # sont symbolisées par leur numéro d'ordre.
    # remplacement des étoiles successives par le rang d'ordre des lettres radicales (pour homogénéiser le traitement
    # des verbes irréguliers) si le n° correspondant est absent :
    if "1" not in scheme:
        scheme = scheme.replace("*", "1", 1)
    if "2" not in scheme:
        scheme = scheme.replace("*", "2", 1)
    if "3" not in scheme:
        scheme = scheme.replace("*", "3", 1)
    if "4" not in scheme:
        scheme = scheme.replace("*", "4", 1)
    # sauf pour 3, parce que sinon, on a des problèmes si "3" est présent comme lettre radicale...
    # donc on remet un caractère jocker.
    scheme = scheme.replace("3", "µ")

    # NB : on présume que les chiffres sont dans l'ordre avec ce système, un "schème" de type ar-3a2a1a réalise en
    # fait une inversion des lettres - pas malin, mais bon.
    # De même, on peut forcer une lettre faible à une autre valeur par exemple ar-mi**â*ũ peut être forcé sur
    # ar-mi*yâ3ũ quand le W doit se transformer en Y.
    # Les radicales faibles sont w et y. Pour "régulariser" sinon, mettre la radicale faible en majuscule.
    shemeinit = scheme  # sauvegarde de la valeur primitive

    # verbes hamzés en 2 et défectifs : dans les formes 1 et 4 la hamza saute sur les formes de type **a* ou **i* mais pas la forme 10 en sta**a* ou sti**a* ou sta**i*
    # si la hamza ne saute pas, employer ` (hamza invariable) à la place de ' (hamza variable).
    if racine[1:3] == "'y":
        if "12aµ" in scheme and "st" not in scheme:
            scheme = scheme.replace("12aµ", "1aµ")
        if "12iµ" in scheme and "st" not in scheme:
            scheme = scheme.replace("12iµ", "1iµ")
        if "12uµ" in scheme and "st" not in scheme:
            scheme = scheme.replace("12uµ", "1uµ")

    # deuxième radicale = creuse ?
    if var in {"(2)", "(3)", "(5)", "(6)", "(9)"} and racine[1] in {"w", "y"}:
        # ces formes sont régulières, cf Schier p.64. cf Ryding p. 580.
        racine = f"{racine[0]}{racine[1].upper()}{racine[2]}"
    if racine[1:3] in {"wy", "wY", "yy", "yY"}:
        # ces formes sont régulières.
        racine = f"{racine[0]}{racine[1].upper()}{racine[2]}"

    # Sinon, traitement des formes creuses après neutralisation des formes verbales invariables :
    if racine[1] in {"w", "y"} and scheme != "a12aµu":  # invariant, cf Ryding p. 246.
        # verbe creux en W, cf Schier p. 71
        position = scheme.find("2")

        # La 2ème radicale a pu être forcée à autre chose.
        if position > -1:
            # contexte de la radicale : quelles sont les voyelles (courtes ou longues) avant et après la consonne 2 :
            contexte = f"{scheme[position - 1]}2" if est_voyelle(scheme[position - 1]) else "°2"
            if scheme[position + 1] in {"²", scheme[position]}:
                contexte += "²"
                contexte += scheme[position + 2] if est_voyelle(scheme[position + 2]) else "°"
            elif est_voyelle(scheme[position + 1]):
                contexte += scheme[position + 1]
            else:
                contexte += "°"

            if contexte == "a2a" and position == 2:
                # la lettre en position +2 est-elle une finale de syllable ?
                if nature(scheme, position + 2)[0] in {"f", "d"}:
                    if racine[1] == "w":
                        scheme = f"{scheme[: position - 1]}u{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[: position - 1]}â{scheme[position + 2 :]}"

            elif contexte == "a2a" and position != 2:
                # la lettre en position +2 est-elle une finale de syllable ?
                if nature(scheme, position + 2)[0] == "f":
                    scheme = f"{scheme[: position - 1]}a{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[: position - 1]}â{scheme[position + 2 :]}"

            # a2i remplacé par â ou i
            elif contexte == "a2i":
                # la lettre en position +2 est-elle une finale de syllable ?
                if nature(scheme, position + 2)[0] in {"f", "d"}:
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[: position - 1]}â{scheme[position + 2 :]}"

            # a2u remplacé par â ou u
            elif contexte == "a2u":
                # la lettre en position +2 est-elle une finale de syllable ?
                if nature(scheme, position + 2)[0] in {"f", "d"}:
                    scheme = f"{scheme[: position - 1]}u{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[: position - 1]}â{scheme[position + 2 :]}"

            # a2î remplacé par âyi dans ar-*a*î*ũ -- erreur d'interprétation, c'est en fait un ar-*â*i*ũ où la hamza est mal écrite
            # elif contexte == "a2î":
            #     scheme = f"{scheme[: position - 1]}âyi{scheme[position + 2 :]}"

            # a2²i remplacé par ay²i mais pas dans ar-mu*a2²i*ũ (forme 2 invariable)
            elif contexte == "a2²i" and scheme != "mu1a2²iµũ":
                scheme = f"{scheme[: position - 1]}ay²i{scheme[position + 2 :]}"

            # âwi : remplacé par â'i sauf formes verbales 2, 3, 5 et 6
            elif contexte == "â2i":
                scheme = f"{scheme[: position - 1]}â'i{scheme[position + 2 :]}"

            # i2° remplacé par î
            elif contexte == "i2°":
                scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

            # iwâ remplacé par iyâ
            elif contexte in {"i2â", "î2â"}:
                scheme = f"{scheme[: position - 1]}iyâ{scheme[position + 2 :]}"

            # uwi (passif) remplacé par î ou i
            elif contexte == "u2i":
                if nature(scheme, position + 2)[0] in {"f", "d"}:
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

            # °2a : problème à l'impératif pour toutes ces formes : quand l'impératif se termine par
            # la troisième radicale, celle-ci doit fermer la syllabe, et non ouvrir sur une terminaison.
            elif contexte == "°2a":
                # °wa : â si la syllable longue est possible, a sinon
                suite = nature(scheme, position + 2)
                if suite == "ff":
                    scheme = f"{scheme[:position]}a{scheme[position + 2 :]}"
                elif suite[0] == "f":
                    scheme = f"{scheme[:position]}a{scheme[position + 2 :]}"
                elif suite[0] == "d":
                    scheme = f"{scheme[:position]}a{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[:position]}â{scheme[position + 2 :]}"

            # °2â : â, et w supprimé
            elif contexte == "°2â":
                # distinction entre le nom verbal de la forme (iv) **â*ũ
                # et le pluriel irrégulier a**â*ũ (régulier) & mi**â*ũ régulier
                if scheme[0] == "a" or scheme[:2] == "mi":
                    scheme = f"{scheme[:position]}wâ{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[:position]}â{scheme[position + 2 :]}"

            # °2i : î si la syllable longue est possible, i sinon
            elif contexte == "°2i":
                if nature(scheme, position + 2)[0] == "f":
                    scheme = f"{scheme[:position]}i{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[:position]}î{scheme[position + 2 :]}"

            # °2u : û si la syllable longue est possible, u sinon
            elif contexte == "°2u":
                if nature(scheme, position + 2)[0] in {"f", "d"}:
                    scheme = f"{scheme[:position]}u{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"

            # °2û remplacé par û ou î (participe passif)
            elif contexte == "°2û":
                if racine[1] == "w":
                    scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"
                else:
                    scheme = f"{scheme[:position]}î{scheme[position + 2 :]}"

            elif contexte == "°û":
                scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"

            # voiture balai : on remplace tous les "2" par la lettre radicale :
            scheme = scheme.replace("2", racine[1])

    # première radicale en W
    if racine[0] == "w":
        position = scheme.find("1")
        # La 1ère radicale a pu être forcée à autre chose.
        if (
            position > -1
            # première forme, suppression du w dans les formes w2i3, sauf dans les verbes sourds (2=3)
            and scheme[position + 2] == "i"
            and var == "(1)"
            and racine[1] != racine[2]
        ):
            scheme = f"{scheme[:-1]}{scheme[position + 1 :]}"
        # huitième forme : iwta2a3 => it²a2a3 : à faire à la main, la forme i*ta*a*a est une "exception régulière"

    # fin verbes assimilés en W

    # verbe sourd, on supprime la voyelle intercalaire entre 2 et 3 si c'est possible (forme contractée préférentielle)
    # * Si la 3 porte un sukkun (la 2 est alors une initiale de syllabe fermée), pas de suppression (forme déployée).
    # * Si la 3 porte une voyelle courte, la 2 peut porter un sukkun (forme contractée), dans ce cas :
    #    * Si la 1 porte une voyelle on peut supprimer la voyelle (courte et éventuelle) de la 2
    #    * Si la 1 ne porte pas de voyelle on doit y transférer la voyelle courte de la 2.
    #  because of a phonological rule that prevents two identical consonants from being
    # in sequence with a short vowel between them when they are directly followed by a vowel,
    # However, if the second identical stem consonant is followed by another consonant,
    # the identical consonants remain separated
    position2 = scheme.find("2")
    position3 = scheme.find("µ")
    if (
        racine[1] == racine[2]  # deux consonnes identiques
        and racine[1] not in {"*", ".", "?"}  # "lettres" bidon dans les modèles
        and position3 > -1  # si un petit malin propose un schème sans position 3 en redoublant la 2...
        # on est dans un cas "sourd"
        and position2 > -1
    ):
        # sécurité : exclusion du cas des modèles d'exception imposant la deuxième radicale
        nature2 = nature(scheme, position2)  # Quelle est la nature de la seconde radicale?

        # initiale d'une syllabe ouverte, donc 2 porte une voyelle courte et 3 une voyelle.
        # contraction sur les verbes (var~=""), formes verbales, ou sur les noms (var=="") dont l'infixe n'est pas de la forme *v*v* (voyelle courte avant la deuxième radicale).
        # le cas des noms n'est pas très clair, mais on constate que les **v* sont contractés, et certains *v*v* ne le sont pas, on suppose que ce qui apparaissent contractés sont des *v** d'origine (?)
        if nature2 == "io" and (var != "" or (var == "" and scheme[position2 - 1] not in {"a", "i", "u"})):
            if est_voyelle(scheme[position2 - 1]):  # ie, la première radicale est vocalisée
                # alors on peut supprimer la voyelle de la deuxième radicale
                # La surdité n'est normalement réalisée que si la voyelle de la première radicale est courte.
                # On ne peut normalement pas faire suivre une voyelle longue par une consonne avec tchechid (ce qui formerait une super-longue).
                # Mais c'est une variante d'orthographe. Au besoin, créer un modèle de type ar-*â**a pour imposer la configuration.
                if est_voyelle_courte(scheme, position2 - 1):
                    scheme = scheme[: position3 - 2] + scheme[position3 - 1 :]

            # sinon on transfère la voyelle de la deuxième radicale sur la première
            else:
                scheme = "".join(
                    [
                        # début jusqu'à la deuxième radicale
                        scheme[:position2],
                        # insertion de la voyelle de la seconde radicale
                        scheme[position3 - 1],
                        # deuxième radicale
                        scheme[position2],
                        # et directement la troisième (le signe de redoublement sera inséré lors
                        # de la translittération en arabe).
                        scheme[position3:],
                    ]
                )

    # fin exclusion de sécurité.

    # Cas des formes sourdes à quatre radicales = idem sur 3 et 4
    position4 = scheme.find("4")
    if (
        len(racine) > 3
        and racine[3] == racine[2]  # deux consonnes identiques
        and racine[3] not in {"*", ".", "?"}  # "lettres" bidon dans les modèles
        and position4 > -1  # si un petit malin propose un schème sans position 3 en redoublant la 2...
    ):
        # on est dans un cas "sourd"
        position3 = scheme.find("µ")
        nature3 = nature(scheme, position3)
        # initiale d'une syllabe ouverte, donc 3 porte une voyelle courte et 4 une voyelle.
        if nature3 == "io":
            if est_voyelle(scheme[position3 - 1]):
                # ie, la deuxième radicale est vocalisée
                # alors on peut supprimer la troisième radicale
                if est_voyelle_courte(scheme, position2 - 1):
                    scheme = f"{scheme[: position4 - 2]}{scheme[position4 - 1 :]}"
                    # scheme = f"{scheme[: position4 - 1]}{scheme[position4:]}"

            # sinon on transfère la voyelle de la troisième radicale sur la deuxième
            else:
                scheme = "".join(
                    [
                        # début jusqu'à la troisième radicale
                        scheme[:position3],
                        # insertion de la voyelle de la troisième radicale
                        scheme[position4 - 1],
                        # troisième radicale
                        scheme[position3],
                        # et directement la troisième (le signe de redoublement sera inséré lors
                        # de la translittération en arabe).
                        scheme[position4:],
                    ]
                )

    # Inversement, les verbes où la troisième radicale est redoublée dans le schème doivent se
    # conjuguer comme des sourds
    # ie, si le schème contient un µµ ou un µ² devant une consonne il faut séparer les deux, et boucher le trou avec un "a" pour ne pas avoir trois consonnes d'affilée.
    if scheme.find("µµ") > -1 or scheme.find("µ²") > -1:
        scheme = re.sub(r"µ²", "µµ", scheme, count=1)  # homogénéisation des cas
        position3 = scheme.find("µµ")
        if not est_voyelle(scheme[position3 + 2]) or not scheme[position3 + 2]:
            scheme = f"{scheme[: position3 - 1]}a{scheme[position3 + 1 :]}"

    scheme = scheme.replace("2", racine[1])

    # Toisième radicale : cas des verbes défectifs
    if racine[2] in {"w", "y"}:
        # préparation du contexte
        position = scheme.find("µ")
        contexte = ""
        if position > -1:  # La 3ème radicale a pu être forcée à autre chose.
            # contexte de la radicale : quelles sont les voyelles (courtes ou longues) avant et après la consonne 3 :
            contexte += f"{scheme[position - 1]}3" if est_voyelle(scheme[position - 1]) else "°3"
            if len(scheme) == position:
                contexte = contexte  # fin de schème
            elif scheme[position + 1] in {"²", scheme[position]}:
                contexte += "²"
                contexte += scheme[position + 2] if est_voyelle(scheme[position + 2]) else "°"
            elif est_voyelle(scheme[position + 1]):
                contexte += scheme[position + 1]
            else:
                contexte += "°"

            # troisième radicale défective en w
            if racine[2] == "w" and var in {"(1)", ""}:
                # verbe défectif en W, cf Schier p. 74

                if contexte == "a3a":
                    # awa final devient â au prétérit de la première forme, é sinon
                    if position == len(scheme) - 1:
                        # position finale
                        if position == 5 and scheme[1] == "a":  # première forme
                            scheme = f"{scheme[: position - 1]}â{scheme[position + 2 :]}"
                        else:
                            scheme = f"{scheme[: position - 1]}é{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}a{scheme[position + 2 :]}"

                # test sur première forme
                elif contexte == "a3â":
                    # awâ final devient ayâ au passif devant a3âni final
                    if (
                        position == len(scheme) - 3 and scheme[position + 2 : position + 4] == "ni" and (var != "")
                    ):  # les duels ne sont pas concernés.
                        scheme = f"{scheme[: position - 1]}ayâ{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[:position]}{racine[2]}{scheme[position + 1 :]}"

                elif contexte == "a3@":
                    scheme = f"{scheme[: position - 1]}â@{scheme[position + 2 :]}"

                elif contexte == "a3î":
                    scheme = f"{scheme[: position - 1]}ay{scheme[position + 2 :]}"

                elif contexte == "a3u":
                    scheme = f"{scheme[: position - 1]}é{scheme[position + 2 :]}"

                elif contexte == "a3û":
                    scheme = f"{scheme[: position - 1]}aw{scheme[position + 2 :]}"

                elif contexte == "a3ũ":
                    # Pb ici, "ã" pour *a*a*ũ, *i*a*ũ et *u*a*ũ, "ãé" sinon. Cf. Palmer §50 p100
                    if shemeinit in {"1a2aµũ", "1i2aµũ", "1u2aµũ"}:
                        scheme = f"{scheme[: position - 1]}ã"
                    else:
                        scheme = f"{scheme[: position - 1]}ãé"

                elif contexte == "a3ã":
                    # Pb ici, "ã" pour *a*a*ũ, *i*a*ũ et *u*a*ũ, "ãé" sinon. Cf. Palmer §50 p100
                    if shemeinit in {"1a2aµã", "1i2aµã", "1u2aµã"}:
                        scheme = f"{scheme[: position - 1]}ã"
                    else:
                        scheme = f"{scheme[: position - 1]}ãé"

                elif contexte == "a3ĩ":
                    # Pb ici, "ã" pour *a*a*ũ, *i*a*ũ et *u*a*ũ, "ãé" sinon. Cf. Palmer §50 p100
                    if shemeinit in {"1a2aµĩ", "1i2aµĩ", "1u2aµĩ"}:
                        scheme = f"{scheme[: position - 1]}ã"
                    else:
                        scheme = f"{scheme[: position - 1]}ãé"

                elif contexte == "â3ũ":
                    # seul cas pratique derrière un â long?
                    scheme = f"{scheme[: position - 1]}â'u"  # diptote dans ce cas

                elif contexte == "a3°":
                    # inaccompli passif (2FP, 3FP) en ay
                    # versus accompli actif en voyelle de l'inaccompli (?) :
                    if scheme[position - 3] == "a":  # on est à l'inaccompli
                        scheme = f"{scheme[: position - 1]}aw{scheme[position + 1 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}ay{scheme[position + 1 :]}"

                elif contexte == "i3a":
                    scheme = f"{scheme[: position - 1]}iya{scheme[position + 2 :]}"

                elif contexte == "i3@":
                    scheme = f"{scheme[: position - 1]}iy@{scheme[position + 2 :]}"

                elif contexte == "i3i":
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"

                elif contexte == "i3â":
                    scheme = f"{scheme[: position - 1]}iyâ{scheme[position + 2 :]}"

                elif contexte == "i3î":
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

                elif contexte == "i3ĩ":
                    scheme = f"{scheme[: position - 1]}ĩ{scheme[position + 2 :]}"

                elif contexte == "i3u":
                    scheme = f"{scheme[: position - 1]}iy{scheme[position + 2 :]}"

                elif contexte == "i3û":
                    scheme = f"{scheme[: position - 1]}û{scheme[position + 2 :]}"

                elif contexte == "i3ũ":
                    scheme = f"{scheme[: position - 1]}ĩ{scheme[position + 2 :]}"

                elif contexte == "i3°":
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

                elif contexte == "u3i":
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"

                elif contexte == "u3î":
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

                elif contexte == "u3u":
                    # dépend si c'est en fin de mot
                    if position == len(scheme) - 1:
                        scheme = f"{scheme[: position - 1]}îû{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}u{scheme[position + 2 :]}"

                elif contexte == "u3û":
                    scheme = f"{scheme[: position - 1]}îû{scheme[position + 2 :]}"

                elif contexte == "u3ũ":
                    scheme = f"{scheme[: position - 1]}ĩ{scheme[position + 2 :]}"

                elif contexte == "u3":  # en fin de mot
                    scheme = f"{scheme[: position - 1]}u{scheme[position + 1 :]}"

                elif contexte == "u3°":
                    scheme = f"{scheme[: position - 1]}û{scheme[position + 1 :]}"

                elif scheme[position - 1] == "y":  # cas du diminutif en *u*ay*ũ ou *u*ay*@ũ:
                    scheme = f"{scheme[:position]}y{scheme[position + 1 :]}"

                elif contexte == "û3ũ":  # Pb d'écriture
                    scheme = f"{scheme[: position - 1]}uw²ũ{scheme[position + 2 :]}"

                elif contexte == "°3ũ" and scheme[position - 2] == "a":
                    # traitement différent de *a*wũ et *u*wũ - bon, enfin, du moins ça marche :-/
                    scheme = f"{scheme[:position]}wũ{scheme[position + 2 :]}"

                elif contexte in {"°3ũ", "°3ĩ"}:
                    scheme = f"{scheme[:position]}ã{scheme[position + 2 :]}"

                elif contexte == "°3ã" and scheme[position + 2] != "é":
                    scheme = f"{scheme[:position]}ã{scheme[position + 2 :]}"

                # la radicale faible disparaît parfois devant @, mais il faut dans ce cas la supprimer à la main.
                # fin traitement des cas particuliers en w

            else:
                # verbe défectif en Y, cf Schier p. 74
                # ou formes dérivées d'un verbe défectif, traité comme un "y"
                if contexte == "a3a":
                    if position == len(scheme) - 1:  # position finale
                        scheme = f"{scheme[: position - 1]}é{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}a{scheme[position + 2 :]}"

                elif contexte == "a3â":
                    scheme = f"{scheme[: position - 1]}ayâ{scheme[position + 2 :]}"

                elif contexte == "a3@":
                    scheme = f"{scheme[: position - 1]}â@{scheme[position + 2 :]}"

                elif contexte == "â3@":
                    scheme = f"{scheme[: position - 1]}ây@{scheme[position + 2 :]}"

                elif contexte == "a3î":
                    scheme = f"{scheme[: position - 1]}ay{scheme[position + 2 :]}"

                elif contexte == "a3u":
                    # dépend si c'est en fin de mot
                    if position == len(scheme) - 1:
                        scheme = f"{scheme[: position - 1]}é{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}ay{scheme[position + 2 :]}"

                elif contexte == "a3û":
                    scheme = f"{scheme[: position - 1]}aw{scheme[position + 2 :]}"

                elif contexte in {"a3ũ", "a3ã", "a3ĩ"}:
                    scheme = f"{scheme[: position - 1]}ãé"

                elif contexte == "â3i":
                    scheme = f"{scheme[: position - 1]}â'i{scheme[position + 2 :]}"
                    # typiquement -*i*â*iy²ũ doit conserver la hamza de -*i*â*ũ
                    # en fait on peut neutraliser via un W fort.
                elif contexte == "â3ũ":  # and racine[1] != "'")  # exception pour la hamza en 2 ?
                    scheme = f"{scheme[: position - 1]}â'u"  # diptote dans ce cas

                elif contexte == "a3°":
                    # ay devant consonne, é en finale
                    scheme = f"{scheme[: position - 1]}ay{scheme[position + 1 :]}"

                elif contexte == "a3" and racine[1] == "'":
                    # exemple de ar-r'y impératif sur un schème de type ar-*a3
                    scheme = f"{scheme[: position - 1]}a"

                elif contexte == "a3":
                    scheme = f"{scheme[: position - 1]}i"

                elif contexte == "i3a":
                    scheme = f"{scheme[: position - 1]}iya{scheme[position + 2 :]}"

                elif contexte == "i3@":
                    scheme = f"{scheme[: position - 1]}iy@{scheme[position + 2 :]}"

                elif contexte == "î3@":
                    scheme = f"{scheme[: position - 1]}îy@{scheme[position + 2 :]}"

                elif contexte == "i3â":
                    scheme = f"{scheme[: position - 1]}iyâ{scheme[position + 2 :]}"

                elif contexte == "i3i":
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 2 :]}"

                elif contexte == "i3î":  # î
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"

                elif contexte == "i3ĩ":
                    scheme = f"{scheme[: position - 1]}ĩ{scheme[position + 2 :]}"

                elif contexte == "i3u":  # dépend si c'est en fin de mot
                    if position == len(scheme) - 1:
                        scheme = f"{scheme[: position - 1]}î{scheme[position + 2 :]}"
                    else:
                        scheme = f"{scheme[: position - 1]}u{scheme[position + 2 :]}"

                elif contexte == "i3û":
                    scheme = f"{scheme[: position - 1]}û{scheme[position + 2 :]}"

                elif contexte == "i3ũ":
                    scheme = f"{scheme[: position - 1]}ĩ"

                elif contexte == "i3°":
                    scheme = f"{scheme[: position - 1]}î{scheme[position + 1 :]}"

                elif contexte == "i3":  # en fin de mot
                    scheme = f"{scheme[: position - 1]}i{scheme[position + 1 :]}"

                elif contexte == "u3ũ":
                    scheme = f"{scheme[: position - 1]}ĩ{scheme[position + 2 :]}"

                elif (contexte == "û3ũ") and scheme[:3] == "ma1":
                    # contamination du y sur le û dans la forme ma**û*ũ, cf Wright 1874 §170,
                    # mais la 2 est déjà remplacée dans le schème donc on ne peut pas tester le schème d'origine
                    scheme = f"{scheme[: position - 1]}iy²ũ{scheme[position + 2 :]}"

                elif (contexte == "û3@") and scheme[:3] == "ma1":
                    # idem féminin
                    scheme = f"{scheme[: position - 1]}iy²@{scheme[position + 2 :]}"

                # fin traitement des cas particuliers en y
            # verbe défectifs

        # 3ème radicale présente

    # verbes défectifs
    # voiture balai :
    scheme = scheme.replace("µ", racine[2])

    # quatrième radicale éventuelle
    # si on applique un schème quadrilittère à une racine à trois consonnes, on redouble simplement la dernière
    scheme = scheme.replace("4", racine[2 if (len(racine) <= 3 or racine[3] == "") else 3])

    # première radicale
    scheme = scheme.replace("1", racine[0])

    # pb : si le schème est en "1°" le "i" prosthétique est virtuel à ce stade :
    # le cas général "de prolongation" ne marche pas, il faut forcer à la main :
    if scheme[0] == "w" and not est_voyelle(scheme[1]):
        scheme = f"î{scheme[1]}"

    # Accord des w et y de prolongation en fonction du contexte vocalique
    # (ne concerne pas les W et Y, invariables par principe) :
    while (position := scheme.find("iw")) > -1:
        if est_voyelle(scheme[position + 2]):
            scheme = f"{scheme[:position]}iW{scheme[position + 2 :]}"  # éviter une boucle infinie
        elif (
            scheme[position + 2] == "²"
        ):  # Pb sinon avec les -iw²- qu'il ne faut pas transformer en î², ce qui n'aurait aucun sens...
            scheme = f"{scheme[:position]}iY{scheme[position + 2 :]}"
        else:
            scheme = f"{scheme[:position]}î{scheme[position + 2 :]}"

    while (position := scheme.find("uy")) > -1:
        if est_voyelle(scheme[position + 2]):
            scheme = f"{scheme[:position]}uY{scheme[position + 2 :]}"
        else:
            scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"

    while (position := scheme.find("wî")) > -1:
        scheme = f"{scheme[:position]}yi{scheme[position + 2 :]}"

    # nettoyage éventuel : Y et W des verbes réguliers; neutralisation des verbes hamzé
    scheme = (
        scheme.replace("Y", "y")
        .replace("W", "w")
        .replace("`", "'")  # remplacement de l'accent grave par un guillement simple
    )

    # écriture des lettres de prolongations
    while (position := scheme.find("ûw")) > -1:
        scheme = f"{scheme[:position]}uw²{scheme[position + 2 :]}"

    while (position := scheme.find("uw")) > -1:
        if est_voyelle(scheme[position + 2]):
            scheme = f"{scheme[:position]}uW{scheme[position + 2 :]}"
        else:
            scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"

    while (position := scheme.find("iy")) > -1:
        if est_voyelle(scheme[position + 2]) or scheme[position + 2] == "²":  # Pb sinon avec les -iy²-
            scheme = f"{scheme[:position]}iY{scheme[position + 2 :]}"
        else:
            scheme = f"{scheme[:position]}î{scheme[position + 2 :]}"

    while (position := scheme.find("îy")) > -1:
        scheme = f"{scheme[:position]}iy²{scheme[position + 2 :]}"

    while (position := scheme.find("yî")) > -1:
        if est_voyelle_courte(scheme, position - 1):
            # intercepter des cas comme taXyîTũ => taXYîTũ et pas taXy²iTũ ;
            # d'autre part des séquences de type âyî restent invariables (pas de redoublement possible après une voyelle longue).
            scheme = f"{scheme[:position]}y²i{scheme[position + 2 :]}"
        else:
            scheme = f"{scheme[:position]}Yî{scheme[position + 2 :]}"

    while (position := scheme.find("û²")) > -1:
        scheme = f"{scheme[:position]}uw²{scheme[position + 2 :]}"

    # nettoyage éventuel : Y et W repassent en minuscule pour l'affichage :
    scheme = scheme.replace("Y", "y").replace("W", "w")

    # ajout d'une voyelle mutable, si le mot commence par deux consonnes :
    if not est_voyelle(scheme[0]) and not est_voyelle(scheme[1]):
        # Consonne en première position et pas de voyelle en deuxième position = il faut rajouter une voyelle préfixe.
        scheme = f"{mobile}{scheme}"

    # ajustement de l'initiale pour les verbes hamzés en 1 : i' se transforme en î et u' en û
    # (une même syllabe ne peut pas être à la fois ouverte et fermée par une hamza)
    if scheme[:3] == "i'":
        scheme = f"iy{scheme[2]}" if est_voyelle(scheme[2]) else f"î{scheme[2]}"
    if scheme[:3] == "u'":
        scheme = f"uw{scheme[2]}" if est_voyelle(scheme[2]) else f"û{scheme[2]}"
    if scheme[:3] == "a'":
        scheme = f"aw{scheme[2]}" if est_voyelle(scheme[2]) else f"â{scheme[2]}"

    # ajustement pour les verbes assimilés en y
    if (position := scheme.find("uy")) > -1:
        if not est_voyelle(scheme[position + 2]):
            scheme = f"{scheme[:position]}û{scheme[position + 2 :]}"

    # Ajustement des redoublements en ² en doublant la consonne à la place :
    while "²" in scheme:
        position = scheme.find("²")
        lettre = scheme[position - 1]
        scheme = f"{scheme[:position]}{lettre}{scheme[position + 1 :]}"

    # ... mais pas la hamza sinon pb d'affichage
    if "''" in scheme:
        position = scheme.find("''")
        scheme = f"{scheme[: position + 1]}²{scheme[position + 2 :]}"

    # Pb d'affichage de deux hamza de suite : mettre la première en ligne (pas sûr que ce soit la meilleure solution)
    if "'a'" in scheme:
        position = scheme.find("'a'")
        scheme = f"{scheme[:position]}`a'{scheme[position + 3 :]}"

    # the end !
    return scheme
