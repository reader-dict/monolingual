import html
import re
import unicodedata
from collections import defaultdict

from ... import context, utils


def strip_accents(text: str) -> str:
    """
    Remove stress marks only, letters such as "й" and "ё" are kept.

    >>> strip_accents("ключе́й ёлка́ ко̀е-где́")
    'ключей ёлка кое-где'
    """
    decomposed = unicodedata.normalize("NFD", text)
    return unicodedata.normalize("NFC", "".join(char for char in decomposed if char not in "\u0300\u0301"))


def cleanup(form: str) -> str:
    """
    >>> cleanup(" &#42;ультрамонтанства")
    'ультрамонтанства'
    >>> cleanup("торосья<sup>△</sup>")
    'торосья'
    >>> cleanup("Гё&#768;тебо́рга")
    'Гётеборга'
    >>> cleanup("авиаопрыски&shy;ватель")
    'авиаопрыскиватель'
    >>> cleanup("ВИЧ&#8209;диссидента")
    'ВИЧ-диссидента'
    >>> cleanup("*бешенный")
    'бешенный'
    """
    # Entities first, they would be cut at "#": `Гё&#768;тебо́рга` → `Гё&`
    form = html.unescape(form).replace("\xa0", " ")
    # Soft and non-breaking hyphens
    form = form.replace("\xad", "").replace("\u2011", "-")
    return strip_accents(utils.cleanup_rev_variant(form, rpl=["*", " ''(уст.)''", " ''(перен.)''", "<sup>△</sup>"]))


def render_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_variant("Форма-гл", [], defaultdict(str, {'база': 'выбирать', 'время': 'пр', 'род': '', 'лицо': '123', 'число': 'мн', 'накл': '', 'деепр': '', 'прич': '', 'кр': '', 'помета': '', 'знач': '', 'язык': 'ru', 'слоги': 'выбирали', 'МФА': '', 'аудио': '', 'омофоны': '', 'коммент': '', 'дореф': ''}), "выбирали")
    'выбирать'
    >>> render_variant("Форма-гл", ["есть#(глагол_I)", "пр", "м", "", "ед"], defaultdict(str, {"залог": "действ", "язык": "ru", "слоги": "{{по-слогам|ел}}", "МФА": "{{t-ru|ел}}}"}), "ел")
    'есть'

    >>> render_variant("Форма-сущ", [], defaultdict(str, {"база": "аба", "слоги": "{{по-слогам|аб}}", "МФА": "{{t-ru|аб}}"}), "аб")
    'аба'
    >>> render_variant("Форма-сущ", ["аба", "р", "мн", "", "", "", "ru"], defaultdict(str, {"слоги": "{{по-слогам|аб}}", "МФА": "{{t-ru|аб}}"}), "аб")
    'аба'

    >>> render_variant("прич.", ["зыбить"], defaultdict(str), "")
    'зыбить'
    >>> render_variant("прич.", ["находить (наталкиваться)", "наст"], defaultdict(str), "")
    'находить'
    >>> render_variant("прич.", ["<small>?</small>"], defaultdict(str), "")
    ''
    >>> render_variant("Форма-сущ", ["сто́ла", "р", "мн"], defaultdict(str), "стол")
    'стола'
    """
    if tpl.startswith("Форма-") and (base := data["база"]) and not parts:
        parts.append(base)

    if (variant := parts[0]) == "<small>?</small>":
        variant = ""
    if " (" in variant:
        variant = variant.split(" (", 1)[0]
    if "#" in variant:
        variant = variant.split("#", 1)[0]
    return strip_accents(variant)


def comparative_forms(text: str) -> list[str]:
    """
    The forms given by `|степень=`, without the markup of the templates it holds,
    nor the comments: "/" in a closing tag was taken as a separator.

    >>> comparative_forms("[[шире|ши́ре]]")
    ['ши́ре']
    >>> comparative_forms("здорове́е<sup>△</sup>, поздорове́е<sup>△</sup>, <i>устар.</i>: здоро́вее")
    ['здорове́е', 'поздорове́е', 'здоро́вее']
    >>> comparative_forms("<b>коинциде́нтней; коинциде́нтнее</b>")
    ['коинциде́нтней', 'коинциде́нтнее']
    >>> comparative_forms("деше́вле <i>и</i> подеше́вле <i>(в значении цены)</i>, дешеве́е <i>(в перен. знач.)</i>")
    ['деше́вле', 'подеше́вле', 'дешеве́е']
    >>> comparative_forms("го́рче<sup>△</sup> (вкус); го́рше<sup>△</sup>, го́рший<sup>△</sup> (эмоция)")
    ['го́рче', 'го́рше', 'го́рший']
    >>> comparative_forms("ме́ньше (поме́ньше), ме́ньший (ме́ньшее, ме́ньшая)")
    ['ме́ньше', 'ме́ньший', 'поме́ньше', 'ме́ньшее', 'ме́ньшая']
    >>> comparative_forms("ле́пше, ле́пее, (<i>редк.</i> ле́плее)")
    ['ле́пше', 'ле́пее', 'ле́плее']
    >>> comparative_forms("сипа́че, сипа́чей<!-- сопатый — сопа́че -->")
    ['сипа́че', 'сипа́чей']
    >>> comparative_forms("1")  # not a form
    []
    """
    text = re.sub(r"<!--.*?-->|<sup>.*?</sup>|<i>.*?</i>", " ", text, flags=re.DOTALL)
    text = re.sub(r"\[\[(?:[^|\]]*+\|)?([^\]]*+)\]\]", r"\1", text)
    text = re.sub(r"<[^>]*+>|''+", " ", text)

    def words(part: str) -> list[str]:
        return [word for word in re.split(r"[\s,;:/]+", part) if len(word) > 2 and any(c.isalpha() for c in word)]

    def start(word: str) -> str:
        return strip_accents(word).removeprefix("по")[:3]

    forms = words(re.sub(r"\([^()]*+\)", " ", text))
    # A note in parentheses can hold other forms of the word, "(поме́ньше)", or not, "(вкус)"
    starts = {start(form) for form in forms}
    for note in re.findall(r"\(([^()]*+)\)", text):
        forms.extend(word for word in words(note) if start(word) in starts)
    return [form for form in forms if not form.endswith(".")]


def render_reverse_variant(tpl: str, parts: list[str], data: defaultdict[str, str], word: str) -> str:
    """
    >>> render_reverse_variant("rev-flexion", ["коро́ль"], defaultdict(str), "")
    'коро́ль'
    """
    if tpl == "rev-flexion":
        return parts[0].strip()

    forms: set[str]
    table = context.expand(utils.reconstruct_tpl(tpl, parts, data), "ru")
    if table.startswith("{"):
        table = "\n".join(
            line
            for raw_line in table.splitlines()
            if (line := raw_line.strip()) and (line[0] == "|" and not line.startswith(("|-", "|}")))
        )
        table = re.sub(r'^\| class="grey"[^\n]++', "", table, flags=re.MULTILINE)
        table = re.sub(r"^\|\}[ ]*+<b>[^\n]++", "", table, flags=re.MULTILINE)
        table = (
            table.replace("<br>", "\n| ")
            .replace("<br/>", "\n| ")
            .replace("<br />", "\n| ")
            .replace("||", "\n| ")
            .replace("(по) ", "\n| ")
        )
        table = re.sub(r'^\|[ ]*+bgcolor="[^|\n]++', "", table, flags=re.MULTILINE)
        # Cell attributes: `| colspan=2| дву́х`
        table = re.sub(r"^\|[ ]*+[a-z]++=[^|\n]*+\|(?!\|)", "| ", table, flags=re.MULTILINE)
        forms = {form[1:].strip() for form in table.splitlines()}
    else:
        table = re.sub(r"<br[ ]*+/?>", "</td><td>", table)
        # Labels inside a cell: `не́кой<br />[[Викисловарь:Условные сокращения|<i>устар.</i>]]&nbsp;не́коей`
        table = re.sub(r"\[\[[^\]|]*+\|<i>[^<]*+</i>\]\]", "", table)
        # Drop cell attributes (`<td rowspan="3">`) and footnote marks (`<sup>△</sup>`)
        table = re.sub(r"<td [^>]*+>", "<td>", table)
        table = re.sub(r"<sup>[^<]*+</sup>", "", table)
        forms = set(re.findall(r"<td>([^<]++)</td>", table))
        # Links in a cell, only the first one was kept as the form is cut at "#":
        # `[[погасший#пога́сший|пога́сший]], [[погаснувший#пога́снувший|пога́снувший]]` → `пога́сший, пога́снувший`
        forms = {re.sub(r"\[\[(?:[^|\]]*+\|)?([^|\]]*+)\]\]", r"\1", form) for form in forms}
        # A second form in parentheses, it was dropped with them: `пога́снул (пога́с)` → `пога́снул, пога́с`
        forms = {re.sub(r"^([^\s()]++)[ ]*+\(([^\s().,;]++)\)$", r"\1, \2", form.strip()) for form in forms}

    # Comparative degree of adjectives: `|степень=[[шире|ши́ре]]`
    if comparative := data.get("степень", ""):
        forms |= set(comparative_forms(comparative))

    if not forms:
        return ""

    forms = {cleanup(form) for form in forms}
    # One cell can hold several forms: "его́, него́"
    if " " not in word:
        forms = {part for form in forms for part in re.split(r"[\s,;]+", form)}
    # Analytic forms: "буду/будешь… сидеть"
    forms = {form for form in forms if "/" not in form and "…" not in form}
    forms.discard("&")
    forms.discard("")
    forms.discard("-")
    forms.discard("—")
    forms.discard("}")
    forms.discard(word)

    return "|".join(forms)


handlers = {
    "прич.": render_variant,
    "Форма-гл": render_variant,
    "Форма-сущ": render_variant,
    "Форма-прил": render_variant,
    "Форма-мест": render_variant,
    "Форма-прич": render_variant,
    "Форма-числ": render_variant,
    "rev-flexion": render_reverse_variant,
}


def append_to_reverse_variants(tpl: str) -> None:
    """Dynamically append a template to reverse variants templates."""
    if tpl in handlers:
        return
    handlers[tpl] = render_reverse_variant
