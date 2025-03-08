"""Alimony payments (Unterhalt)."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def kind_zahlbetrag_m(
    kind_anspruch_m: float,
    kindergeld__betrag_m: float,
    unterhalt_params: dict,
    demographics__kind: bool,
) -> float:
    """Monthly actual child alimony payments to be received after deductions.

    Parameters
    ----------
    kind_anspruch_m
        See basic input variable :ref:`kind_anspruch_m <kind_anspruch_m>`.
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.

    Returns
    -------
    """
    if demographics__kind:
        abzugsrate = unterhalt_params["abzugsrate_kindergeld"]["kind"]
    else:
        abzugsrate = unterhalt_params["abzugsrate_kindergeld"]["erwachsener"]

    return kind_anspruch_m - abzugsrate * kindergeld__betrag_m
