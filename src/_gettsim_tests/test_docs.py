from __future__ import annotations

import datetime
import inspect

import pytest

from _gettsim.config import (
    PATHS_TO_INTERNAL_FUNCTIONS,
    RESOURCE_DIR,
    TYPES_INPUT_VARIABLES,
)
from _gettsim.functions.loader import (
    load_aggregation_specs_tree,
    load_functions_tree_for_date,
)
from _gettsim.shared import remove_group_suffix


def _nice_output_list_of_strings(list_of_strings):
    my_str = "\n".join(sorted(list_of_strings))
    return f"\n\n{my_str}\n\n"


@pytest.fixture(scope="module")
def default_input_variables():
    return sorted(TYPES_INPUT_VARIABLES.keys())


@pytest.fixture(scope="module")
def all_function_names():
    functions = _load_internal_functions()  # noqa: F821
    return sorted([func.leaf_name for func in functions])


@pytest.fixture(scope="module")
def aggregation_dict():
    return load_aggregation_specs_tree()


@pytest.fixture(scope="module")
def time_indep_function_names(all_function_names):
    time_dependent_functions = {}
    for year in range(1990, 2023):
        year_functions = load_functions_tree_for_date(
            datetime.date(year=year, month=1, day=1)
        )
        new_dict = {func.function.__name__: func.leaf_name for func in year_functions}
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
    functions = _load_internal_functions()  # noqa: F821

    # Collect arguments of all non-internal functions (do not start with underscore)
    arguments = [
        i
        for f in functions
        for i in list(inspect.signature(f).parameters)
        if not f.leaf_name.startswith("_")
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


@pytest.mark.xfail(reason="Not able to load functions regardless of date any more.")
def test_funcs_in_doc_module_and_func_from_internal_files_are_the_same():
    documented_functions = {
        f.leaf_name
        for f in _load_functions(  # noqa: F821
            RESOURCE_DIR / "functions" / "all_functions_for_docs.py",
            package_root=RESOURCE_DIR,
            include_imported_functions=True,
        )
    }

    internal_function_files = [
        RESOURCE_DIR.joinpath(p) for p in PATHS_TO_INTERNAL_FUNCTIONS
    ]

    internal_functions = {
        f.leaf_name
        for f in _load_functions(  # noqa: F821
            internal_function_files,
            package_root=RESOURCE_DIR,
            include_imported_functions=True,
        )
        if not f.original_function_name.startswith("_")
    }

    assert documented_functions == internal_functions


@pytest.mark.xfail(reason="Not able to load functions regardless of date any more.")
def test_type_hints():  # noqa: PLR0912
    """Check if output and input types of all functions coincide."""
    types = {}

    for func in _load_internal_functions():  # noqa: F821
        if func.skip_vectorization:
            continue

        name = func.leaf_name

        for var, internal_type in func.__annotations__.items():
            if var == "return":
                if name in types:
                    if types[name] != internal_type:
                        raise ValueError(
                            f"The return type hint of {func.original_function_name}, "
                            f"does not coincide  with the input type hint of "
                            f"another function."
                        )
                else:
                    types[name] = internal_type
            else:
                if var in TYPES_INPUT_VARIABLES:
                    if internal_type != TYPES_INPUT_VARIABLES[var]:
                        raise ValueError(
                            f"The input type hint of {var} in function "
                            f"{func.original_function_name} does not coincide with the "
                            f"standard data types provided in the config file."
                        )
                elif var in types:
                    if types[var] != internal_type:
                        raise ValueError(
                            f"The type hint of {var} in {func.original_function_name} "
                            f"does not coincide with the input type hint "
                            f"of another function."
                        )
                else:
                    types[var] = internal_type
