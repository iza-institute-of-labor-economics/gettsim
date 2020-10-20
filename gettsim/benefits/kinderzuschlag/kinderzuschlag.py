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


def kinderzuschlag_m_hh(
    kinderzuschlag_vermögens_check_hh: FloatSeries,
    kinderzuschlag_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    rentner_in_hh: BoolSeries,
) -> FloatSeries:
    """

    Parameters
    ----------
    kinderzuschlag_vermögens_check_hh
        See :func:`kinderzuschlag_vermögens_check_hh`.
    kinderzuschlag_vorrang_hh
        See :func:`kinderzuschlag_vorrang_hh`.
    wohngeld_kinderzuschlag_vorrang_hh
        See :func:`wohngeld_kinderzuschlag_vorrang_hh`.
    rentner_in_hh
        See :func:`rentner_in_hh`.

    Returns
    -------

    """
    cond = (
        ~kinderzuschlag_vorrang_hh & ~wohngeld_kinderzuschlag_vorrang_hh
    ) | rentner_in_hh
    kinderzuschlag_vermögens_check_hh.loc[cond] = 0
    return kinderzuschlag_vermögens_check_hh


def kinderzuschlag_m_vorläufig_hh(
    _kinderzuschlag_m_vorläufig: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """

    Parameters
    ----------
    _kinderzuschlag_m_vorläufig
        See :func:`_kinderzuschlag_m_vorläufig`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return _kinderzuschlag_m_vorläufig.groupby(hh_id).max()


def kinderzuschlag_ab_juli_2019(
    hh_id: IntSeries,
    _arbeitsl_geld_2_brutto_eink_hh: FloatSeries,
    kinderzuschlag_eink_min: FloatSeries,
    kinderzuschlag_kindereink_abzug: FloatSeries,
    kinderzuschlag_eink_anrechn: FloatSeries,
) -> FloatSeries:
    """Creates "_kinderzuschlag_m_vorläufig" since 07/2019.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    _arbeitsl_geld_2_brutto_eink_hh
        See :func:`_arbeitsl_geld_2_brutto_eink_hh`.
    kinderzuschlag_eink_min
        See :func:`kinderzuschlag_eink_min`.
    kinderzuschlag_kindereink_abzug
        See :func:`kinderzuschlag_kindereink_abzug`.
    kinderzuschlag_eink_anrechn
        See :func:`kinderzuschlag_eink_anrechn`.

    Returns
    -------

    """
    out = hh_id * 0
    condition = (
        hh_id.replace(_arbeitsl_geld_2_brutto_eink_hh) >= kinderzuschlag_eink_min
    )
    out.loc[condition] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return out.groupby(hh_id).transform("max")


def kinderzuschlag_ab_2005_bis_juni_2019(
    hh_id: IntSeries,
    kinderzuschlag_eink_spanne: BoolSeries,
    kinderzuschlag_kindereink_abzug: FloatSeries,
    kinderzuschlag_eink_anrechn: FloatSeries,
) -> FloatSeries:
    """Creates "_kinderzuschlag_m_vorläufig" until 06/2019.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kinderzuschlag_eink_spanne
        See :func:`kinderzuschlag_eink_spanne`.
    kinderzuschlag_kindereink_abzug
        See :func:`kinderzuschlag_kindereink_abzug`.
    kinderzuschlag_eink_anrechn
        See :func:`kinderzuschlag_eink_anrechn`.

    Returns
    -------

    """
    out = kinderzuschlag_eink_spanne * 0
    out.loc[kinderzuschlag_eink_spanne] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return out.groupby(hh_id).transform("max")
