from __future__ import annotations

import textwrap

from _gettsim.config import RESOURCE_DIR
from _gettsim.functions_loader import _load_functions


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
    out = _load_functions("_gettsim.social_insurance_contributions.eink_grenzen")
    function = out[list(out)[0]]

    assert function.__module__ == "_gettsim.social_insurance_contributions.eink_grenzen"
