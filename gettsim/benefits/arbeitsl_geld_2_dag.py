import copy

import pandas as pd

from gettsim.benefits.arbeitsl_geld_2 import alg2
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func


def sum_basis_arbeitsl_geld_2_eink_hh(
    sum_arbeitsl_geld_2_eink_hh, kindergeld_m_hh, unterhaltsvors_m_hh
):
    out = sum_arbeitsl_geld_2_eink_hh + kindergeld_m_hh + unterhaltsvors_m_hh

    return out.rename("sum_basis_arbeitsl_geld_2_eink")


def sum_arbeitsl_geld_2_eink(_arbeitsl_geld_2_eink, eink_anrechn_frei):
    out = (_arbeitsl_geld_2_eink - eink_anrechn_frei).clip(lower=0)

    return out.rename("sum_arbeitsl_geld_2_eink")


def arbeitsl_geld_2_brutto_eink_hh(_arbeitsl_geld_2_brutto_eink, hh_id):
    out = _arbeitsl_geld_2_brutto_eink.groupby(hh_id).apply(sum)
    return out.rename("arbeitsl_geld_2_brutto_eink_hh")


def alleinerziehenden_mehrbedarf(
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

    return df["alleinerziehenden_mehrbedarf"]


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
    out = unterhaltsvors_m.groupby(hh_id).apply(sum)
    return out.rename("unterhaltsvors_m_hh")


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
    out = sum_arbeitsl_geld_2_eink.groupby(hh_id).apply(sum)
    return out.rename("sum_arbeitsl_geld_2_eink_hh")


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

    out = (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbstst_m
        + vermiet_eink_m
        + kapital_eink_m
        + ges_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )
    return out.rename("_arbeitsl_geld_2_brutto_eink")


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
    out = _arbeitsl_geld_2_brutto_eink - eink_st_m - soli_st_m - sozialv_beit_m
    out = out.clip(lower=0)
    return out.rename("_arbeitsl_geld_2_eink")


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
    out = ((kaltmiete_m + heizkost_m) / wohnfläche).clip(upper=10)
    return out.rename("miete_pro_sqm")


def _berechtigte_wohnfläche(wohnfläche, bewohnt_eigentum, hh_größe, hh_id):
    out = copy.deepcopy(wohnfläche) * 0
    hh_größe_individual = hh_id.replace(hh_größe)
    out.loc[bewohnt_eigentum] = wohnfläche.loc[bewohnt_eigentum].clip(
        upper=(80 + (hh_größe_individual.loc[bewohnt_eigentum] - 2).clip(lower=0) * 20)
    )
    out.loc[~bewohnt_eigentum] = wohnfläche.loc[~bewohnt_eigentum].clip(
        upper=(45 + (hh_größe_individual.loc[~bewohnt_eigentum] - 1).clip(lower=0) * 15)
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


def hh_größe(hh_id):
    out = (hh_id.astype(int)).groupby(hh_id).size()
    return out.rename("hh_größe")
