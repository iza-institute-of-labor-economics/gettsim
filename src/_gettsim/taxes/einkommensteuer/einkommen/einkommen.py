"""Taxable income."""

from _gettsim.functions.policy_function import policy_function


@policy_function(params_key_for_rounding="eink_st")
def zu_verst_eink_y_sn(
    _zu_verst_eink_mit_kinderfreib_y_sn: float,
    _zu_verst_eink_ohne_kinderfreib_y_sn: float,
    kinderfreib_günstiger_sn: bool,
) -> float:
    """Calculate taxable income on Steuernummer level.

    Parameters
    ----------
    _zu_verst_eink_mit_kinderfreib_y_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_y_sn`.
    _zu_verst_eink_ohne_kinderfreib_y_sn
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_sn`.
    kinderfreib_günstiger_sn
        See :func:`kinderfreib_günstiger_sn`.

    Returns
    -------

    """
    if kinderfreib_günstiger_sn:
        out = _zu_verst_eink_mit_kinderfreib_y_sn
    else:
        out = _zu_verst_eink_ohne_kinderfreib_y_sn

    return out


def _zu_verst_eink_mit_kinderfreib_y_sn(
    _zu_verst_eink_ohne_kinderfreib_y_sn: float,
    einkommensteuer__freibetraege__kinderfreibetrag__betrag_y_sn: float,
) -> float:
    """Calculate taxable income with child allowance on Steuernummer level.

    Parameters
    ----------
    _zu_verst_eink_ohne_kinderfreib_y_sn
        See :func:`_zu_verst_eink_ohne_kinderfreib_y_sn`.
    einkommensteuer__freibetraege__kinderfreibetrag__betrag_y_sn
        See :func:
        `einkommensteuer__freibetraege__kinderfreibetrag__betrag_y_sn`.

    Returns
    -------

    """

    out = (
        _zu_verst_eink_ohne_kinderfreib_y_sn
        - einkommensteuer__freibetraege__kinderfreibetrag__betrag_y_sn
    )
    return max(out, 0.0)


def _zu_verst_eink_ohne_kinderfreib_y_sn(
    einkommensteuer__einkommen__bruttoeinkommen__betrag_y_sn: float,
    freibeträge_y_sn: float,
) -> float:
    """Calculate taxable income without child allowance on Steuernummer level.

    Parameters
    ----------
    einkommensteuer__einkommen__bruttoeinkommen__betrag_y_sn
        See :func:`einkommensteuer__einkommen__bruttoeinkommen__betrag_y_sn`.
    freibeträge_y_sn
        See :func:`freibeträge_y_sn`.


    Returns
    -------

    """
    out = einkommensteuer__einkommen__bruttoeinkommen__betrag_y_sn - freibeträge_y_sn

    return max(out, 0.0)
