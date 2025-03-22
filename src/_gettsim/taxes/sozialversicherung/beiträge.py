"""Social insurance contributions."""

from _gettsim.function_types import policy_function


@policy_function()
def beiträge_versicherter_m(
    sozialversicherung__pflege__beitrag__betrag_versicherter_m: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_m: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_m: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m: float,
) -> float:
    """Sum of social insurance contributions paid by the insured person.
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
def beiträge_arbeitgeber_m(
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
    beiträge_versicherter_m: float,
    beiträge_arbeitgeber_m: float,
) -> float:
    """Sum of employer's and insured person's social insurance contributions.

    Parameters
    ----------
    beiträge_versicherter_m
        See :func:`beiträge_versicherter_m`.
    beiträge_arbeitgeber_m
        See :func:`beiträge_arbeitgeber_m`.
    Returns
    -------

    """
    return beiträge_versicherter_m + beiträge_arbeitgeber_m
