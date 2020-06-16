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
