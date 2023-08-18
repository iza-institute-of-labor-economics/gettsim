from __future__ import annotations

import pytest
from _gettsim.config import (
    DEFAULT_TARGETS,
    GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS,
    GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS,
    PATHS_TO_INTERNAL_FUNCTIONS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions_loader import _load_functions
from _gettsim.shared import remove_group_suffix


def _nice_output_list_of_strings(list_of_strings):
    my_str = "\n".join(sorted(list_of_strings))
    return f"\n\n{my_str}\n\n"


@pytest.fixture(scope="module")
def default_input_variables():
    return sorted(TYPES_INPUT_VARIABLES.keys())


@pytest.fixture(scope="module")
def all_functions() -> dict[str, callable]:
    return _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)


@pytest.fixture(scope="module")
def time_indep_function_names(all_functions: dict[str, callable]) -> list[str]:
    # Create a dictionary mapping function names to the DAG key
    function_name_to_dag_key = {}

    for function_name, function in all_functions.items():
        if hasattr(function, "__info__"):
            info = function.__info__
            if "dates_active_dag_key" in info:
                function_name_to_dag_key[function_name] = info["dates_active_dag_key"]

    # Names of all functions
    all_function_names = sorted(all_functions.keys())

    # Replace functions names with their DAG key if applicable
    time_indep_function_names = [
        (
            function_name_to_dag_key[function_name]
            if function_name in function_name_to_dag_key
            else function_name
        )
        for function_name in sorted(all_function_names)
    ]

    # Remove duplicates
    return list(dict.fromkeys(time_indep_function_names))


def check_length(column_names, limit):
    over_limit = [
        f"{name:40} ({len(name)})" for name in column_names if len(name) > limit
    ]
    assert not over_limit, (
        _nice_output_list_of_strings(over_limit) + f"limit is {limit}"
    )


def test_all_default_targets_among_function_names(time_indep_function_names):
    check = [
        c
        for c in DEFAULT_TARGETS
        if (c not in time_indep_function_names)
        and (remove_group_suffix(c) not in time_indep_function_names)
    ]
    assert not check, _nice_output_list_of_strings(check)


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
