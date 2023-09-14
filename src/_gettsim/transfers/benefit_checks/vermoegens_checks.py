from _gettsim.shared import dates_active


def _kinderzuschl_nach_vermög_check_m_tu(
    _kinderzuschl_vor_vermög_check_m_tu: float,
    vermögen_bedürft_vg: float,
    kinderzuschl_vermög_freib_vg: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_tu
        See :func:`_kinderzuschl_vor_vermög_check_m_tu`.
    vermögen_bedürft_vg
        See basic input variable :ref:`vermögen_bedürft_vg <vermögen_bedürft_vg>`.
    kinderzuschl_vermög_freib_vg
        See :func:`kinderzuschl_vermög_freib_vg`.

    Returns
    -------

    """

    if vermögen_bedürft_vg > kinderzuschl_vermög_freib_vg:
        out = max(
            _kinderzuschl_vor_vermög_check_m_tu
            - (vermögen_bedürft_vg - kinderzuschl_vermög_freib_vg),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_tu
    return out


@dates_active(end="2022-12-31", change_name="kinderzuschl_vermög_freib_vg")
def kinderzuschl_vermög_freib_vg_bis_2022(
    arbeitsl_geld_2_vermög_freib_vg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022.

    Parameters
    ----------
    arbeitsl_geld_2_vermög_freib_vg
        See :func:`arbeitsl_geld_2_vermög_freib_vg`.

    Returns
    -------

    """

    return arbeitsl_geld_2_vermög_freib_vg


@dates_active(start="2023-01-01", change_name="kinderzuschl_vermög_freib_vg")
def kinderzuschl_vermög_freib_vg_ab_2023(
    _arbeitsl_geld_2_vermög_freib_karenzz_vg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023.

    Parameters
    ----------
    _arbeitsl_geld_2_vermög_freib_karenzz_vg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_vg`.

    Returns
    -------

    """

    return _arbeitsl_geld_2_vermög_freib_karenzz_vg


def wohngeld_nach_vermög_check_m_vg(
    wohngeld_vor_vermög_check_m_vg: float,
    vermögen_bedürft_vg: float,
    haushaltsgröße_vg: int,
    wohngeld_params: dict,
) -> float:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    The payment depends on the wealth of the household and the number of household
    members.

    Parameters
    ----------
    wohngeld_vor_vermög_check_m_vg
        See :func:`wohngeld_vor_vermög_check_m_vg`.
    vermögen_bedürft_vg
        See basic input variable :ref:`vermögen_bedürft_vg <vermögen_bedürft_vg>`.
    haushaltsgröße_vg
        See :func:`haushaltsgröße_vg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    if vermögen_bedürft_vg <= (
        wohngeld_params["vermögensgrundfreibetrag"]
        + (wohngeld_params["vermögensfreibetrag_pers"] * (haushaltsgröße_vg - 1))
    ):
        out = wohngeld_vor_vermög_check_m_vg
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
    vg_id
        See basic input variable :ref:`vg_id <vg_id>`.
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


@dates_active(end="2022-12-31", change_name="arbeitsl_geld_2_vermög_freib_vg")
def arbeitsl_geld_2_vermög_freib_vg_bis_2022(
    _arbeitsl_geld_2_grundfreib_vermög_vg: float,
    anz_kinder_bis_17_vg: int,
    haushaltsgröße_vg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    _arbeitsl_geld_2_grundfreib_vermög_vg
        See :func:`_arbeitsl_geld_2_grundfreib_vermög_vg`.
    anz_kinder_bis_17_vg
        See basic input variable :ref:`anz_kinder_bis_17_vg <anz_kinder_bis_17_vg>`.
    haushaltsgröße_vg
        See :func:`haushaltsgröße_vg`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        _arbeitsl_geld_2_grundfreib_vermög_vg
        + anz_kinder_bis_17_vg * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + haushaltsgröße_vg * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@dates_active(start="2023-01-01")
def _arbeitsl_geld_2_vermög_freib_karenzz_vg(
    arbeitsl_geld_2_params: dict,
    haushaltsgröße_vg: int,
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    haushaltsgröße_vg
        See :func:`haushaltsgröße_vg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    out = (
        params["während_karenzzeit"] + (haushaltsgröße_vg - 1) * params["normaler_satz"]
    )

    return out


@dates_active(start="2023-01-01", change_name="arbeitsl_geld_2_vermög_freib_vg")
def arbeitsl_geld_2_vermög_freib_vg_ab_2023(
    arbeitsl_geld_2_params: dict,
    haushaltsgröße_vg: int,
    _arbeitsl_geld_2_vermög_freib_karenzz_vg: float,
    bürgerg_bezug_vorj: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    haushaltsgröße_vg
        See :func:`haushaltsgröße_vg`.
    _arbeitsl_geld_2_vermög_freib_karenzz_vg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_vg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = haushaltsgröße_vg * params["normaler_satz"]
    else:
        out = _arbeitsl_geld_2_vermög_freib_karenzz_vg

    return out
