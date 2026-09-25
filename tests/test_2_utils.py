from pathlib import Path
from unittest.mock import patch

import pytest
import responses

from wikidict import constants, context, utils


@responses.activate
def test_formula_to_svg(caplog: pytest.LogCaptureFixture) -> None:
    formula_hash = "1b3c657d9bf9ae776f50d0b36ae0b1041abfe45d"

    responses.add(
        responses.POST,
        constants.WIKIMEDIA_URL_MATH_CHECK.format(type="chem"),
        headers={"x-resource-location": formula_hash},
        json={
            "success": True,
            "checked": "{\\ce {C10H14N2O4}}",
            "requiredPackages": ["mhchem"],
            "identifiers": [],
            "endsWithDot": False,
        },
    )
    responses.add(
        responses.GET,
        constants.WIKIMEDIA_URL_MATH_RENDER.format(format="svg", hash=formula_hash),
        body="<svg></svg>",
    )

    assert utils.formula_to_svg("C10H14N2O4", cat="chem").startswith("<svg")

    with patch.dict("os.environ", {"FORCE_FORMULA_RENDERING": "1"}):
        assert utils.formula_to_svg("C10H14N2O4", cat="chem").startswith("<svg")


@responses.activate
def test_convert_chem_error(caplog: pytest.LogCaptureFixture) -> None:
    responses.add(responses.POST, constants.WIKIMEDIA_URL_MATH_CHECK.format(type="chem"), status=404)
    utils.convert_chem("bad formula", "word")
    assert caplog.records[0].getMessage() == "<chem> ERROR with 'bad formula' in [word]"


@responses.activate
def test_convert_math_error(caplog: pytest.LogCaptureFixture) -> None:
    responses.add(responses.POST, constants.WIKIMEDIA_URL_MATH_CHECK.format(type="math"), status=404)
    utils.convert_math("bad formula", "word")
    assert caplog.records[0].getMessage() == "<math> ERROR with 'bad formula' in [word]"


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
