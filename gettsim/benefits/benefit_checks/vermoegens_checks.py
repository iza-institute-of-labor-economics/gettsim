import numpy as np
import pandas as pd


def _regelbedarf_m_vermögens_check(regelbedarf_m, unter_vermögens_freibetrag):
    """Set regelbedarf_m to zero if it exceeds the wealth exemption.

    If wealth exceeds the exemption, set benefits to zero (since ALG2 is not yet
    calculated, just set the need to zero)

    """
    return regelbedarf_m.where(unter_vermögens_freibetrag, 0)


def _kinderzuschlag_m_vermögens_check(
    _kinderzuschlag_m_vorläufig, unter_vermögens_freibetrag
):
    """Set kinderzuschlag_temp to zero if it exceeds the wealth exemption."""
    return _kinderzuschlag_m_vorläufig.where(unter_vermögens_freibetrag, 0)


def _wohngeld_basis_hh_vermögens_check(
    hh_id, wohngeld_basis_hh, vermögen_hh, haushaltsgröße
):
    """Calculate a lump sum payment for wohngeld

    The payment depends on the wealth of the household and the number of household
    members.

    60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)

    TODO: Need to write numbers to params.

    """
    condition = hh_id.replace(vermögen_hh) <= (60_000 + (30_000 * (haushaltsgröße - 1)))
    return hh_id.replace(wohngeld_basis_hh).where(condition, 0)


def unter_vermögens_freibetrag(hh_id, vermögen_hh, freibetrag_vermögen_hh):
    return hh_id.replace(vermögen_hh <= freibetrag_vermögen_hh)


def freibetrag_alter(kind, alter, geburtsjahr, arbeitsl_geld_2_params):
    """Calculate exemptions based on individuals age."""

    out = alter * 0
    out.loc[geburtsjahr < 1948] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["vor_1948"]
        * alter.loc[geburtsjahr < 1948]
    )
    out.loc[(1948 <= geburtsjahr) & ~kind] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["standard"]
        * alter.loc[(1948 <= geburtsjahr) & ~kind]
    )

    return out


def freibetrag_alter_hh(hh_id, freibetrag_alter):
    return freibetrag_alter.groupby(hh_id).sum()


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


def freibetrag_vermögen_max_hh(hh_id, freibetrag_vermögen_max):
    return freibetrag_vermögen_max.groupby(hh_id).sum()


def freibetrag_vermögen_hh(
    freibetrag_alter_hh,
    anz_minderj_hh,
    haushaltsgröße_hh,
    freibetrag_vermögen_max_hh,
    arbeitsl_geld_2_params,
):
    return (
        freibetrag_alter_hh
        + anz_minderj_hh * arbeitsl_geld_2_params["vermögensfreibetrag"]["kind"]
        + (haushaltsgröße_hh - anz_minderj_hh)
        * arbeitsl_geld_2_params["vermögensfreibetrag"]["ausstattung"]
    ).clip(upper=freibetrag_vermögen_max_hh)
