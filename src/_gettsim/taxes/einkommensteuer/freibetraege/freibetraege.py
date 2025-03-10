"""Tax allowances."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def betrag_y_sn(
    sonderausgaben_y_sn: float,
    einkommensteuer__einkommen__vorsorgeaufwand_y_sn: float,
    betrag_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    sonderausgaben_y_sn
        See :func:`sonderausgaben_y_sn`.
    einkommensteuer__einkommen__vorsorgeaufwand_y_sn
        See :func:`einkommensteuer__einkommen__vorsorgeaufwand_y_sn`.
    betrag_ind_y_sn
        See :func:`betrag_ind_y_sn`.

    Returns
    -------

    """
    out = (
        sonderausgaben_y_sn
        + einkommensteuer__einkommen__vorsorgeaufwand_y_sn
        + betrag_ind_y_sn
    )

    return out


@policy_function()
def betrag_ind_y(
    pauschbetrag_behinderung_y: float,
    altersfreibetrag__betrag_y: float,
    alleinerziehend__betrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    #ToDo: Check whether these columns are really calculated at the individual level.
    Parameters
    ----------

    pauschbetrag_behinderung_y
        See :func:`pauschbetrag_behinderung_y`.
    altersfreibetrag__betrag_y
        See :func:`altersfreibetrag__betrag_y`.
    alleinerziehend__betrag_y
        See :func:`alleinerziehend__betrag_y`.

    Returns
    -------

    """
    out = (
        pauschbetrag_behinderung_y
        + altersfreibetrag__betrag_y
        + alleinerziehend__betrag_y
    )
    return out
