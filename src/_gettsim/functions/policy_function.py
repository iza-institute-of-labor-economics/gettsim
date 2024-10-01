from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from datetime import date
from typing import Any, TypeVar

import numpy

T = TypeVar("T")


class PolicyFunction(Callable):
    """
    A function that computes an output vector based on some input vectors and/or
    parameters.

    Parameters
    ----------
    function:
        The function to wrap. Argument values of the `@policy_info` are reused unless
        explicitly overwritten.
    module_name:
        The name of the module where the function is defined.
    function_name:
        The name of the function in the DAG
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
        module_name: str = "",
        function_name: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        params_key_for_rounding: str | None = None,
        skip_vectorization: bool | None = None,
    ):
        info: dict[str, Any] = getattr(function, "__info__", {})

        self.skip_vectorization: bool = _first_not_none(
            skip_vectorization, info.get("skip_vectorization"), False
        )

        self.function = (
            function if self.skip_vectorization else _vectorize_func(function)
        )
        self.module_name = module_name

        self.name_in_dag: str = _first_not_none(
            function_name,
            info.get("name_in_dag"),
            function.__name__,
        )

        self.start_date: date = _first_not_none(
            start_date,
            info.get("start_date"),
            date(1, 1, 1),
        )

        self.end_date: date = _first_not_none(
            end_date,
            info.get("end_date"),
            date(9999, 12, 31),
        )

        self.params_key_for_rounding: str | None = _first_not_none_or_none(
            params_key_for_rounding,
            info.get("params_key_for_rounding"),
        )

        # Expose the signature of the wrapped function for dependency resolution
        self.__annotations__ = function.__annotations__
        self.__module__ = function.__module__
        self.__name__ = function.__name__
        self.__signature__ = inspect.signature(self.function)

        # Temporary solution until the rest of the interface is updated
        if hasattr(function, "__info__"):
            self.__info__ = function.__info__

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

    def is_active_at_date(self, date: date) -> bool:
        """Check if the function is active at a given date."""
        return self.start_date <= date <= self.end_date


def _vectorize_func(func: Callable) -> Callable:
    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func


def _first_not_none(*values: T) -> T:
    """
    Return the first value that is not None or raise if all values are None.

    Parameters
    ----------
    values:
        The values to check.

    Raises
    ------
    ValueError:
        If all values are None.
    """
    for value in values:
        if value is not None:
            return value

    raise ValueError("All values are None.")


def _first_not_none_or_none(*values: T) -> T | None:
    """
    Return the first value that is not None or None if all values are None.

    Parameters
    ----------
    values:
        The values to check.
    """
    for value in values:
        if value is not None:
            return value

    return None
