"""Income relevant for housing benefit calculation."""

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


def wohngeld_eink_m_wthh(
    anz_personen_wthh: int,
    wohngeld_eink_freib_m_wthh: float,
    wohngeld_eink_vor_freib_m_wthh: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

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

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

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
    eink_selbst_m: float,
    eink_abhängig_beschäftigt_m: float,
    kapitaleink_brutto_m: float,
    eink_vermietung_m: float,
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
    eink_selbst_m
        See :func:`_eink_selbst`.
    eink_abhängig_beschäftigt_m
        See :func:`eink_abhängig_beschäftigt_m`.
    kapitaleink_brutto_m
        See :func:`kapitaleink_brutto_m`.
    eink_vermietung_m
        See :func:`eink_vermietung_m`.
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
        eink_selbst_m
        + eink_abhängig_beschäftigt_m
        + kapitaleink_brutto_m
        + eink_vermietung_m
    )

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
    eink_selbst_m: float,
    eink_abhängig_beschäftigt_m: float,
    kapitaleink_brutto_m: float,
    eink_vermietung_m: float,
    arbeitsl_geld_m: float,
    sonstig_eink_m: float,
    eink_rente_zu_verst_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    anrechenbares_elterngeld_m: float,
    wohngeld_abzüge_st_sozialv_m: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    Parameters
    ----------
    eink_selbst_m
        See :func:`_eink_selbst`.
    eink_abhängig_beschäftigt_m
        See :func:`eink_abhängig_beschäftigt_m`.
    kapitaleink_brutto_m
        See :func:`kapitaleink_brutto_m`.
    eink_vermietung_m
        See :func:`eink_vermietung_m`.
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
    anrechenbares_elterngeld_m
        See :func:`anrechenbares_elterngeld_m`.
    wohngeld_abzüge_st_sozialv_m
        See :func:`wohngeld_abzüge_st_sozialv_m`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Find out whether kind_unterh_erhalt_m and unterhaltsvors_m
    # are counted as income for Wohngeld income check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/357
    einkommen = (
        eink_selbst_m
        + eink_abhängig_beschäftigt_m
        + kapitaleink_brutto_m
        + eink_vermietung_m
    )

    transfers = (
        arbeitsl_geld_m
        + eink_rente_zu_verst_m
        + kind_unterh_erhalt_m
        + unterhaltsvors_m
        + anrechenbares_elterngeld_m
    )

    eink_ind = einkommen + transfers + sonstig_eink_m
    out = (1 - wohngeld_abzüge_st_sozialv_m) * eink_ind
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
