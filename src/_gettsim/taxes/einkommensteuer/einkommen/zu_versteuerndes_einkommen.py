"""Taxable income."""

from _gettsim.functions.policy_function import policy_function


@policy_function(params_key_for_rounding="eink_st")
def zu_versteuerndes_einkommen_y_sn(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn: float,
    kinderfreibetrag_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Parameters
    ----------
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        See :func:`zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn`.
    zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn
        See :func:`zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn`.
    kinderfreibetrag_günstiger_sn
        See :func:`kinderfreibetrag_günstiger_sn`.

    Returns
    -------

    """
    if kinderfreibetrag_günstiger_sn:
        out = zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
    else:
        out = zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn

    return out


@policy_function
def zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn(
    zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn: float,
    einkommensteuer__freibetraege__kinderfreibetrag_y_sn: float,
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Parameters
    ----------
    zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn
        See :func:`zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn`.
    einkommensteuer__freibetraege__kinderfreibetrag_y_sn
        See :func:`einkommensteuer__freibetraege__kinderfreibetrag_y_sn`.

    Returns
    -------

    """

    out = (
        zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn
        - einkommensteuer__freibetraege__kinderfreibetrag_y_sn
    )
    return max(out, 0.0)


@policy_function
def zu_versteuerndes_einkommen_ohne_kinderfreibetrag_y_sn(
    bruttoeinkommen_y_sn: float,
    einkommensteuer_freibetraege_betrag_y_sn: float,
) -> float:
    """Calculate taxable income without child allowance on Steuernummer level.

    Parameters
    ----------
    bruttoeinkommen_y_sn
        See :func:`bruttoeinkommen_y_sn`.
    einkommensteuer_freibetraege_betrag_y_sn
        See :func:`einkommensteuer_freibetraege_betrag_y_sn`.


    Returns
    -------

    """
    out = bruttoeinkommen_y_sn - einkommensteuer_freibetraege_betrag_y_sn

    return max(out, 0.0)
