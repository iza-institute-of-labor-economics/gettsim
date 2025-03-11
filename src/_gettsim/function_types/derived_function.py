from __future__ import annotations

from typing import TYPE_CHECKING

from _gettsim.function_types import PolicyFunction

if TYPE_CHECKING:
    from collections.abc import Callable


class DerivedFunction(PolicyFunction):
    """
    A function that is derived from another via aggregation, time conversion, etc.

    Parameters
    ----------
    function:
        The function to wrap. Argument values of the `@policy_function` are reused
        unless explicitly overwritten.
    leaf_name:
        The leaf name of the function in the functions tree.
    derived_from:
        The function from which the new function is derived. If the function is derived
        from a data column, this should be the column name.
    """

    def __init__(
        self,
        *,
        function: Callable,
        leaf_name: str,
        derived_from: PolicyFunction | str | tuple[str, str],
    ):
        super().__init__(
            function=function,
            leaf_name=leaf_name,
            start_date=(
                derived_from.start_date
                if isinstance(derived_from, PolicyFunction)
                else None
            ),
            end_date=(
                derived_from.end_date
                if isinstance(derived_from, PolicyFunction)
                else None
            ),
            params_key_for_rounding=None,
            skip_vectorization=True,
        )

        self.derived_from = derived_from
