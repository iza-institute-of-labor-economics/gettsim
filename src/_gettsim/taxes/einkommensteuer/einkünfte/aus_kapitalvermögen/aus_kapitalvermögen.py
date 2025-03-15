"""Einkünfte aus Kapitalvermögen."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y(
    einkommen__kapitaleinnahmen_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate taxable capital income on Steuernummer level.

    Parameters
    ----------
    einkommen__kapitaleinnahmen_y
        See :func:`einkommen__kapitaleinnahmen_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = einkommen__kapitaleinnahmen_y - (
        eink_st_abzuege_params["sparerpauschbetrag"]
        + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)
