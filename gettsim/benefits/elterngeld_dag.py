import pandas as pd

from gettsim.benefits.elterngeld import elterngeld
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif
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
    proxy_eink_vorj_elterngeld,
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
            proxy_eink_vorj_elterngeld,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
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
    proxy_eink_vorj_elterngeld,
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
            proxy_eink_vorj_elterngeld,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
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
    proxy_eink_vorj_elterngeld,
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
            proxy_eink_vorj_elterngeld,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
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
    proxy_eink_vorj_elterngeld,
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
            proxy_eink_vorj_elterngeld,
        ],
        axis=1,
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
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


def proxy_eink_vorj_elterngeld(
    beitr_bemess_grenze_rentenv,
    wohnort_ost,
    bruttolohn_vorj_m,
    elterngeld_params,
    eink_st_params,
    eink_st_abzuege_params,
    soli_st_params,
    soz_vers_beitr_params,
):
    """Calculating the claim for benefits depending on previous wage.

    TODO: This function requires `.fillna(0)` at the end. Investigate!

    """
    # Relevant wage is capped at the contribution thresholds
    max_wage = bruttolohn_vorj_m.clip(lower=None, upper=beitr_bemess_grenze_rentenv)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["elterngeld_soz_vers_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = st_tarif(
        12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"],
        eink_st_params,
    )

    prox_soli = piecewise_polynomial(
        prox_tax,
        lower_thresholds=soli_st_params["soli_st"]["lower_thresholds"],
        upper_thresholds=soli_st_params["soli_st"]["upper_thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return (
        (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0).fillna(0)
    )
