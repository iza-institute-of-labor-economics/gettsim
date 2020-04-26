import datetime

import numpy as np
from dateutil import relativedelta

from gettsim.benefits.arbeitsl_geld import proxy_net_wage_last_year
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func


def elterngeld(
    household,
    params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    household = check_eligibilities(household, params)

    in_cols = list(household.columns.values)
    # Everything was already initialized
    out_cols = []
    household.loc[household["elternzeit_anspruch"], :] = apply_tax_transfer_func(
        household[household["elternzeit_anspruch"]],
        tax_func=calc_elterngeld,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    household.loc[~household["elternzeit_anspruch"], ["elterngeld_m"]] = 0

    return household


def calc_elterngeld(
    person,
    params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    """ Calculating elterngeld given the relevant wage and the eligibility on sibling
    bonus.

    """
    considered_wage = calc_considered_wage(
        person,
        params,
        soz_vers_beitr_params,
        eink_st_abzuege_params,
        eink_st_params,
        soli_st_params,
    )
    if considered_wage < 0:
        person["elterngeld_m"] = 0
    else:
        payed_percentage = calc_elterngeld_percentage(considered_wage, params)

        elterngeld_calc = considered_wage * payed_percentage

        prelim_elterngeld = max(
            min(elterngeld_calc, params["elterngeld_höchstbetrag"]),
            params["elterngeld_mindestbetrag"],
        )
        if person["geschw_bonus"]:
            prelim_elterngeld += calc_geschw_bonus(elterngeld_calc, params)
        prelim_elterngeld += (
            person["anz_mehrlinge_bonus"] * params["elterngeld_mehrling_bonus"]
        )
        person["elterngeld_m"] = prelim_elterngeld

    return person


def calc_considered_wage(
    person,
    params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    """ Calculating the relevant wage for the calculation of elterngeld.


    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.
    """
    # Beitragsbemessungsgrenze differs in east and west germany
    westost = "o" if person["wohnort_ost"] else "w"

    net_wage_last_year = proxy_net_wage_last_year(
        person,
        eink_st_params,
        soli_st_params,
        beit_bem_grenz=soz_vers_beitr_params[f"rvmaxek{westost}"],
        werbungs_pausch=eink_st_abzuege_params["werbungskostenpauschale"],
        sozial_versich_pauschale_alg=params["elterngeld_soz_versich_pauschale"],
    )

    current_net_wage = calc_net_wage(person)

    return net_wage_last_year - current_net_wage


def calc_elterngeld_percentage(considered_wage, params):
    """ This function calculates the percentage share of net income, which is
    reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and decreases
    above the second step until elterngeld_prozent_minimum.
    """
    if considered_wage < params["elterngeld_nettoeinkommen_stufen"][1]:
        wag_diff = params["elterngeld_nettoeinkommen_stufen"][1] - considered_wage

        number_steps = wag_diff / params["elterngeld_prozent_korrektur"]
        percentage = (
            params["elterngeld_faktor"]
            + number_steps * params["elterngeld_prozent_korrektur"]
        )

    elif considered_wage > params["elterngeld_nettoeinkommen_stufen"][2]:
        wag_diff = considered_wage - params["elterngeld_nettoeinkommen_stufen"][2]

        number_steps = wag_diff / params["elterngeld_prozent_korrektur"]
        percentage = max(
            params["elterngeld_faktor"]
            - number_steps * params["elterngeld_prozent_korrektur"],
            params["elterngeld_prozent_minimum"],
        )

    else:
        percentage = params["elterngeld_faktor"]

    return percentage


def calc_net_wage(person):
    """ Calculating the net wage of any person given taxes and social security
    contributions.

    """
    net_wage = (
        person["bruttolohn_m"]
        - person["eink_st_m"]
        - person["soli_st_m"]
        - person["sozialv_beit_m"]
    )

    return net_wage


def calc_geschw_bonus(elterngeld_calc, params):
    """ Calculating the bonus for siblings.


    According to § 2a parents of siblings get a bonus.
    """
    bonus_calc = params["elterngeld_geschw_bonus_aufschlag"] * elterngeld_calc
    bonus = max(bonus_calc, params["elterngeld_geschwister_bonus_minimum"],)
    return bonus


def check_eligibilities(household, params):
    """Check if a parent is eligible for elterngeld. If so, then also check if it is
    eligible for multiple or sibling bonus.

    """
    household["elternzeit_anspruch"] = False
    household["geschw_bonus"] = False
    household["anz_mehrlinge_bonus"] = 0

    children = household[household["kind"]]
    # Are there any children
    if len(children) > 0:
        youngest_child = children[
            (children["geburtsjahr"] == np.max(children["geburtsjahr"]))
            & (children["geburtsmonat"] == np.max(children["geburtsmonat"]))
        ]
        # Get the birthdate of the youngest child(If "Mehrlinge", then just take one)
        birth_date = datetime.date(
            day=youngest_child["geburtstag"].iloc[0].astype(int),
            month=youngest_child["geburtsmonat"].iloc[0].astype(int),
            year=youngest_child["geburtsjahr"].iloc[0].astype(int),
        )
        age_youngest_child = relativedelta.relativedelta(params["datum"], birth_date)
        # Age in months
        age_months = age_youngest_child.years * 12 + age_youngest_child.months
        if (age_months < 0) or (age_months == 0 & age_youngest_child.days < 0):
            raise ValueError(f"Individual {youngest_child.p_id.iloc[0]} not born yet.")
        # The child has to be below the 14th month
        eligible_age = age_months <= params["elterngeld_max_monate_paar"]
        # The parents can only claim up to 14 month elterngeld
        eligible_consumed = (
            youngest_child["m_elterngeld_mut"].iloc[0]
            + youngest_child["m_elterngeld_vat"].iloc[0]
        ) <= 14
        # Parents are eligible for elterngeld, if the child is young enough and they
        # have not yet consumed all elterngeld months.
        if eligible_age & eligible_consumed:
            # Each parent can't claim more than 12 month
            eligible = ~household["kind"] & (
                household["m_elterngeld"] <= params["elterngeld_max_monate_ind"]
            )

            household.loc[eligible, "elternzeit_anspruch"] = True

            if (len(children[(params["jahr"] - children["geburtsjahr"]) < 3]) == 2) | (
                len(children[(params["jahr"] - children["geburtsjahr"]) < 6]) > 2
            ):
                household.loc[eligible, "geschw_bonus"] = True
                # Checking if there are multiples
                if len(youngest_child) > 0:
                    household.loc[eligible, "anz_mehrlinge_bonus"] = (
                        len(youngest_child) - 1
                    )

    return household
