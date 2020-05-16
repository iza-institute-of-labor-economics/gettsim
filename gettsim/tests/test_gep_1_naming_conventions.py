import pytest

from gettsim.config import GEP_1_CHARACTER_LIMIT
from gettsim.config import ROOT_DIR
from gettsim.functions_loader import load_functions


@pytest.mark.xfail
def test_length_of_variable_names():
    sources = [
        ROOT_DIR / "benefits",
        ROOT_DIR / "soz_vers",
        ROOT_DIR / "taxes",
        ROOT_DIR / "renten_anspr.py",
        ROOT_DIR / "verfügb_eink.py",
    ]

    functions = load_functions(sources)

    over_limit = [name for name in functions if len(name) >= GEP_1_CHARACTER_LIMIT]

    assert not over_limit
