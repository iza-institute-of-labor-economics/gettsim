import numpy as np
import pandas as pd


def kinderzuschlag_eink_regel_bis_2010(
    alleinerziehenden_mehrbedarf, anz_erw_tu, arbeitsl_geld_2_params
):
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
    choices = [
        arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf),
        arbeitsl_geld_2_params["regelsatz"][3] * anz_erw_tu,
    ]

    data = np.select([anz_erw_tu == 1, anz_erw_tu == 2, anz_erw_tu > 2], choices,)

    eink_regel = pd.Series(index=alleinerziehenden_mehrbedarf.index, data=data)

    return eink_regel


def kinderzuschlag_kaltmiete_m(kaltmiete_m, tax_unit_share):
    return kaltmiete_m * tax_unit_share


def kinderzuschlag_heizkost_m(heizkost_m, tax_unit_share):
    return heizkost_m * tax_unit_share


def kinderzuschlag_kosten_unterk_m(
    wohnbedarf_eltern_anteil, kinderzuschlag_kaltmiete_m, kinderzuschlag_heizkost_m
):
    """Calculate share of living costs.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    """
    return wohnbedarf_eltern_anteil * (
        kinderzuschlag_kaltmiete_m + kinderzuschlag_heizkost_m
    )


def wohnbedarf_eltern_anteil(anz_kinder_tu, anz_erw_tu, kinderzuschlag_params):
    """Calculate living needs broken down to the parents."""
    conditions = []
    choices = []
    for n_adults in [1, 2]:
        for n_children in [1, 2, 3, 4]:
            condition = (anz_kinder_tu == n_children) & (anz_erw_tu == n_adults)
            choice = kinderzuschlag_params["wohnbedarf_eltern_anteil"][n_adults][
                n_children - 1
            ]

            conditions.append(condition)
            choices.append(choice)

        condition = (anz_kinder_tu >= 5) & (anz_erw_tu == n_adults)
        choice = kinderzuschlag_params["wohnbedarf_eltern_anteil"][n_adults][4]

        conditions.append(condition)
        choices.append(choice)

    # Add defaults. Is is really necessary or are the former conditions exhaustive?
    conditions.append(True)
    choices.append(1)

    anteil = pd.Series(index=anz_erw_tu.index, data=np.select(conditions, choices))

    return anteil


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
    eink_anr_arbeitsl_geld_2_hh, kinderzuschlag_eink_relev, kinderzuschlag_params
):
    """Calculate the parents income that needs to be subtracted (§6a (6) S. 3 BKGG)."""
    return (
        kinderzuschlag_params["kinderzuschlag_transferentzug_eltern"]
        * (eink_anr_arbeitsl_geld_2_hh - kinderzuschlag_eink_relev)
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
    arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_eink_max,
    eink_anr_arbeitsl_geld_2_hh,
):
    """Calculate a dummy for whether the household is in the correct income range."""
    ab_2005 = 2005 <= jahr

    if ab_2005.all():
        eink_spanne = (arbeitsl_geld_2_brutto_eink_hh >= kinderzuschlag_eink_min) & (
            eink_anr_arbeitsl_geld_2_hh <= kinderzuschlag_eink_max
        )

    else:
        eink_spanne = pd.Series(dtype=float)

    return eink_spanne


def kinderzuschlag_ab_juli_2019(
    hh_id,
    arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_kindereink_abzug,
    kinderzuschlag_eink_anrechn,
):
    """Kinderzuschlag / Additional Child Benefit

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
    kinderzuschlag = pd.Series(index=kinderzuschlag_eink_min.index, data=0)
    condition = arbeitsl_geld_2_brutto_eink_hh >= kinderzuschlag_eink_min
    kinderzuschlag.loc[condition] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return kinderzuschlag


def kinderzuschlag_ab_2005_bis_juni_2019(
    hh_id,
    kinderzuschlag_eink_spanne,
    kinderzuschlag_kindereink_abzug,
    kinderzuschlag_eink_anrechn,
):
    """Kinderzuschlag / Additional Child Benefit

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
    kinderzuschlag = pd.Series(index=kinderzuschlag_eink_spanne.index, data=0)
    kinderzuschlag.loc[kinderzuschlag_eink_spanne] = (
        kinderzuschlag_kindereink_abzug.groupby(hh_id).transform("sum")
        - kinderzuschlag_eink_anrechn
    ).clip(lower=0)

    return kinderzuschlag


def kinderzuschlag_temp_ab_2005(hh_id, kinderzuschlag):
    """Calculate kinderzuschlag_temp since 2005.

    'kiz_temp' is the theoretical kiz claim, before it is checked against other benefits
    later on.

    """
    return kinderzuschlag.groupby(hh_id).transform("max")


def kinderzuschlag_temp_bis_2004(p_id):
    """Calculate kinderzuschlag_temp until 2004.

    'kiz_temp' is the theoretical kiz claim, before it is checked against other benefits
    later on.

    """
    return pd.Series(index=p_id.index, data=0)
