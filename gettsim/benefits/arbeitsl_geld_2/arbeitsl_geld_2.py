import numpy as np


def arbeitsl_geld_2_m_hh(
    arbeitsl_geld_2_m_minus_eink_hh,
    wohngeld_vorrang_hh,
    kinderzuschlag_vorrang_hh,
    wohngeld_kinderzuschlag_vorrang_hh,
    anz_rentner_hh,
):
    out = arbeitsl_geld_2_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
    )
    out.loc[cond | (anz_rentner_hh != 0)] = 0
    return out


def regelbedarf_m_hh(regelsatz_m_hh, kost_unterk_m_hh):
    """

    Parameters
    ----------
    regelsatz_m_hh
    kost_unterk_m_hh

    Returns
    -------

    """
    return regelsatz_m_hh + kost_unterk_m_hh


def alleinerziehenden_mehrbedarf_hh(
    alleinerziehend_hh,
    anz_kinder_hh,
    anz_kind_zwischen_0_6_hh,
    anz_kind_zwischen_0_15_hh,
    arbeitsl_geld_2_params,
):
    """Compute alleinerziehenden_mehrbedarf.

    Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    """
    lower = arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"] * anz_kinder_hh
    value = (
        (anz_kind_zwischen_0_6_hh >= 1)
        | ((2 <= anz_kind_zwischen_0_15_hh) & (anz_kind_zwischen_0_15_hh <= 3))
    ) * arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]

    out = alleinerziehend_hh * value.clip(
        lower=lower, upper=arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]
    )
    return out


def kindersatz_m_hh_bis_2010(
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

    return per_child.groupby(hh_id).sum()


def kindersatz_m_hh_ab_2011(
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

    return per_child.groupby(hh_id).sum()


def regelsatz_m_hh_bis_2010(
    anz_erwachsene_hh,
    alleinerziehenden_mehrbedarf_hh,
    kindersatz_m_hh,
    arbeitsl_geld_2_params,
):
    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf_hh),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            (2 + alleinerziehenden_mehrbedarf_hh)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + (anz_erwachsene_hh - 2).clip(lower=0)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        ),
    )

    return kindersatz_m_hh + data


def regelsatz_m_hh_ab_2011(
    anz_erwachsene_hh,
    alleinerziehenden_mehrbedarf_hh,
    kindersatz_m_hh,
    arbeitsl_geld_2_params,
):
    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf_hh),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf_hh)
        + (
            arbeitsl_geld_2_params["regelsatz"][3]
            * (anz_erwachsene_hh - 2).clip(lower=0)
        ),
    )

    return kindersatz_m_hh + data
