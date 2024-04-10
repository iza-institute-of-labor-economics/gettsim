import inspect
import re
import textwrap
from collections.abc import Callable
from datetime import date

from _gettsim.config import SUPPORTED_GROUPINGS


class KeyErrorMessage(str):
    """Subclass str to allow for line breaks in KeyError messages."""

    __slots__ = ()

    def __repr__(self):
        return str(self)


TIME_DEPENDENT_FUNCTIONS: dict[str, list[Callable]] = {}


def policy_info(
    *,
    start_date: str = "0001-01-01",
    end_date: str = "9999-12-31",
    name_in_dag: str | None = None,
    rounding_key: str | None = None,
) -> Callable:
    """
    A decorator to attach additional information to a policy function.

    **Dates active (start, end, change_name):**

    Specifies that a function is only active between two dates, `start` and `end`. By
    using the `change_name` argument, you can specify a different name for the function
    in the DAG.

    Note that even if you use this decorator with the `change_name` argument, you must
    ensure that the function name is unique in the file where it is defined. Otherwise,
    the function would be overwritten by the last function with the same name.

    **Rounding spec (rounding_key):**

    Adds the location of the rounding specification to a function.

    Parameters
    ----------
    start_date
        The start date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    end_date
        The end date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    name_in_dag
        The name that should be used as the key for the function in the DAG.
        If omitted, we use the name of the function as defined.
    rounding_key
        Key of the parameters dictionary where rounding specifications are found. For
        functions that are not user-written this is just the name of the respective
        .yaml file.

    Returns
    -------
        The function with attributes __info__["dates_active_start"],
        __info__["dates_active_end"], __info__["dates_active_dag_key"], and
        __info__["rounding_params_key"].
    """

    _validate_dashed_iso_date(start_date)
    _validate_dashed_iso_date(end_date)

    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)

    _validate_date_range(start_date, end_date)

    def inner(func: Callable) -> Callable:
        dag_key = name_in_dag if name_in_dag else func.__name__

        _check_for_conflicts_in_time_dependent_functions(
            dag_key, func.__name__, start_date, end_date
        )

        # Remember data from decorator
        if not hasattr(func, "__info__"):
            func.__info__ = {}
        func.__info__["dates_active_start"] = start_date
        func.__info__["dates_active_end"] = end_date
        func.__info__["dates_active_dag_key"] = dag_key
        if rounding_key is not None:
            func.__info__["rounding_params_key"] = rounding_key

        # Register time-dependent function
        if dag_key not in TIME_DEPENDENT_FUNCTIONS:
            TIME_DEPENDENT_FUNCTIONS[dag_key] = []
        TIME_DEPENDENT_FUNCTIONS[dag_key].append(func)

        return func

    return inner


_dashed_iso_date = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_dashed_iso_date(date_str: str):
    if not _dashed_iso_date.match(date_str):
        raise ValueError(f"Date {date_str} does not match the format YYYY-MM-DD.")


def _validate_date_range(start: date, end: date):
    if start > end:
        raise ValueError(f"The start date {start} must be before the end date {end}.")


def _check_for_conflicts_in_time_dependent_functions(
    dag_key: str, function_name: str, start: date, end: date
):
    """
    Raises an error if a different time-dependent function has already been registered
    for the given dag_key and their date ranges overlap.
    """

    if dag_key not in TIME_DEPENDENT_FUNCTIONS:
        return

    for f in TIME_DEPENDENT_FUNCTIONS[dag_key]:
        # A function is not conflicting with itself. We compare names instead of
        # identities since functions might get wrapped, which would change their
        # identity but not their name.
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
            f"{function_name_2!r} ({start_2} to {end_2}).\n\n"
            f"Overlapping from {max(start_1, start_2)} to {min(end_1, end_2)}."
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

    Parameters
    ----------
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

    argument_names_without_defaults = [
        p for p in parameters if parameters[p].default == parameters[p].empty
    ]

    return argument_names_without_defaults


def remove_group_suffix(col):
    out = col
    for g in SUPPORTED_GROUPINGS:
        out = out.removesuffix(f"_{g}")

    return out
