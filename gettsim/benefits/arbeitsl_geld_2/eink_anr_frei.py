from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def eink_anr_frei_bis_10_2005(
    bruttolohn_m, arbeitsl_geld_2_2005_netto_quote, arbeitsl_geld_2_params
):
    return piecewise_polynomial(
        x=bruttolohn_m,
        thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
        rates_multiplier=arbeitsl_geld_2_2005_netto_quote,
    )


def eink_anr_frei_ab_10_2005(
    bruttolohn_m, kinder_in_hh_individual, arbeitsl_geld_2_params
):
    out = bruttolohn_m * 0
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
    bruttolohn_m, nettolohn_m, arbeitsl_geld_2_params,
):
    """Calculate Nettoquote.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = (
        nettolohn_m
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
    ).clip(lower=0)

    arbeitsl_geld_2_2005_netto_quote = alg2_2005_bne / bruttolohn_m

    return arbeitsl_geld_2_2005_netto_quote
