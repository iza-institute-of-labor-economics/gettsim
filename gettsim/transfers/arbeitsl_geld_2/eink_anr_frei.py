from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def eink_anr_frei_bis_09_2005(
    bruttolohn_m: FloatSeries,
    arbeitsl_geld_2_2005_netto_quote: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calcualte share of income, which remains to the individual until 09/2005.

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


def eink_anr_frei_ab_10_2005(
    hh_id: IntSeries,
    bruttolohn_m: FloatSeries,
    kinder_in_hh: BoolSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calcualte share of income, which remains to the individual sinc 10/2005.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    kinder_in_hh
        See :func:`kinder_in_h`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = bruttolohn_m * 0
    kinder_in_hh_individual = hh_id.replace(kinder_in_hh).astype(bool)
    out.loc[kinder_in_hh_individual] = piecewise_polynomial(
        x=bruttolohn_m.loc[kinder_in_hh_individual],
        thresholds=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei_kinder"][
            "intercepts_at_lower_thresholds"
        ],
    )
    out.loc[~kinder_in_hh_individual] = piecewise_polynomial(
        x=bruttolohn_m.loc[~kinder_in_hh_individual],
        thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return out


def arbeitsl_geld_2_2005_netto_quote(
    bruttolohn_m: FloatSeries, nettolohn_m: FloatSeries, arbeitsl_geld_2_params: dict
) -> FloatSeries:
    """Calcualte share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    nettolohn_m
        See :func:`nettolohn_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = (
        nettolohn_m
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
    ).clip(lower=0)

    arbeitsl_geld_2_2005_netto_quote = alg2_2005_bne / bruttolohn_m

    return arbeitsl_geld_2_2005_netto_quote
