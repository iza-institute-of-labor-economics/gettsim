"""This module provides functions to compute residence allowance (Wohngeld).

    Wohngeld has priority over ALG2 if the recipients can cover their needs according to
    SGB II when receiving Wohngeld. The priority check follows the following logic:

    1. Calculate Wohngeld on the Bedarfsgemeinschaft level.
    2. Check whether the Bedarfsgemeinschaft can cover its own needs (Regelbedarf) with
       Wohngeld. If not, the Bedarfsgemeinschaft is eligible for ALG2.
    3. Compute Wohngeld again for all individuals in the household that can cover their
       own needs with Wohngeld. This is the final Wohngeld amount that is paid out to
       the wohngeldrechtlicher Teilhaushalt.

    Note: Because Wohngeld is nonlinear in the number of people in the
    wohngeldrechtlicher Teilhaushalt, there may be some individuals that pass the
    priority check, but cannot cover their needs with the Wohngeld calculated in point
    3. In this sense, this implementation is an approximation of the actual Wohngeld.
"""

from _gettsim.config import numpy_or_jax as np
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info

aggregate_by_p_id_wohngeld = {
    "_wohngeld_eink_freib_alleinerz_bonus": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "kind_bis_10_mit_kindergeld",
        "aggr": "sum",
    },
}


def wohngeld_m_wthh(
    _wohngeld_nach_vermög_check_m_wthh: float,
    erwachsene_alle_rentner_hh: bool,
    wohngeld_und_kiz_günstiger_als_sgb_ii: bool,
) -> float:
    """Housing benefit after wealth and priority checks.

    Parameters
    ----------
    _wohngeld_nach_vermög_check_m_wthh
        See :func:`_wohngeld_nach_vermög_check_m_wthh`.
    erwachsene_alle_rentner_hh
        See :func:`erwachsene_alle_rentner_hh <erwachsene_alle_rentner_hh>`.
    wohngeld_und_kiz_günstiger_als_sgb_ii
        See basic input variable :ref:`wohngeld_und_kiz_günstiger_als_sgb_ii
        <wohngeld_und_kiz_günstiger_als_sgb_ii>`.

    Returns
    -------

    """
    # TODO (@MImmesberger): This implementation may be only an approximation of the
    # actual rules for individuals that are on the margin of the priority check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/752

    # TODO (@MImmesberger): No interaction between Wohngeld/ALG2 and Grundsicherung im
    # Alter (SGB XII) is implemented yet. We assume for now that households with only
    # retirees are eligible for Grundsicherung im Alter but not for ALG2/Wohngeld. All
    # other households are not eligible for SGB XII, but SGB II / Wohngeld. Once this is
    # resolved, remove the `erwachsene_alle_rentner_hh` condition.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/703

    if not erwachsene_alle_rentner_hh and wohngeld_und_kiz_günstiger_als_sgb_ii:
        out = _wohngeld_nach_vermög_check_m_wthh
    else:
        out = 0.0

    return out


def wohngeld_abzüge_st_sozialv_m(
    eink_st_y_sn: float,
    ges_rentenv_beitr_arbeitnehmer_m: float,
    ges_krankenv_beitr_arbeitnehmer_m: float,
    kind: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions on the individual level.

    Note that eink_st_y_sn is used as an approximation for taxes on income (as mentioned
    in § 16 WoGG Satz 1 Nr. 1).

    Parameters
    ----------
    eink_st_y_sn
        See :func:`eink_st_y_sn`.
    ges_rentenv_beitr_arbeitnehmer_m
        See :func:`ges_rentenv_beitr_arbeitnehmer_m`.
    ges_krankenv_beitr_arbeitnehmer_m
        See :func:`ges_krankenv_beitr_arbeitnehmer_m`.
    kind
        See basic input variable :ref:`kind <kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (eink_st_y_sn > 0)
        + (ges_rentenv_beitr_arbeitnehmer_m > 0)
        + (ges_krankenv_beitr_arbeitnehmer_m > 0)
    )
    if kind:
        out = 0.0
    else:
        out = wohngeld_params["abzug_stufen"][abzug_stufen]
    return out


@policy_info(end_date="2006-12-31", name_in_dag="wohngeld_eink_vor_freib_m")
def wohngeld_eink_vor_freib_m_ohne_elterngeld(  # noqa: PLR0913
    eink_selbst_y: float,
    eink_abhängig_beschäftigt_y: float,
    kapitaleink_brutto_y: float,
    eink_vermietung_y: float,
    arbeitsl_geld_m: float,
    sonstig_eink_m: float,
    eink_rente_zu_verst_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    wohngeld_abzüge_st_sozialv_m: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    Parameters
    ----------
    eink_selbst_y
        See :func:`_eink_selbst`.
    eink_abhängig_beschäftigt_y
        See :func:`eink_abhängig_beschäftigt_y`.
    kapitaleink_brutto_y
        See :func:`kapitaleink_brutto_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    eink_rente_zu_verst_m
        See :func:`eink_rente_zu_verst_m`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    wohngeld_abzüge_st_sozialv_m
        See :func:`wohngeld_abzüge_st_sozialv_m`.

    Returns
    -------

    """
    einkommen = (
        eink_selbst_y
        + eink_abhängig_beschäftigt_y
        + kapitaleink_brutto_y
        + eink_vermietung_y
    ) / 12

    transfers = (
        arbeitsl_geld_m
        + eink_rente_zu_verst_m
        + kind_unterh_erhalt_m
        + unterhaltsvors_m
    )

    eink_ind = einkommen + transfers + sonstig_eink_m
    out = (1 - wohngeld_abzüge_st_sozialv_m) * eink_ind
    return out


@policy_info(start_date="2007-01-01", name_in_dag="wohngeld_eink_vor_freib_m")
def wohngeld_eink_vor_freib_m_mit_elterngeld(  # noqa: PLR0913
    eink_selbst_y: float,
    eink_abhängig_beschäftigt_y: float,
    kapitaleink_brutto_y: float,
    eink_vermietung_y: float,
    arbeitsl_geld_m: float,
    sonstig_eink_m: float,
    eink_rente_zu_verst_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    elterngeld_anr_m: float,
    wohngeld_abzüge_st_sozialv_m: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    Parameters
    ----------
    eink_selbst_y
        See :func:`_eink_selbst`.
    eink_abhängig_beschäftigt_y
        See :func:`eink_abhängig_beschäftigt_y`.
    kapitaleink_brutto_y
        See :func:`kapitaleink_brutto_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    eink_rente_zu_verst_m
        See :func:`eink_rente_zu_verst_m`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    elterngeld_anr_m
        See :func:`elterngeld_anr_m`.
    wohngeld_abzüge_st_sozialv_m
        See :func:`wohngeld_abzüge_st_sozialv_m`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Find out whether kind_unterh_erhalt_m and unterhaltsvors_m
    # are counted as income for Wohngeld income check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/357
    einkommen = (
        eink_selbst_y
        + eink_abhängig_beschäftigt_y
        + kapitaleink_brutto_y
        + eink_vermietung_y
    ) / 12

    transfers = (
        arbeitsl_geld_m
        + eink_rente_zu_verst_m
        + kind_unterh_erhalt_m
        + unterhaltsvors_m
        + elterngeld_anr_m
    )

    eink_ind = einkommen + transfers + sonstig_eink_m
    out = (1 - wohngeld_abzüge_st_sozialv_m) * eink_ind
    return out


def wohngeld_arbeitendes_kind(bruttolohn_m: float, kindergeld_anspruch: bool) -> bool:
    """Check if children are working.

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


@policy_info(end_date="2015-12-31", name_in_dag="wohngeld_eink_freib_m")
def wohngeld_eink_freib_m_bis_2015(  # noqa: PLR0913
    bruttolohn_m: float,
    wohngeld_arbeitendes_kind: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    kind: bool,
    _wohngeld_eink_freib_alleinerz_bonus: int,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions for one individual until 2015.

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
    _wohngeld_eink_freib_alleinerz_bonus
        See :func:`_wohngeld_eink_freib_alleinerz_bonus`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    freib_behinderung_m = piecewise_polynomial(
        behinderungsgrad,
        thresholds=[*list(wohngeld_params["freib_behinderung"]), np.inf],
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
            _wohngeld_eink_freib_alleinerz_bonus
            * wohngeld_params["freib_kinder_m"]["alleinerz"]
        )
    else:
        freib_kinder_m = 0.0
    return freib_behinderung_m + freib_kinder_m


@policy_info(start_date="2016-01-01", name_in_dag="wohngeld_eink_freib_m")
def wohngeld_eink_freib_m_ab_2016(
    bruttolohn_m: float,
    wohngeld_arbeitendes_kind: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtracting for one individual since 2016.

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

    if wohngeld_arbeitendes_kind:
        freib_kinder_m = min(
            bruttolohn_m, wohngeld_params["freib_kinder_m"]["arbeitendes_kind"]
        )
    elif alleinerz:
        freib_kinder_m = wohngeld_params["freib_kinder_m"]["alleinerz"]
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def wohngeld_eink_m_wthh(
    anz_personen_wthh: int,
    wohngeld_eink_freib_m_wthh: float,
    wohngeld_eink_vor_freib_m_wthh: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    wohngeld_eink_freib_m_wthh
        See :func:`wohngeld_eink_freib_m_wthh`.
    wohngeld_eink_vor_freib_m_wthh
        See :func:`wohngeld_eink_vor_freib_m_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_einkommen_formel(
        anz_personen=anz_personen_wthh,
        einkommen_freibetrag=wohngeld_eink_freib_m_wthh,
        einkommen_vor_freibetrag=wohngeld_eink_vor_freib_m_wthh,
        params=wohngeld_params,
    )


def wohngeld_eink_m_bg(
    anz_personen_bg: int,
    wohngeld_eink_freib_m_bg: float,
    wohngeld_eink_vor_freib_m_bg: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_eink_freib_m_bg
        See :func:`wohngeld_eink_freib_m_bg`.
    wohngeld_eink_vor_freib_m_bg
        See :func:`wohngeld_eink_vor_freib_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_einkommen_formel(
        anz_personen=anz_personen_bg,
        einkommen_freibetrag=wohngeld_eink_freib_m_bg,
        einkommen_vor_freibetrag=wohngeld_eink_vor_freib_m_bg,
        params=wohngeld_params,
    )


def wohngeld_min_miete_m_hh(anz_personen_hh: int, wohngeld_params: dict) -> float:
    """Minimum rent considered in Wohngeld calculation.

    Parameters
    ----------
    anz_personen_hh
        See :func:`anz_personen_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    out = wohngeld_params["min_miete"][
        min(anz_personen_hh, max(wohngeld_params["min_miete"]))
    ]
    return float(out)


def wohngeld_miete_m_wthh(
    wohngeld_miete_m_hh: float,
    anz_personen_wthh: int,
    anz_personen_hh: int,
) -> float:
    """Rent considered in housing benefit calculation on wohngeldrechtlicher
    Teilhaushalt level.

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    wohngeld_miete_m_hh
        See :func:`wohngeld_miete_m_hh`.
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    anz_personen_hh
        See :func:`anz_personen_hh`.

    Returns
    -------

    """
    return wohngeld_miete_m_hh * (anz_personen_wthh / anz_personen_hh)


def wohngeld_miete_m_bg(
    wohngeld_miete_m_hh: float,
    anz_personen_bg: int,
    anz_personen_hh: int,
) -> float:
    """Rent considered in housing benefit calculation on BG level.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    wohngeld_miete_m_hh
        See :func:`wohngeld_miete_m_hh`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    anz_personen_hh
        See :func:`anz_personen_hh`.

    Returns
    -------

    """
    return wohngeld_miete_m_hh * (anz_personen_bg / anz_personen_hh)


@policy_info(end_date="2008-12-31", name_in_dag="wohngeld_miete_m_hh")
def wohngeld_miete_bis_2008_m_hh(  # noqa: PLR0913
    mietstufe: int,
    immobilie_baujahr_hh: int,
    anz_personen_hh: int,
    bruttokaltmiete_m_hh: float,
    wohngeld_min_miete_m_hh: float,
    wohngeld_params: dict,
) -> float:
    """Rent considered in housing benefit calculation on household level until 2008.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    immobilie_baujahr_hh
        See basic input variable :ref:`immobilie_baujahr_hh <immobilie_baujahr_hh>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    bruttokaltmiete_m_hh
        See :func:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    wohngeld_min_miete_m_hh
        See :func:`wohngeld_min_miete_m_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    max_berücks_personen = wohngeld_params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen_hh, max_berücks_personen)

    # Get yearly cutoff in params which is closest and above the construction year
    # of the property. We assume that the same cutoffs exist for each household
    # size.
    params_max_miete = wohngeld_params["max_miete"]
    selected_bin_index = np.searchsorted(
        sorted(params_max_miete[1]), immobilie_baujahr_hh, side="left"
    )

    constr_year = list(params_max_miete[1])[selected_bin_index]

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen_hh <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen_hh][constr_year][mietstufe]
    else:
        max_miete_m = params_max_miete[max_definierte_hh_größe][constr_year][
            mietstufe
        ] + params_max_miete["jede_weitere_person"][constr_year][mietstufe] * (
            berücks_personen - max_definierte_hh_größe
        )

    out = min(bruttokaltmiete_m_hh, max_miete_m)
    out = max(out, wohngeld_min_miete_m_hh)

    return out


@policy_info(start_date="2009-01-01", name_in_dag="wohngeld_miete_m_hh")
def wohngeld_miete_ab_2009_m_hh(  # noqa: PLR0912 (see #516)
    mietstufe: int,
    anz_personen_hh: int,
    bruttokaltmiete_m_hh: float,
    wohngeld_min_miete_m_hh: float,
    wohngeld_params: dict,
) -> float:
    """Rent considered in housing benefit since 2009.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    anz_personen_hh
        See :func:`anz_personen_hh`.
    bruttokaltmiete_m_hh
        See :func:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    wohngeld_min_miete_m_hh
        See :func:`wohngeld_min_miete_m_hh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    params_max_miete = wohngeld_params["max_miete"]

    max_berücks_personen = wohngeld_params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]
    berücks_personen = min(anz_personen_hh, max_berücks_personen)

    # Calc maximal considered rent
    max_definierte_hh_größe = max(i for i in params_max_miete if isinstance(i, int))
    if anz_personen_hh <= max_definierte_hh_größe:
        max_miete_m = params_max_miete[anz_personen_hh][mietstufe]
    else:
        max_miete_m = (
            params_max_miete[max_definierte_hh_größe][mietstufe]
            + (berücks_personen - max_definierte_hh_größe)
            * params_max_miete["jede_weitere_person"][mietstufe]
        )

    # Calc heating allowance. Until 2020, heating allowance was not
    # introduced yet. For this time frame, the respective parameter is
    # not part of wohngeld_params and heating allowance is set to 0.
    # TODO(@MImmesberger): Apply policy_info decorator.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/711
    if "heizkostenentlastung_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i for i in wohngeld_params["heizkostenentlastung_m"] if isinstance(i, int)
        )
    if "heizkostenentlastung_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            heating_allowance_m = wohngeld_params["heizkostenentlastung_m"][
                anz_personen_hh
            ]
        else:
            heating_allowance_m = wohngeld_params["heizkostenentlastung_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                wohngeld_params["heizkostenentlastung_m"]["jede_weitere_person"]
            )
    else:
        heating_allowance_m = 0

    # Calc heating cost component. Until 2022, heating cost component was not
    # introduced yet. For this time frame, the respective parameter is not part
    # of params and heating cost component is set to 0.
    if "dauerhafte_heizkostenkomponente_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i
            for i in wohngeld_params["dauerhafte_heizkostenkomponente_m"]
            if isinstance(i, int)
        )
    if "dauerhafte_heizkostenkomponente_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            heating_component_m = wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                anz_personen_hh
            ]
        else:
            heating_component_m = wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                wohngeld_params["dauerhafte_heizkostenkomponente_m"][
                    "jede_weitere_person"
                ]
            )
    else:
        heating_component_m = 0

    # Calc climate component. Until 2022, climate component was not
    # introduced yet. For this time frame, the respective parameter is not
    # part of params and climate component is set to 0.
    if "klimakomponente_m" in wohngeld_params:
        max_def_hh_größe_heating = max(
            i for i in wohngeld_params["klimakomponente_m"] if isinstance(i, int)
        )
    if "klimakomponente_m" in wohngeld_params:
        if anz_personen_hh <= max_def_hh_größe_heating:
            climate_component_m = wohngeld_params["klimakomponente_m"][anz_personen_hh]
        else:
            climate_component_m = wohngeld_params["klimakomponente_m"][
                max_def_hh_größe_heating
            ] + (berücks_personen - max_def_hh_größe_heating) * (
                wohngeld_params["klimakomponente_m"]["jede_weitere_person"]
            )
    else:
        climate_component_m = 0

    out = min(bruttokaltmiete_m_hh, max_miete_m + climate_component_m)
    out = max(out, wohngeld_min_miete_m_hh) + heating_allowance_m + heating_component_m

    return out


def _wohngeld_nach_vermög_check_m_wthh(
    wohngeld_vor_vermög_check_m_wthh: float,
    vermögen_bedürft_wthh: float,
    anz_personen_wthh: int,
    wohngeld_params: dict,
) -> float:
    """Preliminary housing benefit after wealth check.

    This target is used for the actual Wohngeld calculation of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    wohngeld_vor_vermög_check_m_wthh
        See :func:`wohngeld_vor_vermög_check_m_wthh`.
    vermögen_bedürft_wthh
        See :func:`vermögen_bedürft_wthh <vermögen_bedürft_wthh>`.
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return _wohngeld_nach_vermög_check_formel(
        basisbetrag_m=wohngeld_vor_vermög_check_m_wthh,
        vermögen=vermögen_bedürft_wthh,
        anz_personen=anz_personen_wthh,
        params=wohngeld_params,
    )


def wohngeld_nach_vermög_check_m_bg(
    wohngeld_vor_vermög_check_m_bg: float,
    vermögen_bedürft_bg: float,
    anz_personen_bg: int,
    wohngeld_params: dict,
) -> float:
    """Preliminary housing benefit after wealth check.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag.

    Parameters
    ----------
    wohngeld_vor_vermög_check_m_bg
        See :func:`wohngeld_vor_vermög_check_m_bg`.
    vermögen_bedürft_bg
        See :func:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return _wohngeld_nach_vermög_check_formel(
        basisbetrag_m=wohngeld_vor_vermög_check_m_bg,
        vermögen=vermögen_bedürft_bg,
        anz_personen=anz_personen_bg,
        params=wohngeld_params,
    )


@policy_info(params_key_for_rounding="wohngeld")
def wohngeld_vor_vermög_check_m_wthh(
    anz_personen_wthh: int,
    wohngeld_eink_m_wthh: float,
    wohngeld_miete_m_wthh: float,
    wohngeld_params: dict,
) -> float:
    """Housing benefit on wohngeldrechtlicher Teilhaushalt level without wealth or
    priority checks.

    This target is used for the actual Wohngeld calculation of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    wohngeld_eink_m_wthh
        See :func:`wohngeld_eink_m_wthh`.
    wohngeld_miete_m_wthh
        See :func:`wohngeld_miete_m_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_basisformel(
        anz_personen=anz_personen_wthh,
        einkommen_m=wohngeld_eink_m_wthh,
        miete_m=wohngeld_miete_m_wthh,
        params=wohngeld_params,
    )


@policy_info(params_key_for_rounding="wohngeld")
def wohngeld_vor_vermög_check_m_bg(
    anz_personen_bg: int,
    wohngeld_eink_m_bg: float,
    wohngeld_miete_m_bg: float,
    wohngeld_params: dict,
):
    """Housing benefit on Bedarfsgemeinschaft level without wealth or priority checks.

    This target is used to do the priority check against ALG2 and Kinderzuschlag.
    Wohngeld has priority over the two transfers if the Bedarfsgemeinschaft can cover
    their basic needs (Regelbedarf in SGB II sense) with it.

    Parameters
    ----------
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_eink_m_bg
        See :func:`wohngeld_eink_m_bg`.
    wohngeld_miete_m_bg
        See :func:`wohngeld_miete_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_basisformel(
        anz_personen=anz_personen_bg,
        einkommen_m=wohngeld_eink_m_bg,
        miete_m=wohngeld_miete_m_bg,
        params=wohngeld_params,
    )


def _wohngeld_basisformel(
    anz_personen: int,
    einkommen_m: float,
    miete_m: float,
    params: dict,
) -> float:
    """Basic formula for housing benefit calculation.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    anz_personen
        Number of people Wohngeld is being calculated for.
    einkommen_m
        Sum of income of people Wohngeld should be calculated for.
    miete_m
        Sum of rent.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    max_berücks_personen = params["bonus_sehr_große_haushalte"][
        "max_anz_personen_normale_berechnung"
    ]

    koeffizienten = params["koeffizienten_berechnungsformel"][
        min(anz_personen, max_berücks_personen)
    ]
    out = params["faktor_berechnungsformel"] * (
        miete_m
        - (
            (
                koeffizienten["a"]
                + (koeffizienten["b"] * miete_m)
                + (koeffizienten["c"] * einkommen_m)
            )
            * einkommen_m
        )
    )
    out = max(out, 0.0)

    if anz_personen > max_berücks_personen:
        # If more than 12 persons, there is a lump-sum on top.
        # The maximum is still capped at `miete_m`.
        out = min(
            out
            + params["bonus_sehr_große_haushalte"]["bonus_jede_weitere_person"]
            * (anz_personen - max_berücks_personen),
            miete_m,
        )

    return out


def _wohngeld_nach_vermög_check_formel(
    basisbetrag_m: float,
    vermögen: float,
    anz_personen: int,
    params: dict,
) -> float:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    The payment depends on the wealth of the household and the number of household
    members.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    basisbetrag_m
        Wohngeld as calculated via the basic formula (`_wohngeld_basisformel`).
    vermögen
        Relevant wealth of the Wohngeld recipients.
    anz_personen
        Number of people Wohngeld is being calculated for.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """

    if anz_personen == 1:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"]
    else:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"] + params[
            "vermögensfreibetrag_pers"
        ] * (anz_personen - 1)

    if vermögen <= vermögensfreibetrag:
        out = basisbetrag_m
    else:
        out = 0.0

    return out


def _wohngeld_einkommen_formel(
    anz_personen: int,
    einkommen_freibetrag: float,
    einkommen_vor_freibetrag: float,
    params: dict,
) -> float:
    """Calculate final income relevant for calculation of housing benefit on household
    level.
    Reference: § 13 WoGG

    Parameters
    ----------
    anz_personen
        Number of people Wohngeld is being calculated for.
    einkommen_freibetrag
        Income that is not considered for Wohngeld calculation.
    einkommen_vor_freibetrag
        Sum of income.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """
    eink_nach_abzug_m_hh = einkommen_vor_freibetrag - einkommen_freibetrag
    unteres_eink = params["min_eink"][min(anz_personen, max(params["min_eink"]))]

    out = max(eink_nach_abzug_m_hh, unteres_eink)
    return float(out)
