"""Wealth checks for Arbeitslosengeld II/Bürgergeld."""

from _gettsim.functions.policy_function import policy_function


def grundfreibetrag_vermögen(
    kind: bool,
    alter: int,
    geburtsjahr: int,
    maximaler_grundfreibetrag_vermögen: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate wealth exemptions based on individuals age.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    maximaler_grundfreibetrag_vermögen
        See :func:`maximaler_grundfreibetrag_vermögen`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    threshold_years = list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].keys())
    if geburtsjahr <= threshold_years[0]:
        out = (
            next(iter(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values()))
            * alter
        )
    elif (geburtsjahr >= threshold_years[1]) and (not kind):
        out = (
            list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values())[1] * alter
        )
    else:
        out = 0.0

    return float(min(out, maximaler_grundfreibetrag_vermögen))


def maximaler_grundfreibetrag_vermögen(
    geburtsjahr: int,
    kind: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate maximal wealth exemptions by year of birth.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    threshold_years = list(
        arbeitsl_geld_2_params["vermögensgrundfreibetrag_obergrenze"].keys()
    )
    obergrenzen = list(
        arbeitsl_geld_2_params["vermögensgrundfreibetrag_obergrenze"].values()
    )
    if kind:
        out = 0.0
    else:
        if geburtsjahr < threshold_years[1]:
            out = obergrenzen[0]
        elif geburtsjahr < threshold_years[2]:
            out = obergrenzen[1]
        elif geburtsjahr < threshold_years[3]:
            out = obergrenzen[2]
        else:
            out = obergrenzen[3]

    return float(out)


@policy_function(start_date="2023-01-01")
def freibetrag_vermögen_in_karenzzeit_bg(
    arbeitsl_geld_2_params: dict,
    anz_personen_bg: int,
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    out = params["während_karenzzeit"] + (anz_personen_bg - 1) * params["normaler_satz"]

    return out


@policy_function(end_date="2022-12-31", name_in_dag="freibetrag_vermögen_bg")
def freibetrag_vermögen_bg_bis_2022(
    grundfreibetrag_vermögen_bg: float,
    anz_kinder_bis_17_bg: int,
    anz_personen_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    grundfreibetrag_vermögen_bg
        See :func:`grundfreibetrag_vermögen_bg`.
    anz_kinder_bis_17_bg
        See :func:`anz_kinder_bis_17_bg`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        grundfreibetrag_vermögen_bg
        + anz_kinder_bis_17_bg * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + anz_personen_bg * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@policy_function(start_date="2023-01-01", leaf_name="freibetrag_vermögen_bg")
def freibetrag_vermögen_bg_ab_2023(
    arbeitsl_geld_2_params: dict,
    anz_personen_bg: int,
    freibetrag_vermögen_in_karenzzeit_bg: float,
    bürgerg_bezug_vorj: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    freibetrag_vermögen_in_karenzzeit_bg
        See :func:`freibetrag_vermögen_in_karenzzeit_bg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = anz_personen_bg * params["normaler_satz"]
    else:
        out = freibetrag_vermögen_in_karenzzeit_bg

    return out
