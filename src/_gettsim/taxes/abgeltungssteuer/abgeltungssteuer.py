"""Taxes on capital income (Abgeltungssteuer)."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2009-01-01")
def betrag_y_sn(
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn: float,
    abgelt_st_params: dict,
) -> float:
    """Abgeltungssteuer on Steuernummer level.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return (
        abgelt_st_params["satz"]
        * einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
    )
