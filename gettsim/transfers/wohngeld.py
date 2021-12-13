"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def wohngeld_m_hh(
    wohngeld_vermögens_check_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    alle_erwachsene_rentner_hh: BoolSeries,
) -> FloatSeries:
    """Calculate final housing benefit per household.

    Parameters
    ----------
    wohngeld_vermögens_check_hh
        See :func:`wohngeld_vermögens_check_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    wohngeld_kinderzuschlag_vorrang_hh
        See :func:`wohngeld_kinderzuschlag_vorrang_hh`.
    alle_erwachsene_rentner_hh
        See :func:`alle_erwachsene_rentner_hh`.

    Returns
    -------

    """
    cond = (
        ~wohngeld_vorrang_hh & ~wohngeld_kinderzuschlag_vorrang_hh
    ) | alle_erwachsene_rentner_hh
    wohngeld_vermögens_check_hh.loc[cond] = 0
    return wohngeld_vermögens_check_hh


def wohngeld_basis_hh(hh_id: IntSeries, wohngeld_basis: FloatSeries) -> FloatSeries:
    """Calculate preliminary housing benefit per household.

    Social benefit for recipients with income above basic social assistance Computation
    is very complicated, accounts for household size, income, actual rent and differs on
    the municipality level ('Mietstufe' (1,...,6)).

    We usually don't have information on the last item. Therefore we assume 'Mietstufe'
    3, corresponding to an average level, but other Mietstufen can be specified in
    `household`.

    Benefit amount depends on parameters `wohngeld_miete` (rent) and
    `wohngeld_eink` (income) (§19 WoGG).

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    wohngeld_basis
        See :func:`wohngeld_basis`.

    Returns
    -------

    """
    # ToDo: When thinking about calculating wohngeld on the correct level, we need
    # account for multiple tax units in one household. The following is the old code!
    # See #218.
    # out = (wohngeld_basis * tu_vorstand).groupby(hh_id).sum().round(2)
    out = wohngeld_basis.groupby(hh_id).max().round(2)
    return out


def zu_verst_ges_rente_tu(
    zu_verst_ges_rente: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Aggreate pension payments subject to taxation in tax unit.

    Parameters
    ----------
    zu_verst_ges_rente
        See :func:`zu_verst_ges_rente`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return zu_verst_ges_rente.groupby(tu_id).sum()


def wohngeld_abzüge_tu(
    eink_st_tu: FloatSeries,
    rentenv_beitr_m_tu: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calcualte housing benefit subtractions.

    Parameters
    ----------
    eink_st_tu
        See :func:`eink_st_tu`.
    rentenv_beitr_m_tu
        See :func:`rentenv_beitr_m_tu`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (eink_st_tu > 0) * 1 + (rentenv_beitr_m_tu > 0) + (ges_krankenv_beitr_m_tu > 0)
    )
    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def zu_verst_ges_rente(
    ertragsanteil: FloatSeries, gesamte_rente_m: FloatSeries
) -> FloatSeries:
    """Calculate pension payment subject to taxation.

    Parameters
    ----------
    ertragsanteil
        See :func:`ertragsanteil`.
    gesamte_rente_m
        See basic input variable :ref:`gesamte_rente_m <gesamte_rente_m>`.

    Returns
    -------

    """
    return ertragsanteil * gesamte_rente_m


def wohngeld_brutto_eink_tu(
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


def wohngeld_sonstiges_eink_tu(
    arbeitsl_geld_m_tu: FloatSeries,
    sonstig_eink_m_tu: FloatSeries,
    zu_verst_ges_rente_tu: FloatSeries,
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
    zu_verst_ges_rente_tu
        See :func:`zu_verst_ges_rente_tu`.
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
        + zu_verst_ges_rente_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )


def anzahl_kinder_unter_11_per_tu(tu_id: IntSeries, alter: IntSeries) -> IntSeries:
    """Count children under eleven per tax unit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    alter : IntSeries
        See :func:`alter`.

    Returns
    -------

    """
    return (alter < 11).groupby(tu_id).transform("sum")


def wohngeld_eink_abzüge_bis_2015(
    bruttolohn_m: FloatSeries,
    arbeitende_kinder: IntSeries,
    behinderungsgrad: IntSeries,
    alleinerziehend: BoolSeries,
    kind: BoolSeries,
    anzahl_kinder_unter_11_per_tu: IntSeries,
    wohngeld_params: dict,
):
    """Calculate housing benefit subtractions until 2015.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    arbeitende_kinder
        See :func:`arbeitende_kinder`.
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    alleinerziehend
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    anzahl_kinder_unter_11_per_tu
        See :func:`anzahl_kinder_unter_11_per_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzüge = (
        (behinderungsgrad > 80) * wohngeld_params["freib_behinderung"]["ab80"]
        + ((1 <= behinderungsgrad) & (behinderungsgrad <= 80))
        * wohngeld_params["freib_behinderung"]["u80"]
        + (
            arbeitende_kinder
            * bruttolohn_m.clip(lower=None, upper=wohngeld_params["freib_kinder"][24])
        )
        + (
            (alleinerziehend & ~kind)
            * anzahl_kinder_unter_11_per_tu
            * wohngeld_params["freib_kinder"][12]
        )
    )

    return abzüge


def arbeitende_kinder(
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


def wohngeld_eink_abzüge_ab_2016(
    bruttolohn_m: FloatSeries,
    kindergeld_anspruch: BoolSeries,
    behinderungsgrad: IntSeries,
    alleinerziehend: BoolSeries,
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
    alleinerziehend
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    workingchild = (bruttolohn_m > 0) & kindergeld_anspruch

    abzüge = (
        (behinderungsgrad > 0) * wohngeld_params["freib_behinderung"]
        + workingchild
        * bruttolohn_m.clip(lower=0, upper=wohngeld_params["freib_kinder"][24])
        + alleinerziehend * wohngeld_params["freib_kinder"][12] * ~kind
    )

    return abzüge


def wohngeld_eink(
    tu_id: IntSeries,
    haushaltsgröße: IntSeries,
    wohngeld_eink_abzüge: FloatSeries,
    wohngeld_abzüge_tu: FloatSeries,
    wohngeld_brutto_eink_tu: FloatSeries,
    wohngeld_sonstiges_eink_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calculate final income relevant for calculation of housing benefit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_eink_abzüge
        See :func:`wohngeld_eink_abzüge`.
    wohngeld_abzüge_tu
        See :func:`wohngeld_abzüge_tu`.
    wohngeld_brutto_eink_tu
        See :func:`wohngeld_brutto_eink_tu`.
    wohngeld_sonstiges_eink_tu
        See :func:`wohngeld_sonstiges_eink_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    wohngeld_eink_abzüge_tu = wohngeld_eink_abzüge.groupby(tu_id).sum()

    vorläufiges_eink = (1 - wohngeld_abzüge_tu) * (
        wohngeld_brutto_eink_tu + wohngeld_sonstiges_eink_tu - wohngeld_eink_abzüge_tu
    )

    unteres_eink = haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_eink"])

    return tu_id.replace(vorläufiges_eink).clip(lower=unteres_eink)


def wohngeld_min_miete(haushaltsgröße: IntSeries, wohngeld_params: dict) -> FloatSeries:
    """Calculate minamal rent subject housing benefit calculation.

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    return haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_miete"])


def wohngeld_miete_bis_2008(
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

    data = [
        wohngeld_params["max_miete"][hh_größe][constr_year][ms]
        if hh_größe <= 5
        else wohngeld_params["max_miete"][5][constr_year][ms]
        + wohngeld_params["max_miete"]["5plus"][constr_year][ms] * (hh_größe - 5)
        for hh_größe, constr_year, ms in zip(
            haushaltsgröße, constr_year_category, mietstufe
        )
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_ab_2009(
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
    data = [
        wohngeld_params["max_miete"][hh_größe][ms]
        if hh_größe <= 5
        else wohngeld_params["max_miete"][5][ms]
        + wohngeld_params["max_miete"]["5plus"][ms] * (hh_größe - 5)
        for hh_größe, ms in zip(haushaltsgröße, mietstufe)
    ]

    wg_miete = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return wg_miete


def wohngeld_miete_ab_2021(
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
    data = [
        wohngeld_params["max_miete"][hh_größe][ms]
        + wohngeld_params["heizkosten_zuschuss"][hh_größe]
        if hh_größe <= 5
        else wohngeld_params["max_miete"][5][ms]
        + (wohngeld_params["max_miete"]["5plus"][ms] * (hh_größe - 5))
        + wohngeld_params["heizkosten_zuschuss"][5]
        + wohngeld_params["heizkosten_zuschuss"]["5plus"] * (hh_größe - 5)
        for hh_größe, ms in zip(haushaltsgröße, mietstufe)
    ]

    out = (
        np.clip(data, a_min=None, a_max=hh_id.replace(bruttokaltmiete_m_hh))
        * tax_unit_share
    ).clip(lower=wohngeld_min_miete)

    return out


def wohngeld_basis(
    haushaltsgröße: IntSeries,
    wohngeld_eink: FloatSeries,
    wohngeld_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """Calcualte preliminary housing benefit.

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_eink
        See :func:`wohngeld_eink`.
    wohngeld_miete
        See :func:`wohngeld_miete`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    koeffizienten = [
        wohngeld_params["koeffizienten_berechnungsformel"][hh_größe]
        for hh_größe in haushaltsgröße.clip(upper=12)
    ]

    koeffizienten_a = [koeffizient["a"] for koeffizient in koeffizienten]
    koeffizienten_b = [koeffizient["b"] for koeffizient in koeffizienten]
    koeffizienten_c = [koeffizient["c"] for koeffizient in koeffizienten]

    out = (
        wohngeld_params["faktor_berechnungsformel"]
        * (
            wohngeld_miete
            - (
                (
                    koeffizienten_a
                    + (koeffizienten_b * wohngeld_miete)
                    + (koeffizienten_c * wohngeld_eink)
                )
                * wohngeld_eink
            )
        )
    ).clip(lower=0)

    # If more than 12 persons, there is a lump-sum on top.
    # The maximum is still capped at `wohngeld_miete`.
    out_more_than_12 = (
        out + wohngeld_params["bonus_12_mehr"] * (haushaltsgröße - 12)
    ).clip(upper=wohngeld_miete)

    out = out.where(haushaltsgröße <= 12, out_more_than_12)

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


def sonstig_eink_m_tu(sonstig_eink_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate additional per tax unit.

    Parameters
    ----------
    sonstig_eink_m
        See basic input variable :ref:`sonstig_eink_m <sonstig_eink_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return sonstig_eink_m.groupby(tu_id).sum()
