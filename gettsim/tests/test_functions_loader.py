from gettsim.config import ROOT_DIR
from gettsim.functions_loader import load_functions


def func():
    pass


def test_load_function():
    assert load_functions(func) == {"func": func}


def test_renaming_functions():
    out = load_functions([func, {"func_": func}])
    assert len(out) == 2
    assert "func" in out and "func_" in out


def test_load_path():
    assert load_functions(ROOT_DIR / "soz_vers" / "krankenv_pflegev.py")
