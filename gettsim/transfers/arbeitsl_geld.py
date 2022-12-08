"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif
from gettsim.transfers.rente import ges_rente_regelaltersgrenze


def arbeitsl_geld_m(
    anz_kinder_tu: int,
    anspruchsdauer_aktuell: int,
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

    if anz_kinder_tu == 0:
        arbeitsl_geld_satz = (
            arbeitsl_geld_params["satz_ohne_kinder"] * anspruchsdauer_aktuell / 12
        )
    else:
        arbeitsl_geld_satz = (
            arbeitsl_geld_params["satz_mit_kindern"] * anspruchsdauer_aktuell / 12
        )

    out = arbeitsl_geld_eink_vorj_proxy * arbeitsl_geld_satz

    return out


def anspruchsdauer_aktuell(
    anspruchsdauer_gesamt: int,
    alter: int,
    arbeitsl_geld_params: dict,
    arbeitsl_geld_berechtigt: bool,
    arbeitsl_geld_m_vorj: int,
    arbeitsl_geld_m_v2j: int,
) -> int:
    """Calculate the amount of months a person can receive unemployment benifit
    this year.

    Parameters
    ----------
    anspruchsdauer_gesamt
        See :func:`anspruchsdauer_gesamt`.
    alter
        See basic input variable :ref:`alter <alter>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.
    arbeitsl_geld_berechtigt
        See :func:`arbeitsl_geld_berechtigt`.
    arbeitsl_geld_m_vorj
        See basic input variable :ref:`arbeitsl_geld_m_vorj <arbeitsl_geld_m_vorj>`.
    arbeitsl_geld_m_v2j
        See basic input variable :ref:`arbeitsl_geld_m_v2j <arbeitsl_geld_m_v2j>`.

    Returns
    -------

    """

    if arbeitsl_geld_berechtigt:
        if alter >= arbeitsl_geld_params["anwartschaftszeit"]["threshold_5"]["age"]:
            out = max(
                anspruchsdauer_gesamt - arbeitsl_geld_m_vorj - arbeitsl_geld_m_v2j, 0
            )
        else:
            out = max(anspruchsdauer_gesamt - arbeitsl_geld_m_vorj, 0)
    else:
        out = 0

    return out


def anspruchsdauer_gesamt(
    anwartschaftszeit: int,
    alter: int,
    arbeitsl_geld_params: dict,
) -> int:
    """Calculate the amount of months a person could receive unemployment benifit.

    Parameters
    ----------
    anwartschaftszeit
        See basic input variable :ref:`anwartschaftszeit <anwartschaftszeit>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    for threshold in [
        "threshold_1",
        "threshold_2",
        "threshold_3",
        "threshold_4",
        "threshold_5",
        "threshold_6",
        "threshold_7",
    ]:
        if (
            anwartschaftszeit
            >= arbeitsl_geld_params["anwartschaftszeit"][threshold]["min"]
            and alter >= arbeitsl_geld_params["anwartschaftszeit"][threshold]["age"]
        ):
            out = arbeitsl_geld_params["anwartschaftszeit"][threshold]["anspruch"]
        else:
            out = 0

        return out
    return out


def arbeitsl_geld_berechtigt(
    alter: int,
    arbeitssuchend: bool,
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
        and (alter < regelaltersgrenze)
        and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )

    return out


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
