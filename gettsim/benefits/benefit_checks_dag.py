import pandas as pd
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_benefit_checks import OUT_COLS,INPUT_COLS


def kinderzuschlag_m(
    p_id,
    hh_id,
    tu_id,
    kind,
    rentner,
    alter,
    vermögen_hh,
    anz_erwachsene_hh,
    anz_minderj_hh,
    kinderzuschlag_temp,
    wohngeld_basis_hh,
    regelbedarf_m,
    sum_basis_arbeitsl_geld_2_eink,
    geburtsjahr,
    jahr,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            rentner,
            alter,
            vermögen_hh,
            anz_erwachsene_hh,
            anz_minderj_hh,
            kinderzuschlag_temp,
            wohngeld_basis_hh,
            regelbedarf_m,
            sum_basis_arbeitsl_geld_2_eink,
            geburtsjahr,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": params},
    )

    return df["kinderzuschlag_m"]


def wohngeld_m(
        p_id,
        hh_id,
        tu_id,
        kind,
        rentner,
        alter,
        vermögen_hh,
        anz_erwachsene_hh,
        anz_minderj_hh,
        kinderzuschlag_temp,
        wohngeld_basis_hh,
        regelbedarf_m,
        sum_basis_arbeitsl_geld_2_eink,
        geburtsjahr,
        jahr,
        params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            rentner,
            alter,
            vermögen_hh,
            anz_erwachsene_hh,
            anz_minderj_hh,
            kinderzuschlag_temp,
            wohngeld_basis_hh,
            regelbedarf_m,
            sum_basis_arbeitsl_geld_2_eink,
            geburtsjahr,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "params": params},
    )

    return df["wohngeld_m"]


def arbeitsl_geld_2_m(
        p_id,
        hh_id,
        tu_id,
        kind,
        rentner,
        alter,
        vermögen_hh,
        anz_erwachsene_hh,
        anz_minderj_hh,
        kinderzuschlag_temp,
        wohngeld_basis_hh,
        regelbedarf_m,
        sum_basis_arbeitsl_geld_2_eink,
        geburtsjahr,
        jahr,
        params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            rentner,
            alter,
            vermögen_hh,
            anz_erwachsene_hh,
            anz_minderj_hh,
            kinderzuschlag_temp,
            wohngeld_basis_hh,
            regelbedarf_m,
            sum_basis_arbeitsl_geld_2_eink,
            geburtsjahr,
            jahr,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={"params": params},
    )

    return df["arbeitsl_geld_2_m"]
