"""Income relevant for housing benefit calculation."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.config import numpy_or_jax as np
from _gettsim.functions.policy_function import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial

aggregation_specs = {
    "freibetrag_alleinerziehend_bonus": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_kindergeld_empf",
        source_col="kindergeld__kind_bis_10_mit_kindergeld",
        aggr="sum",
    ),
}


@policy_function
def einkommen_m_wthh(
    demographic_vars__anzahl_personen_wthh: int,
    freibetrag_m_wthh: float,
    einkommen_vor_freibetrag_m_wthh: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    Parameters
    ----------
    demographic_vars__anzahl_personen_wthh
        See :func:`demographic_vars__anzahl_personen_wthh`.
    freibetrag_m_wthh
        See :func:`freibetrag_m_wthh`.
    einkommen_vor_freibetrag_m_wthh
        See :func:`einkommen_vor_freibetrag_m_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_einkommen_formel(
        anzahl_personen=demographic_vars__anzahl_personen_wthh,
        einkommen_freibetrag=freibetrag_m_wthh,
        einkommen_vor_freibetrag=einkommen_vor_freibetrag_m_wthh,
        params=wohngeld_params,
    )


@policy_function
def einkommen_m_bg(
    demographic_vars__anzahl_personen_bg: int,
    freibetrag_m_bg: float,
    einkommen_vor_freibetrag_m_bg: float,
    wohngeld_params: dict,
) -> float:
    """Income relevant for Wohngeld calculation.

    Reference: § 13 WoGG

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    demographic_vars__anzahl_personen_bg
        See :func:`demographic_vars__anzahl_personen_bg`.
    freibetrag_m_bg
        See :func:`freibetrag_m_bg`.
    einkommen_vor_freibetrag_m_bg
        See :func:`einkommen_vor_freibetrag_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return _wohngeld_einkommen_formel(
        anzahl_personen=demographic_vars__anzahl_personen_bg,
        einkommen_freibetrag=freibetrag_m_bg,
        einkommen_vor_freibetrag=einkommen_vor_freibetrag_m_bg,
        params=wohngeld_params,
    )


@policy_function
def abzüge_steuern_sozialversicherung_m(
    taxes__einkommensteuer__betrag_y_sn: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m: float,
    kind: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions on the individual level.

    Note that taxes__einkommensteuer__betrag_y_sn is used as an approximation for taxes
    on income (as mentioned in § 16 WoGG Satz 1 Nr. 1).

    Parameters
    ----------
    taxes__einkommensteuer__betrag_y_sn
        See :func:
        `taxes__einkommensteuer__betrag_y_sn`.
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m
        See :func:
        `sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m
        See :func:
        `sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m`.
    kind
        See basic input variable :ref:`kind <kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (taxes__einkommensteuer__betrag_y_sn > 0)
        + (sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m > 0)
        + (sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m > 0)
    )
    if kind:
        out = 0.0
    else:
        out = wohngeld_params["abzug_stufen"][abzug_stufen]
    return out


@policy_function(end_date="2006-12-31", name_in_dag="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_ohne_elterngeld(  # noqa: PLR0913
    eink_selbst_m: float,
    eink_abhängig_beschäftigt_m: float,
    kapitaleink_brutto_m: float,
    eink_vermietung_m: float,
    arbeitslosengeld__betrag_m: float,
    sonstig_eink_m: float,
    einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvorschuss__betrag_m: float,
    abzüge_steuern_sozialversicherung_m: float,
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
    arbeitslosengeld__betrag_m
        See :func:`arbeitslosengeld__betrag_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m
        See :func:`einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    abzüge_steuern_sozialversicherung_m
        See :func:`abzüge_steuern_sozialversicherung_m`.

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
        arbeitslosengeld__betrag_m
        + einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m
        + kind_unterh_erhalt_m
        + unterhaltsvorschuss__betrag_m
    )

    eink_ind = einkommen + transfers + sonstig_eink_m
    out = (1 - abzüge_steuern_sozialversicherung_m) * eink_ind
    return out


@policy_function(start_date="2007-01-01", name_in_dag="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_mit_elterngeld(  # noqa: PLR0913
    eink_selbst_m: float,
    eink_abhängig_beschäftigt_m: float,
    kapitaleink_brutto_m: float,
    eink_vermietung_m: float,
    arbeitslosengeld__betrag_m: float,
    sonstig_eink_m: float,
    einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvorschuss__betrag_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
    abzüge_steuern_sozialversicherung_m: float,
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
    arbeitslosengeld__betrag_m
        See :func:`arbeitslosengeld__betrag_m`.
    sonstig_eink_m
        See :func:`sonstig_eink_m`.
    einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m
        See :func:`einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    elterngeld__anrechenbarer_betrag_m
        See :func:`elterngeld__anrechenbarer_betrag_m`.
    abzüge_steuern_sozialversicherung_m
        See :func:`abzüge_steuern_sozialversicherung_m`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Find out whether kind_unterh_erhalt_m and
    # unterhaltsvorschuss__betrag_m are counted as income for Wohngeld income check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/357
    einkommen = (
        eink_selbst_m
        + eink_abhängig_beschäftigt_m
        + kapitaleink_brutto_m
        + eink_vermietung_m
    )

    transfers = (
        arbeitslosengeld__betrag_m
        + einkommensteuer__einkommen__bruttoeinkommen_renteneinkommen_m
        + kind_unterh_erhalt_m
        + unterhaltsvorschuss__betrag_m
        + elterngeld__anrechenbarer_betrag_m
    )

    eink_ind = einkommen + transfers + sonstig_eink_m
    out = (1 - abzüge_steuern_sozialversicherung_m) * eink_ind
    return out


@policy_function(end_date="2015-12-31", name_in_dag="freibetrag_m")
def freibetrag_m_bis_2015(  # noqa: PLR0913
    bruttolohn_m: float,
    demographic_vars__ist_kind_mit_erwerbseinkommen: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    kind: bool,
    freibetrag_alleinerziehend_bonus: int,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions for one individual until 2015.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    demographic_vars__ist_kind_mit_erwerbseinkommen
        See :func:`demographic_vars__ist_kind_mit_erwerbseinkommen`.
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    freibetrag_alleinerziehend_bonus
        See :func:`freibetrag_alleinerziehend_bonus`.
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
    if demographic_vars__ist_kind_mit_erwerbseinkommen:
        freib_kinder_m = min(
            bruttolohn_m, wohngeld_params["freib_kinder_m"]["arbeitendes_kind"]
        )

    elif alleinerz and (not kind):
        freib_kinder_m = (
            freibetrag_alleinerziehend_bonus
            * wohngeld_params["freib_kinder_m"]["alleinerz"]
        )
    else:
        freib_kinder_m = 0.0
    return freib_behinderung_m + freib_kinder_m


@policy_function(start_date="2016-01-01", name_in_dag="freibetrag_m")
def freibetrag_m_ab_2016(
    bruttolohn_m: float,
    demographic_vars__ist_kind_mit_erwerbseinkommen: bool,
    behinderungsgrad: int,
    alleinerz: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtracting for one individual since 2016.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    demographic_vars__ist_kind_mit_erwerbseinkommen
        See :func:`demographic_vars__ist_kind_mit_erwerbseinkommen`.
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

    if demographic_vars__ist_kind_mit_erwerbseinkommen:
        freib_kinder_m = min(
            bruttolohn_m, wohngeld_params["freib_kinder_m"]["arbeitendes_kind"]
        )
    elif alleinerz:
        freib_kinder_m = wohngeld_params["freib_kinder_m"]["alleinerz"]
    else:
        freib_kinder_m = 0.0

    return freib_behinderung_m + freib_kinder_m


def _wohngeld_einkommen_formel(
    anzahl_personen: int,
    einkommen_freibetrag: float,
    einkommen_vor_freibetrag: float,
    params: dict,
) -> float:
    """Calculate final income relevant for calculation of housing benefit on household
    level.
    Reference: § 13 WoGG

    Parameters
    ----------
    anzahl_personen
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
    unteres_eink = params["min_eink"][min(anzahl_personen, max(params["min_eink"]))]

    out = max(eink_nach_abzug_m_hh, unteres_eink)
    return float(out)
