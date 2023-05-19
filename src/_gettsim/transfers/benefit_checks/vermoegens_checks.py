from _gettsim.shared import dates_active


def _kinderzuschl_nach_vermög_check_m_tu(
    _kinderzuschl_vor_vermög_check_m_tu: float,
    vermögen_bedürft_hh: float,
    arbeitsl_geld_2_vermög_freib_hh: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_tu
        See :func:`_kinderzuschl_vor_vermög_check_m_tu`.
    vermögen_bedürft_hh
        See basic input variable :ref:`vermögen_bedürft_hh <vermögen_bedürft_hh>`.
    arbeitsl_geld_2_vermög_freib_hh
        See :func:`arbeitsl_geld_2_vermög_freib_hh`.

    Returns
    -------

    """

    if vermögen_bedürft_hh > arbeitsl_geld_2_vermög_freib_hh:
        out = max(
            _kinderzuschl_vor_vermög_check_m_tu
            - (vermögen_bedürft_hh - arbeitsl_geld_2_vermög_freib_hh),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_tu
    return out


def wohngeld_nach_vermög_check_m_hh(
    wohngeld_vor_vermög_check_m_hh: float,
    vermögen_bedürft_hh: float,
    haushaltsgröße_hh: int,
    wohngeld_params: dict,
) -> float:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    The payment depends on the wealth of the household and the number of household
    members.

    Parameters
    ----------
    wohngeld_vor_vermög_check_m_hh
        See :func:`wohngeld_vor_vermög_check_m_hh`.
    vermögen_bedürft_hh
        See basic input variable :ref:`vermögen_bedürft_hh <vermögen_bedürft_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    if vermögen_bedürft_hh <= (
        wohngeld_params["vermögensgrundfreibetrag"]
        + (wohngeld_params["vermögensfreibetrag_pers"] * (haushaltsgröße_hh - 1))
    ):
        out = wohngeld_vor_vermög_check_m_hh
    else:
        out = 0.0

    return out


def _arbeitsl_geld_2_grundfreib_vermög(
    kind: bool,
    alter: int,
    geburtsjahr: int,
    _arbeitsl_geld_2_max_grundfreib_vermög: float,
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
    _arbeitsl_geld_2_max_grundfreib_vermög
        See :func:`_arbeitsl_geld_2_max_grundfreib_vermög`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    threshold_years = list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].keys())
    if geburtsjahr <= threshold_years[0]:
        out = (
            list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values())[0] * alter
        )
    elif (geburtsjahr >= threshold_years[1]) and (not kind):
        out = (
            list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values())[1] * alter
        )
    else:
        out = 0.0

    return float(min(out, _arbeitsl_geld_2_max_grundfreib_vermög))


def _arbeitsl_geld_2_max_grundfreib_vermög(
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


@dates_active(end="2022-12-31", change_name="arbeitsl_geld_2_vermög_freib_hh")
def arbeitsl_geld_2_vermög_freib_hh_bis_2022(
    _arbeitsl_geld_2_grundfreib_vermög_hh: float,
    anz_kinder_bis_17_hh: int,
    haushaltsgröße_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    _arbeitsl_geld_2_grundfreib_vermög_hh
        See :func:`_arbeitsl_geld_2_grundfreib_vermög_hh`.
    anz_kinder_bis_17_hh
        See basic input variable :ref:`anz_kinder_bis_17_hh <anz_kinder_bis_17_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        _arbeitsl_geld_2_grundfreib_vermög_hh
        + anz_kinder_bis_17_hh * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + haushaltsgröße_hh * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@dates_active(start="2023-01-01", change_name="arbeitsl_geld_2_vermög_freib_hh")
def arbeitsl_geld_2_vermög_freib_hh_ab_2023(
    arbeitsl_geld_2_params: dict,
    haushaltsgröße_hh: int,
    bürgerg_bezug_vorj: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = haushaltsgröße_hh * params["normaler_satz"]
    else:
        out = (
            params["während_karenzzeit"]
            + (haushaltsgröße_hh - 1) * params["normaler_satz"]
        )

    return out
