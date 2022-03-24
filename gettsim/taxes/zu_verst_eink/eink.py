from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def eink_selbst(eink_selbst_m: FloatSeries) -> FloatSeries:
    """Aggregate income gross from self-employment to full year income.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.

    Returns
    -------

    """
    return 12 * eink_selbst_m


def eink_abhängig_beschäftigt(
    bruttolohn_m: FloatSeries,
    geringfügig_beschäftigt: BoolSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Aggreagate monthly gross wage to yearly income and deduct 'Werbungskosten'.

    The wage is reducted by a lump sum payment for 'Werbungskosten'

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    if geringfügig_beschäftigt:
        out = 0.0
    else:
        out = 12 * bruttolohn_m - eink_st_abzüge_params["werbungskostenpauschale"]

    return out


def kapitaleink_brutto(kapitaleink_brutto_m: FloatSeries) -> FloatSeries:
    """Aggregate monthly gross capital income to yearly income.


    Parameters
    ----------
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.

    Returns
    -------

    """
    return 12 * kapitaleink_brutto_m


def eink_vermietung(vermiet_eink_m: FloatSeries) -> FloatSeries:
    """Aggregate monthly gross rental income to yearly income.

    Parameters
    ----------
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.

    Returns
    -------

    """
    return 12 * vermiet_eink_m


def eink_rente_zu_verst(
    sum_ges_rente_priv_rente_m: FloatSeries, rente_ertragsanteil: FloatSeries
) -> FloatSeries:
    """Aggregate monthly gross pension income subject to taxation to yearly income.

    We could summarize other incomes here as well, but only use pensions.

    Parameters
    ----------
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.
    rente_ertragsanteil
        See :func:`rente_ertragsanteil`.

    Returns
    -------

    """
    return rente_ertragsanteil * 12 * sum_ges_rente_priv_rente_m


def sum_eink_ohne_kapital(
    eink_selbst: FloatSeries,
    eink_abhängig_beschäftigt: FloatSeries,
    eink_vermietung: FloatSeries,
    eink_rente_zu_verst: FloatSeries,
) -> FloatSeries:
    """Sum of gross incomes without capital income.

    Since 2009 capital income is not subject to normal taxation.
    Parameters
    ----------
    eink_selbst
        See :func:`eink_selbst`.
    eink_abhängig_beschäftigt
        See :func:`eink_abhängig_beschäftigt`.
    eink_vermietung
        See :func:`eink_vermietung`.
    eink_rente_zu_verst
        See :func:`eink_rente_zu_verst`.

    Returns
    -------

    """
    out = (
        eink_selbst + eink_abhängig_beschäftigt + eink_vermietung + eink_rente_zu_verst
    )
    return out


def kapitaleink(
    kapitaleink_brutto: FloatSeries, eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Capital income minus Sparerpauschbetrag

    Parameters
    ----------
    kapitaleink_brutto
        See :func:`kapitaleink_brutto`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = (
        kapitaleink_brutto
        - eink_st_abzüge_params["sparerpauschbetrag"]
        - eink_st_abzüge_params["sparer_werbungskosten_pauschbetrag"]
    )

    return max(out, 0.0)


def sum_eink_mit_kapital(
    sum_eink_ohne_kapital: FloatSeries, kapitaleink: FloatSeries,
):
    """Sum of gross incomes with capital income.

    Parameters
    ----------
    sum_eink_ohne_kapital
        See :func:`sum_eink_ohne_kapital`.
    kapitaleink
        See :func:`kapitaleink`.

    Returns
    -------

    """
    return sum_eink_ohne_kapital + kapitaleink


def rente_ertragsanteil(
    jahr_renteneintr: IntSeries, eink_st_params: dict
) -> FloatSeries:
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
        thresholds=eink_st_params["rente_ertragsanteil"]["thresholds"],
        rates=eink_st_params["rente_ertragsanteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["rente_ertragsanteil"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


def eink_rente_zu_verst_m(
    rente_ertragsanteil: FloatSeries, sum_ges_rente_priv_rente_m: FloatSeries
) -> FloatSeries:
    """Calculate pension payment subject to taxation.

    Parameters
    ----------
    rente_ertragsanteil
        See :func:`rente_ertragsanteil`.
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.

    Returns
    -------

    """
    return rente_ertragsanteil * sum_ges_rente_priv_rente_m
