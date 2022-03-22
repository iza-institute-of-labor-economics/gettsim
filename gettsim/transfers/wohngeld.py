"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def wohngeld_m_hh(
    wohngeld_nach_vermög_check_m_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    erwachsene_alle_rentner_hh: BoolSeries,
) -> FloatSeries:
    """Calculate final housing benefit per household.

    Parameters
    ----------
    wohngeld_nach_vermög_check_m_hh
        See :func:`wohngeld_nach_vermög_check_m_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.

    Returns
    -------

    """
    if (not wohngeld_vorrang_hh) & (
        not wohngeld_kinderzuschl_vorrang_hh
    ) | erwachsene_alle_rentner_hh:
        out = 0.0
    else:
        out = wohngeld_nach_vermög_check_m_hh

    return out


def wohngeld_abzüge_m_tu(
    eink_st_tu: FloatSeries,
    ges_rentenv_beitr_m_tu: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate housing benefit subtractions.

    Parameters
    ----------
    eink_st_tu
        See :func:`eink_st_tu`.
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (eink_st_tu > 0) + (ges_rentenv_beitr_m_tu > 0) + (ges_krankenv_beitr_m_tu > 0)
    )
    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def wohngeld_eink_m_tu(
    eink_selbst_tu: FloatSeries,
    eink_abhängig_beschäftigt_tu: FloatSeries,
    kapitaleink_brutto_tu: FloatSeries,
    eink_vermietung_tu: FloatSeries,
    arbeitsl_geld_m_tu: FloatSeries,
    sonstig_eink_m_tu: FloatSeries,
    eink_rente_zu_verst_m_tu: FloatSeries,
    unterhaltsvors_m_tu: FloatSeries,
    elterngeld_m_tu: FloatSeries,
) -> FloatSeries:
    """Sum gross incomes relevant for housing benefit calculation per tax unit.

    Parameters
    ----------
    eink_selbst_tu
        See :func:`_eink_selbst_tu`.
    eink_abhängig_beschäftigt_tu
        See :func:`eink_abhängig_beschäftigt_tu`.
    kapitaleink_brutto_tu
        See :func:`kapitaleink_brutto_tu`.
    eink_vermietung_tu
        See :func:`eink_vermietung_tu`.
    arbeitsl_geld_m_tu
        See :func:`arbeitsl_geld_m_tu`.
    sonstig_eink_m_tu
        See :func:`sonstig_eink_m_tu`.
    eink_rente_zu_verst_m_tu
        See :func:`eink_rente_zu_verst_m_tu`.
    unterhaltsvors_m_tu
        See :func:`unterhaltsvors_m_tu`.
    elterngeld_m_tu
        See :func:`elterngeld_m_tu`.

    Returns
    -------

    """
    einkommen = (
        eink_selbst_tu
        + eink_abhängig_beschäftigt_tu
        + kapitaleink_brutto_tu
        + eink_vermietung_tu
    ) / 12

    transfers = (
        arbeitsl_geld_m_tu
        + eink_rente_zu_verst_m_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )
    return einkommen + transfers + sonstig_eink_m_tu


def wohngeld_eink_abzüge_m_bis_2015(
    bruttolohn_m: FloatSeries,
    wohngeld_arbeitendes_kind: BoolSeries,
    behinderungsgrad: IntSeries,
    alleinerz: BoolSeries,
    kind: BoolSeries,
    anz_kinder_bis_10_tu: IntSeries,
    wohngeld_params: dict,
):
    """Calculate housing benefit subtractions until 2015.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohngeld_arbeitendes_kind
        See :func:`wohngeld_arbeitendes_kind`.
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    anz_kinder_bis_10_tu
        See :func:`anz_kinder_bis_10_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    freib_behinderung_m = piecewise_polynomial(
        behinderungsgrad,
        thresholds=list(wohngeld_params["freib_behinderung"]) + [np.inf],
        rates=np.array([[0] * len(wohngeld_params["freib_behinderung"])]),
        intercepts_at_lower_thresholds=[
            yearly_v / 12 for yearly_v in wohngeld_params["freib_behinderung"].values()
        ],
    )

    # Subtraction for single parents and working children
    if wohngeld_arbeitendes_kind:
        freib_kinder_m = min(
            bruttolohn_m, wohngeld_params["freib_kinder_m"]["arbeitendes_kind"]
        )

    elif alleinerz & (not kind):
        freib_kinder_m = (
            anz_kinder_bis_10_tu * wohngeld_params["freib_kinder_m"]["alleinerz"]
        )
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def wohngeld_arbeitendes_kind(
    bruttolohn_m: FloatSeries, kindergeld_anspruch: BoolSeries
) -> BoolSeries:
    """Check if chiildren are working.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.

    Returns
    -------

    """
    return (bruttolohn_m > 0) & kindergeld_anspruch


def wohngeld_eink_abzüge_m_ab_2016(
    bruttolohn_m: FloatSeries,
    wohngeld_arbeitendes_kind: BoolSeries,
    behinderungsgrad: IntSeries,
    alleinerz: BoolSeries,
    kind: BoolSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate housing benefit subtracting since 2016.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohngeld_arbeitendes_kind
        See :func:`wohngeld_arbeitendes_kind`.
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    freib_behinderung_m = (
        wohngeld_params["freib_behinderung"] / 12 if behinderungsgrad > 0 else 0
    )

    # Subtraction for single parents and working children
    if wohngeld_arbeitendes_kind:
        freib_kinder_m = min(
            bruttolohn_m, wohngeld_params["freib_kinder_m"]["arbeitendes_kind"]
        )
    elif alleinerz & (not kind):
        freib_kinder_m = wohngeld_params["freib_kinder_m"]["alleinerz"]
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def wohngeld_eink_m(
    haushaltsgröße_hh: IntSeries,
    wohngeld_eink_abzüge_m_tu: FloatSeries,
    wohngeld_abzüge_m_tu: FloatSeries,
    wohngeld_eink_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate final income relevant for calculation of housing benefit.

    Parameters
    ----------
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_eink_abzüge_m_tu
        See :func:`wohngeld_eink_abzüge_m_tu`.
    wohngeld_abzüge_m_tu
        See :func:`wohngeld_abzüge_m_tu`.
    wohngeld_eink_m_tu
        See :func:`wohngeld_eink_m_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    vorläufiges_eink = (1 - wohngeld_abzüge_m_tu) * (
        wohngeld_eink_m_tu - wohngeld_eink_abzüge_m_tu
    )

    unteres_eink = wohngeld_params["min_eink"].min(
        haushaltsgröße_hh, max(wohngeld_params["min_eink"])
    )

    out = max(vorläufiges_eink, unteres_eink)
    return out


def wohngeld_min_miete(
    haushaltsgröße_hh: IntSeries, wohngeld_params: dict
) -> FloatSeries:
    """Calculate minimal rent subject housing benefit calculation.

    Parameters
    ----------
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    out = wohngeld_params["min_miete"].min(
        haushaltsgröße_hh, max(wohngeld_params["min_miete"])
    )
    return out


def wohngeld_miete_m_bis_2008(
    mietstufe: IntSeries,
    immobilie_baujahr_hh: IntSeries,
    haushaltsgröße_hh: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    _anteil_personen_in_haushalt_tu: FloatSeries,
    wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
):
    """Calculate maximal rent subject housing benefit calculation until 2008.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    immobilie_baujahr_hh
        See basic input variable :ref:`immobilie_baujahr_hh <immobilie_baujahr_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.
    wohngeld_min_miete
        See :func:`wohngeld_min_miete`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    # Get yearly cutoff in params which is closest and above the construction year
    # of the property. We assume that the same cutoffs exist for each household
    # size.
    selected_bin = np.searchsorted(thresholds, x, side="right") - 1

    yearly_cutoffs = sorted(wohngeld_params["max_miete"][1], reverse=True)
    conditions = [immobilie_baujahr_hh <= cutoff for cutoff in yearly_cutoffs]
    constr_year_category = np.select(conditions, yearly_cutoffs)
    max_definierte_hh_größe = max(
        i for i in wohngeld_params["max_miete"] if isinstance(i, int)
    )
    data = [
        wohngeld_params["max_miete"][hh_größe][constr_year][ms]
        if hh_größe <= max_definierte_hh_größe
        else wohngeld_params["max_miete"][max_definierte_hh_größe][constr_year][ms]
        + wohngeld_params["max_miete"]["jede_weitere_person"][constr_year][ms]
        * (hh_größe - max_definierte_hh_größe)
        for hh_größe, constr_year, ms in zip(
            haushaltsgröße_hh, constr_year_category, mietstufe
        )
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=bruttokaltmiete_m_hh)
        * _anteil_personen_in_haushalt_tu
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_m_ab_2009(
    mietstufe: IntSeries,
    haushaltsgröße_hh: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    _anteil_personen_in_haushalt_tu: FloatSeries,
    wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate maximal rent subject housing benefit calculation since 2009.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.
    wohngeld_min_miete
        See :func:`wohngeld_min_miete`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    max_definierte_hh_größe = max(
        i for i in wohngeld_params["max_miete"] if isinstance(i, int)
    )
    data = [
        wohngeld_params["max_miete"][hh_größe][ms]
        if hh_größe <= max_definierte_hh_größe
        else wohngeld_params["max_miete"][max_definierte_hh_größe][ms]
        + wohngeld_params["max_miete"]["jede_weitere_person"][ms]
        * (hh_größe - max_definierte_hh_größe)
        for hh_größe, ms in zip(haushaltsgröße_hh, mietstufe)
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=bruttokaltmiete_m_hh)
        * _anteil_personen_in_haushalt_tu
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_m_ab_2021(
    mietstufe: IntSeries,
    haushaltsgröße_hh: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    _anteil_personen_in_haushalt_tu: FloatSeries,
    wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate maximal rent subject housing benefit calculation since 2021.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.
    wohngeld_min_miete
        See :func:`wohngeld_min_miete`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    max_definierte_hh_größe = max(
        i for i in wohngeld_params["max_miete"] if isinstance(i, int)
    )
    data = [
        wohngeld_params["max_miete"][hh_größe][ms]
        + wohngeld_params["heizkosten_zuschuss"][hh_größe]
        if hh_größe <= max_definierte_hh_größe
        else wohngeld_params["max_miete"][5][ms]
        + (
            wohngeld_params["max_miete"]["jede_weitere_person"][ms]
            * (hh_größe - max_definierte_hh_größe)
        )
        + wohngeld_params["heizkosten_zuschuss"][5]
        + wohngeld_params["heizkosten_zuschuss"]["5plus"]
        * (hh_größe - max_definierte_hh_größe)
        for hh_größe, ms in zip(haushaltsgröße_hh, mietstufe)
    ]

    out = (
        np.clip(data, a_min=None, a_max=bruttokaltmiete_m_hh)
        * _anteil_personen_in_haushalt_tu
    ).clip(lower=wohngeld_min_miete)

    return out


def wohngeld_vor_vermög_check_m(
    haushaltsgröße_hh: IntSeries,
    wohngeld_eink_m: FloatSeries,
    wohngeld_miete_m: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calcualte preliminary housing benefit.

    Parameters
    ----------
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_eink_m
        See :func:`wohngeld_eink_m`.
    wohngeld_miete_m
        See :func:`wohngeld_miete_m`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    koeffizienten = [
        wohngeld_params["koeffizienten_berechnungsformel"][hh_größe]
        for hh_größe in haushaltsgröße_hh.clip(upper=(max(wohngeld_params["min_eink"])))
    ]

    koeffizienten_a = [koeffizient["a"] for koeffizient in koeffizienten]
    koeffizienten_b = [koeffizient["b"] for koeffizient in koeffizienten]
    koeffizienten_c = [koeffizient["c"] for koeffizient in koeffizienten]

    out = (
        wohngeld_params["faktor_berechnungsformel"]
        * (
            wohngeld_miete_m
            - (
                (
                    koeffizienten_a
                    + (koeffizienten_b * wohngeld_miete_m)
                    + (koeffizienten_c * wohngeld_eink_m)
                )
                * wohngeld_eink_m
            )
        )
    ).clip(lower=0)

    # If more than 12 persons, there is a lump-sum on top.
    # The maximum is still capped at `wohngeld_miete_m`.
    out_more_than_12 = (
        out
        + wohngeld_params["bonus_12_mehr"]
        * (haushaltsgröße_hh - max(wohngeld_params["min_eink"]))
    ).clip(upper=wohngeld_miete_m)

    out = out.where(
        haushaltsgröße_hh <= (max(wohngeld_params["min_eink"])), out_more_than_12
    )

    return out


def _anteil_personen_in_haushalt_tu(
    tax_unit_größe_tu: IntSeries, haushaltsgröße_hh: IntSeries
) -> FloatSeries:
    """Calculate the share of tax units in household.

    ToDo: Change to tax_unit_größe / haushaltsgröße_hh

    Parameters
    ----------
    tax_unit_größe_tu
        See :func:`tax_unit_größe_tu`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.

    Returns
    -------

    """
    return tax_unit_größe_tu / haushaltsgröße_hh
