from typing import Callable

from dags.signature import rename_arguments

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


def create_functions_for_time_units(
        functions: dict[str, Callable],
        data_cols: list[str],
) -> dict[str, Callable]:
    """
    Create functions for other time units.

    The time unit of a function is determined by a naming convention:
    * Yearly functions end with "_y", "_y_hh" or "_y_tu".
    * Monthly functions end with "_m", "_m_hh" or "_m_tu".
    * Weekly functions end with "_w", "_w_hh" or "_w_tu".
    * Daily functions end with "_d", "_d_hh" or "_d_tu".

    Unless the corresponding function already exists, the following functions are
    created:
    * For yearly functions, create monthly, weekly and daily functions.
    * For monthly functions, create yearly, weekly and daily functions.
    * For weekly functions, create yearly, monthly and daily functions.
    * For daily functions, create yearly, monthly and weekly functions.

    Parameters
    ----------
    functions
        Dictionary of functions.
    data_cols
        List of data columns.

    Returns
    -------
    dict[str, Callable]
        Dictionary of created functions.
    """

    result = {}

    for name, func in functions.items():
        result.update(_create_functions_for_time_units(name, func))

    for name in data_cols:
        result.update(_create_functions_for_time_units(name))

    return {
        name: func
        for name, func in result.items()
        if name not in functions and name not in data_cols
    }


def _create_functions_for_time_units(  # noqa: PLR0915
        name: str,
        func: Callable | None = None
) -> dict[str, Callable]:
    result = {}
    info = getattr(func, "__info__", None)

    if name.endswith("_y"):
        result[_replace_suffix(name, "_y", "_m")] = _create_function_for_time_unit(name, info, y_to_m)
        result[_replace_suffix(name, "_y", "_w")] = _create_function_for_time_unit(name, info, y_to_w)
        result[_replace_suffix(name, "_y", "_d")] = _create_function_for_time_unit(name, info, y_to_d)
    if name.endswith("_y_hh"):
        result[_replace_suffix(name, "_y_hh", "_m_hh")] = _create_function_for_time_unit(name, info, y_to_m)
        result[_replace_suffix(name, "_y_hh", "_w_hh")] = _create_function_for_time_unit(name, info, y_to_w)
        result[_replace_suffix(name, "_y_hh", "_d_hh")] = _create_function_for_time_unit(name, info, y_to_d)
    if name.endswith("_y_tu"):
        result[_replace_suffix(name, "_y_tu", "_m_tu")] = _create_function_for_time_unit(name, info, y_to_m)
        result[_replace_suffix(name, "_y_tu", "_w_tu")] = _create_function_for_time_unit(name, info, y_to_w)
        result[_replace_suffix(name, "_y_tu", "_d_tu")] = _create_function_for_time_unit(name, info, y_to_d)

    if name.endswith("_m"):
        result[_replace_suffix(name, "_m", "_y")] = _create_function_for_time_unit(name, info, m_to_y)
        result[_replace_suffix(name, "_m", "_w")] = _create_function_for_time_unit(name, info, m_to_w)
        result[_replace_suffix(name, "_m", "_d")] = _create_function_for_time_unit(name, info, m_to_d)
    if name.endswith("_m_hh"):
        result[_replace_suffix(name, "_m_hh", "_y_hh")] = _create_function_for_time_unit(name, info, m_to_y)
        result[_replace_suffix(name, "_m_hh", "_w_hh")] = _create_function_for_time_unit(name, info, m_to_w)
        result[_replace_suffix(name, "_m_hh", "_d_hh")] = _create_function_for_time_unit(name, info, m_to_d)
    if name.endswith("_m_tu"):
        result[_replace_suffix(name, "_m_tu", "_y_tu")] = _create_function_for_time_unit(name, info, m_to_y)
        result[_replace_suffix(name, "_m_tu", "_w_tu")] = _create_function_for_time_unit(name, info, m_to_w)
        result[_replace_suffix(name, "_m_tu", "_d_tu")] = _create_function_for_time_unit(name, info, m_to_d)

    if name.endswith("_w"):
        result[_replace_suffix(name, "_w", "_y")] = _create_function_for_time_unit(name, info, w_to_y)
        result[_replace_suffix(name, "_w", "_m")] = _create_function_for_time_unit(name, info, w_to_m)
        result[_replace_suffix(name, "_w", "_d")] = _create_function_for_time_unit(name, info, w_to_d)
    if name.endswith("_w_hh"):
        result[_replace_suffix(name, "_w_hh", "_y_hh")] = _create_function_for_time_unit(name, info, w_to_y)
        result[_replace_suffix(name, "_w_hh", "_m_hh")] = _create_function_for_time_unit(name, info, w_to_m)
        result[_replace_suffix(name, "_w_hh", "_d_hh")] = _create_function_for_time_unit(name, info, w_to_d)
    if name.endswith("_w_tu"):
        result[_replace_suffix(name, "_w_tu", "_y_tu")] = _create_function_for_time_unit(name, info, w_to_y)
        result[_replace_suffix(name, "_w_tu", "_m_tu")] = _create_function_for_time_unit(name, info, w_to_m)
        result[_replace_suffix(name, "_w_tu", "_d_tu")] = _create_function_for_time_unit(name, info, w_to_d)

    if name.endswith("_d"):
        result[_replace_suffix(name, "_d", "_y")] = _create_function_for_time_unit(name, info, d_to_y)
        result[_replace_suffix(name, "_d", "_m")] = _create_function_for_time_unit(name, info, d_to_m)
        result[_replace_suffix(name, "_d", "_w")] = _create_function_for_time_unit(name, info, d_to_w)
    if name.endswith("_d_hh"):
        result[_replace_suffix(name, "_d_hh", "_y_hh")] = _create_function_for_time_unit(name, info, d_to_y)
        result[_replace_suffix(name, "_d_hh", "_m_hh")] = _create_function_for_time_unit(name, info, d_to_m)
        result[_replace_suffix(name, "_d_hh", "_w_hh")] = _create_function_for_time_unit(name, info, d_to_w)
    if name.endswith("_d_tu"):
        result[_replace_suffix(name, "_d_tu", "_y_tu")] = _create_function_for_time_unit(name, info, d_to_y)
        result[_replace_suffix(name, "_d_tu", "_m_tu")] = _create_function_for_time_unit(name, info, d_to_m)
        result[_replace_suffix(name, "_d_tu", "_w_tu")] = _create_function_for_time_unit(name, info, d_to_w)

    return result

def _replace_suffix(name: str, old_suffix: str, new_suffix: str) -> str:
    if not name.endswith(old_suffix):
        return name

    return name.removesuffix(old_suffix) + new_suffix


def _create_function_for_time_unit(
        function_name: str,
        info: dict | None,
        converter: Callable[[float], float]
) -> Callable[[float], float]:
    @rename_arguments(mapper={"x": function_name})
    def func(x: float) -> float:
        return converter(x)

    if info is not None:
        func.__info__ = info

    return func
