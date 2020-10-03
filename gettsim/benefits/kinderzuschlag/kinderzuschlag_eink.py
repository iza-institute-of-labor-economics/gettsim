import numpy as np
import pandas as pd


from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

def kinderzuschlag_eink_regel_bis_2010(
    tu_id,
    hh_id,
    alleinerziehenden_mehrbedarf_hh,
    anz_erwachsene_tu,
    arbeitsl_geld_2_params,
):
    """This function creates "kinderzuschlag_eink_regel" until 2010.

    Parameters
    ----------
    tu_id
    hh_id
    alleinerziehenden_mehrbedarf_hh
    anz_erwachsene_tu
    arbeitsl_geld_2_params

    Returns
    -------

    """
    alleinerziehenden_mehrbedarf = hh_id.replace(alleinerziehenden_mehrbedarf_hh)
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


def kinderzuschlag_eink_regel_ab_2011(
    tu_id,
    hh_id,
    alleinerziehenden_mehrbedarf_hh,
    anz_erwachsene_tu,
    arbeitsl_geld_2_params,
):
    """This function creates "kinderzuschlag_eink_regel" since 2011.

    Parameters
    ----------
    tu_id
    hh_id
    alleinerziehenden_mehrbedarf_hh
    anz_erwachsene_tu
    arbeitsl_geld_2_params

    Returns
    -------

    """
    alleinerziehenden_mehrbedarf = hh_id.replace(alleinerziehenden_mehrbedarf_hh)
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


def kinderzuschlag_eink_relev(
    kinderzuschlag_eink_regel, kinderzuschlag_kosten_unterk_m
):
    """

    Parameters
    ----------
    kinderzuschlag_eink_regel
    kinderzuschlag_kosten_unterk_m

    Returns
    -------

    """
    return kinderzuschlag_eink_regel + kinderzuschlag_kosten_unterk_m


def anz_kinder_anspruch_per_hh(hh_id, kindergeld_anspruch):
    """Count number of children eligible to child benefit (§6a (1) Nr. 1 BKGG)kdu.

    Parameters
    ----------
    hh_id
    kindergeld_anspruch

    Returns
    -------

    """
    return kindergeld_anspruch.groupby(hh_id).transform("sum")


def kinderzuschlag_eink_max(
    kinderzuschlag_eink_relev, anz_kinder_anspruch_per_hh, kinderzuschlag_params
):
    """Calculate kinderzuschlag depending on threshold.

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG)

    Parameters
    ----------
    kinderzuschlag_eink_relev
    anz_kinder_anspruch_per_hh
    kinderzuschlag_params

    Returns
    -------

    """
    return (
        kinderzuschlag_eink_relev
        + kinderzuschlag_params["kinderzuschlag"] * anz_kinder_anspruch_per_hh
    )


def kinderzuschlag_eink_min(hh_id, kind, alleinerziehend, kinderzuschlag_params):
    """Calculate minimum income.

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    hh_id
    kind
    alleinerziehend
    kinderzuschlag_params

    Returns
    -------

    """
    hat_kinder_hh = kind.groupby(hh_id).transform("any")
    is_alleinerziehend_hh = alleinerziehend.groupby(hh_id).transform("all")

    conditions = [~hat_kinder_hh, is_alleinerziehend_hh, ~is_alleinerziehend_hh]
    choices = [
        0,
        kinderzuschlag_params["kinderzuschlag_min_eink_alleinerz"],
        kinderzuschlag_params["kinderzuschlag_min_eink_paare"],
    ]

    return pd.Series(index=hh_id.index, data=np.select(conditions, choices))


def kinderzuschlag_kindereink_abzug(
    kindergeld_anspruch, bruttolohn_m, unterhaltsvors_m, kinderzuschlag_params
):
    """Deduct children income for each eligible child (§6a (3) S.3 BKGG).

    Parameters
    ----------
    kindergeld_anspruch
    bruttolohn_m
    unterhaltsvors_m
    kinderzuschlag_params

    Returns
    -------

    """
    return kindergeld_anspruch * (
        kinderzuschlag_params["kinderzuschlag"]
        - kinderzuschlag_params["kinderzuschlag_transferentzug_kind"]
        * (bruttolohn_m + unterhaltsvors_m)
    ).clip(lower=0)


def kinderzuschlag_eink_anrechn(
    hh_id, arbeitsl_geld_2_eink_hh, kinderzuschlag_eink_relev, kinderzuschlag_params
):
    """Calculate the parents income that needs to be subtracted (§6a (6) S. 3 BKGG).

    Parameters
    ----------
    hh_id
    arbeitsl_geld_2_eink_hh
    kinderzuschlag_eink_relev
    kinderzuschlag_params

    Returns
    -------

    """
    return (
        kinderzuschlag_params["kinderzuschlag_transferentzug_eltern"]
        * (hh_id.replace(arbeitsl_geld_2_eink_hh) - kinderzuschlag_eink_relev)
    ).clip(lower=0)


def kinderzuschlag_eink_spanne(
    hh_id,
    _arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_eink_max,
    arbeitsl_geld_2_eink_hh,
):
    """Calculate a dummy for whether the household is in the correct income range.

    Parameters
    ----------
    hh_id
    _arbeitsl_geld_2_brutto_eink_hh
    kinderzuschlag_eink_min
    kinderzuschlag_eink_max
    arbeitsl_geld_2_eink_hh

    Returns
    -------

    """

    eink_spanne = (
        hh_id.replace(_arbeitsl_geld_2_brutto_eink_hh) >= kinderzuschlag_eink_min
    ) & (hh_id.replace(arbeitsl_geld_2_eink_hh) <= kinderzuschlag_eink_max)

    return eink_spanne
