"""
Transliterator used across multiple templates.

Source: https://de.wiktionary.org/w/index.php?title=Modul:Umschrift&oldid=10104221
"""


class Umschrift:
    @staticmethod
    def ab(text: str) -> str:
        abkyr = "АаБбВвГгӶӷДдЕеЖжЗзӠӡИиКкҚқЛлМмНнОоПпԤԥРрСсТтҬҭУуФфХхҲҳЦцЧчҶҷҼҽШшЫыҨҩь"
        ablat = "AaBbVvGgĞğDdEeŽžZzŹźIiKkĶķLlMmNnOoPpṔṕRrSsTtŢţUuFfHhḨḩCcČčÇçČčŠšYyÒòʹ"
        special = {"Ҟ": "K̄", "ҟ": "k̄", "Ҵ": "C̄", "ҵ": "c̄", "Ҿ": "Č̦", "ҿ": "č̦", "Џ": "D̂", "џ": "d̂", "ә": "a̋"}
        trans = str.maketrans(abkyr, ablat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def abq(text: str) -> str:
        abqkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяӀӏ"
        abqlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ‡‡"
        trans = str.maketrans(abqkyr, abqlat)
        return text.translate(trans)

    @staticmethod
    def ady(text: str) -> str:
        adykyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяӀӏ"
        adylat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ‡‡"
        trans = str.maketrans(adykyr, adylat)
        return text.translate(trans)

    @staticmethod
    def alt(text: str) -> str:
        altkyr = "АаБбВвГгДдјЕеЁёЖжЗзИиЙйКкЛлМмНнҤҥОоӦӧПпРрСсТтУуӰӱФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        altlat = "AaBbVvGgDďǰEeËëŽžZzIiJjKkLlMmNnṄṅOoÖöPpRrSsTtUuÜüFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        special = {"Ј": "J̌"}
        trans = str.maketrans(altkyr, altlat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def av(text: str) -> str:
        avkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяӀӏ"
        avlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ‡‡"
        trans = str.maketrans(avkyr, avlat)
        return text.translate(trans)

    @staticmethod
    def ba(text: str) -> str:
        bakyr = "АаБбВвГгҒғДдЕеЁёЖжЗзИиЙйКкҠҡЛлМмНнҢңОоӨөПпРрСсҪҫТтУуҮүФфХхҺһЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        balat = "AaBbVvGgĠġDdEeËëŽžZzIiJjKkǨǩLlMmNnṆṇOoÔôPpRrSsȘșTtUuÙùFfHhḤḥCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        special = {"Ҙ": "Z̦", "ҙ": "z̦", "Ә": "A̋", "ә": "a̋"}
        trans = str.maketrans(bakyr, balat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def be(text: str) -> str:
        kyr = "АаБбВвГгҐґДдЕеЁёЖжЗзІіЙйКкЛлМмНнОоПпРрСсТтУуЎўФфЦцЧчШшЫыЭэ"
        lat = "AaBbVvHhGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuŬŭFfCcČčŠšYyĖė"
        special = {
            "Ъ": '"',
            "ъ": '"',
            "’": '"',
            "Ь": "ʹ",
            "ь": "ʹ",
            "Х": "Ch",
            "х": "ch",
            "Ю": "Ju",
            "ю": "ju",
            "Я": "Ja",
            "я": "ja",
        }
        trans = str.maketrans(kyr, lat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def bg(text: str) -> str:
        kyr = "АаБбВвГгДдЕеЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфЦцЧчШшЫы"
        lat = "AaBbVvGgDdEeŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfCcČčŠšYy"
        special = {
            "Ъ": "Ă",
            "ъ": None,
            "Ь": "ʹ",
            "ь": "ʹ",
            "Х": "Ch",
            "х": "ch",
            "Щ": "Št",
            "щ": "št",
            "Ю": "Ju",
            "ю": "ju",
            "Я": "Ja",
            "я": "ja",
            "Ѝ": "Ì",
            "ѝ": "ì",
        }
        trans = str.maketrans(kyr, lat)
        res = []
        strlen = len(text)
        for i, c in enumerate(text):
            if c == "ъ":
                res.append('"' if i == strlen - 1 else "ă")
            else:
                res.append(special.get(c) or c.translate(trans))
        return "".join(res)

    @staticmethod
    def bua(text: str) -> str:
        buakyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоӨөПпРрСсТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяҺһ"
        bualat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoÔôPpRrSsTtUuÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâḤḥ"
        trans = str.maketrans(buakyr, bualat)
        return text.translate(trans)

    @staticmethod
    def ce(text: str) -> str:
        cekyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяӀӏ"
        celat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ‡‡"
        trans = str.maketrans(cekyr, celat)
        return text.translate(trans)

    @staticmethod
    def chm(text: str) -> str:
        chmkyr = "АаӒӓБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнҤҥОоӦӧПпРрСсТтУуӰӱФфХхЦцЧчШшЩщЪъЫыӸӹЬьЭэЮюЯя"
        chmlat = "AaÄäBbVvGgDdEeËëŽžZzIiJjKkLlMmNnṄṅOoÖöPpRrSsTtUuÜüFfHhCcČčŠšŜŝʺʺYyŸÿʹʹÈèÛûÂâ‵"
        trans = str.maketrans(chmkyr, chmlat)
        return text.translate(trans)

    @staticmethod
    def ckt(text: str) -> str:
        cktkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкӃӄЛлԒԓМмНнӇӈОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯяʼ"
        cktlat = "AaBbVvGgDdEeËëŽžZzIiJjKkḲḳLlĻļMmNnŇňOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYy’’ÈèÛûÂâ‵"
        trans = str.maketrans(cktkyr, cktlat)
        return text.translate(trans)

    @staticmethod
    def crh(text: str) -> str:
        crhkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        crhlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(crhkyr, crhlat)
        return text.translate(trans)

    @staticmethod
    def cv(text: str) -> str:
        cvkyr = "АаӐӑБбВвГгДдЕеЁёӖӗЖжЗзИиЙйКкЛлМмНнОоПпРрСсҪҫТтУуӲӳФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        cvlat = "AaĂăBbVvGgDdEeËëĔĕŽžZzIiJjKkLlMmNnOoPpRrSsÇçTtUuŰűFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(cvkyr, cvlat)
        return text.translate(trans)

    @staticmethod
    def dng(text: str) -> str:
        dngkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнҢңӘәОоПпРрСсТтУуЎўҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        dnglat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnṆṇÀàOoPpRrSsTtUuŬŭÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        special = {"Җ": "Ž̧", "җ": "ž̧"}
        trans = str.maketrans(dngkyr, dnglat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def grc(text: str) -> str:
        grb = "βΒδΔγΓϊΪκΚλΛμΜνΝπϖΠρῤϱΡσςΣτΤϋΫξΞζΖ;·Ϝϝ"
        lat = "bBdDgGïÏkKlLmMnNppPrrrRssStTÿŸxXzZ?;Ww"
        result = []
        cp = 0
        length = len(text)
        possible2 = True

        def is_blank(c: str) -> bool:
            return c.isspace()

        def is_punct(c: str) -> bool:
            # Accept Greek punctuation and ASCII punctuation
            return c in ";·" or not c.isalnum() and not c.isspace()

        while cp < length:
            # handle blanks and punctuation
            while cp < length and (is_blank(text[cp]) or is_punct(text[cp])):
                if text[cp] == ";":
                    result.append("?")
                elif text[cp] == "·":
                    result.append(";")
                else:
                    result.append(text[cp])
                cp += 1

            # Zahlschrift check
            if cp < length - 1:
                rem = text[cp:length]
                blgef = rem.find(" ")
                pgef = next((i for i, c in enumerate(rem) if is_punct(c)), None)
                endgef = length
                if blgef != -1:
                    endgef = cp + blgef
                if pgef is not None and cp + pgef < endgef:
                    endgef = cp + pgef
                cpend = endgef - 1
                if text[cpend] == "ʹ" or text[cp] == "͵":
                    # Zahlschrift ermitteln
                    result.append(grcZZ(text[cp : cpend + 1]))
                    cp = endgef
                    continue

            # two-char combos
            if cp + 1 < length and possible2:
                first, second = text[cp], text[cp + 1]
                element = first + second

                def in_(s: str, c: str) -> bool:
                    return c in s

                # all combinations, order as in Lua
                if first == "α" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("au")
                    cp += 2
                    continue
                if first == "Α" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("Au")
                    cp += 2
                    continue
                if element == "αϋ":
                    result.append("aÿ")
                    cp += 2
                    continue
                if element == "Αϋ":
                    result.append("Aÿ")
                    cp += 2
                    continue
                if first == "α" and in_("ἱἵἳἷ", second):
                    result.append("hai")
                    cp += 2
                    continue
                if first == "Α" and in_("ἱἵἳἷ", second):
                    result.append("Hai")
                    cp += 2
                    continue
                if first == "ε" and in_("ἱἵἳἷ", second):
                    result.append("hei")
                    cp += 2
                    continue
                if first == "Ε" and in_("ἱἵἳἷ", second):
                    result.append("Hei")
                    cp += 2
                    continue
                if first == "ε" and in_("ὑὕὓὗ", second):
                    result.append("heu")
                    cp += 2
                    continue
                if first == "Ε" and in_("ὑὕὓὗ", second):
                    result.append("Heu")
                    cp += 2
                    continue
                if first == "ε" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("eu")
                    cp += 2
                    continue
                if first == "Ε" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("Eu")
                    cp += 2
                    continue
                if element == "ηυ":
                    result.append("ēu")
                    cp += 2
                    continue
                if element == "Ηυ":
                    result.append("Ēu")
                    cp += 2
                    continue
                if element == "γγ":
                    result.append("ng")
                    cp += 2
                    continue
                if element == "Γγ":
                    result.append("Ng")
                    cp += 2
                    continue
                if element == "γκ":
                    if cp == 0 or (cp > 0 and text[cp - 1] == " "):
                        result.append("gk")
                    else:
                        result.append("nk")
                    cp += 2
                    continue
                if element == "Γk":
                    if cp == 0 or (cp > 0 and text[cp - 1] == " "):
                        result.append("Gk")
                    else:
                        result.append("Nk")
                    cp += 2
                    continue
                if element == "γξ":
                    result.append("nx")
                    cp += 2
                    continue
                if element == "Γξ":
                    result.append("Nx")
                    cp += 2
                    continue
                if element == "γχ":
                    result.append("nch")
                    cp += 2
                    continue
                if element == "Γχ":
                    result.append("Nch")
                    cp += 2
                    continue
                if element == "ηυ":
                    result.append("ēu")
                    cp += 2
                    continue
                if element == "Ηυ":
                    result.append("Ēu")
                    cp += 2
                    continue
                if first == "η" and in_("ὑὕὓὗ", second):
                    result.append("hēu")
                    cp += 2
                    continue
                if first == "Η" and in_("ὑὕὓὗ", second):
                    result.append("Hēu")
                    cp += 2
                    continue
                if first == "ο" and in_("ἱἵἳἷ", second):
                    result.append("hoi")
                    cp += 2
                    continue
                if first == "Ο" and in_("ἱἵἳἷ", second):
                    result.append("Hoi")
                    cp += 2
                    continue
                if first == "ο" and in_("ὑὕὓὗ", second):
                    result.append("hu")
                    cp += 2
                    continue
                if first == "Ο" and in_("ὑὕὓὗ", second):
                    result.append("Hu")
                    cp += 2
                    continue
                if first == "ο" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("u")
                    cp += 2
                    continue
                if first == "Ο" and in_("υύὺῠῡὐὔὒῦὖ", second):
                    result.append("U")
                    cp += 2
                    continue
                if first == "υ" and in_("ἱἵἳἷ", second):
                    result.append("hyi")
                    cp += 2
                    continue
                if first == "Υ" and in_("ἱἵἳἷ", second):
                    result.append("Hyi")
                    cp += 2
                    continue
                if element == "ῤῥ":
                    result.append("rrh")
                    cp += 2
                    continue
                possible2 = False

            # single-char logic
            if cp < length:
                element = text[cp]
                h_erwartet = False
                if cp == 0 or (cp > 0 and (text[cp - 1] == " " or is_punct(text[cp - 1]))):
                    h_erwartet = True

                def in_(s: str, c: str) -> bool:
                    return c in s

                # all single-char logic, direct translation
                if element in ("θ", "ϑ"):
                    result.append("th")
                elif element in ("Θ", "ϴ"):
                    result.append("Th")
                elif in_("αάὰᾰᾱᾷἀἄἂᾆᾶᾳᾴᾲἆᾀᾄᾂ", element):
                    result.append("a")
                elif in_("ΑΆᾺᾸᾹἈἌἊᾎᾼἎᾈᾌᾊ", element):
                    result.append("A")
                elif in_("εέὲἐἔἒ", element):
                    result.append("e")
                elif in_("ΕΈῈἘἜἚ", element):
                    result.append("E")
                elif in_("ηήὴῇἠἤἢᾖῆῃῄῂἦᾐᾔᾒ", element):
                    result.append("ē")
                elif in_("ΗΉῊἨἬἪᾞῌἮᾘᾜᾚ", element):
                    result.append("Ē")
                elif in_("ἁἅἃᾇἇᾁᾅᾃ", element):
                    result.append("ha" if h_erwartet else "a")
                elif in_("ἉἍἋᾏἏᾉᾍᾋ", element):
                    result.append("Ha" if h_erwartet else "A")
                elif in_("ἑἕἓ", element):
                    result.append("he" if h_erwartet else "e")
                elif in_("ἙἝἛ", element):
                    result.append("He" if h_erwartet else "E")
                elif in_("ἡἥἣᾗἧᾑᾕᾓ", element):
                    result.append("hē" if h_erwartet else "ē")
                elif in_("ἩἭἫᾟἯᾙᾝᾛ", element):
                    result.append("Hē" if h_erwartet else "Ē")
                elif in_("ἱἵἳἷ", element):
                    result.append("hi" if h_erwartet else "i")
                elif in_("ἹἽἻἿ", element):
                    result.append("Hi" if h_erwartet else "I")
                elif in_("ὁὅὃ", element):
                    result.append("ho" if h_erwartet else "o")
                elif in_("ὉὍὋ", element):
                    result.append("Ho" if h_erwartet else "O")
                elif in_("ὡὥὣᾧὧᾡᾥᾣ", element):
                    result.append("hō" if h_erwartet else "ō")
                elif in_("ὩὭὫᾯὯᾩᾭᾫ", element):
                    result.append("Hō" if h_erwartet else "Ō")
                elif in_("ὑὕὓὗ", element):
                    result.append("hy" if h_erwartet else "y")
                elif in_("ὙὝὛὟ", element):
                    result.append("Hy" if cp == 0 else "Y")
                elif in_("ιίὶῐῑἰἴἲῖἶ", element):
                    result.append("i")
                elif in_("ΙΊῚῘῙἸἼἺἾ", element):
                    result.append("I")
                elif in_("ΐῒῗ", element):
                    result.append("ï")
                elif in_("οόὸὀὄὂ", element):
                    result.append("o")
                elif in_("ΟΌῸὈὌὊ", element):
                    result.append("O")
                elif in_("ωώὼῷὠὤὢᾦῶῳῴὦᾠᾤᾢ", element):
                    result.append("ō")
                elif in_("ΩΏῺὨὬὪᾮῼὮᾨᾬᾪ", element):
                    result.append("Ō")
                elif element == "φ":
                    result.append("ph")
                elif element == "Φ":
                    result.append("Ph")
                elif element == "χ":
                    result.append("ch")
                elif element == "Χ":
                    result.append("Ch")
                elif element == "ψ":
                    result.append("ps")
                elif element == "Ψ":
                    result.append("Ps")
                elif element == "ῥ":
                    result.append("rh")
                elif element == "Ῥ":
                    result.append("Rh")
                elif in_("υύὺῠῡὐὔὒῦὖ", element):
                    result.append("y")
                elif in_("ΥΎῪῨῩ", element):
                    result.append("Y")
                elif in_("ϋΰῢῧ", element):
                    result.append("ÿ")
                else:
                    try:
                        idx = grb.index(element)
                        result.append(lat[idx])
                    except ValueError:
                        result.append(element)
                cp += 1
                possible2 = True
        return "".join(result)

    @staticmethod
    def kbd(text: str) -> str:
        kbdkyr = "АаЭэБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЮюЯяӀӏ"
        kbdlat = "AaÈèBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÛûÂâ‡‡"
        trans = str.maketrans(kbdkyr, kbdlat)
        return text.translate(trans)

    @staticmethod
    def kca(text: str) -> str:
        kcakyr = (
            "АаӒӓӐӑБбВвГгДдЕеЁёӘәЖжЗзИиЙйКкӃӄЛлԒԓМмНнӇӈОоŎŏӦӧӨөӪӫПпРрСсТтУуӰӱЎўФфХхӼӽЦцЧчҶҷШшЩщЪъЫыЬьЭэЄєЮюЯяҚқӅӆҢңҲҳ"
        )
        kcalat = (
            "AaÄäĂăBbVvGgDdEeËëÀàŽžZzIiJjKkḲḳLlĻļMmNnṆṇOoŎŏÖöÔôŐőPpRrSsTtUuÜüŬŭFfHhḤḥCcČčÇçŠšŜŝʺʺYyʹʹÈèÊêÛûÂâĶķĻļṆṇḨḩ"
        )
        special = {"Ӛ": "A̋", "ӛ": "a̋", "Є̈": "Ê̈̋", "є̈": "ê̈̋", "Ю̆": "Û̆", "ю̆": "û̆̋", "Я̆": "Û̆", "я̆̆": "û̆̋"}
        trans = str.maketrans(kcakyr, kcalat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def kk(text: str) -> str:
        kkkyr = "АаБбВвГгҒғДдЕеЁёЖжЗзИиЙйКкҚқЛлМмНнҢңОоӨөПпРрСсТтУуҰұҮүФфХхҺһЦцЧчШшЩщЪъЫыІіЬьЭэЮюЯя"
        kklat = "AaBbVvGgĠġDdEeËëŽžZzIiJjKkĶķLlMmNnṆṇOoÔôPpRrSsTtUuÚúÙùFfHhḤḥCcČčŠšŜŝʺʺYyÌìʹʹÈèÛûÂâ"
        special = {"Ә": "A̋", "ә": "a̋"}
        trans = str.maketrans(kkkyr, kklat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def kv(text: str) -> str:
        kvkyr = "АаБбВвГгДдЕеЁёЖжЗзИиІіЙйКкЛлМмНнОоӦӧПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        kvlat = "AaBbVvGgDdEeËëŽžZzIiÌìJjKkLlMmNnOoÖöPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(kvkyr, kvlat)
        return text.translate(trans)

    @staticmethod
    def krc(text: str) -> str:
        krckyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоӨөПпРрСсТтУуҮүЎўФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        krclat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoÔôPpRrSsTtUuÙùŬŭFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(krckyr, krclat)
        return text.translate(trans)

    @staticmethod
    def ky(text: str) -> str:
        kykyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнҢңОоӨөПпРрСсТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        kylat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnṆṇOoÔôPpRrSsTtUuÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(kykyr, kylat)
        return text.translate(trans)

    @staticmethod
    def mdf(text: str) -> str:
        mdfkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        mdflat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(mdfkyr, mdflat)
        return text.translate(trans)

    @staticmethod
    def mk(text: str) -> str:
        kyr = "АаБбВвГгДдЃѓЕеЖжЗзИиЈјКкЛлМмНнОоПпРрСсЌќТтУуФфХхЦцЧчШш"
        lat = "AaBbVvGgDdǴǵEeŽžZzIiJjKkLlMmNnOoPpRrSsḰḱTtUuFfHhCcČčŠš"
        special = {
            "Ѕ": "Dz",
            "ѕ": "dz",
            "ʼ": '"',
            "Џ": "Dž",
            "џ": "dž",
            "Њ": "Nj",
            "њ": "nj",
            "Љ": "Lj",
            "љ": "lj",
            "Ѝ": "Ì",
            "ѝ": "ì",
        }
        trans = str.maketrans(kyr, lat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def mn(text: str) -> str:
        mnkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоӨөПпРрСсТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        mnlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoÔôPpRrSsTtUuÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(mnkyr, mnlat)
        return text.translate(trans)

    @staticmethod
    def os(text: str) -> str:
        oskyr = "АаӔӕБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        oslat = "AaÆæBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(oskyr, oslat)
        return text.translate(trans)

    @staticmethod
    def ru(text: str) -> str:
        kyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпРрСсТтУуФфЦцЧчШшЫыЭэ"
        lat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnOoPpRrSsTtUuFfCcČčŠšYyĖė"
        special = {
            "Ъ": '"',
            "ъ": '"',
            "’": '"',
            "Ь": "ʹ",
            "ь": "ʹ",
            "Х": "Ch",
            "х": "ch",
            "Щ": "Šč",
            "щ": "šč",
            "Ю": "Ju",
            "ю": "ju",
            "Я": "Ja",
            "я": "ja",
        }
        trans = str.maketrans(kyr, lat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def sah(text: str) -> str:
        sahkyr = "АаБбВвГгҔҕДдЕеЁёЖжЗзИиЙйКкЛлМмНнҤҥОоӨөПпРрСсҺһТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        sahlat = "AaBbVvGgĞǧDdEeËëŽžZzIiJjKkLlMmNnṄṅOoÔôPpRrSsḤḥTtUuÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(sahkyr, sahlat)
        return text.translate(trans)

    @staticmethod
    def sh(text: str, locale: str) -> str:
        kyr = "АаБбВвГгДдЂђЕеЖжЗзИиЈјКкЛлМмНнОоПпРрСсЌќТтЋћУуФфХхЦцЧчШш"
        lat = "AaBbVvGgDdĐđEeŽžZzIiJjKkLlMmNnOoPpRrSsḰḱTtĆćUuFfHhCcČčŠš"
        special = {"Љ": "Lj", "љ": "lj", "Њ": "Nj", "њ": "nj", "Џ": "Dž", "џ": "dž"}
        trans = str.maketrans(kyr, lat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def tg(text: str) -> str:
        tgkyr = "АаБбВвГгҒғДдЕеЁёЖжЗзИиӢӣЙйКкҚқЛлМмНнОоПпРрСсТтУуӮӯФфХхҲҳЧчҶҷШшЪъЭэЮюЯя"
        tglat = "AaBbVvGgĠġDdEeËëŽžZzIiĪīJjKkĶķLlMmNnOoPpRrSsTtUuŪūFfHhḨḩČčÇçŠšʺʺÈèÛûÂâ"
        trans = str.maketrans(tgkyr, tglat)
        return text.translate(trans)

    @staticmethod
    def tt(text: str) -> str:
        ttkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнҢңОоӨөПпРрСсТтУуҮүФфХхҺһЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        ttlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnṆṇOoÔôPpRrSsTtUuÙùFfHhḤḥCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        special = {"Ә": "A̋", "ә": "a̋", "Җ": "Ž̧", "җ": "ž̧"}
        trans = str.maketrans(ttkyr, ttlat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def tyv(text: str) -> str:
        tyvkyr = "АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнҢңОоӨөПпРрСсТтУуҮүФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        tyvlat = "AaBbVvGgDdEeËëŽžZzIiJjKkLlMmNnṆṇOoÔôPpRrSsTtUuÙùFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        trans = str.maketrans(tyvkyr, tyvlat)
        return text.translate(trans)

    @staticmethod
    def udm(text: str) -> str:
        udmkyr = "АаБбВвГгДдЕеЁёЖжЗзИиӤӥЙйКкЛлМмНнОоӦӧПпРрСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя"
        udmlat = "AaBbVvGgDdEeËëŽžZzIiÎîJjKkLlMmNnOoÖöPpRrSsTtUuFfHhCcČčŠšŜŝʺʺYyʹʹÈèÛûÂâ"
        special = {"Ӝ": "Z̄", "ӝ": "z̄", "Ӟ": "Z̈", "ӟ": "z̈", "Ӵ": "C̈", "ӵ": "c̈"}
        trans = str.maketrans(udmkyr, udmlat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def uk(text: str) -> str:
        kyr = "АаБбВвГгҐґДдЕеЁёЖжЗзИиІіЇїЙйКкЛлМмНнОоПпРрСсТтУуФфЦцЧчШш"
        lat = "AaBbVvHhGgDdEeËëŽžZzYyIiÏïJjKkLlMmNnOoPpRrSsTtUuFfCcČčŠš"
        special = {
            "Ъ": '"',
            "ъ": '"',
            "ʼ": '"',
            "Є": "Je",
            "є": "je",
            "Ь": "ʹ",
            "ь": "ʹ",
            "Х": "Ch",
            "х": "ch",
            "Щ": "Šč",
            "щ": "šč",
            "Ю": "Ju",
            "ю": "ju",
            "Я": "Ja",
            "я": "ja",
        }
        trans = str.maketrans(kyr, lat)
        return "".join(special.get(c, c.translate(trans)) for c in text)

    @staticmethod
    def uum(text: str) -> str:
        uumkyr = "АаБбВвГгҐґДдЕеЖжЗзИиЙйКкЛлМмНнОоӦӧПпРрСсТтУуӰӱФфХхЧчШшЫыЭэ"
        uumlat = "AaBbVvGgǦǧDdEeŽžZzIiJjKkLlMmNnOoÖöPpRrSsTtUuÜüFfHhČčŠšYyÈè"
        special = {"Д'": "Ď", "д'": "ď", "Т'": "Ť", "т'": "ť"}
        res = []
        cp = 0
        strlen = len(text)
        trans = str.maketrans(uumkyr, uumlat)
        while cp < strlen:
            digraph = text[cp : cp + 2]
            if digraph in special:
                res.append(special[digraph])
                cp += 2
            else:
                c = text[cp]
                res.append(c.translate(trans))
                cp += 1
        return "".join(res)

    @staticmethod
    def main(text: str, locale: str) -> str:
        if locale == "ab":
            return Umschrift.ab(text)
        if locale == "abq":
            return Umschrift.abq(text)
        if locale == "ady":
            return Umschrift.ady(text)
        if locale in {"alt", "atv"}:
            return Umschrift.alt(text)
        if locale == "av":
            return Umschrift.av(text)
        if locale == "ba":
            return Umschrift.ba(text)
        if locale == "be":
            return Umschrift.be(text)
        if locale == "bg":
            return Umschrift.bg(text)
        if locale in {"bua", "bxr"}:
            return Umschrift.bua(text)
        if locale == "ce":
            return Umschrift.ce(text)
        if locale == "chm":
            return Umschrift.chm(text)
        if locale == "ckt":
            return Umschrift.ckt(text)
        if locale == "crh":
            return Umschrift.crh(text)
        if locale == "cv":
            return Umschrift.cv(text)
        if locale == "dng":
            return Umschrift.dng(text)
        if locale == "grc":
            return Umschrift.grc(text)
        if locale == "kbd":
            return Umschrift.kbd(text)
        if locale == "kca":
            return Umschrift.kca(text)
        if locale == "kk":
            return Umschrift.kk(text)
        if locale == "kv":
            return Umschrift.kv(text)
        if locale == "krc":
            return Umschrift.krc(text)
        if locale == "ky":
            return Umschrift.ky(text)
        if locale == "mdf":
            return Umschrift.mdf(text)
        if locale == "mk":
            return Umschrift.mk(text)
        if locale == "mn":
            return Umschrift.mn(text)
        if locale == "os":
            return Umschrift.os(text)
        if locale == "ru":
            return Umschrift.ru(text)
        if locale == "sah":
            return Umschrift.sah(text)
        if locale in {"sh", "sr", "bs"}:
            return Umschrift.sh(text, locale)
        if locale == "tg":
            return Umschrift.tg(text)
        if locale == "tt":
            return Umschrift.tt(text)
        if locale == "tyv":
            return Umschrift.tyv(text)
        if locale == "udm":
            return Umschrift.udm(text)
        if locale == "uk":
            return Umschrift.uk(text)
        if locale == "uum":
            return Umschrift.uum(text)
        return ""


def grcZZ(text: str) -> str:
    ZZ = "ΑΒΓΔΕϚΖΗΘΙΚΛΜΝΞΟΠϞΡΣΤΥΦΧΨΩϠ"
    Zahlen = [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80,
        90,
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
    ]
    strlen = len(text)
    mio = tsd = ezh = 0
    Summe = 0

    cp = strlen - 1
    # Einer/Zehner/Hunderter
    if strlen > 0 and text[cp] == "ʹ":
        cp -= 1
        Potenz_zuvor = -1
        go_on = True
        while cp >= 0 and go_on:
            Suche = text[cp].upper()
            try:
                index = ZZ.index(Suche)
            except ValueError:
                index = 18 if Suche == "Ϙ" else -1
            if index >= 0:
                Potenz = index // 9
                if Potenz_zuvor < 0:
                    ezh = Zahlen[index]
                    cp -= 1
                    Potenz_zuvor = Potenz
                elif Potenz > Potenz_zuvor:
                    if cp == 0 or (cp > 0 and text[cp - 1] != "͵"):
                        ezh += Zahlen[index]
                        cp -= 1
                        Potenz_zuvor = Potenz
                    else:
                        go_on = False
                else:
                    go_on = False
            else:
                return f"Falsches Zahlzeichen: {text[cp]}"
        endcp = cp
    else:
        endcp = strlen

    cp = 0
    if strlen > 0 and text[0] != "͵":
        return "Fehlendes Stellenwertsymbol am Beginn"

    Bereich = ""
    while cp < endcp:
        # Millionen
        if text[cp : cp + 2] == "͵͵" or (text[cp] != "͵" and Bereich == "M"):
            if text[cp : cp + 2] == "͵͵":
                cp += 2
            Bereich = "M"
            Suche = text[cp].upper()
            try:
                index = ZZ.index(Suche)
            except ValueError:
                index = 18 if Suche == "Ϙ" else -1
            if index >= 0:
                mio += Zahlen[index]
                cp += 1
            else:
                return f"Falsches Zahlzeichen: {text[cp]}"
        # Tausender
        elif text[cp] == "͵" or Bereich == "T":
            if text[cp] == "͵":
                cp += 1
            Bereich = "T"
            Suche = text[cp].upper()
            try:
                index = ZZ.index(Suche)
            except ValueError:
                index = 18 if Suche == "Ϙ" else -1
            if index >= 0:
                tsd += Zahlen[index]
                cp += 1
            else:
                return f"Falsches Zahlzeichen: {text[cp]}"
        else:
            cp += 1

    Summe = mio * 1_000_000 + tsd * 1_000 + ezh
    res = f"{Summe}"
    strlen = len(res)
    if strlen > 6:
        return f"{res[: strlen - 6]}.{res[strlen - 5 : strlen - 3]}.{res[strlen - 2 :]}"
    elif strlen > 4:
        return f"{res[: strlen - 3]}.{res[strlen - 2 :]}"
    return res


def transliterate(locale: str, text: str) -> str:
    """
    Return the transliterated form of *text*.

    >>> transliterate("ar", "qāt")
    ''
    >>> transliterate("bg", "карам велосипед")
    'karam velosiped'
    >>> transliterate("grc", "ἄλγος")
    'algos'
    >>> transliterate("hi", "tānkh")
    ''
    >>> transliterate("ru", "курган")
    'kurgan'
    >>> transliterate("uk", "Бахмут")
    'Bachmut'
    """
    return Umschrift.main(text, locale)
