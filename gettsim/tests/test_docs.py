import datetime
import inspect

import pytest

from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.config import ROOT_DIR
from gettsim.config import TYPES_INPUT_VARIABLES
from gettsim.functions_loader import _convert_paths_to_import_strings
from gettsim.functions_loader import _load_functions
from gettsim.policy_environment import load_reforms_for_date


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
    for year in range(1990, 2021):
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


def nice_output(list_of_strings):
    return "\n\n" + "\n".join(sorted(list_of_strings)) + "\n\n"


def test_all_input_vars_documented(
    default_input_variables, time_indep_function_names, all_function_names
):
    """Test if arguments of all non-internal functions are either the name of another
    function, a documented input variable, or a parameter dictionnairy
    """
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

    check = [
        c
        for c in arguments
        if c not in time_indep_function_names
        and c not in all_function_names
        and c not in default_input_variables
        and not c.endswith("_params")
    ]
    assert not check, nice_output(check)


def test_funcs_in_doc_module_and_func_from_internal_files_are_the_same():
    documented_functions = _load_functions(
        ROOT_DIR / "functions.py", include_imported_functions=True
    )

    internal_function_files = [
        ROOT_DIR.joinpath(p) for p in PATHS_TO_INTERNAL_FUNCTIONS
    ]
    internal_functions = _load_functions(
        internal_function_files, include_imported_functions=True
    )

    # Private functions are not imported in functions.py.
    internal_functions = {
        k: v for k, v in internal_functions.items() if not k.startswith("_")
    }

    assert set(documented_functions) == set(internal_functions)


def test_type_hints():
    """Check if output and input types of all functions coincide."""
    imports = _convert_paths_to_import_strings(PATHS_TO_INTERNAL_FUNCTIONS)
    functions = _load_functions(imports)

    # Load all time dependent functions
    time_dependent_functions = {}
    for year in range(1990, 2021):
        year_functions = load_reforms_for_date(datetime.date(year=year, month=1, day=1))
        new_dict = {func.__name__: key for key, func in year_functions.items()}
        time_dependent_functions = {**time_dependent_functions, **new_dict}

    return_types = {}
    for name, func in functions.items():
        for var, internal_type in func.__annotations__.items():
            if var == "return":
                if name in time_dependent_functions:
                    output_name = time_dependent_functions[name]
                else:
                    output_name = name

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
