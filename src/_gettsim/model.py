from __future__ import annotations

import inspect
from collections.abc import Callable
from datetime import date

from _gettsim.functions_loader import _vectorize_func


class PolicyFunction(Callable):
    """
    A function that computes an output vector based on some input vectors.
    """

    # Default values are set to None and overwritten in the body here, so callers don't
    # have to repeat default values for functions with the @policy_info decorator.
    # Instead, they can just always pass None.
    def __init__(  # noqa: PLR0913
        self,
        function: Callable,
        module_name: str,
        function_name: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        params_key_for_rounding: str | None = None,
        skip_vectorization: bool | None = None,
    ):
        self.function = function if skip_vectorization else _vectorize_func(function)
        self.module_name = module_name
        self.function_name = function_name or function.__name__
        self.start_date = start_date or date(1, 1, 1)
        self.end_date = end_date or date(9999, 12, 31)
        self.params_key_for_rounding = params_key_for_rounding

        # Expose the signature of the wrapped function for dependency resolution
        self.__signature__ = inspect.signature(self.function)

        # Temporary solution until the rest of the interface is updated
        if hasattr(function, "__info__"):
            self.__info__ = function.__info__


    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    @property
    def dependencies(self) -> set[str]:
        return set(inspect.signature(self).parameters)

    def is_active_at_date(self, date: date) -> bool:
        return self.start_date <= date <= self.end_date
