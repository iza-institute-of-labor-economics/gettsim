from __future__ import annotations

import inspect
from collections.abc import Callable


class GroupByFunction(Callable):
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
        leaf_name: str | None = None,
    ):
        self.function = function
        self.leaf_name = leaf_name if leaf_name else function.__name__

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


def group_by_function() -> GroupByFunction:
    """
    Decorator that creates a groupby function from a function.
    """

    def decorator(func: Callable) -> GroupByFunction:
        return GroupByFunction(function=func)

    return decorator
