import re
from collections import defaultdict

from ... import place
from ...user_functions import concat, extract_keywords_from, italic, ruby
from .langs import langs
from .m_ts import ts
from .transliterator import transliterate


def dot(text: str, data: defaultdict[str, str]) -> str:
    """
    >>> dot("text", defaultdict(str))
    'text。'
    >>> dot("text", defaultdict(str, {"nodot": "1"}))
    'text'
    >>> dot("text", defaultdict(str, {"dot": "!"}))
    'text!'
    """
    if custom_dot := data["dot"]:
        text += custom_dot
    elif not data["nodot"]:
        text += "。"
    return text


def gender_number_specs(parts: str) -> str:
    """
    Source: https://zh.wiktionary.org/wiki/Module:Gender_and_number
    Source: https://zh.wiktionary.org/w/index.php?title=Module:Gender_and_number/data&oldid=8957898

    >>> gender_number_specs("m")
    'm'
    >>> gender_number_specs("m-p")
    'm 複'
    >>> gender_number_specs("m-an-p")
    'm 有生 複'
    >>> gender_number_specs("?-p")
    '? 複'
    >>> gender_number_specs("?!-an-s")
    '性別無記錄 有生 單'
    >>> gender_number_specs("mfbysense-p")
    'm 複 或 f 複 遵詞義'
    >>> gender_number_specs("mfequiv-s")
    'm 單 或 f 單 同義'
    >>> gender_number_specs("mfequiv")
    'm 或 f 同義'
    >>> gender_number_specs("biasp-s")
    '非完 單 或 完 單'
    """
    specs = {
        # Genders
        "m": "m",
        "n": "n",
        "f": "f",
        "gneut": "gn",
        "g!": "性別無記錄",
        "c": "c",
        # Numbers
        "s": "單",
        "d": "雙",
        "num!": "數無記載",
        "p": "複",
        # Animacy
        "an": "有生",
        "in": "無生",
        "an!": "有生性無記錄",
        "pr": "個人",
        "anml": "動物",
        "np": "非個人",
        # Virility
        "vr": "男",
        "nv": "非男",
        # Aspect
        "pf": "完",
        "impf": "非完",
        "asp!": "體貌無記錄",
        # Other
        "?": "?",
        "?!": "性別無記錄",
    }
    specs_combined = {
        "biasp": [specs["impf"], specs["pf"]],
        "mf": [specs["m"], specs["f"]],
        "mfbysense": [specs["m"], specs["f"]],
        "mfequiv": [specs["m"], specs["f"]],
    }
    text = []

    for part in parts.split("-"):
        if part in specs_combined:
            combinations = specs_combined[parts.split("-")[0]]
            spec = specs[parts.split("-")[1]] if "-" in parts else ""
            res = " 或 ".join(f"{a} {b}".strip() for a, b in zip(combinations, [spec] * len(combinations), strict=True))
            if "sense" in part:
                res += " 遵詞義"
            elif "equiv" in part:
                res += " 同義"
            text.append(res)
            return " 單 ".join(text)
        else:
            text.append(specs[part])

    return " ".join(text)


def larger(text: str) -> str:
    return f'<span style="font-size:larger">{text}</span>'


def gloss_tr_poss(data: defaultdict[str, str], gloss: str, *, trans: str = "") -> str:
    more = []
    text = ""
    trts = ""
    if (tr := data["tr"]) and tr != "-":
        trts += italic(tr)
    if data["ts"]:
        if trts:
            trts += " "
        trts += f"/{data['ts']}/"
    if trts:
        more.append(trts)
    if trans:
        more.append(italic(trans))
    if gloss:
        more.append(f"“{gloss}”")
    if data["pos"]:
        more.append(data["pos"])
    if data["lit"]:
        more.append(f"字面意思為“{data['lit']}”")
    if more:
        text += f" ({concat(more, ', ')})"
    return text


def zh_meaning(parts: list[str]) -> tuple[str, str, list[str]]:
    trad, simp = [], []
    trans: list[str] = []

    for arg in parts:
        if tr := transliterate("zh", arg):
            trans.append(tr)
        part = arg.lstrip("^")
        trad.append(part)
        simp.append(ts(part))

    return "".join(trad), "".join(simp), trans


def render_cmn_erhua_form_of(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cmn_erhua_form_of("cmn-erhua form of", [""], defaultdict(str), word="一丁點兒")
    '(官話) 一丁點／一丁点 的兒化形式。'
    >>> render_cmn_erhua_form_of("cmn-erhua form of", ["foo"], defaultdict(str), word="一丁點兒")
    '(官話) 一丁點／一丁点 (“foo”) 的兒化形式。'
    """
    label = "" if data["nolb"] else "(官話) "
    data["notext"] = "1"
    if parts:
        data["t"] = parts[0]
    return f"{label}{render_zh_l(tpl, [word[:-1]], data)} 的兒化形式。"


def render_foreign_derivation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_foreign_derivation("back-formation", ["zh"], defaultdict(str))
    '逆構詞'
    >>> render_foreign_derivation("back-formation", ["zh", "咕嚕肉"], defaultdict(str))
    '<span style="font-size:larger">咕嚕肉／咕噜肉</span> 的逆構詞'

    >>> render_foreign_derivation("bor", ["zh", "en", "sandwich"], defaultdict(str))
    '英語 <span style="font-size:larger">sandwich</span>'
    >>> render_foreign_derivation("bor+", ["zh", "en", "sandwich"], defaultdict(str))
    '借自英語 <span style="font-size:larger">sandwich</span>'

    >>> render_foreign_derivation("calque", ["zh", "sa", "महायान"], defaultdict(str))
    '仿譯自梵語 <span style="font-size:larger">महायान</span>'

    >>> render_foreign_derivation("cog", ["mkh-vie-pro", "*-taːw", "", "刀"], defaultdict(str))
    '原始越語 *-taːw (“刀”)'

    >>> render_foreign_derivation("der", ["zh", "en", "sandwich"], defaultdict(str))
    '英語 <span style="font-size:larger">sandwich</span>'
    >>> render_foreign_derivation("der+", ["zh", "en", "sandwich"], defaultdict(str))
    '派生自英語 <span style="font-size:larger">sandwich</span>'

    >>> render_foreign_derivation("etyl", ["ru", "zh"], defaultdict(str))
    '俄語'

    >>> render_foreign_derivation("inh", ["zh", "sit-pro", "*m-daj ~ m-di"], defaultdict(str))
    '原始漢藏語 *m-daj ~ m-di'
    >>> render_foreign_derivation("inh+", ["zh", "sit-pro", "*m-daj ~ m-di"], defaultdict(str))
    '繼承自原始漢藏語 *m-daj ~ m-di'

    >>> render_foreign_derivation("l", ["en", "VIP"], defaultdict(str))
    '<span style="font-size:larger">VIP</span>'

    >>> render_foreign_derivation("lbor", ["zh", "la", "Epicūrus"], defaultdict(str))
    '古典借詞，源自拉丁語 <span style="font-size:larger">Epicūrus</span>'

    >>> render_foreign_derivation("m", ["mnc", "ᠰᠠᡳᠴᡠᠩᡤᠠ ᡶᡝᠩᡧᡝᠨ"], defaultdict(str))
    '<span style="font-size:larger">ᠰᠠᡳᠴᡠᠩᡤᠠ ᡶᡝᠩᡧᡝᠨ</span>'
    >>> render_foreign_derivation("m+", ["mnc", "ᠰᠠᡳᠴᡠᠩᡤᠠ ᡶᡝᠩᡧᡝᠨ"], defaultdict(str))
    '滿語 <span style="font-size:larger">ᠰᠠᡳᠴᡠᠩᡤᠠ ᡶᡝᠩᡧᡝᠨ</span>'

    >>> render_foreign_derivation("ncog", ["nan-hbl", "跤"], defaultdict(str))
    '泉漳話 <span style="font-size:larger">跤</span>'

    >>> render_foreign_derivation("obor", ["zh", "ja", "-"], defaultdict(str))
    '形譯詞自日語'
    >>> render_foreign_derivation("obor", ["zh", "ja", "aaaa"], defaultdict(str))
    '形譯詞，源自日語 <span style="font-size:larger">aaaa</span>'

    >>> render_foreign_derivation("pcal", ["zh", "en", "Eiffel Tower"], defaultdict(str))
    '部分仿譯自英語 <span style="font-size:larger">Eiffel Tower</span>'

    >>> render_foreign_derivation("psm", ["zh", "en", "DotA"], defaultdict(str))
    '音義兼譯自英語 <span style="font-size:larger">DotA</span>'

    >>> render_foreign_derivation("semantic loan", ["zh", "en", "forget-me-not"], defaultdict(str))
    '意譯自英語 <span style="font-size:larger">forget-me-not</span>'

    >>> render_foreign_derivation("transliteration", ["zh", "ru", "Пу́тин"], defaultdict(str))
    '音譯自俄語 <span style="font-size:larger">Пу́тин</span>'
    """
    tpl = tpl.lower()

    mentions = (
        "back-formation",
        "backformation",
        "back-form",
        "backform",
        "bf",
        "l",
        "l-lite",
        "link",
        "ll",
        "mention",
        "m",
        "m-lite",
    )
    dest_lang_ignore = (
        "cog",
        "cog-lite",
        "cognate",
        "etyl",
        # "false cognate",
        # "fcog",
        # "langname-mention",
        "m+",
        "nc",
        "ncog",
        "noncog",
        "noncognate",
        *mentions,
    )
    if tpl not in dest_lang_ignore and parts:
        parts.pop(0)  # Remove the destination language

    is_back_formation = tpl in {"back-formation", "backformation", "back-form", "backform", "bf"}
    dst_locale = parts.pop(0) if parts else data["2"]

    if tpl == "etyl" and parts:
        parts.pop(0)

    phrase = ""
    starter = ""
    if not data["notext"]:
        if tpl in {"bor+"}:
            starter = "借自"
        # elif tpl in {"adapted borrowing", "abor"}:
        #     if is_from := bool(parts and parts[0] == "-"):
        #         parts.pop(0)
        #     starter = "同化借詞 " + ("from " if is_from else "of ")
        elif tpl in {"calque", "cal", "clq"}:
            starter = "仿譯自"
        elif tpl in {"der+"}:
            starter = "派生自"
        # if tpl in {"false cognate", "fcog"}:
        #     starter = "false cognate of "
        elif tpl in {"inh+"}:
            starter = "繼承自"
        elif tpl in {"partial calque", "pcal", "pclq"}:
            starter = "部分仿譯自"
        elif tpl in {"semantic loan", "sl"}:
            starter = "意譯自"
        elif tpl in {"learned borrowing", "lbor"}:
            starter = "古典借詞，源自"
        # elif tpl in {"semi-learned borrowing", "slbor"}:
        #     starter = "semi-learned borrowing from "
        elif tpl in {"orthographic borrowing", "obor"}:
            starter = "形譯詞，源自" if parts and parts[0] != "-" else "形譯詞自"
        # elif tpl in {"unadapted borrowing", "ubor"}:
        #     starter = "unadapted borrowing from "
        elif tpl in {"phono-semantic matching", "psm"}:
            starter = "音義兼譯自"
        elif tpl in {"transliteration", "translit"}:
            starter = "音譯自"
        elif is_back_formation:
            starter = " 的逆構詞" if parts else "逆構詞"

    lang = "translingual" if dst_locale == "mul" else langs.get(dst_locale, "")
    if tpl not in mentions:
        phrase += lang

    if parts or data["3"]:
        word = parts.pop(0) if parts else data["3"]
        if word.startswith("w:"):
            word = word[2:]
        if word == "-":
            return f"{starter}{phrase}"
        if "//" in word:
            word = word.replace("//", " / ")
    else:
        word = ""

    word = data["alt"] or word

    if parts:
        word = parts.pop(0) or word  # 4, alt=

    if dst_locale == "zh":
        word = render_zh_l(tpl, [word], data)

    if word:
        phrase += f" {word if word.startswith('*') else larger(word)}"

    if data["g"]:
        phrase += f" {gender_number_specs(data['g'])}"

    gloss = parts.pop(0) if parts else data["t"] or data["gloss"]
    trans = "" if data["tr"] else transliterate(dst_locale, word)
    phrase += gloss_tr_poss(data, gloss, trans=trans)
    phrase = phrase.lstrip()

    return f"{phrase}{starter}" if is_back_formation else f"{starter}{phrase}"


def render_ja_r(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_ja_r("ja-r", ["羨ましい"], defaultdict(str))
    '羨ましい'
    >>> render_ja_r("ja-r", ["羨ましい", "羨ましい"], defaultdict(str))
    '羨ましい'
    >>> render_ja_r("ja-r", ["羨ましい", "うらやましい"], defaultdict(str))
    '<ruby>羨ましい<rt>うらやましい</rt></ruby>'
    >>> render_ja_r("ja-r", ["羨ましい", "うらやましい", "a"], defaultdict(str, {"lit": "lit"}))
    '<ruby>羨ましい<rt>うらやましい</rt></ruby> (“a”, 字面意思為“lit”)'
    >>> render_ja_r("ja-r", ["羨ましい", "", "a"], defaultdict(str, {"lit": "lit"}))
    '羨ましい (“a”, 字面意思為“lit”)'

    >>> render_ja_r("ja-r", ["任天堂", "^ニンテンドー"], defaultdict(str))
    '<ruby>任天堂<rt>ニンテンドー</rt></ruby>'

    >>> render_ja_r("ja-r", ["物%の%哀れ", "もの %の% あわれ"], defaultdict(str))
    '<ruby>物<rt>もの</rt></ruby>の<ruby>哀れ<rt>あわれ</rt></ruby>'
    >>> render_ja_r("ja-r", ["物 の 哀れ", "もの の あわれ"], defaultdict(str))
    '<ruby>物<rt>もの</rt></ruby>の<ruby>哀れ<rt>あわれ</rt></ruby>'

    >>> render_ja_r("ryu-r", ["唐手", "とーでぃー"], defaultdict(str, {"t": "Chinese hand"}))
    '<ruby>唐手<rt>とーでぃー</rt></ruby> (“Chinese hand”)'

    >>> render_ja_r("ja-compound", ["唐手", "とーでぃー"], defaultdict(str, {"t": "Chinese hand", "noquote": "1"}))
    '<ruby>唐手<rt>とーでぃー</rt></ruby> (Chinese hand)'
    """
    if len(parts) == 1 or not parts[1]:
        text = parts[0]
    elif parts[0] == parts[1]:
        text = parts[0]
    else:
        parts[1] = parts[1].removeprefix("^")

        if sep := "%" if "%" in parts[0] else " " if " " in parts[0] else "":
            texts = [part.strip() for part in parts[0].split(sep)]
            tops = [part.strip() for part in parts[1].split(sep)]
            text = "".join(t if t == p else ruby(t, p) for t, p in zip(texts, tops))
        else:
            text = ruby(parts[0], parts[1])

    more: list[str] = []
    if len(parts) > 2:
        more.append(f"“{parts[2]}”")
    if lit := data["lit"]:
        more.append(f"字面意思為“{lit}”")
    if t := data["t"] or transliterate("ja", parts[0]):
        more.append(t if data["noquote"] else f"“{t}”")
    if more:
        text += f" ({', '.join(more)})"

    return text


def render_name_translit(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_name_translit("name translit", ["zh", "en,en,en", "Cubitt", "more"], defaultdict(str, {"type": "姓氏", "eq": "eq", "t": "t", "tr": "tr", "xlit": "xlit"}))
    '英語、英語和英語姓氏 <i>Cubitt</i> (tr，“t”)，xlit 的轉寫，等同於 eq；或來自<i>more</i> 的轉寫'

    >> render_name_translit("foreign name", ["zh", "en"], defaultdict(str, {"type": "父名"}))
    '父名於英語'
    >>> render_name_translit("foreign name", ["zh", "pl", "Wałęsa", "name2", "name3"], defaultdict(str, {"type": "男性名字", "xlit": "xlit", "eq": "eq"}))
    '男性名字於波蘭語，<i>Wałęsa</i>，xlit，等同於 eq；或來自<i>name2</i>；或來自<i>name3</i>'
    """
    tpl = tpl.lower().replace("-", " ")
    parts.pop(0)  # Destination language
    src_langs = parts.pop(0)
    src_lang = src_langs.split(",", 1)[0]

    origins = concat([langs[src_lang.strip()] for src_lang in src_langs.split(",")], sep="、", last_sep="和")
    text = f"{origins}{data['type']}" if tpl == "name translit" else f"{data['type']}於{origins}"
    if not parts:
        return text

    what = parts.pop(0)
    tr = data["tr"] or transliterate(src_lang, what)
    t = data["t"]
    xlit = data["xlit"]
    eq = data["eq"]

    text += f" {italic(what)}" if tpl == "name translit" else f"，{italic(what)}"
    if tr:
        text += f" ({tr}，“{t}”)" if t else f" ({t})"
    elif t:
        text += f" ({t})"

    if xlit := data["xlit"]:
        text += f"，{xlit}"
        if tpl == "name translit":
            text += " 的轉寫"

    if eq := data["eq"]:
        text += f"，等同於 {eq}"

    while parts:
        text += f"；或來自{italic(parts[0])}"
        if transliterated := transliterate(src_lang, parts.pop(0)):
            text += f" ({transliterated})"

    if tpl == "name translit":
        text += " 的轉寫"

    return text


def render_och_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_och_l("och-l", ["悠"], defaultdict(str))
    '悠 (上古)'
    >>> render_och_l("och-l", ["悠", "some def"], defaultdict(str))
    '悠 (上古, “some def”)'
    """
    text = f"{parts[0]} (上古"
    if tr := transliterate("och", parts.pop(0)):
        text += f", <i>{tr}</i>"
    if parts:
        text += f", “{parts[0]}”"
    return f"{text})"


def render_place(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_place("place", ["zh", "軍事基地", "南部", "s/內華達", "c/美國"], defaultdict(str))
    '軍事基地名，位於美國內華達州南部'
    """
    return place.get(parts, data, "zh")


def render_surname(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_surname("surname", ["zh"], defaultdict(str))
    '姓氏'
    >>> render_surname("surname", [], defaultdict(str, {"lang": "zh"}))
    '姓氏'
    >>> render_surname("surname", ["zh", ""], defaultdict(str))
    '姓氏'
    >>> render_surname("surname", ["zh", "rare"], defaultdict(str))
    'rare姓氏'
    >>> render_surname("surname", ["zh", "rare"], defaultdict(str, {"from":"丹麥語", "from2": "挪威語", "g": "c", "xlit": "xlit", "m": "m", "f": "f", "eq": "eq"}))
    '源自丹麥語和挪威語的通性rare姓氏，xlit，陽性等價詞 m，陰性等價詞 f，等價於英語eq'
    """
    if parts:
        parts.pop(0)  # Remove the lang

    text: list[str] = []

    # Note: the order is important
    has_from_attr = False
    for attr, prefix in [
        ("from", "源自"),
        ("from2", "和"),
    ]:
        if val := data[attr]:
            text.append(f"{prefix}{val}")
            has_from_attr = True
    if has_from_attr:
        text.append("的")

    if gender := data["g"]:
        # Source: https://zh.wiktionary.org/w/index.php?title=Module:Names&oldid=9294843#L-705--L-721
        text.append(
            {"unisex": "通性", "common gender": "通性", "c": "通性", "m": "男性", "f": "女性"}.get(gender, "性別不明")
        )

    if parts:
        text.append(parts[0])
    text.append("姓氏")

    # Note: the order is important
    for attr, prefix in [
        ("xlit", ""),
        ("m", "陽性等價詞 "),
        ("f", "陰性等價詞 "),
        ("eq", "等價於英語"),
    ]:
        if val := data[attr]:
            text.append(f"，{prefix}{val}")

    return "".join(text)


def render_zh_altname(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_altname("zh-alt-name", ["七邊形"], defaultdict(str))
    '七邊形／七边形的別名。'
    """
    return f"{render_zh_l(tpl, parts, data, word=word)}的別名。"


def render_zh_div(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    Source: https://zh.wiktionary.org/w/index.php?title=Module:Zh/templates&oldid=9109462#L-205

    >>> render_zh_div("zh-div", ["市"], defaultdict(str))
    '(～市)'
    >>> render_zh_div("zh-div", ["市"], defaultdict(str, {"f": "縣"}))
    '(～市，舊稱～縣)'
    """
    result = []
    for i, part in enumerate(parts, 1):
        if i != 1:
            result.append("separator ")
        result.append(f"～{part}")
        if i == 1 and (f := data["f"]):
            j = 2
            result.append(f"，舊稱～{f}")
            while ff := data[f"f{j}"]:
                result.append(f"，～{ff}")
                j += 1

    joined = "".join(result)
    sep = ";" if "formerly" in joined else ","
    joined = joined.replace("separator", sep)
    return f"({joined})"


def render_zh_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_l("zh-l", ["一丁點"], defaultdict(str))
    '一丁點／一丁点'
    >>> render_zh_l("zh-l", ["一丁點", "foo"], defaultdict(str, {"lit": "lit", "t": "t", "tr": "tr"}))
    '一丁點／一丁点 (<i>tr</i>, “t”, 字面意思為“lit”)'
    """
    trad, simp, trans = zh_meaning([parts.pop(0)])

    text = f"{trad}{f'／{simp}' if trad != simp else ''}"
    tr = data["tr"] or parts.pop(0) if parts else " ".join(trans)
    gl = data["t"] or (parts.pop(0) if parts else "")
    if not tr and not gl and not data["lit"]:
        return text

    text += " ("
    if tr:
        text += italic(tr)
    if gl:
        if tr:
            text += ", "
        text += f"“{gl}”"
    if data["lit"]:
        if tr:
            text += ", 字面意思為"
        text += f"“{data['lit']}”"
    text += ")"
    return text


def render_zh_mw(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    Source: https://zh.wiktionary.org/w/index.php?title=Module:Zh/templates&oldid=9109462#L-107

    >>> render_zh_mw("zh-mw", ["位"], defaultdict(str))
    '<span style="padding-left:15px;font-size:80%">(量詞：位)</span>'
    >>> render_zh_mw("zh-mw", ["m:臺", "m,c:部"], defaultdict(str))
    '<span style="padding-left:15px;font-size:80%">(量詞：臺 官；部 官 粵)</span>'
    """
    lang_abbrev_alt = {
        "m": "官",
        "c": "粵",
        "g": "贛",
        "h": "客",
        "j": "晉",
        "mb": "北",
        "md": "東",
        "px": "莆",
        "mn": "南",
        "mn-t": "潮",
        "mn-l": "雷",
        "w": "吳",
        "x": "湘",
    }
    result = []
    for part in parts:
        subparts = part.split(":")
        note = "".join(f" {lang_abbrev_alt[d]}" for d in subparts[0].split(",")) if len(subparts) == 2 else ""
        result.append((subparts[1] if len(subparts) == 2 else subparts[0]) + note)
    return f'<span style="padding-left:15px;font-size:80%">(量詞：{"；".join(result)})</span>'


def render_zh_short(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    Source: https://zh.wiktionary.org/w/index.php?title=Module:Zh/templates&oldid=9109462#L-239

    >>> render_zh_short("zh-short", ["一剎那"], defaultdict(str))
    '一剎那／一刹那 的簡稱。'
    >>> render_zh_short("zh-short", ["一剎那", "foo"], defaultdict(str, {"lit": "lit", "tr": "tr"}))
    '一剎那foo／一刹那foo (tr) 的簡稱。'
    """
    pinyin = data["tr"]
    gloss = re.sub(r"[\u200b\u200c]", "", data["t"])
    notext = data["notext"]
    comb = data["and"]
    noterm = not parts
    anno = []

    start = ""

    if comb:
        return f"{start}{' + '.join(parts)}{f': “{gloss}”' if gloss else ''}"

    trad, simp, trans = zh_meaning(parts)

    pinyin_val = pinyin if pinyin and pinyin != "-" else (" ".join(trans) if len(trans) == len(trad) else "")
    if pinyin_val:
        anno.append(pinyin_val)

    if gloss:
        anno.append(f"“{gloss}”")

    return (
        ("" if notext else start)
        + ("" if noterm else trad + (f"／{simp}" if trad != simp else ""))
        + (f" ({', '.join(anno)})" if (pinyin_val or gloss) else "")
        + " 的簡稱。"
    )


def render_zh_x(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_x("zh-x", ["今 大 富浪沙 國 大 皇帝、大 衣坡儒 國 大 皇帝、大南 國 大 皇帝 切 願 將 三 國 不 協 之 處 調和，以 敦 永 好。", "The Emperor of France, Emperor of Spain, and Emperor of Đại Nam hereby urgently express their wish to conciliate the dispute and achieve longlasting peace."], defaultdict(str))
    '<dl><dt>今 大 富浪沙 國 大 皇帝、大 衣坡儒 國 大 皇帝、大南 國 大 皇帝 切 願 將 三 國 不 協 之 處 調和，以 敦 永 好。</dt><dd><i>The Emperor of France, Emperor of Spain, and Emperor of Đại Nam hereby urgently express their wish to conciliate the dispute and achieve longlasting peace.</i></dd></dl>'
    >>> render_zh_x("zh-x", [], defaultdict(str, {"1": "今 大 富浪沙 國 大 皇帝、大 衣坡儒 國 大 皇帝、大南 國 大 皇帝 切 願 將 三 國 不 協 之 處 調和，以 敦 永 好。", "2": "The Emperor of France, Emperor of Spain, and Emperor of Đại Nam hereby urgently express their wish to conciliate the dispute and achieve longlasting peace."}))
    '<dl><dt>今 大 富浪沙 國 大 皇帝、大 衣坡儒 國 大 皇帝、大南 國 大 皇帝 切 願 將 三 國 不 協 之 處 調和，以 敦 永 好。</dt><dd><i>The Emperor of France, Emperor of Spain, and Emperor of Đại Nam hereby urgently express their wish to conciliate the dispute and achieve longlasting peace.</i></dd></dl>'
    """
    form = data["1"] or parts.pop(0)
    trans = data["2"] or (parts[0] if parts else "")
    return "" if not trans else f"<dl><dt>{form}</dt><dd><i>{trans}</i></dd></dl>"


def render_粵(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_粵("粵", [], defaultdict(str))
    '〈粵〉'
    >>> render_粵("粵", [], defaultdict(str, {"无": "1"}))
    '粵'
    >>> render_粵("粵", ["客家", "客家"], defaultdict(str))
    '〈粵／客家／客家〉'
    """
    text = concat(["粵", *parts], "／")
    return text if data["无"] else f"〈{text}〉"


template_mapping = {
    "och-l": render_och_l,
    "ja-r": render_ja_r,
    "place": render_place,
    "zh-div": render_zh_div,
    "zh-mw": render_zh_mw,
    "zh-x": render_zh_x,
    "粵": render_粵,
    **dict.fromkeys(
        {
            "adapted borrowing",
            "abor",
            "back-formation",
            "backform",
            "backformation",
            "back-form",
            "bf",
            "borrowed",
            "bor",
            "Bor",
            "bor-lite",
            "bor+",
            "Bor+",
            "calque",
            "cal",
            "clq",
            "cognate",
            "cog",
            "cog-lite",
            "derived",
            "der",
            "der+",
            "der-lite",
            "etyl",
            "false cognate",
            "fcog",
            "inherited",
            "inh-lite",
            "inh",
            "inh+",
            "l",
            "l-lite",
            "langname-mention",
            "learned borrowing",
            "lbor",
            "link",
            "ll",
            "mention",
            "m",
            "m+",
            "m-lite",
            "noncognate",
            "nc",
            "ncog",
            "noncog",
            "obor",
            "orthographic borrowing",
            "partial calque",
            "pcal",
            "pclq",
            "phono-semantic matching",
            "psm",
            "semantic loan",
            "semi-learned borrowing",
            "sl",
            "slbor",
            "transliteration",
            "translit",
            "unadapted borrowing",
            "ubor",
            "uder",
        },
        render_foreign_derivation,
    ),
    **dict.fromkeys({"cmn-erhua form of", "Cmn-erhua form of", "zh-erhua form of"}, render_cmn_erhua_form_of),
    **dict.fromkeys({"foreign name", "name translit", "Name translit"}, render_name_translit),
    **dict.fromkeys({"surname", "patronymic"}, render_surname),
    **dict.fromkeys({"zh-altname", "Zh-altname", "zh-alt-name", "Zh-alt-name", "中文別名"}, render_zh_altname),
    **dict.fromkeys({"zh-l", "zh-m"}, render_zh_l),
    **dict.fromkeys(
        {"zh-short", "Zh-short", "zh-short-comp", "Zh-short-comp", "zh-etym-short", "Zh-etym-short"}, render_zh_short
    ),
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
