def kinderbonus_m(
    kinderfreib_günstiger_tu: bool,
    kinderbonus_basis_m: float,
) -> float:
    """Calculate Kinderbonus for an individual child after Günstigerprüfung.

    (one-time payment, non-allowable against transfer payments).

    Parameters
    ----------
    kinderfreib_günstiger_tu
        See :func:`kinderfreib_günstiger_tu`.
    kinderbonus_basis_m
        See :func:`kinderbonus_basis_m`.

    Returns
    -------

    """
    out = 0.0 if kinderfreib_günstiger_tu else kinderbonus_basis_m

    return out


def kinderbonus_basis_m(kindergeld_basis_m: float, kindergeld_params: dict) -> float:
    """Calculate potential Kinderbonus for an individual child.

    (one-time payment, non-allowable against transfer payments)

    Parameters
    ----------
    kindergeld_basis_m
        See :func:`kindergeld_basis_m`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """
    # Kinderbonus parameter is specified on the yearly level
    # kindergeld_basis_m is zero for all adults
    if kindergeld_basis_m > 0:
        out = kindergeld_params["kinderbonus"] / 12
    else:
        out = 0.0

    return out
