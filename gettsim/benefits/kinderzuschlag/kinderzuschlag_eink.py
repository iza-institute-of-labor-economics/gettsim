import numpy as np
import pandas as pd


def kinderzuschlag_eink_regel_bis_2010(
    alleinerziehenden_mehrbedarf, anz_erw_tu, arbeitsl_geld_2_params
):
    """This function creates "kinderzuschlag_eink_regel" until 2010.


    Parameters
    ----------
    alleinerziehenden_mehrbedarf
    anz_erw_tu
    arbeitsl_geld_2_params

    Returns
    -------

    """
    choices = [
        arbeitsl_geld_2_params["regelsatz"] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
        * (2 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"]
        * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
        * anz_erw_tu,
    ]

    data = np.select([anz_erw_tu == 1, anz_erw_tu == 2, anz_erw_tu > 2], choices,)

    eink_regel = pd.Series(index=alleinerziehenden_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschlag_eink_regel_ab_2011(
    alleinerziehenden_mehrbedarf, anz_erw_tu, arbeitsl_geld_2_params
):
    """This function creates "kinderzuschlag_eink_regel" since 2011.

    Parameters
    ----------
    alleinerziehenden_mehrbedarf
    anz_erw_tu
    arbeitsl_geld_2_params

    Returns
    -------

    """
    choices = [
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][3] * anz_erw_tu,
    ]

    data = np.select([anz_erw_tu == 1, anz_erw_tu == 2, anz_erw_tu > 2], choices,)

    eink_regel = pd.Series(index=alleinerziehenden_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschlag_eink_relev(
    kinderzuschlag_eink_regel, kinderzuschlag_kosten_unterk_m
):
    return kinderzuschlag_eink_regel + kinderzuschlag_kosten_unterk_m


def anz_kinder_anspruch_per_hh(hh_id, kindergeld_anspruch):
    """Count number of children eligible to child benefit (§6a (1) Nr. 1 BKGG)kdu."""
    return kindergeld_anspruch.groupby(hh_id).transform("sum")


def kinderzuschlag_eink_max(
    kinderzuschlag_eink_relev, anz_kinder_anspruch_per_hh, kinderzuschlag_params
):
    """Calculate kinderzuschlag depending on threshold.

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG)

    """
    return (
        kinderzuschlag_eink_relev
        + kinderzuschlag_params["kinderzuschlag"] * anz_kinder_anspruch_per_hh
    )


def kinderzuschlag_eink_min(hh_id, kind, alleinerziehend, kinderzuschlag_params):
    """Calculate minimum income.

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

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
    """Deduct children income for each eligible child (§6a (3) S.3 BKGG)."""
    return kindergeld_anspruch * (
        kinderzuschlag_params["kinderzuschlag"]
        - kinderzuschlag_params["kinderzuschlag_transferentzug_kind"]
        * (bruttolohn_m + unterhaltsvors_m)
    ).clip(lower=0)


def kinderzuschlag_eink_anrechn(
    arbeitsl_geld_2_eink_hh, kinderzuschlag_eink_relev, kinderzuschlag_params
):
    """Calculate the parents income that needs to be subtracted (§6a (6) S. 3 BKGG)."""
    return (
        kinderzuschlag_params["kinderzuschlag_transferentzug_eltern"]
        * (arbeitsl_geld_2_eink_hh - kinderzuschlag_eink_relev)
    ).clip(lower=0)


def kinderzuschlag_eink_spanne(
    kinderzuschlag_eink_spanne_bis_2004, kinderzuschlag_eink_spanne_ab_2005
):
    return (
        kinderzuschlag_eink_spanne_bis_2004
        if kinderzuschlag_eink_spanne_ab_2005.empty
        else kinderzuschlag_eink_spanne_ab_2005
    )


def kinderzuschlag_eink_spanne_bis_2004(jahr):
    bis_2004 = jahr <= 2004

    if bis_2004.all():
        eink_spanne = pd.Series(index=jahr.index, data=0)

    else:
        eink_spanne = pd.Series(dtype=float)

    return eink_spanne


def kinderzuschlag_eink_spanne_ab_2005(
    jahr,
    _arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_eink_max,
    arbeitsl_geld_2_eink_hh,
):
    """Calculate a dummy for whether the household is in the correct income range."""
    ab_2005 = 2005 <= jahr

    if ab_2005.all():
        eink_spanne = (_arbeitsl_geld_2_brutto_eink_hh >= kinderzuschlag_eink_min) & (
            arbeitsl_geld_2_eink_hh <= kinderzuschlag_eink_max
        )

    else:
        eink_spanne = pd.Series(dtype=float)

    return eink_spanne
