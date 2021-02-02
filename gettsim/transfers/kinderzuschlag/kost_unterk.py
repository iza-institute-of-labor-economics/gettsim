import numpy as np
import pandas as pd

from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschlag_kosten_unterk_m(
    wohnbedarf_eltern_anteil: FloatSeries,
    kinderzuschlag_kaltmiete_m: FloatSeries,
    kinderzuschlag_heizkost_m: FloatSeries,
) -> FloatSeries:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    wohnbedarf_eltern_anteil
        See :func:`wohnbedarf_eltern_anteil`.
    kinderzuschlag_kaltmiete_m
        See :func:`kinderzuschlag_kaltmiete_m`.
    kinderzuschlag_heizkost_m
        See :func:`kinderzuschlag_heizkost_m`.

    Returns
    -------

    """
    return wohnbedarf_eltern_anteil * (
        kinderzuschlag_kaltmiete_m + kinderzuschlag_heizkost_m
    )


def kinderzuschlag_kaltmiete_m(
    hh_id: IntSeries, kaltmiete_m_hh: FloatSeries, tax_unit_share: FloatSeries
) -> FloatSeries:
    """Calculate costs of living without heating costs.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kaltmiete_m_hh
        See basic input variable :ref:`kaltmiete_m_hh <kaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.

    Returns
    -------

    """
    return hh_id.replace(kaltmiete_m_hh) * tax_unit_share


def kinderzuschlag_heizkost_m(
    hh_id: IntSeries, heizkosten_m_hh: FloatSeries, tax_unit_share: FloatSeries
) -> FloatSeries:
    """Calculate costs of heating.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.

    Returns
    -------

    """
    return hh_id.replace(heizkosten_m_hh) * tax_unit_share


def wohnbedarf_eltern_anteil(
    tu_id: IntSeries,
    anz_kinder_tu: IntSeries,
    anz_erwachsene_tu: IntSeries,
    kinderzuschlag_params: dict,
) -> FloatSeries:
    """Calculate living needs broken down to the parents.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    kinderzuschlag_params
        See params documentation :ref:`kinderzuschlag_params <kinderzuschlag_params>`.

    Returns
    -------

    """
    kinder_in_tu = tu_id.replace(anz_kinder_tu)
    erwachsene_in_tu = tu_id.replace(anz_erwachsene_tu)
    conditions = []
    choices = []
    ex_min = kinderzuschlag_params["exmin"]
    adults_map = {1: "single", 2: "paare"}
    for n_adults in [1, 2]:
        for n_children in [1, 2, 3, 4]:
            condition = (kinder_in_tu == n_children) & (erwachsene_in_tu == n_adults)
            """
            Calculate share of living costs to attributed to the parents.
            Defined as parents' subsistence level on housing, divided by sum
            of subsistence level from parents and children.
            """
            choice = (
                ex_min["kosten_der_unterkunft"][adults_map[n_adults]]
                + ex_min["heizkosten"][adults_map[n_adults]]
            ) / (
                ex_min["kosten_der_unterkunft"][adults_map[n_adults]]
                + ex_min["heizkosten"][adults_map[n_adults]]
                + (
                    n_children
                    * (
                        ex_min["kosten_der_unterkunft"]["kinder"]
                        + ex_min["heizkosten"]["kinder"]
                    )
                )
            )

            conditions.append(condition)
            choices.append(choice)

        condition = (kinder_in_tu >= 5) & (erwachsene_in_tu == n_adults)
        choice = (
            ex_min["kosten_der_unterkunft"][adults_map[n_adults]]
            + ex_min["heizkosten"][adults_map[n_adults]]
        ) / (
            ex_min["kosten_der_unterkunft"][adults_map[n_adults]]
            + ex_min["heizkosten"][adults_map[n_adults]]
            + (
                5
                * (
                    ex_min["kosten_der_unterkunft"]["kinder"]
                    + ex_min["heizkosten"]["kinder"]
                )
            )
        )

        conditions.append(condition)
        choices.append(choice)

    # Add defaults. Is is really necessary or are the former conditions exhaustive?
    conditions.append(True)
    choices.append(1)

    anteil = pd.Series(index=tu_id.index, data=np.select(conditions, choices))

    return anteil
