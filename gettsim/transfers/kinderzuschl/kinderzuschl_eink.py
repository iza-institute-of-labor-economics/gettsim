import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_eink_regel_bis_2010(
    tu_id: IntSeries,
    hh_id: IntSeries,
    _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    alleinerziehenden_mehrbedarf = hh_id.replace(
        _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh
    )
    erwachsene_in_tu = tu_id.replace(anz_erwachsene_tu)
    choices = [
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
        * (2 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        * erwachsene_in_tu,
    ]

    data = np.select(
        [erwachsene_in_tu == 1, erwachsene_in_tu == 2, erwachsene_in_tu > 2], choices,
    )

    eink_regel = pd.Series(index=alleinerziehenden_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschl_eink_regel_ab_2011(
    tu_id: IntSeries,
    hh_id: IntSeries,
    _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    alleinerziehenden_mehrbedarf = hh_id.replace(
        _arbeitsl_geld_2_alleinerziehenden_mehrbedarf_m_hh
    )
    erwachsene_in_tu = tu_id.replace(anz_erwachsene_tu)
    choices = [
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][3] * erwachsene_in_tu,
    ]

    data = np.select(
        [erwachsene_in_tu == 1, erwachsene_in_tu == 2, erwachsene_in_tu > 2], choices,
    )

    eink_regel = pd.Series(index=alleinerziehenden_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschl_eink_relev(
    kinderzuschl_eink_regel: FloatSeries, kinderzuschl_kosten_unterk_m: FloatSeries
) -> FloatSeries:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    kinderzuschl_eink_regel
        See :func:`kinderzuschl_eink_regel`.
    kinderzuschl_kosten_unterk_m
        See :func:`kinderzuschl_kosten_unterk_m`.

    Returns
    -------

    """
    return kinderzuschl_eink_regel + kinderzuschl_kosten_unterk_m


def anz_kinder_anspruch_per_hh(
    hh_id: IntSeries, kindergeld_anspruch: BoolSeries
) -> IntSeries:
    """Count number of children eligible to child benefit (§6a (1) Nr. 1 BKGG)kdu.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.

    Returns
    -------

    """
    return kindergeld_anspruch.groupby(hh_id).transform("sum")


def kinderzuschl_eink_max(
    kinderzuschl_eink_relev: FloatSeries,
    anz_kinder_anspruch_per_hh: IntSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate maximum income to be eligible for additional
       child benefit (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    kinderzuschl_eink_relev
        See :func:`kinderzuschl_eink_relev`.
    anz_kinder_anspruch_per_hh
        See :func:`anz_kinder_anspruch_per_hh`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    return (
        kinderzuschl_eink_relev
        + kinderzuschl_params["maximum"] * anz_kinder_anspruch_per_hh
    )


def kinderzuschl_eink_min(
    hh_id: IntSeries,
    kind: BoolSeries,
    alleinerziehend: BoolSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    alleinerziehend
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    hat_kinder_hh = kind.groupby(hh_id).transform("any")
    is_alleinerziehend_hh = alleinerziehend.groupby(hh_id).transform("all")

    conditions = [~hat_kinder_hh, is_alleinerziehend_hh, ~is_alleinerziehend_hh]
    choices = [
        0,
        kinderzuschl_params["min_eink_alleinerz"],
        kinderzuschl_params["min_eink_paare"],
    ]

    return pd.Series(index=hh_id.index, data=np.select(conditions, choices))


def kinderzuschl_kindereink_abzug(
    kindergeld_anspruch: BoolSeries,
    bruttolohn_m: FloatSeries,
    unterhaltsvors_m: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Deduct children income for each eligible child.

    (§6a (3) S.3 BKGG)

    Parameters
    ----------
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    return kindergeld_anspruch * (
        kinderzuschl_params["maximum"]
        - kinderzuschl_params["entzugsrate_kind"] * (bruttolohn_m + unterhaltsvors_m)
    ).clip(lower=0)


def kinderzuschl_eink_anrechn(
    hh_id: IntSeries,
    arbeitsl_geld_2_eink_hh: FloatSeries,
    kinderzuschl_eink_relev: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    arbeitsl_geld_2_eink_hh
        See :func:`arbeitsl_geld_2_eink_hh`.
    kinderzuschl_eink_relev
        See :func:`kinderzuschl_eink_relev`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    return (
        kinderzuschl_params["entzugsrate_eltern"]
        * (hh_id.replace(arbeitsl_geld_2_eink_hh) - kinderzuschl_eink_relev)
    ).clip(lower=0)


def kinderzuschl_eink_spanne(
    hh_id: IntSeries,
    arbeitsl_geld_2_brutto_eink_hh: FloatSeries,
    kinderzuschl_eink_min: FloatSeries,
    kinderzuschl_eink_max: FloatSeries,
    arbeitsl_geld_2_eink_hh: FloatSeries,
) -> BoolSeries:
    """Check if household income is in income range for child benefit.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    arbeitsl_geld_2_brutto_eink_hh
        See :func:`arbeitsl_geld_2_brutto_eink_hh`.
    kinderzuschl_eink_min
        See :func:`kinderzuschl_eink_min`.
    kinderzuschl_eink_max
        See :func:`kinderzuschl_eink_max`.
    arbeitsl_geld_2_eink_hh
        See :func:`arbeitsl_geld_2_eink_hh`.

    Returns
    -------

    """

    eink_spanne = (
        hh_id.replace(arbeitsl_geld_2_brutto_eink_hh) >= kinderzuschl_eink_min
    ) & (hh_id.replace(arbeitsl_geld_2_eink_hh) <= kinderzuschl_eink_max)

    return eink_spanne
