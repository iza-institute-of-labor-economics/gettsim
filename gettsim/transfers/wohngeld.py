"""This module provides functions to compute residence allowance (Wohngeld)."""
import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial


def wohngeld_m_hh(
    wohngeld_nach_vermög_check_m_hh: float,
    wohngeld_vorrang_hh: bool,
    wohngeld_kinderzuschl_vorrang_hh: bool,
    erwachsene_alle_rentner_hh: bool,
) -> float:
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
    if (
        (not wohngeld_vorrang_hh)
        and (not wohngeld_kinderzuschl_vorrang_hh)
        or erwachsene_alle_rentner_hh
    ):
        out = 0.0
    else:
        out = wohngeld_nach_vermög_check_m_hh

    return out


def wohngeld_abzüge_m_tu(
    eink_st_tu: float,
    ges_rentenv_beitr_m_tu: float,
    ges_krankenv_beitr_m_tu: float,
    wohngeld_params: dict,
) -> float:
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
    out = wohngeld_params["abzug_stufen"][abzug_stufen]
    return out


def wohngeld_eink_vor_abzug_m_tu(
    eink_selbst_tu: float,
    eink_abhängig_beschäftigt_tu: float,
    kapitaleink_brutto_tu: float,
    eink_vermietung_tu: float,
    arbeitsl_geld_m_tu: float,
    sonstig_eink_m_tu: float,
    eink_rente_zu_verst_m_tu: float,
    unterhaltsvors_m_tu: float,
    elterngeld_m_tu: float,
) -> float:
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
    einkommen_tu = (
        eink_selbst_tu
        + eink_abhängig_beschäftigt_tu
        + kapitaleink_brutto_tu
        + eink_vermietung_tu
    ) / 12

    transfers_tu = (
        arbeitsl_geld_m_tu
        + eink_rente_zu_verst_m_tu
        + unterhaltsvors_m_tu
        + elterngeld_m_tu
    )

    return einkommen_tu + transfers_tu + sonstig_eink_m_tu


def wohngeld_eink_abzüge_m_bis_2015(
    bruttolohn_m: float,
    wohngeld_arbeitendes_kind: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    kind: bool,
    anz_kinder_bis_10_tu: int,
    wohngeld_params: dict,
) -> float:
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

    elif alleinerz and (not kind):
        freib_kinder_m = (
            anz_kinder_bis_10_tu * wohngeld_params["freib_kinder_m"]["alleinerz"]
        )
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def wohngeld_arbeitendes_kind(bruttolohn_m: float, kindergeld_anspruch: bool) -> bool:
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
    out = (bruttolohn_m > 0) and kindergeld_anspruch
    return out


def wohngeld_eink_abzüge_m_ab_2016(
    bruttolohn_m: float,
    wohngeld_arbeitendes_kind: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    kind: bool,
    wohngeld_params: dict,
) -> float:
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
    elif alleinerz and (not kind):
        freib_kinder_m = wohngeld_params["freib_kinder_m"]["alleinerz"]
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def wohngeld_eink_m(
    haushaltsgröße_hh: int,
    wohngeld_eink_abzüge_m_tu: float,
    wohngeld_abzüge_m_tu: float,
    wohngeld_eink_vor_abzug_m_tu: float,
    wohngeld_params: dict,
) -> float:
    """Calculate final income relevant for calculation of housing benefit.

    Parameters
    ----------
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.
    wohngeld_eink_abzüge_m_tu
        See :func:`wohngeld_eink_abzüge_m_tu`.
    wohngeld_abzüge_m_tu
        See :func:`wohngeld_abzüge_m_tu`.
    wohngeld_eink_vor_abzug_m_tu
        See :func:`wohngeld_eink_vor_abzug_m_tu`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    vorläufiges_eink = (1 - wohngeld_abzüge_m_tu) * (
        wohngeld_eink_vor_abzug_m_tu - wohngeld_eink_abzüge_m_tu
    )

    unteres_eink = wohngeld_params["min_eink"][
        min(haushaltsgröße_hh, max(wohngeld_params["min_eink"]))
    ]

    out = max(vorläufiges_eink, unteres_eink)
    return out


def wohngeld_min_miete(haushaltsgröße_hh: int, wohngeld_params: dict) -> float:
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
    out = wohngeld_params["min_miete"][
        min(haushaltsgröße_hh, max(wohngeld_params["min_miete"]))
    ]
    return out


def wohngeld_miete_m_bis_2008(
    mietstufe: int,
    immobilie_baujahr_hh: int,
    haushaltsgröße_hh: int,
    bruttokaltmiete_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
    wohngeld_min_miete: float,
    wohngeld_params: dict,
) -> float:
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
    params_max_miete = wohngeld_params["max_miete"]
    selected_bin_index = np.searchsorted(
        sorted(params_max_miete[1]), immobilie_baujahr_hh, side="left"
    )

    constr_year = list(params_max_miete[1])[selected_bin_index]

    # Calc maximal considered rent
    # ToDo: Think about calculating max_definierte_hh_größe already in parameter
    # ToDo: pre-processing and add it to wohngeld_params
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if haushaltsgröße_hh <= max_definierte_hh_größe:
        max_miete = params_max_miete[haushaltsgröße_hh][constr_year][mietstufe]
    else:
        max_miete = params_max_miete[max_definierte_hh_größe][constr_year][
            mietstufe
        ] + params_max_miete["jede_weitere_person"][constr_year][mietstufe] * (
            haushaltsgröße_hh - max_definierte_hh_größe
        )

    out = min(bruttokaltmiete_m_hh, max_miete) * _anteil_personen_in_haushalt_tu
    out = max(out, wohngeld_min_miete)

    return out


def wohngeld_miete_m_ab_2009(
    mietstufe: int,
    haushaltsgröße_hh: int,
    bruttokaltmiete_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
    wohngeld_min_miete: float,
    wohngeld_params: dict,
) -> float:
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

    params_max_miete = wohngeld_params["max_miete"]

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if haushaltsgröße_hh <= max_definierte_hh_größe:
        max_miete = params_max_miete[haushaltsgröße_hh][mietstufe]
    else:
        max_miete = params_max_miete[max_definierte_hh_größe][
            mietstufe
        ] + params_max_miete["jede_weitere_person"][mietstufe] * (
            haushaltsgröße_hh - max_definierte_hh_größe
        )

    out = min(bruttokaltmiete_m_hh, max_miete) * _anteil_personen_in_haushalt_tu
    out = max(out, wohngeld_min_miete)

    return out


def wohngeld_miete_m_ab_2021(
    mietstufe: int,
    haushaltsgröße_hh: int,
    bruttokaltmiete_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
    wohngeld_min_miete: float,
    wohngeld_params: dict,
) -> float:
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
    params_max_miete = wohngeld_params["max_miete"]

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if haushaltsgröße_hh <= max_definierte_hh_größe:
        max_miete = params_max_miete[haushaltsgröße_hh][mietstufe]
    else:
        max_miete = (
            params_max_miete[max_definierte_hh_größe][mietstufe]
            + (haushaltsgröße_hh - max_definierte_hh_größe)
            * params_max_miete["jede_weitere_person"][mietstufe]
        )

    # Calc heating allowance
    max_def_hh_größe_heating = max(
        i for i in wohngeld_params["heizkosten_zuschuss"] if isinstance(i, int)
    )
    if haushaltsgröße_hh <= max_def_hh_größe_heating:
        heating_allowance = wohngeld_params["heizkosten_zuschuss"][haushaltsgröße_hh]
    else:
        heating_allowance = wohngeld_params["heizkosten_zuschuss"][
            max_def_hh_größe_heating
        ] + (haushaltsgröße_hh - max_def_hh_größe_heating) * (
            wohngeld_params["heizkosten_zuschuss"]["jede_weitere_person"]
        )

    out = (
        min(bruttokaltmiete_m_hh, max_miete + heating_allowance)
        * _anteil_personen_in_haushalt_tu
    )
    out = max(out, wohngeld_min_miete)

    return out


def wohngeld_vor_vermög_check_m_hh(
    haushaltsgröße_hh: int,
    wohngeld_eink_m: float,
    wohngeld_miete_m: float,
    wohngeld_params: dict,
) -> float:
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
    max_considered_hh_größe = max(wohngeld_params["min_eink"])

    koeffizienten = wohngeld_params["koeffizienten_berechnungsformel"][
        min(haushaltsgröße_hh, max_considered_hh_größe)
    ]
    out = wohngeld_params["faktor_berechnungsformel"] * (
        wohngeld_miete_m
        - (
            (
                koeffizienten["a"]
                + (koeffizienten["b"] * wohngeld_miete_m)
                + (koeffizienten["c"] * wohngeld_eink_m)
            )
            * wohngeld_eink_m
        )
    )
    out = max(out, 0.0)

    if haushaltsgröße_hh > max_considered_hh_größe:
        # If more than 12 persons, there is a lump-sum on top.
        # The maximum is still capped at `wohngeld_miete_m`.
        out += wohngeld_params["bonus_12_mehr"] * (
            haushaltsgröße_hh - max_considered_hh_größe
        )
        out = min(out, wohngeld_miete_m)

    return out


def _anteil_personen_in_haushalt_tu(
    tax_unit_größe_tu: int, haushaltsgröße_hh: int
) -> float:
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
