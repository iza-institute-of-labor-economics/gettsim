import inspect
import re
from collections.abc import Callable
from typing import Any

from dags.signature import rename_arguments
from optree import tree_flatten_with_path

from _gettsim.config import SUPPORTED_GROUPINGS, SUPPORTED_TIME_UNITS
from _gettsim.functions.derived_function import DerivedFunction
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.shared import update_tree

_M_PER_Y = 12
_W_PER_Y = 365.25 / 7
_D_PER_Y = 365.25


def y_to_m(value: float) -> float:
    """
    Converts yearly to monthly values.

    Parameters
    ----------
    value
        Yearly value to be converted to monthly value.

    Returns
    -------
    float
        Monthly value.
    """
    return value / _M_PER_Y


def y_to_w(value: float) -> float:
    """
    Converts yearly to weekly values.

    Parameters
    ----------
    value
        Yearly value to be converted to weekly value.

    Returns
    -------
    float
        Weekly value.
    """
    return value / _W_PER_Y


def y_to_d(value: float) -> float:
    """
    Converts yearly to daily values.

    Parameters
    ----------
    value
        Yearly value to be converted to daily value.

    Returns
    -------
    float
        Daily value.
    """
    return value / _D_PER_Y


def m_to_y(value: float) -> float:
    """
    Converts monthly to yearly values.

    Parameters
    ----------
    value
        Monthly value to be converted to yearly value.

    Returns
    -------
    float
        Yearly value.
    """
    return value * _M_PER_Y


def m_to_w(value: float) -> float:
    """
    Converts monthly to weekly values.

    Parameters
    ----------
    value
        Monthly value to be converted to weekly value.

    Returns
    -------
    float
        Weekly value.
    """
    return value * _M_PER_Y / _W_PER_Y


def m_to_d(value: float) -> float:
    """
    Converts monthly to daily values.

    Parameters
    ----------
    value
        Monthly value to be converted to daily value.

    Returns
    -------
    float
        Daily value.
    """
    return value * _M_PER_Y / _D_PER_Y


def w_to_y(value: float) -> float:
    """
    Converts weekly to yearly values.

    Parameters
    ----------
    value
        Weekly value to be converted to yearly value.

    Returns
    -------
    float
        Yearly value.
    """
    return value * _W_PER_Y


def w_to_m(value: float) -> float:
    """
    Converts weekly to monthly values.

    Parameters
    ----------
    value
        Weekly value to be converted to monthly value.

    Returns
    -------
    float
        Monthly value.
    """
    return value * _W_PER_Y / _M_PER_Y


def w_to_d(value: float) -> float:
    """
    Converts weekly to daily values.

    Parameters
    ----------
    value
        Weekly value to be converted to daily value.

    Returns
    -------
    float
        Daily value.
    """
    return value * _W_PER_Y / _D_PER_Y


def d_to_y(value: float) -> float:
    """
    Converts daily to yearly values.

    Parameters
    ----------
    value
        Daily value to be converted to yearly value.

    Returns
    -------
    float
        Yearly value.
    """
    return value * _D_PER_Y


def d_to_m(value: float) -> float:
    """
    Converts daily to monthly values.

    Parameters
    ----------
    value
        Daily value to be converted to monthly value.

    Returns
    -------
    float
        Monthly value.
    """
    return value * _D_PER_Y / _M_PER_Y


def d_to_w(value: float) -> float:
    """
    Converts daily to weekly values.

    Parameters
    ----------
    value
        Daily value to be converted to weekly value.

    Returns
    -------
    float
        Weekly value.
    """
    return value * _D_PER_Y / _W_PER_Y


_time_conversion_functions = {
    "y_to_m": y_to_m,
    "y_to_w": y_to_w,
    "y_to_d": y_to_d,
    "m_to_y": m_to_y,
    "m_to_w": m_to_w,
    "m_to_d": m_to_d,
    "w_to_y": w_to_y,
    "w_to_m": w_to_m,
    "w_to_d": w_to_d,
    "d_to_y": d_to_y,
    "d_to_m": d_to_m,
    "d_to_w": d_to_w,
}


def create_time_conversion_functions(
    functions_tree: dict[str, Any],
    data_cols: list[str],
) -> dict[str, Any]:
    """
     Create functions that convert variables to different time units.

    The time unit of a function is determined by a naming convention:
    * Functions referring to yearly values end with "_y", or "_y_x" where "x" is a
        grouping level.
    * Functions referring to monthly values end with "_m", or "_m_x" where "x" is a
        grouping level.
    * Functions referring to weekly values end with "_w", or "_w_x" where "x" is a
        grouping level.
    * Functions referring to daily values end with "_d", or "_d_x" where "x" is a
        grouping level.

    Unless the corresponding function already exists, the following functions are
    created:
    * For functions referring to yearly values, create monthly, weekly and daily
    functions.
    * For functions referring to monthly values, create yearly, weekly and daily
    functions.
    * For functions referring to weekly values, create yearly, monthly and daily
    functions.
    * For functions referring to daily values, create yearly, monthly and weekly
    functions.

    Parameters
    ----------
    functions_tree:
        Dictionary of functions.
    data_cols:
        List of data columns.

    Returns
    -------
    derived_functions:
        Dictionary of created functions.
    """

    converted_functions = {}

    paths, funcs, _ = tree_flatten_with_path(functions_tree)
    qualified_names = ["__".join(path) for path in paths]

    # Create time-conversions for existing functions
    for path, func in zip(paths, funcs):
        function_name = path[-1]
        new_funcs_dict = {
            der_name: der_func
            for der_name, der_func in _create_time_conversion_functions(
                function_name, func
            ).items()
            if der_name not in qualified_names and der_name not in data_cols
        }
        for k, v in new_funcs_dict.items():
            stem = path[:-1] if len(path) > 1 else None
            new_path = [*stem, k] if stem else [k]
            converted_functions = update_tree(converted_functions, new_path, v)

    for qualified_name in data_cols:
        name = qualified_name.split("__")[-1]
        new_funcs_dict = {
            der_name: der_func
            for der_name, der_func in _create_time_conversion_functions(name).items()
            if der_name not in data_cols
        }
        for k, v in new_funcs_dict.items():
            stem = qualified_name.split("__")[-1] if "__" in qualified_name else None
            new_path = [*stem, k] if stem else [k]
            converted_functions = update_tree(converted_functions, new_path, v)

    return converted_functions


def _create_time_conversion_functions(
    name: str, func: PolicyFunction | None = None
) -> dict[str, DerivedFunction]:
    result: dict[str, DerivedFunction] = {}

    all_time_units = list(SUPPORTED_TIME_UNITS)

    units = "".join(all_time_units)
    groupings = "|".join([f"_{grouping}" for grouping in SUPPORTED_GROUPINGS])
    function_with_time_unit = re.compile(
        f"(?P<base_name>.*_)(?P<time_unit>[{units}])(?P<aggregation>{groupings})?"
    )
    match = function_with_time_unit.fullmatch(name)
    dependencies = set(inspect.signature(func).parameters) if func else set()

    if match:
        base_name = match.group("base_name")
        time_unit = match.group("time_unit")
        aggregation = match.group("aggregation") or ""

        missing_time_units = [unit for unit in all_time_units if unit != time_unit]
        for missing_time_unit in missing_time_units:
            new_name = f"{base_name}{missing_time_unit}{aggregation}"

            # Without this check, we could create cycles in the DAG: Consider a
            # hard-coded function `var_y` that takes `var_m` as an input, assuming it
            # to be provided in the input data. If we create a function `var_m`, which
            # would take `var_y` as input, we create a cycle. If `var_m` is actually
            # provided as an input, `var_m` would be overwritten, removing the cycle.
            # However, if `var_m` is not provided as an input, an error message would
            # be shown that a cycle between `var_y` and `var_m` was detected. This
            # hides the actual problem, which is that `var_m` is not provided as an
            # input.
            if new_name in dependencies:
                continue

            result[new_name] = DerivedFunction(
                _create_function_for_time_unit(
                    name,
                    _time_conversion_functions[f"{time_unit}_to_{missing_time_unit}"],
                ),
                function_name=new_name,
                derived_from=func or name,
            )

    return result


def _create_function_for_time_unit(
    function_name: str, converter: Callable[[float], float]
) -> Callable[[float], float]:
    @rename_arguments(mapper={"x": function_name})
    def func(x: float) -> float:
        return converter(x)

    return func
