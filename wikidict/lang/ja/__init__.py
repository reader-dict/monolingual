"""Japanese language."""

import re

from ... import lang, utils
from . import variant_handlers as variant_handlers_mod
from .template_adapters import adapters as template_adapters  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = (
    "https://ja.wiktionary.org/wiki/%E7%89%B9%E5%88%A5:%E3%81%8A%E3%81%BE%E3%81%8B%E3%81%9B%E8%A1%A8%E7%A4%BA"
)

module_trans = "モジュール"
template_trans = "テンプレート"
appendix_trans = "付録"

head_sections = (
    "{{ja}}",
    "{{l|ja}}",
    "{{kanji}}",
    "日本語",  # japanese
    "記号",  # symbol
)
section_patterns = ("#", r"\*")
section_sublevels = (3, 4, 5)
etyl_section = ("{{etym}}", "字源")
sections = (
    *etyl_section,
    "{{abbr",
    "{{adnominal",
    "{{adj",
    "{{adv",
    "{{auxverb",
    "{{colloc",
    "{{conj",
    "{{idiom",
    "{{interj",
    "{{name",
    "{{noun",
    "{{parti",
    "{{prefix",
    "{{pron",
    "{{prov",
    "{{suffix",
    "{{syn",
    # "{{usage",
    "{{verb",
    "略語",  # abbreviation
    "形容詞",  # adjective
    "形容動詞",  # adjective
    "連体詞",  # adnominal word
    "副詞",  # adverb
    "助動詞",  # auxiliary verb
    "造語成分",  # coined word
    "連語",  # collocation
    "普通名詞",  # common noun
    "普通{{noun",  # common noun
    "複合助辞",  # compound particle
    "活用",  # conjugation
    "接続詞",  # conjunction
    "漢字混り表記",  # kanji mixed notation
    "和語の漢字表記",  # kanji representation of native Japanese words
    "成句",  # idiom
    "感動詞",  # interjection
    "不変化詞",  # invariable particle
    "呼称",  # name
    "固有名詞",  # proper name
    "名詞",  # noun
    "由来",  # origin
    "助詞",  # particle
    "慣用句",  # phrase
    "地名語",  # place name
    "接頭辞",  # prefix
    "代名詞",  # pronoun
    "固有名詞",  # proper noun
    "ことわざ",  # proverb
    "句読点",  # punctuation mark
    # "備考",  # remark (example with the word "麒麟竭", but it requires more work)
    "意義",  # significance
    "接尾辞",  # suffix
    "記号",  # symbol
    "類義語",  # synonyms
    # "用法",  # usage
    "動詞",  # verb
)

reverse_variant_titles = ("{{日本語",)
reverse_variant_templates = ("{{rev-flexion",)

templates_ignored = (
    "{{wikipedia",
    "{{wp",
    "{{要出典",  # citation needed
)


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from wikidict import context
    >>> _ = context.reset("ja")

    >>> find_pronunciations("", "ja")
    []

    >>> context.new_word("みる")
    >>> find_pronunciations("{{ja-pron|acc=1}}", "ja")
    ['みる (頭高型 – [1])']

    >>> context.new_word("麒麟竭")
    >>> find_pronunciations("{{ja-pron|きりんけつ|acc=2}}", "ja")
    ['きりんけつ (中高型 – [2])']

    >>> context.new_word("みる")
    >>> find_pronunciations("{{ja-pron|acc=1}}", "ja")
    ['みる (頭高型 – [1])']

    >>> context.new_word("貴様")
    >>> find_pronunciations("{{ja-pron|きさま|acc=0|dev=1}}", "ja")
    ['きさま (平板型 – [0])']

    >>> context.new_word("て")
    >>> find_pronunciations("{{ipa|te|lang=ja}}", "ja")
    ['/te/']
    """
    from wikidict import context

    lookups = [
        r"(\{\{ipa\|[^}]++\}\})",
        rf"(\{{\{{{locale}-pron\|[^}}]++\}}\}})",
        # rf"(\{{\{{IPA\|{locale}\|[^}}]++\}}\}})",
        # rf"(\{{\{{{locale}-IPA[^}}]*+\}}\}})",
    ]
    patterns = [r": (/[^/]++/)$", r"<samp>(\[[^\]]++\])</samp>", r"&#32;([\[/][^\]/]++[\]/])(?!\])"]

    for lookup in lookups:
        for tpl in re.findall(lookup, code):
            expanded = context.expand(tpl, "ja")

            if "<del>" in expanded:
                expanded = re.sub(r"<del>[^<]++</del>", "", expanded)

            if locale == "ja":
                line = expanded.splitlines()[0]
                if "東京式" in line:
                    line = re.sub(r"\[\[([^\]]++)\]\]", r"\1", line.split(" ", 1)[1], count=1)
                    line = re.sub(r"[ ]++<samp>[^<]++</samp>", "", line)
                    if "[[" in line:
                        line = line.split("[[", 1)[0]
                    return [line.replace("&#8203;", "")]

            for pattern in patterns:
                if not (prons := re.findall(pattern, expanded, flags=re.MULTILINE)):
                    continue
                return sorted(set(prons))

    return []


def attach_synonyms(code: str) -> str:
    r"""
    Put the synonyms under their meaning, as a sub-definition, when they give its number ("語義1").
    The list is kept as it is when one of its lines can't be matched with a meaning.

    >>> attach_synonyms("==={{interj|ja}}===\n#考え込む様子。\n#*「ふうん、なるほど。」\n#冷淡な反応。\n===={{syn}}====\n*語義1：[[ふむ]]、[[なるほど]]\n*語義2：[[あっそ]]\n==註==")
    "==={{interj|ja}}===\n#考え込む様子。\n#*「ふうん、なるほど。」\n## ''類義語:'' [[ふむ]]、[[なるほど]]\n#冷淡な反応。\n## ''類義語:'' [[あっそ]]\n==註=="
    >>> attach_synonyms("==={{suffix}}===\n# 学年。\n# 年数。\n===={{syn}}====\n語義1\n*第…[[学年]]\n*[[回生]]\n語義2\n*[[年草]]\n===={{trans}}====")
    "==={{suffix}}===\n# 学年。\n## ''類義語:'' 第…[[学年]]、[[回生]]\n# 年数。\n## ''類義語:'' [[年草]]\n===={{trans}}===="
    >>> attach_synonyms("==={{noun}}===\n# 一。\n# 二。\n===={{syn}}====\n*（語義1）[[退職]]、[[辞職]]\n*[[気楽]]（語義1、語義2）")
    "==={{noun}}===\n# 一。\n## ''類義語:'' [[退職]]、[[辞職]]、[[気楽]]\n# 二。\n## ''類義語:'' [[気楽]]"
    >>> attach_synonyms("==={{noun}}===\n# 一。\n===={{syn}}====\n*[[気楽]]\n*（語義1）[[退職]]")
    '==={{noun}}===\n# 一。\n===={{syn}}====\n*[[気楽]]\n*（語義1）[[退職]]'
    >>> attach_synonyms("==={{noun}}===\n# 一。\n===={{syn}}====\n*（語義2）[[退職]]")
    '==={{noun}}===\n# 一。\n===={{syn}}====\n*（語義2）[[退職]]'
    """
    numbers = r"語義\s*+(\d++(?:\s*+[、,・]\s*+(?:語義)?\s*+\d++)*+)"
    heading = re.compile(rf"^[;:*]?\s*+[（(]?{numbers}[）)]?\s*+[:：]?\s*+$")
    prefix = re.compile(rf"^\*\s*+(?:\{{\{{sense\|{numbers}\}}\}}|[（(]{numbers}[）)]|{numbers}\s*+[:：])\s*+(.+)$")
    suffix = re.compile(rf"^\*\s*+(.+?)\s*+[（(]{numbers}[）)]\s*+$")
    lines = code.split("\n")

    def level(line: str) -> int:
        return len(line) - len(line.lstrip("=")) if line.startswith("=") else 0

    def refs(text: str) -> list[int]:
        return [int(number) for number in re.findall(r"\d++", text)]

    drop: set[int] = set()
    insert: dict[int, str] = {}
    for start, line in enumerate(lines):
        if not re.fullmatch(r"(=++)\s*+(?:\{\{syn\}\}|類義語)\s*+\1\s*+", line):
            continue
        end = next((n for n in range(start + 1, len(lines)) if level(lines[n])), len(lines))
        # The meanings: the "#" items of the section this one belongs to, before its first sub-section
        parent = next((n for n in range(start - 1, -1, -1) if 0 < level(lines[n]) < level(line)), -1)
        first_sub = next((n for n in range(parent + 1, start + 1) if level(lines[n])), start)
        items = [n for n in range(parent + 1, first_sub) if lines[n].startswith("#") and lines[n][1:2] not in "#*:"]
        synonyms: dict[int, list[str]] = {}
        current: list[int] = []
        for text in (lines[n].strip() for n in range(start + 1, end)):
            if not text or re.fullmatch(r"\{\{(?:top|mid|bottom|stub)[^}]*+\}\}|\[\[[^\[\]|:]++:[^\[\]]*+\]\]", text):
                continue
            if match := heading.match(text):
                current = refs(match[1])
                continue
            if match := prefix.match(text):
                found, synonym = refs(match[1] or match[2] or match[3]), match[4]
            elif match := suffix.match(text):
                found, synonym = refs(match[2]), match[1]
            elif text.startswith("*") and current:
                found, synonym = current, text.lstrip("* ")
            else:
                break
            if not found or any(not 0 < number <= len(items) for number in found):
                break
            for number in found:
                synonyms.setdefault(number, []).append(synonym)
        else:
            if synonyms:
                for number, texts in synonyms.items():
                    # After the meaning and its own sub-items
                    item = items[number - 1]
                    after = next(
                        (n for n in range(item + 1, first_sub) if lines[n][:2] not in ("#*", "#:", "##")), first_sub
                    )
                    insert[after - 1] = f"## ''類義語:'' {'、'.join(texts)}"
                drop.update(range(start, end))

    out: list[str] = []
    for n, line in enumerate(lines):
        if n not in drop:
            out.append(line)
        if n in insert:
            out.append(insert[n])
    return "\n".join(out)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    r"""
    >>> adjust_wikicode("=={{L|ja}}==\n==={{etym}}:いる===", "ja", word="いる")
    '=={{L|ja}}==\n==={{etym}}==='
    >>> adjust_wikicode("=={{L|ja}}==\n=== {{etym}}1 ===", "ja", word="いる")
    '=={{L|ja}}==\n==={{etym}}==='
    >>> adjust_wikicode("=={{L|ja}}==\n===形容詞：硬い　固い　堅い===", "ja", word="かたい")
    '=={{L|ja}}==\n===形容詞==='

    >>> adjust_wikicode("=={{L|ja}}==\n==={{interj|ja}}===", "ja")
    '=={{L|ja}}==\n==={{interj==='

    >>> adjust_wikicode("=={{L|ja}}==\n==記号==\n{{Wikipedia|V}}\n\n# [[バナジウム]]の元素記号", "ja", word="いる")
    '=={{L|ja}}==\n==記号==\n{{Wikipedia|V}}\n\n# [[バナジウム]]の元素記号'

    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span id="語義1"></span> [[月]]', "ja", word="新月")
    '=={{L|ja}}==\n==={{noun}}===\n# [[月]]'
    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span id=\"yadoru\"><b>やどる</b></span>。一晩宿泊する。', "ja", word="新月")
    '=={{L|ja}}==\n==={{noun}}===\n#<b>やどる</b>。一晩宿泊する。'
    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span style="font-size:smaller;">（全濁字）</span>', "ja", word="重")
    '=={{L|ja}}==\n==={{noun}}===\n#<small>（全濁字）</small>'

    >>> from ... import context
    >>> _ = context.reset("ja")

    >>> context.new_word("みる")
    >>> adjust_wikicode("=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n{{日本語上一段活用}}", "ja", word="みる")
    '=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n# {{rev-flexion|みた}}\n# {{rev-flexion|みない}}\n# {{rev-flexion|みます}}\n# {{rev-flexion|みよ}}\n# {{rev-flexion|みよう}}\n# {{rev-flexion|みること}}\n# {{rev-flexion|みれば}}\n# {{rev-flexion|みろ}}'

    >>> context.new_word("存続")
    >>> adjust_wikicode("=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n{{日本語変格活用|{{PAGENAME}}|する}}", "ja", word="存続")
    '=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n# {{rev-flexion|存続される}}\n# {{rev-flexion|存続した}}\n# {{rev-flexion|存続しない}}\n# {{rev-flexion|存続します}}\n# {{rev-flexion|存続しろ}}\n# {{rev-flexion|存続する}}\n# {{rev-flexion|存続すること}}\n# {{rev-flexion|存続すれば}}\n# {{rev-flexion|存続せず}}\n# {{rev-flexion|存続せよ}}'

    >>> context.new_word("有する")
    >>> adjust_wikicode("=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n{{日本語変格活用|{{ruby|有|ゆう}}|する}}", "ja", word="有する")
    '=={{L|ja}}==\n==={{verb}}===\n===={{conjug}}====\n# {{rev-flexion|有される}}\n# {{rev-flexion|有した}}\n# {{rev-flexion|有しない}}\n# {{rev-flexion|有します}}\n# {{rev-flexion|有しろ}}\n# {{rev-flexion|有すること}}\n# {{rev-flexion|有すれば}}\n# {{rev-flexion|有せず}}\n# {{rev-flexion|有せよ}}'
    """
    # `<span style="font-size:smaller;">` → ``
    code = re.sub(r'<span style="font-size:[ ]*+small[^"]*+">([^<]++)</span>', r"<small>\1</small>", code)

    # `<span id="語義1"></span>` → ``
    # `<span id="語義1"><b>語義</b></span> ` → `<b>語義</b>`
    code = re.sub(r"</?span[^>]*+>", "", code)

    # Synonyms go under their meaning when they give its number: `*語義1：[[ふむ]]`
    code = attach_synonyms(code)

    # `==={{etym}}:いる===` → `==={{etym}}===`
    code = re.sub(r"(^={3,})[ ]*+([^：:}=|]++\}*+)[^\n]++", r"\1\2\1", code, flags=re.MULTILINE)

    # `==記号==` → `==記号==\n===記号===`
    code = re.sub(r"^(==[ ]*+記号[ ]*+==)", r"\1\n===記号===", code)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"^(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]++\}}\}})"
        cleaned: list[str] = []

        for line in code.splitlines():
            if not any(tpl in line for tpl in interesting_reverse_variant_titles):
                cleaned.append(line)
                continue

            # Remove current page name template: `{{日本語変格活用|{{PAGENAME}}}}` → `{{日本語変格活用|<WORD>}}`
            if "{{FULLPAGENAME" in line:
                line = line.replace("{{FULLPAGENAME}}", word)
            if "{{PAGENAME" in line:
                line = line.replace("{{PAGENAME}}", word)

            # Remove ruby tags: `{{日本語変格活用|{{ruby|有|ゆう}}|する}}}}` → `{{日本語変格活用|有|する}}`
            if "{{ruby" in line:
                line = re.sub(r"\{\{ruby\|([^|]++)\|[^}]++\}\}", r"\1", line)

            for tpl in re.findall(pattern, line, flags=re.MULTILINE):
                tpl_name = tpl[2 : max(0, tpl.find("|")) or tpl.find("}")].strip(" \u200e")
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(cleaned)

    return code
