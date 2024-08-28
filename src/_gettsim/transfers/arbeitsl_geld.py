"""Functions to compute unemployment benefits (Arbeitslosengeld)."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.eink_st import _eink_st_tarif


def arbeitsl_geld_m(
    _eink_st_kinderfreib_anz_ansprüche: int,
    arbeitsl_geld_berechtigt: bool,
    arbeitsl_geld_eink_vorj_proxy_m: float,
    arbeitsl_geld_params: dict,
) -> float:
    """Calculate individual unemployment benefit.

    Parameters
    ----------
    _eink_st_kinderfreib_anz_ansprüche
        See :func:`_eink_st_kinderfreib_anz_ansprüche`.
    arbeitsl_geld_berechtigt
        See :func:`arbeitsl_geld_berechtigt`.
    arbeitsl_geld_eink_vorj_proxy_m
        See :func:`arbeitsl_geld_eink_vorj_proxy_m`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """

    if _eink_st_kinderfreib_anz_ansprüche == 0:
        arbeitsl_geld_satz = arbeitsl_geld_params["satz_ohne_kinder"]
    elif _eink_st_kinderfreib_anz_ansprüche > 0:
        arbeitsl_geld_satz = arbeitsl_geld_params["satz_mit_kindern"]

    if arbeitsl_geld_berechtigt:
        out = arbeitsl_geld_eink_vorj_proxy_m * arbeitsl_geld_satz
    else:
        out = 0.0

    return out


def arbeitsl_geld_restl_anspruchsd(
    alter: int,
    sozialv_pflicht_5j: float,
    anwartschaftszeit: bool,
    m_durchg_alg1_bezug: float,
    arbeitsl_geld_params: dict,
) -> int:
    """Calculate the remaining amount of months a person can receive unemployment
    benefit this year.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    sozialv_pflicht_5j
        See basic input variable :ref:`sozialv_pflicht_5j <sozialv_pflicht_5j>`.
    anwartschaftszeit
        See basic input variable :ref:`anwartschaftszeit <anwartschaftszeit>`.
    m_durchg_alg1_bezug
        See basic input variable :ref:`m_durchg_alg1_bezug <m_durchg_alg1_bezug>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    nach_alter = piecewise_polynomial(
        alter,
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
        sozialv_pflicht_5j,
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
        out = max(anspruchsdauer_gesamt - m_durchg_alg1_bezug, 0)
    else:
        out = 0

    return out


def arbeitsl_geld_berechtigt(  # noqa: PLR0913
    alter: int,
    arbeitssuchend: bool,
    arbeitsl_geld_restl_anspruchsd: int,
    arbeitsstunden_w: float,
    arbeitsl_geld_params: dict,
    ges_rente_regelaltersgrenze: float,
) -> bool:
    """Check eligibility for unemployment benefit.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    arbeitssuchend
        See basic input variable :ref:`arbeitssuchend <arbeitssuchend>`.
    arbeitsl_geld_restl_anspruchsd
        See :func:`arbeitsl_geld_restl_anspruchsd`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.

    Returns
    -------

    """
    regelaltersgrenze = ges_rente_regelaltersgrenze

    out = (
        arbeitssuchend
        and (arbeitsl_geld_restl_anspruchsd > 0)
        and (alter < regelaltersgrenze)
        and (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )

    return out


def arbeitsl_geld_eink_vorj_proxy_m(
    _ges_rentenv_beitr_bemess_grenze_m: float,
    elterngeld_bruttolohn_vor_geburt_m: float,
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
    elterngeld_bruttolohn_vor_geburt_m
        See basic input variable :ref:`elterngeld_bruttolohn_vor_geburt_m <elterngeld_bruttolohn_vor_geburt_m>`.
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
        elterngeld_bruttolohn_vor_geburt_m, _ges_rentenv_beitr_bemess_grenze_m
    )

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = arbeitsl_geld_params["sozialv_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    # Caution: currently wrong calculation due to
    # 12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"] not being
    # the same as zu versteuerndes einkommen
    # waiting for PR Lohnsteuer #150 to be merged to correct this problem
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
