import numpy as np
from pandas.api.types import is_bool_dtype
from pandas.api.types import is_datetime64_any_dtype
from pandas.api.types import is_float_dtype
from pandas.api.types import is_integer_dtype
from pandas.api.types import is_object_dtype


def convert_series_to_internal_type(series, internal_type):
    """Check if data type of series fits to the internal type of gettsim and
    otherwise convert data type of series to the internal type of gettsim.

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

    if internal_type == float:
        # Conversion from boolean to float fails
        if is_bool_dtype(series):
            raise ValueError(f"Conversion of data type to {internal_type} failed.")
        elif not is_float_dtype(series):
            try:
                series = series.astype(float)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == bool:
        out = is_bool_dtype(series)
        cond1 = is_integer_dtype(series) or is_float_dtype(series)
        cond2 = is_object_dtype(series)
        if out:
            series = series
        # if input data type is integer or float,
        # check if series consists only of 1 or 0
        elif cond1:
            if len([v for v in series.unique() if v not in [1, 0]]) == 0:
                try:
                    series = series.astype(bool)
                except ValueError:
                    raise ValueError(
                        f"Conversion of data type to {internal_type} failed."
                    )
            else:
                raise ValueError(
                    f"Conversion to {internal_type} failed."
                    f" Input data does not only consist of 1 or 0."
                )
        # if input data type is string, check if series consists only of True or False
        elif cond2:
            if len([v for v in series.unique() if v not in ["True", "False"]]) == 0:
                try:
                    series = series.replace({"True": True, "False": False})
                except ValueError:
                    raise ValueError(
                        f"Conversion to {internal_type} failed."
                        f" Input data does not only consist of True or False."
                    )
            else:
                raise ValueError(
                    f"Conversion to {internal_type} failed."
                    f" Input data does not consist of statements True or False."
                )
        else:
            try:
                series = series.astype(bool)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == int:
        out = is_integer_dtype(series)
        cond = is_float_dtype(series)
        if out:
            series = series
        elif cond:
            # checking if decimal spaces are equal to 0, if not return error
            if np.array_equal(series, series.astype(np.int64)):
                try:
                    series = series.astype(np.int64)
                except ValueError:
                    raise ValueError(
                        f"Conversion of data type to {internal_type} failed."
                    )
            else:
                raise ValueError(
                    "Data type of input is float but should be int. "
                    "An automatic conversion would lead to rounded numbers."
                )
        else:
            try:
                series = series.astype(np.int64)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    elif internal_type == np.datetime64:
        out = is_datetime64_any_dtype(series)
        if out:
            series = series
        else:
            try:
                series = series.astype(np.datetime64)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    else:
        raise ValueError(f"The internal type {internal_type} is not defined.")

    return series
