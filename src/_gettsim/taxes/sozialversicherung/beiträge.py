"""Social insurance contributions."""

from _gettsim.function_types import policy_function


@policy_function()
def beiträge_arbeitnehmer_m(
    sozialversicherung__pflege__beitrag__betrag_versicherter_m: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_m: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_m: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m: float,
) -> float:
    """Sum of employee's social insurance contributions.

    Parameters
    ----------
    sozialversicherung__pflege__beitrag__betrag_versicherter_m
        See :func:`sozialversicherung__pflege__beitrag__betrag_versicherter_m`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_m
        See :func:`sozialversicherung__kranken__beitrag__betrag_versicherter_m`.
    sozialversicherung__rente__beitrag__betrag_versicherter_m
        See :func:
        `sozialversicherung__rente__beitrag__betrag_versicherter_m`.
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m`.

    Returns
    -------

    """
    return (
        sozialversicherung__pflege__beitrag__betrag_versicherter_m
        + sozialversicherung__kranken__beitrag__betrag_versicherter_m
        + sozialversicherung__rente__beitrag__betrag_versicherter_m
        + sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m
    )


@policy_function()
def beitrag_arbeitgeber_m(
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
    betrag_versicherter_m: float,
    betrag_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and employee's social insurance contributions.

    Parameters
    ----------
    betrag_versicherter_m
        See :func:`betrag_versicherter_m`.
    betrag_arbeitgeber_m
        See :func:`betrag_arbeitgeber_m`.
    Returns
    -------

    """
    return betrag_versicherter_m + betrag_arbeitgeber_m
