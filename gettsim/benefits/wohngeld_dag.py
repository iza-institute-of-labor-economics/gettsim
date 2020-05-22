import pandas as pd

from gettsim.benefits.wohngeld import wg
from gettsim.dynamic_function_generation import create_function
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_wohngeld import OUT_COLS


def wohngeld_basis_hh(
    hh_id,
    tu_id,
    p_id,
    tu_vorstand,
    kind,
    kaltmiete_m,
    heizkost_m,
    alleinerziehend,
    alter,
    immobilie_baujahr,
    kindergeld_anspruch,
    mietstufe,
    bruttolohn_m,
    ges_rente_m,
    _ertragsanteil,
    elterngeld_m,
    arbeitsl_geld_m,
    sonstig_eink_m,
    unterhaltsvors_m,
    brutto_eink_1,
    brutto_eink_4,
    brutto_eink_5,
    brutto_eink_6,
    eink_st_m,
    rentenv_beit_m,
    ges_krankenv_beit_m,
    behinderungsgrad,
    jahr,
    _st_rente_per_tu,
    arbeitsl_geld_m_per_tu,
    sonstig_eink_m_per_tu,
    brutto_eink_1_per_tu,
    brutto_eink_4_per_tu,
    brutto_eink_5_per_tu,
    brutto_eink_6_per_tu,
    eink_st_m_per_tu,
    rentenv_beit_m_per_tu,
    ges_krankenv_beit_m_per_tu,
    unterhaltsvors_m_per_tu,
    elterngeld_m_per_tu,
    _wohngeld_abzüge,
    _wohngeld_brutto_eink,
    wohngeld_params,
):

    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            tu_vorstand,
            kind,
            kaltmiete_m,
            heizkost_m,
            alleinerziehend,
            alter,
            immobilie_baujahr,
            kindergeld_anspruch,
            mietstufe,
            bruttolohn_m,
            ges_rente_m,
            _ertragsanteil,
            elterngeld_m,
            arbeitsl_geld_m,
            sonstig_eink_m,
            unterhaltsvors_m,
            brutto_eink_1,
            brutto_eink_4,
            brutto_eink_5,
            brutto_eink_6,
            eink_st_m,
            rentenv_beit_m,
            ges_krankenv_beit_m,
            behinderungsgrad,
            jahr,
            _st_rente_per_tu,
            arbeitsl_geld_m_per_tu,
            sonstig_eink_m_per_tu,
            brutto_eink_1_per_tu,
            brutto_eink_4_per_tu,
            brutto_eink_5_per_tu,
            brutto_eink_6_per_tu,
            eink_st_m_per_tu,
            rentenv_beit_m_per_tu,
            ges_krankenv_beit_m_per_tu,
            unterhaltsvors_m_per_tu,
            elterngeld_m_per_tu,
            _wohngeld_abzüge,
            _wohngeld_brutto_eink,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=wg,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={"params": wohngeld_params},
    )

    return df["wohngeld_basis_hh"]


def _st_rente_per_tu(tu_id, _ertragsanteil, ges_rente_m):
    _st_rente = _ertragsanteil * ges_rente_m
    return _st_rente.groupby(tu_id).transform("sum")


def _groupby_sum(group, variable):
    """TODO: Rewrite to simple sum."""
    return variable.groupby(group).transform("sum")


for inc in [
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "eink_st_m",
    "rentenv_beit_m",
    "ges_krankenv_beit_m",
    "unterhaltsvors_m",
    "elterngeld_m",
]:
    __new_function = create_function(
        _groupby_sum, inc + "_per_tu", {"group": "tu_id", "variable": inc}
    )

    exec(f"{inc}_per_tu = __new_function")


def _wohngeld_abzüge(
    eink_st_m_per_tu, rentenv_beit_m_per_tu, ges_krankenv_beit_m_per_tu, wohngeld_params
):
    abzug_stufen = (
        (eink_st_m_per_tu > 0) * 1
        + (rentenv_beit_m_per_tu > 0)
        + (ges_krankenv_beit_m_per_tu > 0)
    )

    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def _wohngeld_brutto_eink(
    brutto_eink_1_per_tu,
    brutto_eink_4_per_tu,
    brutto_eink_5_per_tu,
    brutto_eink_6_per_tu,
):
    return (
        brutto_eink_1_per_tu.clip(lower=0)
        + brutto_eink_4_per_tu.clip(lower=0)
        + brutto_eink_5_per_tu.clip(lower=0)
        + brutto_eink_6_per_tu.clip(lower=0)
    ) / 12
