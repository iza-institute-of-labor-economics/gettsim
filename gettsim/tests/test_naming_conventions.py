import pytest

from gettsim.config import DEFAULT_TARGETS
from gettsim.config import GEP_01_CHARACTER_LIMIT_DEFAULT_TARGETS
from gettsim.config import GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS
from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import STANDARD_DATA_TYPES
from gettsim.functions_loader import _load_functions


@pytest.fixture(scope="module")
def all_column_names():
    functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    return sorted(list(functions.keys()) + list(STANDARD_DATA_TYPES.keys()))


def nice_output(list_of_strings):
    return "\n\n" + "\n".join(sorted(list_of_strings)) + "\n\n"


def check_length(column_names, limit):
    over_limit = [
        f"{name:40} ({len(name)})" for name in column_names if len(name) > limit
    ]
    assert not over_limit, nice_output(over_limit)


def test_all_default_targets_among_column_names(all_column_names):
    check = [c for c in DEFAULT_TARGETS if c not in all_column_names]
    assert not check, nice_output(check)


def test_length_column_names_user_facing():
    user_facing_names = DEFAULT_TARGETS
    check_length(
        column_names=user_facing_names, limit=GEP_01_CHARACTER_LIMIT_DEFAULT_TARGETS
    )


def test_length_column_names_internal(all_column_names):
    internal_names = [
        c
        for c in all_column_names
        if c not in DEFAULT_TARGETS and not c.startswith("_")
    ]
    check_length(
        column_names=internal_names, limit=GEP_01_CHARACTER_LIMIT_OTHER_COLUMNS
    )
