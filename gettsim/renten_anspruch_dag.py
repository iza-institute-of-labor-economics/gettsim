import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.renten_anspr import pensions
from gettsim.tests.test_renten_anspr import INPUT_COLS


def rente_anspr_m(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    wohnort_ost,
    alter,
    geburtsjahr,
    entgeltpunkte,
    jahr,
    renten_daten_params,
    soz_vers_beitr_params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            wohnort_ost,
            alter,
            geburtsjahr,
            entgeltpunkte,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=INPUT_COLS,
        out_cols=["rente_anspr_m"],
        func_kwargs={
            "renten_daten": renten_daten_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
        },
    )

    return df["rente_anspr_m"]
