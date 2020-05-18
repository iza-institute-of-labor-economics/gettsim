import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.kindergeld import kindergeld
from gettsim.tests.test_kindergeld import INPUT_COLS
from gettsim.tests.test_kindergeld import OUT_COLS


def kindergeld_m_basis(
    hh_id,
    tu_id,
    p_id,
    alter,
    arbeitsstunden_w,
    in_ausbildung,
    bruttolohn_m,
    kindergeld_params,
):

    df = pd.concat(
        [hh_id, tu_id, p_id, alter, arbeitsstunden_w, in_ausbildung, bruttolohn_m],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": kindergeld_params},
    )

    return df["kindergeld_m_basis"]


def kindergeld_m_tu_basis(kindergeld_m_basis, tu_id):
    out = kindergeld_m_basis.groupby(tu_id).apply(sum)
    return out.rename("kindergeld_m_tu_basis")
