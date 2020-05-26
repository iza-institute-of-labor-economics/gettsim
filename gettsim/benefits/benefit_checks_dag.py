import numpy as np
import pandas as pd

from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func


OUT_COLS = ["kinderzuschlag_m", "wohngeld_m", "arbeitsl_geld_2_m"]


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
    regelbedarf_m_vorläufig,
    kinderzuschlag_temp_vorläufig,
    wohngeld_basis_hh_vorläufig,
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
            regelbedarf_m_vorläufig,
            kinderzuschlag_temp_vorläufig,
            wohngeld_basis_hh_vorläufig,
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
    regelbedarf_m_vorläufig,
    kinderzuschlag_temp_vorläufig,
    wohngeld_basis_hh_vorläufig,
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
            regelbedarf_m_vorläufig,
            kinderzuschlag_temp_vorläufig,
            wohngeld_basis_hh_vorläufig,
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
    regelbedarf_m_vorläufig,
    kinderzuschlag_temp_vorläufig,
    wohngeld_basis_hh_vorläufig,
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
            regelbedarf_m_vorläufig,
            kinderzuschlag_temp_vorläufig,
            wohngeld_basis_hh_vorläufig,
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


def regelbedarf_m_vorläufig_bis_2004(regelbedarf_m):
    return regelbedarf_m


def regelbedarf_m_vorläufig_ab_2005(regelbedarf_m, vermögen_hh, freibetrag_vermögen):
    """Set regelbedarf_m to zero if it exceeds the wealth exemption.

    If wealth exceeds the exemption, set benefits to zero (since ALG2 is not yet
    calculated, just set the need to zero)

    TODO: Remove the check vor `vermögen_hh`

    """
    return regelbedarf_m.where(
        vermögen_hh.isna() | (vermögen_hh <= freibetrag_vermögen), 0
    )


def kinderzuschlag_temp_vorläufig_bis_2004(kinderzuschlag_temp):
    return kinderzuschlag_temp


def kinderzuschlag_temp_vorläufig_ab_2005(
    kinderzuschlag_temp, vermögen_hh, freibetrag_vermögen
):
    """Set kindergeldzuschlag_temp to zero if it exceeds the wealth exemption.

    TODO: Remove the check vor `vermögen_hh`.

    """
    return kinderzuschlag_temp.where(
        vermögen_hh.isna() | (vermögen_hh <= freibetrag_vermögen), 0
    )


def wohngeld_basis_hh_vorläufig_bis_2004(wohngeld_basis_hh):
    return wohngeld_basis_hh


def wohngeld_basis_hh_vorläufig_ab_2005(wohngeld_basis_hh, vermögen_hh, haushaltsgröße):
    """Calculate a lump sum payment for wohngeld

    The payment depends on the wealth of the household and the number of household
    members.

    60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)

    TODO: Need to write numbers to params.

    TODO: Remove the check vor `vermögen_hh`

    """
    condition = vermögen_hh <= (60_000 + (30_000 * (haushaltsgröße - 1)))
    return wohngeld_basis_hh.where(vermögen_hh.isna() | condition, 0)
