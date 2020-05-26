import numpy as np
import pandas as pd

from gettsim.dynamic_function_generation import create_function


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

    """
    return regelbedarf_m.where(vermögen_hh <= freibetrag_vermögen, 0)


def kinderzuschlag_temp_vorläufig_bis_2004(kinderzuschlag_temp):
    return kinderzuschlag_temp


def kinderzuschlag_temp_vorläufig_ab_2005(
    kinderzuschlag_temp, vermögen_hh, freibetrag_vermögen
):
    """Set kinderzuschlag_temp to zero if it exceeds the wealth exemption."""
    return kinderzuschlag_temp.where(vermögen_hh <= freibetrag_vermögen, 0)


def wohngeld_basis_hh_vorläufig_bis_2004(wohngeld_basis_hh):
    return wohngeld_basis_hh


def wohngeld_basis_hh_vorläufig_ab_2005(wohngeld_basis_hh, vermögen_hh, haushaltsgröße):
    """Calculate a lump sum payment for wohngeld

    The payment depends on the wealth of the household and the number of household
    members.

    60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)

    TODO: Need to write numbers to params.

    """
    condition = vermögen_hh <= (60_000 + (30_000 * (haushaltsgröße - 1)))
    return wohngeld_basis_hh.where(condition, 0)


def sum_wohngeld_m_arbeitsl_geld_2_eink(
    sum_basis_arbeitsl_geld_2_eink, wohngeld_basis_hh_vorläufig
):
    return sum_basis_arbeitsl_geld_2_eink + wohngeld_basis_hh_vorläufig


def sum_kinderzuschlag_arbeitsl_geld_2_eink(
    sum_basis_arbeitsl_geld_2_eink, kinderzuschlag_temp_vorläufig
):
    return sum_basis_arbeitsl_geld_2_eink + kinderzuschlag_temp_vorläufig


def sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink(
    sum_basis_arbeitsl_geld_2_eink,
    wohngeld_basis_hh_vorläufig,
    kinderzuschlag_temp_vorläufig,
):
    return (
        sum_basis_arbeitsl_geld_2_eink
        + wohngeld_basis_hh_vorläufig
        + kinderzuschlag_temp_vorläufig
    )


def _subtract_and_clip_at_zero(minuend, subtrahend):
    return (minuend - subtrahend).clip(lower=0)


for outcome in ["basis", "wohngeld_m", "kinderzuschlag", "wohngeld_m_kinderzuschlag"]:
    function_name = f"arbeitsl_geld_2_m_{outcome}"

    __new_function = create_function(
        _subtract_and_clip_at_zero,
        function_name,
        {
            "minuend": "regelbedarf_m_vorläufig",
            "subtrahend": f"sum_{outcome}_arbeitsl_geld_2_eink",
        },
    )
    exec(f"{function_name} = __new_function")
    del __new_function


def _vorrang_check(variable, arbeitsl_geld_2_m_basis):
    return (variable == 0) & (arbeitsl_geld_2_m_basis > 0)


for variable in ["wohngeld_m", "kinderzuschlag", "wohngeld_m_kinderzuschlag"]:
    function_name = f"{variable}_vorrang"

    __new_function = create_function(
        _vorrang_check, function_name, {"variable": f"arbeitsl_geld_2_m_{variable}"}
    )
    exec(f"{function_name} = __new_function")
    del __new_function


def anz_rentner_per_hh(hh_id, rentner):
    return rentner.groupby(hh_id).transform("sum")


def arbeitsl_geld_2_m(
    arbeitsl_geld_2_m_basis,
    wohngeld_m_vorrang,
    kinderzuschlag_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    anz_rentner_per_hh,
):
    cond = (
        wohngeld_m_vorrang | kinderzuschlag_vorrang | wohngeld_m_kinderzuschlag_vorrang
    )
    return arbeitsl_geld_2_m_basis.where(~cond & (anz_rentner_per_hh == 0), 0)


def wohngeld_m(
    wohngeld_basis_hh_vorläufig,
    wohngeld_m_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    arbeitsl_geld_2_m_basis,
    anz_rentner_per_hh,
):
    cond = (
        ~wohngeld_m_vorrang
        & ~wohngeld_m_kinderzuschlag_vorrang
        & (arbeitsl_geld_2_m_basis > 0)
    )
    return wohngeld_basis_hh_vorläufig.where(~cond & (anz_rentner_per_hh == 0), 0)


def kinderzuschlag_m(
    kinderzuschlag_temp_vorläufig,
    kinderzuschlag_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    arbeitsl_geld_2_m_basis,
    anz_rentner_per_hh,
):
    cond = (
        ~kinderzuschlag_vorrang
        & ~wohngeld_m_kinderzuschlag_vorrang
        & (arbeitsl_geld_2_m_basis > 0)
    )
    return kinderzuschlag_temp_vorläufig.where(~cond & (anz_rentner_per_hh == 0), 0)
