from __future__ import annotations

import inspect
from collections.abc import Callable


class GroupingFunction(Callable):
    """
    A function that computes endogenous grouping IDs.

    Parameters
    ----------
    function:
        The grouping function.
    """

    def __init__(
        self,
        *,
        function: Callable,
    ):
        self.function = function

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


def grouping_function() -> GroupingFunction:
    """
    Decorator that creates a grouping function from a function.
    """

    def decorator(func: Callable) -> GroupingFunction:
        return GroupingFunction(func)

    return decorator
