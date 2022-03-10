"""This module provides functions to compute parental leave benefits (Elterngeld)."""
import numpy as np
import pandas as pd

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def elterngeld_m_tu(elterngeld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """Aggregate parental leave benefit on tax unit level.

    Parameters
    ----------
    elterngeld_m
        See :func:`elterngeld_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return elterngeld_m.groupby(tu_id).sum()


def elterngeld_m_hh(elterngeld_m: FloatSeries, hh_id: IntSeries) -> FloatSeries:
    """Aggregate parental leave benefit on household level.

    Parameters
    ----------
    elterngeld_m
        See :func:`elterngeld_m`.
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    Returns
    -------

    """
    return elterngeld_m.groupby(hh_id).sum()


def elterngeld_m(
    elterngeld_eink_relev: FloatSeries,
    elternzeit_anspruch: BoolSeries,
    elterngeld_eink_erlass: FloatSeries,
    geschw_bonus: FloatSeries,
    mehrlinge_bonus: FloatSeries,
    elterngeld_params: dict,
) -> FloatSeries:
    """Calculate parental leave benefit (elterngeld).

    For the calculation, the relevant wage and the eligibility for bonuses is needed.

    Parameters
    ----------
    elterngeld_eink_relev
        See :func:`elterngeld_eink_relev`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    elterngeld_eink_erlass
        See :func:`elterngeld_eink_erlass`.
    geschw_bonus
        See :func:`geschw_bonus`.
    mehrlinge_bonus
        See :func:`mehrlinge_bonus`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    alternative_elterngeld = (
        elterngeld_eink_erlass.clip(
            lower=elterngeld_params["mindestbetrag"],
            upper=elterngeld_params["höchstbetrag"],
        )
        + geschw_bonus
        + mehrlinge_bonus
    )

    data = np.where(
        (elterngeld_eink_relev < 0) | ~elternzeit_anspruch, 0, alternative_elterngeld
    )

    return pd.Series(index=elterngeld_eink_relev.index, data=data)


def proxy_eink_vorj_elterngeld(
    _ges_rentenv_beitr_bemess_grenze_m: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    elterngeld_params: dict,
    eink_st_params: dict,
    eink_st_abzüge_params: dict,
    soli_st_params: dict,
) -> FloatSeries:
    """Calculating the claim for benefits depending on previous wage.

    TODO: This function requires `.fillna(0)` at the end. Investigate!

    Parameters
    ----------
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.
    bruttolohn_vorj_m
        See basic input variable :ref:`bruttolohn_vorj_m <bruttolohn_vorj_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
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
    max_wage = bruttolohn_vorj_m.clip(upper=_ges_rentenv_beitr_bemess_grenze_m)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["soz_vers_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = _eink_st_tarif(
        (12 * max_wage - eink_st_abzüge_params["werbungskostenpauschale"]).clip(
            lower=0
        ),
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


def elternzeit_anspruch(
    hh_id: IntSeries,
    alter_jüngstes_kind_monate: FloatSeries,
    m_elterngeld_mut: IntSeries,
    m_elterngeld_vat: IntSeries,
    m_elterngeld: IntSeries,
    kind: BoolSeries,
    elterngeld_params: dict,
) -> BoolSeries:
    """Check parental leave eligibility.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    alter_jüngstes_kind_monate
        See :func:`alter_jüngstes_kind_monate`.
    m_elterngeld_mut
        See basic input variable :ref:`m_elterngeld_mut <m_elterngeld_mut>`.
    m_elterngeld_vat
        See basic input variable :ref:`m_elterngeld_vat <m_elterngeld_vat>`.
    m_elterngeld
        See basic input variable :ref:`m_elterngeld <m_elterngeld>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    eligible_age = (
        (alter_jüngstes_kind_monate <= elterngeld_params["max_monate_paar"])
        .groupby(hh_id)
        .transform("any")
    )

    eligible_consumed = (
        (m_elterngeld_mut + m_elterngeld_vat < elterngeld_params["max_monate_paar"])
        .groupby(hh_id)
        .transform("any")
    )

    eligible = (
        eligible_age
        & eligible_consumed
        & ~kind
        & (m_elterngeld <= elterngeld_params["max_monate_ind"])
    )

    return eligible


def berechtigt_für_geschw_bonus(
    hh_id: IntSeries,
    geburtsjahr: IntSeries,
    elternzeit_anspruch: BoolSeries,
    elterngeld_params: dict,
) -> BoolSeries:
    """Check for sibling bonus on parental leave benefit.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    kleinkinder = (
        elterngeld_params["datum"].year - geburtsjahr
        < list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].keys())[0]
    )
    vorschulkinder = (
        elterngeld_params["datum"].year - geburtsjahr
        < list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].keys())[1]
    )

    bonus = (
        (
            kleinkinder.groupby(hh_id).transform("sum")
            == list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())[0]
        )
        | (
            vorschulkinder.groupby(hh_id).transform("sum")
            >= list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())[1]
        )
    ) & elternzeit_anspruch

    return bonus


def anz_mehrlinge_anspruch(
    hh_id: IntSeries, elternzeit_anspruch: BoolSeries, jüngstes_kind: BoolSeries
) -> IntSeries:
    """Check for multiple bonus on parental leave benefit.

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    jüngstes_kind
        See :func:`jüngstes_kind`.

    Returns
    -------

    """
    mehrlinge = jüngstes_kind.groupby(hh_id).transform("sum")
    return elternzeit_anspruch * (mehrlinge - 1)


def nettolohn_m(
    bruttolohn_m: FloatSeries,
    tu_id: IntSeries,
    eink_st_tu: FloatSeries,
    soli_st_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    sozialv_beitr_m: FloatSeries,
) -> FloatSeries:
    """Calculate the net wage.

    Taxes and social insurance contributions are needed for the calculation.


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    eink_st_tu
        See :func:`eink_st_tu`.
    soli_st_tu
        See :func:`soli_st_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.

    Returns
    -------

    """
    return (
        bruttolohn_m
        - tu_id.replace((eink_st_tu / anz_erwachsene_tu) / 12)
        - tu_id.replace((soli_st_tu / anz_erwachsene_tu) / 12)
        - sozialv_beitr_m
    ).clip(lower=0)


def elterngeld_eink_relev(
    proxy_eink_vorj_elterngeld: FloatSeries, nettolohn_m: FloatSeries
) -> FloatSeries:
    """Calculating the relevant wage for the calculation of elterngeld.

    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.


    Parameters
    ----------
    proxy_eink_vorj_elterngeld
        See :func:`proxy_eink_vorj_elterngeld`.
    nettolohn_m
        See :func:`nettolohn_m`.

    Returns
    -------


    """
    return proxy_eink_vorj_elterngeld - nettolohn_m


def elterngeld_anteil_eink_erlass(
    elterngeld_eink_relev: FloatSeries, elterngeld_params: dict
) -> FloatSeries:
    """Calculate the share of net income which is reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    Parameters
    ----------
    elterngeld_eink_relev
        See :func:`elterngeld_eink_relev`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """
    conditions = [
        elterngeld_eink_relev < elterngeld_params["nettoeinkommen_stufen"][1],
        elterngeld_eink_relev > elterngeld_params["nettoeinkommen_stufen"][2],
        True,
    ]

    choices = [
        (elterngeld_params["nettoeinkommen_stufen"][1] - elterngeld_eink_relev)
        / elterngeld_params["eink_schritt_korrektur"]
        * elterngeld_params["prozent_korrektur"]
        + elterngeld_params["faktor"],
        (
            elterngeld_params["faktor"]
            - (elterngeld_eink_relev - elterngeld_params["nettoeinkommen_stufen"][2])
            / elterngeld_params["eink_schritt_korrektur"]
        ).clip(lower=elterngeld_params["prozent_minimum"]),
        elterngeld_params["faktor"],
    ]

    data = np.select(conditions, choices)

    return pd.Series(index=elterngeld_eink_relev.index, data=data)


def elterngeld_eink_erlass(
    elterngeld_eink_relev: FloatSeries, elterngeld_anteil_eink_erlass: FloatSeries
) -> FloatSeries:
    """Calculate base parental leave benefit.

    Parameters
    ----------
    elterngeld_eink_relev
        See :func:`elterngeld_eink_relev`.
    elterngeld_anteil_eink_erlass
        See :func:`elterngeld_anteil_eink_erlass`.

    Returns
    -------

    """
    return elterngeld_eink_relev * elterngeld_anteil_eink_erlass


def geschw_bonus(
    elterngeld_eink_erlass: FloatSeries,
    berechtigt_für_geschw_bonus: BoolSeries,
    elterngeld_params: dict,
) -> FloatSeries:
    """Calculate the bonus for siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    elterngeld_eink_erlass
        See :func:`elterngeld_eink_erlass`.
    berechtigt_für_geschw_bonus
        See :func:`berechtigt_für_geschw_bonus`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (elterngeld_params["geschw_bonus_aufschlag"] * elterngeld_eink_erlass).clip(
        lower=elterngeld_params["geschw_bonus_minimum"]
    ) * berechtigt_für_geschw_bonus


def mehrlinge_bonus(
    anz_mehrlinge_anspruch: IntSeries, elterngeld_params: dict
) -> FloatSeries:
    """Calculate the bonus for multiples.

    Parameters
    ----------
    anz_mehrlinge_anspruch
        See :func:`anz_mehrlinge_anspruch`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return anz_mehrlinge_anspruch * elterngeld_params["mehrlingbonus"]
