import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.favorability_check import favorability_check
from gettsim.tests.test_favorability_check import INPUT_COLS
from gettsim.tests.test_favorability_check import OUT_COLS


def eink_st_m_tu(
    hh_id,
    tu_id,
    p_id,
    gem_veranlagt,
    kind,
    _st_kein_kind_freib_tu,
    _st_kind_freib_tu,
    abgelt_st_m_tu,
    kindergeld_m_basis,
    kindergeld_m_tu_basis,
    jahr,
    params,
):

    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            gem_veranlagt,
            kind,
            _st_kein_kind_freib_tu,
            _st_kind_freib_tu,
            abgelt_st_m_tu,
            kindergeld_m_basis,
            kindergeld_m_tu_basis,
            jahr,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=favorability_check(),
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": params},
    )

    return df["eink_st_m_tu"]
