"""This module provides functions to compute alimony payments (Unterhalt)."""
import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def unterhaltsvors_m_tu(unterhaltsvors_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly child support advance payment on tax unit level.


    Parameters
    ----------
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    Returns
    -------

    """
    return unterhaltsvors_m.groupby(tu_id).sum()


def unterhaltsvors_m_hh(unterhaltsvors_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate monthly child support advance payment on household level.

    Parameters
    ----------
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return unterhaltsvors_m.groupby(hh_id).sum()


def unterhaltsvors_m(
    tu_id: IntSeries,
    alleinerziehend: BoolSeries,
    alter: IntSeries,
    unterhaltsvorschuss_eink_tu: FloatSeries,
    unterhalt_params: dict,
    kindergeld_params: dict,
) -> FloatSeries:
    """Calculate advance on alimony payment(Unterhaltsvorschuss).

    Single Parents get alimony payments for themselves and for their child from the ex
    partner. If the ex partner is not able to pay the child alimony, the government pays
    the child alimony to the mother (or the father, if he has the kids)

    The amount is specified in §1612a BGB and, ultimately, in
    Mindesunterhaltsverordnung.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    alleinerziehend
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    unterhaltsvorschuss_eink_tu
        See :func:`unterhaltsvorschuss_eink_tu`.
    unterhalt_params
        See params documentation :ref:`unterhalt_params <unterhalt_params>`.
    kindergeld_params
        See params documentation :ref:`kindergeld_params <kindergeld_params>`.

    Returns
    -------

    """

    # Initialize output Series
    out = pd.Series(0, index=tu_id.index)

    # The right-hand-side variable is aggregated by tax units whereas we need personal
    # ids on the left-hand-side. Index with tax unit identifier for expansion and remove
    # index because it is
    unterhaltsvorschuss_eink = tu_id.replace(unterhaltsvorschuss_eink_tu)

    conditions = [
        (alter < 6) & alleinerziehend,
        (alter >= 6) & (alter < 12) & alleinerziehend,
        # Older kids get it only if the parent has income > 600€.
        (alter >= 12)
        & (alter < 18)
        & alleinerziehend
        & (
            unterhaltsvorschuss_eink
            > unterhalt_params["unterhaltsvorschuss_mindesteinkommen"]
        ),
    ]

    conditions = [c.astype(bool) for c in conditions]
    choices = [
        (unterhalt_params["mindestunterhalt"][6] - kindergeld_params["kindergeld"][1]),
        (unterhalt_params["mindestunterhalt"][12] - kindergeld_params["kindergeld"][1]),
        (unterhalt_params["mindestunterhalt"][17] - kindergeld_params["kindergeld"][1]),
    ]

    out[:] = np.ceil(np.select(conditions, choices)).astype(int)

    # TODO: Check against actual transfers
    return out


def unterhaltsvorschuss_eink_tu(
    bruttolohn_m_tu: FloatSeries,
    sonstig_eink_m_tu: FloatSeries,
    eink_selbst_m_tu: FloatSeries,
    vermiet_eink_m_tu: FloatSeries,
    kapital_eink_m_tu: FloatSeries,
    gesamte_rente_m_tu: FloatSeries,
    arbeitsl_geld_m_tu: FloatSeries,
) -> FloatSeries:
    """Calculate relevant income for advance on alimony payment.

    Parameters
    ----------
    bruttolohn_m_tu
        See :func:`bruttolohn_m_tu`.
    sonstig_eink_m_tu
        See :func:`sonstig_eink_m_tu`.
    eink_selbst_m_tu
        See :func:`eink_selbst_m_tu`.
    vermiet_eink_m_tu
        See :func:`vermiet_eink_m_tu`.
    kapital_eink_m_tu
        See :func:`kapital_eink_m_tu`.
    gesamte_rente_m_tu
        See :func:`gesamte_rente_m_tu`.
    arbeitsl_geld_m_tu
        See :func:`arbeitsl_geld_m_tu`.

    Returns
    -------

    """
    out = (
        bruttolohn_m_tu
        + sonstig_eink_m_tu
        + eink_selbst_m_tu
        + vermiet_eink_m_tu
        + kapital_eink_m_tu
        + gesamte_rente_m_tu
        + arbeitsl_geld_m_tu
    )

    return out


def eink_selbst_m_tu(eink_selbst_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly self employed income on tax unit level.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return eink_selbst_m.groupby(tu_id).sum()


def vermiet_eink_m_tu(vermiet_eink_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly rental income on tax unit level.

    Parameters
    ----------
    vermiet_eink_m
        See basic input variable :ref:`vermiet_eink_m <vermiet_eink_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return vermiet_eink_m.groupby(tu_id).sum()


def kapital_eink_m_tu(kapital_eink_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly capital income on tax unit level.

    Parameters
    ----------
    kapital_eink_m
        See basic input variable :ref:`kapital_eink_m <kapital_eink_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return kapital_eink_m.groupby(tu_id).sum()


def gesamte_rente_m_tu(gesamte_rente_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate monthly pension income on tax unit level.

    Parameters
    ----------
    gesamte_rente_m
        See basic input variable :ref:`gesamte_rente_m <gesamte_rente_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return gesamte_rente_m.groupby(tu_id).sum()
