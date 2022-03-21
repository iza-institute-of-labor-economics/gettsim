"""
Kinderzuschlag / Additional Child Benefit

    The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they would
    be eligible to ALG2 due to the fact that their claim rises because of their
    children, they can claim Kiz.

    A couple of criteria need to be met.

    1. the household has to have some income

    2. net income minus housing benefit needs has to be lower than total ALG2 need plus
       additional child benefit.

    3. Over a certain income threshold (which depends on housing costs, and is therefore
       household-specific), parental income is deducted from child benefit claim.

    In contrast to ALG2, Kiz considers only the rental costs that are attributed to the
    parents. This is done by some fixed share which is updated on annual basis
    ('jährlicher Existenzminimumsbericht')
"""
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_m_hh(
    _kinderzuschl_nach_vermög_check_m_hh: FloatSeries,
    kinderzuschl_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    anz_rentner_hh: IntSeries,
) -> FloatSeries:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    _kinderzuschl_nach_vermög_check_m_hh
        See :func:`_kinderzuschl_nach_vermög_check_m_hh`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    anz_rentner_hh
        See :func:`anz_rentner_hh`.

    Returns
    -------

    """
    if ((not kinderzuschl_vorrang_hh) & (not wohngeld_kinderzuschl_vorrang_hh)) | (
        anz_rentner_hh > 0
    ):
        out = 0
    else:
        out = _kinderzuschl_nach_vermög_check_m_hh

    return out


def kinderzuschl_vorläufig_m_hh_ab_07_2019(
    arbeitsl_geld_2_brutto_eink_m_hh: FloatSeries,
    kinderzuschl_eink_min_m_hh_hh: FloatSeries,
    kinderzuschl_kindereink_abzug_m_hh: FloatSeries,
    kinderzuschl_eink_anrechn_m_hh: FloatSeries,
) -> FloatSeries:
    """Calculate preliminary child benefit since 07/2019.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    arbeitsl_geld_2_brutto_eink_m_hh
        See :func:`arbeitsl_geld_2_brutto_eink_m_hh`.
    kinderzuschl_eink_min_m_hh_hh
        See :func:`kinderzuschl_eink_min_m_hh_hh`.
    kinderzuschl_kindereink_abzug_m_hh
        See :func:`kinderzuschl_kindereink_abzug_m_hh`.
    kinderzuschl_eink_anrechn_m_hh
        See :func:`kinderzuschl_eink_anrechn_m_hh`.

    Returns
    -------

    """
    if arbeitsl_geld_2_brutto_eink_m_hh >= kinderzuschl_eink_min_m_hh_hh:
        out = max(
            kinderzuschl_kindereink_abzug_m_hh - kinderzuschl_eink_anrechn_m_hh, 0
        )
    else:
        out = 0

    return out


def kinderzuschl_vorläufig_m_hh_bis_06_2019(
    arbeitsl_geld_2_brutto_eink_m_hh: FloatSeries,
    kinderzuschl_eink_min_m_hh: FloatSeries,
    kinderzuschl_eink_max_m_hh: FloatSeries,
    arbeitsl_geld_2_eink_m_hh: FloatSeries,
    kinderzuschl_kindereink_abzug_m_hh: FloatSeries,
    kinderzuschl_eink_anrechn_m_hh: FloatSeries,
) -> FloatSeries:
    """Calculate preliminary child benefit since 2005 until 06/2019.

    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink_m_hh
        See :func:`arbeitsl_geld_2_brutto_eink_m_hh`.
    kinderzuschl_eink_min_m_hh
        See :func:`kinderzuschl_eink_min_m_hh`.
    kinderzuschl_eink_max_m_hh
        See :func:`kinderzuschl_eink_max_m_hh`.
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.
    kinderzuschl_kindereink_abzug_m_hh
        See :func:`kinderzuschl_kindereink_abzug_m_hh`.
    kinderzuschl_eink_anrechn_m_hh
        See :func:`kinderzuschl_eink_anrechn_m_hh`.

    Returns
    -------

    """

    # Check if household income is in income range for child benefit.
    if (arbeitsl_geld_2_brutto_eink_m_hh >= kinderzuschl_eink_min_m_hh) & (
        arbeitsl_geld_2_eink_m_hh <= kinderzuschl_eink_max_m_hh
    ):
        out = max(
            kinderzuschl_kindereink_abzug_m_hh - kinderzuschl_eink_anrechn_m_hh, 0
        )
    else:
        out = 0

    return out
