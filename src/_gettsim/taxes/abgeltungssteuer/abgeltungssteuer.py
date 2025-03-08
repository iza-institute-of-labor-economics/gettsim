"""Taxes on capital income (Abgeltungssteuer)."""

from _gettsim.functions.policy_function import policy_function


@policy_function(start_date="2009-01-01")
def betrag_y_sn(
    zu_versteuerndes_kapitaleinkommen_y_sn: float, abgelt_st_params: dict
) -> float:
    """Abgeltungssteuer on Steuernummer level.

    Parameters
    ----------
    zu_versteuerndes_kapitaleinkommen_y_sn
        See :func:`zu_versteuerndes_kapitaleinkommen_y_sn`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return abgelt_st_params["satz"] * zu_versteuerndes_kapitaleinkommen_y_sn


@policy_function()
def zu_versteuerndes_kapitaleinkommen_y_sn(
    kapitaleink_brutto_y_sn: float,
    demographic_vars__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate taxable capital income on Steuernummer level.

    Parameters
    ----------
    kapitaleink_brutto_y_sn
        See :func:`kapitaleink_brutto_y_sn`.
    demographic_vars__anzahl_personen_sn
        See :func:`demographic_vars__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = kapitaleink_brutto_y_sn - demographic_vars__anzahl_personen_sn * (
        eink_st_abzuege_params["sparerpauschbetrag"]
        + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)
