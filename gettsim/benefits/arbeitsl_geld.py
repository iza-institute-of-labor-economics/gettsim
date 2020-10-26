"""Functions to compute unemployment benefits (Arbeitslosengeld).

"""
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_m_tu(arbeitsl_geld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """

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
    """

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
    berechtigt_für_arbeitsl_geld: BoolSeries,
    proxy_eink_vorj_arbeitsl_geld: FloatSeries,
    arbeitsl_geld_params: dict,
) -> FloatSeries:
    """

    Parameters
    ----------
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    berechtigt_für_arbeitsl_geld
        See :func:`berechtigt_für_arbeitsl_geld`.
    proxy_eink_vorj_arbeitsl_geld
        See :func:`proxy_eink_vorj_arbeitsl_geld`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    arbeitsl_geld_satz = (tu_id.replace(anz_kinder_tu) == 0).replace(
        {
            True: arbeitsl_geld_params["arbeitsl_geld_satz_ohne_kinder"],
            False: arbeitsl_geld_params["arbeitsl_geld_satz_mit_kindern"],
        }
    )

    arbeitsl_geld_m = berechtigt_für_arbeitsl_geld.astype(float) * 0

    arbeitsl_geld_m[berechtigt_für_arbeitsl_geld] = (
        proxy_eink_vorj_arbeitsl_geld * arbeitsl_geld_satz
    )

    return arbeitsl_geld_m


def monate_arbeitsl(
    arbeitsl_lfdj_m: IntSeries, arbeitsl_vorj_m: IntSeries, arbeitsl_vor2j_m: IntSeries
) -> IntSeries:
    """

    Parameters
    ----------
    arbeitsl_lfdj_m
        See basic input variable :ref:`arbeitsl_lfdj_m <arbeitsl_lfdj_m>`.
    arbeitsl_vorj_m
        See basic input variable :ref:`arbeitsl_vorj_m <arbeitsl_vorj_m>`.
    arbeitsl_vor2j_m
        See basic input variable :ref:`arbeitsl_vor2j_m <arbeitsl_vor2j_m>`.

    Returns
    -------

    """
    return arbeitsl_lfdj_m + arbeitsl_vorj_m + arbeitsl_vor2j_m


def berechtigt_für_arbeitsl_geld(
    monate_arbeitsl: IntSeries,
    alter: IntSeries,
    ges_rente_m: FloatSeries,
    arbeitsstunden_w: FloatSeries,
    arbeitsl_geld_params: dict,
) -> BoolSeries:
    """Check eligibility for unemployment benefits.

    Different rates for parent and non-parents. Take into account actual wages. There
    are different replacement rates depending on presence of children

    Parameters
    ----------
    monate_arbeitsl
        See :func:`monate_arbeitsl`.
    alter
        See basic input variable :ref:`alter <alter>`.
    ges_rente_m
        See basic input variable :ref:`ges_rente_m <ges_rente_m>`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    arbeitsl_geld_params
        See params documentation :ref:`arbeitsl_geld_params <arbeitsl_geld_params>`.

    Returns
    -------

    """
    return (
        (1 <= monate_arbeitsl)
        & (monate_arbeitsl <= 12)
        & (alter < 65)
        & (ges_rente_m == 0)
        & (arbeitsstunden_w < arbeitsl_geld_params["arbeitsl_geld_stundengrenze"])
    )


def proxy_eink_vorj_arbeitsl_geld(
    beitr_bemess_grenze_rentenv: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    arbeitsl_geld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> FloatSeries:
    """Calculating the claim for benefits depending on previous wage.

    Parameters
    ----------
    beitr_bemess_grenze_rentenv
        See :func:`beitr_bemess_grenze_rentenv`.
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
    max_wage = bruttolohn_vorj_m.clip(lower=None, upper=beitr_bemess_grenze_rentenv)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = arbeitsl_geld_params["soz_vers_pausch_arbeitsl_geld"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = st_tarif(
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

    return (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0)


def beitr_bemess_grenze_rentenv(
    wohnort_ost: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    out = wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
        }
    )
    return out.astype(float)
