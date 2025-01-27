from __future__ import annotations

import functools
import inspect
import re
from collections.abc import Callable
from datetime import date
from typing import TypeVar

import numpy

T = TypeVar("T")


class PolicyFunction(Callable):
    """
    A function that computes an output vector based on some input vectors and/or
    parameters.

    Parameters
    ----------
    function:
        The function to wrap. Argument values of the `@policy_function` are reused
        unless explicitly overwritten.
    leaf_name:
        The leaf name of the function in the functions tree.
    start_date:
        The date from which the function is active (inclusive).
    end_date:
        The date until which the function is active (inclusive).
    params_key_for_rounding:
        The key in the params dictionary that should be used for rounding.
    skip_vectorization:
        Whether the function should be vectorized.
    """

    def __init__(  # noqa: PLR0913
        self,
        function: Callable,
        *,
        leaf_name: str | None = None,
        start_date: date = "0001-01-01",
        end_date: date = "9999-12-31",
        params_key_for_rounding: str | None = None,
        skip_vectorization: bool | None = False,
    ):
        self.skip_vectorization: bool = skip_vectorization
        self.function = (
            function if self.skip_vectorization else _vectorize_func(function)
        )
        self.leaf_name: str = leaf_name if leaf_name else function.__name__
        self.qualified_name: str = None
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.params_key_for_rounding: str | None = params_key_for_rounding

        # Expose the signature of the wrapped function for dependency resolution
        self.__annotations__ = function.__annotations__
        self.__module__ = function.__module__
        self.__name__ = function.__name__
        self.__signature__ = inspect.signature(self.function)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def dependencies(self) -> set[str]:
        """The names of input variables that the function depends on."""
        return set(inspect.signature(self).parameters)

    @property
    def original_function_name(self) -> str:
        """The name of the wrapped function."""
        return self.function.__name__

    def set_qualified_name(self, qualified_name: str) -> None:
        """Set the qualified name of the function in the functions tree."""
        self.qualified_name = qualified_name

    def is_active_at_date(self, date: date) -> bool:
        """Check if the function is active at a given date."""
        return self.start_date <= date <= self.end_date


def policy_function(
    *,
    start_date: str = "0001-01-01",
    end_date: str = "9999-12-31",
    leaf_name: str | None = None,
    params_key_for_rounding: str | None = None,
    skip_vectorization: bool = False,
) -> PolicyFunction:
    """
    Decorator that wraps a callable into a `PolicyFunction`.

    **Dates active (start_date, end_date, leaf_name):**

    Specifies that a PolicyFunction is only active between two dates, `start` and `end`.
    By using the `leaf_name` argument, you can specify a different name for the
    PolicyFunction in the functions tree.

    Note that even if you use this decorator with the `leaf_name` argument, you must
    ensure that the function name is unique in the file where it is defined. Otherwise,
    the function would be overwritten by the last function with the same name.

    **Rounding spec (params_key_for_rounding):**

    Adds the location of the rounding specification to a PolicyFunction.

    Parameters
    ----------
    start_date
        The start date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    end_date
        The end date (inclusive) in the format YYYY-MM-DD (part of ISO 8601).
    leaf_name
        The name that should be used as the PolicyFunction's leaf name in the DAG. If
        omitted, we use the name of the function as defined.
    params_key_for_rounding
        Key of the parameters dictionary where rounding specifications are found. For
        functions that are not user-written this is just the name of the respective
        .yaml file.
    skip_vectorization
        Whether the function is already vectorized and, thus, should not be vectorized
        again.

    Returns
    -------
    PolicyFunction
        A PolicyFunction object.
    """

    _validate_dashed_iso_date(start_date)
    _validate_dashed_iso_date(end_date)

    start_date = date.fromisoformat(start_date)
    end_date = date.fromisoformat(end_date)

    _validate_date_range(start_date, end_date)

    def inner(func: Callable) -> PolicyFunction:
        return PolicyFunction(
            func,
            leaf_name=leaf_name if leaf_name else func.__name__,
            start_date=start_date,
            end_date=end_date,
            params_key_for_rounding=params_key_for_rounding,
            skip_vectorization=skip_vectorization,
        )

    return inner


_dashed_iso_date = re.compile(r"\d{4}-\d{2}-\d{2}")


def _validate_dashed_iso_date(date_str: str):
    if not _dashed_iso_date.match(date_str):
        raise ValueError(f"Date {date_str} does not match the format YYYY-MM-DD.")


def _validate_date_range(start: date, end: date):
    if start > end:
        raise ValueError(f"The start date {start} must be before the end date {end}.")


def _vectorize_func(func: Callable) -> Callable:
    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func
