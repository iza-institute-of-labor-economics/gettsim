from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import TYPE_CHECKING, TypeVar

import numpy

if TYPE_CHECKING:
    from datetime import date

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
        leaf_name: str,
        start_date: date,
        end_date: date,
        params_key_for_rounding: str | None,
        skip_vectorization: bool | None,
    ):
        self.skip_vectorization: bool = skip_vectorization
        self.function = (
            function if self.skip_vectorization else _vectorize_func(function)
        )
        self.leaf_name: str = leaf_name
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


def _vectorize_func(func: Callable) -> Callable:
    # What should work once that Jax backend is fully supported
    signature = inspect.signature(func)
    func_vec = numpy.vectorize(func)

    @functools.wraps(func)
    def wrapper_vectorize_func(*args, **kwargs):
        return func_vec(*args, **kwargs)

    wrapper_vectorize_func.__signature__ = signature

    return wrapper_vectorize_func
