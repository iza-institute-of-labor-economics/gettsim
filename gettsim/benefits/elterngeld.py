import datetime

import numpy as np
from dateutil import relativedelta

from gettsim.benefits.arbeitslosengeld import proxy_net_wage_last_year
from gettsim.tax_transfer import _apply_tax_transfer_func


def elterngeld(
    household,
    params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    household = check_eligibilities(household, params)

    in_cols = list(household.columns.values)
    # Everything was already initialized
    out_cols = []
    household.loc[household["elternzeit_anspruch"], :] = _apply_tax_transfer_func(
        household[household["elternzeit_anspruch"]],
        tax_func=calc_elterngeld,
        level=["hid", "tu_id", "pid"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    household.loc[~household["elternzeit_anspruch"], ["elterngeld"]] = 0

    return household


def calc_elterngeld(
    person,
    params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """ Calculating elterngeld given the relevant wage and the eligibility on sibling
    bonus.

    """
    considered_wage = calc_considered_wage(
        person,
        params,
        soz_vers_beitr_params,
        e_st_abzuege_params,
        e_st_params,
        soli_st_params,
    )
    if considered_wage < 0:
        person["elterngeld"] = 0
    else:
        payed_percentage = calc_elterngeld_percentage(considered_wage, params)

        elterngeld_calc = considered_wage * payed_percentage

        prelim_elterngeld = max(
            min(elterngeld_calc, params["elgmax"]), params["elgmin"]
        )
        if person["geschw_bonus"]:
            prelim_elterngeld += calc_geschw_bonus(elterngeld_calc, params)
        prelim_elterngeld += person["num_mehrlinge"] * params["mehrling_bonus"]
        person["elterngeld"] = prelim_elterngeld

    return person


def calc_considered_wage(
    person,
    params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """ Calculating the relevant wage for the calculation of elterngeld.


    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.
    """
    # Beitragsbemessungsgrenze differs in east and west germany
    westost = "o" if person["east"] else "w"

    net_wage_last_year = proxy_net_wage_last_year(
        person,
        e_st_params,
        soli_st_params,
        beit_bem_grenz=soz_vers_beitr_params[f"rvmaxek{westost}"],
        werbungs_pausch=e_st_abzuege_params["werbung"],
        soz_vers_pausch=params["soz_vers_pausch"],
    )

    current_net_wage = calc_net_wage(person)

    return net_wage_last_year - current_net_wage


def calc_elterngeld_percentage(considered_wage, params):
    """ This function calculates the percentage share of net income, which is
    reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below elg_st_1 and decreases
    above elg_st_2 until perc_deduct_limit.
    """
    if considered_wage < params["elg_st_1"]:
        wag_diff = params["elg_st_1"] - considered_wage

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = params["elgfaktor"] + number_steps * params["elg_perc_correct"]

    elif considered_wage > params["elg_st_2"]:
        wag_diff = considered_wage - params["elg_st_2"]

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = max(
            params["elgfaktor"] - number_steps * params["elg_perc_correct"],
            params["perc_deduct_limit"],
        )

    else:
        percentage = params["elgfaktor"]

    return percentage


def calc_net_wage(person):
    """ Calculating the net wage of any person given taxes and social security
    contributions.

    """
    net_wage = (
        person["m_wage"] - person["incometax"] - person["soli"] - person["svbeit"]
    )

    return net_wage


def calc_geschw_bonus(elterngeld_calc, params):
    """ Calculating the bonus for siblings.


    According to § 2a parents of siblings get a bonus.
    """
    bonus_calc = params["elg_geschw_bonus_share"] * elterngeld_calc
    bonus = max(
        min(bonus_calc, params["elg_geschw_bonus_max"]), params["elg_geschw_bonus_min"]
    )
    return bonus


def check_eligibilities(household, params):
    """Check if a parent is eligible for elterngeld. If so, then also check if it is
    eligible for multiple or sibling bonus.

    """
    household["elternzeit_anspruch"] = False
    household["geschw_bonus"] = False
    household["num_mehrlinge"] = 0

    children = household[household["child"]]
    # Are there any children
    if len(children) > 0:
        youngest_child = children[
            (children["byear"] == np.max(children["byear"]))
            & (children["bmonth"] == np.max(children["bmonth"]))
        ]
        # Get the birthdate of the youngest child(If "Mehrlinge", then just take one)
        birth_date = datetime.date(
            day=youngest_child["bday"].iloc[0].astype(int),
            month=youngest_child["bmonth"].iloc[0].astype(int),
            year=youngest_child["byear"].iloc[0].astype(int),
        )
        age_youngest_child = relativedelta.relativedelta(params["date"], birth_date)
        # Age in months
        age_months = age_youngest_child.years * 12 + age_youngest_child.months
        if (age_months < 0) or (age_months == 0 & age_youngest_child.days < 0):
            raise ValueError(f"Individual {youngest_child.pid.iloc[0]} not born yet.")
        # The child has to be below the 14th month
        eligible_age = age_months <= params["max_joint_months"]
        # The parents can only claim up to 14 month elterngeld
        eligible_consumed = (
            youngest_child["elterngeld_mon_mut"].iloc[0]
            + youngest_child["elterngeld_mon_vat"].iloc[0]
        ) <= 14
        # Parents are eligible for elterngeld, if the child is young enough and they
        # have not yet consumed all elterngeld months.
        if eligible_age & eligible_consumed:
            # Each parent can't claim more than 12 month
            eligible = ~household["child"] & (
                household["elterngeld_mon"] <= params["max_months"]
            )

            household.loc[eligible, "elternzeit_anspruch"] = True

            if (len(children[(params["year"] - children["byear"]) < 3]) == 2) | (
                len(children[(params["year"] - children["byear"]) < 6]) > 2
            ):
                household.loc[eligible, "geschw_bonus"] = True
                household.loc[eligible, "num_mehrlinge"] = len(youngest_child) - 1

    return household
