import inspect
import re
import textwrap
from datetime import date
from typing import Callable
from typing import Optional

from _gettsim.config import SUPPORTED_GROUPINGS


class KeyErrorMessage(str):
    """Subclass str to allow for line breaks in KeyError messages."""

    def __repr__(self):
        return str(self)


def add_rounding_spec(params_key):
    """Decorator adding the location of the rounding specification to a function.

    Parameters
    ----------
    params_key : str
        Key of the parameters dictionary where rounding specifications are found. For
        functions that are not user-written this is just the name of the respective
        .yaml file.

    Returns
    -------
    func : function
        Function with __rounding_params_key__ attribute

    """

    def inner(func):
        func.__rounding_params_key__ = params_key
        return func

    return inner


TIME_DEPENDENT_FUNCTIONS = []


def dates_active(
    start: str = "0001-01-01",
    end: str = "9999-12-31",
    change_name: Optional[str] = None,
) -> Callable:
    """
    Parameters
    ----------
    start
        The start date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    end
        The end date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    change_name
        The name that should be used as the key for the function in the DAG.
        If omitted, we use the name of the function as defined.

    Returns
    -------
        The function with attributes __dates_active_start__, __dates_active_end__,
        and __dates_active_dag_key__.
    """

    _validate_dashed_iso_date(start)
    _validate_dashed_iso_date(end)

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    _validate_date_range(start_date, end_date)

    def inner(func: Callable) -> Callable:
        func.__dates_active_start__ = start_date
        func.__dates_active_end__ = end_date
        func.__dates_active_dag_key__ = change_name if change_name else func.__name__

        _check_for_conflicts(func.__dates_active_dag_key__, start_date, end_date)
        TIME_DEPENDENT_FUNCTIONS.append(func)

        return func

    return inner


_dashed_iso_date = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_dashed_iso_date(date_str: str):
    if not _dashed_iso_date.match(date_str):
        raise ValueError(f"Date {date_str} does not match the format YYYY-MM-DD.")


def _validate_date_range(start: date, end: date):
    if start > end:
        raise ValueError(
            f"The start date {start.isoformat()} must be before the end date "
            f"{end.isoformat()}."
        )


def _check_for_conflicts(dag_key: str, start: date, end: date):
    if any(
        f.__dates_active_dag_key__ == dag_key
        and (
            start <= f.__dates_active_start__ <= end
            or f.__dates_active_start__ <= start <= f.__dates_active_end__
        )
        for f in TIME_DEPENDENT_FUNCTIONS
    ):
        raise ConflictingTimeDependentFunctionsError(
            f"The time period of {dag_key} ({start} to {end}) overlaps with another "
            f"function's time period."
        )


class ConflictingTimeDependentFunctionsError(Exception):
    """Exception raised when two time dependent functions are active at the same time.

    Attributes
    ----------
    message : str
        The error message.

    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def format_list_linewise(list_):
    formatted_list = '",\n    "'.join(list_)
    return textwrap.dedent(
        """
        [
            "{formatted_list}",
        ]
        """
    ).format(formatted_list=formatted_list)


def parse_to_list_of_strings(user_input, name):
    """Parse None, str, and list of strings to list of strings.

    Note that the function automatically removes duplicates.

    """
    if user_input is None:
        user_input = []
    elif isinstance(user_input, str):
        user_input = [user_input]
    elif isinstance(user_input, list) and all(isinstance(i, str) for i in user_input):
        pass
    else:
        NotImplementedError(
            f"{name!r} needs to be None, a string or a list of strings."
        )

    return sorted(set(user_input))


def format_errors_and_warnings(text, width=79):
    """Format our own exception messages and warnings by dedenting paragraphs and
    wrapping at the specified width. Mainly required because of messages are written as
    part of indented blocks in our source code.

    Parameter
    ---------
    text : str
        The text which can include multiple paragraphs separated by two newlines.
    width : int
        The text will be wrapped by `width` characters.

    Returns
    -------
    formatted_text : str
        Correctly dedented, wrapped text.

    """
    text = text.lstrip("\n")
    paragraphs = text.split("\n\n")
    wrapped_paragraphs = []
    for paragraph in paragraphs:
        dedented_paragraph = textwrap.dedent(paragraph)
        wrapped_paragraph = textwrap.fill(dedented_paragraph, width=width)
        wrapped_paragraphs.append(wrapped_paragraph)

    formatted_text = "\n\n".join(wrapped_paragraphs)

    return formatted_text


def get_names_of_arguments_without_defaults(function):
    """Get argument names without defaults.

    The detection of argument names also works for partialed functions.

    Examples
    --------
    >>> def func(a, b): pass
    >>> get_names_of_arguments_without_defaults(func)
    ['a', 'b']
    >>> import functools
    >>> func_ = functools.partial(func, a=1)
    >>> get_names_of_arguments_without_defaults(func_)
    ['b']

    """
    parameters = inspect.signature(function).parameters

    argument_names_without_defaults = []
    for parameter in parameters:
        if parameters[parameter].default == parameters[parameter].empty:
            argument_names_without_defaults.append(parameter)

    return argument_names_without_defaults


def remove_group_suffix(col):
    out = col
    for g in SUPPORTED_GROUPINGS:
        out = out.removesuffix(f"_{g}")

    return out
