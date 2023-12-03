from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

import pytest
from _gettsim.config import RESOURCE_DIR
from _gettsim.functions_loader import _create_derived_functions, _load_functions

if TYPE_CHECKING:
    from collections.abc import Callable


def func():
    pass


def test_load_function():
    assert _load_functions(func) == {"func": func}


def test_renaming_functions():
    out = _load_functions([func, {"func_": func}])
    assert len(out) == 2
    assert "func" in out
    assert "func_" in out


def test_load_modules():
    assert _load_functions("_gettsim.social_insurance_contributions.ges_krankenv")


def test_load_path():
    assert _load_functions(
        RESOURCE_DIR / "social_insurance_contributions" / "ges_krankenv.py"
    )


def test_special_attribute_module_is_set(tmp_path):
    py_file = """
    def func():
        pass
    """
    tmp_path.joinpath("functions.py").write_text(textwrap.dedent(py_file))

    out = _load_functions(tmp_path.joinpath("functions.py"))
    assert isinstance(out, dict)
    assert "func" in out
    assert len(out) == 1
    assert out["func"].__module__ == "functions.py"


def test_special_attribute_module_is_set_for_internal_functions():
    a_few_functions = _load_functions(
        "_gettsim.social_insurance_contributions.einkommensgrenzen"
    )
    function = next(iter(a_few_functions.values()))
    assert (
        function.__module__
        == "_gettsim.social_insurance_contributions.einkommensgrenzen"
    )


@pytest.mark.parametrize(
    ("functions", "targets"),
    [
        ({"foo_y": lambda: 1}, ["foo_d_hh"]),
        ({"foo_y": lambda: 1}, ["foo_d", "foo_d_hh"]),
    ],
)
def test_create_derived_functions(
    functions: dict[str, Callable], targets: list[str]
) -> None:
    time_conversion_functions, aggregation_functions = _create_derived_functions(
        functions, targets, [], {}
    )
    derived_functions = {**time_conversion_functions, **aggregation_functions}

    for name in targets:
        assert name in derived_functions
