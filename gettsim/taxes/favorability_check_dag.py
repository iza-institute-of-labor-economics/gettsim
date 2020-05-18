import numpy as np
import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.favorability_check import favorability_check
from gettsim.tests.test_favorability_check import INPUT_COLS
from gettsim.tests.test_favorability_check import OUT_COLS


def _beantrage_kind_freib_tu(
    _st_kein_kind_freib_tu, kindergeld_m_tu_basis, _st_kind_freib_tu
):
    st_kein_kind_freib = _st_kein_kind_freib_tu - 12 * kindergeld_m_tu_basis
    out = st_kein_kind_freib > _st_kind_freib_tu
    return out.rename("_beantrage_kind_freib_tu")


def eink_st_m_tu(
    _st_kein_kind_freib_tu, _st_kind_freib_tu, _beantrage_kind_freib_tu,
):
    """

    Parameters
    ----------
    _st_kein_kind_freib_tu
    _st_kind_freib_tu
    _beantrage_kind_freib_tu

    Returns
    -------

    """
    out = pd.Series(index=_beantrage_kind_freib_tu.index, name="eink_st_m_tu")
    out.loc[_beantrage_kind_freib_tu] = (
        _st_kind_freib_tu.loc[_beantrage_kind_freib_tu] / 12
    )
    out.loc[~_beantrage_kind_freib_tu] = (
        _st_kein_kind_freib_tu.loc[~_beantrage_kind_freib_tu] / 12
    )
    return out


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
