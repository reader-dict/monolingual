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

float_separator = "."
thousands_separator = ","

head_sections = (
    "{{ja}}",
    "{{l|ja}}",
    "{{kanji}}",
    "日本語",  # japanese
    "記号",  # symbol
)
section_patterns = ("#", r"\*")
section_sublevels = (5, 4, 3)
etyl_section = ("{{etym}}", "字源")
sections = (
    *etyl_section,
    "{{adjc",
    "{{adjective",
    "{{colloc",
    "{{conjug",
    "{{idiom",
    "{{noun",
    "{{prov",
    "{{verb",
    "形容動詞",  # adjective
    "副詞",  # adverb
    "造語成分",  # coined word
    "連語",  # collocation
    "活用",  # conjugation
    "漢字混り表記",  # kanji mixed notation
    "成句",  # idiom
    "呼称",  # name
    "名詞",  # noun
    "由来",  # origin
    "助詞",  # particle
    "慣用句",  # phrase
    "地名語",  # place name
    "固有名詞",  # proper noun
    "ことわざ",  # proverb
    # "備考",  # remark (example with the word "麒麟竭", but it requires more work)
    "意義",  # significance
    "記号",  # symbol
    "動詞",  # verb
)

variant_titles = sections
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

    >>> context.new_word("麒麟竭")
    >>> find_pronunciations("{{ja-pron|きりんけつ|acc=2}}", "ja")
    ['[kìríꜜǹkètsù]']

    >>> context.new_word("て")
    >>> find_pronunciations("{{ipa|te|lang=ja}}", "ja")
    ['/te/']
    """
    from wikidict import context

    lookups = [
        r"(\{\{ipa\|[^}]+}})",
        rf"(\{{\{{{locale}-pron\|[^}}]+}}}})",
        # rf"(\{{\{{IPA\|{locale}\|[^}}]+}}}})",
        # rf"(\{{\{{{locale}-IPA[^}}]*}}}})",
    ]
    patterns = [r": (/[^/]+/)$", r"<samp>(\[[^\]]+\])</samp>", r"&#32;([\[/][^\]/]+[\]/])(?!\])"]

    for lookup in lookups:
        for tpl in re.findall(lookup, code):
            expanded = context.expand(tpl, "ja")
            for pattern in patterns:
                if not (prons := re.findall(pattern, expanded, flags=re.MULTILINE)):
                    continue
                return sorted(set(prons))

    return []


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

    >>> adjust_wikicode("{{kanji header|部画=人:2+6}}", "ja", word="併")
    '=={{kanji}}==\n{{kanji header|部画=人:2+6}}'

    >>> adjust_wikicode("=={{L|ja}}==\n==記号==\n{{Wikipedia|V}}\n\n# [[バナジウム]]の元素記号", "ja", word="いる")
    '=={{L|ja}}==\n==記号==\n{{Wikipedia|V}}\n# [[バナジウム]]の元素記号'

    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span id="語義1"></span> [[月]]', "ja", word="新月")
    '=={{L|ja}}==\n=== {{noun}} ===\n# [[月]]'
    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span id=\"yadoru\"><b>やどる</b></span>。一晩宿泊する。', "ja", word="新月")
    '=={{L|ja}}==\n=== {{noun}} ===\n#<b>やどる</b>。一晩宿泊する。'
    >>> adjust_wikicode('=={{L|ja}}==\n=== {{noun}} ===\n#<span style="font-size:smaller;">（全濁字）</span>', "ja", word="重")
    '=={{L|ja}}==\n=== {{noun}} ===\n#<small>（全濁字）</small>'

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

    if "{{kanji header" in code:
        code = f"=={{{{kanji}}}}==\n{code}"

    # Keep interesting sections only
    if not (code := utils.extract_relevant_sections(code, locale)):
        return ""

    # `<span style="font-size:smaller;">` → ``
    code = re.sub(r'<span style="font-size:[ ]*small[^"]*">([^<]+)</span>', r"<small>\1</small>", code)

    # `<span id="語義1"></span>` → ``
    # `<span id="語義1"><b>語義</b></span> ` → `<b>語義</b>`
    code = re.sub(r"</?span[^>]*>", "", code)

    # `==={{etym}}:いる===` → `==={{etym}}===`
    code = re.sub(r"^={3,}[ ]*\{\{etym\}\}.+", "==={{etym}}===", code, flags=re.MULTILINE)

    # `==記号==` → `==記号==\n===記号===`
    code = re.sub(r"^(==[ ]*記号[ ]*==)", r"\1\n===記号===", code)

    #
    # Reverse variants
    #

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        pattern = rf"^(\{{\{{(?:{'|'.join(tpl[2:] for tpl in interesting_reverse_variant_titles)})[^}}]+}}}})"
        cleaned: list[str] = []

        for line in code.splitlines():
            if not any(tpl in line for tpl in interesting_reverse_variant_titles):
                cleaned.append(line)
                continue

            # Remove current page name template: `{{日本語変格活用|{{PAGENAME}}}}` → `{{日本語変格活用|<WORD>}}`
            if "{{PAGENAME" in line:
                line = line.replace("{{PAGENAME}}", word)

            # Remove ruby tags: `{{日本語変格活用|{{ruby|有|ゆう}}|する}}}}` → `{{日本語変格活用|有|する}}`
            if "{{ruby" in line:
                line = re.sub(r"\{\{ruby\|([^|]+)\|[^}]+}}", r"\1", line)

            for tpl in re.findall(pattern, line, flags=re.MULTILINE):
                tpl_name = tpl[2 : max(0, tpl.find("|")) or tpl.find("}")].strip(" \u200e")
                variant_handlers_mod.append_to_reverse_variants(tpl_name)
                forms = utils.process_templates(word, tpl, locale, templates_status=templates_status, variant_only=True)
                cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))

        code = "\n".join(cleaned)

    return code
