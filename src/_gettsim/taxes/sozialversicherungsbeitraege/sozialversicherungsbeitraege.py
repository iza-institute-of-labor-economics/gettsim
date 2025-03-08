"""Social insurance contributions."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def betrag_arbeitnehmer_m(
    sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m
        See :func:
        `sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m`.

    Returns
    -------

    """
    return (
        sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m
    )


@policy_function()
def betrag_arbeitgeber_m(
    sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions.

    Parameters
    ----------
    sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitgeber_m`.

    Returns
    -------

    """
    return (
        sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitgeber_m
    )


@policy_function()
def betrag_gesamt_m(
    betrag_arbeitnehmer_m: float,
    betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and employee's social insurance contributions.

    Parameters
    ----------
    betrag_arbeitnehmer_m
        See :func:`betrag_arbeitnehmer_m`.
    betrag_arbeitgeber_m
        See :func:`betrag_arbeitgeber_m`.
    Returns
    -------

    """
    return betrag_arbeitnehmer_m + betrag_arbeitgeber_m
