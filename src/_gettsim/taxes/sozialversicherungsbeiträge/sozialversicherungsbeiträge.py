"""Social insurance contributions."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def betrag_arbeitnehmer_m(
    sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitnehmer_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitnehmer_m
        See :func:
        `sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitnehmer_m`.

    Returns
    -------

    """
    return (
        sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitnehmer_m
        + sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitnehmer_m
    )


@policy_function()
def betrag_arbeitgeber_m(
    sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitgeber_m: float,
    sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions.

    Parameters
    ----------
    sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitgeber_m`.
    sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitgeber_m
        See :func:`sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitgeber_m`.

    Returns
    -------

    """
    return (
        sozialversicherungsbeiträge__pflegeversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeiträge__krankenversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeiträge__rentenversicherung__betrag_arbeitgeber_m
        + sozialversicherungsbeiträge__arbeitslosenversicherung__betrag_arbeitgeber_m
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
