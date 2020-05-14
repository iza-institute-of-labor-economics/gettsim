import pandas as pd

from gettsim.benefits.kinderzuschlag import kiz
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_kinderzuschlag import INPUT_COLS
from gettsim.tests.test_kinderzuschlag import OUT_COLS


def kinderzuschlag_temp(
    p_id,
    hh_id,
    tu_id,
    kind,
    alter,
    arbeitsstunden_w,
    bruttolohn_m,
    in_ausbildung,
    kaltmiete_m,
    heizkost_m,
    alleinerziehend,
    kindergeld_anspruch,
    alleinerziehenden_mehrbedarf,
    anz_erw_tu,
    anz_kinder_tu,
    arbeitsl_geld_2_brutto_eink_hh,
    sum_arbeitsl_geld_2_eink_hh,
    kindergeld_m_hh,
    unterhaltsvors_m,
    jahr,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            alter,
            arbeitsstunden_w,
            bruttolohn_m,
            in_ausbildung,
            kaltmiete_m,
            heizkost_m,
            alleinerziehend,
            kindergeld_anspruch,
            alleinerziehenden_mehrbedarf,
            anz_erw_tu,
            anz_kinder_tu,
            arbeitsl_geld_2_brutto_eink_hh,
            sum_arbeitsl_geld_2_eink_hh,
            kindergeld_m_hh,
            unterhaltsvors_m,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=kiz,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": params["kinderzuschlag_params"],
            "arbeitsl_geld_2_params": params["arbeitsl_geld_2_params"],
        },
    )

    return df["kinderzuschlag_temp"]
