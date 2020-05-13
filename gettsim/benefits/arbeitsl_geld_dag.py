import pandas as pd

from gettsim.benefits.arbeitsl_geld import ui
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func


def arbeitsl_geld_m(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_vorj_m,
    wohnort_ost,
    kind,
    arbeitsl_lfdj_m,
    arbeitsl_vorj_m,
    arbeitsl_vor2j_m,
    ges_rente_m,
    arbeitsstunden_w,
    anz_kinder_tu,
    alter,
    jahr,
    params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_vorj_m,
            wohnort_ost,
            kind,
            arbeitsl_lfdj_m,
            arbeitsl_vorj_m,
            arbeitsl_vor2j_m,
            ges_rente_m,
            arbeitsstunden_w,
            anz_kinder_tu,
            alter,
            jahr,
        ],
        axis=1,
    )

    in_cols = [
        "p_id",
        "hh_id",
        "tu_id",
        "bruttolohn_vorj_m",
        "wohnort_ost",
        "kind",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
        "ges_rente_m",
        "arbeitsstunden_w",
        "anz_kinder_tu",
        "alter",
        "jahr",
    ]

    df = apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=in_cols,
        out_cols=["arbeitsl_geld_m"],
        func_kwargs={
            "params": params["arbeitsl_geld_params"],
            "soz_vers_beitr_params": params["soz_vers_beitr_params"],
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "eink_st_params": params["eink_st_params"],
            "soli_st_params": params["soli_st_params"],
        },
    )

    return df["arbeitsl_geld_m"]
