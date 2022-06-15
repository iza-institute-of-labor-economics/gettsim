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
    # Copy input series in out
    out = series.copy()

    basic_error_msg = (
        "Conversion from input type " f"{out.dtype} to {internal_type.__name__} failed."
    )
    if is_object_dtype(out):
        raise ValueError(basic_error_msg + " Object type is not supported as input.")
    else:

        # Conversion to float
        if internal_type == float:
            # Conversion from boolean to float fails
            if is_bool_dtype(out):
                raise ValueError(basic_error_msg + " This conversion is not supported.")
            elif not is_float_dtype(out):
                try:
                    out = out.astype(float)
                except ValueError:
                    raise ValueError(basic_error_msg)

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
            elif not is_integer_dtype(out):
                try:
                    out = out.astype(np.int64)
                except ValueError:
                    raise ValueError(basic_error_msg)

        # Conversion to boolean
        elif internal_type == bool:

            # if input data type is integer or float,
            if is_integer_dtype(out) or is_float_dtype(out):

                # check if series consists only of 1 or 0
                if len([v for v in out.unique() if v not in [1, 0]]) == 0:
                    out = out.astype(bool)
                else:
                    raise ValueError(
                        basic_error_msg + " This conversion is only supported if"
                        " input data exclusively contains the values 1 and 0."
                    )

            elif not is_bool_dtype(out):
                raise ValueError(
                    basic_error_msg + " Conversion to boolean is only supported for"
                    " int and float columns."
                )

        # Conversion to DateTime
        elif internal_type == np.datetime64:
            if not is_datetime64_any_dtype(out):
                try:
                    out = out.astype(np.datetime64)
                except ValueError:
                    raise ValueError(basic_error_msg)
        else:
            raise ValueError(f"The internal type {internal_type} is not yet supported.")

    return out
