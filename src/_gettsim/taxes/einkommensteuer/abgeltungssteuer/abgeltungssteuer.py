"""Taxes on capital income (Abgeltungssteuer)."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2009-01-01")
def betrag_y_sn(
    zu_versteuerndes_einkommen_y_sn: float,
    abgelt_st_params: dict,
) -> float:
    """Abgeltungssteuer on Steuernummer level.

    Parameters
    ----------
    zu_versteuerndes_einkommen_y_sn
        See :func:`zu_versteuerndes_einkommen_y_sn`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return abgelt_st_params["satz"] * zu_versteuerndes_einkommen_y_sn


@policy_function(start_date="2009-01-01")
def zu_versteuerndes_einkommen_y_sn(
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y_sn: float,
    einkommensteuer__anzahl_personen_sn: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Taxable capital income for Abgeltungssteuer.

    TODO(@MImmesberger): Find out whether Sparerpauschbetrag and
    Sparer-Werbungskostenpauschbetrag are transferable to partner with same sn_id.
    https://github.com/iza-institute-of-labor-economics/gettsim/issues/843

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y_sn
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_y_sn
        - einkommensteuer__anzahl_personen_sn
        * (
            eink_st_abzuege_params["sparerpauschbetrag"]
            + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
        )
    )
    return max(out, 0.0)
