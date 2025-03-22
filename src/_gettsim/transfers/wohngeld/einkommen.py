"""Income relevant for housing benefit calculation."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.config import numpy_or_jax as np
from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial

aggregation_specs = {
    "alleinerziehendenbonus": AggregateByPIDSpec(
        p_id_to_aggregate_by="kindergeld__p_id_empfänger",
        source_col="kindergeld__kind_bis_10_mit_kindergeld",
        aggr="sum",
    ),
}


@policy_function()
def einkommen_m_wthh(
    anzahl_personen_wthh: int,
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
    anzahl_personen_wthh
        See :func:`anzahl_personen_wthh`.
    freibetrag_m_wthh
        See :func:`freibetrag_m_wthh`.
    einkommen_vor_freibetrag_m_wthh
        See :func:`einkommen_vor_freibetrag_m_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return einkommen(
        anzahl_personen=anzahl_personen_wthh,
        einkommen_freibetrag=freibetrag_m_wthh,
        einkommen_vor_freibetrag=einkommen_vor_freibetrag_m_wthh,
        params=wohngeld_params,
    )


@policy_function()
def einkommen_m_bg(
    arbeitslosengeld_2__anzahl_personen_bg: int,
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
    arbeitslosengeld_2__anzahl_personen_bg
        See :func:`arbeitslosengeld_2__anzahl_personen_bg`.
    freibetrag_m_bg
        See :func:`freibetrag_m_bg`.
    einkommen_vor_freibetrag_m_bg
        See :func:`einkommen_vor_freibetrag_m_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    return einkommen(
        anzahl_personen=arbeitslosengeld_2__anzahl_personen_bg,
        einkommen_freibetrag=freibetrag_m_bg,
        einkommen_vor_freibetrag=einkommen_vor_freibetrag_m_bg,
        params=wohngeld_params,
    )


@policy_function()
def abzugsanteil_vom_einkommen_für_steuern_sozialversicherung(
    einkommensteuer__betrag_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y: float,
    demographics__kind: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions on the individual level.

    Note that einkommensteuer__betrag_y_sn is used as an approximation for taxes
    on income (as mentioned in § 16 WoGG Satz 1 Nr. 1).

    Parameters
    ----------
    einkommensteuer__betrag_y_sn
        See :func:
        `einkommensteuer__betrag_y_sn`.
    sozialversicherung__rente__beitrag__betrag_versicherter_y
        See :func:
        `sozialversicherung__rente__beitrag__betrag_versicherter_y`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_y
        See :func:
        `sozialversicherung__kranken__beitrag__betrag_versicherter_y`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    abzug_stufen = (
        (einkommensteuer__betrag_y_sn > 0)
        + (sozialversicherung__rente__beitrag__betrag_versicherter_y > 0)
        + (sozialversicherung__kranken__beitrag__betrag_versicherter_y > 0)
    )
    if demographics__kind:
        out = 0.0
    else:
        out = wohngeld_params["abzug_stufen"][abzug_stufen]
    return out


@policy_function(end_date="2006-12-31", leaf_name="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_ohne_elterngeld(  # noqa: PLR0913
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
    einkommensteuer__einkünfte__sonstige__betrag_m: float,
    einkommensteuer__renteneinkommen_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        See :func:`_eink_selbst`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m`.
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m`.
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        See :func:`einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m`.
    sozialversicherung__arbeitslosen__betrag_m
        See :func:`sozialversicherung__arbeitslosen__betrag_m`.
    einkommensteuer__einkünfte__sonstige__betrag_m
        See :func:`einkommensteuer__einkünfte__sonstige__betrag_m`.
    einkommensteuer__renteneinkommen_m
        See :func:`einkommensteuer__renteneinkommen_m`.
    unterhalt__tatsächlich_erhaltener_betrag_m
        See basic input variable :ref:`unterhalt__tatsächlich_erhaltener_betrag_m <unterhalt__tatsächlich_erhaltener_betrag_m>`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung
        See :func:`abzugsanteil_vom_einkommen_für_steuern_sozialversicherung`.

    Returns
    -------

    """
    einkommen = (
        einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m
        + einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
    )

    transfers = (
        sozialversicherung__arbeitslosen__betrag_m
        + einkommensteuer__renteneinkommen_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
    )

    eink_ind = einkommen + transfers + einkommensteuer__einkünfte__sonstige__betrag_m
    out = (1 - abzugsanteil_vom_einkommen_für_steuern_sozialversicherung) * eink_ind
    return out


@policy_function(start_date="2007-01-01", leaf_name="einkommen_vor_freibetrag_m")
def einkommen_vor_freibetrag_m_mit_elterngeld(  # noqa: PLR0913
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    sozialversicherung__arbeitslosen__betrag_m: float,
    einkommensteuer__einkünfte__sonstige__betrag_m: float,
    einkommensteuer__renteneinkommen_m: float,
    unterhalt__tatsächlich_erhaltener_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    elterngeld__anrechenbarer_betrag_m: float,
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung: float,
) -> float:
    """Sum gross incomes relevant for housing benefit calculation on individual level
    and deducting individual housing benefit subtractions.
    Reference: § 14 WoGG

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        See :func:`_eink_selbst`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m`.
    einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m`.
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        See :func:`einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m`.
    sozialversicherung__arbeitslosen__betrag_m
        See :func:`sozialversicherung__arbeitslosen__betrag_m`.
    einkommensteuer__einkünfte__sonstige__betrag_m
        See :func:`einkommensteuer__einkünfte__sonstige__betrag_m`.
    einkommensteuer__renteneinkommen_m
        See :func:`einkommensteuer__renteneinkommen_m`.
    unterhalt__tatsächlich_erhaltener_betrag_m
        See basic input variable :ref:`unterhalt__tatsächlich_erhaltener_betrag_m <unterhalt__tatsächlich_erhaltener_betrag_m>`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    elterngeld__anrechenbarer_betrag_m
        See :func:`elterngeld__anrechenbarer_betrag_m`.
    abzugsanteil_vom_einkommen_für_steuern_sozialversicherung
        See :func:`abzugsanteil_vom_einkommen_für_steuern_sozialversicherung`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Find out whether unterhalt__tatsächlich_erhaltener_betrag_m and
    # unterhaltsvorschuss__betrag_m are counted as income for Wohngeld income check.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/357
    einkommen = (
        einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__betrag_ohne_minijob_m
        + einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
    )

    transfers = (
        sozialversicherung__arbeitslosen__betrag_m
        + einkommensteuer__renteneinkommen_m
        + unterhalt__tatsächlich_erhaltener_betrag_m
        + unterhaltsvorschuss__betrag_m
        + elterngeld__anrechenbarer_betrag_m
    )

    eink_ind = einkommen + transfers + einkommensteuer__einkünfte__sonstige__betrag_m
    out = (1 - abzugsanteil_vom_einkommen_für_steuern_sozialversicherung) * eink_ind
    return out


@policy_function(end_date="2015-12-31", leaf_name="freibetrag_m")
def freibetrag_m_bis_2015(  # noqa: PLR0913
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    ist_kind_mit_erwerbseinkommen: bool,
    demographics__behinderungsgrad: int,
    demographics__alleinerziehend: bool,
    demographics__kind: bool,
    alleinerziehendenbonus: int,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtractions for one individual until 2015.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    ist_kind_mit_erwerbseinkommen
        See :func:`ist_kind_mit_erwerbseinkommen`.
    demographics__behinderungsgrad
        See basic input variable :ref:`demographics__behinderungsgrad <demographics__behinderungsgrad>`.
    demographics__alleinerziehend
        See basic input variable :ref:`demographics__alleinerziehend <demographics__alleinerziehend>`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.
    alleinerziehendenbonus
        See :func:`alleinerziehendenbonus`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """
    freibetrag_behinderung_m = piecewise_polynomial(
        demographics__behinderungsgrad,
        thresholds=[*list(wohngeld_params["freibetrag_behinderung"]), np.inf],
        rates=np.array([[0] * len(wohngeld_params["freibetrag_behinderung"])]),
        intercepts_at_lower_thresholds=[
            yearly_v / 12
            for yearly_v in wohngeld_params["freibetrag_behinderung"].values()
        ],
    )

    # Subtraction for single parents and working children
    if ist_kind_mit_erwerbseinkommen:
        freibetrag_kinder_m = min(
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m,
            wohngeld_params["freibetrag_kinder_m"]["arbeitendes_kind"],
        )

    elif demographics__alleinerziehend and (not demographics__kind):
        freibetrag_kinder_m = (
            alleinerziehendenbonus
            * wohngeld_params["freibetrag_kinder_m"]["alleinerziehend"]
        )
    else:
        freibetrag_kinder_m = 0.0
    return freibetrag_behinderung_m + freibetrag_kinder_m


@policy_function(start_date="2016-01-01", leaf_name="freibetrag_m")
def freibetrag_m_ab_2016(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    ist_kind_mit_erwerbseinkommen: bool,
    demographics__behinderungsgrad: int,
    demographics__alleinerziehend: bool,
    wohngeld_params: dict,
) -> float:
    """Calculate housing benefit subtracting for one individual since 2016.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    ist_kind_mit_erwerbseinkommen
        See :func:`ist_kind_mit_erwerbseinkommen`.
    demographics__behinderungsgrad
        See basic input variable :ref:`demographics__behinderungsgrad <demographics__behinderungsgrad>`.
    demographics__alleinerziehend
        See basic input variable :ref:`demographics__alleinerziehend <demographics__alleinerziehend>`.
    demographics__kind
        See basic input variable :ref:`demographics__kind <demographics__kind>`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.
    Returns
    -------

    """
    freibetrag_behinderung_m = (
        wohngeld_params["freibetrag_behinderung"] / 12
        if demographics__behinderungsgrad > 0
        else 0
    )

    if ist_kind_mit_erwerbseinkommen:
        freibetrag_kinder_m = min(
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m,
            wohngeld_params["freibetrag_kinder_m"]["arbeitendes_kind"],
        )
    elif demographics__alleinerziehend:
        freibetrag_kinder_m = wohngeld_params["freibetrag_kinder_m"]["alleinerziehend"]
    else:
        freibetrag_kinder_m = 0.0

    return freibetrag_behinderung_m + freibetrag_kinder_m


def einkommen(
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


@policy_function()
def ist_kind_mit_erwerbseinkommen(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    kindergeld__grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Check if children are working.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    kindergeld__grundsätzlich_anspruchsberechtigt
        See :func:`kindergeld__grundsätzlich_anspruchsberechtigt`.

    Returns
    -------

    """
    out = (
        einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m > 0
    ) and kindergeld__grundsätzlich_anspruchsberechtigt
    return out
