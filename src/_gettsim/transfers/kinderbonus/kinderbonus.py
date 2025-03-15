"""Kinderbonus."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2020-01-01", end_date="2021-12-31")
def betrag_y(kindergeld__betrag_y: float, kindergeld_params: dict) -> float:
    """Calculate Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    Parameters
    ----------
    kindergeld__betrag_y
        See :func:`kindergeld__betrag_y`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kinderbonus parameter is specified on the yearly level
    # kindergeld__betrag_y is zero for all adults
    if kindergeld__betrag_y > 0:
        out = kindergeld_params["kinderbonus"]
    else:
        out = 0.0

    return out
