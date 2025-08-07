import re
from collections import defaultdict

from ...user_functions import chinese, concat, extract_keywords_from, italic, strong
from .langs import langs
from .m_ts import ts


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
    result = []

    for part in parts.split("-"):
        if part in specs_combined:
            combinations = specs_combined[parts.split("-")[0]]
            spec = specs[parts.split("-")[1]] if "-" in parts else ""
            res = " 或 ".join(f"{a} {b}".strip() for a, b in zip(combinations, [spec] * len(combinations), strict=True))
            if "sense" in part:
                res += " 遵詞義"
            elif "equiv" in part:
                res += " 同義"
            result.append(res)
            return " 單 ".join(result)
        else:
            result.append(specs[part])

    return " ".join(result)


def gloss_tr_poss(data: defaultdict[str, str], gloss: str, *, trans: str = "") -> str:
    local_phrase = []
    phrase = ""
    trts = ""
    if (tr := data["tr"]) and tr != "-":
        trts += italic(tr)
    if data["ts"]:
        if trts:
            trts += " "
        trts += f"/{data['ts']}/"
    if trts:
        local_phrase.append(trts)
    if trans:
        local_phrase.append(italic(trans))
    if gloss:
        local_phrase.append(f"“{gloss}”")
    if data["pos"]:
        local_phrase.append(data["pos"])
    if data["lit"]:
        local_phrase.append(f"literally “{data['lit']}”")
    if local_phrase:
        phrase += f" ({concat(local_phrase, ', ')})"
    return phrase


def render_cmn_erhua_form_of(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_cmn_erhua_form_of("cmn-erhua form of", [""], defaultdict(str), word="一丁點兒")
    '(官話) 一丁點／一丁点 的兒化形式。'
    >>> render_cmn_erhua_form_of("cmn-erhua form of", ["foo"], defaultdict(str), word="一丁點兒")
    '(官話) 一丁點／一丁点 (“foo”) 的兒化形式。'
    """
    # TO DO: transliterations
    label = "" if data["nolb"] else "(官話) "
    data["notext"] = "1"
    if parts:
        data["t"] = parts[0]
    return f"{label}{render_zh_short(tpl, [word[:-1]], data)}{dot(' 的兒化形式', data)}"


def render_foreign_derivation(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_foreign_derivation("bor", ["zh", "en", "sandwich"], defaultdict(str))
    '英語 <i>sandwich</i>'
    >>> render_foreign_derivation("bor+", ["zh", "en", "sandwich"], defaultdict(str))
    '借自英語 <i>sandwich</i>'

    >>> render_foreign_derivation("der", ["zh", "en", "sandwich"], defaultdict(str))
    '英語 <i>sandwich</i>'
    >>> render_foreign_derivation("der+", ["zh", "en", "sandwich"], defaultdict(str))
    '派生自英語 <i>sandwich</i>'
    """
    # Short path for the {{m|en|WORD}} template
    if tpl in {"m", "m-lite"} and len(parts) == 2 and not data:
        word = parts[1]
        if word.startswith("w:"):
            word = word[2:]
        return strong(word) if parts[0] in {"en", "mul"} else italic(word)

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
        "false cognate",
        "fcog",
        "langname-mention",
        "m+",
        "nc",
        "ncog",
        "noncog",
        "noncognate",
        *mentions,
    )
    if tpl not in dest_lang_ignore and parts:
        parts.pop(0)  # Remove the destination language

    dst_locale = parts.pop(0) if parts else data["2"]

    if tpl == "etyl" and parts:
        parts.pop(0)

    phrase = ""
    starter = ""
    if data["notext"] != "1":
        if tpl in {"bor+"}:
            starter = "借自"
        # elif tpl in {"adapted borrowing", "abor"}:
        #     if is_from := bool(parts and parts[0] == "-"):
        #         parts.pop(0)
        #     starter = "同化借詞 " + ("from " if is_from else "of ")
        # elif tpl in {"calque", "cal", "clq"}:
        #     starter = "calque of "
        if tpl in {"der+"}:
            starter = "派生自"
        # if tpl in {"false cognate", "fcog"}:
        #     starter = "false cognate of "
        # elif tpl in {"inh+"}:
        #     starter = "inherited from "
        # elif tpl in {"partial calque", "pcal", "pclq"}:
        #     starter = "partial calque of "
        # elif tpl in {"semantic loan", "sl"}:
        #     starter = "semantic loan of "
        # elif tpl in {"learned borrowing", "lbor"}:
        #     starter = "learned borrowing from "
        # elif tpl in {"semi-learned borrowing", "slbor"}:
        #     starter = "semi-learned borrowing from "
        # elif tpl in {"orthographic borrowing", "obor"}:
        #     starter = "orthographic borrowing from "
        # elif tpl in {"unadapted borrowing", "ubor"}:
        #     starter = "unadapted borrowing from "
        # elif tpl in {"phono-semantic matching", "psm"}:
        #     starter = "phono-semantic matching of "
        # elif tpl in {"transliteration", "translit"}:
        #     starter = "transliteration of "
        # elif tpl in {"back-formation", "backformation", "back-form", "backform", "bf"}:
        #     starter = "back-formation"
        #     if parts:
        #         starter += " from"
        phrase = starter if data["nocap"] == "1" else starter.capitalize()

    lang = "translingual" if dst_locale == "mul" else langs.get(dst_locale, "")
    phrase += lang if tpl not in mentions else ""

    if parts or data["3"]:
        word = parts.pop(0) if parts else data["3"]
        if word.startswith("w:"):
            word = word[2:]
        if word == "-":
            return phrase
        if "//" in word:
            word = word.replace("//", " / ")
    else:
        word = ""

    word = data["alt"] or word
    gloss = data["t"] or data["gloss"]

    if parts:
        word = parts.pop(0) or word  # 4, alt=

    if tpl in {"l", "l-lite", "link", "ll"}:
        phrase += f" {word}"
    elif word:
        if (
            (starter == "partial calque of " and dst_locale in {"mul", "zh"})
            or starter == "adapted borrowing of "
            or dst_locale in {"ar", "ja"}
        ):
            phrase += f" {word}"
        else:
            phrase += f" {italic(word)}"
    if data["g"]:
        phrase += f" {gender_number_specs(data['g'])}"
    trans = ""  # trans = "" if data["tr"] else transliterate(dst_locale, word)
    if parts:
        gloss = parts.pop(0)  # 5, t=, gloss=

    phrase += gloss_tr_poss(data, gloss, trans=trans)

    return phrase.lstrip()


def render_och_l(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_och_l("och-l", ["悠"], defaultdict(str))
    '悠 (上古)'
    >>> render_och_l("och-l", ["悠", "some def"], defaultdict(str))
    '悠 (上古, “some def”)'
    """
    # TO DO: transliteration
    text = f"{parts.pop(0)} (上古"
    if parts:
        text += f", “{parts[0]}”"
    return f"{text})"


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
    >>> render_zh_l("zh-l", ["痟", "mad"], defaultdict(str, {"tr": "siáu"}))
    '痟 (<i>siáu</i>, “mad”)'
    """
    # TO DO: add transliterations (ex: https://zh.wiktionary.org/wiki/2019冠狀病毒病)
    return chinese(parts, data)


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


def render_zh_pron(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    >>> render_zh_pron("zh-pron", [], defaultdict(str, {"m": "huángmǎguà,er=y", "c": "wong4 maa5 kwaa3-2", "cat": "n"}))
    '官話: huángmǎguà\\n粵語: wong<sup>4</sup> maa<sup>5</sup> kwaa<sup>3-2</sup>'
    """
    text: list[str] = []

    if mandarin := data["m"]:
        pron = mandarin.split(",", 1)[0]
        text.append(f"官話: {pron}")

    if cantonese := data["c"]:
        pron = re.sub(r"([\d\-]+)", r"<sup>\1</sup>", cantonese)
        text.append(f"粵語: {pron}")

    return "\n".join(text)


def render_zh_short(tpl: str, parts: list[str], data: defaultdict[str, str], *, word: str = "") -> str:
    """
    Source: https://zh.wiktionary.org/w/index.php?title=Module:Zh/templates&oldid=9109462#L-239

    >>> render_zh_short("zh-short", ["一剎那"], defaultdict(str))
    '一剎那／一刹那'
    >>> render_zh_short("zh-short", ["一剎那"], defaultdict(str, {"tr": "siáu"}))
    '一剎那／一刹那 (siáu)'
    """
    # TO DO: transliterations
    pinyin = data["tr"]
    gloss = re.sub(r"[\u200b\u200c]", "", data["t"])
    notext = data["notext"]
    comb = data["and"]
    noterm = not parts
    tr: list[str] = []
    t, s, anno = [], [], []

    start = ""

    if comb:
        return f"{start}{' + '.join(parts)}{f': “{gloss}”' if gloss else ''}"

    for arg in parts:
        # if not pinyin and (trans := transliterate("zh", arg)):
        #     tr.append(trans)
        part = arg.lstrip("^")
        t.append(part)
        s.append(ts(part))

    trad = "".join(t)
    simp = "".join(s)

    pinyin_val = pinyin if pinyin != "-" else (" ".join(tr) if len(tr) == len(t) else "")
    if pinyin_val:
        anno.append(pinyin_val)

    if gloss:
        anno.append(f"“{gloss}”")

    return (
        ("" if notext else start)
        + ("" if noterm else trad + (f"／{simp}" if trad != simp else ""))
        + (f" ({', '.join(anno)})" if (pinyin_val or gloss) else "")
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
    if not trans:
        return ""
    return f"<dl><dt>{form}</dt><dd><i>{trans}</i></dd></dl>"


template_mapping = {
    "och-l": render_och_l,
    "zh-div": render_zh_div,
    "zh-mw": render_zh_mw,
    "zh-pron": render_zh_pron,
    "zh-x": render_zh_x,
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
            "bor-lite",
            "bor+",
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
    **dict.fromkeys({"cmn-erhua form of", "zh-erhua form of"}, render_cmn_erhua_form_of),
    **dict.fromkeys({"zh-l", "zh-m"}, render_zh_l),
    **dict.fromkeys({"zh-short", "Zh-short-comp"}, render_zh_short),
}


def lookup_template(tpl: str) -> bool:
    return tpl in template_mapping


def render_template(word: str, template: tuple[str, ...]) -> str:
    tpl, *parts = template
    data = extract_keywords_from(parts)
    return template_mapping[tpl](tpl, parts, data, word=word)
