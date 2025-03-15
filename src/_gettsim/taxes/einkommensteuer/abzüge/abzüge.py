"""Tax allowances."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y_sn(
    sonderausgaben_y_sn: float,
    vorsorgeaufwendungen_y_sn: float,
    betrag_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    sonderausgaben_y_sn
        See :func:`sonderausgaben_y_sn`.
    vorsorgeaufwendungen_y_sn
        See :func:`vorsorgeaufwendungen_y_sn`.
    betrag_ind_y_sn
        See :func:`betrag_ind_y_sn`.

    Returns
    -------

    """
    out = sonderausgaben_y_sn + vorsorgeaufwendungen_y_sn + betrag_ind_y_sn

    return out


@policy_function()
def betrag_ind_y(
    pauschbetrag_behinderung_y: float,
    alleinerziehend_betrag_y: float,
    altersfreibetrag_y: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    Parameters
    ----------

    pauschbetrag_behinderung_y
        See :func:`pauschbetrag_behinderung_y`.
    alleinerziehend_betrag_y
        See :func:`alleinerziehend_betrag_y`.
    altersfreibetrag_y
        See :func:`altersfreibetrag_y`.

    Returns
    -------

    """
    out = pauschbetrag_behinderung_y + alleinerziehend_betrag_y + altersfreibetrag_y
    return out
