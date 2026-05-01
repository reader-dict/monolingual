import re
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.lang.da.langs import langs as langs_da
from wikidict.lang.da.variant_handlers import table_to_forms
from wikidict.render import parse_word
from wikidict.stubs import Definitions


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("da")


@pytest.mark.parametrize(
    "word, pronunciations, etymology, definitions, variants, reverse_variants",
    [
        (
            "▶",
            [],
            [],
            {"Symbol": ["knap som bruges til at afspille en video, lyd el. musik"]},
            [],
            [],
        ),
        (
            "bakterie",
            [],
            [
                "fra latin <i>bacterium</i>, latinisering af græsk <i>bakterion</i> (βακτήριον\xa0- lille stav), diminutiv af <i>baktron</i> (βάκτρον - stav)"
            ],
            {
                "Substantiv": ["(mikrobiologi) en encellet mikroskopisk organisme uden cellekerne"],
                "Synonymer": ["bacille (ældre sprogbrug)"],
            },
            [],
            ["bakterien", "bakterier", "bakterierne"],
        ),
        (
            "disse",
            [],
            [],
            {"Substantiv": ["ikke noget"]},
            ["denne"],
            [],
        ),
        (
            "et",
            [],
            [],
            {"Artikel": ["intetkøn af en"]},
            [],
            [],
        ),
        (
            "her",
            ["/hɛːˀɒ̯/"],
            [],
            {
                "Adverbium": [
                    "Stedet hvor vi er nu. Vores placering.",
                    "(<i>radiokommunikation, radiotelefoni</i>) Dette opkalder stammer fra denne opkalder",
                ],
                "Formelt Subjekt": [
                    "bruges som upersonligt subjekt, refererer ofte fremad eller tilbage til et andet led i sætningen."
                ],
                "Synonymer": ["her er"],
            },
            [],
            [],
        ),
        (
            "hund",
            ["[ˈhunə-]", "[ˈhunˀ]"],
            [
                "Menes at stamme fra indoeuropæisk sprog <i>ḱʷn̥tós</i>, fra <i>ḱwṓ</i> og derfra videre til germansk sprog <i>*hundaz</i> og fra oldnordisk hundr."
            ],
            {
                "Decl": ["I sammensætninger er formen <i>hunde-</i> f.eks. <i>hundehus</i>, <i>hundeliv</i>."],
                "Substantiv": [
                    "(<i>zoologi</i>): et pattedyr af underarten <i>Canis lupus familiaris</i>.",
                    "(<i>slang</i>): 100 DKK-seddel (bruges ikke i flertal)",
                ],
            },
            [],
            ["hunde", "hunden", "hundene", "hundenes", "hundens", "hundes", "hunds"],
        ),
        (
            "godt nytår",
            [],
            [],
            {"Sætning": ["En hilsen der siges omkring den 1. januar."]},
            [],
            [],
        ),
        ("jørme", [], [], {"Verbum": ["vrimle, myldre; sværme"]}, ["vørme"], []),
        (
            "mus",
            [],
            [
                "Fra oldnordisk mús.",
                "Fra engelsk mouse.",
            ],
            {"Substantiv": ["(<i>zoologi</i>) pattedyr", "(<i>data</i>) en enhed som tilsluttes computere"]},
            [],
            ["mus'", "musen", "musene", "musenes", "musens"],
        ),
        (
            "-ør",
            [],
            ["Fra fransk: -eur, af latin -ator."],
            {"Endelse": ["Betegner den, der udfører et arbejde."]},
            [],
            [],
        ),
        (
            "skulle",
            [],
            [],
            {"Verbum": ["Er nødt til at gøre. Forpligtet til at gøre."], "Synonymer": ["måtte", "burde"]},
            [],
            ["skal", "skullet"],
        ),
        (
            "søm",
            [],
            ["Fra oldnordisk saumr, fra sýja (<i>at sy</i>).", "Fra oldnordisk saumr <i>hankøn</i>."],
            {
                "Substantiv": [
                    "sammensyning",
                    "spids metalpind med et hoved, beregnet til at sammenføje træstykker til hinanden",
                ]
            },
            [],
            ["sømme", "sømmen", "sømmene", "sømmenes", "sømmens", "sømmes", "sømmet", "sømmets", "søms"],
        ),
        (
            "til",
            [],
            [
                'Indoeuropæisk: *ad (i betydningen: fastsætte, ordne) -> germansk *tila- (i betydningen: mål; jf. tysk: Ziel) -> oldnordisk til. Ordet betyder altså egentlig: "<i>med</i> xxx <i>som mål</i>", hvor xxx kan erstattes af et substantiv (navneord).'
            ],
            {"Præposition": ["Ordet betegner en retning hen imod eller et tilhørsforhold"]},
            [],
            [],
        ),
        (
            "tolvte",
            ["/ˈtɔldə/"],
            ["Fra oldnordisk tolfti."],
            {"Ordenstal": ["nummer tolv i rækken"]},
            [],
            [],
        ),
        (
            "tyv",
            [],
            [],
            {
                "Substantiv": ["En person, der uretmæssigt tager andre folks ejendele i besiddelse."],
                "Udtryk": [
                    "(når noget bliver gjort uden at nogen får det at vide før det er for sent): Som en <b>tyv</b> om natten."
                ],
            },
            [],
            ["tyve", "tyven", "tyvene"],
        ),
        (
            "PMV",
            [],
            [],
            {"Substantiv": ["(<i>militær</i>) <i>Forkortelse af</i> <b>pansret mandskabsvogn</b>"]},
            [],
            [],
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
    code = page(word, "da")

    # Needs specific transformations before hand (they are done in --parse & --get-word, but this is not a taken path by the test)
    # `{{=da=}}` → `=={{da}}==`
    code = re.sub(r"\{\{=(\w+)=\}\}", r"=={{\1}}==", code, flags=re.MULTILINE)
    # Transform sub-locales into their own section to prevent mixing stuff
    # `{{-da-}}` → `=={{da}}==`
    # `{{-mul-}}` → `=={{mul}}==`
    code = re.sub(rf"\{{\{{-({'|'.join(langs_da)})-\}}\}}", r"=={{\1}}==", code, flags=re.MULTILINE)

    details = parse_word(word, code, "da", force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert etymology == details.etymology
    assert definitions == details.definitions
    assert variants == details.variants
    assert reverse_variants == details.reverse_variants


@pytest.mark.parametrize(
    "word, wikitext, forms",
    [
        (
            "baskyle",
            """{| border=0 \n|-\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;ubestemt<br>\nen&nbsp;<b>[[bakterie]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;bestemt<br>\n<b>[[bakterien#Dansk|bakterien]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;ubestemt<br>\n<b>[[bakterier#Dansk|bakterier]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;bestemt<br>\n<b>[[bakterierne#Dansk|bakterierne]]</b>\n|}\n|}""",
            ["bakterie", "bakterien", "bakterier", "bakterierne"],
        ),
        (
            "hund",
            """&nbsp; &nbsp; Bøjning af „hund“\n\n{| class="inflection-table" style="text-align:center;width:100%;"\n|- style="background-color:#eee;"\n! rowspan="2" style="width:25%;" | fælleskøn\n! colspan="2" | \'\'Ental\'\'\n! colspan="2" | \'\'Flertal\'\'\n|- style="font-size:90%;background-color:#eee;"\n! \'\'ubestemt\'\' || \'\'bestemt\'\' || \'\'ubestemt\'\' || \'\'bestemt\'\'\n|-\n! style="background-color:#eee;" | \'\'[[nominativ]]\'\', \'\'[[dativ]]\'\' og \'\'[[akkusativ]]\'\'\n| style="background-color:#f9f9f9;"| [[hund]]\n| style="background-color:#f9f9f9;"| [[hunden]]\n| style="background-color:#f9f9f9;"| [[hunde]]\n| style="background-color:#f9f9f9;"| [[hundene]]\n|-\n! style="background-color:#eee;" | \'\'[[genitiv]]\'\'\n| style="background-color:#f9f9f9;"| [[hunds]]\n| style="background-color:#f9f9f9;"| [[hundens]]\n| style="background-color:#f9f9f9;"| [[hundes]]\n| style="background-color:#f9f9f9;"| [[hundenes]]\n|-\n|}""",
            ["hunde", "hunden", "hundene", "hundenes", "hundens", "hundes", "hunds"],
        ),
        (
            "kapitel",
            """{|  style="background-color:#FFFAFA; color: #8B795E; text-align:center; border: 1px solid #EEE9BF; font-size:11px; line-height:14px; font-stretch:extra-expanded;" cellpadding="3" cellspacing="1"\n|- style="background-color:#EEE9BF; "\n! width=70 | Bøjning af \'\'[[kapitel]] \'\'\n! colspan=2 | Ental\n! colspan=2  | Flertal\n|- style="background-color:#EEE9BF; "\n! \'\'\'intetkøn\'\'\'\n! width=65 | Ubestemt\n! width=65 | Bestemt || width=65 | Ubestemt || width=65 | Bestemt\n|- align=center\n!style="background-color:#EEE9BF; " | Nominativ\n| [[]]\n| [[kapitlet]] || [[]]\n| [[kapitlen]]\n|- align=center\n!style="background-color:#EEE9BF; " | Genitiv\n| [[s]]\n| [[kapitlets]] || [[s]]\n| [[kapitlens]]\n|}""",
            ["kapitels", "kapitlen", "kapitlens", "kapitlet", "kapitlets"],
        ),
        (
            "hond",
            """{| class="prettytable" style="margin-left: 15px;"\n|- style="text-align:center;"\n|width=30px| \'\'\'Bøjning\'\'\'\n|width=80px colspan="2"| Ental\n|width=80px colspan="2"| Flertal\n|- style="text-align:center;"\n|width=30px|\n|bgcolor="#ffffff"| Ubestemt\n|bgcolor="#efefef"| Bestemt\n|bgcolor="#ffffff"| Ubestemt\n|bgcolor="#efefef"| Bestemt\n|- style="text-align:center;"\n| Nominativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondin\n|bgcolor="#ffffff"| hendur\n|bgcolor="#efefef"| hendurnar\n|- style="text-align:center;"\n| Akkusativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondina\n|bgcolor="#ffffff"| hendur\n|bgcolor="#efefef"| hendurnar\n|- style="text-align:center;"\n| Dativ\n|bgcolor="#ffffff"| hond\n|bgcolor="#efefef"| hondini\n|bgcolor="#ffffff"| hondum\n|bgcolor="#efefef"| hondunum\n|- style="text-align:center;"\n| Genitiv\n|bgcolor="#ffffff"| handar\n|bgcolor="#efefef"| handarinnar\n|bgcolor="#ffffff"| handa \n|bgcolor="#efefef"| handanna\n|}""",
            [
                "handa",
                "handanna",
                "handar",
                "handarinnar",
                "hendur",
                "hendurnar",
                "hondin",
                "hondina",
                "hondini",
                "hondum",
                "hondunum",
            ],
        ),
        (
            "hond",
            """{| class="wikitable"\n|-\n! Ental !! Flertal !! Diminutiv ental !!Diminutiv flertal\n|- align="center"\n| hond || honde &nbsp;\n| hondjie || hondjies\n|}""",
            ["honde", "hondjie", "hondjies"],
        ),
        (
            "getuige",
            """{| border=0 \n|-\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nBest.  Ental<br>\nde    <b>[[getuige]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nEntal&nbsp;diminutiv<br>\n<b>[[(getuigetje)]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal<br>\n<b>[[getuigen]]</b>\n|}\n| width=1% |\n|bgcolor="#fff3f3" valign=top width=25%|\n{|\nFlertal&nbsp;diminutiv<br>\n<b>[[(getuigetjes)]]</b>\n|}\n|}""",
            ["getuigen", "getuigetje", "getuigetjes"],
        ),
        (
            "pracovat",
            """'''pracovat'''&nbsp;''imperfektiv''&nbsp;(''perfektiv''&nbsp;[[-]])""",
            [],
        ),
        (
            "pracovat",
            """Konjugation af \'\'\'pracovat\'\'\'</small>\n\n{| class="wikitable inflection-table" style="text-indent:4px"\n! Person\n! Præsens\n! Præteritum\n! Futurum\n! Konditionalis\n! Imperativ\n|-\n! style="text-align:center;" |\'\'já\'\'\n|pracuju,<br>pracuji (formel) ||pracoval jsem \'\'M\'\'<br>&nbsp;pracovala jsem \'\'F\'\'||budu pracovat ||pracoval bych \'\'M\'\'<br>&nbsp;pracovala bych \'\'F\'\'|| —\n|-\n! style="text-align:center;" |\'\'ty\'\'\n| pracuješ ||pracoval jsi \'\'M\'\'<br>&nbsp;pracovala jsi \'\'F\'\'||budeš pracovat ||pracoval bys \'\'M\'\'<br>&nbsp;pracovala bys \'\'F\'\'||pracuj\n|-\n! style="text-align:center;" |\'\'on\'\'<br>\'\'ona\'\'<br>\'\'ono\'\'\n| pracuje ||pracoval \'\'M\'\'<br>&nbsp;pracovala \'\'F\'\'<br>&nbsp;pracovalo \'\'N\'\' ||bude pracovat || pracoval by \'\'M\'\'<br>&nbsp;pracovala by \'\'F\'\'<br>&nbsp;pracovalo by \'\'N\'\'|| —\n|-\n! style="text-align:center;" |\'\'my\'\'\n| pracujeme ||pracovali jsme \'\'M\'\'<br>&nbsp;pracovaly jsme \'\'F\'\'|| budeme pracovat ||pracovali bychom \'\'M\'\'<br>&nbsp;pracovaly bychom \'\'F\'\'||pracujme\n|-\n! style="text-align:center;" |\'\'vy\'\'\n| pracujete ||pracovali jste \'\'M\'\'<br>&nbsp;pracovaly jste \'\'F\'\'||budete pracovat || pracovali byste \'\'M\'\'<br>&nbsp;pracovaly byste \'\'F\'\'||pracujte\n|-\n! style="text-align:center;" |\'\'oni\'\'<br>\'\'ony\'\'<br>\'\'ony\'\'\n| pracujou,<br>pracují (formel) ||pracovali \'\'M\'\'<br>&nbsp;pracovaly \'\'F\'\'<br>&nbsp;pracovala \'\'N\'\'||budou pracovat ||pracovali by \'\'M levende\'\'<br>&nbsp;pracovaly by \'\'M ikke-levende\'\', \'\'F\'\'<br>&nbsp;pracovala by \'\'N\'\'|| —\n|}""",
            [
                "bude pracovat",
                "budeme pracovat",
                "budete pracovat",
                "budeš pracovat",
                "budou pracovat",
                "budu pracovat",
                "pracuj",
                "pracuje",
                "pracujeme",
                "pracujete",
                "pracuješ",
                "pracuji",
                "pracujme",
                "pracujou",
                "pracujte",
                "pracuju",
                "pracují",
            ],
        ),
    ],
)
def test_table_to_forms(word: str, wikitext: str, forms: list[str]) -> None:
    assert table_to_forms(word, wikitext) == forms
