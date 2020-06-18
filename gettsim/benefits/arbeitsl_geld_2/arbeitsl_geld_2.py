import numpy as np


def regelbedarf_m(regelsatz_m, kost_unterk_m):
    """Basic monthly subsistence level, including cost of dwelling.

    Parameters
    ----------
    regelsatz_m
    kost_unterk_m

    Returns
    -------

    """
    return regelsatz_m + kost_unterk_m


def alleinerziehenden_mehrbedarf(
    alleinerziehend,
    anz_kinder_hh,
    anz_kind_zwischen_0_6_per_hh,
    anz_kind_zwischen_0_15_per_hh,
    arbeitsl_geld_2_params,
):
    """Compute alleinerziehenden_mehrbedarf.

    Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    """
    lower = arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"] * anz_kinder_hh
    value = (
        (anz_kind_zwischen_0_6_per_hh >= 1)
        | ((2 <= anz_kind_zwischen_0_15_per_hh) & (anz_kind_zwischen_0_15_per_hh <= 3))
    ) * arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]

    return alleinerziehend * value.clip(
        lower=lower, upper=arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]
    )


def kindersatz_m_bis_2010(
    hh_id,
    kind_zwischen_0_6,
    kind_zwischen_7_13,
    kind_zwischen_14_24,
    arbeitsl_geld_2_params,
):
    anteile = arbeitsl_geld_2_params["anteil_regelsatz"]

    per_child = arbeitsl_geld_2_params["regelsatz"] * (
        anteile["kinder_0_6"] * kind_zwischen_0_6
        + anteile["kinder_7_13"] * kind_zwischen_7_13
        + anteile["kinder_14_24"] * kind_zwischen_14_24
    )

    return per_child.groupby(hh_id).transform("sum")


def kindersatz_m_ab_2011(
    hh_id,
    kind_zwischen_0_6,
    kind_zwischen_7_13,
    kind_zwischen_14_24,
    arbeitsl_geld_2_params,
):
    per_child = (
        arbeitsl_geld_2_params["regelsatz"][6] * kind_zwischen_0_6
        + arbeitsl_geld_2_params["regelsatz"][5] * kind_zwischen_7_13
        + arbeitsl_geld_2_params["regelsatz"][4] * kind_zwischen_14_24
    )

    return per_child.groupby(hh_id).transform("sum")


def regelsatz_m_bis_2010(
    hh_id,
    anz_erwachsene_hh,
    alleinerziehenden_mehrbedarf,
    kindersatz_m,
    arbeitsl_geld_2_params,
):
    anz_erwachsene_in_hh = hh_id.replace(anz_erwachsene_hh)
    data = np.where(
        anz_erwachsene_in_hh == 1,
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            (2 + alleinerziehenden_mehrbedarf)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + (anz_erwachsene_in_hh - 2).clip(lower=0)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        ),
    )

    return kindersatz_m + data


def regelsatz_m_ab_2011(
    hh_id,
    anz_erwachsene_hh,
    alleinerziehenden_mehrbedarf,
    kindersatz_m,
    arbeitsl_geld_2_params,
):
    anz_erwachsene_in_hh = hh_id.replace(anz_erwachsene_hh)
    data = np.where(
        anz_erwachsene_in_hh == 1,
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf)
        + (
            arbeitsl_geld_2_params["regelsatz"][3]
            * (anz_erwachsene_in_hh - 2).clip(lower=0)
        ),
    )

    return kindersatz_m + data
