from gettsim.piecewise_functions import piecewise_polynomial


def brutto_eink_1(eink_selbst_m):
    """Income from Self-Employment

    Parameters
    ----------
    eink_selbst_m

    Returns
    -------

    """
    return 12 * eink_selbst_m.clip(lower=0)


def brutto_eink_1_tu(brutto_eink_1, tu_id):
    """Aggregate income from Self-Employment on tax unit level.


    Parameters
    ----------
    brutto_eink_1
    tu_id

    Returns
    -------

    """
    return brutto_eink_1.groupby(tu_id).sum()


def brutto_eink_4(bruttolohn_m, geringfügig_beschäftigt, eink_st_abzuege_params):
    """Calculates the gross incomes of non selfemployed work.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    bruttolohn_m
    geringfügig_beschäftigt
    eink_st_abzuege_params

    Returns
    -------

    """
    out = 12 * bruttolohn_m - eink_st_abzuege_params["werbungskostenpauschale"]
    out.loc[geringfügig_beschäftigt] = 0
    return out.clip(lower=0)


def brutto_eink_4_tu(brutto_eink_4, tu_id):
    """Aggregate the gross incomes of non selfemployed work on tax unit level.

    Parameters
    ----------
    brutto_eink_4
    tu_id

    Returns
    -------

    """
    return brutto_eink_4.groupby(tu_id).sum()


def brutto_eink_5(kapital_eink_m):
    """Capital Income.


    Parameters
    ----------
    kapital_eink_m

    Returns
    -------

    """
    return (12 * kapital_eink_m).clip(lower=0)


def brutto_eink_5_tu(brutto_eink_5, tu_id):
    """Capital income on tax unit level.

    Parameters
    ----------
    brutto_eink_5
    tu_id

    Returns
    -------

    """
    return brutto_eink_5.groupby(tu_id).sum()


def brutto_eink_6(vermiet_eink_m):
    """Income from rents.

    Parameters
    ----------
    vermiet_eink_m

    Returns
    -------

    """
    return (12 * vermiet_eink_m).clip(lower=0)


def brutto_eink_6_tu(brutto_eink_6, tu_id):
    """Income from rents on tax unit level.

    Parameters
    ----------
    brutto_eink_6
    tu_id

    Returns
    -------

    """
    return brutto_eink_6.groupby(tu_id).sum()


def brutto_eink_7(ges_rente_m, _ertragsanteil):
    """Calculates the gross income of 'Sonsitge Einkünfte'.

    In our case that's only pensions.

    Parameters
    ----------
    ges_rente_m
    _ertragsanteil

    Returns
    -------

    """
    return _ertragsanteil * 12 * ges_rente_m


def brutto_eink_7_tu(brutto_eink_7, tu_id):
    """Calculates the gross income of 'Sonsitge Einkünfte' on tax unit level.

    Parameters
    ----------
    brutto_eink_7
    tu_id

    Returns
    -------

    """
    return brutto_eink_7.groupby(tu_id).sum()


def sum_brutto_eink_ohne_kapital(
    brutto_eink_1, brutto_eink_4, brutto_eink_6, brutto_eink_7
):
    """Sum of gross incomes without capital income.

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
    return brutto_eink_1 + brutto_eink_4 + brutto_eink_6 + brutto_eink_7


def sum_brutto_eink_mit_kapital(
    sum_brutto_eink_ohne_kapital, brutto_eink_5, eink_st_abzuege_params
):
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    sum_brutto_eink_ohne_kapital
    brutto_eink_5
    eink_st_abzuege_params

    Returns
    -------

    """
    return sum_brutto_eink_ohne_kapital + (
        brutto_eink_5
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    ).clip(lower=0)


def _ertragsanteil(jahr_renteneintr, eink_st_params):
    """Calculate the share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=jahr_renteneintr,
        thresholds=eink_st_params["ertragsanteil"]["thresholds"],
        rates=eink_st_params["ertragsanteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["ertragsanteil"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out
