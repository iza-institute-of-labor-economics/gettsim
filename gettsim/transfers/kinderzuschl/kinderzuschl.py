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
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_m_hh(
    kinderzuschl_vermögens_check_hh: FloatSeries,
    kinderzuschl_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    rentner_in_hh: BoolSeries,
) -> FloatSeries:
    """Aggregate child benefit on household level.

    Parameters
    ----------
    kinderzuschl_vermögens_check_hh
        See :func:`kinderzuschl_vermögens_check_hh`.
    kinderzuschl_vorrang_hh
        See :func:`kinderzuschl_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    rentner_in_hh
        See :func:`rentner_in_hh`.

    Returns
    -------

    """
    out = kinderzuschl_vermögens_check_hh.copy()
    cond = (
        ~kinderzuschl_vorrang_hh & ~wohngeld_kinderzuschl_vorrang_hh
    ) | rentner_in_hh
    out.loc[cond] = 0
    return out


def kinderzuschl_vorläufig_m_hh(
    kinderzuschl_vorläufig_m: FloatSeries, hh_id: IntSeries
) -> FloatSeries:
    """Aggregate preliminary child benefit on household level.

    Parameters
    ----------
    kinderzuschl_vorläufig_m
        See :func:`kinderzuschl_vorläufig_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return kinderzuschl_vorläufig_m.groupby(hh_id).max()


def kinderzuschl_vorläufig_m_ab_07_2019(
    hh_id: IntSeries,
    arbeitsl_geld_2_brutto_eink_hh: FloatSeries,
    kinderzuschl_eink_min: FloatSeries,
    kinderzuschl_kindereink_abzug: FloatSeries,
    kinderzuschl_eink_anrechn: FloatSeries,
) -> FloatSeries:
    """Calculate preliminary child benefit since 07/2019.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    arbeitsl_geld_2_brutto_eink_hh
        See :func:`arbeitsl_geld_2_brutto_eink_hh`.
    kinderzuschl_eink_min
        See :func:`kinderzuschl_eink_min`.
    kinderzuschl_kindereink_abzug
        See :func:`kinderzuschl_kindereink_abzug`.
    kinderzuschl_eink_anrechn
        See :func:`kinderzuschl_eink_anrechn`.

    Returns
    -------

    """
    out = pd.Series(0, index=hh_id.index)
    condition = hh_id.replace(arbeitsl_geld_2_brutto_eink_hh) >= kinderzuschl_eink_min
    out.loc[condition] = (
        kinderzuschl_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschl_eink_anrechn
    ).clip(lower=0)

    return out.groupby(hh_id).transform("max")


def kinderzuschl_vorläufig_m_bis_06_2019(
    hh_id: IntSeries,
    kinderzuschl_eink_spanne: BoolSeries,
    kinderzuschl_kindereink_abzug: FloatSeries,
    kinderzuschl_eink_anrechn: FloatSeries,
) -> FloatSeries:
    """Calculate preliminary child benefit since 2005 until 06/2019.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kinderzuschl_eink_spanne
        See :func:`kinderzuschl_eink_spanne`.
    kinderzuschl_kindereink_abzug
        See :func:`kinderzuschl_kindereink_abzug`.
    kinderzuschl_eink_anrechn
        See :func:`kinderzuschl_eink_anrechn`.

    Returns
    -------

    """
    out = pd.Series(0, index=kinderzuschl_eink_spanne.index)
    out.loc[kinderzuschl_eink_spanne] = (
        kinderzuschl_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschl_eink_anrechn
    ).clip(lower=0)
    return out.groupby(hh_id).transform("max")
