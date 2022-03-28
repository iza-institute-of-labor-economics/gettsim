"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif


def arbeitsl_geld_m(
    anz_kinder_tu: int,
    arbeitsl_geld_berechtigt: bool,
    arbeitsl_geld_eink_vorj_proxy: float,
    arbeitsl_geld_params: dict,
) -> float:
    """Calculate unemployment benefit.

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
        out = 0.0
    else:
        if anz_kinder_tu == 0:
            arbeitsl_geld_satz = arbeitsl_geld_params["satz_ohne_kinder"]
        else:
            arbeitsl_geld_satz = arbeitsl_geld_params["satz_mit_kindern"]

        out = arbeitsl_geld_eink_vorj_proxy * arbeitsl_geld_satz

    return out


def arbeitsl_monate_gesamt(
    arbeitsl_monate_lfdj: int, arbeitsl_monate_vorj: int, arbeitsl_monate_v2j: int,
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
        and (alter < arbeitsl_geld_params["altersgrenze"]["alter"])
        and (sum_ges_rente_priv_rente_m == 0)
        and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )
    return out


def arbeitsl_geld_eink_vorj_proxy(
    _ges_rentenv_beitr_bemess_grenze_m: float,
    bruttolohn_vorj_m: float,
    arbeitsl_geld_params: dict,
    eink_st_params: dict,
    eink_st_abzüge_params: dict,
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
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.
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
        12 * max_wage - eink_st_abzüge_params["werbungskostenpauschale"],
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
