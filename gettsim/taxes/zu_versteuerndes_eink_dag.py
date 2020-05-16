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
        "brutto_eink_7",
        "brutto_eink_7_tu",
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


def brutto_eink_4(bruttolohn_m):
    """
    Wage income
    Parameters
    ----------
    bruttolohn_m

    Returns
    -------

    """
    out = np.maximum(12 * bruttolohn_m, 0)
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
