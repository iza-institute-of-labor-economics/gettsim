"""Alimony payments (Unterhalt)."""

from _gettsim.function_types import policy_function


@policy_function()
def kind_festgelegter_zahlbetrag_m(
    anspruch_m: float,
    kindergeld__betrag_m: float,
    unterhalt_params: dict,
    demographics__kind: bool,
) -> float:
    """Monthly actual child alimony payments to be received by the child after
    deductions.

    Parameters
    ----------
    anspruch_m
        See basic input variable :ref:`anspruch_m <anspruch_m>`.
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

    return anspruch_m - abzugsrate * kindergeld__betrag_m
