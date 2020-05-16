import numpy as np
import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.zu_versteuerndes_eink import zve


def _zu_versteuerndes_eink_kein_kind_freib(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    betreuungskost_m,
    eink_selbstst_m,
    kapital_eink_m,
    vermiet_eink_m,
    jahr_renteneintr,
    ges_rente_m,
    arbeitsstunden_w,
    in_ausbildung,
    gem_veranlagt,
    kind,
    behinderungsgrad,
    rentenv_beit_m,
    prv_rente_beit_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    alleinerziehend,
    alter,
    anz_kinder_tu,
    jahr,
    wohnort_ost,
    brutto_eink_1,
    brutto_eink_4,
    brutto_eink_5,
    brutto_eink_6,
    brutto_eink_7,
    behinderungsgrad_pauschalbetrag,
    ges_krankenv_beit_m,
    eink_st_abzuege_params,
    soz_vers_beitr_params,
    kindergeld_params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            betreuungskost_m,
            eink_selbstst_m,
            kapital_eink_m,
            vermiet_eink_m,
            jahr_renteneintr,
            ges_rente_m,
            arbeitsstunden_w,
            in_ausbildung,
            gem_veranlagt,
            kind,
            behinderungsgrad,
            rentenv_beit_m,
            prv_rente_beit_m,
            arbeitsl_v_beit_m,
            pflegev_beit_m,
            alleinerziehend,
            alter,
            anz_kinder_tu,
            jahr,
            brutto_eink_1,
            brutto_eink_4,
            brutto_eink_5,
            brutto_eink_6,
            brutto_eink_7,
            behinderungsgrad_pauschalbetrag,
            wohnort_ost,
            ges_krankenv_beit_m,
        ],
        axis=1,
    )

    out_cols = [
        "_zu_versteuerndes_eink_kein_kind_freib",
        "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib",
        "_zu_versteuerndes_eink_kind_freib",
        "_zu_versteuerndes_eink_abgelt_st_m_kind_freib",
        "kind_freib",
        "_ertragsanteil",
        "sonder",
        "hh_freib",
        "altersfreib",
        "vorsorge",
    ]

    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=["hh_id", "tu_id"],
        in_cols=df.columns.tolist(),
        out_cols=out_cols,
        func_kwargs={
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "kindergeld_params": kindergeld_params,
        },
    )

    return df["_zu_versteuerndes_eink_kein_kind_freib"]


# def altersfreib(
#     p_id,
#     hh_id,
#     tu_id,
#     bruttolohn_m,
#     betreuungskost_m,
#     eink_selbstst_m,
#     kapital_eink_m,
#     vermiet_eink_m,
#     jahr_renteneintr,
#     ges_rente_m,
#     arbeitsstunden_w,
#     in_ausbildung,
#     gem_veranlagt,
#     kind,
#     behinderungsgrad,
#     rentenv_beit_m,
#     prv_rente_beit_m,
#     arbeitsl_v_beit_m,
#     pflegev_beit_m,
#     alleinerziehend,
#     alter,
#     anz_kinder_tu,
#     jahr,
#     wohnort_ost,
#     ges_krankenv_beit_m,
#     eink_st_abzuege_params,
#     soz_vers_beitr_params,
#     kindergeld_params,
# ):
#
#     df = pd.concat(
#         [
#             p_id,
#             hh_id,
#             tu_id,
#             bruttolohn_m,
#             betreuungskost_m,
#             eink_selbstst_m,
#             kapital_eink_m,
#             vermiet_eink_m,
#             jahr_renteneintr,
#             ges_rente_m,
#             arbeitsstunden_w,
#             in_ausbildung,
#             gem_veranlagt,
#             kind,
#             behinderungsgrad,
#             rentenv_beit_m,
#             prv_rente_beit_m,
#             arbeitsl_v_beit_m,
#             pflegev_beit_m,
#             alleinerziehend,
#             alter,
#             anz_kinder_tu,
#             jahr,
#             wohnort_ost,
#             ges_krankenv_beit_m,
#         ],
#         axis=1,
#     )
#
#     df = apply_tax_transfer_func(
#         df,
#         tax_func=zve,
#         level=["hh_id", "tu_id"],
#         in_cols=INPUT_COLS,
#         out_cols=OUT_COLS,
#         func_kwargs={
#             "eink_st_abzuege_params": eink_st_abzuege_params,
#             "soz_vers_beitr_params": soz_vers_beitr_params,
#             "kindergeld_params": kindergeld_params,
#         },
#     )
#
#     return df["altersfreib"]
#
#
# def _zu_versteuerndes_eink_kind_freib(
#     p_id,
#     hh_id,
#     tu_id,
#     bruttolohn_m,
#     betreuungskost_m,
#     eink_selbstst_m,
#     kapital_eink_m,
#     vermiet_eink_m,
#     jahr_renteneintr,
#     ges_rente_m,
#     arbeitsstunden_w,
#     in_ausbildung,
#     gem_veranlagt,
#     kind,
#     behinderungsgrad,
#     rentenv_beit_m,
#     prv_rente_beit_m,
#     arbeitsl_v_beit_m,
#     pflegev_beit_m,
#     alleinerziehend,
#     alter,
#     anz_kinder_tu,
#     jahr,
#     wohnort_ost,
#     ges_krankenv_beit_m,
#     eink_st_abzuege_params,
#     soz_vers_beitr_params,
#     kindergeld_params,
# ):
#
#     df = pd.concat(
#         [
#             p_id,
#             hh_id,
#             tu_id,
#             bruttolohn_m,
#             betreuungskost_m,
#             eink_selbstst_m,
#             kapital_eink_m,
#             vermiet_eink_m,
#             jahr_renteneintr,
#             ges_rente_m,
#             arbeitsstunden_w,
#             in_ausbildung,
#             gem_veranlagt,
#             kind,
#             behinderungsgrad,
#             rentenv_beit_m,
#             prv_rente_beit_m,
#             arbeitsl_v_beit_m,
#             pflegev_beit_m,
#             alleinerziehend,
#             alter,
#             anz_kinder_tu,
#             jahr,
#             wohnort_ost,
#             ges_krankenv_beit_m,
#         ],
#         axis=1,
#     )
#
#     df = apply_tax_transfer_func(
#         df,
#         tax_func=zve,
#         level=["hh_id", "tu_id"],
#         in_cols=INPUT_COLS,
#         out_cols=OUT_COLS,
#         func_kwargs={
#             "eink_st_abzuege_params": eink_st_abzuege_params,
#             "soz_vers_beitr_params": soz_vers_beitr_params,
#             "kindergeld_params": kindergeld_params,
#         },
#     )
#
#     return df["_zu_versteuerndes_eink_kind_freib"]


def brutto_eink_1(eink_selbstst_m):
    """
    Income from Self-Employment

    Parameters
    ----------
    eink_selbstst_m

    Returns
    -------

    """
    out = np.maximum(12 * eink_selbstst_m, 0)
    return out.rename("brutto_eink_1")


def brutto_eink_1_tu(brutto_eink_1, tu_id):
    """


    Parameters
    ----------
    brutto_eink_1
    tu_id

    Returns
    -------

    """
    out = brutto_eink_1.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_1_tu")


def brutto_eink_4(bruttolohn_m, geringfügig_beschäftigt, eink_st_abzuege_params):
    """
    Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'
    Parameters
    ----------
    bruttolohn_m

    Returns
    -------

    """
    out = np.maximum(
        bruttolohn_m.multiply(12).subtract(
            eink_st_abzuege_params["werbungskostenpauschale"]
        ),
        0,
    )
    out.loc[geringfügig_beschäftigt] = 0
    return out.rename("brutto_eink_4")


def brutto_eink_4_tu(brutto_eink_4, tu_id):
    """

    Parameters
    ----------
    brutto_eink_4
    tu_id

    Returns
    -------

    """
    out = brutto_eink_4.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_4_tu")


def brutto_eink_5(kapital_eink_m):
    """
    Capital Income

    Parameters
    ----------
    kapital_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * kapital_eink_m, 0)
    return out.rename("brutto_eink_5")


def brutto_eink_5_tu(brutto_eink_5, tu_id):
    """

    Parameters
    ----------
    brutto_eink_5
    tu_id

    Returns
    -------

    """
    out = brutto_eink_5.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_5_tu")


def brutto_eink_6(vermiet_eink_m):
    """
    Income from rents

    Parameters
    ----------
    vermiet_eink_m

    Returns
    -------

    """
    out = np.maximum(12 * vermiet_eink_m, 0)
    return out.rename("brutto_eink_6")


def brutto_eink_6_tu(brutto_eink_6, tu_id):
    """

    Parameters
    ----------
    brutto_eink_6
    tu_id

    Returns
    -------

    """
    out = brutto_eink_6.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_6_tu")


def brutto_eink_7(ges_rente_m, _ertragsanteil):
    """
    Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions.

    Parameters
    ----------
    ges_rente_m
    _ertragsanteil

    Returns
    -------

    """
    out = _ertragsanteil.multiply(12 * ges_rente_m)
    return out.rename("brutto_eink_7")


def brutto_eink_7_tu(brutto_eink_7, tu_id):
    """

    Parameters
    ----------
    brutto_eink_7
    tu_id

    Returns
    -------

    """
    out = brutto_eink_7.groupby(tu_id).apply(sum)
    return out.rename("brutto_eink_7_tu")


def _ertragsanteil(jahr_renteneintr):
    """
    Calculate the share of pensions subject to income taxation.

    Parameters
    ----------
    jahr_renteneintr

    Returns
    -------

    """
    out = pd.Series(index=jahr_renteneintr.index, name="_ertragsanteil", dtype=float)
    out.loc[jahr_renteneintr <= 2004] = 0.27
    out.loc[jahr_renteneintr.between(2005, 2020)] = 0.5 + 0.02 * (
        jahr_renteneintr - 2005
    )
    out.loc[jahr_renteneintr.between(2021, 2040)] = 0.8 + 0.01 * (
        jahr_renteneintr - 2020
    )
    out.loc[jahr_renteneintr >= 2041] = 1
    return out


def sum_brutto_eink(brutto_eink_1, brutto_eink_4, brutto_eink_6, brutto_eink_7):
    """
    Since 2009 capital income is not subject to noraml taxation.
    Parameters
    ----------
    brutto_eink_1
    brutto_eink_4
    brutto_eink_6
    brutto_eink_7

    Returns
    -------

    """
    out = brutto_eink_1 + brutto_eink_4 + brutto_eink_6 + brutto_eink_7
    return out.rename("_sum_brutto_eink_ohne_kapital")


def _sum_brutto_eink_mit_kapital(
    _sum_brutto_eink_ohne_kapital, brutto_eink_5, eink_st_abzuege_params
):
    out = _sum_brutto_eink_ohne_kapital + np.maximum(
        brutto_eink_5
        - eink_st_abzuege_params["sparerpauschbetrag"]
        - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"],
        0,
    )
    return out.rename("_sum_brutto_eink_mit_kapital")


def behinderungsgrad_pauschalbetrag(behinderungsgrad, eink_st_abzuege_params):
    """
    Calculate the different deductions for different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
    eink_st_abzuege_params

    Returns
    -------

    """
    behinderungsgrad_stufe = [
        behinderungsgrad.between(25, 30),
        behinderungsgrad.between(35, 40),
        behinderungsgrad.between(45, 50),
        behinderungsgrad.between(55, 60),
        behinderungsgrad.between(65, 70),
        behinderungsgrad.between(75, 80),
        behinderungsgrad.between(85, 90),
        behinderungsgrad.between(95, 100),
    ]

    out = np.nan_to_num(
        np.select(
            behinderungsgrad_stufe,
            eink_st_abzuege_params["behinderten_pausch_betrag"].values(),
        )
    )
    return pd.Series(
        data=out, index=behinderungsgrad.index, name="behinderungsgrad_pauschalbetrag"
    )
