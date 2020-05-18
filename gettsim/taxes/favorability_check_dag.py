import numpy as np
import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.favorability_check import favorability_check
from gettsim.tests.test_favorability_check import INPUT_COLS
from gettsim.tests.test_favorability_check import OUT_COLS


def min_st(
    _st_kein_kind_freib_tu,
    _st_kind_freib_tu,
    kindergeld_m_tu_basis,
    eink_st_abzuege_params,
):
    st_kein_kind_freib = _st_kein_kind_freib_tu - kindergeld_m_tu_basis


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
    eink_st_abzuege_params,
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
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=favorability_check,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": eink_st_abzuege_params},
    )
    # Right now, we only select the max. Will be changed when function comes in place!
    return df["eink_st_m_tu"].groupby(tu_id).apply(max)


def eink_st_m(eink_st_m_tu, gem_veranlagt, kind, tu_id):
    """
    Assign Income tax to individuals
    Parameters
    ----------
    eink_st_m_tu
    gem_veranlagt
    kind
    tu_id

    Returns
    -------

    """
    out = np.select(
        [gem_veranlagt & ~kind, ~gem_veranlagt & ~kind, kind],
        [tu_id.replace(eink_st_m_tu) / 2, tu_id.replace(eink_st_m_tu), 0],
    )
    return pd.Series(data=out, index=tu_id.index, name="eink_st_m")


def kindergeld_m(
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
    eink_st_abzuege_params,
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
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=favorability_check,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": eink_st_abzuege_params},
    )

    return df["kindergeld_m"]


def kindergeld_m_hh(kindergeld_m, hh_id):
    """
    Aggregate Child benefit on the household level, as we could have several
    tax_units in one household.
    Parameters
    ----------
    kindergeld_m
    hh_id

    Returns
    -------

    """
    out = kindergeld_m.groupby(hh_id).apply(sum)
    return out.rename("kindergeld_m_hh")


def kindergeld_m_tu(kindergeld_m, tu_id):
    out = kindergeld_m.groupby(tu_id).apply(sum)
    return out.rename("kindergeld_m_tu")
