import numpy as np
import pandas as pd

from gettsim.benefits.elterngeld import elterngeld
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif


def elterngeld_m(
    hh_id,
    tu_id,
    p_id,
    kind,
    bruttolohn_m,
    bruttolohn_vorj_m,
    wohnort_ost,
    eink_st_m,
    soli_st_m,
    sozialv_beit_m,
    geburtsjahr,
    geburtsmonat,
    geburtstag,
    m_elterngeld_mut,
    m_elterngeld_vat,
    m_elterngeld,
    jahr,
    proxy_eink_vorj_elterngeld,
    date_of_birth,
    alter_jüngstes_kind,
    alter_jüngstes_kind_tage,
    alter_jüngstes_kind_monate,
    jüngstes_kind,
    elternzeit_anspruch,
    anz_mehrlinge_bonus,
    berechtigt_für_geschw_bonus,
    netto_eink,
    elterngeld_eink_relev,
    elterngeld_anteil_eink_erlass,
    elterngeld_eink_erlass,
    geschw_bonus,
    elterngeld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            kind,
            bruttolohn_m,
            bruttolohn_vorj_m,
            wohnort_ost,
            eink_st_m,
            soli_st_m,
            sozialv_beit_m,
            geburtsjahr,
            geburtsmonat,
            geburtstag,
            m_elterngeld_mut,
            m_elterngeld_vat,
            m_elterngeld,
            jahr,
            proxy_eink_vorj_elterngeld,
            date_of_birth,
            alter_jüngstes_kind,
            alter_jüngstes_kind_tage,
            alter_jüngstes_kind_monate,
            jüngstes_kind,
            elternzeit_anspruch,
            anz_mehrlinge_bonus,
            berechtigt_für_geschw_bonus,
            netto_eink,
            elterngeld_eink_relev,
            elterngeld_anteil_eink_erlass,
            elterngeld_eink_erlass,
            geschw_bonus,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=["elterngeld_m"],
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["elterngeld_m"]


def proxy_eink_vorj_elterngeld(
    beitr_bemess_grenze_rentenv,
    wohnort_ost,
    bruttolohn_vorj_m,
    elterngeld_params,
    eink_st_params,
    eink_st_abzuege_params,
    soli_st_params,
    soz_vers_beitr_params,
):
    """Calculating the claim for benefits depending on previous wage.

    TODO: This function requires `.fillna(0)` at the end. Investigate!

    """
    # Relevant wage is capped at the contribution thresholds
    max_wage = bruttolohn_vorj_m.clip(lower=None, upper=beitr_bemess_grenze_rentenv)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["elterngeld_soz_vers_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = st_tarif(
        12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"],
        eink_st_params,
    )

    prox_soli = piecewise_polynomial(
        prox_tax,
        lower_thresholds=soli_st_params["soli_st"]["lower_thresholds"],
        upper_thresholds=soli_st_params["soli_st"]["upper_thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return (
        (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0).fillna(0)
    )


def date_of_birth(geburtsjahr, geburtsmonat, geburtstag):
    return pd.to_datetime(
        pd.concat(
            [
                geburtsjahr.rename("year"),
                geburtsmonat.rename("month"),
                geburtstag.rename("day"),
            ],
            axis=1,
        )
    )


def alter_jüngstes_kind(hh_id, date_of_birth, kind):
    alter_jüngstes_kind = date_of_birth.loc[kind].groupby(hh_id).max()
    # Re-index to get NaT for households without children.
    alter_jüngstes_kind = alter_jüngstes_kind.reindex(index=hh_id.unique())
    # Replace hh_ids with timestamps and re-cast to `datetime64[ns]` if there was no kid
    # which yields object dtype.
    return hh_id.replace(alter_jüngstes_kind).astype("datetime64[ns]")


def jüngstes_kind(date_of_birth, alter_jüngstes_kind):
    return date_of_birth == alter_jüngstes_kind


def alter_jüngstes_kind_tage(hh_id, alter_jüngstes_kind, elterngeld_params):
    """Calculate the age of the youngest child in days."""
    date = pd.to_datetime(elterngeld_params["datum"])
    age_in_days = date - alter_jüngstes_kind

    # Check was formerly implemented in `check_eligibilities` for elterngeld.
    unborn_children = age_in_days.dt.total_seconds() < 0
    if unborn_children.any():
        hh_ids = hh_id[unborn_children].unique()
        raise ValueError(f"Households with ids {hh_ids} have unborn children.")

    return age_in_days


def alter_jüngstes_kind_monate(alter_jüngstes_kind_tage):
    return alter_jüngstes_kind_tage / np.timedelta64(1, "M")


def elternzeit_anspruch(
    hh_id,
    alter_jüngstes_kind_monate,
    m_elterngeld_mut,
    m_elterngeld_vat,
    kind,
    m_elterngeld,
    elterngeld_params,
):
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
    hh_id, geburtsjahr, elternzeit_anspruch, elterngeld_params
):
    under_age_three = elterngeld_params["jahr"] - geburtsjahr < 3
    under_age_six = elterngeld_params["jahr"] - geburtsjahr < 6

    bonus = (
        (under_age_three.groupby(hh_id).transform("sum") == 2)
        | (under_age_six.groupby(hh_id).transform("sum") > 2)
    ) & elternzeit_anspruch

    return bonus


def anz_mehrlinge_bonus(hh_id, elternzeit_anspruch, jüngstes_kind):
    mehrlinge = jüngstes_kind.groupby(hh_id).transform("sum")
    return elternzeit_anspruch * (mehrlinge - 1)


def netto_eink(bruttolohn_m, eink_st_m, soli_st_m, sozialv_beit_m):
    """Calculate the net wage given taxes and social security contributions."""
    return bruttolohn_m - eink_st_m - soli_st_m - sozialv_beit_m


def elterngeld_eink_relev(proxy_eink_vorj_elterngeld, netto_eink):
    """Calculating the relevant wage for the calculation of elterngeld.

    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.

    """
    return proxy_eink_vorj_elterngeld - netto_eink


def elterngeld_anteil_eink_erlass(elterngeld_eink_relev, elterngeld_params):
    """Calculate the share of net income which is reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until elterngeld_prozent_minimum.

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


def elterngeld_eink_erlass(elterngeld_eink_relev, elterngeld_anteil_eink_erlass):
    return elterngeld_eink_relev * elterngeld_anteil_eink_erlass


def geschw_bonus(
    elterngeld_eink_erlass, berechtigt_für_geschw_bonus, elterngeld_params
):
    """ Calculating the bonus for siblings.

    According to § 2a parents of siblings get a bonus.

    """
    return (
        (
            elterngeld_params["elterngeld_geschw_bonus_aufschlag"]
            * elterngeld_eink_erlass
        ).clip(lower=elterngeld_params["elterngeld_geschwister_bonus_minimum"])
        * berechtigt_für_geschw_bonus
    )


# def elterngeld_m
