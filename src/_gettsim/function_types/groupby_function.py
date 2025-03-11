from __future__ import annotations

import inspect
from collections.abc import Callable


class GroupbyFunction(Callable):
    """
    A function that computes endogenous groupby IDs.

    Parameters
    ----------
    function:
        The groupby function.
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


def groupby_function() -> GroupbyFunction:
    """
    Decorator that creates a groupby function from a function.
    """

    def decorator(func: Callable) -> GroupbyFunction:
        return GroupbyFunction(function=func)

    return decorator
