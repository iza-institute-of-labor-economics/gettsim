import numpy as np
import pandas as pd

from gettsim.benefits.kinderzuschlag import kiz
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_kinderzuschlag import OUT_COLS


def kinderzuschlag_temp(
    p_id,
    hh_id,
    tu_id,
    kind,
    alter,
    arbeitsstunden_w,
    bruttolohn_m,
    in_ausbildung,
    kaltmiete_m,
    heizkost_m,
    alleinerziehend,
    kindergeld_anspruch,
    alleinerziehenden_mehrbedarf,
    anz_erw_tu,
    anz_kinder_tu,
    arbeitsl_geld_2_brutto_eink_hh,
    sum_arbeitsl_geld_2_eink_hh,
    kindergeld_m_hh,
    unterhaltsvors_m,
    jahr,
    kinderzuschlag_eink_regel,
    kinderzuschlag_kaltmiete_m,
    kinderzuschlag_heizkost_m,
    kinderzuschlag_kosten_unterk_m,
    wohnbedarf_eltern_anteil,
    kinderzuschlag_eink_relev,
    anz_kinder_anspruch_per_hh,
    kinderzuschlag_eink_max,
    kinderzuschlag_eink_min,
    kinderzuschlag_kindereink_abzug,
    kinderzuschlag_eink_anrechn,
    kinderzuschlag_eink_spanne,
    arbeitsl_geld_2_params,
    kinderzuschlag_params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            kind,
            alter,
            arbeitsstunden_w,
            bruttolohn_m,
            in_ausbildung,
            kaltmiete_m,
            heizkost_m,
            alleinerziehend,
            kindergeld_anspruch,
            alleinerziehenden_mehrbedarf,
            anz_erw_tu,
            anz_kinder_tu,
            arbeitsl_geld_2_brutto_eink_hh,
            sum_arbeitsl_geld_2_eink_hh,
            kindergeld_m_hh,
            unterhaltsvors_m,
            jahr,
            kinderzuschlag_eink_regel,
            kinderzuschlag_kaltmiete_m,
            kinderzuschlag_heizkost_m,
            kinderzuschlag_kosten_unterk_m,
            anz_kinder_anspruch_per_hh,
            wohnbedarf_eltern_anteil,
            kinderzuschlag_eink_relev,
            kinderzuschlag_eink_max,
            kinderzuschlag_eink_min,
            kinderzuschlag_kindereink_abzug,
            kinderzuschlag_eink_anrechn,
            kinderzuschlag_eink_spanne,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=kiz,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={
            "params": kinderzuschlag_params,
            "arbeitsl_geld_2_params": arbeitsl_geld_2_params,
        },
    )

    return df["kinderzuschlag_temp"]


def kinderzuschlag_eink_regel(
    kinderzuschlag_eink_regel_bis_2010, kinderzuschlag_eink_regel_ab_2011
):
    return (
        kinderzuschlag_eink_regel_bis_2010
        if kinderzuschlag_eink_regel_ab_2011.empty
        else kinderzuschlag_eink_regel_ab_2011
    )


def kinderzuschlag_eink_regel_bis_2010(
    jahr, alleinerziehenden_mehrbedarf, anz_erw_tu, arbeitsl_geld_2_params
):
    bis_2010 = jahr <= 2010

    if bis_2010.all():
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

        eink_regel = pd.Series(index=jahr.index, data=data)

    else:
        eink_regel = pd.Series(dtype=float)

    return eink_regel


def kinderzuschlag_eink_regel_ab_2011(
    jahr, alleinerziehenden_mehrbedarf, anz_erw_tu, arbeitsl_geld_2_params
):
    ab_2011 = 2011 <= jahr

    if ab_2011.all():
        choices = [
            arbeitsl_geld_2_params["regelsatz"][1] * (1 + alleinerziehenden_mehrbedarf),
            arbeitsl_geld_2_params["regelsatz"][2] * (2 + alleinerziehenden_mehrbedarf),
            arbeitsl_geld_2_params["regelsatz"][3] * anz_erw_tu,
        ]

        data = np.select([anz_erw_tu == 1, anz_erw_tu == 2, anz_erw_tu > 2], choices,)

        eink_regel = pd.Series(index=jahr.index, data=data)

    else:
        eink_regel = pd.Series(dtype=float)

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
    sum_arbeitsl_geld_2_eink_hh, kinderzuschlag_eink_relev, kinderzuschlag_params
):
    """Calculate the parents income that needs to be subtracted (§6a (6) S. 3 BKGG)."""
    return (
        kinderzuschlag_params["kinderzuschlag_transferentzug_eltern"]
        * (sum_arbeitsl_geld_2_eink_hh - kinderzuschlag_eink_relev)
    ).clip(lower=0)


def kinderzuschlag_eink_spanne(
    arbeitsl_geld_2_brutto_eink_hh,
    kinderzuschlag_eink_min,
    kinderzuschlag_eink_max,
    sum_arbeitsl_geld_2_eink_hh,
):
    """Calculate a dummy for whether the household is in the correct income range."""
    return (arbeitsl_geld_2_brutto_eink_hh >= kinderzuschlag_eink_min) & (
        sum_arbeitsl_geld_2_eink_hh <= kinderzuschlag_eink_max
    )


# def kinderzuschlag():
#     pass


# def kinderzuschlag_ab_juli_2019():
#     pass


# def kinderzuschlag_ab_2005_bis_juni_2019():
#     """Calculate Kinderzuschlag from 2005 until June 2019."""
#     pass
