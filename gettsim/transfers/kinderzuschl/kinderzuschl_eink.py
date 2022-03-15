import numpy as np
import pandas as pd

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_eink_regel_m_bis_2010(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    alleinerz_mehrbedarf = _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
    erwachsene_in_tu = anz_erwachsene_tu
    choices = [
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerz_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
        * (2 + alleinerz_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        * erwachsene_in_tu,
    ]

    data = np.select(
        [erwachsene_in_tu == 1, erwachsene_in_tu == 2, erwachsene_in_tu > 2], choices,
    )

    eink_regel = pd.Series(index=alleinerz_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschl_eink_regel_m_ab_2011(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    alleinerz_mehrbedarf = _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
    erwachsene_in_tu = anz_erwachsene_tu
    choices = [
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerz_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerz_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][3] * erwachsene_in_tu,
    ]

    data = np.select(
        [erwachsene_in_tu == 1, erwachsene_in_tu == 2, erwachsene_in_tu > 2], choices,
    )

    eink_regel = pd.Series(index=alleinerz_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschl_eink_relev_m(
    kinderzuschl_eink_regel_m: FloatSeries, kinderzuschl_kost_unterk_m: FloatSeries
) -> FloatSeries:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    kinderzuschl_eink_regel_m
        See :func:`kinderzuschl_eink_regel_m`.
    kinderzuschl_kost_unterk_m
        See :func:`kinderzuschl_kost_unterk_m`.

    Returns
    -------

    """
    return kinderzuschl_eink_regel_m + kinderzuschl_kost_unterk_m


def _kinderzuschl_anz_kinder_anspruch_hh(
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


def kinderzuschl_eink_max_m(
    kinderzuschl_eink_relev_m: FloatSeries,
    _kinderzuschl_anz_kinder_anspruch_hh: IntSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate maximum income to be eligible for additional
       child benefit (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    kinderzuschl_eink_relev_m
        See :func:`kinderzuschl_eink_relev_m`.
    _kinderzuschl_anz_kinder_anspruch_hh
        See :func:`_kinderzuschl_anz_kinder_anspruch_hh`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    return (
        kinderzuschl_eink_relev_m
        + kinderzuschl_params["maximum"] * _kinderzuschl_anz_kinder_anspruch_hh
    )


def kinderzuschl_eink_min_m(
    hh_id: IntSeries,
    kind: BoolSeries,
    alleinerz: BoolSeries,
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
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    hat_kinder_hh = kind.groupby(hh_id).transform("any")
    is_alleinerz_hh = alleinerz.groupby(hh_id).transform("all")

    conditions = [(not hat_kinder_hh), is_alleinerz_hh, (not is_alleinerz_hh)]
    choices = [
        0,
        kinderzuschl_params["min_eink_alleinerz"],
        kinderzuschl_params["min_eink_paare"],
    ]

    return pd.Series(index=hh_id.index, data=np.select(conditions, choices))


def kinderzuschl_kindereink_abzug_m(
    kindergeld_anspruch: BoolSeries,
    bruttolohn_m: FloatSeries,
    unterhaltsvors_m: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Child benefit after children income for each eligible child is considered.

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
    out = kindergeld_anspruch * (
        kinderzuschl_params["maximum"]
        - kinderzuschl_params["entzugsrate_kind"] * (bruttolohn_m + unterhaltsvors_m)
    )

    if out < 0:
        return 0
    else:
        return out


def kinderzuschl_eink_anrechn_m(
    arbeitsl_geld_2_eink_m_hh: FloatSeries,
    kinderzuschl_eink_relev_m: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.
    kinderzuschl_eink_relev_m
        See :func:`kinderzuschl_eink_relev_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        arbeitsl_geld_2_eink_m_hh - kinderzuschl_eink_relev_m
    )

    if out < 0:
        return 0
    else:
        return out


def kinderzuschl_eink_spanne(
    arbeitsl_geld_2_brutto_eink_m_hh: FloatSeries,
    kinderzuschl_eink_min_m: FloatSeries,
    kinderzuschl_eink_max_m: FloatSeries,
    arbeitsl_geld_2_eink_m_hh: FloatSeries,
) -> BoolSeries:
    """Check if household income is in income range for child benefit.

    Parameters
    ----------
    arbeitsl_geld_2_brutto_eink_m_hh
        See :func:`arbeitsl_geld_2_brutto_eink_m_hh`.
    kinderzuschl_eink_min_m
        See :func:`kinderzuschl_eink_min_m`.
    kinderzuschl_eink_max_m
        See :func:`kinderzuschl_eink_max_m`.
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.

    Returns
    -------

    """

    eink_spanne = (arbeitsl_geld_2_brutto_eink_m_hh >= kinderzuschl_eink_min_m) & (
        arbeitsl_geld_2_eink_m_hh <= kinderzuschl_eink_max_m
    )

    return eink_spanne
