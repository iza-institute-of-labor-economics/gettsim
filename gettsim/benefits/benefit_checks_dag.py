import numpy as np
import pandas as pd

from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_benefit_checks import OUT_COLS


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
    freibetrag_alter,
    freibetrag_alter_per_hh,
    freibetrag_vermögen_max,
    freibetrag_vermögen_max_per_hh,
    freibetrag_vermögen,
    # regelbedarf_m_angepasst,
    # kinderzuschlag_temp_angepasst,
    arbeitsl_geld_2_params,
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
            freibetrag_alter,
            freibetrag_alter_per_hh,
            freibetrag_vermögen_max,
            freibetrag_vermögen_max_per_hh,
            freibetrag_vermögen,
            # regelbedarf_m_angepasst,
            # kinderzuschlag_temp_angepasst,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={"params": arbeitsl_geld_2_params},
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
    freibetrag_alter,
    freibetrag_alter_per_hh,
    freibetrag_vermögen_max,
    freibetrag_vermögen_max_per_hh,
    freibetrag_vermögen,
    # regelbedarf_m_angepasst,
    # kinderzuschlag_temp_angepasst,
    arbeitsl_geld_2_params,
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
            freibetrag_alter,
            freibetrag_alter_per_hh,
            freibetrag_vermögen_max,
            freibetrag_vermögen_max_per_hh,
            freibetrag_vermögen,
            # regelbedarf_m_angepasst,
            # kinderzuschlag_temp_angepasst,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={"params": arbeitsl_geld_2_params},
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
    freibetrag_alter,
    freibetrag_alter_per_hh,
    freibetrag_vermögen_max,
    freibetrag_vermögen_max_per_hh,
    freibetrag_vermögen,
    # regelbedarf_m_angepasst,
    # kinderzuschlag_temp_angepasst,
    arbeitsl_geld_2_params,
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
            freibetrag_alter,
            freibetrag_alter_per_hh,
            freibetrag_vermögen_max,
            freibetrag_vermögen_max_per_hh,
            freibetrag_vermögen,
            # regelbedarf_m_angepasst,
            # kinderzuschlag_temp_angepasst,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )

    return df["arbeitsl_geld_2_m"]


def freibetrag_alter(kind, alter, geburtsjahr, arbeitsl_geld_2_params):
    """Calculate exemptions based on individuals age."""
    conditions = [
        geburtsjahr < 1948,
        (1948 <= geburtsjahr) & ~kind,
        True,
    ]

    choices = [
        arbeitsl_geld_2_params["vermögensfreibetrag"]["vor_1948"] * alter,
        arbeitsl_geld_2_params["vermögensfreibetrag"]["standard"] * alter,
        0,
    ]

    data = np.select(conditions, choices)

    return pd.Series(index=alter.index, data=data)


def freibetrag_alter_per_hh(hh_id, freibetrag_alter):
    return freibetrag_alter.groupby(hh_id).transform("sum")


def freibetrag_vermögen_max(geburtsjahr, kind, arbeitsl_geld_2_params):
    conditions = [
        geburtsjahr < 1957,
        (1958 <= geburtsjahr) & (geburtsjahr <= 1963),
        (1964 <= geburtsjahr) & ~kind,
        True,
    ]

    choices = [
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1948_bis_1957"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1958_bis_1963"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["nach_1963"],
        0,
    ]

    data = np.select(conditions, choices)

    return pd.Series(index=geburtsjahr.index, data=data)


def freibetrag_vermögen_max_per_hh(hh_id, freibetrag_vermögen_max):
    return freibetrag_vermögen_max.groupby(hh_id).transform("sum")


def freibetrag_vermögen(
    freibetrag_alter_per_hh,
    anz_minderj_hh,
    kind,
    haushaltsgröße,
    freibetrag_vermögen_max_per_hh,
    arbeitsl_geld_2_params,
):
    return (
        freibetrag_alter_per_hh
        + anz_minderj_hh * arbeitsl_geld_2_params["vermögensfreibetrag"]["kind"]
        + (haushaltsgröße - anz_minderj_hh)
        * arbeitsl_geld_2_params["vermögensfreibetrag"]["ausstattung"]
    ).clip(upper=freibetrag_vermögen_max_per_hh)


# def regelbedarf_m_angepasst(regelbedarf_m, vermögen_hh, freibetrag_vermögen):
#     """Adjust regelbedarf_m.

#     If wealth exceeds the exemption, set benefits to zero (since ALG2 is not yet
#     calculated, just set the need to zero)

#     """
#     return regelbedarf_m.where(vermögen_hh <= freibetrag_vermögen, 0)


# def kinderzuschlag_temp_angepasst(
#     kinderzuschlag_temp, vermögen_hh, freibetrag_vermögen
# ):
#     return kinderzuschlag_temp.where(vermögen_hh <= freibetrag_vermögen, 0)
