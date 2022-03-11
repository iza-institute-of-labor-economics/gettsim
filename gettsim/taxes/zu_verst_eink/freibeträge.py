import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def _eink_st_behinderungsgrad_pauschbetrag(
    behinderungsgrad: IntSeries, eink_st_abzüge_params: dict
) -> FloatSeries:
    """Assign tax deduction allowance for handicaped to different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """

    # Get disability degree thresholds
    bins = sorted(eink_st_abzüge_params["behinderten_pauschbetrag"])

    # Create corresponding bins
    binned = pd.cut(behinderungsgrad, bins=bins + [np.inf], right=False, labels=bins)

    # Replace values in the intervals
    out = binned.replace(eink_st_abzüge_params["behinderten_pauschbetrag"]).astype(
        float
    )

    return out


def eink_st_alleinerz_freib_tu_bis_2014(
    alleinerz_tu: BoolSeries, eink_st_abzüge_params: dict
) -> FloatSeries:
    """Calculates tax deduction allowance for single parents until 2014.

    This used to be called 'Haushaltsfreibetrag'.

    Parameters
    ----------
    alleinerz_tu
        See :func:`alleinerz_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = alleinerz_tu.astype(float) * 0
    out.loc[alleinerz_tu] = eink_st_abzüge_params["alleinerz_freibetrag"]
    return out


def eink_st_alleinerz_freib_tu_ab_2015(
    alleinerz_tu: BoolSeries, anz_kinder_tu: IntSeries, eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Calculates tax deduction allowance for single parents since 2015.

    Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerz_tu
        See :func:`alleinerz_tu`.
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = alleinerz_tu.astype(float) * 0
    out.loc[alleinerz_tu] = (
        eink_st_abzüge_params["alleinerz_freibetrag"]
        + anz_kinder_tu.loc[alleinerz_tu]
        * eink_st_abzüge_params["alleinerz_freibetrag_zusatz"]
    )
    return out


def eink_st_altersfreib(
    bruttolohn_m: FloatSeries,
    alter: IntSeries,
    kapitaleink_brutto_m: FloatSeries,
    eink_selbst_m: FloatSeries,
    vermiet_eink_m: FloatSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Calculates tax deduction allowance for elderly.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = bruttolohn_m * 0
    agelimit = eink_st_abzüge_params["altersentlastungsbetrag_altersgrenze"]
    out.loc[alter > agelimit] = (
        eink_st_abzüge_params["altersentlastung_quote"]
        * 12
        * (
            bruttolohn_m
            + (kapitaleink_brutto_m + eink_selbst_m + vermiet_eink_m).clip(lower=0)
        )
    ).clip(upper=eink_st_abzüge_params["altersentlastungsbetrag_max"])[alter > agelimit]
    return out


def eink_st_sonderausgaben_bis_2011(
    kind: BoolSeries, eink_st_abzüge_params: dict
) -> FloatSeries:
    """Calculating sonderausgaben for childcare until 2011.

    There is only a lumpsum payment implemented.
    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = kind.astype(float) * 0
    out.loc[~kind] = eink_st_abzüge_params["sonderausgabenpauschbetrag"]
    return out


def eink_st_sonderausgaben_ab_2012(
    betreuungskost_m: FloatSeries,
    tu_id: IntSeries,
    kind: BoolSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Calculate sonderausgaben for childcare since 2012.

    We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg.
    Parameters
    ----------
    betreuungskost_m
        See basic input variable :ref:`betreuungskost_m <betreuungskost_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.

    Returns
    -------

    """
    erwachsene_in_tu = tu_id.replace(anz_erwachsene_tu)
    abziehbare_betreuungskosten = (12 * betreuungskost_m).clip(
        upper=eink_st_abzüge_params["kinderbetreuungskosten_abz_maximum"]
    )

    berechtigte_kinder = kind.groupby(tu_id).transform(sum)
    out = (
        berechtigte_kinder
        * abziehbare_betreuungskosten
        * eink_st_abzüge_params["kinderbetreuungskosten_abz_anteil"]
    ) / erwachsene_in_tu

    out.loc[kind] = 0
    return out


def eink_st_kinderfreib_tu(
    anz_kinder_mit_kindergeld_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
    """Aggregate child allowances on tax unit level.

    Parameters
    ----------
    anz_kinder_mit_kindergeld_tu
        See :func:`anz_kinder_mit_kindergeld_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    kifreib_total = sum(eink_st_abzüge_params["kinderfreibetrag"].values())
    return kifreib_total * anz_kinder_mit_kindergeld_tu * anz_erwachsene_tu


def anz_kinder_mit_kindergeld_tu(
    tu_id: IntSeries, kindergeld_anspruch: BoolSeries
) -> FloatSeries:
    """Count number of children eligible for Child Benefit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.

    Returns
    -------

    """
    return kindergeld_anspruch.groupby(tu_id).sum()
