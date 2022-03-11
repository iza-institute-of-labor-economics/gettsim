"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_m_tu(arbeitsl_geld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate unemployment benefit on tax unit level.

    Parameters
    ----------
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return arbeitsl_geld_m.groupby(tu_id).sum()


def arbeitsl_geld_m_hh(arbeitsl_geld_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate unemployment benefit on household level.

    Parameters
    ----------
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.

    Returns
    -------

    """
    return arbeitsl_geld_m.groupby(hh_id).sum()


def arbeitsl_geld_m(
    tu_id: IntSeries,
    anz_kinder_tu: IntSeries,
    arbeitsl_geld_berechtigt: BoolSeries,
    arbeitsl_geld_eink_vorj_proxy: FloatSeries,
    arbeitsl_geld_params: dict,
) -> FloatSeries:
    """Calculate unemployment benefit.

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
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
    arbeitsl_geld_satz = (tu_id.replace(anz_kinder_tu) == 0).replace(
        {
            True: arbeitsl_geld_params["satz_ohne_kinder"],
            False: arbeitsl_geld_params["satz_mit_kindern"],
        }
    )

    arbeitsl_geld_m = arbeitsl_geld_berechtigt.astype(float) * 0

    arbeitsl_geld_m[arbeitsl_geld_berechtigt] = (
        arbeitsl_geld_eink_vorj_proxy * arbeitsl_geld_satz
    )

    return arbeitsl_geld_m


def arbeitsl_monate_gesamt(
    arbeitsl_monate_lfdj: IntSeries,
    arbeitsl_monate_vorj: IntSeries,
    arbeitsl_monate_v2j: IntSeries,
) -> IntSeries:
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
    arbeitsl_monate_gesamt: IntSeries,
    alter: IntSeries,
    sum_ges_rente_priv_rente_m: FloatSeries,
    arbeitsstunden_w: FloatSeries,
    arbeitsl_geld_params: dict,
) -> BoolSeries:
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
    return (
        (
            arbeitsl_monate_gesamt
            <= arbeitsl_geld_params["dauer_auszahlung"]["max_dauer"]
        )
        & (alter < arbeitsl_geld_params["altersgrenze"]["alter"])
        & (sum_ges_rente_priv_rente_m == 0)
        & (arbeitsstunden_w < arbeitsl_geld_params["stundengrenze"])
    )


def arbeitsl_geld_eink_vorj_proxy(
    _ges_rentenv_beitr_bemess_grenze_m: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    arbeitsl_geld_params: dict,
    eink_st_params: dict,
    eink_st_abzüge_params: dict,
    soli_st_params: dict,
) -> FloatSeries:
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
    max_wage = bruttolohn_vorj_m.clip(
        lower=None, upper=_ges_rentenv_beitr_bemess_grenze_m
    )

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

    return (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0)
