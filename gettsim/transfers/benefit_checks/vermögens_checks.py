def _kinderzuschl_nach_vermög_check_m_hh(
    _kinderzuschl_vor_vermög_check_m_hh: float,
    vermögen_hh: float,
    arbeitsl_geld_2_vermög_freib_hh: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_hh
        See :func:`_kinderzuschl_vor_vermög_check_m_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    arbeitsl_geld_2_vermög_freib_hh
        See :func:`arbeitsl_geld_2_vermög_freib_hh`.

    Returns
    -------

    """

    if vermögen_hh > arbeitsl_geld_2_vermög_freib_hh:
        out = 0.0
    else:
        out = _kinderzuschl_vor_vermög_check_m_hh
    return out


def wohngeld_nach_vermög_check_m_hh(
    wohngeld_vor_vermög_check_m_hh: float,
    vermögen_hh: float,
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
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    if vermögen_hh <= (
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
    """Calculate exemptions based on individuals age.

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

    return min(out, _arbeitsl_geld_2_max_grundfreib_vermög)


def _arbeitsl_geld_2_max_grundfreib_vermög(
    geburtsjahr: int,
    kind: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate maximal wealth exemptions by year of birth.

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

    return out


def arbeitsl_geld_2_vermög_freib_hh(
    _arbeitsl_geld_2_grundfreib_vermög_hh: float,
    anz_kinder_bis_17_hh: int,
    haushaltsgröße_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate actual exemptions.

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
