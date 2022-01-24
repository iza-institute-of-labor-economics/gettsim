import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_2_m_hh(
    arbeitsl_geld_2_m_minus_eink_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    kinderzuschl_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    rentner_in_hh: BoolSeries,
) -> FloatSeries:

    """Calculate final monthly subsistence payment on household level.

    Parameters
    ----------
    arbeitsl_geld_2_m_minus_eink_hh
        See :func:`arbeitsl_geld_2_m_minus_eink_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    rentner_in_hh
        See :func:`rentner_in_hh`.

    Returns
    -------
    FloatSeries with the income by unemployment insurance per household.
    """
    out = arbeitsl_geld_2_m_minus_eink_hh.clip(lower=0)
    cond = (
        wohngeld_vorrang_hh
        | kinderzuschl_vorrang_hh
        | wohngeld_kinderzuschl_vorrang_hh
        | rentner_in_hh
    )
    out.loc[cond] = 0
    return out


def regelbedarf_m_hh(
    regelsatz_m_hh: FloatSeries, kost_unterk_m_hh: FloatSeries
) -> FloatSeries:
    """Basic monthly subsistence level on household level.

    This includes cost of dwelling.

    Parameters
    ----------
    regelsatz_m_hh
        See :func:`regelsatz_m_hh`.
    kost_unterk_m_hh
        See :func:`kost_unterk_m_hh`.

    Returns
    -------
    FloatSeries checks the minimum monthly needs of an household.
    """
    return regelsatz_m_hh + kost_unterk_m_hh


def alleinerziehenden_mehrbedarf_hh(
    alleinerziehend_hh: BoolSeries,
    anz_kinder_hh: IntSeries,
    anz_kind_zwischen_0_6_hh: IntSeries,
    anz_kind_zwischen_0_15_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Compute additional need for single parents.

    Additional need for single parents. Maximum 60% of the standard amount on top if
    you have at least one kid below 6 or two or three below 15, you get 36%
    on top alternatively, you get 12% per kid, depending on what's higher.

    Parameters
    ----------
    alleinerziehend_hh
        See :func:`alleinerziehend_hh`.
    anz_kinder_hh
        See :func:`anz_kinder_hh`.
    anz_kind_zwischen_0_6_hh
        See :func:`anz_kind_zwischen_0_6_hh`.
    anz_kind_zwischen_0_15_hh
        See :func:`anz_kind_zwischen_0_15_hh`.
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
        (anz_kind_zwischen_0_6_hh >= 1)
        | ((2 <= anz_kind_zwischen_0_15_hh) & (anz_kind_zwischen_0_15_hh <= 3))
    ) * arbeitsl_geld_2_params["mehrbedarf_anteil"]["kind_unter_7_oder_mehr"]

    # Clip value at calculated minimal share and given upper share
    out = alleinerziehend_hh * value.clip(
        lower=lower, upper=arbeitsl_geld_2_params["mehrbedarf_anteil"]["max"]
    )
    return out


def kindersatz_m_hh_bis_2010(
    anz_kind_zwischen_0_6_hh: IntSeries,
    anz_kind_zwischen_7_13_hh: IntSeries,
    anz_kind_zwischen_14_24_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate basic monthly subsistence for children until 2010.

    Since 2010 children get additional shares instead of lump sum payments.

    Parameters
    ----------
    anz_kind_zwischen_0_6_hh
        See :func:`anz_kind_zwischen_0_6_hh`.
    anz_kind_zwischen_7_13_hh
        See :func:`anz_kind_zwischen_7_13_hh`.
    anz_kind_zwischen_14_24_hh
        See :func:`anz_kind_zwischen_14_24_hh`.
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
        anteile["kinder_0_6"] * anz_kind_zwischen_0_6_hh
        + anteile["kinder_7_13"] * anz_kind_zwischen_7_13_hh
        + anteile["kinder_14_24"] * anz_kind_zwischen_14_24_hh
    )

    return out


def kindersatz_m_hh_ab_2011(
    anz_kind_zwischen_0_6_hh: IntSeries,
    anz_kind_zwischen_7_13_hh: IntSeries,
    anz_kind_zwischen_14_24_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate basic monthly subsistence for children since 2011.

    Here the sum in euro is directly in the law.

    Parameters
    ----------
    anz_kind_zwischen_0_6_hh
        See :func:`anz_kind_zwischen_0_6_hh`.
    anz_kind_zwischen_7_13_hh
        See :func:`anz_kind_zwischen_7_13_hh`.
    anz_kind_zwischen_14_24_hh
        See :func:`anz_kind_zwischen_14_24_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the support of children since year 2011
    """
    # Sum payments for each age group
    out = (
        arbeitsl_geld_2_params["regelsatz"][6] * anz_kind_zwischen_0_6_hh
        + arbeitsl_geld_2_params["regelsatz"][5] * anz_kind_zwischen_7_13_hh
        + arbeitsl_geld_2_params["regelsatz"][4] * anz_kind_zwischen_14_24_hh
    )

    return out


def regelsatz_m_hh_bis_2010(
    anz_erwachsene_hh: IntSeries,
    alleinerziehenden_mehrbedarf_hh: FloatSeries,
    kindersatz_m_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Calculate basic monthly subsistence without dwelling until 2010.


    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    alleinerziehenden_mehrbedarf_hh
        See :func:`alleinerziehenden_mehrbedarf_hh`.
    kindersatz_m_hh
        See :func:`kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the sum in Euro.
    """
    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf_hh),
        arbeitsl_geld_2_params["regelsatz"]
        * (
            2 * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            + (anz_erwachsene_hh - 2).clip(lower=0)
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        ),
    )

    return kindersatz_m_hh + data


def regelsatz_m_hh_ab_2011(
    anz_erwachsene_hh: IntSeries,
    alleinerziehenden_mehrbedarf_hh: FloatSeries,
    kindersatz_m_hh: FloatSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:

    """Calculate basic monthly subsistence without dwelling since 2011.

    Parameters
    ----------
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    alleinerziehenden_mehrbedarf_hh
        See :func:`alleinerziehenden_mehrbedarf_hh`.
    kindersatz_m_hh
        See :func:`kindersatz_m_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------
    FloatSeries with the minimum needs of an household in Euro.
    """
    data = np.where(
        anz_erwachsene_hh == 1,
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf_hh),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf_hh)
        + (
            arbeitsl_geld_2_params["regelsatz"][3]
            * (anz_erwachsene_hh - 2).clip(lower=0)
        ),
    )

    return kindersatz_m_hh + data
