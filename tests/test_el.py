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
    "word, pronunciations, etymology, definitions, variants",
    [
        (
            "ανα-",
            ["/a.na/"],
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
            [
                "<b>επίπεδο</b>, <i>ουδέτερο του</i> <b>επίπεδος</b> &lt; (διαχρονικό&nbsp;δάνειο) αρχαία ελληνική ἐπίπεδον",
            ],
            {
                "Ουσιαστικό|ο.": [
                    "(<i>γεωμετρία</i>) η λεία ομοιόμορφη γεωμετρική επιφάνεια η οποία μπορεί να εφαρμόσει πλήρως με τον εαυτό της ακόμα και εν κινήσει",
                    "η στάθμη",
                    "το ύψος όπου βρίσκεται κάτι σε μια ιεραρχική κλίμακα",
                    "(<i>μεταφορικά</i>) η σπουδαιότητα, η σημαντικότητα",
                ]
            },
            ["επίπεδος"],
        ),
        (
            "ετικέτα",
            ["/e.tiˈce.ta/"],
            [
                "<b>ετικέτα</b> &lt; (άμεσο δάνειο) ιταλική etichetta &lt; γαλλική étiquette &lt; μέση γαλλική estiquette &lt; παλαιά γαλλική estiquette, &lt; φραγκική <big>*</big>stikkan &lt; πρωτογερμανική <big>*</big>stikaną / <big>*</big>stikōną <big>*</big>staikijaną &lt; <i>πρωτοϊνδοευρωπαϊκή ρίζα</i> <big>*</big><i>stig</i>- / <big>*</big>*<i>steyg</i>-",
                "<i>για το πρωτόκολλο συμπεριφοράς</i> &lt; σημασιολογικό δάνειο από τη γαλλική étiquette",
                "<i>για την πληροφορική</i> &lt; σημασιολογικό δάνειο από την αγγλική tag",
            ],
            {
                "Ουσιαστικό|θ.": [
                    "(<i>κυριολεκτικά</i>) μικρό κομμάτι χαρτιού στο οποίο αναγράφονται συνοπτικές πληροφορίες",
                    "(<i>μεταφορικά</i>) στερεότυπος χαρακτηρισμός, η ταμπέλα",
                    "κανόνες καλής συμπεριφοράς",
                    ("&#8776;&nbsp;<i>συνώνυμα</i><i>:</i> πρωτόκολλο, σαβουάρ φερ (savoir faire)",),
                ]
            },
            [],
        ),
        (
            "λαμβάνω",
            ["/laɱˈva.no/"],
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
            [],
            {},
            ["τσιγγάνος"],
        ),
        (
            "-αίικο",
            ["/ˈe.i.ko/"],
            [
                "<b>-αίικο</b> &lt; <i>ουσιαστικοποιημένο ουδέτερο</i> <i>του επιθέτου</i>&nbsp;-αίικος επίθημα σε επίθετα ή οικογενειακά επώνυμα -αί(οι) + -ικος"
            ],
            {
                "Επίθημα|ο.": [
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
    etymology: list[Definitions],
    definitions: Definitions,
    variants: list[str],
    page: Callable[[str, str], str],
) -> None:
    """Test the sections finder and definitions getter."""
    print(f"{word = }")
    code = page(word, LANG)
    details = parse_word(word, code, LANG, force=True)
    assert details
    assert pronunciations == details.pronunciations
    assert OrderedDict(definitions) == details.definitions
    assert etymology == details.etymology
    assert variants == details.variants
