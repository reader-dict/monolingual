import html
import re
import unicodedata
from collections import defaultdict

from ... import context, utils


def strip_accents(text: str) -> str:
    """
    Remove stress marks only, letters such as "й" and "ї" are kept.

    >>> strip_accents("ї́жак мо́ї край")
    'їжак мої край'
    """
    decomposed = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(char for char in decomposed if char not in "\u0300\u0301"))


def cleanup(form: str) -> str:
    """
    >>> cleanup("альбо́мчики*")
    'альбомчики'
    >>> cleanup("кам&#39;яни́стого")
    "кам'янистого"
    """
    # Entities first, they would be cut at "#": `кам&#39;яни́стого` → `кам&`
    form = html.unescape(form.replace("&#160;", "").replace("&#32;", ""))
    cleaned = strip_accents(
        utils.cleanup_rev_variant(
            form,
            rpl=["*", "&#160;", "&#32;", "на/у ", "буду/будеш… "],
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


RE_CLEANUPS1 = [
    # Several cells on one line in the adjective tables: `|| [[називний|Н.]] ||  class="declension-white" | вірогі́дний`
    (re.compile(r"[ ]*+\|\|[ ]*+class=\"declension-white\"[ ]*+\|"), "\n|"),
    (re.compile(r"(?m)^<td[^>]*?bgcolor=\"#ffffff\"[^>]*+>([^<]++)</td>"), r"| \1"),
    # The past tense and the imperative of the verbs, the line was removed with its attributes:
    # `| bgcolor="#ffffff" align="left" | чита́в<br />чита́ла` → `| чита́в<br />чита́ла`
    (re.compile(r"(?m)^\|[^|\n]*?bgcolor=\"#ffffff\"[^|\n]*+\|[ ]*+"), "| "),
]
RE_CLEANUPS2 = [
    (re.compile(r"(?m)^\|[^|]*?declension-white[^|]*+"), ""),
    (re.compile(r"(?m)^\|[^\n]*?bgcolor=.*+$"), ""),
    (re.compile(r"<br[^>]*?>"), "\n| "),
    (re.compile(r"(?m)^\|[ ]*+\[\[([^|#]++)\|.++"), r"| \1"),
]


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
    'убреде|убредем|убредемемо|убредете|убредеш|убреди|убреду|убредуть|убредімо|убредіть|убрела|убрели|убрело|убрів'

    >>> context.new_word("стояти")  # `( -їмо́)`
    >>> render_reverse_variant("дієсл uk нед 5b^", ["сто", "сті́"], defaultdict(str, {"склади": "{{склади|сто|я́|ти}}"}), "стояти")
    'стоти|стою|стояв|стоявши|стояла|стояли|стояло|стоятиме|стоятимемо|стоятимете|стоятимеш|стоятиму|стоятимуть|стоять|стоячи|стоячий|стоїм|стоїмїмо|стоїте|стоїть|стоїш|стій|стійте'

    >>> context.new_word("збіднити")  # `( -имо́)`
    >>> render_reverse_variant("дієсл uk 4bДВ", [], defaultdict(str, {"склади": "{{склади|збід|ни́|ти}}|збідн|збідн}}"}), "збіднити")
    'збідни|збіднив|збіднила|збіднили|збіднило|збідним|збіднимимо|збідните|збіднить|збідниш|збідню|збіднять|збідніте'

    >>> context.new_word("розпилити")  # `( -имо)`
    >>> render_reverse_variant("дієсл uk 4c/bДВ", ["розпил", "розпи́л", "розпил"], defaultdict(str, {"склади": "{{склади|роз|пи|ли́|ти}}", "ю": "1", "и": "1", "БезосФорма": "", "відп": ""}), "розпилити")
    'розпилений|розпили|розпилив|розпиливши|розпилила|розпилили|розпилило|розпилим|розпилимим|розпилите|розпилить|розпилиш|розпилю|розпилять|розпиліте'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    if data[""] == "1":
        data.pop("")
        parts.append(parts[0])

    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "uk")

    for pattern, rpl in RE_CLEANUPS1:
        table = pattern.sub(rpl, table)

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

    for pattern, rpl in RE_CLEANUPS2:
        table = pattern.sub(rpl, table)
    table = table.replace(" | ", "\n| ")

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
    # Several forms in a cell: "цабаньмо, цабанімо", and no analytic forms: "буде щастіти"
    forms = {part.strip() for form in forms for part in form.split(",")}
    if " " not in word:
        forms = {form for form in forms if " " not in form}
    forms.discard("")
    forms.discard("–")
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
