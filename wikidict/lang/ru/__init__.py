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
    """
    # https://ru.wiktionary.org/wiki/%D0%A8%D0%B0%D0%B1%D0%BB%D0%BE%D0%BD:%D1%81%D1%83%D1%89-ru
    pattern: re.Pattern[str] = re.compile(rf"\{{сущ.{locale}.[^\}}\n]*?(?:[^\}}\n|]++\|)?([fmnмжс])")
    return utils.unique(
        [
            {
                "f": "ж",
                "m": "м",
                "n": "ср",
            }.get(gender, gender)
            for gender in utils.flatten(pattern.findall(code))
        ]
    )


def find_pronunciations(code: str, locale: str) -> list[str]:
    """
    >>> from ... import context
    >>> _ = context.reset("ru")

    >>> context.new_word("word")
    >>> find_pronunciations("", "ru")
    []

    >>> find_pronunciations("{{transcriptions-ru|страни́ца|страни́цы|Ru-страница.ogg}}", "ru")
    ['[strɐˈnʲit͡sə]']

    >>> context.new_word("кажется")
    >>> find_pronunciations("{{transcription-ru|ка́жется|Ru-кажется.ogg}}", "ru")
    ['[ˈkaʐɨt͡sə]']
    """
    lines: list[str] = []
    for tpl in re.findall(rf"\{{\{{transcriptions?-{locale}[^}}\n]*+}}}}", code):
        new_lines = context.expand(tpl, "ru").splitlines()
        for line in lines:
            if pron := re.search(r"ед\.&nbsp;ч\.&nbsp;&#91;([^&]++)&#93;", line):
                return [f"[{pron[1]}]"]
        lines.extend(new_lines)

    # Nothing found, lets pick the first result
    for line in lines:
        if pron := re.search(r"&#91;([^&]++)&#93;", line):
            return [f"[{pron[1]}]"]

    return []


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
    '= {{-ru-}} =\n{{гл ru 11b/c-ся|}}\n# {{rev-flexion|вейся}}\n# {{rev-flexion|вейтесь}}\n# {{rev-flexion|вилась}}\n# {{rev-flexion|вилось}}\n# {{rev-flexion|вился}}\n# {{rev-flexion|вьюсь}}\n# {{rev-flexion|вьются}}\n# {{rev-flexion|вьёмся}}\n# {{rev-flexion|вьётесь}}\n# {{rev-flexion|вьётся}}\n# {{rev-flexion|вьёшься}}'

    >>> context.new_word("оба")
    >>> adjust_wikicode("= {{-ru-}} =\n{{числ ru оба\n|основа=о́б\n|основа1=об\n|слоги={{по-слогам|о́|.|ба}}\n|тип=собирательное\n}}", "ru", word="оба")
    '= {{-ru-}} =\n{{числ ru оба|}}\n# {{rev-flexion|обе}}\n# {{rev-flexion|обеим}}\n# {{rev-flexion|обеими}}\n# {{rev-flexion|обеих}}\n# {{rev-flexion|обоим}}\n# {{rev-flexion|обоими}}\n# {{rev-flexion|обоих}}'

    >>> context.new_word("бежать")
    >>> adjust_wikicode("= {{-ru-}} =\n{{гл ru 5b-ж\n|основа=беж\n|основа1=бег\n|основа2=бе́г\n|слоги={{по слогам|бе|жа́ть}}\n|дореф=бѣжа́ть\n|2в=1\n|коммент=В некоторых значениях «бежать» может использоваться как глагол совершенного вида, особенно в формах прош. времени: {{пример|преступники {{выдел|бежали}} из тюрьмы}} {{пример|враг {{выдел|бежал}}}} {{пример|он {{выдел|бежал}} городской суеты}} {{пример|суп {{выдел|бежал}}}}. В 3л. мн.ч. употребляется нестандартная форма «''бегу́т''». До XIX также равноправной формой была форма «''бежа́т''» (см. пример).\n|imper-1p=1\n}}", "ru", word="бежать")
    '= {{-ru-}} =\n{{гл ru 5b-ж|}}\n# {{rev-flexion|беганный}}\n# {{rev-flexion|беги}}\n# {{rev-flexion|бегите}}\n# {{rev-flexion|бегу}}\n# {{rev-flexion|бегут}}\n# {{rev-flexion|бегущий}}\n# {{rev-flexion|бежа}}\n# {{rev-flexion|бежав}}\n# {{rev-flexion|бежавший}}\n# {{rev-flexion|бежал}}\n# {{rev-flexion|бежала}}\n# {{rev-flexion|бежали}}\n# {{rev-flexion|бежало}}\n# {{rev-flexion|бежим}}\n# {{rev-flexion|бежимый}}\n# {{rev-flexion|бежит}}\n# {{rev-flexion|бежите}}\n# {{rev-flexion|бежишь}}'

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
    '= {{-ru-}} =\n{{гл ru 5b^-т|}}\n# {{rev-flexion|сидев}}\n# {{rev-flexion|сидевший}}\n# {{rev-flexion|сидел}}\n# {{rev-flexion|сидела}}\n# {{rev-flexion|сидели}}\n# {{rev-flexion|сидело}}\n# {{rev-flexion|сиди}}\n# {{rev-flexion|сидим}}\n# {{rev-flexion|сидимый}}\n# {{rev-flexion|сидит}}\n# {{rev-flexion|сидите}}\n# {{rev-flexion|сидишь}}\n# {{rev-flexion|сидя}}\n# {{rev-flexion|сидят}}\n# {{rev-flexion|сидящий}}\n# {{rev-flexion|сижу}}'

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
                    cleaned.append(f"{{{{{tpl_name}|}}}}")  # This is required for genders finding
                    cleaned.extend(f"# {{{{rev-flexion|{form}}}}}" for form in sorted(forms.split("|")))
                    tpl_code = ""
            else:
                cleaned.append(line)

        code = "\n".join(cleaned)

    return code


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
