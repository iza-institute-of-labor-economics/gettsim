import numpy as np


def arbeitsl_geld_2_m_hh(
    arbeitsl_geld_2_m_minus_eink_hh,
    wohngeld_vorrang_hh,
    kinderzuschlag_vorrang_hh,
    wohngeld_kinderzuschlag_vorrang_hh,
    rentner_in_hh,
):
    """

    Parameters
    ----------
    arbeitsl_geld_2_m_minus_eink_hh
    wohngeld_vorrang_hh
    kinderzuschlag_vorrang_hh
    wohngeld_kinderzuschlag_vorrang_hh
    rentner_in_hh

    Returns
    -------

    """
    out = arbeitsl_geld_2_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschlag_vorrang_hh
        | wohngeld_kinderzuschlag_vorrang_hh
        | rentner_in_hh
    )
    out.loc[cond] = 0
    return out


def regelbedarf_m_hh(regelsatz_m_hh, kost_unterk_m_hh):
    """Basic monthly subsistence level, including cost of dwelling.

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

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    """
    # Get minimal Mehrbedarf share. Minimal rate times number of children
    lower = arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"] * anz_kinder_hh

    # Special case if 1 kid below 6 or 2,3 below 15.
    value = (
        (anz_kind_zwischen_0_6_hh >= 1)
        | ((2 <= anz_kind_zwischen_0_15_hh) & (anz_kind_zwischen_0_15_hh <= 3))
    ) * arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]

    # Clip value at calculated minimal share and given upper share
    out = alleinerziehend_hh * value.clip(
        lower=lower, upper=arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]
    )
    return out


def kindersatz_m_hh_bis_2010(
    anz_kind_zwischen_0_6_hh,
    anz_kind_zwischen_7_13_hh,
    anz_kind_zwischen_14_24_hh,
    arbeitsl_geld_2_params,
):
    """Since 2010 children get additional shares instead of lump sum payments

    Parameters
    ----------
    anz_kind_zwischen_0_6_hh
    anz_kind_zwischen_7_13_hh
    anz_kind_zwischen_14_24_hh
    arbeitsl_geld_2_params

    Returns
    -------

    """
    # Dictionary of additional shares.
    anteile = arbeitsl_geld_2_params["anteil_regelsatz"]

    # Multiply number of kids in age range with corresponding additional share
    out = arbeitsl_geld_2_params["regelsatz"] * (
        anteile["kinder_0_6"] * anz_kind_zwischen_0_6_hh
        + anteile["kinder_7_13"] * anz_kind_zwischen_7_13_hh
        + anteile["kinder_14_24"] * anz_kind_zwischen_14_24_hh
    )

    return out


def kindersatz_m_hh_ab_2011(
    anz_kind_zwischen_0_6_hh,
    anz_kind_zwischen_7_13_hh,
    anz_kind_zwischen_14_24_hh,
    arbeitsl_geld_2_params,
):
    """Here the sum in euro is directly in the law

    Parameters
    ----------
    anz_kind_zwischen_0_6_hh
    anz_kind_zwischen_7_13_hh
    anz_kind_zwischen_14_24_hh
    arbeitsl_geld_2_params

    Returns
    -------

    """
    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kind_zwischen_0_6_hh
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kind_zwischen_7_13_hh
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kind_zwischen_14_24_hh
    )

    return out


def regelsatz_m_hh_bis_2010(
    anz_erwachsene_hh,
    alleinerziehenden_mehrbedarf_hh,
    kindersatz_m_hh,
    arbeitsl_geld_2_params,
):
    """

    Parameters
    ----------
    anz_erwachsene_hh
    alleinerziehenden_mehrbedarf_hh
    kindersatz_m_hh
    arbeitsl_geld_2_params

    Returns
    -------

    """
    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf_hh),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
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
    """Calculating the regelsatz for each person.

    Parameters
    ----------
    anz_erwachsene_hh
    alleinerziehenden_mehrbedarf_hh
    kindersatz_m_hh
    arbeitsl_geld_2_params

    Returns
    -------

    """
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
