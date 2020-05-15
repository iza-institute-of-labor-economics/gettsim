import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.eink_st import eink_st
from gettsim.tests.test_eink_st import INPUT_COLS
from gettsim.tests.test_eink_st import OUT_COLS


def abgelt_st_m(
    p_id,
    hh_id,
    tu_id,
    kind,
    _zu_versteuerndes_eink_kein_kind_freib,
    _zu_versteuerndes_eink_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
    brutto_eink_5,
    gem_veranlagt,
    brutto_eink_5_tu,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            _zu_versteuerndes_eink_kein_kind_freib,
            _zu_versteuerndes_eink_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
            brutto_eink_5,
            gem_veranlagt,
            brutto_eink_5_tu,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=eink_st,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_params": params["eink_st_params"],
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soli_st_params": params["soli_st_params"],
            "abgelt_st_params": params["abgelt_st_params"],
        },
    )

    return df["abgelt_st_m"]


def abgelt_st_m_tu(abgelt_st_m, tu_id):
    out = abgelt_st_m.groupby(tu_id).apply(sum)
    return out.rename("abgelt_st_m_tu")


def soli_st_m(
    p_id,
    hh_id,
    tu_id,
    kind,
    _zu_versteuerndes_eink_kein_kind_freib,
    _zu_versteuerndes_eink_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
    brutto_eink_5,
    gem_veranlagt,
    brutto_eink_5_tu,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            _zu_versteuerndes_eink_kein_kind_freib,
            _zu_versteuerndes_eink_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
            brutto_eink_5,
            gem_veranlagt,
            brutto_eink_5_tu,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=eink_st,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_params": params["eink_st_params"],
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soli_st_params": params["soli_st_params"],
            "abgelt_st_params": params["abgelt_st_params"],
        },
    )

    return df["soli_st_m"]


def soli_st_m_tu(soli_st_m, tu_id):
    out = soli_st_m.groupby(tu_id).apply(sum)
    return out.rename("soli_st_m_tu")


def _st_kein_kind_freib(
    p_id,
    hh_id,
    tu_id,
    kind,
    _zu_versteuerndes_eink_kein_kind_freib,
    _zu_versteuerndes_eink_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
    brutto_eink_5,
    gem_veranlagt,
    brutto_eink_5_tu,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            _zu_versteuerndes_eink_kein_kind_freib,
            _zu_versteuerndes_eink_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
            brutto_eink_5,
            gem_veranlagt,
            brutto_eink_5_tu,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=eink_st,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_params": params["eink_st_params"],
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soli_st_params": params["soli_st_params"],
            "abgelt_st_params": params["abgelt_st_params"],
        },
    )

    return df["_st_kein_kind_freib"]


def _st_kein_kind_freib_tu(_st_kein_kind_freib, tu_id):
    out = _st_kein_kind_freib.groupby(tu_id).apply(sum)
    return out.rename("_st_kein_kind_freib_tu")


def _st_kind_freib(
    p_id,
    hh_id,
    tu_id,
    kind,
    _zu_versteuerndes_eink_kein_kind_freib,
    _zu_versteuerndes_eink_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
    _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
    brutto_eink_5,
    gem_veranlagt,
    brutto_eink_5_tu,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            _zu_versteuerndes_eink_kein_kind_freib,
            _zu_versteuerndes_eink_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kind_freib,
            _zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib,
            brutto_eink_5,
            gem_veranlagt,
            brutto_eink_5_tu,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=eink_st,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_params": params["eink_st_params"],
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soli_st_params": params["soli_st_params"],
            "abgelt_st_params": params["abgelt_st_params"],
        },
    )

    return df["_st_kind_freib"]


def _st_kind_freib_tu(_st_kind_freib, tu_id):
    out = _st_kind_freib.groupby(tu_id).apply(sum)
    return out.rename("_st_kind_freib_tu")
