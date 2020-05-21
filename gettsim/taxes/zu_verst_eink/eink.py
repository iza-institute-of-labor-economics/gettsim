import numpy as np


def brutto_eink_1(eink_selbstst_m):
    """
    Income from Self-Employment

    Parameters
    ----------
    eink_selbstst_m

    Returns
    -------

    """
    out = np.maximum(12 * eink_selbstst_m, 0)
    return out.rename("brutto_eink_1")


def brutto_eink_1_tu(brutto_eink_1, tu_id):
    """


    Parameters
    ----------
    brutto_eink_1
    tu_id

    Returns
    -------

    """
    out = brutto_eink_1.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_1_tu")


def brutto_eink_4(bruttolohn_m, geringfügig_beschäftigt, eink_st_abzuege_params):
    """
    Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'
    Parameters
    ----------
    bruttolohn_m

    Returns
    -------

    """
    out = np.maximum(
        bruttolohn_m.multiply(12).subtract(
            eink_st_abzuege_params["werbungskostenpauschale"]
        ),
        0,
    )
    out.loc[geringfügig_beschäftigt] = 0
    return out.rename("brutto_eink_4")


def brutto_eink_4_tu(brutto_eink_4, tu_id):
    """

    Parameters
    ----------
    brutto_eink_4
    tu_id

    Returns
    -------

    """
    out = brutto_eink_4.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_4_tu")


def brutto_eink_5(kapital_eink_m):
    """
    Capital Income

    Parameters
    ----------
    kapital_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * kapital_eink_m, 0)
    return out.rename("brutto_eink_5")


def brutto_eink_5_tu(brutto_eink_5, tu_id):
    """

    Parameters
    ----------
    brutto_eink_5
    tu_id

    Returns
    -------

    """
    out = brutto_eink_5.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_5_tu")


def brutto_eink_6(vermiet_eink_m):
    """
    Income from rents

    Parameters
    ----------
    vermiet_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * vermiet_eink_m, 0)
    return out.rename("brutto_eink_6")


def brutto_eink_6_tu(brutto_eink_6, tu_id):
    """

    Parameters
    ----------
    brutto_eink_6
    tu_id

    Returns
    -------

    """
    out = brutto_eink_6.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_6_tu")


def brutto_eink_7(ges_rente_m, _ertragsanteil):
    """
    Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions.

    Parameters
    ----------
    ges_rente_m
    _ertragsanteil

    Returns
    -------

    """
    out = _ertragsanteil.multiply(12 * ges_rente_m)
    return out.rename("brutto_eink_7")


def brutto_eink_7_tu(brutto_eink_7, tu_id):
    """

    Parameters
    ----------
    brutto_eink_7
    tu_id

    Returns
    -------

    """
    out = brutto_eink_7.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_7_tu")


def _sum_brutto_eink_ohne_kapital(
    brutto_eink_1, brutto_eink_4, brutto_eink_6, brutto_eink_7
):
    """
    Since 2009 capital income is not subject to noraml taxation.
    Parameters
    ----------
    brutto_eink_1
    brutto_eink_4
    brutto_eink_6
    brutto_eink_7

    Returns
    -------

    """
    out = brutto_eink_1 + brutto_eink_4 + brutto_eink_6 + brutto_eink_7
    return out.rename("sum_brutto_eink")


def _sum_brutto_eink_mit_kapital(
    _sum_brutto_eink_ohne_kapital, brutto_eink_5, eink_st_abzuege_params
):
    out = _sum_brutto_eink_ohne_kapital + (
        brutto_eink_5
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    ).clip(lower=0)
    return out.rename("sum_brutto_eink")
