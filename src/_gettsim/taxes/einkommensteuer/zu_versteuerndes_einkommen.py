"""Taxable income."""

from _gettsim.function_types import policy_function


@policy_function(params_key_for_rounding="eink_st")
def zu_versteuerndes_einkommen_y_sn(
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn: float,
    einkommensteuer__gesamteinkommen_y: float,
    kinderfreibetrag_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Parameters
    ----------
    zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
        See :func:`zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn`.
    einkommensteuer__gesamteinkommen_y
        See :func:`einkommensteuer__gesamteinkommen_y`.
    kinderfreibetrag_günstiger_sn
        See :func:`kinderfreibetrag_günstiger_sn`.

    Returns
    -------

    """
    if kinderfreibetrag_günstiger_sn:
        out = zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn
    else:
        out = einkommensteuer__gesamteinkommen_y

    return out


@policy_function()
def zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn(
    einkommensteuer__gesamteinkommen_y: float,
    kinderfreibetrag_y_sn: float,
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Parameters
    ----------
    einkommensteuer__gesamteinkommen_y
        See :func:`einkommensteuer__gesamteinkommen_y`.
    kinderfreibetrag_y_sn
        See :func:`kinderfreibetrag_y_sn`.

    Returns
    -------

    """

    out = einkommensteuer__gesamteinkommen_y - kinderfreibetrag_y_sn
    return max(out, 0.0)
