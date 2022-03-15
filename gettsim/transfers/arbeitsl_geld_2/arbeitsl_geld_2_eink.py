from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_2_eink_m_hh(
    arbeitsl_geld_2_eink_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Sum up the income per household for calculation of basic subsistence.

    Parameters
    ----------
    arbeitsl_geld_2_eink_m
        See :func:`arbeitsl_geld_2_eink_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------
    FloatSeries returns the income given by unemployment insurance per household.
    """
    return arbeitsl_geld_2_eink_m.groupby(hh_id).sum()


def arbeitsl_geld_2_eink_m(
    arbeitsl_geld_2_brutto_eink_m: FloatSeries,
    eink_st_tu: FloatSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_gesamt_m: FloatSeries,
    arbeitsl_geld_2_eink_anr_frei_m: FloatSeries,
) -> FloatSeries:

    """Sum up the income for calculation of basic subsistence.

    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink_m
        See :func:`arbeitsl_geld_2_eink_m`.
    sozialv_beitr_gesamt_m
        See :func:`sozialv_beitr_gesamt_m`.
    eink_st_tu
        See :func:`eink_st_tu`.
    soli_st_tu
        See :func:`soli_st_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_eink_anr_frei_m
        See :func:`arbeitsl_geld_2_eink_anr_frei_m`.

    Returns
    -------
    Float Series with the income of a person by unemployment insurance.
    """

    out = (
        arbeitsl_geld_2_brutto_eink_m
        - (eink_st_tu / anz_erwachsene_tu / 12)
        - (soli_st_tu / anz_erwachsene_tu / 12)
        - sozialv_beitr_gesamt_m
        - arbeitsl_geld_2_eink_anr_frei_m
    )

    if out < 0:
        return 0
    else:
        return out


def arbeitsl_geld_2_brutto_eink_m_hh(
    arbeitsl_geld_2_brutto_eink_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:

    """Sum up the income before tax per household for calculation of basic subsistence.
    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink_m
        See :func:`arbeitsl_geld_2_brutto_eink_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------
    Float Series with the income of a person by unemployment insurance before tax.
    """
    return arbeitsl_geld_2_brutto_eink_m.groupby(hh_id).sum()


def arbeitsl_geld_2_brutto_eink_m(
    bruttolohn_m: FloatSeries,
    sonstig_eink_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    kapitaleink_brutto_m: FloatSeries,
    sum_ges_rente_priv_rente_m: FloatSeries,
    arbeitsl_geld_m: FloatSeries,
    elterngeld_m: FloatSeries,
) -> FloatSeries:

    """Sum up the income before tax for calculation of basic subsistence.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`hh_id <hh_id>`.
    sonstig_eink_m
        See basic input variable :ref:`sonstig_eink_m <sonstig_eink_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    elterngeld_m
        See :func:`elterngeld_m`.

    Returns
    -------
    FloatSeries with the income by unemployment insurance before tax.
    """
    return (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbst_m
        + vermiet_eink_m
        + kapitaleink_brutto_m
        + sum_ges_rente_priv_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )


def arbeitsl_geld_2_2005_netto_quote(
    bruttolohn_m: FloatSeries,
    elterngeld_nettolohn_m: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    elterngeld_nettolohn_m
        See :func:`elterngeld_nettolohn_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = (
        elterngeld_nettolohn_m
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
    )

    if alg2_2005_bne < 0:
        arbeitsl_geld_2_2005_netto_quote = 0
    else:
        arbeitsl_geld_2_2005_netto_quote = alg2_2005_bne / bruttolohn_m

    return arbeitsl_geld_2_2005_netto_quote


def arbeitsl_geld_2_eink_anr_frei_m_bis_09_2005(
    bruttolohn_m: FloatSeries,
    arbeitsl_geld_2_2005_netto_quote: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate share of income, which remains to the individual until 09/2005.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    arbeitsl_geld_2_2005_netto_quote
        See :func:`arbeitsl_geld_2_2005_netto_quote`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=bruttolohn_m,
        thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
        rates_multiplier=arbeitsl_geld_2_2005_netto_quote,
    )
    return out


def arbeitsl_geld_2_eink_anr_frei_m_ab_10_2005(
    bruttolohn_m: FloatSeries, anz_kinder_hh: IntSeries, arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calcualte share of income, which remains to the individual sinc 10/2005.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    anz_kinder_hh
        See :func:`anz_kinder_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = bruttolohn_m * 0
    kinder_in_hh_individual = bool(anz_kinder_hh > 0)

    if kinder_in_hh_individual:
        out = piecewise_polynomial(
            x=bruttolohn_m,
            thresholds=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["thresholds"],
            rates=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["rates"],
            intercepts_at_lower_thresholds=arbeitsl_geld_2_params[
                "eink_anr_frei_kinder"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        out = piecewise_polynomial(
            x=bruttolohn_m,
            thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
            rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
            intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
                "intercepts_at_lower_thresholds"
            ],
        )
    return out
