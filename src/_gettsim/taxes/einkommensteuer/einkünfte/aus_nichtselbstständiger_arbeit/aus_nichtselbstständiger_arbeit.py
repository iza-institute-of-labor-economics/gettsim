"""Einkünfte aus nichtselbstständiger Arbeit."""

from _gettsim.function_types import policy_function


@policy_function()
def betrag_y(
    betrag_ohne_minijob_y: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
) -> float:
    """Taxable income from dependent employment. In particular, taxable income is set to
    0 for marginally employed persons.

    Parameters
    ----------
    betrag_ohne_minijob_y
        See :func:`betrag_ohne_minijob_y`.
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.

    Returns
    -------

    """
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_ohne_minijob_y

    return out


@policy_function()
def betrag_ohne_minijob_y(
    einnahmen__bruttolohn_y: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Aggregate monthly gross wage to yearly income and deduct
    'Werbungskostenpauschale'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    einnahmen__bruttolohn_y
        See basic input variable :ref:`einnahmen__bruttolohn_y <einnahmen__bruttolohn_y>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    abzug = eink_st_abzuege_params["werbungskostenpauschale"]

    out = einnahmen__bruttolohn_y - abzug

    return max(out, 0.0)
