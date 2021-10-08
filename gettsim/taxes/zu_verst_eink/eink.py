from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def brutto_eink_1(eink_selbst_m: FloatSeries) -> FloatSeries:
    """Aggregate income gross from self-employment to full year income.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.

    Returns
    -------

    """
    return 12 * eink_selbst_m.clip(lower=0)


def brutto_eink_1_tu(brutto_eink_1: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate income gross from self-employment on tax unit level.


    Parameters
    ----------
    brutto_eink_1
        See :func:`brutto_eink_1`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return brutto_eink_1.groupby(tu_id).sum()


def brutto_eink_4(
    bruttolohn_m: FloatSeries,
    geringfügig_beschäftigt: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Aggreagate monthly gross wage to yearly income and deduct 'Werbungskosten'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = 12 * bruttolohn_m - eink_st_abzuege_params["werbungskostenpauschale"]
    out.loc[geringfügig_beschäftigt] = 0
    return out.clip(lower=0)


def brutto_eink_4_tu(brutto_eink_4: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate gross income of non selfemployed work on tax unit level.

    Parameters
    ----------
    brutto_eink_4
        See :func:`brutto_eink_4`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return brutto_eink_4.groupby(tu_id).sum()


def brutto_eink_5(kapital_eink_m: FloatSeries) -> FloatSeries:
    """Aggregate monthly gross capital income to yearly income.


    Parameters
    ----------
    kapital_eink_m
        See basic input variable :ref:`kapital_eink_m <kapital_eink_m>`.

    Returns
    -------

    """
    return (12 * kapital_eink_m).clip(lower=0)


def brutto_eink_5_tu(brutto_eink_5: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate yearly gross capital income on tax unit level.

    Parameters
    ----------
    brutto_eink_5
        See :func:`brutto_eink_5`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return brutto_eink_5.groupby(tu_id).sum()


def brutto_eink_6(vermiet_eink_m: FloatSeries) -> FloatSeries:
    """Aggregate monthly gross rental income to yearly income.

    Parameters
    ----------
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.

    Returns
    -------

    """
    return (12 * vermiet_eink_m).clip(lower=0)


def brutto_eink_6_tu(brutto_eink_6: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate yearly gross income from rents on tax unit level.

    Parameters
    ----------
    brutto_eink_6
        See :func:`brutto_eink_6`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.


    Returns
    -------

    """
    return brutto_eink_6.groupby(tu_id).sum()


def brutto_eink_7(ges_rente_m: FloatSeries, ertragsanteil: FloatSeries) -> FloatSeries:
    """Aggregate monthly gross pension payments subject to taxation to yearly income.

    We could summarize other incomes here as well, but only use pensions.

    Parameters
    ----------
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.
    ertragsanteil
        See :func:`ertragsanteil`.

    Returns
    -------

    """
    return ertragsanteil * 12 * ges_rente_m


def brutto_eink_7_tu(brutto_eink_7: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate yearly gross pension income subject to taxation on tax unit level.

    Parameters
    ----------
    brutto_eink_7
        See :func:`brutto_eink_7`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return brutto_eink_7.groupby(tu_id).sum()


def sum_brutto_eink_ohne_kapital(
    brutto_eink_1: FloatSeries,
    brutto_eink_4: FloatSeries,
    brutto_eink_6: FloatSeries,
    brutto_eink_7: FloatSeries,
) -> FloatSeries:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to noraml taxation.
    Parameters
    ----------
    brutto_eink_1
        See :func:`brutto_eink_1`.
    brutto_eink_4
        See :func:`brutto_eink_4`.
    brutto_eink_6
        See :func:`brutto_eink_6`.
    brutto_eink_7
        See :func:`brutto_eink_7`.

    Returns
    -------

    """
    return brutto_eink_1 + brutto_eink_4 + brutto_eink_6 + brutto_eink_7


def sum_brutto_eink_mit_kapital(
    sum_brutto_eink_ohne_kapital: FloatSeries,
    brutto_eink_5: FloatSeries,
    eink_st_abzuege_params: dict,
):
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    sum_brutto_eink_ohne_kapital
        See :func:`sum_brutto_eink_ohne_kapital`.
    brutto_eink_5
        See :func:`brutto_eink_5`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    return sum_brutto_eink_ohne_kapital + (
        brutto_eink_5
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
    ).clip(lower=0)


def ertragsanteil(jahr_renteneintr: IntSeries, eink_st_params: dict) -> FloatSeries:
    """Calculate the share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr
            See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.
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
