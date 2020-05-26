import copy

import pandas as pd

from gettsim.benefits.arbeitsl_geld_2 import alg2
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func


def sum_basis_arbeitsl_geld_2_eink_hh(
    sum_arbeitsl_geld_2_eink_hh, kindergeld_m_hh, unterhaltsvors_m_hh
):
    return sum_arbeitsl_geld_2_eink_hh + kindergeld_m_hh + unterhaltsvors_m_hh


def sum_arbeitsl_geld_2_eink(_arbeitsl_geld_2_eink, eink_anrechn_frei):
    return (_arbeitsl_geld_2_eink - eink_anrechn_frei).clip(lower=0)


def arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink, hh_id):
    return _arbeitsl_geld_2_brutto_eink.groupby(hh_id).sum()


# def alleinerziehenden_mehrbedarf(
#     p_id,
#     hh_id,
#     tu_id,
#     kind,
#     alter,
#     kaltmiete_m,
#     heizkost_m,
#     wohnfläche,
#     bewohnt_eigentum,
#     alleinerziehend,
#     bruttolohn_m,
#     ges_rente_m,
#     kapital_eink_m,
#     arbeitsl_geld_m,
#     sonstig_eink_m,
#     eink_selbstst_m,
#     vermiet_eink_m,
#     eink_st_m,
#     soli_st_m,
#     sozialv_beit_m,
#     unterhaltsvors_m,
#     elterngeld_m,
#     jahr,
#     anz_kind_zwischen_0_6_per_hh,
#     anz_kind_zwischen_0_15_per_hh,
#     arbeitsl_geld_2_2005_netto_quote,
#     arbeitsl_geld_2_params,
# ):
#     df = pd.concat(
#         [
#             p_id,
#             hh_id,
#             tu_id,
#             kind,
#             alter,
#             kaltmiete_m,
#             heizkost_m,
#             wohnfläche,
#             bewohnt_eigentum,
#             alleinerziehend,
#             bruttolohn_m,
#             ges_rente_m,
#             kapital_eink_m,
#             arbeitsl_geld_m,
#             sonstig_eink_m,
#             eink_selbstst_m,
#             vermiet_eink_m,
#             eink_st_m,
#             soli_st_m,
#             sozialv_beit_m,
#             unterhaltsvors_m,
#             elterngeld_m,
#             jahr,
#             anz_kind_zwischen_0_6_per_hh,
#             anz_kind_zwischen_0_15_per_hh,
#             arbeitsl_geld_2_2005_netto_quote,
#         ],
#         axis=1,
#     )

#     out_cols = [
#         "sum_basis_arbeitsl_geld_2_eink",
#         "sum_arbeitsl_geld_2_eink",
#         "arbeitsl_geld_2_brutto_eink_hh",
#         "alleinerziehenden_mehrbedarf",
#         "regelbedarf_m",
#         "regelsatz_m",
#         "unterhaltsvors_m_hh",
#         "eink_anrechn_frei",
#         "arbeitsl_geld_2_eink",
#         "sum_arbeitsl_geld_2_eink_hh",
#     ]

#     df = apply_tax_transfer_func(
#         df,
#         tax_func=alg2,
#         level=["hh_id"],
#         in_cols=df.columns.tolist(),
#         out_cols=out_cols,
#         func_kwargs={"params": arbeitsl_geld_2_params},
#     )

#     return df["alleinerziehenden_mehrbedarf"]


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


def regelsatz_m(
    p_id,
    hh_id,
    tu_id,
    kind,
    alter,
    alleinerziehend,
    alleinerziehenden_mehrbedarf,
    bruttolohn_m,
    ges_rente_m,
    kapital_eink_m,
    arbeitsl_geld_m,
    sonstig_eink_m,
    eink_selbstst_m,
    vermiet_eink_m,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    unterhaltsvors_m,
    elterngeld_m,
    jahr,
    anz_kind_zwischen_0_6_per_hh,
    anz_kind_zwischen_0_15_per_hh,
    arbeitsl_geld_2_2005_netto_quote,
    arbeitsl_geld_2_params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            alter,
            alleinerziehend,
            alleinerziehenden_mehrbedarf,
            bruttolohn_m,
            ges_rente_m,
            kapital_eink_m,
            arbeitsl_geld_m,
            sonstig_eink_m,
            eink_selbstst_m,
            vermiet_eink_m,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            unterhaltsvors_m,
            elterngeld_m,
            jahr,
            anz_kind_zwischen_0_6_per_hh,
            anz_kind_zwischen_0_15_per_hh,
            arbeitsl_geld_2_2005_netto_quote,
        ],
        axis=1,
    )

    out_cols = [
        "sum_basis_arbeitsl_geld_2_eink",
        "sum_arbeitsl_geld_2_eink",
        "arbeitsl_geld_2_brutto_eink_hh",
        "alleinerziehenden_mehrbedarf",
        "regelbedarf_m",
        "regelsatz_m",
        "unterhaltsvors_m_hh",
        "eink_anrechn_frei",
        "arbeitsl_geld_2_eink",
        "sum_arbeitsl_geld_2_eink_hh",
    ]

    df = apply_tax_transfer_func(
        df,
        tax_func=alg2,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )

    return df["regelsatz_m"]


def unterhaltsvors_m_hh(unterhaltsvors_m, hh_id):
    return unterhaltsvors_m.groupby(hh_id).sum()


def eink_anrechn_frei(
    p_id,
    hh_id,
    tu_id,
    kind,
    alter,
    kaltmiete_m,
    heizkost_m,
    wohnfläche,
    bewohnt_eigentum,
    alleinerziehend,
    alleinerziehenden_mehrbedarf,
    bruttolohn_m,
    ges_rente_m,
    kapital_eink_m,
    arbeitsl_geld_m,
    sonstig_eink_m,
    eink_selbstst_m,
    vermiet_eink_m,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    unterhaltsvors_m,
    elterngeld_m,
    jahr,
    anz_kind_zwischen_0_6_per_hh,
    anz_kind_zwischen_0_15_per_hh,
    arbeitsl_geld_2_2005_netto_quote,
    arbeitsl_geld_2_params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            alter,
            kaltmiete_m,
            heizkost_m,
            wohnfläche,
            bewohnt_eigentum,
            alleinerziehend,
            alleinerziehenden_mehrbedarf,
            bruttolohn_m,
            ges_rente_m,
            kapital_eink_m,
            arbeitsl_geld_m,
            sonstig_eink_m,
            eink_selbstst_m,
            vermiet_eink_m,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            unterhaltsvors_m,
            elterngeld_m,
            jahr,
            anz_kind_zwischen_0_6_per_hh,
            anz_kind_zwischen_0_15_per_hh,
            arbeitsl_geld_2_2005_netto_quote,
        ],
        axis=1,
    )

    out_cols = [
        "sum_basis_arbeitsl_geld_2_eink",
        "sum_arbeitsl_geld_2_eink",
        "arbeitsl_geld_2_brutto_eink_hh",
        "alleinerziehenden_mehrbedarf",
        "regelbedarf_m",
        "regelsatz_m",
        "eink_anrechn_frei",
        "arbeitsl_geld_2_eink",
        "sum_arbeitsl_geld_2_eink_hh",
    ]

    df = apply_tax_transfer_func(
        df,
        tax_func=alg2,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )

    return df["eink_anrechn_frei"]


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
    bruttolohn_m, eink_st_m, soli_st_m, sozialv_beit_m, arbeitsl_geld_2_params
):
    """Calculate Nettoquote.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = (
        bruttolohn_m
        - eink_st_m
        - soli_st_m
        - sozialv_beit_m
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
    _arbeitsl_geld_2_brutto_eink, eink_st_m, soli_st_m, sozialv_beit_m
):
    """
    Relevant net income of alg2. The function deducts income tax and social security
    contributions.

    Parameters
    ----------
    _arbeitsl_geld_2_brutto_eink
    eink_st_m
    soli_st_m
    sozialv_beit_m

    Returns
    -------

    """
    return (_arbeitsl_geld_2_brutto_eink - eink_st_m - soli_st_m - sozialv_beit_m).clip(
        lower=0
    )


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
    out = copy.deepcopy(wohnfläche) * 0
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


def anz_kinder_per_hh(hh_id, kind):
    return kind.groupby(hh_id).transform("sum")


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
