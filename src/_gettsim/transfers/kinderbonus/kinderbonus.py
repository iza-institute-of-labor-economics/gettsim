"""Kinderbonus."""


def betrag_m(kindergeld__betrag_m: float, kindergeld_params: dict) -> float:
    """Calculate Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    Parameters
    ----------
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kinderbonus parameter is specified on the yearly level
    # kindergeld__betrag_m is zero for all adults
    if kindergeld__betrag_m > 0:
        out = kindergeld_params["kinderbonus"] / 12
    else:
        out = 0.0

    return out
