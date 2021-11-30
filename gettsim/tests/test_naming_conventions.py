# from gettsim.config import GEP_01_CHARACTER_LIMIT_INTERNAL
from gettsim.config import GEP_01_CHARACTER_LIMIT_USER_FACING
from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.functions_loader import _load_functions


def test_length_of_variable_names():
    functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    over_limit = [
        f"{name:40} ({len(name)})"
        for name in functions
        if len(name) >= GEP_01_CHARACTER_LIMIT_USER_FACING
    ]
    assert not over_limit, "\n\n" + "\n".join(sorted(over_limit)) + "\n\n"
