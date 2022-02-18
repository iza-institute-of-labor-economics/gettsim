import datetime

import pytest

from gettsim.config import DEFAULT_TARGETS
from gettsim.config import GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS
from gettsim.config import GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS
from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import TYPES_INPUT_VARIABLES
from gettsim.functions_loader import _load_functions
from gettsim.policy_environment import load_reforms_for_date
from gettsim.tests.utils_tests import nice_output_list_of_strings


@pytest.fixture(scope="module")
def default_input_variables():
    return sorted(TYPES_INPUT_VARIABLES.keys())


@pytest.fixture(scope="module")
def all_function_names():
    functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    return sorted(functions.keys())


@pytest.fixture(scope="module")
def time_indep_function_names(all_function_names):
    time_dependent_functions = {}
    for year in range(1990, 2023):
        year_functions = load_reforms_for_date(datetime.date(year=year, month=1, day=1))
        new_dict = {func.__name__: key for key, func in year_functions.items()}
        time_dependent_functions = {**time_dependent_functions, **new_dict}

    # Only use time dependent function names
    time_indep_function_names = [
        (time_dependent_functions[c] if c in time_dependent_functions else c)
        for c in sorted(all_function_names)
    ]

    # Remove duplicates
    time_indep_function_names = list(dict.fromkeys(time_indep_function_names))
    return time_indep_function_names


def check_length(column_names, limit):
    over_limit = [
        f"{name:40} ({len(name)})" for name in column_names if len(name) > limit
    ]
    assert not over_limit, nice_output_list_of_strings(over_limit)


def test_all_default_targets_among_function_names(time_indep_function_names):
    check = [c for c in DEFAULT_TARGETS if c not in time_indep_function_names]
    assert not check, nice_output_list_of_strings(check)


def test_length_column_names_default_targets():
    check_length(
        column_names=DEFAULT_TARGETS, limit=GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS
    )


def test_length_column_names_input_variables(default_input_variables):
    check_length(
        column_names=default_input_variables,
        limit=GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS,
    )


def test_length_column_names_other_functions(time_indep_function_names):
    # Consider all functions that are not purely internal (starting with an underscore)
    # and not part of default targets
    other_function_names = [
        c
        for c in time_indep_function_names
        if c not in DEFAULT_TARGETS and not c.startswith("_")
    ]

    check_length(
        column_names=other_function_names, limit=GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS
    )
