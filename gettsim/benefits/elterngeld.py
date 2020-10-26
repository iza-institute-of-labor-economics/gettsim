"""This module provides functions to compute parental leave benefits (Elterngeld)."""
import numpy as np
import pandas as pd

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif
from gettsim.typing import BoolSeries
from gettsim.typing import DateTimeSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def elterngeld_m_tu(elterngeld_m: FloatSeries, tu_id: IntSeries) -> FloatSeries:
    """

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
    """

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
    anz_mehrlinge_bonus: FloatSeries,
    elterngeld_params: dict,
) -> FloatSeries:
    """Calculate elterngeld given the relevant wage and the eligibility for bonuses.

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
    anz_mehrlinge_bonus
        See :func:`anz_mehrlinge_bonus`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    alternative_elterngeld = (
        elterngeld_eink_erlass.clip(
            lower=elterngeld_params["elterngeld_mindestbetrag"],
            upper=elterngeld_params["elterngeld_höchstbetrag"],
        )
        + geschw_bonus
        + anz_mehrlinge_bonus
    )

    data = np.where(
        (elterngeld_eink_relev < 0) | ~elternzeit_anspruch, 0, alternative_elterngeld
    )

    return pd.Series(index=elterngeld_eink_relev.index, data=data)


def proxy_eink_vorj_elterngeld(
    beitr_bemess_grenze_rentenv: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    elterngeld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> FloatSeries:
    """Calculating the claim for benefits depending on previous wage.

    TODO: This function requires `.fillna(0)` at the end. Investigate!

    Parameters
    ----------
    beitr_bemess_grenze_rentenv
        See :func:`beitr_bemess_grenze_rentenv`.
    bruttolohn_vorj_m
        See basic input variable :ref:`bruttolohn_vorj_m <bruttolohn_vorj_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
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
    max_wage = bruttolohn_vorj_m.clip(upper=beitr_bemess_grenze_rentenv)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["elterngeld_soz_vers_pausch"] * max_wage

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

    return (
        (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0).fillna(0)
    )


def date_of_birth(
    geburtsjahr: IntSeries, geburtsmonat: IntSeries, geburtstag: IntSeries
) -> DateTimeSeries:
    """Create date of birth variable.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    geburtstag
        See basic input variable :ref:`geburtstag <geburtstag>`.

    Returns
    -------

    """
    out = pd.to_datetime(
        pd.concat(
            [
                geburtsjahr.rename("year"),
                geburtsmonat.rename("month"),
                geburtstag.rename("day"),
            ],
            axis=1,
        )
    )
    return out


def alter_jüngstes_kind(
    hh_id: IntSeries, date_of_birth: DateTimeSeries, kind: BoolSeries
) -> DateTimeSeries:
    """

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    date_of_birth
        See :func:`geburtstag`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------

    """
    alter_jüngstes_kind = date_of_birth.loc[kind].groupby(hh_id).max()
    # Re-index to get NaT for households without children.
    alter_jüngstes_kind = alter_jüngstes_kind.reindex(index=hh_id.unique())
    # Replace hh_ids with timestamps and re-cast to `datetime64[ns]` if there was no kid
    # which yields object dtype.
    return hh_id.replace(alter_jüngstes_kind).astype("datetime64[ns]")


def jüngstes_kind(
    date_of_birth: DateTimeSeries, alter_jüngstes_kind: DateTimeSeries
) -> BoolSeries:
    """

    Parameters
    ----------
    date_of_birth
        See :func:`date_of_birth`.
    alter_jüngstes_kind
        See :func:`alter_jüngstes_kind`.

    Returns
    -------

    """
    return date_of_birth == alter_jüngstes_kind


def alter_jüngstes_kind_monate(
    hh_id: IntSeries, alter_jüngstes_kind: DateTimeSeries, elterngeld_params: dict
) -> FloatSeries:
    """

    Parameters
    ----------
    hh_id
        See basic input variable :ref:`hh_id <hh_id>`.
    alter_jüngstes_kind
        See :func:`alter_jüngstes_kind`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """
    date = pd.to_datetime(elterngeld_params["datum"])
    age_in_days = date - alter_jüngstes_kind

    # Check was formerly implemented in `check_eligibilities` for elterngeld.
    unborn_children = age_in_days.dt.total_seconds() < 0
    if unborn_children.any():
        hh_ids = hh_id[unborn_children].unique()
        raise ValueError(f"Households with ids {hh_ids} have unborn children.")
    return age_in_days / np.timedelta64(1, "M")


def elternzeit_anspruch(
    hh_id: IntSeries,
    alter_jüngstes_kind_monate: FloatSeries,
    m_elterngeld_mut: IntSeries,
    m_elterngeld_vat: IntSeries,
    m_elterngeld: IntSeries,
    kind: BoolSeries,
    elterngeld_params: dict,
) -> BoolSeries:
    """

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
        (alter_jüngstes_kind_monate <= elterngeld_params["elterngeld_max_monate_paar"])
        .groupby(hh_id)
        .transform("any")
    )

    eligible_consumed = (
        (
            m_elterngeld_mut + m_elterngeld_vat
            < elterngeld_params["elterngeld_max_monate_paar"]
        )
        .groupby(hh_id)
        .transform("any")
    )

    eligible = (
        eligible_age
        & eligible_consumed
        & ~kind
        & (m_elterngeld <= elterngeld_params["elterngeld_max_monate_ind"])
    )

    return eligible


def berechtigt_für_geschw_bonus(
    hh_id: IntSeries,
    geburtsjahr: IntSeries,
    elternzeit_anspruch: BoolSeries,
    elterngeld_params: dict,
) -> BoolSeries:
    """

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
    under_age_three = elterngeld_params["datum"].year - geburtsjahr < 3
    under_age_six = elterngeld_params["datum"].year - geburtsjahr < 6

    bonus = (
        (under_age_three.groupby(hh_id).transform("sum") == 2)
        | (under_age_six.groupby(hh_id).transform("sum") > 2)
    ) & elternzeit_anspruch

    return bonus


def anz_mehrlinge_anspruch(
    hh_id: IntSeries, elternzeit_anspruch: BoolSeries, jüngstes_kind: BoolSeries
) -> IntSeries:
    """

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
    """Calculate the net wage given taxes and social security contributions.


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
    decreases above the second step until elterngeld_prozent_minimum.

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
        elterngeld_eink_relev
        < elterngeld_params["elterngeld_nettoeinkommen_stufen"][1],
        elterngeld_eink_relev
        > elterngeld_params["elterngeld_nettoeinkommen_stufen"][2],
        True,
    ]

    choices = [
        (
            elterngeld_params["elterngeld_nettoeinkommen_stufen"][1]
            - elterngeld_eink_relev
        )
        / elterngeld_params["elterngeld_eink_schritt_korrektur"]
        * elterngeld_params["elterngeld_prozent_korrektur"]
        + elterngeld_params["elterngeld_faktor"],
        (
            elterngeld_params["elterngeld_faktor"]
            - (
                elterngeld_eink_relev
                - elterngeld_params["elterngeld_nettoeinkommen_stufen"][2]
            )
            / elterngeld_params["elterngeld_eink_schritt_korrektur"]
        ).clip(lower=elterngeld_params["elterngeld_prozent_minimum"]),
        elterngeld_params["elterngeld_faktor"],
    ]

    data = np.select(conditions, choices)

    return pd.Series(index=elterngeld_eink_relev.index, data=data)


def elterngeld_eink_erlass(
    elterngeld_eink_relev: FloatSeries, elterngeld_anteil_eink_erlass: FloatSeries
) -> FloatSeries:
    """

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
    """Calculating the bonus for siblings.

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
    return (
        (
            elterngeld_params["elterngeld_geschw_bonus_aufschlag"]
            * elterngeld_eink_erlass
        ).clip(lower=elterngeld_params["elterngeld_geschwister_bonus_minimum"])
        * berechtigt_für_geschw_bonus
    )


def anz_mehrlinge_bonus(
    anz_mehrlinge_anspruch: IntSeries, elterngeld_params: dict
) -> FloatSeries:
    """

    Parameters
    ----------
    anz_mehrlinge_anspruch
        See :func:`anz_mehrlinge_anspruch`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return anz_mehrlinge_anspruch * elterngeld_params["elterngeld_mehrling_bonus"]
