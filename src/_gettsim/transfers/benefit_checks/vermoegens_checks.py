from _gettsim.shared import policy_info


def _kinderzuschl_nach_vermög_check_m_bg(
    _kinderzuschl_vor_vermög_check_m_bg: float,
    vermögen_bedürft_bg: float,
    kinderzuschl_vermög_freib_bg: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_bg
        See :func:`_kinderzuschl_vor_vermög_check_m_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    kinderzuschl_vermög_freib_bg
        See :func:`kinderzuschl_vermög_freib_bg`.

    Returns
    -------

    """

    if vermögen_bedürft_bg > kinderzuschl_vermög_freib_bg:
        out = max(
            _kinderzuschl_vor_vermög_check_m_bg
            - (vermögen_bedürft_bg - kinderzuschl_vermög_freib_bg),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_bg
    return out


@policy_info(end_date="2022-12-31", name_in_dag="kinderzuschl_vermög_freib_bg")
def kinderzuschl_vermög_freib_bg_bis_2022(
    arbeitsl_geld_2_vermög_freib_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022.

    Parameters
    ----------
    arbeitsl_geld_2_vermög_freib_bg
        See :func:`arbeitsl_geld_2_vermög_freib_bg`.

    Returns
    -------

    """

    return arbeitsl_geld_2_vermög_freib_bg


@policy_info(start_date="2023-01-01", name_in_dag="kinderzuschl_vermög_freib_bg")
def kinderzuschl_vermög_freib_bg_ab_2023(
    _arbeitsl_geld_2_vermög_freib_karenzz_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023.

    Parameters
    ----------
    _arbeitsl_geld_2_vermög_freib_karenzz_bg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_bg`.

    Returns
    -------

    """

    return _arbeitsl_geld_2_vermög_freib_karenzz_bg


def wohngeld_nach_vermög_check_m_hh(
    wohngeld_vor_vermög_check_m_hh: float,
    vermögen_bedürft_hh: float,
    anz_personen_hh: int,
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
    anz_personen_hh
        See :func:`anz_personen_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    if vermögen_bedürft_hh <= (
        wohngeld_params["vermögensgrundfreibetrag"]
        + (wohngeld_params["vermögensfreibetrag_pers"] * (anz_personen_hh - 1))
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
            next(iter(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values()))
            * alter
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


@policy_info(end_date="2022-12-31", name_in_dag="arbeitsl_geld_2_vermög_freib_bg")
def arbeitsl_geld_2_vermög_freib_bg_bis_2022(
    _arbeitsl_geld_2_grundfreib_vermög_hh: float,
    anz_kinder_bis_17_hh: int,
    anz_personen_hh: int,
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
    anz_personen_hh
        See :func:`anz_personen_hh`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        _arbeitsl_geld_2_grundfreib_vermög_hh
        + anz_kinder_bis_17_hh * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + anz_personen_hh * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@policy_info(start_date="2023-01-01")
def _arbeitsl_geld_2_vermög_freib_karenzz_bg(
    arbeitsl_geld_2_params: dict,
    anz_personen_hh: int,
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    out = params["während_karenzzeit"] + (anz_personen_hh - 1) * params["normaler_satz"]

    return out


@policy_info(start_date="2023-01-01", name_in_dag="arbeitsl_geld_2_vermög_freib_bg")
def arbeitsl_geld_2_vermög_freib_bg_ab_2023(
    arbeitsl_geld_2_params: dict,
    anz_personen_hh: int,
    _arbeitsl_geld_2_vermög_freib_karenzz_bg: float,
    bürgerg_bezug_vorj: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    _arbeitsl_geld_2_vermög_freib_karenzz_bg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_bg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = anz_personen_hh * params["normaler_satz"]
    else:
        out = _arbeitsl_geld_2_vermög_freib_karenzz_bg

    return out
