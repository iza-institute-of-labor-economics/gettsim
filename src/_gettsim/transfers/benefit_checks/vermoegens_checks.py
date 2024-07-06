from _gettsim.shared import policy_info


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


@policy_info(end_date="2022-12-31", name_in_dag="kinderzuschl_vermög_freib_fg")
def kinderzuschl_vermög_freib_fg_bis_2022(
    arbeitsl_geld_2_vermög_freib_fg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022.

    Parameters
    ----------
    arbeitsl_geld_2_vermög_freib_fg
        See :func:`arbeitsl_geld_2_vermög_freib_fg`.

    Returns
    -------

    """

    return arbeitsl_geld_2_vermög_freib_fg


@policy_info(start_date="2023-01-01", name_in_dag="kinderzuschl_vermög_freib_fg")
def kinderzuschl_vermög_freib_fg_ab_2023(
    _arbeitsl_geld_2_vermög_freib_karenzz_fg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023.

    Parameters
    ----------
    _arbeitsl_geld_2_vermög_freib_karenzz_fg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_fg`.

    Returns
    -------

    """

    return _arbeitsl_geld_2_vermög_freib_karenzz_fg


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
    _arbeitsl_geld_2_grundfreib_vermög_bg: float,
    anz_kinder_bis_17_bg: int,
    anz_personen_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    _arbeitsl_geld_2_grundfreib_vermög_bg
        See :func:`_arbeitsl_geld_2_grundfreib_vermög_bg`.
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
        _arbeitsl_geld_2_grundfreib_vermög_bg
        + anz_kinder_bis_17_bg * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + anz_personen_bg * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@policy_info(end_date="2022-12-31", name_in_dag="arbeitsl_geld_2_vermög_freib_fg")
def arbeitsl_geld_2_vermög_freib_fg_bis_2022(
    _arbeitsl_geld_2_grundfreib_vermög_fg: float,
    anz_kinder_bis_17_fg: int,
    anz_personen_fg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    _arbeitsl_geld_2_grundfreib_vermög_fg
        See :func:`_arbeitsl_geld_2_grundfreib_vermög_fg`.
    anz_kinder_bis_17_fg
        See :func:`anz_kinder_bis_17_fg`.
    anz_personen_fg
        See :func:`anz_personen_fg`.

    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = (
        _arbeitsl_geld_2_grundfreib_vermög_fg
        + anz_kinder_bis_17_fg * arbeitsl_geld_2_params["vermögensfreibetrag_kind"]
        + anz_personen_fg * arbeitsl_geld_2_params["vermögensfreibetrag_austattung"]
    )
    return out


@policy_info(start_date="2023-01-01")
def _arbeitsl_geld_2_vermög_freib_karenzz_bg(
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


@policy_info(start_date="2023-01-01")
def _arbeitsl_geld_2_vermög_freib_karenzz_fg(
    arbeitsl_geld_2_params: dict,
    anz_personen_fg: int,
) -> float:
    """Calculate wealth exemptions since 2023 during Karenzzeit. This variable is also
    reffered to as 'erhebliches Vermögen'.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params
        <arbeitsl_geld_2_params>`.
    anz_personen_fg
        See :func:`anz_personen_fg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    out = params["während_karenzzeit"] + (anz_personen_fg - 1) * params["normaler_satz"]

    return out


@policy_info(start_date="2023-01-01", name_in_dag="arbeitsl_geld_2_vermög_freib_bg")
def arbeitsl_geld_2_vermög_freib_bg_ab_2023(
    arbeitsl_geld_2_params: dict,
    anz_personen_bg: int,
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
    anz_personen_bg
        See :func:`anz_personen_bg`.
    _arbeitsl_geld_2_vermög_freib_karenzz_bg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_bg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = anz_personen_bg * params["normaler_satz"]
    else:
        out = _arbeitsl_geld_2_vermög_freib_karenzz_bg

    return out


@policy_info(start_date="2023-01-01", name_in_dag="arbeitsl_geld_2_vermög_freib_fg")
def arbeitsl_geld_2_vermög_freib_fg_ab_2023(
    arbeitsl_geld_2_params: dict,
    anz_personen_fg: int,
    _arbeitsl_geld_2_vermög_freib_karenzz_fg: float,
    bürgerg_bezug_vorj: bool,
) -> float:
    """Calculate actual wealth exemptions since 2023.

    During the first year (Karenzzeit), the wealth exemption is substantially larger.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.
    anz_personen_fg
        See :func:`anz_personen_fg`.
    _arbeitsl_geld_2_vermög_freib_karenzz_fg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_fg`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.


    Returns
    -------

    """
    params = arbeitsl_geld_2_params["schonvermögen_bürgergeld"]
    if bürgerg_bezug_vorj:
        out = anz_personen_fg * params["normaler_satz"]
    else:
        out = _arbeitsl_geld_2_vermög_freib_karenzz_fg

    return out
