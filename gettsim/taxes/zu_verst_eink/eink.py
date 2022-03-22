from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def eink_selbst_m_tu(eink_selbst_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly self employed income on tax unit level.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_selbst_m.groupby(tu_id).sum()


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


def eink_selbst_tu(eink_selbst: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate income gross from self-employment on tax unit level.


    Parameters
    ----------
    eink_selbst
        See :func:`eink_selbst`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_selbst.groupby(tu_id).sum()


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
        return 0
    else:
        return 12 * bruttolohn_m - eink_st_abzüge_params["werbungskostenpauschale"]


def eink_abhängig_beschäftigt_tu(
    eink_abhängig_beschäftigt: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate gross income of non selfemployed work on tax unit level.

    Parameters
    ----------
    eink_abhängig_beschäftigt
        See :func:`eink_abhängig_beschäftigt`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_abhängig_beschäftigt.groupby(tu_id).sum()


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


def kapitaleink_brutto_tu(
    kapitaleink_brutto: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate yearly gross capital income on tax unit level.

    Parameters
    ----------
    kapitaleink_brutto
        See :func:`kapitaleink_brutto`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kapitaleink_brutto.groupby(tu_id).sum()


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


def eink_vermietung_tu(eink_vermietung: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate yearly gross income from rents on tax unit level.

    Parameters
    ----------
    eink_vermietung
        See :func:`eink_vermietung`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.


    Returns
    -------

    """
    return eink_vermietung.groupby(tu_id).sum()


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


def bruttolohn_m_tu(bruttolohn_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Sum monthly wages in tax unit.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------
    FloatSeries with sum of monthly wages per tax unit.
    """
    return bruttolohn_m.groupby(tu_id).sum()


def kapitaleink_brutto_m_tu(
    kapitaleink_brutto_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggregate monthly capital income on tax unit level.

    Parameters
    ----------
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kapitaleink_brutto_m.groupby(tu_id).sum()


def vermiet_eink_m_tu(vermiet_eink_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly rental income on tax unit level.

    Parameters
    ----------
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return vermiet_eink_m.groupby(tu_id).sum()


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
    return (
        eink_selbst + eink_abhängig_beschäftigt + eink_vermietung + eink_rente_zu_verst
    )


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


def sum_eink_tu(sum_eink: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Sum of gross incomes on tax unit level.

    Parameters
    ----------
    sum_eink
        See :func:`sum_eink`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return sum_eink.groupby(tu_id).sum()


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


def sonstig_eink_m_tu(sonstig_eink_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate additional per tax unit.

    Parameters
    ----------
    sonstig_eink_m
        See basic input variable :ref:`sonstig_eink_m <sonstig_eink_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return sonstig_eink_m.groupby(tu_id).sum()


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


def eink_rente_zu_verst_m_tu(
    eink_rente_zu_verst_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggreate pension payments subject to taxation in tax unit.

    Parameters
    ----------
    eink_rente_zu_verst_m
        See :func:`eink_rente_zu_verst_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_rente_zu_verst_m.groupby(tu_id).sum()
