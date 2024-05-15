"""This module provides functions to compute residence allowance (Wohngeld)."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info
from _gettsim.transfers.wohngeld_formulas import (
    _wohngeld_basisformel,
    _wohngeld_einkommen_formula,
    _wohngeld_max_miete_formel_ab_2009,
    _wohngeld_max_miete_formel_bis_2009,
    _wohngeld_min_miete_formel,
    _wohngeld_nach_vermög_check_formel,
)

aggregate_by_p_id_wohngeld = {
    "_wohngeld_eink_freib_alleinerz_bonus": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "kind_bis_10_mit_kindergeld",
        "aggr": "sum",
    },
}


def wohngeld_m_wth(
    vermögen_bedürft_wth: float,
    anz_personen_wth: int,
    erwachsene_alle_rentner_hh: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit.

    Wohngeld has priority over ALG2 if the recipients can cover their needs according to
    SGB II when receiving Wohngeld. The priority check follows the following logic:

    1. Calculate Wohngeld on the Bedarfsgemeinschaft level.
    2. Check whether the Bedarfsgemeinschaft can cover its own needs (Regelbedarf) with
       Wohngeld. If not, the Bedarfsgemeinschaft is eligible for ALG2.
    3. Compute Wohngeld again for all individuals in the household that can cover their
       own needs with Wohngeld. This is the final Wohngeld amount that is paid out to
       the wohngeldrechtlicher Teilhaushalt.

    Note: Because Wohngeld is nonlinear in the number of people in the
    wohngeldrechtlicher Teilhaushalt, there might be some individuals that pass the
    priority check, but cannot cover their needs with the Wohngeld calculated in point
    3. In this sense, this implementation is an approximation of the actual Wohngeld.

    Parameters
    ----------
    vermögen_bedürft_wth
        See :func:`vermögen_bedürft_wth`.
    anz_personen_wth
        See :func:`anz_personen_wth`.
    erwachsene_alle_rentner_hh
        See basic input variable :ref:`erwachsene_alle_rentner_hh
        <erwachsene_alle_rentner_hh>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    # TODO (@MImmesberger): Document approximation.
    # TODO (@MImmesberger): Remove erwachsene_alle_rentner_hh condition once households
    # can get both Grundsicherung im Alter and ALG2/Wohngeld.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/696

    if not erwachsene_alle_rentner_hh:
        out = _wohngeld_nach_vermög_check_formel(
            wohngeld_basisbetrag=wohngeld_vor_vermög_check_m_wth,
            vermögen=vermögen_bedürft_wth,
            anz_personen=anz_personen_wth,
            wohngeld_params=wohngeld_params,
        )
    else:
        out = 0.0

    return out


def wohngeld_abzüge_st_sozialv_m(
    eink_st_y_sn: float,
    ges_rentenv_beitr_m: float,
    ges_krankenv_beitr_m: float,
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
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    kind
        See basic input variable :ref:`kind <kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (eink_st_y_sn > 0) + (ges_rentenv_beitr_m > 0) + (ges_krankenv_beitr_m > 0)
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


def wohngeld_eink_m_wth(
    anz_personen_wth: int,
    wohngeld_eink_freib_m_wth: float,
    wohngeld_eink_vor_freib_m_wth: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    anz_personen_wth
        See :func:`anz_personen_wth`.
    wohngeld_eink_freib_m_wth
        See :func:`wohngeld_eink_freib_m_wth`.
    wohngeld_eink_vor_freib_m_wth
        See :func:`wohngeld_eink_vor_freib_m_wth`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_einkommen_formula(
        anz_personen=anz_personen_wth,
        einkommen_freibetrag=wohngeld_eink_freib_m_wth,
        einkommen_vor_freibetrag=wohngeld_eink_vor_freib_m_wth,
        wohngeld_params=wohngeld_params,
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
    return _wohngeld_einkommen_formula(
        anz_personen=anz_personen_bg,
        einkommen_freibetrag=wohngeld_eink_freib_m_bg,
        einkommen_vor_freibetrag=wohngeld_eink_vor_freib_m_bg,
        wohngeld_params=wohngeld_params,
    )


def wohngeld_min_miete_m_wth(anz_personen_wth: int, wohngeld_params: dict) -> float:
    """Minimum rent considered in Wohngeld calculation.

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    anz_personen_wth
        See :func:`anz_personen_wth`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    return _wohngeld_min_miete_formel(
        anz_personen=anz_personen_wth, wohngeld_params=wohngeld_params
    )


def wohngeld_min_miete_m_bg(anz_personen_bg: int, wohngeld_params: dict) -> float:
    """Minimum rent considered in Wohngeld calculation.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    return _wohngeld_min_miete_formel(
        anz_personen=anz_personen_bg, wohngeld_params=wohngeld_params
    )


@policy_info(end_date="2008-12-31", name_in_dag="wohngeld_miete_m_wth")
def wohngeld_miete_bis_2008_m_wth(  # noqa: PLR0913
    mietstufe: int,
    immobilie_baujahr_wth: int,
    anz_personen_wth: int,
    bruttokaltmiete_m_wth: float,
    wohngeld_min_miete_m_wth: float,
    wohngeld_params: dict,
) -> float:
    """Maximal rent subject housing benefit calculation on household level until 2008.

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    immobilie_baujahr_wth
        See basic input variable :ref:`immobilie_baujahr_wth <immobilie_baujahr_wth>`.
    anz_personen_wth
        See :func:`anz_personen_wth`.
    bruttokaltmiete_m_wth
        See basic input variable :ref:`bruttokaltmiete_m_wth <bruttokaltmiete_m_wth>`.
    wohngeld_min_miete_m_wth
        See :func:`wohngeld_min_miete_m_wth`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_max_miete_formel_bis_2009(
        mietstufe=mietstufe,
        immobilie_baujahr=immobilie_baujahr_wth,
        anz_personen=anz_personen_wth,
        bruttokaltmiete_m=bruttokaltmiete_m_wth,
        wohngeld_min_miete_m=wohngeld_min_miete_m_wth,
        wohngeld_params=wohngeld_params,
    )


@policy_info(end_date="2008-12-31", name_in_dag="wohngeld_miete_m_bg")
def wohngeld_miete_bis_2008_m_bg(  # noqa: PLR0913
    mietstufe: int,
    immobilie_baujahr_bg: int,
    anz_personen_bg: int,
    bruttokaltmiete_m_bg: float,
    wohngeld_min_miete_m_bg: float,
    wohngeld_params: dict,
) -> float:
    """Maximal rent subject housing benefit calculation on household level until 2008.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    immobilie_baujahr_bg
        See basic input variable :ref:`immobilie_baujahr_bg <immobilie_baujahr_bg>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    bruttokaltmiete_m_bg
        See basic input variable :ref:`bruttokaltmiete_m_bg <bruttokaltmiete_m_bg>`.
    wohngeld_min_miete_m_bg
        See :func:`wohngeld_min_miete_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_max_miete_formel_bis_2009(
        mietstufe=mietstufe,
        immobilie_baujahr=immobilie_baujahr_bg,
        anz_personen=anz_personen_bg,
        bruttokaltmiete_m=bruttokaltmiete_m_bg,
        wohngeld_min_miete_m=wohngeld_min_miete_m_bg,
        wohngeld_params=wohngeld_params,
    )


@policy_info(start_date="2009-01-01", name_in_dag="wohngeld_miete_m_wth")
def wohngeld_miete_ab_2009_m_wth(
    mietstufe: int,
    anz_personen_wth: int,
    bruttokaltmiete_m_wth: float,
    wohngeld_min_miete_m_wth: float,
    wohngeld_params: dict,
) -> float:
    """Maximum rent considered in housing benefit since 2009.

    This target is used to calculate the actual Wohngeld of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    anz_personen_wth
        See :func:`anz_personen_wth`.
    bruttokaltmiete_m_wth
        See basic input variable :ref:`bruttokaltmiete_m_wth <bruttokaltmiete_m_wth>`.
    wohngeld_min_miete_m_wth
        See :func:`wohngeld_min_miete_m_wth`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_max_miete_formel_ab_2009(
        mietstufe=mietstufe,
        anz_personen_wth=anz_personen_wth,
        bruttokaltmiete_m_wth=bruttokaltmiete_m_wth,
        wohngeld_min_miete_m_wth=wohngeld_min_miete_m_wth,
        wohngeld_params=wohngeld_params,
    )


@policy_info(start_date="2009-01-01", name_in_dag="wohngeld_miete_m_bg")
def wohngeld_miete_ab_2009_m_bg(
    mietstufe: int,
    anz_personen_bg: int,
    bruttokaltmiete_m_bg: float,
    wohngeld_min_miete_m_bg: float,
    wohngeld_params: dict,
) -> float:
    """Maximum rent considered in housing benefit since 2009.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    mietstufe
        See basic input variable :ref:`mietstufe <mietstufe>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    bruttokaltmiete_m_bg
        See basic input variable :ref:`bruttokaltmiete_m_bg <bruttokaltmiete_m_bg>`.
    wohngeld_min_miete_m_bg
        See :func:`wohngeld_min_miete_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_max_miete_formel_ab_2009(
        mietstufe=mietstufe,
        anz_personen_bg=anz_personen_bg,
        bruttokaltmiete_m_bg=bruttokaltmiete_m_bg,
        wohngeld_min_miete_m_bg=wohngeld_min_miete_m_bg,
        wohngeld_params=wohngeld_params,
    )


def wohngeld_nach_vermög_check_m_bg(
    wohngeld_vor_vermög_check_m_bg: float,
    vermögen_bedürft_bg: float,
    anz_personen_bg: int,
    wohngeld_params: dict,
) -> float:
    """Set preliminary housing benefit to zero if it exceeds the wealth exemption.

    This target is used for the priority check calculation against ALG2 and
    Kinderzuschlag.

    Parameters
    ----------
    wohngeld_vor_vermög_check_m_bg
        See :func:`wohngeld_vor_vermög_check_m_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return _wohngeld_nach_vermög_check_formel(
        wohngeld_basisbetrag=wohngeld_vor_vermög_check_m_bg,
        vermögen=vermögen_bedürft_bg,
        anz_personen=anz_personen_bg,
        wohngeld_params=wohngeld_params,
    )


@policy_info(params_key_for_rounding="wohngeld")
def wohngeld_vor_vermög_check_m_wth(
    anz_personen_wth: int,
    wohngeld_eink_m_wth: float,
    wohngeld_miete_m_wth: float,
    wohngeld_params: dict,
) -> float:
    """Calcualte preliminary housing benefit.

    This target is used for the actual Wohngeld calculation of the Bedarfsgemeinschaften
    that passed the priority check against ALG2 and Kinderzuschlag.

    Parameters
    ----------
    anz_personen_wth
        See :func:`anz_personen_wth`.
    wohngeld_eink_m_wth
        See :func:`wohngeld_eink_m_wth`.
    wohngeld_miete_m_wth
        See :func:`wohngeld_miete_m_wth`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_basisformel(
        anz_personen=anz_personen_wth,
        einkommen=wohngeld_eink_m_wth,
        miete=wohngeld_miete_m_wth,
        wohngeld_params=wohngeld_params,
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
        einkommen=wohngeld_eink_m_bg,
        miete=wohngeld_miete_m_bg,
        wohngeld_params=wohngeld_params,
    )
