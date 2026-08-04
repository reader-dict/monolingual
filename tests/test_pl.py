import re
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "pl"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "a",
            ["[a]"],
            [
                "<i>majuskuła:</i> A &lt; łac. &lt; <i>etruski</i> &lt; gr. Α, α &lt; fen. &lt; <i>protosynajski</i> &lt; <i>egipski</i>",
                "franc. are z łac. area",
                "W polszczyźnie od XIII wieku; ogsłow. (por. czes. a 'i', rzadziej 'a', ros. а 'a, ale, lecz, i', serb.-chorw. a 'a, i', scs. a 'a, ale, i, chociaż, jakkolwiek') z prasł. *a – partykuła wzmacniająca i nawiązująca, prapokrewne z litew. õ 'i, a' oraz stind. ât 'potem, i, tak'.",
            ],
            {
                "Litera": [
                    "pierwsza litera podstawowego współczesnego alfabetu łacińskiego; zob. <i>też</i> a w Wikipedii"
                ],
                "Symbol": [
                    "fonet. (<i>w IPA</i>) samogłoska otwarta przednia niezaokrąglona",
                    "fiz. jedn. miar. symbol jednostki powierzchni, ara, równego 100\xa0m², czyli setnej części hektara",
                    '<svg width="1.23ex" height="2.343ex" style="vertical-align:-0.338ex" aria-labelledby="MathJax-SVG-1-Title" focusable="false" role="img" viewBox="0 -863.1 529.5 1008.6" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><defs aria-hidden="true"><path id="E1-MJMATHI-61" d="m33 157q0 101 76 192t171 92q51 0 90-49 16 30 46 30 13 0 23-8t10-20q0-13-37-160t-38-166q0-25 7-33t21-9q9 1 20 9 21 20 41 96 6 20 10 21 2 1 10 1h4q19 0 19-9 0-6-5-27t-20-54-32-50q-13-13-32-21-8-2-24-2-34 0-57 15t-30 31l-6 15q-1 1-4-1-2-2-4-4-59-56-120-56-55 0-97 40t-42 127zm318 171q0 6-5 22t-23 35-46 20q-35 0-67-31t-50-81q-29-79-41-164 0-3 0-11t-1-12q0-45 18-62t43-18q38 0 75 33t44 51q2 4 27 107t26 111z"/><path id="E1-MJMAIN-20D7" d="m-123 694q0 8 5 14t15 6q10 0 15-8t8-19 13-27 27-27q11-7 11-18 0-9-7-15t-17-10-30-19-38-40q-14-15-22-15t-14 6-6 14 11 23 23 25 13 11h-171l-171 1q-1 1-3 3t-5 3-3 5-2 8q0 7 13 20h359q-24 38-24 59z"/></defs><g transform="scale(1 -1)" fill="currentColor" stroke="currentColor" stroke-width="0" aria-hidden="true"><use xlink:href="#E1-MJMATHI-61"/><use x="499" y="34" xlink:href="#E1-MJMAIN-20D7"/></g></svg> fiz. symbol oznaczający wektor przyspieszenia',
                    "muz. szósty dźwięk w podstawowej skali diatonicznej; zob. <i>też</i> a (dźwięk) w Wikipedii",
                ],
                "Synonimy": ["i, oraz", "ale, natomiast, zaś", "więc", "przy czym", "o!"],
                "Spójnik": [
                    "<i>…uzupełniania</i>",
                    "<i>…przeciwstawności</i>",
                    "<i>…wynikania</i>",
                    "<i>…objaśnień</i>",
                ],
                "Partykuła": ["<i>…wzmacniająca</i>"],
                "Wykrzyknik": ["<i>wyraz zaskoczenia, zdziwienia</i>"],
                "Rzeczownik|n.": ["jęz. pierwsza litera polskiego alfabetu; zob. <i>też</i> a w Wikipedii"],
            },
            [],
            [],
        ),
        (
            "ABC",
            ["[a‿bɛ‿ˈt͡sɛ]"],
            ["pol. A + B + C; od pierwszych liter alfabetu"],
            {
                "Rzeczownik|n.": [
                    "podstawy czegoś, podstawy wiedzy na jakiś temat",
                    "podręcznik, w którym można znaleźć podstawy czegoś, najważniejsze informacje z danej dziedziny",
                    "zestaw podstawowych narzędzi, akcesoriów do jakiejś pracy lub dziedziny aktywności",
                ],
                "Skrótowiec": [
                    "geogr. pot. Aruba, Bonaire i Curaçao, grupa wysp na Morzu Karaibskim; zob. <i>też</i> wyspy ABC w Wikipedii"
                ],
                "Synonimy": ["abc, a b c"],
            },
            [],
            [],
        ),
        (
            "-centryzm",
            ["[ˈt͡sɛ̃ntrɨsm̥]"],
            [],
            {},
            [],
            [
                "-centryzmach",
                "-centryzmami",
                "-centryzmem",
                "-centryzmie",
                "-centryzmom",
                "-centryzmowi",
                "-centryzmu",
                "-centryzmy",
                "-centryzmów",
            ],
        ),
        (
            "książka",
            ["[ˈcɕɔ̃w̃ʃka]"],
            [
                "prasł. *kъnigy, zdrobnienie od prasł. *kъnъ – kloc drewna; por. knieja; do XVI wieku tylko w liczbie mnogiej"
            ],
            {
                "Rzeczownik|ż.": [
                    "bibliot. dokument piśmienniczy w postaci publikacji wielostronicowej o określonej liczbie stron, o charakterze trwałym; zob. <i>też</i> książka w Wikipedii",
                    "treść książki (1.1) (np. powieść)",
                    "oprawiony plik arkuszy papieru przeznaczony do zapisków",
                    "karc. <i>brydż</i> sytuacja kiedy rozgrywający oddali już maksymalną dopuszczalną liczbę lew i oddanie kolejnej spowodowałoby nieugranie kontraktu",
                ],
                "Synonimy": ["wolumin, pozycja, księga", "pozycja, księga"],
            },
            [],
            ["książce", "książek", "książkach", "książkami", "książki", "książko", "książkom", "książką", "książkę"],
        ),
        (
            "piękny",
            ["[ˈpʲjɛ̃ŋknɨ]"],
            [],
            {
                "Przymiotnik": ["taki, którego cechuje piękno: bardzo ładny, wzbudzający zachwyt"],
                "Synonimy": [
                    "ładny, atrakcyjny, wspaniały, śliczny, boski, uroczy, reg. śl. piekny, reg. śl. pyszny, reg. śl. szumny"
                ],
            },
            [],
            [
                "najpiękniejsi",
                "najpiękniejsza",
                "najpiękniejsze",
                "najpiękniejszego",
                "najpiękniejszej",
                "najpiękniejszemu",
                "najpiękniejszy",
                "najpiękniejszych",
                "najpiękniejszym",
                "najpiękniejszymi",
                "najpiękniejszą",
                "piękna",
                "piękne",
                "pięknego",
                "pięknej",
                "pięknemu",
                "piękni",
                "piękniejsi",
                "piękniejsza",
                "piękniejsze",
                "piękniejszego",
                "piękniejszej",
                "piękniejszemu",
                "piękniejszy",
                "piękniejszych",
                "piękniejszym",
                "piękniejszymi",
                "piękniejszą",
                "pięknych",
                "pięknym",
                "pięknymi",
                "piękną",
            ],
        ),
        (
            "planeta",
            ["[plãˈnɛta]"],
            ["łac. planeta &lt; gr. πλανάω (planáō) → wędruję"],
            {
                "Rzeczownik|ż.": [
                    "astr. ciało niebieskie o znacznej masie nie emitujące światła i zazwyczaj okrążające macierzystą gwiazdę; zob. <i>też</i> planeta w Wikipedii",
                    "więz. dziewczyna",
                ]
            },
            [],
            ["planecie", "planet", "planetach", "planetami", "planeto", "planetom", "planety", "planetą", "planetę"],
        ),
        (
            "rozpowszechniony",
            [],
            [],
            {
                "Przymiotnik": ["występujący powszechnie, często, na dużą skalę"],
                "Odmiana": ["zob. rozpowszechnić"],
            },
            ["rozpowszechnić"],
            [
                "najrozpowszechnieni",
                "najrozpowszechniona",
                "najrozpowszechnione",
                "najrozpowszechnionego",
                "najrozpowszechnionej",
                "najrozpowszechnionemu",
                "najrozpowszechniony",
                "najrozpowszechnionych",
                "najrozpowszechnionym",
                "najrozpowszechnionymi",
                "najrozpowszechnioną",
                "rozpowszechnieni",
                "rozpowszechniona",
                "rozpowszechnione",
                "rozpowszechnionego",
                "rozpowszechnionej",
                "rozpowszechnionemu",
                "rozpowszechnionych",
                "rozpowszechnionym",
                "rozpowszechnionymi",
                "rozpowszechnioną",
            ],
        ),
        (
            "rozpowszechnić",
            [],
            [],
            {
                "Czasownik": [
                    "uczynić coś powszechnie znanym",
                    "stać się znanym lub używanym powszechnie",
                    "wystąpić często lub w dużej liczbie",
                ]
            },
            [],
            [
                "rozpowszechni",
                "rozpowszechnicie",
                "rozpowszechnij",
                "rozpowszechnijcie",
                "rozpowszechnijmy",
                "rozpowszechnili",
                "rozpowszechniliście",
                "rozpowszechniliśmy",
                "rozpowszechnimy",
                "rozpowszechnisz",
                "rozpowszechnią",
                "rozpowszechnię",
                "rozpowszechnił",
                "rozpowszechniła",
                "rozpowszechniłam",
                "rozpowszechniłaś",
                "rozpowszechniłem",
                "rozpowszechniłeś",
                "rozpowszechniło",
                "rozpowszechniłom",
                "rozpowszechniłoś",
            ],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    code = page(word, LANG)

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    # `== piękny ({{język polski}}) ==` → `==polski==`
    code = re.sub(r"^==[ ]*.*\(\{\{język ([^}]+)\}\}\)[ ]*==", r"==\1==", code, flags=re.MULTILINE)
    # `== a ({{użycie międzynarodowe}}) ==` → `==międzynarodowe==`
    code = re.sub(r"^==[ ]*.*\(\{\{użycie ([^}]+)\}\}\)[ ]*==", r"==\1==", code, flags=re.MULTILINE)

    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
