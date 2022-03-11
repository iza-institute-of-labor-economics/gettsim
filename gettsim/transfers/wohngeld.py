"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def wohngeld_m_hh(
    wohngeld_nach_vermög_check_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschl_vorrang_hh: BoolSeries,
    erwachsene_alle_rentner_hh: BoolSeries,
) -> FloatSeries:
    """Calculate final housing benefit per household.

    Parameters
    ----------
    wohngeld_nach_vermög_check_hh
        See :func:`wohngeld_nach_vermög_check_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    wohngeld_kinderzuschl_vorrang_hh
        See :func:`wohngeld_kinderzuschl_vorrang_hh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh`.

    Returns
    -------

    """
    cond = (
        ~wohngeld_vorrang_hh & ~wohngeld_kinderzuschl_vorrang_hh
        | erwachsene_alle_rentner_hh
    )
    wohngeld_nach_vermög_check_hh.loc[cond] = 0
    return wohngeld_nach_vermög_check_hh


def wohngeld_vor_vermög_check_hh(
    hh_id: IntSeries, wohngeld_vor_vermög_check: FloatSeries
) -> FloatSeries:
    """Calculate preliminary housing benefit per household.

    Social benefit for recipients with income above basic social assistance Computation
    is very complicated, accounts for household size, income, actual rent and differs on
    the municipality level ('Mietstufe' (1,...,6)).

    We usually don't have information on the last item. Therefore we assume 'Mietstufe'
    3, corresponding to an average level, but other Mietstufen can be specified in
    `household`.

    Benefit amount depends on parameters `wohngeld_miete_m` (rent) and
    `wohngeld_eink_m` (income) (§19 WoGG).

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    wohngeld_vor_vermög_check
        See :func:`wohngeld_vor_vermög_check`.

    Returns
    -------

    """
    # ToDo: When thinking about calculating wohngeld on the correct level, we need
    # account for multiple tax units in one household. The following is the old code!
    # See #218.
    # out = (wohngeld_vor_vermög_check * tu_vorstand).groupby(hh_id).sum().round(2)
    out = wohngeld_vor_vermög_check.groupby(hh_id).max().round(2)
    return out


def wohngeld_abzüge_tu(
    eink_st_tu: FloatSeries,
    ges_rentenv_beitr_m_tu: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calcualte housing benefit subtractions.

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
        (eink_st_tu > 0) * 1
        + (ges_rentenv_beitr_m_tu > 0)
        + (ges_krankenv_beitr_m_tu > 0)
    )
    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def wohngeld_brutto_eink_m_tu(
    brutto_eink_1_tu: FloatSeries,
    brutto_eink_4_tu: FloatSeries,
    brutto_eink_5_tu: FloatSeries,
    brutto_eink_6_tu: FloatSeries,
) -> FloatSeries:
    """Sum gross incomes relevant for housing benefit calculation per tax unit.

    Parameters
    ----------
    brutto_eink_1_tu
        See :func:`_brutto_eink_1_tu`.
    brutto_eink_4_tu
        See :func:`brutto_eink_4_tu`.
    brutto_eink_5_tu
        See :func:`brutto_eink_5_tu`.
    brutto_eink_6_tu
        See :func:`brutto_eink_6_tu`.

    Returns
    -------

    """
    return (
        brutto_eink_1_tu + brutto_eink_4_tu + brutto_eink_5_tu + brutto_eink_6_tu
    ) / 12


def wohngeld_sonstiges_eink_m_tu(
    arbeitsl_geld_m_tu: FloatSeries,
    sonstig_eink_m_tu: FloatSeries,
    eink_rente_zu_verst_m_tu: FloatSeries,
    unterhaltsvors_m_tu: FloatSeries,
    elterngeld_m_tu: FloatSeries,
) -> FloatSeries:
    """Sumn addtitional incomes relevant for housing benefit per tax unit.

    Parameters
    ----------
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
    return (
        arbeitsl_geld_m_tu
        + sonstig_eink_m_tu
        + eink_rente_zu_verst_m_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )


def anzahl_kinder_unter_11_per_tu(tu_id: IntSeries, alter: IntSeries) -> IntSeries:
    """Count children under eleven per tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------

    """
    return (alter < 11).groupby(tu_id).transform("sum")


def wohngeld_eink_abzüge_m_bis_2015(
    bruttolohn_m: FloatSeries,
    wohngeld_arbeitende_kinder: IntSeries,
    behinderungsgrad: IntSeries,
    alleinerz: BoolSeries,
    kind: BoolSeries,
    anzahl_kinder_unter_11_per_tu: IntSeries,
    wohngeld_params: dict,
):
    """Calculate housing benefit subtractions until 2015.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohngeld_arbeitende_kinder
        See :func:`wohngeld_arbeitende_kinder`.
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    anzahl_kinder_unter_11_per_tu
        See :func:`anzahl_kinder_unter_11_per_tu`.
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
    freib_kinder_m = (
        wohngeld_arbeitende_kinder
        * bruttolohn_m.clip(lower=None, upper=wohngeld_params["freib_kinder_m"][24])
    ) + (
        (alleinerz & ~kind)
        * anzahl_kinder_unter_11_per_tu
        * wohngeld_params["freib_kinder_m"][12]
    )

    return freib_behinderung_m + freib_kinder_m


def wohngeld_arbeitende_kinder(
    bruttolohn_m: FloatSeries, kindergeld_anspruch: BoolSeries
) -> IntSeries:
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
    kindergeld_anspruch: BoolSeries,
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
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
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
    workingchild = (bruttolohn_m > 0) & kindergeld_anspruch

    abzüge = (
        (behinderungsgrad > 0) * wohngeld_params["freib_behinderung"] / 12
        + workingchild
        * bruttolohn_m.clip(lower=0, upper=wohngeld_params["freib_kinder_m"][24])
        + alleinerz * wohngeld_params["freib_kinder_m"][12] * ~kind
    )

    return abzüge


def wohngeld_eink_m(
    tu_id: IntSeries,
    haushaltsgröße: IntSeries,
    wohngeld_eink_abzüge_m: FloatSeries,
    wohngeld_abzüge_tu: FloatSeries,
    wohngeld_brutto_eink_m_tu: FloatSeries,
    wohngeld_sonstiges_eink_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate final income relevant for calculation of housing benefit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_eink_abzüge_m
        See :func:`wohngeld_eink_abzüge_m`.
    wohngeld_abzüge_tu
        See :func:`wohngeld_abzüge_tu`.
    wohngeld_brutto_eink_m_tu
        See :func:`wohngeld_brutto_eink_m_tu`.
    wohngeld_sonstiges_eink_m_tu
        See :func:`wohngeld_sonstiges_eink_m_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    wohngeld_eink_abzüge_m_tu = wohngeld_eink_abzüge_m.groupby(tu_id).sum()

    vorläufiges_eink = (1 - wohngeld_abzüge_tu) * (
        wohngeld_brutto_eink_m_tu
        + wohngeld_sonstiges_eink_m_tu
        - wohngeld_eink_abzüge_m_tu
    )

    unteres_eink = haushaltsgröße.clip(upper=max(wohngeld_params["min_eink"])).replace(
        wohngeld_params["min_eink"]
    )

    return tu_id.replace(vorläufiges_eink).clip(lower=unteres_eink)


def wohngeld_min_miete(haushaltsgröße: IntSeries, wohngeld_params: dict) -> FloatSeries:
    """Calculate minimal rent subject housing benefit calculation.

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """

    return haushaltsgröße.clip(upper=(max(wohngeld_params["min_eink"]))).replace(
        wohngeld_params["min_miete"]
    )


def wohngeld_miete_m_bis_2008(
    mietstufe: IntSeries,
    immobilie_baujahr_hh: IntSeries,
    haushaltsgröße: IntSeries,
    hh_id: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    tax_unit_share: FloatSeries,
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
    haushaltsgröße
        See :func:`haushaltsgröße`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.
    wohngeld_min_miete
        See :func:`wohngeld_min_miete`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    immobilie_baujahr = hh_id.replace(immobilie_baujahr_hh)
    # Get yearly cutoff in params which is closest and above the construction year
    # of the property. We assume that the same cutoffs exist for each household
    # size.
    yearly_cutoffs = sorted(wohngeld_params["max_miete"][1], reverse=True)
    conditions = [immobilie_baujahr <= cutoff for cutoff in yearly_cutoffs]
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
            haushaltsgröße, constr_year_category, mietstufe
        )
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_m_ab_2009(
    mietstufe: IntSeries,
    haushaltsgröße: IntSeries,
    hh_id: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    tax_unit_share: FloatSeries,
    wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate maximal rent subject housing benefit calculation since 2009.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.
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
        for hh_größe, ms in zip(haushaltsgröße, mietstufe)
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_m_ab_2021(
    mietstufe: IntSeries,
    haushaltsgröße: IntSeries,
    hh_id: IntSeries,
    bruttokaltmiete_m_hh: FloatSeries,
    tax_unit_share: FloatSeries,
    wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate maximal rent subject housing benefit calculation since 2021.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.
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
        for hh_größe, ms in zip(haushaltsgröße, mietstufe)
    ]

    out = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return out


def wohngeld_vor_vermög_check(
    haushaltsgröße: IntSeries,
    wohngeld_eink_m: FloatSeries,
    wohngeld_miete_m: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calcualte preliminary housing benefit.

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
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
        for hh_größe in haushaltsgröße.clip(upper=(max(wohngeld_params["min_eink"])))
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
        * (haushaltsgröße - max(wohngeld_params["min_eink"]))
    ).clip(upper=wohngeld_miete_m)

    out = out.where(
        haushaltsgröße <= (max(wohngeld_params["min_eink"])), out_more_than_12
    )

    return out


def tax_unit_share(tu_id: IntSeries, haushaltsgröße: IntSeries) -> FloatSeries:
    """Calculate the share of tax units in household.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.

    Returns
    -------

    """
    return tu_id.groupby(tu_id).transform("count") / haushaltsgröße
