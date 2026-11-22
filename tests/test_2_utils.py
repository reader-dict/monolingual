import re
from pathlib import Path
from unittest.mock import patch

import pytest

from wikidict import context, utils


def test_formula_to_svg() -> None:
    assert utils.formula_to_svg("C10H14N2O4", cat="chem").startswith("<svg")

    formula = r"x_1 + \frac{a}{b}"
    with patch.dict("wikidict.svg.CACHE", clear=True):
        svg = utils.formula_to_svg(formula)
        # Sizes in em, the baseline of the formula on the one of the text
        assert re.match(r'<svg width="[\d.]+em" height="[\d.]+em" style="vertical-align:-[\d.]+em"', svg)
        assert 'fill="currentColor"' in svg
        assert "<symbol" not in svg
        assert formula in utils.svg.CACHE

        with patch.dict("os.environ", {"FORCE_FORMULA_RENDERING": "1"}):
            assert utils.formula_to_svg(formula) == svg


def test_convert_chem_error(caplog: pytest.LogCaptureFixture) -> None:
    assert utils.convert_chem("bad formula", "word") == "bad formula"
    assert caplog.records[0].getMessage() == "<chem> ERROR with 'bad formula' in [word]"


def test_convert_math_error(caplog: pytest.LogCaptureFixture) -> None:
    assert utils.convert_math("x^", "word") == "x^"
    assert caplog.records[0].getMessage() == "<math> ERROR with 'x^' in [word]"


def test_process_template_continue_on_error() -> None:
    """
    Given a word with 2 definitions: the first one will end on a Lua error, the second is correct;
    then we should keep the second definition, and report the error of the first.
    """
    templates_status: list[tuple[str, str]] = []

    with patch.dict("os.environ", {"CWD": str(Path(context.__file__).parent.parent)}):
        assert context.reset("en")
        context.new_word("ab")

        # Error: unknown template
        assert not utils.process_templates("foo", "{{unknown|arg1}}", "en", templates_status=templates_status)
        assert templates_status == [("foo", "skipped")]

        # Definition is OK, then we want to keep it
        assert (
            utils.process_templates("foo", "{{lb|mul|taxonomy}}", "en", templates_status=templates_status)
            == "(<i>taxonomy</i>)"
        )
        assert templates_status == [("foo", "skipped")]
