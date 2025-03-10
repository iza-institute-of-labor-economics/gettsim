"""Wealth checks for Arbeitslosengeld II/Bürgergeld."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def grundfreibetrag_vermögen(
    demographics__kind: bool,
    demographics__alter: int,
    demographics__geburtsjahr: int,
    maximaler_grundfreibetrag_vermögen: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate wealth exemptions based on individuals age.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    maximaler_grundfreibetrag_vermögen
        See :func:`maximaler_grundfreibetrag_vermögen`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    threshold_years = list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].keys())
    if demographics__geburtsjahr <= threshold_years[0]:
        out = (
            next(iter(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values()))
            * demographics__alter
        )
    elif (demographics__geburtsjahr >= threshold_years[1]) and (not demographics__kind):
        out = (
            list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values())[1]
            * demographics__alter
        )
    else:
        out = 0.0

    return float(min(out, maximaler_grundfreibetrag_vermögen))


@policy_function()
def maximaler_grundfreibetrag_vermögen(
    demographics__geburtsjahr: int,
    demographics__kind: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate maximal wealth exemptions by year of birth.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    demographics__hh_id
        See basic input variable :ref:`demographics__hh_id <demographics__hh_id>`.
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.
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
    if demographics__kind:
        out = 0.0
    else:
        if demographics__geburtsjahr < threshold_years[1]:
            out = obergrenzen[0]
        elif demographics__geburtsjahr < threshold_years[2]:
            out = obergrenzen[1]
        elif demographics__geburtsjahr < threshold_years[3]:
            out = obergrenzen[2]
        else:
            out = obergrenzen[3]

    return float(out)


@policy_function(start_date="2023-01-01")
def freibetrag_vermögen_in_karenzzeit_bg(
    arbeitsl_geld_2_params: dict,
    demographic_vars__anzahl_personen_bg: int,
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    demographic_vars__anzahl_personen_bg
        See :func:`demographic_vars__anzahl_personen_bg`.
    arbeitslosengeld_2_bezug_im_vorjahr
        See basic input variable :ref:`arbeitslosengeld_2_bezug_im_vorjahr <arbeitslosengeld_2_bezug_im_vorjahr>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    out = (
        params["während_karenzzeit"]
        + (demographic_vars__anzahl_personen_bg - 1) * params["normaler_satz"]
    )

    return out


@policy_function(end_date="2022-12-31", leaf_name="freibetrag_vermögen_bg")
def freibetrag_vermögen_bg_bis_2022(
    grundfreibetrag_vermögen_bg: float,
    demographic_vars__anzahl_kinder_bis_17_bg: int,
    demographic_vars__anzahl_personen_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    grundfreibetrag_vermögen_bg
        See :func:`grundfreibetrag_vermögen_bg`.
    demographic_vars__anzahl_kinder_bis_17_bg
        See :func:`demographic_vars__anzahl_kinder_bis_17_bg`.
    demographic_vars__anzahl_personen_bg
        See :func:`demographic_vars__anzahl_personen_bg`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        grundfreibetrag_vermögen_bg
        + demographic_vars__anzahl_kinder_bis_17_bg
        * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + demographic_vars__anzahl_personen_bg
        * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@policy_function(start_date="2023-01-01", leaf_name="freibetrag_vermögen_bg")
def freibetrag_vermögen_bg_ab_2023(
    arbeitsl_geld_2_params: dict,
    demographic_vars__anzahl_personen_bg: int,
    freibetrag_vermögen_in_karenzzeit_bg: float,
    arbeitslosengeld_2_bezug_im_vorjahr: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    demographic_vars__anzahl_personen_bg
        See :func:`demographic_vars__anzahl_personen_bg`.
    freibetrag_vermögen_in_karenzzeit_bg
        See :func:`freibetrag_vermögen_in_karenzzeit_bg`.
    arbeitslosengeld_2_bezug_im_vorjahr
        See basic input variable :ref:`arbeitslosengeld_2_bezug_im_vorjahr <arbeitslosengeld_2_bezug_im_vorjahr>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if arbeitslosengeld_2_bezug_im_vorjahr:
        out = demographic_vars__anzahl_personen_bg * params["normaler_satz"]
    else:
        out = freibetrag_vermögen_in_karenzzeit_bg

    return out
