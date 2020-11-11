# import pytest
# from gettsim.config import GEP_1_CHARACTER_LIMIT
# from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
# from gettsim.functions_loader import _load_functions
# @pytest.mark.xfail
# def test_length_of_variable_names():
#     functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
#     over_limit = [name for name in functions if len(name) >= GEP_1_CHARACTER_LIMIT]
#     assert not over_limit
