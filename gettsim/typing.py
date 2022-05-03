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

    # Conversion to float
    if internal_type == float:
        # Conversion from boolean to float fails
        if is_bool_dtype(series):
            raise ValueError("Conversion of boolean to float is not supported.")
        elif not is_float_dtype(series):
            try:
                series = series.astype(float)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")

    # Conversion to int
    elif internal_type == int:
        if is_float_dtype(series):

            # checking if decimal spaces are equal to 0, if not return error
            if np.array_equal(series, series.astype(np.int64)):
                series = series.astype(np.int64)
            else:
                raise ValueError(
                    "Conversion of float to int is only supported"
                    " if all decimal spaces of input data are equal to 0."
                )
        elif not is_integer_dtype(series):
            try:
                series = series.astype(np.int64)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")

    # Conversion to boolean
    elif internal_type == bool:

        # if input data type is integer or float,
        if is_integer_dtype(series) or is_float_dtype(series):

            # check if series consists only of 1 or 0
            if len([v for v in series.unique() if v not in [1, 0]]) == 0:
                series = series.astype(bool)
            else:
                raise ValueError(
                    "Conversion of int or float to boolean is only supported"
                    " if input data only consists of 1 and 0."
                )

        # if input data type is object
        elif is_object_dtype(series):

            # Check if series consists only of True or False
            if len([v for v in series.unique() if v not in ["True", "False"]]) == 0:
                series = series.replace({"True": True, "False": False})
            else:
                raise ValueError(
                    "Conversion of object to boolean is only supported"
                    " if input data only consists of True and False."
                )
        elif not is_bool_dtype(series):
            raise ValueError(
                "Conversion to bool is only supported for "
                "bool, int, float or object columns."
            )

    # Conversion to DateTime
    elif internal_type == np.datetime64:
        if not is_datetime64_any_dtype(series):
            try:
                series = series.astype(np.datetime64)
            except ValueError:
                raise ValueError(f"Conversion of data type to {internal_type} failed.")
    else:
        raise ValueError(f"The internal type {internal_type} is not yet supported.")

    return series
