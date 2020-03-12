import numpy as np


def disposable_income(household):
    household["verfüg_eink_m"] = household[
        [
            "bruttolohn_m",
            "kapital_eink_m",
            "eink_selbstst_m",
            "vermiet_eink_m",
            # "miete_unterstellt", We need to discuss this!
            "ges_rente_m",
            "sonstig_eink_m",
            "kindergeld",
            "unterhaltsvors_m",
        ]
    ].sum(axis=1) - household[
        [
            "eink_st",
            "soli_st",
            "abgelt_st",
            "ges_krankv_beit_m",
            "rentenv_beit_m",
            "pflegev_beit_m",
            "arbeitsl_v_beit_m",
        ]
    ].sum(
        axis=1
    )

    # Disposible income on hh level
    household["verfüg_eink_hh_m"] = round(
        np.maximum(
            0,
            sum(household["verfüg_eink_m"])
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
#                "kindergeld",
#            ]
#        ].sum(axis=1),
#        2,
#    )
#    return household
