import pandas as pd

from gettsim.benefits.elterngeld import elterngeld
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_elterngeld import INPUT_COLS
from gettsim.tests.test_elterngeld import OUT_COLS


def elterngeld_m(
    hh_id,
    tu_id,
    p_id,
    kind,
    bruttolohn_m,
    bruttolohn_vorj_m,
    wohnort_ost,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    geburtsjahr,
    geburtsmonat,
    geburtstag,
    m_elterngeld_mut,
    m_elterngeld_vat,
    m_elterngeld,
    jahr,
    elterngeld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            kind,
            bruttolohn_m,
            bruttolohn_vorj_m,
            wohnort_ost,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            geburtsjahr,
            geburtsmonat,
            geburtstag,
            m_elterngeld_mut,
            m_elterngeld_vat,
            m_elterngeld,
            jahr,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["elterngeld_m"]


def geschw_bonus(
    hh_id,
    tu_id,
    p_id,
    kind,
    bruttolohn_m,
    bruttolohn_vorj_m,
    wohnort_ost,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    geburtsjahr,
    geburtsmonat,
    geburtstag,
    m_elterngeld_mut,
    m_elterngeld_vat,
    m_elterngeld,
    jahr,
    elterngeld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            kind,
            bruttolohn_m,
            bruttolohn_vorj_m,
            wohnort_ost,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            geburtsjahr,
            geburtsmonat,
            geburtstag,
            m_elterngeld_mut,
            m_elterngeld_vat,
            m_elterngeld,
            jahr,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["geschw_bonus"]


def anz_mehrlinge_bonus(
    hh_id,
    tu_id,
    p_id,
    kind,
    bruttolohn_m,
    bruttolohn_vorj_m,
    wohnort_ost,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    geburtsjahr,
    geburtsmonat,
    geburtstag,
    m_elterngeld_mut,
    m_elterngeld_vat,
    m_elterngeld,
    jahr,
    elterngeld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            kind,
            bruttolohn_m,
            bruttolohn_vorj_m,
            wohnort_ost,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            geburtsjahr,
            geburtsmonat,
            geburtstag,
            m_elterngeld_mut,
            m_elterngeld_vat,
            m_elterngeld,
            jahr,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["anz_mehrlinge_bonus"]


def elternzeit_anspruch(
    hh_id,
    tu_id,
    p_id,
    kind,
    bruttolohn_m,
    bruttolohn_vorj_m,
    wohnort_ost,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    geburtsjahr,
    geburtsmonat,
    geburtstag,
    m_elterngeld_mut,
    m_elterngeld_vat,
    m_elterngeld,
    jahr,
    elterngeld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            kind,
            bruttolohn_m,
            bruttolohn_vorj_m,
            wohnort_ost,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            geburtsjahr,
            geburtsmonat,
            geburtstag,
            m_elterngeld_mut,
            m_elterngeld_vat,
            m_elterngeld,
            jahr,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["elternzeit_anspruch"]
