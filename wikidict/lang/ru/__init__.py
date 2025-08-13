"""Russian language."""

import re

from ...user_functions import flatten, unique
from .transcriptions import transcript

# Float number separator
float_separator = ","

# Thousands separator
thousands_separator = " "

# Markers for sections that contain interesting text to analyse.
section_level = 1
section_sublevels = (3, 4)
head_sections = ("{{-ru-}}",)
etyl_section = ("этимология",)
sections = (
    *etyl_section,
    "значение",
    "{{значение}}",
    "семантические свойства",
    "{{семантические свойства}}",
    "морфологические и синтаксические свойства",
    "как самостоятельный глагол",  # for verbs with aux
    "в значении вспомогательного глагола или связки",  # for verbs with aux
)

# Variants
variant_titles = ("значение",)
variant_templates = ("{{прич.",)

# Some definitions are not good to keep
templates_ignored = (
    "??",
    "DEFAULTSORT",
    "etym-lang",
    "gb",
    "improve",
    "КЭС-2",
    "L",
    "l",
    "Lacuna",
    "lacuna",
    "ngram ru",
    "OED",
    "offensive",
    "offensive-inline",
    "unfinished",
    "wikipedia",
    "Цитата",
    "семантика",
    "пример",
    "помета.",
    "Категория",
    "длина слова",
    "из",
    "Шанский",
    "Виноградов",
    "русские приставки",
    "Крылов",
    "перев-блок",
    "Аникин",
    "Ушаков1940",
    "Крысин",
)

# Templates more complex to manage.
templates_multi = {
    # {{"|Сработать по Шеремету}}
    '"': 'f"„{parts[1]}“"',
    # {{=|Атлант}}
    "=": 'f"то же, что {parts[1]}"',
    # {{^|183}}
    "^": "f'<sup>{parts[1]}</sup>'",
    # {{aslinks|время, времечко; временами, временно (во избежание); время от времени|,;|1}}
    # {{aslinks|выезжать#I}}
    "aslinks": "parts[1].split('#', 1)[0]",
    # {{comment|РФ|Российская Федерация|Россия}}
    "comment": "f'{parts[1]}&nbsp;({parts[-1]})'",
    # {{Cyrs|аблъко}}
    "Cyrs": "parts[1]",
    # {{razr|Кудряш}}
    "razr": "f'<span style=\"letter-spacing:0.2em;margin-right:-0.2em;\">{parts[1]}<span>'",
    # {{fonts|Πίστιος}}
    "fonts": "parts[1]",
    # {{red|♦}}
    "red": "f'<span style=\"color:red;\">{parts[1]}</span>'",
    # {{sla-pro|*desnъ}}
    "sla-pro": "f'праслав. {parts[1]}'",
    # {{verb-dir|verb}}
    "verb-dir": "f'(о движении, совершаемом однократно или в определённом направлении, в отличие от сходного по смыслу гл. {parts[1]})'",
    # {{verb-dir-n|verb}}
    "verb-dir-n": "f'(о движении, совершаемом неоднократно или не в определённом направлении, в отличие от сходного по смыслу гл. {parts[1]})'",
    # {{wikiref|совершенный вид}}
    "wikiref": "parts[-1]",
    # {{кс|Унбегаун, с. 44}}
    "кс": 'f"[{parts[1]}]"',
    # {{t:=|поисковая оптимизация}} →  {{_t_|поисковая оптимизация}} (converted in `render.adjust_wikicode()`)
    "_t_": 'f"то же, что {parts[1]}"',
    "страд.": "italic('страд.') + ' к' + ((' ' + parts[1]) if len(parts) > 1 else '')",
    # {{марр|значение слова или выражения}}
    "марр": 'f"‘{parts[1]}’"',
    # {{этим-2|{{lang|en|AI|ИИ}}|{{lang|en|artificial intelligence|искусственный интеллект}}|[[тренер]]|{{lang|en|trainer|тренер}}}}
    "этим-2": "f\"{parts[1]} + {parts[3] if len(parts) > 3 else ''}\"",
    # {{дееприч.|сфотать}}
    "дееприч.": "f\"<i>дееприч.</i> от {parts[1] if len(parts) > 1 else ''}\"",
    # {{-ся|аббревиировать}}
    "-ся": "f'Образовано добавлением -ся к гл. {parts[-1]}, далее'",
    # {{совершить|аббревиировать}}
    "совершить": "f'совершить действие, выраженное гл. {parts[-1]}; провести некоторое время, совершая такое действие'",
    # {{отн.|аббревиировать}}
    "отн.": "f'относящийся к {parts[-1]}, связанный с ним'",
    # {{нкря|Неограниченные возможности|b4kB6}}
    "нкря": "parts[1]",
    # {{прежде|Камбоджа}}
    "прежде": "f'прежнее название {parts[0]}'",
    # {{аффиксы|жить|в-|-ся}}
    "аффиксы": "f'{parts[1]} с добавлением {\", \".join(parts[2:])}, далее '",
    # {{результат|lang=ru|блевать}}
    "результат": "f'результат действия по знач. гл. {next(p for p in parts[1:] if \"=\" not in p)}'",
    # {{праиндоеврокорень|foo}}
    "праиндоеврокорень": "f'происходит от праиндоевропейского корня {parts[1]}'",
    # {{шаблон|wikify}}
    "Шаблон": "parts[1]",
    # {{числ.|42}}
    "числ.": "f'ппорядковое числительное к {parts[1]}'",
}
templates_multi["&quot;"] = templates_multi['"']
templates_multi["==="] = templates_multi["="]
templates_multi["Script/Slavonic"] = templates_multi["Cyrs"]
templates_multi["script/Slavonic"] = templates_multi["Cyrs"]
templates_multi["template"] = templates_multi["Шаблон"]
templates_multi["то же"] = templates_multi["="]
templates_multi["ссылки"] = templates_multi["aslinks"]
templates_multi["ш"] = templates_multi["Шаблон"]

# Templates that will be completed/replaced using custom text.
templates_other = {
    "?": "<small>?</small>",
    "-": "—",
    "--": "—",
    "--+": "→",
    "f": "<i>ж.</i>",
    "m": "<i>м.</i>",
    "n": "<i>cp.</i>",
    "nobr": "&nbsp;",
    "Ф": "<small>Использованы данные словаря М. Фасмера</small>",
    "Нужен перевод": "<b>Значение этого слова или выражения пока не указано.</b> Вы можете предложить свой вариант.",
    "советск.": "<i>советск.</i>",
    "итп": "и т. п.",
    "втч": "в т. ч.",
    "мн. ч.": "<i>мн. ч.</i>",
    "телеком.": "<i>телеком.</i>",
    "итд": "и т. д.",
    "фотогр. жарг.": "<i>фотогр. жарг.</i>",
    "букв.": "<i>букв.</i>",
    "воен. жарг.": "<i>воен. жарг.</i>",
    "скорн.": "<i>скорн.</i>",
    "жарг. комп. игр.": "<i>жарг. комп. игр.</i>",
    "жарг. нарк.": "<i>жарг. нарк.</i>",
    "метоним.": "<i>метоним.</i>",
    "животн.": "<i>животн.</i>",
    "гидротехн.": "<i>гидротехн.</i>",
    "жарг. аним.": "<i>жарг. аним.</i>",
    "ислам.": "<i>ислам.</i>",
    "стомат.": "<i>стомат.</i>",
    "ж.-д.": "<i>ж.-д.</i>",
    "конев.": "<i>конев.</i>",
    "пчел.": "<i>пчел.</i>",
    "винод.": "<i>винод.</i>",
    "эл.-техн.": "<i>эл.-техн.</i>",
    "несов.": "<i>несов.</i>",
    "сов.": "<i>сов.</i>",
    "арест.": "<i>арест.</i>",
    "гистол.": "<i>гистол.</i>",
    "частич.": "<i>частич.</i>",
    "радиоэл.": "<i>радиоэл.</i>",
    "с.-х.": "<i>с.-х.</i>",
    "жарг. ЛГБТК+": "<i>жарг. ЛГБТК+</i>",
    "спорт. жарг.": "<i>спорт. жарг.</i>",
    "филос.": "<i>филос.</i>",
    "патет.": "<i>патет.</i>",
    "радио.": "<i>радио.</i>",
    "бизн.": "<i>бизн.</i>",
    "экспр.": "<i>экспр.</i>",
    "экзот.": "<i>экзот.</i>",
    "неуп.": "<i>энеуп.</i>",
    "палеонт.": "<i>палеонт.</i>",
    "журн.": "<i>журн.</i>",
    "лимн.": "<i>лимн.</i>",
    "транс.": "<i>транс.</i>",
    "кожев.": "<i>кожев.</i>",
    "возвр.": "<i>возвр.</i>",
    "педагог.": "<i>педагог.</i>",
    "шашечн.": "<i>шашечн.</i>",
    "тур.": "<i>тур.</i>",
    "смягчит.": "<i>смягчит.</i>",
    "кинемат. жарг.": "<i>кинемат. жарг.</i>",
    "вексил.": "<i>вексил.</i>",
    "техн. жарг.": "<i>техн. жарг.</i>",
    "растен.": "<i>растен.</i>",
    "Даль": "<small>[Даль]</small>",
    "СРНГ": "<small>[СРНГ]</small>",
    "ССРЛЯ-2": "<small>[ССРЛЯ]</small>",
    "НКРЯ": "<small>[НКРЯ]</small>",
    "Академия": "<small>[Академия]</small>",
    "по": "Норвежский<sub>no</sub>",
    "звукоподр": "звукоподражательное",
    "прагерм": "прагерм., от которой в числе прочего произошли:",
    "общеслав": "общеслав. формы",
}
templates_other["ср."] = templates_other["n"]
templates_other["м."] = templates_other["m"]
templates_other["мн"] = templates_other["мн. ч."]
templates_other["мн."] = templates_other["мн. ч."]
templates_other["мн.ч."] = templates_other["мн. ч."]
templates_other["ЖД"] = templates_other["ж.-д."]
templates_other["комп. игр. жарг."] = templates_other["жарг. комп. игр."]
templates_other["нарк."] = templates_other["жарг. нарк."]
templates_other["ж."] = templates_other["f"]
templates_other["электр."] = templates_other["эл.-техн."]
templates_other["жарг. ЛГБТ"] = templates_other["жарг. ЛГБТК+"]
templates_other["жарг. гом."] = templates_other["жарг. ЛГБТК+"]
templates_other["жсравни"] = templates_other["n"]
templates_other["сельхоз."] = templates_other["с.-х."]
templates_other["философ."] = templates_other["филос."]
templates_other["экспресс."] = templates_other["экспр."]
templates_other["палеонтол."] = templates_other["палеонт."]
templates_other["част."] = templates_other["частич."]
templates_other["аним. жарг."] = templates_other["жарг. аним."]
templates_other["тех. жарг."] = templates_other["техн. жарг."]


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ru")
    []
    >>> find_genders("{{сущ ru f ina 5a|основа=страни́ц|слоги={{по-слогам|стра|ни́|ца}}}}", "ru")
    ['f']
    """
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    pattern: re.Pattern[str] = re.compile(rf"(?:\{{сущ.{locale}.)([fmnмжс])|(?:\{{сущ.{locale}.*\|)([fmnмжс])")
    return unique(flatten(pattern.findall(code)))


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> find_pronunciations("", "ru")
    []
    >>> # Expected behaviour after #1376: ['[strɐˈnʲit͡sə]']
    >>> find_pronunciations("{{transcriptions-ru|страни́ца|страни́цы|Ru-страница.ogg}}", "ru")
    ['[stranʲi]']
    """
    pattern = re.compile(rf"(?:transcriptions-{locale}.)(\w*)")
    return unique([transcript(word) for word in pattern.findall(code)])


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

        >>> last_template_handler(["en"], "ru")
        'Английский'

        >>> last_template_handler(["выдел", "foo"], "ru")
        'foo'

        >>> last_template_handler(["аббр.", "ru"], "ru")
        '<i>сокр.</i>'
        >>> last_template_handler(["аббр.", "ru", "Свободная демократическая партия", "без ссылки=1"], "ru")
        '<i>сокр.</i> от <i>Свободная демократическая партия</i>'
        >>> last_template_handler(["аббр.", "ru", "Свободная демократическая партия", "без ссылки=1", ""], "ru")
        '<i>сокр.</i> от <i>Свободная демократическая партия</i>'

        >>> last_template_handler(["рег."], "ru")
        '<i>рег.</i>'
        >>> last_template_handler(["рег.", "", "ru"], "ru")
        '<i>рег.</i>'
        >>> last_template_handler(["рег.", "Латвия"], "ru")
        '<i>рег. (Латвия)</i>'

        >>> last_template_handler(["свойство", "абелев"], "ru")
        'свойство по значению прилагательного <i>абелев</i>'
        >>> last_template_handler(["свойство", "погнутый", "состояние=1"], "ru")
        'свойство или состояние по значению прилагательного <i>погнутый</i>'

        >>> last_template_handler(["нареч.", "адекватный"], "ru")
        'наречие к <i>адекватный</i>'
        >>> last_template_handler(["наречие", "адекватный", "в соответствии с чем-либо"], "ru")
        'наречие к <i>адекватный</i>; в соответствии с чем-либо'

        # Labels
        >>> last_template_handler(["зоол.", "ru"], "ru")
        '<i>зоол.</i>'
        >>> last_template_handler(["сленг", "ru"], "ru")
        '<i>сленг</i>'
        >>> last_template_handler(["сленг.", "ru"], "ru")
        '<i>сленг</i>'
        >>> last_template_handler(["гипокор.", "ru", "Александр"], "ru")
        '<i>гипокор.</i> к Александр'
        >>> last_template_handler(["эррат.", "ru", "Александр"], "ru")
        '<i>эррат.</i> от Александр'
        >>> last_template_handler(["умласк."], "ru")
        '<i>уменьш.-ласк.</i>'

        >>> last_template_handler(["Унбегаун"], "ru")
        '<i>Унбегаун Б.-О.</i> Русские фамилии. — М. : Прогресс, 1989. — 443 с. — ISBN 5-01-001045-3.'
        >>> last_template_handler(["Унбегаун", "сокр=1"], "ru")
        'Унбегаун'
    """
    from ...user_functions import extract_keywords_from, italic
    from .. import defaults
    from .labels import labels
    from .langs import langs
    from .template_handlers import lookup_template, render_template

    tpl, *parts = template

    tpl_variant = f"__variant__{tpl}"
    if variant_only:
        tpl = tpl_variant
        template = tuple([tpl_variant, *parts])
    elif lookup_template(tpl_variant):
        # We are fetching the output of a variant template, we do not want to keep it
        return ""

    if lookup_template(template[0]):
        return render_template(word, template)

    data = extract_keywords_from(parts)

    if tpl in {"рег.", "обл.", "местн."}:
        text = "рег."
        if part := next((p for p in parts if p and p != "ru"), ""):
            text += f" ({part})"
        return italic(text)

    if tpl in {"аббр.", "сокр."}:
        text = italic("сокр.")
        if len(parts) > 1:
            text += f" от {italic(parts[1])}"
        return text

    if tpl in {"многокр."}:
        text = italic(tpl)
        if parts:
            text += f" к {parts[0]}"
        return text

    if tpl in {"превосх."}:
        text = italic("превосх. ст.")
        if parts:
            text += f" к прил. {parts[0]}"
        return text

    if tpl == "выдел":
        return parts[0]

    if tpl in {"наречие", "нареч."}:
        text = f"наречие к {italic(parts[0])}"
        if len(parts) > 1:
            text += f"; {parts[1]}"
        return text

    if tpl == "свойство":
        text = tpl
        if data["состояние"] == "1":
            text += " или состояние"
        return f"{text} по значению прилагательного {italic(parts[0])}"

    if tpl == "Унбегаун":
        if data["сокр"] == "1":
            return tpl
        return f"{italic(f'{tpl} Б.-О.')} Русские фамилии. — М. : Прогресс, 1989. — 443 с. — ISBN 5-01-001045-3."

    if label := (labels.get(tpl) or labels.get(tpl.rstrip("."))):
        if tpl == "умласк.":
            label = "уменьш.-ласк."
        text = italic(label)
        if len(parts) > 1:
            text += f" {'от' if tpl == 'эррат.' else 'к'} {parts[-1]}"
        return text

    if lang := langs.get(tpl):
        return lang

    return defaults.last_template_handler(template, locale, word=word, all_templates=all_templates)


random_word_url = "https://ru.wiktionary.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:RandomRootpage"


def adjust_wikicode(code: str, locale: str) -> str:
    # sourcery skip: inline-immediately-returned-variable
    """
    >>> adjust_wikicode("{{t:=|же}}", "ru")
    '{{_t_|же}}'
    """
    # Workaround to prevent "t:=" to be reduced to "t"
    code = code.replace("{{t:=|", "{{_t_|")

    return code
