"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif
from gettsim.transfers.rente import ges_rente_regelaltersgrenze


def arbeitsl_geld_m(
    anz_kinder_tu: int,
    arbeitsl_geld_berechtigt: int,
    arbeitsl_geld_eink_vorj_proxy: float,
    arbeitsl_geld_params: dict,
) -> float:
    """Calculate individual unemployment benefit.

    Parameters
    ----------
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    anspruchsdauer_aktuell
        See :func:`anspruchsdauer_aktuell`.
    arbeitsl_geld_eink_vorj_proxy
        See :func:`arbeitsl_geld_eink_vorj_proxy`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """

    if arbeitsl_geld_berechtigt:
        if anz_kinder_tu == 0:
            arbeitsl_geld_satz = arbeitsl_geld_params["satz_ohne_kinder"]
        else:
            arbeitsl_geld_satz = arbeitsl_geld_params["satz_mit_kindern"]

        out = arbeitsl_geld_eink_vorj_proxy * arbeitsl_geld_satz
    else:
        out = 0.0

    return out


def restliche_anspruchsdauer(
    dauer_nach_anwartschaftszeit: int,
    dauer_nach_alter: int,
    arbeitsl_geld_bezug_m: int,
) -> int:
    """Calculate the remaining amount of months a person can receive unemployment
    benifit this year.

    Parameters
    ----------
    dauer_nach_anwartschaftszeit
        See :func:`dauer_nach_anwartschaftszeit`.
    dauer_nach_alter
        See :func:`dauer_nach_alter`.
    arbeitsl_geld_bezug_m
        See basic input variable :ref:`arbeitsl_geld_bezug_m <arbeitsl_geld_bezug_m>`.


    Returns
    -------

    """
    anspruchsdauer_gesamt = min(dauer_nach_alter, dauer_nach_anwartschaftszeit)
    out = max(anspruchsdauer_gesamt - arbeitsl_geld_bezug_m, 0)

    return out


def arbeitsl_geld_berechtigt(
    alter: int,
    arbeitssuchend: bool,
    restliche_anspruchsdauer: int,
    arbeitsstunden_w: float,
    arbeitsl_geld_params: dict,
    geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Check eligibility for unemployment benefit.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    arbeitssuchend
        See basic input variable :ref:`arbeitssuchend <arbeitssuchend>`.
    restliche_anspruchsdauer
        See :func:`restliche_anspruchsdauer`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    regelaltersgrenze = ges_rente_regelaltersgrenze(geburtsjahr, ges_rente_params)

    out = (
        arbeitssuchend
        and (restliche_anspruchsdauer > 0)
        and (alter < regelaltersgrenze)
        and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )

    return out


def dauer_nach_alter(
    alter: int,
    arbeitsl_geld_params: dict,
) -> int:
    """Calculate the lenght of unemployment benifit according to age.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    nach_alter = piecewise_polynomial(
        alter,
        thresholds=list(arbeitsl_geld_params["anspruchsdauer"]["nach_alter"])
        + [np.inf],
        rates=np.array(
            [[0] * len(arbeitsl_geld_params["anspruchsdauer"]["nach_alter"])]
        ),
        intercepts_at_lower_thresholds=list(
            arbeitsl_geld_params["anspruchsdauer"]["nach_alter"].values()
        ),
    )

    return nach_alter


def dauer_nach_anwartschaftszeit(
    anwartschaftszeit: int,
    arbeitsl_geld_params: dict,
) -> int:
    """Calculate the lenght of unemployment benifit according to anwartschaftszeit.

    Parameters
    ----------
    anwartschaftszeit
        See basic input variable :ref:`anwartschaftszeit <anwartschaftszeit>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    nach_anwartschaftszeit = piecewise_polynomial(
        anwartschaftszeit,
        thresholds=list(
            arbeitsl_geld_params["anspruchsdauer"]["nach_anwartschaftszeit"]
        )
        + [np.inf],
        rates=np.array(
            [
                [0]
                * len(arbeitsl_geld_params["anspruchsdauer"]["nach_anwartschaftszeit"])
            ]
        ),
        intercepts_at_lower_thresholds=list(
            arbeitsl_geld_params["anspruchsdauer"]["nach_anwartschaftszeit"].values()
        ),
    )

    return nach_anwartschaftszeit


def arbeitsl_geld_eink_vorj_proxy(
    _ges_rentenv_beitr_bemess_grenze_m: float,
    bruttolohn_vorj_m: float,
    arbeitsl_geld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> float:
    """Approximate last years income for unemployment benefit.

    Parameters
    ----------
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.
    bruttolohn_vorj_m
        See basic input variable :ref:`bruttolohn_vorj_m <bruttolohn_vorj_m>`.
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
    max_wage = min(bruttolohn_vorj_m, _ges_rentenv_beitr_bemess_grenze_m)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = arbeitsl_geld_params["soz_vers_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = _eink_st_tarif(
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
