"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np


def wohngeld_basis_hh(
    hh_id, wohngeld_basis, tu_vorstand,
):
    """Compute "Wohngeld" or housing benefits.

    Social benefit for recipients with income above basic social assistance Computation
    is very complicated, accounts for household size, income, actual rent and differs on
    the municipality level ('Mietstufe' (1,...,6)).

    We usually don't have information on the last item. Therefore we assume 'Mietstufe'
    3, corresponding to an average level, but other Mietstufen can be specified in
    `household`.

    Benefit amount depends on parameters `wohngeld_max_miete` (rent) and
    `_wohngeld_eink` (income) (§19 WoGG).

    """
    return (wohngeld_basis * tu_vorstand).groupby(hh_id).sum().round(2)


def _zu_verst_ges_rente_tu(_zu_verst_ges_rente, tu_id):
    return _zu_verst_ges_rente.groupby(tu_id).sum()


def _wohngeld_abzüge_tu(
    eink_st_tu, rentenv_beitr_m_tu, ges_krankenv_beitr_m_tu, wohngeld_params
):
    abzug_stufen = (
        (eink_st_tu > 0) * 1 + (rentenv_beitr_m_tu > 0) + (ges_krankenv_beitr_m_tu > 0)
    )
    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def _zu_verst_ges_rente(_ertragsanteil, ges_rente_m):
    return _ertragsanteil * ges_rente_m


def _wohngeld_brutto_eink_tu(
    brutto_eink_1_tu, brutto_eink_4_tu, brutto_eink_5_tu, brutto_eink_6_tu,
):
    return (
        brutto_eink_1_tu + brutto_eink_4_tu + brutto_eink_5_tu + brutto_eink_6_tu
    ) / 12


def _wohngeld_sonstiges_eink_tu(
    arbeitsl_geld_m_tu,
    sonstig_eink_m_tu,
    _zu_verst_ges_rente_tu,
    unterhaltsvors_m_tu,
    elterngeld_m_tu,
):
    return (
        arbeitsl_geld_m_tu
        + sonstig_eink_m_tu
        + _zu_verst_ges_rente_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )


def _anzahl_kinder_unter_11_per_tu(tu_id, alter):
    return (alter < 11).groupby(tu_id).transform("sum")


def wohngeld_eink_abzüge_bis_2015(
    bruttolohn_m,
    arbeitende_kinder,
    behinderungsgrad,
    alleinerziehend,
    kind,
    _anzahl_kinder_unter_11_per_tu,
    wohngeld_params,
):
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


def arbeitende_kinder(bruttolohn_m, kindergeld_anspruch):
    return (bruttolohn_m > 0) & kindergeld_anspruch


def wohngeld_eink_abzüge_ab_2016(
    bruttolohn_m,
    kindergeld_anspruch,
    behinderungsgrad,
    alleinerziehend,
    kind,
    wohngeld_params,
):
    workingchild = (bruttolohn_m > 0) & kindergeld_anspruch

    abzüge = (
        (behinderungsgrad > 0) * wohngeld_params["freib_behinderung"]
        + workingchild
        * bruttolohn_m.clip(lower=0, upper=wohngeld_params["freib_kinder"][24])
        + alleinerziehend * wohngeld_params["freib_kinder"][12] * ~kind
    )

    return abzüge


def _wohngeld_eink(
    tu_id,
    haushaltsgröße,
    wohngeld_eink_abzüge,
    _wohngeld_abzüge_tu,
    _wohngeld_brutto_eink_tu,
    _wohngeld_sonstiges_eink_tu,
    wohngeld_params,
):
    _wohngeld_eink_abzüge_tu = wohngeld_eink_abzüge.groupby(tu_id).sum()

    vorläufiges_eink = (1 - _wohngeld_abzüge_tu) * (
        _wohngeld_brutto_eink_tu
        + _wohngeld_sonstiges_eink_tu
        - _wohngeld_eink_abzüge_tu
    )

    unteres_eink = haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_eink"])

    return tu_id.replace(vorläufiges_eink).clip(lower=unteres_eink)


def _wohngeld_min_miete(haushaltsgröße, wohngeld_params):
    return haushaltsgröße.clip(upper=12).replace(wohngeld_params["min_miete"])


def wohngeld_max_miete_bis_2008(
    mietstufe,
    immobilie_baujahr,
    haushaltsgröße,
    kaltmiete_m,
    tax_unit_share,
    _wohngeld_min_miete,
    wohngeld_params,
):
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

    wg_miete = (np.clip(data, a_min=None, a_max=kaltmiete_m) * tax_unit_share).clip(
        lower=_wohngeld_min_miete
    )
    # wg["wgheiz"] = household["heizkost"] * tax_unit_share

    return wg_miete


def wohngeld_max_miete_ab_2009(
    mietstufe,
    haushaltsgröße,
    kaltmiete_m,
    tax_unit_share,
    _wohngeld_min_miete,
    wohngeld_params,
):
    data = [
        wohngeld_params["max_miete"][hh_größe][ms]
        if hh_größe <= 5
        else wohngeld_params["max_miete"][5][ms]
        + wohngeld_params["max_miete"]["5plus"][ms] * (hh_größe - 5)
        for hh_größe, ms in zip(haushaltsgröße, mietstufe)
    ]

    wg_miete = (np.clip(data, a_min=None, a_max=kaltmiete_m) * tax_unit_share).clip(
        lower=_wohngeld_min_miete
    )
    # wg["wgheiz"] = household["heizkost"] * tax_unit_share

    return wg_miete


def wohngeld_basis(haushaltsgröße, _wohngeld_eink, wohngeld_max_miete, wohngeld_params):
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


def tax_unit_share(tu_id, haushaltsgröße):
    return tu_id.groupby(tu_id).transform("count") / haushaltsgröße


def sonstig_eink_m_tu(sonstig_eink_m, tu_id):
    return sonstig_eink_m.groupby(tu_id).sum()
