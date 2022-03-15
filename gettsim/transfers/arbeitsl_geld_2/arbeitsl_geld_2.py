import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_2_m_hh(
    arbeitsl_geld_2_vor_vorrang_m_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschl_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    erwachsene_alle_rentner_hh: BoolSeries,
) -> FloatSeries:

    """Calculate final monthly subsistence payment on household level.

    Parameters
    ----------
    arbeitsl_geld_2_vor_vorrang_m_hh
        See :func:`arbeitsl_geld_2_vor_vorrang_m_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh   `.

    Returns
    -------
    FloatSeries with the income by unemployment insurance per household.
    """
    out = arbeitsl_geld_2_vor_vorrang_m_hh.copy()
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschl_vorrang_hh
        | wohngeld_kinderzuschl_vorrang_hh
        | erwachsene_alle_rentner_hh
    )
    if cond:
        return 0
    else:
        return out


def arbeitsl_geld_2_regelbedarf_m_hh(
    arbeitsl_geld_2_regelsatz_m_hh: FloatSeries,
    arbeitsl_geld_2_kost_unterk_m_hh: FloatSeries,
) -> FloatSeries:
    """Basic monthly subsistence level on household level.

    This includes cost of dwelling.

    Parameters
    ----------
    arbeitsl_geld_2_regelsatz_m_hh
        See :func:`arbeitsl_geld_2_regelsatz_m_hh`.
    arbeitsl_geld_2_kost_unterk_m_hh
        See :func:`arbeitsl_geld_2_kost_unterk_m_hh`.

    Returns
    -------
    FloatSeries checks the minimum monthly needs of an household.
    """
    return arbeitsl_geld_2_regelsatz_m_hh + arbeitsl_geld_2_kost_unterk_m_hh


def _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh(
    alleinerz_hh: BoolSeries,
    anz_kinder_hh: IntSeries,
    anz_kinder_bis_6_hh: IntSeries,
    anz_kinder_bis_15_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Compute additional need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Parameters
    ----------
    alleinerz_hh
        See :func:`alleinerz_hh`.
    anz_kinder_hh
        See :func:`anz_kinder_hh`.
    anz_kinder_bis_6_hh
        See :func:`anz_kinder_bis_6_hh`.
    anz_kinder_bis_15_hh
        See :func:`anz_kinder_bis_15_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.


    Returns
    -------
    FloatSeries checks how much more a single parent need.
    """

    # Get minimal Mehrbedarf share. Minimal rate times number of children
    lower = arbeitsl_geld_2_params["mehrbedarf_anteil"]["min_1_kind"] * anz_kinder_hh

    # Special case if 1 kid below 6 or 2,3 below 15.
    value = (
        (anz_kinder_bis_6_hh >= 1)
        | ((2 <= anz_kinder_bis_15_hh) & (anz_kinder_bis_15_hh <= 3))
    ) * arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]

    # Clip value at calculated minimal share and given upper share
    if value < lower:
        value = lower
    elif value > arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]:
        value = arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]
    else:
        value = value

    return alleinerz_hh * value


def arbeitsl_geld_2_kindersatz_m_hh_bis_2010(
    anz_kinder_bis_6_hh: IntSeries,
    anz_kinder_ab_7_bis_13_hh: IntSeries,
    anz_kinder_ab_14_bis_24_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate basic monthly subsistence for children until 2010.

    Since 2010 children get additional shares instead of lump sum payments.

    Parameters
    ----------
    anz_kinder_bis_6_hh
        See :func:`anz_kinder_bis_6_hh`.
    anz_kinder_ab_7_bis_13_hh
        See :func:`anz_kinder_ab_7_bis_13_hh`.
    anz_kinder_ab_14_bis_24_hh
        See :func:`anz_kinder_ab_14_bis_24_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the support of children until year 2010.
    """
    # Dictionary of additional shares.
    anteile = arbeitsl_geld_2_params["anteil_regelsatz"]

    # Multiply number of kids in age range with corresponding additional share
    out = arbeitsl_geld_2_params["regelsatz"] * (
        anteile["kinder_0_6"] * anz_kinder_bis_6_hh
        + anteile["kinder_7_13"] * anz_kinder_ab_7_bis_13_hh
        + anteile["kinder_14_24"] * anz_kinder_ab_14_bis_24_hh
    )

    return out


def arbeitsl_geld_2_kindersatz_m_hh_ab_2011(
    anz_kinder_bis_6_hh: IntSeries,
    anz_kinder_ab_7_bis_13_hh: IntSeries,
    anz_kinder_ab_14_bis_24_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate basic monthly subsistence for children since 2011.

    Here the sum in euro is directly in the law.

    Parameters
    ----------
    anz_kinder_bis_6_hh
        See :func:`anz_kinder_bis_6_hh`.
    anz_kinder_ab_7_bis_13_hh
        See :func:`anz_kinder_ab_7_bis_13_hh`.
    anz_kinder_ab_14_bis_24_hh
        See :func:`anz_kinder_ab_14_bis_24_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the support of children since year 2011
    """
    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kinder_bis_6_hh
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kinder_ab_7_bis_13_hh
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kinder_ab_14_bis_24_hh
    )

    return out


def arbeitsl_geld_2_regelsatz_m_hh_bis_2010(
    anz_erwachsene_hh: IntSeries,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    arbeitsl_geld_2_kindersatz_m_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Calculate basic monthly subsistence without dwelling until 2010.


    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    arbeitsl_geld_2_kindersatz_m_hh
        See :func:`arbeitsl_geld_2_kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the sum in Euro.
    """
    if (anz_erwachsene_hh - 2) < 0:
        weitere_erwachsene = 0
    else:
        weitere_erwachsene = anz_erwachsene_hh - 2

    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"]
        * (1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + weitere_erwachsene
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        ),
    )

    return arbeitsl_geld_2_kindersatz_m_hh + data


def arbeitsl_geld_2_regelsatz_m_hh_ab_2011(
    anz_erwachsene_hh: IntSeries,
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    arbeitsl_geld_2_kindersatz_m_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Calculate basic monthly subsistence without dwelling since 2011.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    arbeitsl_geld_2_kindersatz_m_hh
        See :func:`arbeitsl_geld_2_kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the minimum needs of an household in Euro.
    """
    if (anz_erwachsene_hh - 2) < 0:
        weitere_erwachsene = 0
    else:
        weitere_erwachsene = anz_erwachsene_hh - 2

    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"][1]
        * (1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh),
        arbeitsl_geld_2_params["regelsatz"][2]
        * (2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh)
        + (arbeitsl_geld_2_params["regelsatz"][3] * weitere_erwachsene),
    )

    return arbeitsl_geld_2_kindersatz_m_hh + data


def arbeitsl_geld_2_vor_vorrang_m_hh(
    arbeitsl_geld_2_regelbedarf_m_hh: FloatSeries,
    kindergeld_m_hh: FloatSeries,
    unterhaltsvors_m_hh: FloatSeries,
    arbeitsl_geld_2_eink_m_hh: FloatSeries,
    vermögen_hh: FloatSeries,
    arbeitsl_geld_2_vermög_freib_hh: FloatSeries,
) -> FloatSeries:
    """Calculate potential basic subsistence (after income deduction and
    wealth check).

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_hh
        See :func:`arbeitsl_geld_2_regelbedarf_m_hh`.
    kindergeld_m_hh
        See :func:`kindergeld_m_hh`.
    unterhaltsvors_m_hh
        See :func:`unterhaltsvors_m_hh`.
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.
    arbeitsl_geld_2_vermög_freib_hh
        See :func:`arbeitsl_geld_2_vermög_freib_hh`.
    vermögen_hh
        See basic input variable :ref:`vermögen_hh <vermögen_hh>`.

    Returns
    -------

    """

    # Deduct income from other sources
    out = (
        arbeitsl_geld_2_regelbedarf_m_hh
        - arbeitsl_geld_2_eink_m_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )

    # Check wealth exemption
    if (out < 0) | (vermögen_hh > arbeitsl_geld_2_vermög_freib_hh):
        return 0
    else:
        return out
