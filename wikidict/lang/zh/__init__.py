"""Chinese language."""

import re

random_word_url = "https://zh.wiktionary.org/wiki/Special:RandomRootpage"

float_separator = ","
thousands_separator = ","

section_patterns = ("#", r"\*", ":")
head_sections = ("漢語", "汉语", "{{漢}}")
etyl_section = ("词源", "詞源")
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
    "漢字",
    "汉字",
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
    "字母",
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
variant_templates = ()

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


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{zh-pron\\n|m=huángmǎguà,er=y\\n|c=wong4 maa5 kwaa3-2\\n|cat=n\\n}}", "zh")
    '# {{zh-pron|m=huángmǎguà,er=y|c=wong4 maa5 kwaa3-2|cat=n}}'

    >>> adjust_wikicode("{{trans-top|...}}\\n...\\n{{trans-bottom}}", "zh")
    ''

    >>> adjust_wikicode("; '''限定代詞'''", "zh")
    ''
    >>> adjust_wikicode(";限定代詞", "zh")
    ''
    """
    # `{{zh-pron...` → `# {{zh-pron...`
    code = re.sub(r"^\{\{zh-pron", "# {{zh-pron", code, flags=re.MULTILINE)
    # `# {{zh-pron\n|...` → `# {{zh-pron|...`
    code = re.sub(r"^(# \{\{zh-pron.*?\}\})", lambda m: m[0].replace("\n", ""), code, flags=re.DOTALL | re.MULTILINE)

    # Wipe out `{{trans-top|...}}...{{trans-bottom}}`
    if "{{trans-top" in code:
        cleaned: list[str] = []
        in_unwanted_section = False
        for line in code.splitlines():
            if line.startswith("{{trans-top"):
                in_unwanted_section = True
            elif line.startswith("{{trans-bottom}}"):
                in_unwanted_section = False
            elif not in_unwanted_section:
                cleaned.append(line)
        code = "\n".join(cleaned)

    # `; '''限定代詞'''` → `:: 限定代詞`
    # `;限定代詞` → `:: 限定代詞`
    code = re.sub(r"^;\s*'*[^'\s]+'*", "", code, flags=re.MULTILINE)

    return code
