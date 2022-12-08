"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif

# from gettsim.transfers.rente import ges_rente_regelaltersgrenze


def arbeitsl_geld_m(
    anz_kinder_tu: int,
    arbeitsl_geld_berechtigt: bool,
    arbeitsl_geld_eink_vorj_proxy: float,
    arbeitsl_geld_params: dict,
) -> float:
    """Calculate individual unemployment benefit.

    Parameters
    ----------
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    arbeitsl_geld_berechtigt
        See :func:`arbeitsl_geld_berechtigt`.
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


def arbeitsl_monate_gesamt(
    arbeitsl_monate_lfdj: int,
    arbeitsl_monate_vorj: int,
    arbeitsl_monate_v2j: int,
) -> int:
    """Aggregate months of unemployment over the last two years.

    Parameters
    ----------
    arbeitsl_monate_lfdj
        See basic input variable :ref:`arbeitsl_monate_lfdj <arbeitsl_monate_lfdj>`.
    arbeitsl_monate_vorj
        See basic input variable :ref:`arbeitsl_monate_vorj <arbeitsl_monate_vorj>`.
    arbeitsl_monate_v2j
        See basic input variable :ref:`arbeitsl_monate_v2j <arbeitsl_monate_v2j>`.

    Returns
    -------

    """
    return arbeitsl_monate_lfdj + arbeitsl_monate_vorj + arbeitsl_monate_v2j


def arbeitsl_geld_berechtigt(
    arbeitsl_monate_gesamt: int,
    alter: int,
    sum_ges_rente_priv_rente_m: float,
    arbeitsstunden_w: float,
    arbeitsl_geld_params: dict,
    # ges_rente_regelaltersgrenze: float,
    # arbeitslos: bool,
) -> bool:
    """Check eligibility for unemployment benefit.

    Different rates for parent and non-parents. Take into account actual wages. There
    are different replacement rates depending on presence of children

    Parameters
    ----------
    arbeitsl_monate_gesamt
        See :func:`arbeitsl_monate_gesamt`.
    alter
        See basic input variable :ref:`alter <alter>`.
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    out = (
        (
            arbeitsl_monate_gesamt
            <= arbeitsl_geld_params["dauer_auszahlung"]["max_dauer"]
        )
        # the duration of unemployment benifit depends on how long you paid
        # unemloyment insurance in the last 30 months
        and (alter < arbeitsl_geld_params["altersgrenze"]["alter"])
        # supposed to be younger than Regelaltersgrenze
        and (sum_ges_rente_priv_rente_m == 0)  # ?
        and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )
    # # in order to get alg you need to:
    # # - not be in_ausbildung/ dem Arbeitsmarkt zu Verfügung stehen (min. 15 h/ week)
    # # - paid unemployment insurance in at least 12 of the last 30 months
    # # - be registered as unemployed
    # # you then get alg for:
    # # - 6 months for 12 months unemployement insurance
    # # - 8 months for 16, 10 for 20 and 12 for 24
    # # - if you´re at least 50: 15 for 30
    # # - if you´re at least 55: 18 for 36
    # # - if you´re at least 58: 24 for 48
    # # you get:
    # # - 60% (or 67%) of your Leistungsentgelt
    # # Leistungsentgelt =
    # # bruttolohn (of months > mini-job) - lohnsteuer - soli - social insurances (20%)

    # out = (
    #     (
    #         arbeitsl_versich_monate_letzte_30_monate
    #         >= arbeitsl_geld_params["anwartschaftszeit"]["min_dauer"]
    #         == 12
    #     )
    #     and (arbeitslos_gemeldet)
    #     and (~arbeitsl_geld_prev_year)
    #     and (alter < ges_rente_regelaltersgrenze)
    #     and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    # )
    # if alter > 58:
    #     out = (
    #         (
    #             arbeitsl_versich_monate_letzten_30_monate
    #             >= arbeitsl_geld_params["anwartschaftszeit"]["min_dauer"]
    #             == 12
    #         )
    #         and (arbeitslos_gemeldet)
    #         and (~arbeitsl_geld_prev_prev_year)
    #         and (alter < ges_rente_regelaltersgrenze)
    #         and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    #     )

    # out = (
    #     (arbeitsl_monate_gesamt
    # < arbeitsl_geld_params["dauer_auszahlung"]["max_dauer"])
    #     and (arbeitslos)
    #     and (alter < ges_rente_regelaltersgrenze)
    #     and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    # )

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
