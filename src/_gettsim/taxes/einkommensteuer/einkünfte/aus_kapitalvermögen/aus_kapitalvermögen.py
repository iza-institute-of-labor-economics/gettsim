"""Einkünfte aus Kapitalvermögen."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y(
    kapitalerträge_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate taxable capital income on Steuernummer level.

    Parameters
    ----------
    kapitalerträge_y
        See :func:`kapitalerträge_y`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = kapitalerträge_y - (
        eink_st_abzuege_params["sparerpauschbetrag"]
        + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)
