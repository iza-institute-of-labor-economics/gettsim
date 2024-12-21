"""Alimony payments (Unterhalt)."""


def kind_unterh_zahlbetr_m(
    kind_unterh_anspr_m: float,
    kindergeld_m: float,
    unterhalt_params: dict,
    kind: bool,
) -> float:
    """Monthly actual child alimony payments to be received after deductions.

    Parameters
    ----------
    kind_unterh_anspr_m
        See basic input variable :ref:`kind_unterh_anspr_m <kind_unterh_anspr_m>`.
    kindergeld_m
        See :func:`kindergeld_m`.
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

    return kind_unterh_anspr_m - abzugsrate * kindergeld_m
