"""Einkünfte aus Selbstständiger Arbeit."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y_sn(
    einkommen__aus_selbstständigkeit_y: float,
) -> float:
    raise NotImplementedError("Not implemented yet.")
