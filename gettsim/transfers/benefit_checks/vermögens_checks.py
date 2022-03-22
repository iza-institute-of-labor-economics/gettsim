from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def _kinderzuschl_nach_vermög_check_m_hh(
    kinderzuschl_vorläufig_m_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    arbeitsl_geld_2_vermög_freib_hh,
) -> FloatSeries:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    kinderzuschl_vorläufig_m_hh
        See :func:`kinderzuschl_vorläufig_m_hh`.
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
        out = kinderzuschl_vorläufig_m_hh
    return out


def wohngeld_nach_vermög_check_m_hh(
    wohngeld_vor_vermög_check_m_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    haushaltsgröße_hh: IntSeries,
    wohngeld_params: dict,
) -> FloatSeries:
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
    kind: BoolSeries,
    alter: IntSeries,
    geburtsjahr: IntSeries,
    _arbeitsl_geld_2_max_grundfreib_vermög: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
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
    elif (geburtsjahr >= threshold_years[1]) & (not kind):
        out = (
            list(arbeitsl_geld_2_params["vermögensgrundfreibetrag"].values())[1] * alter
        )
    else:
        out = 0.0

    return min(out, _arbeitsl_geld_2_max_grundfreib_vermög)


def _arbeitsl_geld_2_max_grundfreib_vermög(
    geburtsjahr: IntSeries, kind: BoolSeries, arbeitsl_geld_2_params: dict,
) -> FloatSeries:
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
    _arbeitsl_geld_2_grundfreib_vermög_hh: FloatSeries,
    anz_kinder_bis_17_hh: IntSeries,
    haushaltsgröße_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
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
