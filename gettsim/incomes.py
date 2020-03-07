import numpy as np


def disposable_income(household):
    household["dpi_ind"] = household[
        [
            "lohn_m",
            "kapital_eink_m",
            "eink_selbstst_m",
            "vermiet_eink_m",
            # "eigenheim_ersp_m", We need to discuss this!
            "rente_m",
            "sonstig_eink_m",
            "kindergeld",
            "unterhalt_vors_m",
        ]
    ].sum(axis=1) - household[
        [
            "eink_st",
            "soli_st",
            "abgelt_st",
            "krankv_beit_m",
            "rentenv_beit_m",
            "pflegev_beit_m",
            "arbeitsl_beit_m",
        ]
    ].sum(
        axis=1
    )

    # Disposible income on hh level
    household["dpi"] = round(
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


def gross_income(household):
    household["gross"] = round(
        household[
            [
                "lohn_m",
                "kapital_eink_m",
                "eink_selbstst_m",
                "vermiet_eink_m",
                "eigenheim_ersp_m",
                "rente_m",
                "sonstig_eink_m",
                "kindergeld",
            ]
        ].sum(axis=1),
        2,
    )
    return household
