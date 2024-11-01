from __future__ import annotations

from typing import TYPE_CHECKING

from _gettsim.functions.policy_function import PolicyFunction

if TYPE_CHECKING:
    from collections.abc import Callable


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
        from a data column, this should be the column name.
    """

    def __init__(
        self,
        function: Callable,
        function_name: str,
        *,
        derived_from: PolicyFunction | str | tuple[str, str],
    ):
        super().__init__(
            function,
            module_name=derived_from.module_name if isinstance(derived_from, PolicyFunction) else "",
            function_name=function_name,
            start_date=derived_from.start_date if isinstance(derived_from, PolicyFunction) else None,
            end_date=derived_from.end_date if isinstance(derived_from, PolicyFunction) else None,
            params_key_for_rounding=None,
            skip_vectorization=True,
        )

        self.derived_from = derived_from
