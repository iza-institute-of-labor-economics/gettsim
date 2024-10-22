from __future__ import annotations

from typing import Callable

from _gettsim.functions.policy_function import PolicyFunction


class DerivedFunction(PolicyFunction):
    """
    A function that is derived from other functions.

    Parameters
    ----------
    function:
        The function to wrap. Argument values of the `@policy_info` are reused unless
        explicitly overwritten.
    function_name:
        The name of the function in the DAG
    derived_from:
        The function from which the new function is derived. If the function is derived
        from a data column, this may be None.
    """

    def __init__(  # noqa: PLR0913
            self,
            function: Callable,
            function_name: str,
            *,
            derived_from: PolicyFunction | None = None,
    ):
        super().__init__(
            function,
            module_name=derived_from.module_name if derived_from is not None else "",
            function_name=function_name,
            start_date=derived_from.start_date if derived_from is not None else None,
            end_date=derived_from.end_date if derived_from is not None else None,
            params_key_for_rounding=None,
            skip_vectorization=True,
        )

        self.derived_from: PolicyFunction | str = derived_from
