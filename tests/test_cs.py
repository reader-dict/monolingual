from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions

LANG = "cs"


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset(LANG)


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "exemplární",
            ["[ɛgzɛmplaːrɲiː]"],
            [],
            {"Význam": ["příkladný"]},
            [],
            [
                "exemplárních",
                "exemplárního",
                "exemplárním",
                "exemplárními",
                "exemplárnímu",
                "exemplárnější",
                "nejexemplárnější",
            ],
        ),
        (
            "kámen",
            ["[ˈkaː.mɛn]"],
            [],
            {
                "Význam": [
                    "kus horniny",
                    "(<i>hromadné, jen singulár</i>) materiál tvořený kameny (1)",
                    "vzácný nebo dekorativní minerál",
                    "herní figura v deskových hrách, curlingu apod.",
                    "(dříve) stará jednotka hmotnosti",
                    "druh pozdravu, kdy se dva zdravící lidé navzájem dotknou čelní stranou své sevřené pěsti",
                ],
                "Synonyma": [
                    "(v&nbsp;obecném jazyce) šutr, <i>(velký:)</i> balvan, (zdrobněle) kamínek",
                    "kamení, skála, kamenivo",
                    "drahokam, polodrahokam",
                ],
            },
            [],
            ["kamene", "kamenech", "kamenem", "kameni", "kamenu", "kameny", "kameně", "kamenů", "kamenům"],
        ),
        (
            "mela",
            ["[mɛla]"],
            [],
            {"Význam": ["zmatek, vřava, nepřehledná rvačka"]},
            ["mlít"],
            ["mel", "melami", "mele", "melo", "melou", "melu", "mely", "melách", "melám"],
        ),
        ("melo", ["[mɛlɔ]"], [], {}, ["mela"], []),
        (
            "patolízalův",
            ["[patɔliːzaluːf]"],
            ["Odvozeno od podstatného jména patolízal příponou -ův."],
            {"Význam": ["náležící patolízalovi"]},
            [],
            [
                "patolízalova",
                "patolízalovi",
                "patolízalovo",
                "patolízalovou",
                "patolízalovu",
                "patolízalovy",
                "patolízalových",
                "patolízalovým",
                "patolízalovými",
                "patolízalově",
            ],
        ),
        (
            "popření",
            ["[pɔpr̝̊ɛɲiː]"],
            ["Ze slovesa popřít."],
            {
                "Synonyma": ["negace, vyvrácení; ~zapření, ~zamítnutí"],
                "Význam": [
                    "výrok resp. akce, představující nesouhlas s existencí nebo pravdivostí (také účelově, kvůli vlastnímu prospěchu) něčeho; prohlášení něčeho za neplatné, vyvrácení"
                ],
            },
            ["popřený"],
            ["popřeních", "popřením", "popřeními"],
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
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants
