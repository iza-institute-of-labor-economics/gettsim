import numpy as np
import pandas as pd
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschlag_kosten_unterk_m(
    wohnbedarf_eltern_anteil, kinderzuschlag_kaltmiete_m, kinderzuschlag_heizkost_m
):
    """Calculate share of living costs.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    wohnbedarf_eltern_anteil
    kinderzuschlag_kaltmiete_m
    kinderzuschlag_heizkost_m

    Returns
    -------

    """
    return wohnbedarf_eltern_anteil * (
        kinderzuschlag_kaltmiete_m + kinderzuschlag_heizkost_m
    )


def kinderzuschlag_kaltmiete_m(hh_id, kaltmiete_m_hh, tax_unit_share):
    """

    Parameters
    ----------
    hh_id
    kaltmiete_m_hh
    tax_unit_share

    Returns
    -------

    """
    return hh_id.replace(kaltmiete_m_hh) * tax_unit_share


def kinderzuschlag_heizkost_m(hh_id, heizkosten_m_hh, tax_unit_share):
    """

    Parameters
    ----------
    hh_id
    heizkosten_m_hh
    tax_unit_share

    Returns
    -------

    """
    return hh_id.replace(heizkosten_m_hh) * tax_unit_share


def wohnbedarf_eltern_anteil(
    tu_id, anz_kinder_tu, anz_erwachsene_tu, kinderzuschlag_params
):
    """Calculate living needs broken down to the parents.

    Parameters
    ----------
    tu_id
    anz_kinder_tu
    anz_erwachsene_tu
    kinderzuschlag_params

    Returns
    -------

    """
    kinder_in_tu = tu_id.replace(anz_kinder_tu)
    erwachsene_in_tu = tu_id.replace(anz_erwachsene_tu)
    conditions = []
    choices = []
    for n_adults in [1, 2]:
        for n_children in [1, 2, 3, 4]:
            condition = (kinder_in_tu == n_children) & (erwachsene_in_tu == n_adults)
            choice = kinderzuschlag_params["wohnbedarf_eltern_anteil"][n_adults][
                n_children - 1
            ]

            conditions.append(condition)
            choices.append(choice)

        condition = (kinder_in_tu >= 5) & (erwachsene_in_tu == n_adults)
        choice = kinderzuschlag_params["wohnbedarf_eltern_anteil"][n_adults][4]

        conditions.append(condition)
        choices.append(choice)

    # Add defaults. Is is really necessary or are the former conditions exhaustive?
    conditions.append(True)
    choices.append(1)

    anteil = pd.Series(index=tu_id.index, data=np.select(conditions, choices))

    return anteil
