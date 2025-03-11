from typing import Union

import numpy
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_object_dtype,
)

from _gettsim.aggregation import AggregateByGroupSpec, AggregateByPIDSpec
from _gettsim.config import numpy_or_jax as np
from _gettsim.function_types import DerivedFunction, PolicyFunction

NestedFunctionDict = dict[
    str, Union[PolicyFunction, DerivedFunction, "NestedFunctionDict"]
]
NestedTargetDict = dict[str, Union[None, "NestedTargetDict"]]
NestedInputStructureDict = dict[str, Union[None, "NestedInputStructureDict"]]
NestedDataDict = dict[str, Union[pd.Series, "NestedDataDict"]]
NestedSeriesDict = dict[str, Union[pd.Series, "NestedSeriesDict"]]
NestedArrayDict = dict[str, Union[np.ndarray, "NestedArrayDict"]]
NestedAggregationSpecDict = dict[
    str, Union[AggregateByGroupSpec, AggregateByPIDSpec, "NestedAggregationSpecDict"]
]


def check_series_has_expected_type(series: pd.Series, internal_type: np.dtype) -> bool:
    """Checks whether used series has already expected internal type.

    Parameters
    ----------
    series : pandas.Series or pandas.DataFrame or dict of pandas.Series
        Data provided by the user.
    internal_type : TypeVar
        One of the internal gettsim types.

    Returns
    -------
    Bool

    """
    if (internal_type == float) & (is_float_dtype(series)):
        out = True
    elif (internal_type == int) & (is_integer_dtype(series)):
        out = True
    elif (internal_type == bool) & (is_bool_dtype(series)):
        out = True
    elif (internal_type == numpy.datetime64) & (is_datetime64_any_dtype(series)):
        out = True
    else:
        out = False

    return out


def convert_series_to_internal_type(
    series: pd.Series, internal_type: np.dtype
) -> pd.Series:
    """Check if data type of series fits to the internal type of gettsim and otherwise
    convert data type of series to the internal type of gettsim.

    Parameters
    ----------
    series : pd.Series
        Some data series.
    internal_type : TypeVar
        One of the internal gettsim types.

    Returns
    -------
    out : adjusted pd.Series

    """
    # Copy input series in out
    out = series.copy()

    basic_error_msg = (
        f"Conversion from input type {out.dtype} to {internal_type.__name__} failed."
    )
    if is_object_dtype(out):
        raise ValueError(basic_error_msg + " Object type is not supported as input.")
    else:
        # Conversion to float
        if internal_type == float:
            # Conversion from boolean to float fails
            if is_bool_dtype(out):
                raise ValueError(basic_error_msg + " This conversion is not supported.")
            else:
                try:
                    out = out.astype(float)
                except ValueError as e:
                    raise ValueError(basic_error_msg) from e

        # Conversion to int
        elif internal_type == int:
            if is_float_dtype(out):
                # checking if decimal places are equal to 0, if not return error
                if np.array_equal(out, out.astype(np.int64)):
                    out = out.astype(np.int64)
                else:
                    raise ValueError(
                        basic_error_msg + " This conversion is only supported if all"
                        " decimal places of input data are equal to 0."
                    )
            else:
                try:
                    out = out.astype(np.int64)
                except ValueError as e:
                    raise ValueError(basic_error_msg) from e

        # Conversion to boolean
        elif internal_type == bool:
            # if input data type is integer
            if is_integer_dtype(out):
                # check if series consists only of 1 or 0
                if len([v for v in out.unique() if v not in [1, 0]]) == 0:
                    out = out.astype(bool)
                else:
                    raise ValueError(
                        basic_error_msg + " This conversion is only supported if"
                        " input data exclusively contains the values 1 and 0."
                    )
            # if input data type is float
            elif is_float_dtype(out):
                # check if series consists only of 1.0 or 0.0
                if len([v for v in out.unique() if v not in [1, 0]]) == 0:
                    out = out.astype(bool)
                else:
                    raise ValueError(
                        basic_error_msg + " This conversion is only supported if"
                        " input data exclusively contains the values 1.0 and 0.0."
                    )

            else:
                raise ValueError(
                    basic_error_msg + " Conversion to boolean is only supported for"
                    " int and float columns."
                )

        # Conversion to DateTime
        elif internal_type == np.datetime64:
            if not is_datetime64_any_dtype(out):
                try:
                    out = out.astype(np.datetime64)
                except ValueError as e:
                    raise ValueError(basic_error_msg) from e
        else:
            raise ValueError(f"The internal type {internal_type} is not yet supported.")

    return out
