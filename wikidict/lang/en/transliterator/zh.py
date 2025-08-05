"""
Python conversion of the zh-translit module.
Link:
  - https://en.wiktionary.org/wiki/Module:zh-translit

Current version from 2025-04-10 06:45
  - https://en.wiktionary.org/w/index.php?title=Module:zh-translit&oldid=84517680
  - [1] https://en.wiktionary.org/w/index.php?title=Module:zh/data/cmn-tag&oldid=85080649
"""

import re

from ..pronunciations import cmn, gan, yue

# Source: [1]
MT = {
    "腌": ["ā", "āng"],
    "癌": ["ái", "yán"],
    "挨": ["ái", "āi"],
    "胺": ["àn", "ān"],
    "鮟": ["ān", "àn"],
    "𩽾": ["ān", "àn"],
    "銨": ["ǎn", "ān"],
    "铵": ["ǎn", "ān"],
    "熬": ["āo", "áo"],
    "驁": ["ào", "áo"],
    "骜": ["ào", "áo"],
    "陂": ["bēi", "pí"],
    "鈸": ["bó", "bá"],
    "钹": ["bó", "bá"],
    "亳": ["bó", "bò"],
    "伯": ["bǎi", "bāi"],
    "白": ["bái", "bó"],
    "柏": ["bǎi", "bó"],
    "暴": ["bào", "pù"],
    "曝": ["bào", "pù"],
    "傍": ["bàng", "bāng"],
    "比": ["bǐ", "bì"],
    "吡": ["bǐ", "bì"],
    "檳": ["bīng", "bīn"],
    "播": ["bō", "bò"],
    "薄": ["bó", "báo"],
    "醭": ["bú", "pú"],
    "凔": ["cāng", "chuàng"],
    "差": ["chà", "chā"],
    "杈": ["chà", "chā"],
    "衩": ["chǎ", "chà"],
    "顫": ["chàn", "zhàn"],
    "颤": ["chàn", "zhàn"],
    "場": ["chǎng", "cháng"],
    "场": ["chǎng", "cháng"],
    "稱": ["chèn", "chèng"],
    "称": ["chèn", "chèng"],
    "乘": ["chéng", "shèng"],
    "懲": ["chéng", "chěng"],
    "惩": ["chéng", "chěng"],
    "吃": ["chī", "jí"],
    "樗": ["chū", "shū"],
    "儲": ["chǔ", "chú"],
    "储": ["chǔ", "chú"],
    "揣": ["chuài", "chuǎi"],
    "包": ["chuāi", "chuǎi"],
    "擉": ["chuō", "chū"],
    "雌": ["cí", "cī"],
    "廁": ["cè", "cì"],
    "厕": ["cè", "cì"],
    "賜": ["cì", "sì"],
    "赐": ["cì", "sì"],
    "從": ["cóng", "zòng"],
    "从": ["cóng", "zòng"],
    "撮": ["cuō", "cuò"],
    "打": ["dá", "dǎ"],
    "蹈": ["dǎo", "dào"],
    "賧": ["dǎn", "tàn", "tǎn"],
    "赕": ["dǎn", "tàn", "tǎn"],
    "禫": ["dàn", "tǎn"],
    "檔": ["dàng", "dǎng"],
    "档": ["dàng", "dǎng"],
    "蹬": ["dēng", "dèng"],
    "堤": ["dī", "tí"],
    "菂": ["dì", "dī"],
    "嗲": ["diǎ", "diē"],
    "踮": ["diǎn", "diàn"],
    "跌": ["diē", "dié"],
    "耵": ["dīng", "dǐng", "tīng"],
    "度": ["duó", "duò"],
    "踱": ["duó", "duò"],
    "多": ["duō", "duó"],
    "掇": ["duō", "duó"],
    "剟": ["duō", "duó"],
    "㙍": ["duō", "duó"],
    "裰": ["duō", "duó"],
    "咄": ["duō", "duò"],
    "噸": ["dūn", "dùn"],
    "吨": ["dūn", "dùn"],
    "俄": ["é", "è"],
    "伐": ["fá", "fā"],
    "法": ["fǎ", "fà"],
    "髮": ["fà", "fǎ"],
    "发": ["fà", "fǎ"],
    "帆": ["fān", "fán"],
    "藩": ["fān", "fán"],
    "梵": ["fàn", "fán"],
    "坊": ["fáng", "fāng"],
    "鯡": ["fēi", "fèi"],
    "鲱": ["fēi", "fèi"],
    "諷": ["fěng", "fèng"],
    "讽": ["fěng", "fèng"],
    "芣": ["fú", "fóu"],
    "襆": ["fú", "pú"],
    "幞": ["fú", "pú"],
    "縛": ["fù", "fú"],
    "缚": ["fù", "fú"],
    "胳": ["gā", "gē"],
    "伽": ["gā", "jiā"],
    "噶": ["gá", "gé"],
    "笴": ["gǎn", "gě"],
    "筶": ["gào", "gǎo"],
    "仡": ["gē", "qì"],
    "葛": ["gě", "gé"],
    "供": ["gòng", "gōng"],
    "佝": ["gōu", "kòu"],
    "痀": ["gōu", "jū"],
    "呱": ["gū", "wā"],
    "夃": ["gǔ", "gū"],
    "蛄": ["gǔ", "gū"],
    "聒": ["guō", "guā"],
    "佹": ["guī", "guǐ"],
    "劊": ["guì", "kuài"],
    "刽": ["guì", "kuài"],
    "檜": ["guì", "kuài"],
    "桧": ["guì", "kuài"],
    "鱖": ["guì", "jué"],
    "鳜": ["guì", "jué"],
    "摑": ["guāi", "guó", "guō"],
    "掴": ["guāi", "guó", "guō"],
    "絎": ["háng", "hèng"],
    "壑": ["hè", "huò"],
    "頜": ["hé", "gé"],
    "颌": ["hé", "gé"],
    "和": ["hé", "hàn"],
    "褐": ["hè", "hé"],
    "桁": ["héng", "háng"],
    "魟": ["hóng", "hōng"],
    "訌": ["hòng", "hóng"],
    "讧": ["hòng", "hóng"],
    "蕻": ["hóng", "hòng"],
    "逅": ["hòu", "gòu"],
    "糊": ["hù", "hú"],
    "䴉": ["huán", "xuán"],
    "鹮": ["huán", "xuán"],
    "浣": ["huàn", "wǎn", "huǎn"],
    "渾": ["hún", "hùn"],
    "浑": ["hún", "hùn"],
    "緝": ["jī", "qì"],
    "缉": ["jī", "qì"],
    "圾": ["jī", "sè"],
    "擊": ["jī", "jí"],
    "击": ["jī", "jí"],
    "唧": ["jī", "jí"],
    "寂": ["jì", "jí"],
    "績": ["jì", "jī"],
    "绩": ["jì", "jī"],
    "跡": ["jì", "jī"],
    "蹟": ["jì", "jī"],
    "迹": ["jì", "jī"],
    "夾": ["jiā", "jiá"],
    "夹": ["jiā", "jiá"],
    "浹": ["jiā", "jiá"],
    "浃": ["jiā", "jiá"],
    "漸": ["jiān", "jiàn"],
    "渐": ["jiān", "jiàn"],
    "姣": ["jiāo", "jiǎo"],
    "酵": ["jiào", "xiào"],
    "僅": ["jìn", "jǐn"],
    "仅": ["jìn", "jǐn"],
    "覲": ["jìn", "jǐn"],
    "觐": ["jìn", "jǐn"],
    "勁": ["jìn", "jìng"],
    "劲": ["jìn", "jìng"],
    "粳": ["jīng", "gēng"],
    "究": ["jiū", "jiù"],
    "鞠": ["jū", "jú"],
    "掬": ["jū", "jú"],
    "菌": ["jūn", "jùn"],
    "莙": ["jūn", "jùn"],
    "崁": ["kàn", "kǎn"],
    "痾": ["kē", "ē"],
    "疴": ["kē", "ē"],
    "刻": ["kè", "kē"],
    "矻": ["kū", "kù"],
    "會": ["kuài", "guì"],
    "会": ["kuài", "guì"],
    "框": ["kuàng", "kuāng"],
    "眶": ["kuàng", "kuāng"],
    "括": ["kuò", "guā"],
    "适": ["kuò", "guā"],
    "垃": ["lā", "lè"],
    "勞": ["láo", "lào"],
    "劳": ["láo", "lào"],
    "酪": ["lào", "luò"],
    "礌": ["léi", "lèi"],
    "累": ["lěi", "lèi"],
    "擂": ["lèi", "léi"],
    "肋": ["lèi", "lè"],
    "斂": ["liǎn", "liàn"],
    "敛": ["liǎn", "liàn"],
    "璉": ["liǎn", "lián"],
    "琏": ["liǎn", "lián"],
    "鐐": ["liào", "liáo"],
    "镣": ["liào", "liáo"],
    "釕": ["liào", "liǎo"],
    "钌": ["liào", "liǎo"],
    "淋": ["lìn", "lín"],
    "膦": ["lìn", "lín"],
    "呤": ["lìng", "líng"],
    "餾": ["liú", "liù"],
    "馏": ["liú", "liù"],
    "翏": ["liù", "liáo"],
    "籠": ["lǒng", "lóng"],
    "笼": ["lǒng", "lóng"],
    "露": ["lù", "lòu"],
    "孿": ["luán", "lüán"],
    "孪": ["luán", "lüán"],
    "攣": ["luán", "lüán", "liàn"],
    "挛": ["luán", "lüán"],
    "孌": ["luán", "lüǎn", "luǎn"],
    "娈": ["luán", "lüǎn"],
    "僂": ["lǚ", "lóu"],
    "偻": ["lǚ", "lóu"],
    "櫚": ["lǘ", "lǚ"],
    "榈": ["lǘ", "lǚ"],
    "獁": ["mǎ", "mà"],
    "犸": ["mǎ", "mà"],
    "嘜": ["mài", "mà"],
    "唛": ["mài", "mà"],
    "脈": ["mài", "mò"],
    "脉": ["mài", "mò"],
    "屘": ["mǎn", "mān"],
    "瑁": ["mào", "mèi"],
    "糜": ["méi", "mí"],
    "蒙": ["měng", "méng"],
    "懵": ["měng", "méng", "mēng"],
    "閩": ["mǐn", "mín"],
    "闽": ["mǐn", "mín"],
    "茗": ["míng", "mǐng"],
    "酩": ["mǐng", "míng"],
    "膜": ["mó", "mò"],
    "模": ["mú", "mó"],
    "腩": ["nǎn", "nán"],
    "難": ["nàn", "nán"],
    "囊": ["nāng", "náng"],
    "哪": ["né", "nuó"],
    "恁": ["nèn", "rèn"],
    "妮": ["nī", "ní"],
    "拈": ["niān", "nián"],
    "寧": ["nìng", "níng"],
    "宁": ["nìng", "níng"],
    "蹣": ["pán", "mán"],
    "磅": ["páng", "pāng"],
    "澎": ["péng", "pēng"],
    "坯": ["pī", "pēi"],
    "坏": ["pī", "pēi"],
    "劈": ["pǐ", "pī"],
    "匹": ["pǐ", "pī"],
    "癖": ["pǐ", "pì"],
    "縹": ["piāo", "piǎo"],
    "缥": ["piāo", "piǎo"],
    "嘌": ["piào", "piāo"],
    "剽": ["piāo", "piào"],
    "聘": ["pìn", "pìng"],
    "泊": ["pō", "bó", "pò"],
    "頗": ["pō", "pǒ"],
    "颇": ["pō", "pǒ"],
    "剖": ["pōu", "pǒu"],
    "樸": ["pǔ", "pú"],
    "朴": ["pǔ", "pú"],
    "蹼": ["pǔ", "pú"],
    "企": ["qǐ", "qì"],
    "騎": ["qí", "jì"],
    "崎": ["qí", "qī"],
    "期": ["qī", "qí"],
    "蹊": ["qī", "xī"],
    "骑": ["qí", "jì"],
    "卡": ["qiǎ", "kǎ"],
    "髂": ["qià", "kà"],
    "蕁": ["qián", "xún"],
    "潛": ["qián", "qiǎn"],
    "嵌": ["qiàn", "qiān"],
    "撬": ["qiào", "qiāo"],
    "戕": ["qiāng", "qiáng"],
    "嗆": ["qiāng", "qiàng"],
    "強": ["qiáng", "qiǎng"],
    "强": ["qiáng", "qiǎng"],
    "悄": ["qiāo", "qiǎo"],
    "殼": ["qiào", "ké"],
    "壳": ["qiào", "ké"],
    "怯": ["qiè", "què"],
    "氰": ["qíng", "qīng"],
    "穹": ["qióng", "qiōng"],
    "佉": ["qū", "qiā"],
    "麴": ["qū", "qú"],
    "蠼": ["qú", "jué"],
    "炔": ["quē", "jué"],
    "囷": ["qūn", "jūn"],
    "券": ["quàn", "juàn"],
    "攘": ["rǎng", "ráng"],
    "嚷": ["rāng", "rǎng"],
    "瀼": ["ràng", "ráng"],
    "辱": ["rǔ", "rù"],
    "糅": ["róu", "rǒu"],
    "瘙": ["sào", "sāo"],
    "殺": ["shā", "shài"],
    "杀": ["shā", "shài"],
    "廈": ["shà", "xià"],
    "厦": ["shà", "xià"],
    "猞": ["shē", "shè"],
    "懾": ["shè", "zhé"],
    "慑": ["shè", "zhé"],
    "莘": ["shēn", "xīn"],
    "神": ["shēn", "shén"],
    "甚": ["shèn", "shén"],
    "勝": ["shèng", "shēng"],
    "胜": ["shèng", "shēng"],
    "識": ["shí", "shì"],
    "识": ["shí", "shì"],
    "使": ["shǐ", "shì"],
    "室": ["shì", "shǐ"],
    "似": ["shì", "sì"],
    "叔": ["shū", "shú"],
    "淑": ["shū", "shú"],
    "菽": ["shū", "shú"],
    "掓": ["shū", "shú"],
    "儵": ["shū", "shù"],
    "毹": ["shū", "yú"],
    "署": ["shǔ", "shù"],
    "熟": ["shú", "shóu"],
    "漦": ["sī", "chí", "lí"],
    "艘": ["sōu", "sāo"],
    "窣": ["sū", "sù"],
    "綏": ["suí", "suī"],
    "绥": ["suí", "suī"],
    "嗍": ["suō", "shuò"],
    "獺": ["tǎ", "tà"],
    "獭": ["tǎ", "tà"],
    "黮": ["tàn", "tǎn"],
    "濤": ["tāo", "táo"],
    "涛": ["tāo", "táo"],
    "銻": ["tī", "tì"],
    "锑": ["tī", "tì"],
    "帖": ["tiè", "tiě"],
    "聽": ["tīng", "tìng"],
    "听": ["tīng", "tìng"],
    "凸": ["tū", "tú"],
    "突": ["tū", "tú"],
    "喎": ["wāi", "kuāi"],
    "㖞": ["wāi", "kuāi"],
    "玩": ["wán", "wàn"],
    "翫": ["wán", "wàn"],
    "惋": ["wǎn", "wàn"],
    "忘": ["wàng", "wáng"],
    "危": ["wēi", "wéi"],
    "微": ["wēi", "wéi"],
    "巍": ["wēi", "wéi"],
    "薇": ["wēi", "wéi"],
    "溦": ["wēi", "wéi"],
    "唯": ["wéi", "wěi"],
    "圩": ["wéi", "yú"],
    "萎": ["wěi", "wēi"],
    "偽": ["wěi", "wèi"],
    "伪": ["wěi", "wèi"],
    "文": ["wén", "wèn"],
    "聞": ["wén", "wèn"],
    "闻": ["wén", "wèn"],
    "抆": ["wěn", "wèn"],
    "紊": ["wěn", "wèn"],
    "蕹": ["wèng", "yōng"],
    "蝸": ["wō", "guā"],
    "蜗": ["wō", "guā"],
    "撾": ["wō", "zhuā"],
    "挝": ["wō", "zhuā"],
    "烏": ["wù", "wū"],
    "乌": ["wù", "wū"],
    "鸂": ["xī", "qī"],
    "㶉": ["xī", "qī"],
    "夕": ["xī", "xì"],
    "汐": ["xī", "xì"],
    "矽": ["xī", "xì"],
    "翕": ["xī", "xì"],
    "昔": ["xī", "xí"],
    "惜": ["xī", "xí"],
    "息": ["xī", "xí"],
    "熄": ["xī", "xí"],
    "錫": ["xī", "xí"],
    "锡": ["xī", "xí"],
    "禧": ["xǐ", "xī"],
    "銑": ["xǐ", "xiǎn"],
    "铣": ["xǐ", "xiǎn"],
    "呷": ["xiā", "xiá"],
    "薟": ["xiān", "liàn"],
    "莶": ["xiān", "liàn"],
    "醯": ["xiān", "xī"],
    "酰": ["xiān", "xī"],
    "先": ["xiān", "xiàn"],
    "鋧": ["xiàn", "xiǎn"],
    "相": ["xiāng", "xiàng"],
    "淆": ["xiáo", "yáo"],
    "崤": ["xiáo", "yáo"],
    "哮": ["xiào", "xiāo"],
    "楔": ["xiē", "xiè"],
    "挟": ["xié", "xiá"],
    "挾": ["xié", "xiá"],
    "攜": ["xié", "xī"],
    "携": ["xié", "xī"],
    "芯": ["xìn", "xīn"],
    "行": ["xíng", "xìng"],
    "芎": ["xiōng", "qiōng"],
    "魆": ["xū", "xù"],
    "咻": ["xù", "xǔ"],
    "煦": ["xù", "xǔ"],
    "癬": ["xuǎn", "xiǎn"],
    "癣": ["xuǎn", "xiǎn"],
    "削": ["xuē", "xuè"],
    "血": ["xuè", "xuě", "xiě"],
    "穴": ["xué", "xuè"],
    "雪": ["xuě", "xuè"],
    "謔": ["xuè", "nüè"],
    "谑": ["xuè", "nüè"],
    "馴": ["xùn", "xún"],
    "驯": ["xùn", "xún"],
    "崖": ["yá", "yái"],
    "琊": ["yá", "yé"],
    "亞": ["yà", "yǎ"],
    "亚": ["yà", "yǎ"],
    "湮": ["yān", "yīn"],
    "芫": ["yán", "yuán"],
    "奄": ["yǎn", "yān"],
    "養": ["yǎng", "yàng"],
    "养": ["yǎng", "yàng"],
    "烊": ["yàng", "yáng"],
    "耶": ["yē", "yé"],
    "椰": ["yē", "yé"],
    "曳": ["yè", "yì"],
    "液": ["yè", "yì"],
    "腋": ["yè", "yì"],
    "椅": ["yī", "yǐ"],
    "衣": ["yī", "yì"],
    "佁": ["yǐ", "ǎi"],
    "誼": ["yì", "yí"],
    "谊": ["yì", "yí"],
    "㣇": ["yì", "dì"],
    "應": ["yīng", "yìng"],
    "应": ["yīng", "yìng"],
    "佣": ["yōng", "yòng"],
    "拥": ["yōng", "yǒng"],
    "擁": ["yōng", "yǒng"],
    "鈾": ["yóu", "yòu"],
    "媛": ["yuàn", "yuán"],
    "遠": ["yuǎn", "yuàn"],
    "远": ["yuǎn", "yuàn"],
    "鑰": ["yuè", "yào"],
    "钥": ["yuè", "yào"],
    "暈": ["yùn", "yūn"],
    "晕": ["yùn", "yūn"],
    "臢": ["zā", "zāng"],
    "拶": ["zā", "zá"],
    "載": ["zǎi", "zài"],
    "载": ["zǎi", "zài"],
    "仔": ["zǎi", "zǐ"],
    "暫": ["zàn", "zhàn"],
    "暂": ["zàn", "zhàn"],
    "鑿": ["záo", "zuò"],
    "凿": ["záo", "zuò"],
    "鋥": ["zèng", "zhèng"],
    "锃": ["zèng", "zhèng"],
    "扎": ["zhā", "zhá"],
    "紮": ["zhā", "zhá"],
    "吒": ["zhā", "zhà"],
    "炸": ["zhá", "zhà"],
    "奓": ["zhà", "zhā"],
    "著": ["zháo", "zhāo"],
    "着": ["zháo", "zhāo"],
    "蜇": ["zhē", "zhé"],
    "轍": ["zhé", "chè"],
    "辙": ["zhé", "chè"],
    "蟄": ["zhé", "zhí"],
    "蛰": ["zhé", "zhí"],
    "幀": ["zhēn", "zhèng"],
    "帧": ["zhēn", "zhèng"],
    "圳": ["zhèn", "zùn"],
    "掙": ["zhèng", "zhēng"],
    "挣": ["zhèng", "zhēng"],
    "諍": ["zhèng", "zhēng"],
    "诤": ["zhèng", "zhēng"],
    "知": ["zhī", "zhì"],
    "脂": ["zhī", "zhǐ"],
    "质": ["zhì", "zhí"],
    "質": ["zhì", "zhí"],
    "掷": ["zhì", "zhí"],
    "擲": ["zhì", "zhí"],
    "挃": ["zhì", "zhí"],
    "栉": ["zhì", "jié"],
    "櫛": ["zhì", "jié"],
    "中": ["zhōng", "zhòng"],
    "謅": ["zhōu", "zōu"],
    "诌": ["zhōu", "zōu"],
    "驟": ["zhòu", "zòu"],
    "骤": ["zhòu", "zòu"],
    "軸": ["zhòu", "zhóu"],
    "轴": ["zhòu", "zhóu"],
    "舳": ["zhú", "zhóu"],
    "築": ["zhù", "zhú"],
    "筑": ["zhù", "zhú"],
    "贮": ["zhù", "zhǔ"],
    "貯": ["zhù", "zhǔ"],
    "爪": ["zhǎo", "zhuǎ"],
    "畷": ["zhuì", "zhuó"],
    "拙": ["zhuō", "zhuó"],
    "炪": ["zhuō", "zhuó"],
    "卓": ["zhuó", "zhuō"],
    "綜": ["zōng", "zòng"],
    "综": ["zōng", "zòng"],
    "縱": ["zòng", "zōng"],
    "纵": ["zòng", "zōng"],
    "鱒": ["zūn", "zùn"],
    "鳟": ["zūn", "zùn"],
}


class StringUtilities:
    @staticmethod
    def sub(text: str, start: int, end: int) -> str:
        """Substring with 1-based indexing (Lua style)."""
        return text[start - 1 : end]


def tr(text: str, lang: str) -> str:
    if not text:
        return text

    if lang in {"zh", "lzh", "nan-hlh"}:
        lang = "cmn"
    elif lang in {"csp", "yue", "zhx-tai"}:
        lang = "yue"
    elif lang == "nan-hlh":
        lang = "nan-tws"

    if lang == "cmn":
        text = text.replace("#", "")

        def rpl(char: str) -> str:
            return res[0] if (res := MT.get(char)) else cmn.pron.get(char, char)

        translated = "".join(rpl(char) for char in text)
        if text == translated:
            return ""
        return re.sub(r"\^('?.)", lambda m: m[1].upper(), translated)

    if lang == "yue":
        translated = "".join(yue.pron.get(char, char) for char in text)
        translated = re.sub(r"\d[\d\*\-]*(?![\d\*])", r"<sup>\g<0></sup> ", translated)
        if text == translated:
            return ""
        return translated.rstrip()

    return ""
    # TO DO

    if lang == "cdo":
        # TO DO: https://en.wiktionary.org/wiki/Module:cdo-pron
        return ""

    if lang == "gan":
        # TO DO
        translated = "".join(yue.pron.get(char, char) for char in text)
        return gan.rom(translated)

    if lang == "nan-tws":
        # Source: https://en.wiktionary.org/w/index.php?title=Module:nan-pron&oldid=85566090#L-1563
        text = re.sub(r"([1-8])/", r"\1 / ", text)
        text = re.sub(r"[1-8]+", r"<sup>\g<0></sup>", text)
        return text.replace("#", "")

    if lang == "hak":
        # TODO: Implementation needed
        pass

    if lang in {"ltc", "och"}:
        delimiter = "," if lang == "ltc" else ";"
        index = text.split(delimiter)

        for i in range(len(text)):
            module_type = f"{lang}-pron"
            if lang == "och":
                module_type += "-ZS"

            text[i : i + 1]
            # Mock data module loading
            data_module = []  # Would need actual module loading

            if i < len(index):
                if index[i] == "y":
                    index[i] = "1"
                elif index[i]:
                    try:
                        idx = int(index[i]) - 1
                        index[i] = data_module[idx] if idx < len(data_module) else data_module[0]
                    except (ValueError, IndexError):
                        index[i] = data_module[0] if data_module else ""
            else:
                index.append(data_module[0] if data_module else "")

            if lang == "ltc":
                # Mock LTC pronunciation processing
                index[i] = f"processed_{index[i]}" if i < len(index) else ""
            else:
                # Mock OCH pronunciation processing
                if isinstance(index[i], list) and len(index[i]) > 6:
                    index[i] = index[i][6]
                else:
                    index[i] = str(index[i])

        text = " ".join(str(item) for item in index)
        if lang == "och":
            text = f"*{text}"

        return text

    if lang == "nan":
        # TODO: Implementation needed
        pass

    if lang == "wuu":
        if ":" in text:
            # Mock wuu-pron processing
            text = f"wugniu_format({text[4:]})"
        else:
            # Mock wuu-pron processing
            text = f"wugniu_format(wikt_to_wugniu({text}))"
        return text

    if lang == "zhx-sic":
        text = re.sub(r"([\d\-])([a-zA-Z])", r"\1 \2", text)
        return re.sub(r"\d[\d\*\-]*(?![\d\*])", r"<sup>\g<0></sup>", text)

    # Mock module loading for other languages
    return f"rom({text})"


def transliterate(text: str, locale: str = "") -> str:
    """
    >>> transliterate("褚", "cmn")
    'chǔ'
    >>> transliterate("株洲", "cmn")
    'zhūzhōu'

    >> transliterate("林", "gan")
    'lin<sup>4</sup>'

    >>> transliterate("海陸豐", "nan-hlh")
    'hǎilùfēng'

    >> transliterate("羯", "ltc")
    'kjot'

    >>> transliterate("西營盤", "yue")
    'sai<sup>1</sup> jing<sup>4</sup> pun<sup>4</sup>'
    >>> transliterate("閩中語", "zh")
    'mǐnzhōngyǔ'
    >>> transliterate("^閩中語 / ^閩中語", "zh")
    'Mǐnzhōngyǔ / Mǐnzhōngyǔ'
    """
    return tr(text, locale)
