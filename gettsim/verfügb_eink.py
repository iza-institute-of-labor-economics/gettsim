import numpy as np


def disposable_income(household):
    household["verfügb_eink_m"] = household[
        [
            "bruttolohn_m",
            "kapital_eink_m",
            "eink_selbstst_m",
            "vermiet_eink_m",
            # "miete_unterstellt", We need to discuss this!
            "ges_rente_m",
            "sonstig_eink_m",
            "kindergeld_m",
            "unterhaltsvors_m",
        ]
    ].sum(axis=1) - household[
        [
            "eink_st_m",
            "soli_st_m",
            "abgelt_st_m",
            "ges_krankenv_beitr_m",
            "rentenv_beitr_m",
            "pflegev_beitr_m",
            "arbeitsl_v_beitr_m",
        ]
    ].sum(
        axis=1
    )

    # Disposible income on hh level
    household["verfügb_eink_hh_m"] = round(
        np.maximum(
            0,
            sum(household["verfügb_eink_m"])
            + household["arbeitsl_geld_2_m"]
            + household["wohngeld_m"]
            + household["kinderzuschlag_m"],
        ),
        2,
    )
    return household


# def gross_income(household):
#    household["brutto_eink"] = round(
#        household[
#            [
#                "bruttolohn_m",
#                "kapital_eink_m",
#                "eink_selbstst_m",
#                "vermiet_eink_m",
#                "miete_unterstellt",
#                "ges_rente_m",
#                "sonstig_eink_m",
#                "kindergeld_m",
#            ]
#        ].sum(axis=1),
#        2,
#    )
#    return household
