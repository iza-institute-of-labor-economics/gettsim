import numpy as np

from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def sum_basis_arbeitsl_geld_2_eink_hh(
    sum_arbeitsl_geld_2_eink_hh, kindergeld_m_hh, unterhaltsvors_m_hh
):
    """

    Parameters
    ----------
    sum_arbeitsl_geld_2_eink_hh
    kindergeld_m_hh
    unterhaltsvors_m_hh

    Returns
    -------

    """
    return sum_arbeitsl_geld_2_eink_hh + kindergeld_m_hh + unterhaltsvors_m_hh


def sum_arbeitsl_geld_2_eink(_arbeitsl_geld_2_eink, eink_anr_frei):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_eink
    eink_anr_frei

    Returns
    -------

    """
    return (_arbeitsl_geld_2_eink - eink_anr_frei).clip(lower=0)


def arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink, hh_id):
    """

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    hh_id

    Returns
    -------

    """
    return _arbeitsl_geld_2_brutto_eink.groupby(hh_id).sum()


def regelbedarf_m(regelsatz_m, kost_unterk_m):
    """

    Parameters
    ----------
    regelsatz_m
    kost_unterk_m

    Returns
    -------

    """
    return regelsatz_m + kost_unterk_m


def unterhaltsvors_m_hh(unterhaltsvors_m, hh_id):
    """

    Parameters
    ----------
    unterhaltsvors_m
    hh_id

    Returns
    -------

    """
    return unterhaltsvors_m.groupby(hh_id).sum()


def sum_arbeitsl_geld_2_eink_hh(sum_arbeitsl_geld_2_eink, hh_id):
    """

    Parameters
    ----------
    sum_arbeitsl_geld_2_eink
    hh_id

    Returns
    -------

    """
    return sum_arbeitsl_geld_2_eink.groupby(hh_id).sum()


def arbeitsl_geld_2_2005_netto_quote(
    bruttolohn_m, eink_st_m, soli_st_m, sozialv_beitr_m, arbeitsl_geld_2_params
):
    """Calculate Nettoquote.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = (
        bruttolohn_m
        - eink_st_m
        - soli_st_m
        - sozialv_beitr_m
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
        - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
    ).clip(lower=0)

    arbeitsl_geld_2_2005_netto_quote = alg2_2005_bne / bruttolohn_m

    return arbeitsl_geld_2_2005_netto_quote


def _arbeitsl_geld_2_brutto_eink(
    bruttolohn_m,
    sonstig_eink_m,
    eink_selbstst_m,
    vermiet_eink_m,
    kapital_eink_m,
    ges_rente_m,
    arbeitsl_geld_m,
    elterngeld_m,
):
    """
    Calculating the gross income relevant for alg2.

    Parameters
    ----------
    bruttolohn_m
    sonstig_eink_m
    eink_selbstst_m
    vermiet_eink_m
    kapital_eink_m
    ges_rente_m
    arbeitsl_geld_m
    elterngeld_m

    Returns
    -------

    """

    return (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbstst_m
        + vermiet_eink_m
        + kapital_eink_m
        + ges_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )


def _arbeitsl_geld_2_eink(
    _arbeitsl_geld_2_brutto_eink, eink_st_m, soli_st_m, sozialv_beitr_m
):
    """
    Relevant net income of alg2. The function deducts income tax and social security
    contributions.

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    eink_st_m
    soli_st_m
    sozialv_beitr_m

    Returns
    -------

    """
    return (
        _arbeitsl_geld_2_brutto_eink - eink_st_m - soli_st_m - sozialv_beitr_m
    ).clip(lower=0)


def _miete_pro_sqm(kaltmiete_m, heizkost_m, wohnfläche):
    """

    Parameters
    ----------
    kaltmiete_m
    heizkost_m
    wohnfläche

    Returns
    -------

    """
    return ((kaltmiete_m + heizkost_m) / wohnfläche).clip(upper=10)


def _berechtigte_wohnfläche(wohnfläche, bewohnt_eigentum, haushaltsgröße):
    """

    Parameters
    ----------
    wohnfläche
    bewohnt_eigentum
    haushaltsgröße

    Returns
    -------

    """
    out = wohnfläche * 0
    out.loc[bewohnt_eigentum] = wohnfläche.loc[bewohnt_eigentum].clip(
        upper=(80 + (haushaltsgröße.loc[bewohnt_eigentum] - 2).clip(lower=0) * 20)
    )
    out.loc[~bewohnt_eigentum] = wohnfläche.loc[~bewohnt_eigentum].clip(
        upper=(45 + (haushaltsgröße.loc[~bewohnt_eigentum] - 1).clip(lower=0) * 15)
    )
    return out


def kost_unterk_m(_berechtigte_wohnfläche, _miete_pro_sqm):
    """
    Only 'appropriate' housing costs are paid. Two possible options:
    1. Just pay rents no matter what
    return household["miete"] + household["heizkost"]
    2. Add restrictions regarding flat size and rent per square meter (set it 10€,
    slightly above average)

    Parameters
    ----------
    _berechtigte_wohnfläche
    _miete_pro_sqm

    Returns
    -------

    """
    return _berechtigte_wohnfläche * _miete_pro_sqm


def anz_kind_zwischen_0_6_per_hh(hh_id, kind, alter):
    alter_0_bis_6 = (0 <= alter) & (alter <= 6)
    return (kind & alter_0_bis_6).groupby(hh_id).transform("sum")


def anz_kind_zwischen_0_15_per_hh(hh_id, kind, alter):
    alter_0_bis_15 = (0 <= alter) & (alter <= 15)
    return (kind & alter_0_bis_15).groupby(hh_id).transform("sum")


def kind_zwischen_0_6(kind, alter):
    return kind & (0 <= alter) & (alter <= 6)


def kind_zwischen_7_13(kind, alter):
    return kind & (7 <= alter) & (alter <= 13)


def kind_zwischen_14_24(kind, alter):
    return kind & (14 <= alter) & (alter <= 24)


def anz_kinder_per_hh(hh_id, kind):
    return kind.groupby(hh_id).transform("sum")


def anz_erwachsene_per_hh(hh_id, kind):
    return (~kind).groupby(hh_id).transform("sum")


def alleinerziehenden_mehrbedarf(
    alleinerziehend,
    anz_kinder_per_hh,
    anz_kind_zwischen_0_6_per_hh,
    anz_kind_zwischen_0_15_per_hh,
    arbeitsl_geld_2_params,
):
    """Compute alleinerziehenden_mehrbedarf.

    Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    """
    lower = (
        arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"] * anz_kinder_per_hh
    )
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
    anz_erwachsene_per_hh,
    alleinerziehenden_mehrbedarf,
    kindersatz_m,
    arbeitsl_geld_2_params,
):
    data = np.where(
        anz_erwachsene_per_hh == 1,
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            (2 + alleinerziehenden_mehrbedarf)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + (anz_erwachsene_per_hh - 2).clip(lower=0)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        ),
    )

    return kindersatz_m + data


def regelsatz_m_ab_2011(
    anz_erwachsene_per_hh,
    alleinerziehenden_mehrbedarf,
    kindersatz_m,
    arbeitsl_geld_2_params,
):
    data = np.where(
        anz_erwachsene_per_hh == 1,
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf)
        + (
            arbeitsl_geld_2_params["regelsatz"][3]
            * (anz_erwachsene_per_hh - 2).clip(lower=0)
        ),
    )

    return kindersatz_m + data


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
        individual_rates=True,
        rates_multiplier=arbeitsl_geld_2_2005_netto_quote,
    )


def kinder_in_hh(kind, hh_id):
    return kind.groupby(hh_id).any()


def kinder_in_hh_individual(hh_id, kinder_in_hh):
    return hh_id.replace(kinder_in_hh).astype(bool)
