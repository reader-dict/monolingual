import re
import unicodedata
from collections import defaultdict

from ... import context, utils


def strip_accents(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFD", text) if unicodedata.category(char) != "Mn")


def cleanup(form: str) -> str:
    """
    >>> cleanup("альбо́мчики*")
    'альбомчики'
    """
    cleaned = strip_accents(
        utils.cleanup_rev_variant(
            form,
            rpl={"*", "&#160;", "&#32;", "на/у ", "буду/будеш… "},
            skip={"на/в"},
        )
    )
    if cleaned.startswith("="):
        return ""
    return cleaned


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("змп", ["альбом"], defaultdict(str), "альбомчик")
    'альбом'
    """
    return parts[0]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["коро́ль"], defaultdict(str), "")
    'коро́ль'

    >>> _ = context.reset("uk")

    >>> context.new_word("омелюх")  # `data[""] == "1"`
    >>> render_reverse_variant("імен uk 3b m a", ["омелю́х", "омелюх", "омелюх"], defaultdict(str, {"склади": "{{склади|о|ме|лю́х}}", "": "1"}), "омелюх")
    'омелюха|омелюхам|омелюхами|омелюхах|омелюхе|омелюхи|омелюхові|омелюхом|омелюху|омелюхі|омелюхів'

    >>> context.new_word("бугор")  # `=у` in forms
    >>> render_reverse_variant("імен uk 1*b m una", ["буго́р", "бугр"], defaultdict(str, {"склади": "{{склади|бу|го́р}}"}), "бугор")
    'бугра|буграм|буграми|буграх|бугри|бугрові|бугром|бугру|бугрів'

    >>> context.new_word("убрести")  # `( -емо́)`
    >>> render_reverse_variant("дієсл uk 7bДВ", ["убред", "убре", "убрі́"], defaultdict(str, {"склади": "{{склади|у|бре|сти́}}", "відп": ""}), "убрести")
    'убреде|убредем|убредемемо|убредете|убредеш|убреду|убредуть'

    >>> context.new_word("стояти")  # `( -їмо́)`
    >>> render_reverse_variant("дієсл uk нед 5b^", ["сто", "сті́"], defaultdict(str, {"склади": "{{склади|сто|я́|ти}}"}), "стояти")
    'стоти|стою|стоявши|стоятиме|стоятимемо|стоятимете|стоятимеш|стоятиму|стоятимуть|стоять|стоячи|стоячии|стоім|стоімімо|стоіте|стоіть|стоіш'

    >>> context.new_word("збіднити")  # `( -имо́)`
    >>> render_reverse_variant("дієсл uk 4bДВ", [], defaultdict(str, {"склади": "{{склади|збід|ни́|ти}}|збідн|збідн}}"}), "збіднити")
    'збідним|збіднимимо|збідните|збіднить|збідниш|збідню|збіднять'

    >>> context.new_word("розпилити")  # `( -имо)`
    >>> render_reverse_variant("дієсл uk 4c/bДВ", ["розпил", "розпи́л", "розпил"], defaultdict(str, {"склади": "{{склади|роз|пи|ли́|ти}}", "ю": "1", "и": "1", "БезосФорма": "", "відп": ""}), "розпилити")
    'розпилении|розпиливши|розпилим|розпилимим|розпилите|розпилить|розпилиш|розпилю|розпилять'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    if data[""] == "1":
        data.pop("")
        parts.append(parts[0])

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "uk")
    table = re.sub(r'^<td.*bgcolor="#ffffff"[^>]*>([^<]+)</td>', r"| \1", table, flags=re.MULTILINE)
    table = "\n".join(
        line
        for raw_line in table.splitlines()
        if (line := raw_line.strip())
        and (
            line[0] == "|"
            and not line.startswith(("|-", "|}"))
            and "declension-gray" not in line
            and "declension-lightblue" not in line
            and "#eef9ff" not in line
        )
    )
    table = re.sub(r"^\|.*declension-white[^|]*", "", table, flags=re.MULTILINE)
    table = re.sub(r"^\|.*bgcolor=.*$", "", table, flags=re.MULTILINE)
    table = table.replace("<br>", "\n| ").replace("<br/>", "\n| ").replace("<br />", "\n| ").replace(" | ", "\n| ")
    table = re.sub(r"^\|[ ]*\[\[([^|#]+)\|.+", r"| \1", table, flags=re.MULTILINE)

    forms = {form[1:].strip() for form in table.splitlines() if form and "[[" not in form}
    for form in forms.copy():
        if "(" in form:
            if " " not in form:
                forms.add(form.replace("(", "").replace(")", ""))
                forms.discard(form)
            elif ("( -емо́)") in form or "( -їмо́)" in form or "( -имо́)" in form or "( -имо)" in form:
                forms.add(form.split("(", 1)[0])
                forms.add(form[:-2].replace("( -", "").replace(")", ""))
                forms.discard(form)

    forms = {cleanup(form) for form in forms}
    forms.discard("")
    forms.discard("&")
    forms.discard("—")
    forms.discard(word)

    return "|".join(sorted(forms))


handlers = {
    "змп": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
