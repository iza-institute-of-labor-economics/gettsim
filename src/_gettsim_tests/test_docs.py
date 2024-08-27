from __future__ import annotations

import datetime
import inspect

import pytest

from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions_loader import (
    _convert_paths_to_import_strings,
    _load_functions,
    load_aggregation_dict,
)
from _gettsim.policy_environment import load_functions_for_date
from _gettsim.shared import remove_group_suffix


def _nice_output_list_of_strings(list_of_strings):
    my_str = "\n".join(sorted(list_of_strings))
    return f"\n\n{my_str}\n\n"


@pytest.fixture(scope="module")
def default_input_variables():
    return sorted(TYPES_INPUT_VARIABLES.keys())


@pytest.fixture(scope="module")
def all_function_names():
    functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)
    return sorted(functions.keys())


@pytest.fixture(scope="module")
def aggregation_dict():
    return load_aggregation_dict()


@pytest.fixture(scope="module")
def time_indep_function_names(all_function_names):
    time_dependent_functions = {}
    for year in range(1990, 2023):
        year_functions = load_functions_for_date(
            datetime.date(year=year, month=1, day=1)
        )
        new_dict = {func.__name__: key for key, func in year_functions.items()}
        time_dependent_functions = {**time_dependent_functions, **new_dict}

    # Only use time dependent function names
    time_indep_function_names = [
        (time_dependent_functions.get(c, c)) for c in sorted(all_function_names)
    ]

    # Remove duplicates
    time_indep_function_names = list(dict.fromkeys(time_indep_function_names))
    return time_indep_function_names


@pytest.mark.xfail(
    reason="Uses an internal function to load functions,"
    " which does not include derived functions."
)
def test_all_input_vars_documented(
    default_input_variables,
    time_indep_function_names,
    all_function_names,
    aggregation_dict,
):
    """Test if arguments of all non-internal functions are either the name of another
    function, a documented input variable, or a parameter dictionary."""
    functions = _load_functions(PATHS_TO_INTERNAL_FUNCTIONS)

    # Collect arguments of all non-internal functions (do not start with underscore)
    arguments = [
        i
        for f in functions
        for i in list(inspect.signature(functions[f]).parameters)
        if not f.startswith("_")
    ]

    # Remove duplicates
    arguments = list(dict.fromkeys(arguments))
    defined_functions = (
        time_indep_function_names
        + all_function_names
        + default_input_variables
        + list(aggregation_dict)
    )
    check = [
        c
        for c in arguments
        if (c not in defined_functions)
        and (remove_group_suffix(c) not in defined_functions)
        and (not c.endswith("_params"))
    ]

    assert not check, _nice_output_list_of_strings(check)


def test_funcs_in_doc_module_and_func_from_internal_files_are_the_same():
    documented_functions = _load_functions(
        RESOURCE_DIR / "functions.py", include_imported_functions=True
    )

    internal_function_files = [
        RESOURCE_DIR.joinpath(p) for p in PATHS_TO_INTERNAL_FUNCTIONS
    ]
    internal_functions = _load_functions(
        internal_function_files, include_imported_functions=True
    )

    # Private functions are not imported in functions.py.
    internal_functions = {
        k: v for k, v in internal_functions.items() if not k.startswith("_")
    }

    assert set(documented_functions) == set(internal_functions)


def test_type_hints():  # noqa: PLR0912
    """Check if output and input types of all functions coincide."""
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    # Load all time dependent functions
    time_dependent_functions = {}
    for year in range(1990, 2024):
        year_functions = load_functions_for_date(
            datetime.date(year=year, month=1, day=1)
        )
        new_dict = {func.__name__: key for key, func in year_functions.items()}
        time_dependent_functions = {**time_dependent_functions, **new_dict}

    return_types = {}
    for name, func in functions.items():
        if hasattr(func, "__info__") and func.__info__["skip_vectorization"]:
            continue

        for var, internal_type in func.__annotations__.items():
            if var == "return":
                output_name = time_dependent_functions.get(name, name)

                if output_name in return_types:
                    if return_types[output_name] != internal_type:
                        raise ValueError(
                            f"The return type hint of {name}, does not "
                            f"coincide  with the input type hint of "
                            f"another function."
                        )
                else:
                    return_types[name] = internal_type
            else:
                if var in TYPES_INPUT_VARIABLES:
                    if internal_type != TYPES_INPUT_VARIABLES[var]:
                        raise ValueError(
                            f"The input type hint of {var} in function "
                            f"{name} does not coincide with the standard "
                            f"data types provided in the config file."
                        )
                elif var in return_types:
                    if return_types[var] != internal_type:
                        raise ValueError(
                            f"The type hint of {var} in {name} "
                            f"does not coincide with the input type hint "
                            f"of another function."
                        )
                else:
                    return_types[var] = internal_type
