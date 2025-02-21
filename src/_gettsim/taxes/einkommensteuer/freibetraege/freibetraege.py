"""Tax allowances."""


def freibeträge_y_sn(
    einkommensteuer__freibetraege__sonderausgaben__betrag_y_sn: float,
    einkommensteuer__einkommen__vorsorgeaufwand__betrag_y_sn: float,
    freibeträge_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    einkommensteuer__freibetraege__sonderausgaben__betrag_y_sn
        See :func:
        `einkommensteuer__freibetraege__sonderausgaben__betrag_y_sn`.
    einkommensteuer__einkommen__vorsorgeaufwand__betrag_y_sn
        See :func:`einkommensteuer__einkommen__vorsorgeaufwand__betrag_y_sn`.
    freibeträge_ind_y_sn
        See :func:`freibeträge_ind_y_sn`.

    Returns
    -------

    """
    out = (
        einkommensteuer__freibetraege__sonderausgaben__betrag_y_sn
        + einkommensteuer__einkommen__vorsorgeaufwand__betrag_y_sn
        + freibeträge_ind_y_sn
    )

    return out


def freibeträge_ind_y(
    einkommensteuer__freibetraege__pauschbetrag_behinderung__betrag_y: float,
    einkommensteuer__freibetraege__altersfreibetrag__betrag_y: float,
    einkommensteuer__freibetraege__alleinerziehend__betrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    #ToDo: Check whether these columns are really calculated at the individual level.
    Parameters
    ----------

    einkommensteuer__freibetraege__pauschbetrag_behinderung__betrag_y
        See :func:
        `einkommensteuer__freibetraege__pauschbetrag_behinderung__betrag_y`.
    einkommensteuer__freibetraege__altersfreibetrag__betrag_y
        See :func:
        `einkommensteuer__freibetraege__altersfreibetrag__betrag_y`.
    einkommensteuer__freibetraege__alleinerziehend__betrag_y
        See :func:`einkommensteuer__freibetraege__alleinerziehend__betrag_y`.

    Returns
    -------

    """
    out = (
        einkommensteuer__freibetraege__pauschbetrag_behinderung__betrag_y
        + einkommensteuer__freibetraege__altersfreibetrag__betrag_y
        + einkommensteuer__freibetraege__alleinerziehend__betrag_y
    )
    return out
