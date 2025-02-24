"""Taxable income."""

from _gettsim.functions.policy_function import policy_function


@policy_function(params_key_for_rounding="eink_st")
def einkommen_y_sn(
    _einkommen_mit_kinderfreib_y_sn: float,
    _einkommen_ohne_kinderfreib_y_sn: float,
    kinderfreib_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Parameters
    ----------
    _einkommen_mit_kinderfreib_y_sn
        See :func:`_einkommen_mit_kinderfreib_y_sn`.
    _einkommen_ohne_kinderfreib_y_sn
        See :func:`_einkommen_ohne_kinderfreib_y_sn`.
    kinderfreib_günstiger_sn
        See :func:`kinderfreib_günstiger_sn`.

    Returns
    -------

    """
    if kinderfreib_günstiger_sn:
        out = _einkommen_mit_kinderfreib_y_sn
    else:
        out = _einkommen_ohne_kinderfreib_y_sn

    return out


def _einkommen_mit_kinderfreib_y_sn(
    _einkommen_ohne_kinderfreib_y_sn: float,
    einkommensteuer__freibetraege__kinderfreibetrag_y_sn: float,
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Parameters
    ----------
    _einkommen_ohne_kinderfreib_y_sn
        See :func:`_einkommen_ohne_kinderfreib_y_sn`.
    einkommensteuer__freibetraege__kinderfreibetrag_y_sn
        See :func:
        `einkommensteuer__freibetraege__kinderfreibetrag_y_sn`.

    Returns
    -------

    """

    out = (
        _einkommen_ohne_kinderfreib_y_sn
        - einkommensteuer__freibetraege__kinderfreibetrag_y_sn
    )
    return max(out, 0.0)


def _einkommen_ohne_kinderfreib_y_sn(
    einkommensteuer__einkommen__bruttoeinkommen_y_sn: float,
    einkommensteuer_freibetraege_betrag_y_sn: float,
) -> float:
    """Calculate taxable income without child allowance on Steuernummer level.

    Parameters
    ----------
    einkommensteuer__einkommen__bruttoeinkommen_y_sn
        See :func:`einkommensteuer__einkommen__bruttoeinkommen_y_sn`.
    einkommensteuer_freibetraege_betrag_y_sn
        See :func:`einkommensteuer_freibetraege_betrag_y_sn`.


    Returns
    -------

    """
    out = (
        einkommensteuer__einkommen__bruttoeinkommen_y_sn
        - einkommensteuer_freibetraege_betrag_y_sn
    )

    return max(out, 0.0)
