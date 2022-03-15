import numpy as np
import pandas as pd

from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kinderzuschl_kost_unterk_m(
    _kinderzuschl_wohnbedarf_eltern_anteil: FloatSeries,
    kinderzuschl_bruttokaltmiete_m: FloatSeries,
    kinderzuschl_heizkosten_m: FloatSeries,
) -> FloatSeries:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    _kinderzuschl_wohnbedarf_eltern_anteil
        See :func:`_kinderzuschl_wohnbedarf_eltern_anteil`.
    kinderzuschl_bruttokaltmiete_m
        See :func:`kinderzuschl_bruttokaltmiete_m`.
    kinderzuschl_heizkosten_m
        See :func:`kinderzuschl_heizkosten_m`.

    Returns
    -------

    """
    return _kinderzuschl_wohnbedarf_eltern_anteil * (
        kinderzuschl_bruttokaltmiete_m + kinderzuschl_heizkosten_m
    )


def kinderzuschl_bruttokaltmiete_m(
    bruttokaltmiete_m_hh: FloatSeries, _anteil_personen_in_haushalt_tu: FloatSeries,
) -> FloatSeries:
    """Share of household's monthly rent attributed to the tax unit.

    Parameters
    ----------
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.

    Returns
    -------

    """
    return bruttokaltmiete_m_hh * _anteil_personen_in_haushalt_tu


def kinderzuschl_heizkosten_m(
    heizkosten_m_hh: FloatSeries, _anteil_personen_in_haushalt_tu: FloatSeries,
) -> FloatSeries:
    """Share of household's heating expenses attributed to the tax unit.

    Parameters
    ----------
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.

    Returns
    -------

    """
    return heizkosten_m_hh * _anteil_personen_in_haushalt_tu


def _kinderzuschl_wohnbedarf_eltern_anteil(
    tu_id: IntSeries,
    anz_kinder_tu: IntSeries,
    anz_erwachsene_tu: IntSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate living needs broken down to the parents.
     Defined as parents' subsistence level on housing, divided by sum
     of subsistence level from parents and children.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    kinder_in_tu = anz_kinder_tu
    conditions = []
    choices = []
    ex_min = kinderzuschl_params["exmin"]
    adults_map = {1: "single", 2: "paare"}
    for n_adults in [1, 2]:
        for n_children in [1, 2, 3, 4]:
            condition = (kinder_in_tu == n_children) & (anz_erwachsene_tu == n_adults)
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

        condition = (kinder_in_tu >= 5) & (anz_erwachsene_tu == n_adults)
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
