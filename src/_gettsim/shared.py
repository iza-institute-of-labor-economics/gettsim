import inspect
import re
import textwrap
from datetime import date
from typing import Callable, Optional

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
        Function with __info__["rounding_params_key"] attribute

    """

    def inner(func):
        # Remember data from decorator
        if not hasattr(func, "__info__"):
            func.__info__ = {}
        func.__info__["rounding_params_key"] = params_key

        return func

    return inner


TIME_DEPENDENT_FUNCTIONS: dict[str, list[Callable]] = {}


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
        The function with attributes __info__["dates_active_start"],
        __info__["dates_active_end"], and __info__["dates_active_dag_key"].
    """

    _validate_dashed_iso_date(start)
    _validate_dashed_iso_date(end)

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    _validate_date_range(start_date, end_date)

    def inner(func: Callable) -> Callable:
        dag_key = change_name if change_name else func.__name__

        _check_for_conflicts(dag_key, func.__name__, start_date, end_date)

        # Remember data from decorator
        if not hasattr(func, "__info__"):
            func.__info__ = {}
        func.__info__["dates_active_start"] = start_date
        func.__info__["dates_active_end"] = end_date
        func.__info__["dates_active_dag_key"] = dag_key

        # Register time-dependent function
        if dag_key not in TIME_DEPENDENT_FUNCTIONS:
            TIME_DEPENDENT_FUNCTIONS[dag_key] = []
        TIME_DEPENDENT_FUNCTIONS[dag_key].append(func)

        return func

    return inner


_dashed_iso_date = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_dashed_iso_date(date_str: str):
    if not _dashed_iso_date.match(date_str):
        raise ValueError( # noqa: TRY003
            f"Date {date_str} does not match the format YYYY-MM-DD."
        )


def _validate_date_range(start: date, end: date):
    if start > end:
        raise ValueError( # noqa: TRY003
            f"The start date {start} must be before the end date {end}."
        )


def _check_for_conflicts(dag_key: str, function_name: str, start: date, end: date):
    if dag_key not in TIME_DEPENDENT_FUNCTIONS:
        return

    for f in TIME_DEPENDENT_FUNCTIONS[dag_key]:
        # While testing, the same function might be added to the registry again,
        # leading to wrong conflict errors. We prevent this by only reporting
        # conflicts if the functions have different names.
        if f.__name__ != function_name and (
            start <= f.__info__["dates_active_start"] <= end
            or f.__info__["dates_active_start"]
            <= start
            <= f.__info__["dates_active_end"]
        ):
            raise ConflictingTimeDependentFunctionsError(
                dag_key,
                function_name,
                start,
                end,
                f.__name__,
                f.__info__["dates_active_start"],
                f.__info__["dates_active_end"],
            )


class ConflictingTimeDependentFunctionsError(Exception):
    """Raised when two time-dependent functions have overlapping time ranges."""

    def __init__(  # noqa: PLR0913
        self,
        dag_key: str,
        function_name_1: str,
        start_1: date,
        end_1: date,
        function_name_2: str,
        start_2: date,
        end_2: date,
    ):
        super().__init__(
            f"Conflicting functions for key {dag_key!r}: "
            f"{function_name_1!r} ({start_1} to {end_1}) vs. "
            f"{function_name_2!r} ({start_2} to {end_2})."
        )


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
