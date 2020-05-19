import pandas as pd

from gettsim.benefits.unterhalt import uhv
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_unterhalt_vorschuss import INPUT_COLS
from gettsim.tests.test_unterhalt_vorschuss import OUT_COLS


def unterhaltsvors_m(
    p_id,
    hh_id,
    tu_id,
    alleinerziehend,
    alter,
    bruttolohn_m,
    sonstig_eink_m,
    kapital_eink_m,
    vermiet_eink_m,
    eink_selbstst_m,
    arbeitsl_geld_m,
    ges_rente_m,
    gem_veranlagt,
    jahr,
    unterhalt_params,
    kindergeld_params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            alleinerziehend,
            alter,
            bruttolohn_m,
            sonstig_eink_m,
            kapital_eink_m,
            vermiet_eink_m,
            eink_selbstst_m,
            arbeitsl_geld_m,
            ges_rente_m,
            gem_veranlagt,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=uhv,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": unterhalt_params,
            "kindergeld_params": kindergeld_params,
        },
    )

    return df["unterhaltsvors_m"]
