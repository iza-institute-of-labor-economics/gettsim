import textwrap
from pathlib import Path

import pytest

from gettsim.functions_loader import load_functions


def func():
    pass


def test_load_function():
    assert load_functions(func) == {"func": func}


def test_raise_error_on_duplicated_functions():
    with pytest.raises(ValueError):
        load_functions([func, func])


def test_renaming_functions():
    out = load_functions([func, {"func_": func}])
    assert len(out) == 2
    assert "func" in out and "func_" in out


def test_load_modules():
    assert load_functions("gettsim.soz_vers.krankenv_pflegev")


def test_load_path():
    assert load_functions(Path(__file__, "..", "..", "soz_vers", "krankenv_pflegev.py"))


def test_special_attribute_module_is_set(tmp_path):
    py_file = """
    def func():
        pass
    """
    tmp_path.joinpath("functions.py").write_text(textwrap.dedent(py_file))

    out = load_functions(tmp_path.joinpath("functions.py"))
    assert isinstance(out, dict)
    assert "func" in out
    assert len(out) == 1
    assert out["func"].__module__ == "functions.py"


def test_special_attribute_module_is_set_for_internal_functions():
    out = load_functions("gettsim.soz_vers.eink_grenzen")
    function = out[list(out)[0]]

    assert function.__module__ == "gettsim.soz_vers.eink_grenzen"
