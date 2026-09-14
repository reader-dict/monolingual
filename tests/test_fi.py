from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = __name__.split("_", 1)[1]


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "a",
            ["/ˈɑ/", "/ɑ/"],
            [],
            {
                "Lyhenne": [
                    "atto, SI-järjestelmän etuliite, triljoonasosa, 10<sup>−18</sup>",
                    "vuoden tunnus SI-järjestelmässä",
                    "aarin tunnus",
                    "(<i>musiikki, sormintasoittimet</i>) espanjan <i>anular,</i> nimetön (sormi)",
                    "<i>approbatur</i> (hyväksytään)",
                    "(<i>slangia</i>) amfetamiini",
                    "(<i>musiikki, C-duuriasteikossa</i>) 6. juurisävel",
                    "(<i>musiikki, A-molliasteikossa</i>) 1. juurisävel",
                    "(<i>musiikki, sävellajista</i>) a-molli",
                ],
                "Idiomit": ["<b>Kaiken a ja o</b>", ("tärkein, keskeisin asia, alku ja loppu, alfa ja oomega",)],
            },
            [],
            [],
        ),
        (
            "karjalanpaisti",
            ["/ˈkɑrjɑˌlɑnpɑi̯st̪i/"],
            ["yhdyssana osista <i>Karjala</i> (genetiivi) ja <i>paisti</i>"],
            {"Substantiivi": ["suomalainen perinneruoka, johon kuuluu pitkään kypsytettyä lihaa kuutioina"]},
            [],
            [],
        ),
        (
            "kreppi",
            ["/ˈkrepːi/"],
            [],
            {
                "Substantiivi": [
                    "kreppikangas",
                    "kreppipaperi",
                    "(<i>ruoka</i>) hyvin ohut lettu tai räiskäle us. rullalle käärittynä",
                ]
            },
            [],
            [
                "krepeiksi",
                "krepeille",
                "krepeillä",
                "krepeiltä",
                "krepein",
                "krepeissä",
                "krepeistä",
                "krepeittä",
                "krepiksi",
                "krepille",
                "krepillä",
                "krepiltä",
                "krepin",
                "krepissä",
                "krepistä",
                "krepit",
                "krepittä",
                "kreppeihin",
                "kreppein",
                "kreppeineen",
                "kreppeinä",
                "kreppejä",
                "kreppien",
                "kreppiin",
                "kreppinä",
                "kreppiä",
            ],
        ),
        (
            "marssia",
            ["/ˈmɑrsːiɑˣ/"],
            [],
            {
                "Verbi": [
                    "kävellä marssimusiikin tahdissa",
                    "osallistua marssille",
                    "(<i>kuvaannollisesti</i>) tulla esille näyttävästi (varsinkin mielenosoituksellisesti)",
                ],
            },
            ["marssi"],
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    reverse_variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    print(f"{word = }")
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert OrderedDict(definitions) == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
