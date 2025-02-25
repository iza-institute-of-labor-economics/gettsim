"""Alimony payments (Unterhalt)."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def betrag_m(
    kind_unterh_anspr_m: float,
    kindergeld__betrag_m: float,
    unterhalt_params: dict,
    kind: bool,
) -> float:
    """Monthly actual child alimony payments to be received after deductions.

    Parameters
    ----------
    kind_unterh_anspr_m
        See basic input variable :ref:`kind_unterh_anspr_m <kind_unterh_anspr_m>`.
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------
    """
    if kind:
        abzugsrate = unterhalt_params["abzugsrate_kindergeld"]["kind"]
    else:
        abzugsrate = unterhalt_params["abzugsrate_kindergeld"]["erwachsener"]

    return kind_unterh_anspr_m - abzugsrate * kindergeld__betrag_m
