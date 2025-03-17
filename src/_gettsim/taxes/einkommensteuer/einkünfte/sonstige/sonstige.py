"""Sonstige Einkünfte."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y_sn(
    einkommensteuer__einnahmen__sonstige_m: float,
) -> float:
    raise NotImplementedError("Not implemented yet.")
