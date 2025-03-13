"""Social insurance contributions."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_arbeitnehmer_m(
    sozialversicherung__pflege__beitrag__betrag_arbeitnehmer_m: float,
    sozialversicherung__kranken__beitrag__betrag_arbeitnehmer_m: float,
    sozialversicherung__rente__beitrag__betrag_arbeitnehmer_m: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_arbeitnehmer_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    sozialversicherung__pflege__beitrag__betrag_arbeitnehmer_m
        See :func:`sozialversicherung__pflege__beitrag__betrag_arbeitnehmer_m`.
    sozialversicherung__kranken__beitrag__betrag_arbeitnehmer_m
        See :func:`sozialversicherung__kranken__beitrag__betrag_arbeitnehmer_m`.
    sozialversicherung__rente__beitrag__betrag_arbeitnehmer_m
        See :func:
        `sozialversicherung__rente__beitrag__betrag_arbeitnehmer_m`.
    sozialversicherung__arbeitslosen__beitrag__betrag_arbeitnehmer_m
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_arbeitnehmer_m`.

    Returns
    -------

    """
    return (
        sozialversicherung__pflege__beitrag__betrag_arbeitnehmer_m
        + sozialversicherung__kranken__beitrag__betrag_arbeitnehmer_m
        + sozialversicherung__rente__beitrag__betrag_arbeitnehmer_m
        + sozialversicherung__arbeitslosen__beitrag__betrag_arbeitnehmer_m
    )


@policy_function()
def betrag_arbeitgeber_m(
    sozialversicherung__pflege__beitrag__betrag_arbeitgeber_m: float,
    sozialversicherung__kranken__beitrag__betrag_arbeitgeber_m: float,
    sozialversicherung__rente__beitrag__betrag_arbeitgeber_m: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's social insurance contributions.

    Parameters
    ----------
    sozialversicherung__pflege__beitrag__betrag_arbeitgeber_m
        See :func:`sozialversicherung__pflege__beitrag__betrag_arbeitgeber_m`.
    sozialversicherung__kranken__beitrag__betrag_arbeitgeber_m
        See :func:`sozialversicherung__kranken__beitrag__betrag_arbeitgeber_m`.
    sozialversicherung__rente__beitrag__betrag_arbeitgeber_m
        See :func:`sozialversicherung__rente__beitrag__betrag_arbeitgeber_m`.
    sozialversicherung__arbeitslosen__beitrag__betrag_arbeitgeber_m
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_arbeitgeber_m`.

    Returns
    -------

    """
    return (
        sozialversicherung__pflege__beitrag__betrag_arbeitgeber_m
        + sozialversicherung__kranken__beitrag__betrag_arbeitgeber_m
        + sozialversicherung__rente__beitrag__betrag_arbeitgeber_m
        + sozialversicherung__arbeitslosen__beitrag__betrag_arbeitgeber_m
    )


@policy_function()
def beitrag_gesamt_m(
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
