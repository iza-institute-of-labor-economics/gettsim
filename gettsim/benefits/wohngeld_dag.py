import pandas as pd

from gettsim.benefits.wohngeld import wg
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_wohngeld import INPUT_COLS
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
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=wg,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": wohngeld_params},
    )

    return df["wohngeld_basis_hh"]
