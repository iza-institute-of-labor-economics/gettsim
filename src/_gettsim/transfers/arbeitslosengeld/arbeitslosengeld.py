"""Unemployment benefits (Arbeitslosengeld)."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.einkommensteuer.einkommensteuer import einkommensteuer_tarif


@policy_function()
def betrag_m(
    einkommensteuer__freibeträge__kinderfreibetrag_anzahl_ansprüche: int,
    grundsätzlich_anspruchsberechtigt: bool,
    einkommen_vorjahr_proxy_m: float,
    arbeitsl_geld_params: dict,
) -> float:
    """Calculate individual unemployment benefit.

    Parameters
    ----------
    einkommensteuer__freibeträge__kinderfreibetrag_anzahl_ansprüche
        See :func:
        `einkommensteuer__freibeträge__kinderfreibetrag_anzahl_ansprüche`.
    grundsätzlich_anspruchsberechtigt
        See :func:`grundsätzlich_anspruchsberechtigt`.
    einkommen_vorjahr_proxy_m
        See :func:`einkommen_vorjahr_proxy_m`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """

    if einkommensteuer__freibeträge__kinderfreibetrag_anzahl_ansprüche == 0:
        arbeitsl_geld_satz = arbeitsl_geld_params["satz_ohne_kinder"]
    elif einkommensteuer__freibeträge__kinderfreibetrag_anzahl_ansprüche > 0:
        arbeitsl_geld_satz = arbeitsl_geld_params["satz_mit_kindern"]

    if grundsätzlich_anspruchsberechtigt:
        out = einkommen_vorjahr_proxy_m * arbeitsl_geld_satz
    else:
        out = 0.0

    return out


@policy_function()
def verbleibende_anspruchsdauer(
    demographics__alter: int,
    war_5_jahre_sozialversicherungspflichtig: float,
    anwartschaftszeit: bool,
    monate_durchgängiger_alg1_bezug: float,
    arbeitsl_geld_params: dict,
) -> int:
    """Calculate the remaining amount of months a person can receive unemployment
    benefit this year.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    war_5_jahre_sozialversicherungspflichtig
        See basic input variable :ref:`war_5_jahre_sozialversicherungspflichtig <war_5_jahre_sozialversicherungspflichtig>`.
    anwartschaftszeit
        See basic input variable :ref:`anwartschaftszeit <anwartschaftszeit>`.
    monate_durchgängiger_alg1_bezug
        See basic input variable :ref:`monate_durchgängiger_alg1_bezug <monate_durchgängiger_alg1_bezug>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    nach_alter = piecewise_polynomial(
        demographics__alter,
        thresholds=[
            *list(arbeitsl_geld_params["anspruchsdauer"]["nach_alter"]),
            np.inf,
        ],
        rates=np.array(
            [[0] * len(arbeitsl_geld_params["anspruchsdauer"]["nach_alter"])]
        ),
        intercepts_at_lower_thresholds=list(
            arbeitsl_geld_params["anspruchsdauer"]["nach_alter"].values()
        ),
    )
    nach_versich_pfl = piecewise_polynomial(
        war_5_jahre_sozialversicherungspflichtig,
        thresholds=[
            *list(
                arbeitsl_geld_params["anspruchsdauer"][
                    "nach_versicherungspflichtige_monate"
                ]
            ),
            np.inf,
        ],
        rates=np.array(
            [
                [0]
                * len(
                    arbeitsl_geld_params["anspruchsdauer"][
                        "nach_versicherungspflichtige_monate"
                    ]
                )
            ]
        ),
        intercepts_at_lower_thresholds=list(
            arbeitsl_geld_params["anspruchsdauer"][
                "nach_versicherungspflichtige_monate"
            ].values()
        ),
    )
    if anwartschaftszeit:
        anspruchsdauer_gesamt = min(nach_alter, nach_versich_pfl)

    if anwartschaftszeit:
        out = max(anspruchsdauer_gesamt - monate_durchgängiger_alg1_bezug, 0)
    else:
        out = 0

    return out


@policy_function()
def grundsätzlich_anspruchsberechtigt(  # noqa: PLR0913
    demographics__alter: int,
    arbeitssuchend: bool,
    verbleibende_anspruchsdauer: int,
    demographics__arbeitsstunden_w: float,
    arbeitsl_geld_params: dict,
    rente__altersrente__regelaltersrente__altersgrenze: float,
) -> bool:
    """Check eligibility for unemployment benefit.

    Parameters
    ----------
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    arbeitssuchend
        See basic input variable :ref:`arbeitssuchend <arbeitssuchend>`.
    verbleibende_anspruchsdauer
        See :func:`verbleibende_anspruchsdauer`.
    demographics__arbeitsstunden_w
        See basic input variable :ref:`demographics__arbeitsstunden_w <demographics__arbeitsstunden_w>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.

    Returns
    -------

    """
    regelaltersgrenze = rente__altersrente__regelaltersrente__altersgrenze

    out = (
        arbeitssuchend
        and (verbleibende_anspruchsdauer > 0)
        and (demographics__alter < regelaltersgrenze)
        and (demographics__arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )

    return out


@policy_function()
def einkommen_vorjahr_proxy_m(  # noqa: PLR0913
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_m: float,
    einkommen__bruttolohn_vorjahr_m: float,
    arbeitsl_geld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> float:
    """Approximate last years income for unemployment benefit.

    Parameters
    ----------
    sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_m
        See :func:
        `sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_m`.
    einkommen__bruttolohn_vorjahr_m
        See basic input variable :ref:`einkommen__bruttolohn_vorjahr_m <einkommen__bruttolohn_vorjahr_m>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    # Relevant wage is capped at the contribution thresholds
    max_wage = min(
        einkommen__bruttolohn_vorjahr_m,
        sozialversicherung__rente__beitrag__beitragsbemessungsgrenze_m,
    )

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = arbeitsl_geld_params["sozialv_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    # Caution: currently wrong calculation due to
    # 12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"] not being
    # the same as zu versteuerndes einkommen
    # waiting for PR Lohnsteuer #150 to be merged to correct this problem
    prox_tax = einkommensteuer_tarif(
        12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"],
        eink_st_params,
    )
    prox_soli = piecewise_polynomial(
        prox_tax,
        thresholds=soli_st_params["soli_st"]["thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )
    out = max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12
    out = max(out, 0.0)
    return out
