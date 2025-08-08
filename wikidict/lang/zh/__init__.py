"""Chinese language."""

import re

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = ","

# Markers for sections that contain interesting text to analyse.
section_patterns = ("#", r"\*", ":")
head_sections = ("漢語", "汉语", "{{漢}}")
etyl_section = ("词源", "詞源")
sections = (
    *etyl_section,
    "動詞",  # verb
    "动词",  # verb
    "副詞",  # adverb
    "形容詞",  # adjective
    "羅馬化",  # romanization
    "含义",  # meaning
    "開光",  # enlightenment
    "專有名詞",  # proper noun
    "名词",  # noun
    "名詞",  # noun
    "俗語",  # proverb
    "漢字",  # Chinese character
    "分詞",  # participle
    "分词",  # part of speech
    "釋義",  # explanation
)

# Variants
variant_titles = sections
variant_templates = (
    "{{異體",  # heteromorph
)

# Templates to ignore: the text will be deleted.
# definitions_to_ignore = ()

# Templates to ignore: the text will be deleted.
templates_ignored = (
    "attention",
    "attn",
    "audio",
    "cite-book",
    "cln",
    "dead link",
    "Dead link",
    "def-uncertain",
    "rfdef",
    "Rfdef",
    "rfe",
    "Rfe",
    "rfp",
    "rfv-etym",
    "Rfv-etym",
    "rfv-sense",
    "Rfv-sense",
    "senseid",
    "sid",
    "zh-forms",
    "zh-pron",
)

# Templates more complex to manage.
templates_multi = {
    # {{abbreviation of|zh|留名}}
    "abbreviation of": "f'{parts[2]}之縮寫。'",
    # {{cmn-pinyin of|塔吉克}}
    "cmn-pinyin of": "f'<span style=\"font-size:larger\">{concat(parts[1:], '、')}</span>的漢語拼音讀法'",
    # {{misspelling of|zh|稍候}}
    "misspelling of": "f'{parts[2]}的拼寫錯誤。'",
    # {{zh-character component|彡}}
    "zh-character component": "f'漢字部件「{parts[1]}」的名稱。'",
    # {{defdate|from 15th c.}}
    **dict.fromkeys(
        {"defdate", "Defdate"},
        "small('（' + parts[1] + (f'–{parts[2]}' if len(parts) > 2 else '') + '）')",
    ),
    # {{gloss|對患者}}
    **dict.fromkeys({"gloss", "gl"}, "f'（{parts[1]}）'"),
    # {{IPA|zh|/tʷãɔ̃⁵⁴⁵⁴/}}
    **dict.fromkeys({"IPA", "Ipa", "IPAchar", "國際音標/字體", "IPAfont"}, "parts[-1]"),
    # {{lang|zh|中華}}
    **dict.fromkeys({"lang", "Lang"}, "parts[-1]"),
    # {{non-gloss definition|用來表示全範圍}}
    **dict.fromkeys({"non-gloss definition", "n-g", "ng"}, "parts[1]"),
    # {{qualifier|前句常有“一方面”……}}
    **dict.fromkeys({"qualifier", "qual"}, "parenthesis(parts[1])"),
    # {{taxlink|Okapia johnstoni|species}}
    **dict.fromkeys({"taxlink", "Taxlink", "taxfmt"}, "italic(parts[1])"),
    # {{zh-ref|Schuessler, 2007}}
    **dict.fromkeys({"zh-ref", "Zh-ref"}, "parts[1]"),
}

# Templates that will be completed/replaced using custom text.
templates_other = {
    "†": "†",
}


def last_template_handler(
    template: tuple[str, ...],
    locale: str,
    *,
    word: str = "",
    all_templates: list[tuple[str, str, str]] | None = None,
    variant_only: bool = False,
) -> str:
    """
    Will be called in utils.py::transform() when all template handlers were not used.

        >>> last_template_handler(["label", "zh", "internet slang"], "zh")
        '(網路用語)'
        >>> last_template_handler(["lb", "zh", "internet slang", "very rare", "&", "Kashkai"], "zh")
        '(網路用語，非常罕用和Qashqai)'
    """
    from ...user_functions import extract_keywords_from, parenthesis
    from .. import defaults
    from .labels import labels
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template
    tpl = tpl.lower()

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        return render_template(word, template)

    extract_keywords_from(parts)

    if tpl in {"label", "lbl", "lb"}:
        text = ""
        sep = "，"
        for label in parts[1:]:
            if label == "&":
                sep = "和"
            else:
                if text:
                    text += sep
                text += labels.get(label, label)
        return parenthesis(text)

    return defaults.last_template_handler(
        template,
        locale,
        word=word,
        all_templates=all_templates,
        variant_only=variant_only,
    )


random_word_url = "https://zh.wiktionary.org/wiki/Special:RandomRootpage"


def adjust_wikicode(code: str, locale: str) -> str:
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
