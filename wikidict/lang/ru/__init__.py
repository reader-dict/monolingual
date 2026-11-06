"""Russian language."""

import re

from ... import context, lang, utils
from . import variant_handlers as variant_handlers_mod
from .template_overrides import overrides as template_overrides  # noqa: F401
from .variant_handlers import handlers as variant_handlers  # noqa: F401

random_word_url = "https://ru.wiktionary.org/wiki/%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:RandomRootpage"

module_trans = "Модуль"
template_trans = "Шаблон"

section_level = 1
section_sublevels = (3, 4)
head_sections = ("{{-ru-}}", "{{-ru-|nocat}}", "{{-mul-}}")
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
    "синонимы",  # Synonyms
)

variant_templates = ("{{прич.", "{{Форма-")

reverse_variant_templates = ("{{rev-flexion",)
reverse_variant_titles = (
    "{{сущ ru",
    "{{сущ-ru",
    "{{прил ru",
    "{{прил-ru",
    "{{прич ru",
    "{{прич-ru",
    "{{гл ru",
    "{{гл-ru",
    "{{числ ru",
    "{{числ-",  # {{числ-ru}}, {{числ-5}}, {{числ-дцать}}...
    "{{мест ru",
    "{{мест-ru",
    "{{падежи ru",
    "{{Фам ",  # surnames: {{Фам ин ов}}, {{Фам ru f 7a}}...
    "{{Фам-",
    "{{фам ",
    "{{Мс-п",  # possessive adjectives: {{Мс-п6*a}} for "коровий"
)

templates_ignored = (
    "{{?",
    "{{anim",
    "{{DEFAULTSORT",
    "{{improve",
    "{{Lacuna",
    "{{lacuna",
    "{{offensive",
    "{{unfinished",
    "{{wikipedia",
    "{{пример",  # example
    "{{Цитата",  # citation
)


def find_genders(code: str, locale: str) -> list[str]:
    """
    >>> find_genders("", "ru")
    []
    >>> find_genders("{{сущ ru n ina 7a|основа=освеще́ни}}", "ru")
    ['ср']
    >>> find_genders("{{сущ ru f ina 5a|основа=страни́ц|слоги={{по-слогам|стра|ни́|ца}}}}", "ru")
    ['ж']
    >>> find_genders("{{сущ ru m a 2b|}}", "ru")
    ['м']
    >>> find_genders("{{сущ ru пол1|}}", "ru")
    []

    `{{сущ-ru}}` has the gender in its second parameter, in Cyrillic
    >>> find_genders("{{сущ-ru|ма́льчик|мо 3a|}}", "ru")
    ['м']
    >>> find_genders("{{сущ-ru|соба́ка|жо//ж 3a|}}", "ru")
    ['ж']
    >>> find_genders("{{сущ-ru|молоко́|с 3b|}}", "ru")
    ['ср']
    >>> find_genders("{{сущ-ru|дом|м, 1c(1)|}}", "ru")
    ['м']
    >>> find_genders("{{сущ-ru|сирота́|мо-жо 1d|}}", "ru")
    ['м', 'ж']
    >>> find_genders("{{сущ-ru|я́сли|мн.|}}", "ru")
    ['мн']
    >>> find_genders("{{сущ-ru|сепу́лька|hide-text=1|}}", "ru")
    []
    """
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    pattern: re.Pattern[str] = re.compile(
        rf"\{{\{{сущ(?: {locale} ([^ |}}\n]++)|-{locale}\|[^|{{}}\n]*+\|[ ]*+([^ |{{}}\n/,]++))"
    )
    genders = {
        "f": ["ж"],
        "ж": ["ж"],
        "жо": ["ж"],
        "m": ["м"],
        "м": ["м"],
        "мо": ["м"],
        "n": ["ср"],
        "с": ["ср"],
        "со": ["ср"],
        "mf": ["м", "ж"],
        "мо-жо": ["м", "ж"],
        "мн": ["мн"],
        "мн.": ["мн"],
    }
    return utils.unique([gender for match in pattern.findall(code) for gender in genders.get(match[0] or match[1], [])])


def find_pronunciations(code: str, locale: str, word: str = "") -> list[str]:
    """
    The pronunciation of each homonym, starting with the word and its stress.

    >>> from ... import context
    >>> _ = context.reset("ru")

    >>> context.new_word("word")
    >>> find_pronunciations("", "ru")
    []

    >>> find_pronunciations("{{transcriptions-ru|страни́ца|страни́цы|Ru-страница.ogg}}", "ru", "страница")
    ['страни́ца [strɐˈnʲit͡sə]']

    >>> context.new_word("кажется")
    >>> find_pronunciations("{{transcription-ru|ка́жется|Ru-кажется.ogg}}", "ru", "кажется")
    ['ка́жется [ˈkaʐɨt͡sə]']

    >>> context.new_word("атлас")
    >>> find_pronunciations("{{transcriptions-ru|а́тлас|а́тласы||}}\\n{{transcription-ru|атла́с|}}", "ru", "атлас")
    ['а́тлас [ˈatɫəs]', 'атла́с [ɐˈtɫas]']

    >>> context.new_word("стол")
    >>> find_pronunciations("{{transcriptions-ru|стол|столы́}}", "ru", "стол")
    ['[stoɫ]']
    """
    # Each stressed spelling with its first pronunciation: homonyms stressed differently get one each,
    # a word with several pronunciations ("провожжа́ться" [ʑː] and [ʐː]) only the first one, as before
    found: dict[str, str] = {}
    for tpl in re.finditer(rf"\{{\{{transcriptions?-{locale}\|([^|}}\n]*+)[^}}\n]*+}}}}", code):
        lines = context.expand(tpl[0], "ru").splitlines()
        ipa = next((f"[{m[1]}]" for line in lines if (m := _IPA_SINGULAR.search(line))), "")
        ipa = ipa or next((f"[{m[1]}]" for line in lines if (m := _IPA.search(line))), "")
        stressed = utils.stress_word(word, tpl[1]) if word and "=" not in tpl[1] else ""
        if (stressed or ipa) and stressed not in found:
            found[stressed] = ipa
    if len(found) > 1:
        found.pop("", None)
    return [" ".join(part for part in (stressed, ipa) if part) for stressed, ipa in found.items()]


_IPA_SINGULAR = re.compile(r"ед\.&nbsp;ч\.&nbsp;&#91;([^&]++)&#93;")
_IPA = re.compile(r"&#91;([^&]++)&#93;")


_EXAMPLE = re.compile(r"[ ]*\{\{(?:[Пп]ример|[Цц]итата)\b")


def strip_examples(line: str) -> str:
    """
    Remove the usage examples (`{{пример|...}}`, `{{Цитата|...}}`) from a definition line,
    even when their braces are not balanced.

    >>> strip_examples("# a {{пример|x {{выдел|y}} z}} b")
    '# a b'
    >>> strip_examples("# a {{пример|Белов}|x}} {{пример|q}}.")
    '# a.'
    >>> strip_examples("# a {{пример|never closed {{выдел|y}}")
    '# a'
    >>> strip_examples("# a {{пример|{{{1|}}}}} c")
    '# a c'
    >>> strip_examples("# a {{Пример|x}} b {{цитата|y}}")
    '# a b'
    >>> strip_examples("# a {{примерно}}")
    '# a {{примерно}}'
    """
    out: list[str] = []
    pos = 0
    while m := _EXAMPLE.search(line, pos):
        out.append(line[pos : m.start()])
        i, stack = m.end(), [2]
        while stack and i < len(line):
            if line.startswith("{{{", i):
                stack.append(3)
                i += 3
            elif line.startswith("{{", i):
                stack.append(2)
                i += 2
            elif stack[-1] == 3 and line.startswith("}}}", i):
                stack.pop()
                i += 3
            elif line.startswith("}}", i):
                stack.pop()
                i += 2
            else:
                i += 1
        pos = i  # an example that is never closed is dropped up to the end of the line
    out.append(line[pos:])
    return "".join(out)


def adjust_wikicode(
    code: str,
    locale: str,
    *,
    templates_status: list[tuple[str, str]] | None = None,
    word: str = "",
) -> str:
    # sourcery skip: inline-immediately-returned-variable
    r"""
    >>> adjust_wikicode("= {{-ru-|nocat}} =\n{{Форма-гл\n|база=выбирать}}", "ru", word="выбирали")
    '= {{-ru-|nocat}} =\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл\n|база=выбирать}}'
    >>> adjust_wikicode("= {{-ru-}}=\n{{не так|надо=идти}}\n{{Форма-гл|база=идти|накл=inf}}", "ru", word="итти")
    '= {{-ru-}}=\n{{не так|надо=идти}}\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл|база=идти|накл=inf}}'
    >>> adjust_wikicode("= {{-ru-}} =\n{{Омонимы|ru|2}}\n== {{з|(существительное)}} ==\n{{Форма-сущ|луч|ив|мн}}\n== {{з|(глагол)}} ==\n{{Форма-гл|лучить||2|ед|п}}", "ru", word="лучи")
    '= {{-ru-}} =\n{{Омонимы|ru|2}}\n== {{з|(существительное)}} ==\n=== Морфологические и синтаксические свойства ===\n{{Форма-сущ|луч|ив|мн}}\n== {{з|(глагол)}} ==\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл|лучить||2|ед|п}}'
    >>> adjust_wikicode("= {{-ru-}} =\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл|база=идти}}", "ru", word="иду")
    '= {{-ru-}} =\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл|база=идти}}'
    >>> adjust_wikicode("={{-ru-}}=\n== {{з|ударение=пе́кла}} ==\n* {{Форма-сущ|пе́кло|р|1}}\n* {{Форма-сущ|пе́кло|ив|мн}}", "ru", word="пекла")
    '={{-ru-}}=\n== {{з|ударение=пе́кла}} ==\n=== Морфологические и синтаксические свойства ===\n* {{Форма-сущ|пе́кло|р|1}}\n* {{Форма-сущ|пе́кло|ив|мн}}'
    >>> adjust_wikicode("= {{-ru-}} =\n'''км'''\n* {{сокращ|[[километр]]|ед|ru|до=длины}}", "ru", word="км")
    "= {{-ru-}} =\n'''км'''\n==== Значение ====\n# {{сокращ|[[километр]]|ед|ru|до=длины}}"
    >>> adjust_wikicode("= {{-ru-}} =\n'''н. э.'''\n* {{истор.|-}} {{сокращ|[[наша эра]]|гс|ru}}\n** Ср. [[до н. э.]]", "ru", word="н. э.")
    "= {{-ru-}} =\n'''н. э.'''\n==== Значение ====\n# {{истор.|-}} {{сокращ|[[наша эра]]|гс|ru}}\n** Ср. [[до н. э.]]"

    >>> adjust_wikicode("= {{-ru-}} =\n=== Этимология ===\nПроисходит от {{этимология:δίσκος|да}}.{{etym-lang|{{{1|ru}}}|grc}}", "ru", word="дискос")
    '= {{-ru-}} =\n=== Этимология ===\nПроисходит от {{этимология:δίσκος|да}}.'

    >>> adjust_wikicode("= {{-ru-}} =\n==== Синонимы ====\n# —\n#\n", "ru", word="гонит")
    '= {{-ru-}} =\n==== Синонимы ====\n\n#\n'
    >>> adjust_wikicode("= {{-ru-}} =\n==== Синонимы ====\n# ?\n#\n", "ru", word="гонит")
    '= {{-ru-}} =\n==== Синонимы ====\n\n#\n'
    >>> adjust_wikicode("= {{-ru-}} =\n==== Синонимы ====\n#{{aslinks|хлопоты\n#внимание, [[попечение|попечения]]|#,}}\n# {{aslinks|вера, доверие}}", "ru", word="забота")
    '= {{-ru-}} =\n==== Синонимы ====\n#хлопоты\n#внимание, [[попечение|попечения]]\n# {{aslinks|вера, доверие}}'

    >>> from ... import context
    >>> _ = context.reset("ru")

    >>> context.new_word("король")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru m a 2b|основа=коро́л|основа1=корол}}", "ru", word="король")
    '= {{-ru-}} =\n{{сущ ru m a 2b|}}\n# {{rev-flexion|короле}}\n# {{rev-flexion|королей}}\n# {{rev-flexion|короли}}\n# {{rev-flexion|королю}}\n# {{rev-flexion|короля}}\n# {{rev-flexion|королям}}\n# {{rev-flexion|королями}}\n# {{rev-flexion|королях}}\n# {{rev-flexion|королём}}'

    >>> context.new_word("бессудорожный")
    >>> adjust_wikicode("= {{-ru-}} =\n{{прил ru 1*a\n|основа=бессу́дорожн\n|основа1=\n|тип=\n|слоги={{по-слогам|бес|су́|до|рож|ный}}\n|степень=\n|краткая=\n|коммент=\n|дореф=\n}}\n\n{{слобр|ru|судорожный|{{выдел|бес}} + судорожный|п|и=}}\n{{морфо-ru|бес-|судорож|-н|+ый}}", "ru", word="бессудорожный")
    '= {{-ru-}} =\n{{прил ru 1*a|}}\n# {{rev-flexion|бессудорожна}}\n# {{rev-flexion|бессудорожная}}\n# {{rev-flexion|бессудорожно}}\n# {{rev-flexion|бессудорожного}}\n# {{rev-flexion|бессудорожное}}\n# {{rev-flexion|бессудорожной}}\n# {{rev-flexion|бессудорожном}}\n# {{rev-flexion|бессудорожному}}\n# {{rev-flexion|бессудорожною}}\n# {{rev-flexion|бессудорожную}}\n# {{rev-flexion|бессудорожны}}\n# {{rev-flexion|бессудорожные}}\n# {{rev-flexion|бессудорожным}}\n# {{rev-flexion|бессудорожными}}\n# {{rev-flexion|бессудорожных}}\n\n{{слобр|ru|судорожный|{{выдел|бес}} + судорожный|п|и=}}\n{{морфо-ru|бес-|судорож|-н|+ый}}'

    >>> context.new_word("Адрианович")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru m a 4a\n|основа={{PAGENAME}}\n|основа1={{PAGENAME}}\n|слоги={{по-слогам|Ад|ри|.|а́|.|но|вич}}\n}} {{собств.|ru|тип=отчество}}", "ru", word="Адрианович")
    '= {{-ru-}} =\n{{сущ ru m a 4a|}}\n# {{rev-flexion|Адриановича}}\n# {{rev-flexion|Адриановичам}}\n# {{rev-flexion|Адриановичами}}\n# {{rev-flexion|Адриановичах}}\n# {{rev-flexion|Адриановиче}}\n# {{rev-flexion|Адриановичей}}\n# {{rev-flexion|Адриановичем}}\n# {{rev-flexion|Адриановичи}}\n# {{rev-flexion|Адриановичу}}'

    >>> context.new_word("подельник")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru m a 3a\n|основа=поде́льник\n|слоги={{по-слогам|по|де́ль|ник}}\n}}", "ru", word="подельник")
    '= {{-ru-}} =\n{{сущ ru m a 3a|}}\n# {{rev-flexion|подельника}}\n# {{rev-flexion|подельникам}}\n# {{rev-flexion|подельниками}}\n# {{rev-flexion|подельниках}}\n# {{rev-flexion|подельнике}}\n# {{rev-flexion|подельники}}\n# {{rev-flexion|подельников}}\n# {{rev-flexion|подельником}}\n# {{rev-flexion|подельнику}}'

    >>> context.new_word("хвост")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru m ina 1b\n|основа=хвост\n|основа1=хвост\n|слоги={{по слогам|хвост}}\n|М=(на)&nbsp;хвосте́;<br/>(на)&nbsp;хвосту́&nbsp;({{устар.|-}})\n}}", "ru", word="хвост")
    '= {{-ru-}} =\n{{сущ ru m ina 1b|}}\n# {{rev-flexion|хвоста}}\n# {{rev-flexion|хвостам}}\n# {{rev-flexion|хвостами}}\n# {{rev-flexion|хвостах}}\n# {{rev-flexion|хвосте}}\n# {{rev-flexion|хвостов}}\n# {{rev-flexion|хвостом}}\n# {{rev-flexion|хвосту}}\n# {{rev-flexion|хвосты}}'

    >>> context.new_word("виться")
    >>> adjust_wikicode("= {{-ru-}} =\n{{гл ru 11b/c''-ся\n|основа=в\n|слоги={{по-слогам|ви́|ться}}\n}}", "ru", word="виться")
    '= {{-ru-}} =\n{{гл ru 11b/c-ся|}}\n# {{rev-flexion|вейся}}\n# {{rev-flexion|вейтесь}}\n# {{rev-flexion|вившаяся}}\n# {{rev-flexion|вившегося}}\n# {{rev-flexion|вившееся}}\n# {{rev-flexion|вившейся}}\n# {{rev-flexion|вившемся}}\n# {{rev-flexion|вившемуся}}\n# {{rev-flexion|вившеюся}}\n# {{rev-flexion|вившиеся}}\n# {{rev-flexion|вившийся}}\n# {{rev-flexion|вившимися}}\n# {{rev-flexion|вившимся}}\n# {{rev-flexion|вившись}}\n# {{rev-flexion|вившихся}}\n# {{rev-flexion|вившуюся}}\n# {{rev-flexion|вилась}}\n# {{rev-flexion|вились}}\n# {{rev-flexion|вилось}}\n# {{rev-flexion|вился}}\n# {{rev-flexion|вьюсь}}\n# {{rev-flexion|вьются}}\n# {{rev-flexion|вьющаяся}}\n# {{rev-flexion|вьющегося}}\n# {{rev-flexion|вьющееся}}\n# {{rev-flexion|вьющейся}}\n# {{rev-flexion|вьющемся}}\n# {{rev-flexion|вьющемуся}}\n# {{rev-flexion|вьющеюся}}\n# {{rev-flexion|вьющиеся}}\n# {{rev-flexion|вьющийся}}\n# {{rev-flexion|вьющимися}}\n# {{rev-flexion|вьющимся}}\n# {{rev-flexion|вьющихся}}\n# {{rev-flexion|вьющуюся}}\n# {{rev-flexion|вьёмся}}\n# {{rev-flexion|вьётесь}}\n# {{rev-flexion|вьётся}}\n# {{rev-flexion|вьёшься}}'

    `|степень=1` is not a comparative, and an HTML entity in the stem is not cut
    >>> context.new_word("аборальный")
    >>> adjust_wikicode("= {{-ru-}} =\n{{прил ru 1*a\n|основа=абора́льн\n|основа1=абора́лен\n|степень=1\n}}", "ru", word="аборальный")
    '= {{-ru-}} =\n{{прил ru 1*a|}}\n# {{rev-flexion|аборален}}\n# {{rev-flexion|аборальна}}\n# {{rev-flexion|аборальная}}\n# {{rev-flexion|аборально}}\n# {{rev-flexion|аборального}}\n# {{rev-flexion|аборальное}}\n# {{rev-flexion|аборальной}}\n# {{rev-flexion|аборальном}}\n# {{rev-flexion|аборальному}}\n# {{rev-flexion|аборальною}}\n# {{rev-flexion|аборальную}}\n# {{rev-flexion|аборальны}}\n# {{rev-flexion|аборальные}}\n# {{rev-flexion|аборальным}}\n# {{rev-flexion|аборальными}}\n# {{rev-flexion|аборальных}}'
    >>> context.new_word("Гётеборг")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru m ina 3a\n|основа=Гё&#768;тебо́рг\n}}", "ru", word="Гётеборг")
    '= {{-ru-}} =\n{{сущ ru m ina 3a|}}\n# {{rev-flexion|Гётеборга}}\n# {{rev-flexion|Гётеборгам}}\n# {{rev-flexion|Гётеборгами}}\n# {{rev-flexion|Гётеборгах}}\n# {{rev-flexion|Гётеборге}}\n# {{rev-flexion|Гётеборги}}\n# {{rev-flexion|Гётеборгов}}\n# {{rev-flexion|Гётеборгом}}\n# {{rev-flexion|Гётеборгу}}'

    >>> context.new_word("оба")
    >>> adjust_wikicode("= {{-ru-}} =\n{{числ ru оба\n|основа=о́б\n|основа1=об\n|слоги={{по-слогам|о́|.|ба}}\n|тип=собирательное\n}}", "ru", word="оба")
    '= {{-ru-}} =\n{{числ ru оба|}}\n# {{rev-flexion|обе}}\n# {{rev-flexion|обеим}}\n# {{rev-flexion|обеими}}\n# {{rev-flexion|обеих}}\n# {{rev-flexion|обоим}}\n# {{rev-flexion|обоими}}\n# {{rev-flexion|обоих}}'

    >>> context.new_word("бежать")
    >>> adjust_wikicode("= {{-ru-}} =\n{{гл ru 5b-ж\n|основа=беж\n|основа1=бег\n|основа2=бе́г\n|слоги={{по слогам|бе|жа́ть}}\n|дореф=бѣжа́ть\n|2в=1\n|коммент=В некоторых значениях «бежать» может использоваться как глагол совершенного вида, особенно в формах прош. времени: {{пример|преступники {{выдел|бежали}} из тюрьмы}} {{пример|враг {{выдел|бежал}}}} {{пример|он {{выдел|бежал}} городской суеты}} {{пример|суп {{выдел|бежал}}}}. В 3л. мн.ч. употребляется нестандартная форма «''бегу́т''». До XIX также равноправной формой была форма «''бежа́т''» (см. пример).\n|imper-1p=1\n}}", "ru", word="бежать")
    '= {{-ru-}} =\n{{гл ru 5b-ж|}}\n# {{rev-flexion|беган}}\n# {{rev-flexion|бегана}}\n# {{rev-flexion|беганная}}\n# {{rev-flexion|беганного}}\n# {{rev-flexion|беганное}}\n# {{rev-flexion|беганной}}\n# {{rev-flexion|беганном}}\n# {{rev-flexion|беганному}}\n# {{rev-flexion|беганною}}\n# {{rev-flexion|беганную}}\n# {{rev-flexion|беганные}}\n# {{rev-flexion|беганный}}\n# {{rev-flexion|беганным}}\n# {{rev-flexion|беганными}}\n# {{rev-flexion|беганных}}\n# {{rev-flexion|бегано}}\n# {{rev-flexion|беганы}}\n# {{rev-flexion|беги}}\n# {{rev-flexion|бегите}}\n# {{rev-flexion|бегу}}\n# {{rev-flexion|бегут}}\n# {{rev-flexion|бегущая}}\n# {{rev-flexion|бегущего}}\n# {{rev-flexion|бегущее}}\n# {{rev-flexion|бегущей}}\n# {{rev-flexion|бегущем}}\n# {{rev-flexion|бегущему}}\n# {{rev-flexion|бегущею}}\n# {{rev-flexion|бегущие}}\n# {{rev-flexion|бегущий}}\n# {{rev-flexion|бегущим}}\n# {{rev-flexion|бегущими}}\n# {{rev-flexion|бегущих}}\n# {{rev-flexion|бегущую}}\n# {{rev-flexion|бежа}}\n# {{rev-flexion|бежав}}\n# {{rev-flexion|бежавшая}}\n# {{rev-flexion|бежавшего}}\n# {{rev-flexion|бежавшее}}\n# {{rev-flexion|бежавшей}}\n# {{rev-flexion|бежавшем}}\n# {{rev-flexion|бежавшему}}\n# {{rev-flexion|бежавшею}}\n# {{rev-flexion|бежавши}}\n# {{rev-flexion|бежавшие}}\n# {{rev-flexion|бежавший}}\n# {{rev-flexion|бежавшим}}\n# {{rev-flexion|бежавшими}}\n# {{rev-flexion|бежавших}}\n# {{rev-flexion|бежавшую}}\n# {{rev-flexion|бежал}}\n# {{rev-flexion|бежала}}\n# {{rev-flexion|бежали}}\n# {{rev-flexion|бежало}}\n# {{rev-flexion|бежим}}\n# {{rev-flexion|бежима}}\n# {{rev-flexion|бежимая}}\n# {{rev-flexion|бежимо}}\n# {{rev-flexion|бежимого}}\n# {{rev-flexion|бежимое}}\n# {{rev-flexion|бежимой}}\n# {{rev-flexion|бежимом}}\n# {{rev-flexion|бежимому}}\n# {{rev-flexion|бежимою}}\n# {{rev-flexion|бежимую}}\n# {{rev-flexion|бежимы}}\n# {{rev-flexion|бежимые}}\n# {{rev-flexion|бежимый}}\n# {{rev-flexion|бежимым}}\n# {{rev-flexion|бежимыми}}\n# {{rev-flexion|бежимых}}\n# {{rev-flexion|бежит}}\n# {{rev-flexion|бежите}}\n# {{rev-flexion|бежишь}}'

    >>> context.new_word("нутряной")
    >>> adjust_wikicode("= {{-ru-}} =\n{{прил ru 1bX\n|основа=нутрян\n|основа1=\n|слоги={{по-слогам|нутряно́й}}\n|тип=относительное\n|степень=\n|краткая=\n|Категория={{{Категория|Прилагательные, склонение 1bX}}}\n}}", "ru", word="нутряной")
    '= {{-ru-}} =\n{{прил ru 1bX|}}\n# {{rev-flexion|нутряна}}\n# {{rev-flexion|нутряная}}\n# {{rev-flexion|нутряно}}\n# {{rev-flexion|нутряного}}\n# {{rev-flexion|нутряное}}\n# {{rev-flexion|нутряном}}\n# {{rev-flexion|нутряному}}\n# {{rev-flexion|нутряною}}\n# {{rev-flexion|нутряную}}\n# {{rev-flexion|нутряны}}\n# {{rev-flexion|нутряные}}\n# {{rev-flexion|нутряным}}\n# {{rev-flexion|нутряными}}\n# {{rev-flexion|нутряных}}'

    >>> context.new_word("фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтаза")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru f ina 1a\n|основа=фо̀сфорибозѝл-аминоимидазо̀л-сукцинокарбоксамѝд-синта́з\n|слоги={{по-слогам|фос|фо|ри|бо|зил|-|а|.|ми|но|и|ми|да|зол-}}{{по-слогам|сук|ци|но|кар|бо|кса|мид|-|син|та́|за}}\n}}", "ru", word="фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтаза")
    '= {{-ru-}} =\n{{сущ ru f ina 1a|}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтаз}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазам}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазами}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазах}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазе}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазой}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазою}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазу}}\n# {{rev-flexion|фосфорибозил-аминоимидазол-сукцинокарбоксамид-синтазы}}'

    >>> context.new_word("существо")
    >>> adjust_wikicode("= {{-ru-}} =\n{{сущ ru n a 1b\n|основа=существ\n|основа1=суще́ств\n|слоги={{по-слогам|су|ще|ство́}}\n}}", "ru", word="существо")
    '= {{-ru-}} =\n{{сущ ru n a 1b|}}\n# {{rev-flexion|существ}}\n# {{rev-flexion|существа}}\n# {{rev-flexion|существам}}\n# {{rev-flexion|существами}}\n# {{rev-flexion|существах}}\n# {{rev-flexion|существе}}\n# {{rev-flexion|существом}}\n# {{rev-flexion|существу}}'

    >>> context.new_word("дванадесять")
    >>> adjust_wikicode("= {{-ru-}} =\n{{числ ru дванадесять|основа=дв|соотв=двунадесятый|слоги={{по-слогам|два|на́|де|сять}}}}", "ru", word="дванадесять")
    '= {{-ru-}} =\n{{числ ru дванадесять|}}\n# {{rev-flexion|дванадесят}}\n# {{rev-flexion|двенадесят}}\n# {{rev-flexion|двумнадесят}}\n# {{rev-flexion|двумянадесят}}\n# {{rev-flexion|двухнадесят}}'

    >>> context.new_word("торос")
    >>> adjust_wikicode("{{сущ ru m ina 1a^\n|основа=то́рос\n|основа1=торо́с\n|слоги={{по слогам|то|ро́с}}\n|зачин=Также существует вариант склонения по схеме 1a^.\n}}", "ru", word="торос")
    '{{сущ ru m ina 1a^|}}\n# {{rev-flexion|тороса}}\n# {{rev-flexion|торосе}}\n# {{rev-flexion|торосом}}\n# {{rev-flexion|торосу}}\n# {{rev-flexion|торосьев}}\n# {{rev-flexion|торосья}}\n# {{rev-flexion|торосьям}}\n# {{rev-flexion|торосьями}}\n# {{rev-flexion|торосьях}}'

    >>> context.new_word("сидеть")
    >>> adjust_wikicode("= {{-ru-}} =\n{{гл ru 5b^-т\n|основа=сид\n|основа1=сиж\n|основа2=си́д\n|слоги={{по-слогам|си|де́ть}}\n}}", "ru", word="сидеть")
    '= {{-ru-}} =\n{{гл ru 5b^-т|}}\n# {{rev-flexion|сидев}}\n# {{rev-flexion|сидевшая}}\n# {{rev-flexion|сидевшего}}\n# {{rev-flexion|сидевшее}}\n# {{rev-flexion|сидевшей}}\n# {{rev-flexion|сидевшем}}\n# {{rev-flexion|сидевшему}}\n# {{rev-flexion|сидевшею}}\n# {{rev-flexion|сидевши}}\n# {{rev-flexion|сидевшие}}\n# {{rev-flexion|сидевший}}\n# {{rev-flexion|сидевшим}}\n# {{rev-flexion|сидевшими}}\n# {{rev-flexion|сидевших}}\n# {{rev-flexion|сидевшую}}\n# {{rev-flexion|сидел}}\n# {{rev-flexion|сидела}}\n# {{rev-flexion|сидели}}\n# {{rev-flexion|сидело}}\n# {{rev-flexion|сиди}}\n# {{rev-flexion|сидим}}\n# {{rev-flexion|сидима}}\n# {{rev-flexion|сидимая}}\n# {{rev-flexion|сидимо}}\n# {{rev-flexion|сидимого}}\n# {{rev-flexion|сидимое}}\n# {{rev-flexion|сидимой}}\n# {{rev-flexion|сидимом}}\n# {{rev-flexion|сидимому}}\n# {{rev-flexion|сидимою}}\n# {{rev-flexion|сидимую}}\n# {{rev-flexion|сидимы}}\n# {{rev-flexion|сидимые}}\n# {{rev-flexion|сидимый}}\n# {{rev-flexion|сидимым}}\n# {{rev-flexion|сидимыми}}\n# {{rev-flexion|сидимых}}\n# {{rev-flexion|сидит}}\n# {{rev-flexion|сидите}}\n# {{rev-flexion|сидишь}}\n# {{rev-flexion|сидя}}\n# {{rev-flexion|сидят}}\n# {{rev-flexion|сидящая}}\n# {{rev-flexion|сидящего}}\n# {{rev-flexion|сидящее}}\n# {{rev-flexion|сидящей}}\n# {{rev-flexion|сидящем}}\n# {{rev-flexion|сидящему}}\n# {{rev-flexion|сидящею}}\n# {{rev-flexion|сидящие}}\n# {{rev-flexion|сидящий}}\n# {{rev-flexion|сидящим}}\n# {{rev-flexion|сидящими}}\n# {{rev-flexion|сидящих}}\n# {{rev-flexion|сидящую}}\n# {{rev-flexion|сижу}}'

    >>> context.new_word("Тургенев")
    >>> adjust_wikicode("= {{-ru-}} =\n{{Фам ин ов\n|основа=Турге́нев\n|слоги={{по-слогам|Тур|ге́|нев}}\n}}", "ru", word="Тургенев")
    '= {{-ru-}} =\n{{Фам ин ов|}}\n# {{rev-flexion|Тургенева}}\n# {{rev-flexion|Тургеневе}}\n# {{rev-flexion|Тургеневой}}\n# {{rev-flexion|Тургеневу}}\n# {{rev-flexion|Тургеневы}}\n# {{rev-flexion|Тургеневым}}\n# {{rev-flexion|Тургеневыми}}\n# {{rev-flexion|Тургеневых}}'

    >>> context.new_word("коровий")
    >>> adjust_wikicode("= {{-ru-}} =\n{{Мс-п6*a\n|основа=коро́в\n|слоги={{по-слогам|ко|ро́|вий}}\n}}", "ru", word="коровий")
    '= {{-ru-}} =\n{{Мс-п6*a|}}\n# {{rev-flexion|коровье}}\n# {{rev-flexion|коровьего}}\n# {{rev-flexion|коровьей}}\n# {{rev-flexion|коровьем}}\n# {{rev-flexion|коровьему}}\n# {{rev-flexion|коровьею}}\n# {{rev-flexion|коровьи}}\n# {{rev-flexion|коровьим}}\n# {{rev-flexion|коровьими}}\n# {{rev-flexion|коровьих}}\n# {{rev-flexion|коровью}}\n# {{rev-flexion|коровья}}'

    >>> context.new_word("шесть")
    >>> adjust_wikicode("= {{-ru-}} =\n{{числ-5\n|основа=ше́ст\n|основа1=шест\n|соотв=[[шестой|шесто́й]]\n}}", "ru", word="шесть")
    '= {{-ru-}} =\n{{числ-5|}}\n# {{rev-flexion|шести}}\n# {{rev-flexion|шестью}}'

    >>> context.new_word("хвост")
    >>> adjust_wikicode("= {{-ru-}} =\n{{ сущ ru m ina 1b\n|основа=хвост\n|основа1=хвост\n}}", "ru", word="хвост")
    '= {{-ru-}} =\n{{сущ ru m ina 1b|}}\n# {{rev-flexion|хвоста}}\n# {{rev-flexion|хвостам}}\n# {{rev-flexion|хвостами}}\n# {{rev-flexion|хвостах}}\n# {{rev-flexion|хвосте}}\n# {{rev-flexion|хвостов}}\n# {{rev-flexion|хвостом}}\n# {{rev-flexion|хвосту}}\n# {{rev-flexion|хвосты}}'

    >>> context.new_word("крепкий")
    >>> adjust_wikicode("= {{-ru-}} =\n{{прил ru 3*a/c'\n|основа=кре́пк\n|основа1=кре́пок\n|основа2=крепк\n|степень=кре́пче\n}}", "ru", word="крепкий")
    "= {{-ru-}} =\n{{прил ru 3*a/c'|}}\n# {{rev-flexion|крепка}}\n# {{rev-flexion|крепкая}}\n# {{rev-flexion|крепки}}\n# {{rev-flexion|крепкие}}\n# {{rev-flexion|крепким}}\n# {{rev-flexion|крепкими}}\n# {{rev-flexion|крепких}}\n# {{rev-flexion|крепко}}\n# {{rev-flexion|крепкого}}\n# {{rev-flexion|крепкое}}\n# {{rev-flexion|крепкой}}\n# {{rev-flexion|крепком}}\n# {{rev-flexion|крепкому}}\n# {{rev-flexion|крепкою}}\n# {{rev-flexion|крепкую}}\n# {{rev-flexion|крепок}}\n# {{rev-flexion|крепче}}"

    >>> context.new_word("некий")
    >>> adjust_wikicode("= {{-ru-}} =\n{{прил ru 3a^+\n|основа=не́к\n}}", "ru", word="некий")
    '= {{-ru-}} =\n{{прил ru 3a^+|}}\n# {{rev-flexion|некая}}\n# {{rev-flexion|некие}}\n# {{rev-flexion|неким}}\n# {{rev-flexion|некими}}\n# {{rev-flexion|неких}}\n# {{rev-flexion|некое}}\n# {{rev-flexion|некоего}}\n# {{rev-flexion|некоей}}\n# {{rev-flexion|некоем}}\n# {{rev-flexion|некоему}}\n# {{rev-flexion|некоею}}\n# {{rev-flexion|некоим}}\n# {{rev-flexion|некоими}}\n# {{rev-flexion|некоих}}\n# {{rev-flexion|некой}}\n# {{rev-flexion|некою}}\n# {{rev-flexion|некую}}'

    >>> context.new_word("два")
    >>> adjust_wikicode("= {{-ru-}} =\n{{числ-2\n|основа=дв\n|соотв=второ́й\n}}", "ru", word="два")
    '= {{-ru-}} =\n{{числ-2|}}\n# {{rev-flexion|две}}\n# {{rev-flexion|двум}}\n# {{rev-flexion|двумя}}\n# {{rev-flexion|двух}}'

    >>> context.new_word("он")
    >>> adjust_wikicode("= {{-ru-}} =\n{{падежи ru 1\n|nom=он\n|gen=[[его|его́]]{{^|△}},&nbsp;[[него|него́]]{{^|△}}\n|dat=[[ему|ему́]]{{^|△}},&nbsp;[[нему|нему́]]{{^|△}}\n|ins=[[им]]{{^|△}},&nbsp;[[ним]]{{^|△}}\n|prp=[[нём]]{{^|△}}\n}}", "ru", word="он")
    '= {{-ru-}} =\n{{падежи ru 1|}}\n# {{rev-flexion|его}}\n# {{rev-flexion|ему}}\n# {{rev-flexion|им}}\n# {{rev-flexion|него}}\n# {{rev-flexion|нему}}\n# {{rev-flexion|ним}}\n# {{rev-flexion|нём}}'
    """

    # Form pages without a subsection, also under homonym headers:
    # `= {{-ru-}} =\n{{Форма-гл...` → `= {{-ru-}} =\n=== Морфологические и синтаксические свойства ===\n{{Форма-гл...`
    # `== {{з|(существительное)}} ==\n{{Форма-сущ...` → `== ... ==\n=== Морфологические и синтаксические свойства ===\n{{Форма-сущ...`
    code = re.sub(
        r"^(==?[ ]*+[^=\n][^\n]*+\n)((?:[^=\n][^\n]*+\n)*?)(?=(?:\*[ ]*+)?\{\{Форма-)",
        r"\1\2=== Морфологические и синтаксические свойства ===\n",
        code,
        flags=re.MULTILINE,
    )

    # Abbreviation pages have no subsection, and the definition is a bullet:
    # `= {{-ru-}} =\n'''км'''\n* {{сокращ|[[километр]]|ед|ru}}` → `= {{-ru-}} =\n'''км'''\n==== Значение ====\n# {{сокращ|...`
    code = re.sub(
        r"^(==?[ ]*+[^=\n][^\n]*+\n)((?:[^=\n][^\n]*+\n)*?)(?=\*(?!\*)[^\n]*?\{\{сокращ)",
        r"\1\2==== Значение ====\n",
        code,
        flags=re.MULTILINE,
    )
    code = re.sub(r"^\*(?!\*)([^\n]*?\{\{сокращ)", r"#\1", code, flags=re.MULTILINE)

    # A list written inside `{{aslinks}}` (it only turns the words into links) was cut into broken list items:
    # `#{{aslinks|хлопоты\n#внимание, попечение|#,}}` → `#хлопоты\n#внимание, попечение`
    code = re.sub(
        r"\{\{aslinks\|((?:[^{}|\[\n]|\[\[[^\[\]]*+\]\])*+\n(?:[^{}|\[]|\[\[[^\[\]]*+\]\])*+)(?:\|[^{}]*+)?\}\}",
        r"\1",
        code,
    )

    # Usage examples are not kept anyway, and a broken one (an unbalanced brace) dropped the whole definition
    code = "\n".join(strip_examples(line) if line.startswith("#") else line for line in code.split("\n"))

    # Synonyms go under their meaning: as a list of their own, they were not numbered like the meanings
    code = utils.attach_synonyms(code, "значение", "синонимы", "син.", forms=variant_templates)

    # Delete empty synonyms
    code = re.sub(r"^#[ ]*+[—\-?][ ]*+$", "", code, flags=re.MULTILINE)

    # Remove `{{etym-lang|...}}`
    code = re.sub(r"\{\{etym-lang\|[^\n]++", "", code, flags=re.MULTILINE)

    #
    # Reverse variants
    #

    # `{{ прил ru 3a/c"` → `{{прил ru 3a/c"`
    code = re.sub(r"^\{\{[ ]++", "{{", code, flags=re.MULTILINE)

    interesting_reverse_variant_titles = lang.reverse_variant_titles[locale]
    if any(tpl in code for tpl in interesting_reverse_variant_titles):
        cleaned: list[str] = []
        in_tpl = False
        tpl_code = ""

        for line in code.splitlines():
            if line.startswith(interesting_reverse_variant_titles):
                in_tpl = True

            if in_tpl:
                if line.startswith(("|коммент", "|Категория")):
                    continue

                tpl_code += line
                if tpl_code.count("{") == tpl_code.count("}"):
                    in_tpl = False
                    # Remove unrelated templates after a reverse variant one
                    # `{{сущ ru m a 4a|...}} {{собств.|ru|тип=отчество}}` → `{{сущ ru m a 4a|...}}`
                    tpl_code = extract_templates(tpl_code)[0]

                    tpl_name = tpl_code[2 : max(0, tpl_code.find("|")) or tpl_code.find("}")].strip().replace("''", "")
                    variant_handlers_mod.append_to_reverse_variants(tpl_name)

                    forms = utils.process_templates(
                        word,
                        tpl_code,
                        locale,
                        templates_status=templates_status,
                        variant_only=True,
                    )
                    if not forms and tpl_name in {"прил ru", "прич ru"}:
                        # No declension type, so no table
                        forms = "|".join(form for form in decline_adjective(word) if form != word)
                    if forms and tpl_name.startswith(("гл ru", "гл-ru")):
                        forms = "|".join(
                            sorted({f for form in forms.split("|") for f in decline_participle(form, word)})
                        )
                    # This is required for genders finding: `{{сущ ru f ina 1a|}}`, and `{{сущ-ru|коса́|f ina 1d|}}`
                    # as that template has the gender in its second parameter
                    placeholder = tpl_name
                    if params := re.match(r"\{\{сущ-ru\|([^|{}]*+)\|([^|{}]*+)", tpl_code):
                        placeholder += f"|{params[1]}|{params[2]}"
                    cleaned.append(f"{{{{{placeholder}|}}}}")
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code


def decline_adjective(word: str) -> list[str]:
    """
    The forms of an adjective or a participle whose table has no declension type, and so is empty.
    Only the endings that decline one way are handled.

    >>> decline_adjective("быстроглазый")[:4]
    ['быстроглазый', 'быстроглазого', 'быстроглазому', 'быстроглазым']
    >>> decline_adjective("западно-сибирский")[-3:]
    ['западно-сибирские', 'западно-сибирских', 'западно-сибирскими']
    >>> decline_adjective("многосуставной")[:3]
    ['многосуставной', 'многосуставного', 'многосуставному']
    >>> decline_adjective("короткорогий")[3]
    'короткорогим'
    >>> decline_adjective("наилюбезнейший")[1]
    'наилюбезнейшего'
    >>> decline_adjective("раскисший")[1]
    'раскисшего'
    >>> decline_adjective("росомаший")  # a possessive adjective: "росомашьего"
    ['росомаший']
    >>> decline_adjective("синий")  # "синего", but "шаманий" is "шаманьего"
    ['синий']
    """
    if match := re.fullmatch(r"(.+[бвдзлмнпрстфц])ый", word):
        stem, endings = match[1], ("ый", "ого", "ому", "ым", "ом", "ая", "ой", "ую", "ою", "ое", "ые", "ых", "ыми")
    elif match := re.fullmatch(r"(.+[бвдзлмнпрстфц])ой", word):
        stem, endings = match[1], ("ой", "ого", "ому", "ым", "ом", "ая", "ой", "ую", "ою", "ое", "ые", "ых", "ыми")
    elif match := re.fullmatch(r"(.+[гкхжшчщ])ой|(.+[гкх])ий", word):
        stem = match[1] or match[2]
        endings = (word[-2:], "ого", "ому", "им", "ом", "ая", "ой", "ую", "ою", "ое", "ие", "их", "ими")
    elif re.search(r"(?:[^аеёиоуыэюя]ш|щ)ий(?:ся)?$", word):
        return decline_participle(word, word)
    else:
        return [word]
    return [stem + ending for ending in endings]


def decline_participle(form: str, verb: str) -> list[str]:
    """
    The conjugation tables give the participles only as "раскисший", so their other forms are added.
    Other forms are returned as they are, and so are the ones that do not start like the verb: a table
    with an empty stem gives junk such as "анный".

    >>> decline_participle("раскисший", "раскиснуть")
    ['раскисший', 'раскисшего', 'раскисшему', 'раскисшим', 'раскисшем', 'раскисшая', 'раскисшей', 'раскисшую', 'раскисшею', 'раскисшее', 'раскисшие', 'раскисших', 'раскисшими']
    >>> decline_participle("читающийся", "читаться")[:3]
    ['читающийся', 'читающегося', 'читающемуся']
    >>> decline_participle("решённый", "решить")[-4:]
    ['решён', 'решена', 'решено', 'решены']
    >>> decline_participle("раскрытый", "раскрыть")[-4:]
    ['раскрыт', 'раскрыта', 'раскрыто', 'раскрыты']
    >>> decline_participle("читаемый", "читать")[-4:]
    ['читаем', 'читаема', 'читаемо', 'читаемы']
    >>> decline_participle("раскис", "раскиснуть")
    ['раскис']
    >>> decline_participle("анный", "метафоризировать")
    ['анный']
    """
    if form[:1].lower() != verb[:1].lower():
        return [form]
    if match := re.fullmatch(r"(.+[шщ])ий(ся)?", form):
        stem, reflexive = match[1], match[2] or ""
        endings = ("ий", "его", "ему", "им", "ем", "ая", "ей", "ую", "ею", "ее", "ие", "их", "ими")
        return [stem + ending + reflexive for ending in endings]
    if match := re.fullmatch(r"(.+(?:нн|т|м))ый", form):
        stem = match[1]
        endings = ("ый", "ого", "ому", "ым", "ом", "ая", "ой", "ую", "ою", "ое", "ые", "ых", "ыми")
        # Short forms: "прочитан", "решён" and "решена" (the stress moves to the ending)
        short = stem.removesuffix("н") if stem.endswith("нн") else stem
        rest = short[:-2] + short[-2:].replace("ё", "е")
        return [stem + ending for ending in endings] + [short, rest + "а", rest + "о", rest + "ы"]
    return [form]


def extract_templates(templates: str) -> list[str]:
    r"""
    >>> extract_templates("{{сущ ru f ina 1a\n|основа=фо̀сфорибозѝл-аминоимидазо̀л-сукцинокарбоксамѝд-синта́з\n|слоги={{по-слогам|фос|фо|ри|бо|зил|-|а|.|ми|но|и|ми|да|зол-}}{{по-слогам|сук|ци|но|кар|бо|кса|мид|-|син|та́|за}}\n}}")
    ['{{сущ ru f ina 1a\n|основа=фо̀сфорибозѝл-аминоимидазо̀л-сукцинокарбоксамѝд-синта́з\n|слоги={{по-слогам|фос|фо|ри|бо|зил|-|а|.|ми|но|и|ми|да|зол-}}{{по-слогам|сук|ци|но|кар|бо|кса|мид|-|син|та́|за}}\n}}']
    >>> extract_templates("{{сущ ru m a 4a|...}} {{собств.|ru|тип=отчество}}")
    ['{{сущ ru m a 4a|...}}', ' {{собств.|ru|тип=отчество}}']
    """
    res: list[str] = []

    current_template = ""
    for char in list(templates):
        current_template += char
        if char != "}" or len(current_template) <= 4 or current_template.count("{") != current_template.count("}"):
            continue
        res.append(current_template)
        current_template = ""

    return res
