"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def wohngeld_m_hh(
    wohngeld_vermögens_check_hh: FloatSeries,
    wohngeld_vorrang_hh: BoolSeries,
    wohngeld_kinderzuschlag_vorrang_hh: BoolSeries,
    rentner_in_hh: BoolSeries,
) -> FloatSeries:
    """

    Parameters
    ----------
    wohngeld_vermögens_check_hh
        See :func:`wohngeld_vermögens_check_hh`.
    wohngeld_vorrang_hh
        See :func:`wohngeld_vorrang_hh`.
    wohngeld_kinderzuschlag_vorrang_hh
        See :func:`wohngeld_kinderzuschlag_vorrang_hh`.
    rentner_in_hh
        See :func:`rentner_in_hh`.

    Returns
    -------

    """
    cond = ~wohngeld_vorrang_hh & ~wohngeld_kinderzuschlag_vorrang_hh | rentner_in_hh
    wohngeld_vermögens_check_hh.loc[cond] = 0
    return wohngeld_vermögens_check_hh


def wohngeld_basis_hh(hh_id: IntSeries, wohngeld_basis: FloatSeries) -> FloatSeries:
    """Compute "Wohngeld" or housing benefits.

    Social benefit for recipients with income above basic social assistance Computation
    is very complicated, accounts for household size, income, actual rent and differs on
    the municipality level ('Mietstufe' (1,...,6)).

    We usually don't have information on the last item. Therefore we assume 'Mietstufe'
    3, corresponding to an average level, but other Mietstufen can be specified in
    `household`.

    Benefit amount depends on parameters `wohngeld_max_miete` (rent) and
    `_wohngeld_eink` (income) (§19 WoGG).

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


def _zu_verst_ges_rente_tu(
    _zu_verst_ges_rente: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """

    Parameters
    ----------
    _zu_verst_ges_rente
        See :func:`_zu_verst_ges_rente`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return _zu_verst_ges_rente.groupby(tu_id).sum()


def _wohngeld_abzüge_tu(
    eink_st_tu: FloatSeries,
    rentenv_beitr_m_tu: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    eink_st_tu
        See :func:`eink_st_tu`.
    rentenv_beitr_m_tu
        See :func:`rentenv_beitr_m_tu`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    wohngeld_params
        See :ref:`wohngeld_params`.

    Returns
    -------

    """
    abzug_stufen = (
        (eink_st_tu > 0) * 1 + (rentenv_beitr_m_tu > 0) + (ges_krankenv_beitr_m_tu > 0)
    )
    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def _zu_verst_ges_rente(
    _ertragsanteil: FloatSeries, ges_rente_m: FloatSeries
) -> FloatSeries:
    """

    Parameters
    ----------
    _ertragsanteil
        See :func:`_ertragsanteil`.
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.

    Returns
    -------

    """
    return _ertragsanteil * ges_rente_m


def _wohngeld_brutto_eink_tu(
    brutto_eink_1_tu: FloatSeries,
    brutto_eink_4_tu: FloatSeries,
    brutto_eink_5_tu: FloatSeries,
    brutto_eink_6_tu: FloatSeries,
) -> FloatSeries:
    """

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


def _wohngeld_sonstiges_eink_tu(
    arbeitsl_geld_m_tu: FloatSeries,
    sonstig_eink_m_tu: FloatSeries,
    _zu_verst_ges_rente_tu: FloatSeries,
    unterhaltsvors_m_tu: FloatSeries,
    elterngeld_m_tu: FloatSeries,
) -> FloatSeries:
    """

    Parameters
    ----------
    arbeitsl_geld_m_tu
        See :func:`arbeitsl_geld_m_tu`.
    sonstig_eink_m_tu
        See :func:`sonstig_eink_m_tu`.
    _zu_verst_ges_rente_tu
        See :func:`_zu_verst_ges_rente_tu`.
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
        + _zu_verst_ges_rente_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )


def _anzahl_kinder_unter_11_per_tu(tu_id: IntSeries, alter: IntSeries) -> IntSeries:
    """

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


def wohngeld_eink_abzüge_bis_2015(
    bruttolohn_m: FloatSeries,
    arbeitende_kinder: IntSeries,
    behinderungsgrad: IntSeries,
    alleinerziehend: BoolSeries,
    kind: BoolSeries,
    _anzahl_kinder_unter_11_per_tu: IntSeries,
    wohngeld_params: dict,
):
    """

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
    _anzahl_kinder_unter_11_per_tu
        See :func:`_anzahl_kinder_unter_11_per_tu`.
    wohngeld_params
        See :ref:`wohngeld_params`.

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
            * _anzahl_kinder_unter_11_per_tu
            * wohngeld_params["freib_kinder"][12]
        )
    )

    return abzüge


def arbeitende_kinder(
    bruttolohn_m: FloatSeries, kindergeld_anspruch: BoolSeries
) -> IntSeries:
    """

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
    """

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
        See :ref:`wohngeld_params`.
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


def _wohngeld_eink(
    tu_id: IntSeries,
    haushaltsgröße: IntSeries,
    wohngeld_eink_abzüge: FloatSeries,
    _wohngeld_abzüge_tu: FloatSeries,
    _wohngeld_brutto_eink_tu: FloatSeries,
    _wohngeld_sonstiges_eink_tu: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_eink_abzüge
        See :func:`wohngeld_eink_abzüge`.
    _wohngeld_abzüge_tu
        See :func:`_wohngeld_abzüge_tu`.
    _wohngeld_brutto_eink_tu
        See :func:`_wohngeld_brutto_eink_tu`.
    _wohngeld_sonstiges_eink_tu
        See :func:`_wohngeld_sonstiges_eink_tu`.
    wohngeld_params
        See :ref:`wohngeld_params`.

    Returns
    -------

    """
    _wohngeld_eink_abzüge_tu = wohngeld_eink_abzüge.groupby(tu_id).sum()

    vorläufiges_eink = (1 - _wohngeld_abzüge_tu) * (
        _wohngeld_brutto_eink_tu
        + _wohngeld_sonstiges_eink_tu
        - _wohngeld_eink_abzüge_tu
    )

    unteres_eink = haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_eink"])

    return tu_id.replace(vorläufiges_eink).clip(lower=unteres_eink)


def _wohngeld_min_miete(
    haushaltsgröße: IntSeries, wohngeld_params: dict
) -> FloatSeries:
    """

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
    wohngeld_params
        See :ref:`wohngeld_params`.
    Returns
    -------

    """
    return haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_miete"])


def wohngeld_max_miete_bis_2008(
    mietstufe: IntSeries,
    immobilie_baujahr_hh: IntSeries,
    haushaltsgröße: IntSeries,
    hh_id: IntSeries,
    kaltmiete_m_hh: FloatSeries,
    tax_unit_share: FloatSeries,
    _wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
):
    """

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
    kaltmiete_m_hh
        See basic input variable :ref:`kaltmiete_m_hh <kaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.
    _wohngeld_min_miete
        See :func:`_wohngeld_min_miete`.
    wohngeld_params
        See :ref:`wohngeld_params`.

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
        np.clip(data, a_min=None, a_max=hh_id.replace(kaltmiete_m_hh)) * tax_unit_share
    ).clip(lower=_wohngeld_min_miete)

    return wg_miete


def wohngeld_max_miete_ab_2009(
    mietstufe: IntSeries,
    haushaltsgröße: IntSeries,
    hh_id: IntSeries,
    kaltmiete_m_hh: FloatSeries,
    tax_unit_share: FloatSeries,
    _wohngeld_min_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    haushaltsgröße
        See :func:`haushaltsgröße`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    kaltmiete_m_hh
        See basic input variable :ref:`kaltmiete_m_hh <kaltmiete_m_hh>`.
    tax_unit_share
        See :func:`tax_unit_share`.
    _wohngeld_min_miete
        See :func:`_wohngeld_min_miete`.
    wohngeld_params
        See :ref:`wohngeld_params`.

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
        np.clip(data, a_min=None, a_max=hh_id.replace(kaltmiete_m_hh)) * tax_unit_share
    ).clip(lower=_wohngeld_min_miete)

    return wg_miete


def wohngeld_basis(
    haushaltsgröße: IntSeries,
    _wohngeld_eink: FloatSeries,
    wohngeld_max_miete: FloatSeries,
    wohngeld_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    haushaltsgröße
        See :func:`haushaltsgröße`.
    _wohngeld_eink
        See :func:`_wohngeld_eink`.
    wohngeld_max_miete
        See :func:`wohngeld_max_miete`.
    wohngeld_params
        See :ref:`wohngeld_params`.

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

    wg_amount = (
        wohngeld_params["faktor_berechnungsformel"]
        * (
            wohngeld_max_miete
            - (
                (
                    koeffizienten_a
                    + (koeffizienten_b * wohngeld_max_miete)
                    + (koeffizienten_c * _wohngeld_eink)
                )
                * _wohngeld_eink
            )
        )
    ).clip(lower=0)

    # If more than 12 persons, there is a lump-sum on top. You may however not get more
    # than the corrected rent `wohngeld_max_miete`.
    wg_amount_more_than_12 = (
        wg_amount.clip(lower=0)
        + wohngeld_params["bonus_12_mehr"] * (haushaltsgröße - 12)
    ).clip(upper=wohngeld_max_miete)

    wg_amount = wg_amount.where(haushaltsgröße <= 12, wg_amount_more_than_12)

    return wg_amount


def tax_unit_share(tu_id: IntSeries, haushaltsgröße: IntSeries) -> FloatSeries:
    """

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
    """

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
