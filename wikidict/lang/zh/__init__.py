"""Chinese language."""

import re

import regex

from .template_overrides import overrides as template_overrides  # noqa: F401

random_word_url = "https://zh.wiktionary.org/wiki/Special:RandomRootpage"

float_separator = ","
thousands_separator = ","

section_patterns = ("#", ":")
head_sections = ("漢語", "汉语", "{{漢}}")
etyl_section = ("词源", "詞源", *[f"词源 {idx}" for idx in range(1, 20)])
section_sublevels = (4, 3)
sections = (
    *etyl_section,
    # https://zh.wiktionary.org/w/index.php?title=Module:Headword/data&oldid=9239080#L-41
    # abbreviation
    "縮寫",
    "缩写",
    # acronym
    "首字母縮略詞",
    "首字母缩略词",
    # adjective
    "形容詞",
    "形容词",
    # adverb
    "副詞",
    "副词",
    # affix
    "綴詞",
    "缀词",
    # article
    "冠詞",
    "冠词",
    # Chinese character
    # "漢字",  # See #2634
    # "汉字",  # See #2634
    # conjunction
    "連詞",
    "连词",
    # determiners
    "限定詞",
    "限定词",
    # diacritical marks
    "附加符號",
    "附加符号",
    # idiom
    "熟語",
    "熟语",
    "俗語",
    "俗语",
    # infixe
    "中綴",
    "中缀",
    # interfixe
    "間綴",
    "间缀",
    # interjection
    "感嘆詞",
    "感叹词",
    "感歎詞",
    # letter
    # "字母",  # See #2634
    # morpheme
    "詞素",
    "词素",
    # noun
    "名詞",
    "名词",
    # number
    "數字",
    "数字",
    # numeral symbol
    "數字符號",
    "数字符号",
    # numeral
    "數詞",
    "数词",
    # particle
    "助詞",
    "助词",
    # phrase
    "短語",
    "短语",
    # prefixe
    "前綴",
    "前缀",
    # preposition
    "介詞",
    "介词",
    # pronoun
    "代詞",
    "代词",
    # proper noun
    "專有名詞",
    "专有名词",
    # proverb
    "諺語",
    "谚语",
    # punctuation mark
    "標點符號",
    "标点符号",
    # suffixe
    "後綴",
    "后缀",
    # syllable
    "音節",
    "音节",
    # symbol
    "符號",
    "符号",
    # synonyms
    "同義詞",
    "同义词",
    # verb
    "動詞",
    "动词",
    # others
    "羅馬化",  # romanization
    "含义",  # meaning
    "開光",  # enlightenment
    "分詞",  # participle
    "分词",  # part of speech
    "釋義",  # explanation
)

variant_titles = sections

templates_ignored = (
    "{{attention",
    "{{attn",
    "{{audio",
    "{{cite-",
    "{{dead link",
    "{{Dead link",
    "{{def-",
    "{{rf",
    "{{Rf",
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from wikidict import context
    >>> _ = context.reset("zh")
    >>> context.new_word("word")

    >> find_pronunciations("{{zh-pron|m=bǎi jiàzi|c=baai2 gaa3 zi2|j=bai2 jia3 zeh|cat=v}}", "zh")
    ['/bǎi jiàzi/']
    >>> find_pronunciations("{{zh-pron|m=shāohòu|c=saau2 hau6|cat=adv,v}}", "zh")
    ['/shāohòu/']
    """
    from wikidict import context

    res: set[str] = set()
    pattern = r"\[\[(.+)#官話\|\1\]\]"
    for tpl in re.findall(rf"(\{{\{{{locale}-pron[^}}]+}}}})", code):
        if prons := re.findall(pattern, context.expand(tpl, "zh")):
            res.add(prons[0])
    return sorted(f"/{pron}/" for pron in res)


# Example: 興{xīng}
HAN_FOLLOWED_BY_BRACKETS = regex.compile(r"(?<=\[?\p{Han}\]?)(\{[^{}]+\})")
# Example: -{适}-
HAN_SURROUNDED_BY_BRACKETS = regex.compile(r"-\{\p{Han}\}-")


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("==漢語==\n{{zh-pron\n|m=huángmǎguà,er=y\n|c=wong4 maa5 kwaa3-2\n|cat=n\n}}", "zh")
    '==漢語==\n# {{zh-pron|m=huángmǎguà,er=y|c=wong4 maa5 kwaa3-2|cat=n}}'

    >>> adjust_wikicode("==漢語==\n{{trans-top|...}}\n...\n{{trans-bottom}}", "zh")
    '==漢語==\n'

    >>> adjust_wikicode("興{xīng}", "zh")
    '興'
    >>> adjust_wikicode("[群]{Qún}", "zh")
    '[群]'
    >>> adjust_wikicode("月亮是眾生不停輪迴轉世的象徵{{...}}所以用“月亮”這", "zh")
    '月亮是眾生不停輪迴轉世的象徵{{...}}所以用“月亮”這'

    >>> adjust_wikicode("-{适}-", "zh")
    ''

    >> adjust_wikicode("==漢語==\n; '''限定代詞'''", "zh")
    '==漢語==\n'
    >> adjust_wikicode("==漢語==\n;限定代詞", "zh")
    '==漢語==\n'
    >> adjust_wikicode("==漢語==\n:限定代詞", "zh")
    '==漢語==\n'
    >> adjust_wikicode("==漢語==\n; “位置，立場”\n: 來自《{{w|史記}}》：\n:{{zh-x|敢 犯 顏色 以 達 主義，不-顧 其 身。為 國家 樹 長-畫。|[一個人]敢於触犯[君主]威嚴的面孔，這樣才能讓[君主]理解[自己]的'''立場'''；一個人不在乎自己的生命，而是為國家做長遠打算。|ref=Shiji|collapsed=yes}}\n; “意識形態”\n:{{wasei kango|主%義|しゅ%ぎ}}。", "zh")
    "==漢語==\n 來自《{{w|史記}}》：\n:{{zh-x|敢 犯 顏色 以 達 主義，不-顧 其 身。為 國家 樹 長-畫。|[一個人]敢於触犯[君主]威嚴的面孔，這樣才能讓[君主]理解[自己]的'''立場'''；一個人不在乎自己的生命，而是為國家做長遠打算。|ref=Shiji|collapsed=yes}}\n{{wasei kango|主%義|しゅ%ぎ}}。"
    """
    # `{{zh-pron...` → `# {{zh-pron...`
    code = re.sub(r"^\{\{zh-pron", "# {{zh-pron", code, flags=re.MULTILINE)
    # `# {{zh-pron\n|...` → `# {{zh-pron|...`
    code = re.sub(r"^(# \{\{zh-pron.*?\}\})", lambda m: m[0].replace("\n", ""), code, flags=re.DOTALL | re.MULTILINE)

    # Wipe out `{{trans-top|...}}...{{trans-bottom}}`
    code = re.sub(r"\{\{trans-top(.+)\{\{trans-bottom\}\}", "", code, flags=re.DOTALL | re.MULTILINE)

    # `; '''限定代詞'''` → `:: 限定代詞`
    # `;限定代詞` → `:: 限定代詞`
    # (skipped due to #2655)
    # code = re.sub(r"^[;:][ ]*'*[^' {]+'*", "", code, flags=re.MULTILINE)

    code = HAN_FOLLOWED_BY_BRACKETS.sub("", code)
    code = HAN_SURROUNDED_BY_BRACKETS.sub("", code)

    return code
