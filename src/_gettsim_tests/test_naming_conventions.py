from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from _gettsim.config import (
    DEFAULT_TARGETS,
    GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS,
    GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions_loader_new import _load_internal_functions
from _gettsim.shared import remove_group_suffix

if TYPE_CHECKING:
    from _gettsim.policy_function import PolicyFunction


def _nice_output_list_of_strings(list_of_strings):
    my_str = "\n".join(sorted(list_of_strings))
    return f"\n\n{my_str}\n\n"


@pytest.fixture(scope="module")
def default_input_variables():
    return sorted(TYPES_INPUT_VARIABLES.keys())


@pytest.fixture(scope="module")
def all_functions() -> list[PolicyFunction]:
    return _load_internal_functions()


@pytest.fixture(scope="module")
def function_names(all_functions: list[PolicyFunction]) -> list[str]:
    return sorted({func.name_in_dag for func in all_functions})


def check_length(column_names, limit):
    over_limit = [
        f"{name:40} ({len(name)})" for name in column_names if len(name) > limit
    ]
    assert not over_limit, (
        _nice_output_list_of_strings(over_limit) + f"limit is {limit}"
    )


def test_all_default_targets_among_function_names(function_names):
    check = [
        c
        for c in DEFAULT_TARGETS
        if (c not in function_names)
        and (remove_group_suffix(c) not in function_names)
    ]
    assert not check, _nice_output_list_of_strings(check)


@pytest.mark.skip(reason="Target names will change very soon.")
def test_length_column_names_default_targets():
    # TODO(@MImmesberger): Unskip test once target names are updated after updating DAG
    # to include Namespaces.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/760
    check_length(
        column_names=DEFAULT_TARGETS, limit=GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS
    )


def skip_test_length_column_names_input_variables(default_input_variables):
    check_length(
        column_names=default_input_variables,
        limit=GEP_01_CHARACTER_LIMIT_USER_FACING_COLUMNS,
    )


@pytest.mark.skip(reason="Target names will change very soon.")
def test_length_column_names_other_functions(function_names):
    # TODO(@MImmesberger): Unskip test once target names are updated after updating DAG
    # to include Namespaces.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/760
    # Consider all functions that are not purely internal (starting with an underscore)
    # and not part of default targets
    other_function_names = [
        c
        for c in function_names
        if c not in DEFAULT_TARGETS and not c.startswith("_")
    ]

    check_length(
        column_names=other_function_names, limit=GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS
    )
