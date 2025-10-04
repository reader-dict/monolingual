from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context
from wikidict.render import parse_word
from wikidict.stubs import Definitions


@pytest.fixture(scope="module", autouse=True)
def setup_lua_ctx() -> None:
    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("el")


@pytest.mark.parametrize(
    "word, pronunciations, genders, etymology, definitions, variants",
    [
        (
            "ανα-",
            ["/a.na/"],
            [],
            [],
            {
                "Πρόθημα": [
                    "που δηλώνει τόπο, κατεύθυνση προς τα πάνω, ή ανώτερο στάδιο ιεραρχικά ή τοπικά",
                    "<i>επιτατικό</i>",
                    "με υποκοριστική σημασία",
                    "που δηλώνει επανάληψη (ξανα-, επαν-)",
                    "(<i>στερητικό</i>) <i>άλλη μορφή του </i><b>α-</b>",
                ]
            },
            [],
        ),
        (
            "-ης",
            [],
            [],
            [
                "<b>-ης</b> &lt; <i>αρχαία ελληνική</i> -ης",
                "<b>-ης</b> &lt; (<i>ελληνιστική κοινή</i>) -ις &lt; <i>αρχαία ελληνική</i> -(ε)ιος (<i>αρχαία ελληνική</i> κύριος, <i><b>αιτιατική</b></i> τόν κύριον &gt; (<i>ελληνιστική κοινή</i>) τόν κῦριν →ὁ κῦρις &gt; μεσαιωνική ελληνική κύρης &gt; <i>νέα ελληνική</i> νοικοκύρης)",
                "<b>-ης</b> &lt; μεσαιωνική ελληνική <b>-ης</b>",
                "<b>-ης</b> &lt; <i>αρχαία ελληνική</i> <b>-ης, -ης, -ες</b> & <b>-ής, -ής, -ές</b>",
                "<b>-ης</b> &lt; (<i>ελληνιστική κοινή</i>) <b>-ῆς</b> (γενική ενικού θηλυκών: κατά γ<b>ῆς</b>)",
                "<b>-ης</b> &lt; τουρκική <b>-i</b> (fıstık &gt; fıstık<b>i</b>)",
            ],
            {"Επίθημα": ["επίθημα τρικατάληκτων τριγενών επιθέτων (-<b>ής</b>, -<b>ιά</b>, -<b>ί</b>)"]},
            [],
        ),
        (
            "επίπεδο",
            ["/eˈpi.pe.ðo/"],
            ["ουδέτερο"],
            [
                "<b>επίπεδο</b>, <i>ουδέτερο του</i> <b>επίπεδος</b> &lt; (διαχρονικό&nbsp;δάνειο) αρχαία ελληνική ἐπίπεδον",
            ],
            {
                "Ουσιαστικό": [
                    "(<i>γεωμετρία</i>) η λεία ομοιόμορφη γεωμετρική επιφάνεια η οποία μπορεί να εφαρμόσει πλήρως με τον εαυτό της ακόμα και εν κινήσει",
                    "η στάθμη",
                    "το ύψος όπου βρίσκεται κάτι σε μια ιεραρχική κλίμακα",
                    "(<i>μεταφορικά</i>) η σπουδαιότητα, η σημαντικότητα",
                ]
            },
            ["επίπεδος"],
        ),
        (
            "λαμβάνω",
            ["/laɱˈva.no/"],
            [],
            [
                "<b>λαμβάνω</b> &lt; (διαχρονικό&nbsp;δάνειο) αρχαία ελληνική λαμβάνω &lt; πρωτοϊνδοευρωπαϊκή *<i>sleh₂gʷ</i>-",
            ],
            {
                "Ρήμα": [
                    "παίρνω, δέχομαι",
                    "εντοπίζω επιθυμητό σήμα (όπως από ασύρματο)",
                    "(<i>μεταφορικά</i>) καταλαβαίνω",
                ]
            },
            [],
        ),
        (
            "τσιγγάνα",
            [],
            ["θηλυκό"],
            [],
            {},
            ["τσιγγάνος"],
        ),
        (
            "-αίικο",
            ["/ˈe.i.ko/"],
            ["ουδέτερο"],
            [
                "<b>-αίικο</b> &lt; <i>ουσιαστικοποιημένο ουδέτερο</i> <i>του επιθέτου</i>&nbsp;-αίικος επίθημα σε επίθετα ή οικογενειακά επώνυμα -αί(οι) + -ικος"
            ],
            {
                "Επίθημα": [
                    "(<i>λαϊκότροπο</i>) επίθημα με πρώτο συνθετικό",
                    (
                        "οικογενειακό επώνυμο που δηλώνει",
                        ("την οικογένεια ή το σπίτι", "τη συνοικία ή τον τόπο όπου κατοικεί η οικογένεια"),
                        "(<i>περιληπτικό</i>) πατριδωνυμικό ή εθνικό όνομα",
                    ),
                ]
            },
            [],
        ),
    ],
)
def test_parse_word(
    word: str,
    pronunciations: list[str],
    genders: list[str],
    etymology: list[Definitions],
    definitions: list[Definitions],
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    print(f"{word = }")
    code = page(word, "el")
    details = parse_word(word, code, "el", force=True)
    assert pronunciations == details.pronunciations
    assert genders == details.genders
    assert definitions == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants
