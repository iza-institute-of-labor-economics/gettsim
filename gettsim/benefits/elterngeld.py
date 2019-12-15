from gettsim.benefits.arbeitslosengeld import proxy_net_wage_last_year


def elt_geld(
    person,
    params,
    arbeitsl_geld_params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    if person["elt_zeit"]:

        considered_wage = calc_consideraded_wage(
            person,
            arbeitsl_geld_params,
            soz_vers_beitr_params,
            e_st_abzuege_params,
            e_st_params,
            soli_st_params,
        )

        if considered_wage < 0:
            person["elt_geld"] = 0

        else:

            person["elt_geld"] = calc_elt_geld(person, considered_wage, params)

    else:
        person["elt_geld"] = 0

    return person


def calc_elt_geld(person, considered_wage, params):
    """ Calculating elterngeld given the relevant wage and the eligibility on sibling
    bonus.

    """
    payed_percentage = calc_elterngeld_percentage(considered_wage, params)

    elt_geld_calc = considered_wage * payed_percentage

    if person["geschw_bonus"]:
        elt_geld_calc += calc_geschw_bonus(elt_geld_calc, params)

    return max(min(elt_geld_calc, params["elgmax"]), params["elgmin"])


def calc_consideraded_wage(
    person,
    arbeitsl_geld_params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """ Calculating the relevant wage for the calculation of elterngeld.


    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.
    """
    net_wage_last_year = proxy_net_wage_last_year(
        person,
        arbeitsl_geld_params,
        soz_vers_beitr_params,
        e_st_abzuege_params,
        e_st_params,
        soli_st_params,
    )

    current_net_wage = calc_net_wage(person)

    return net_wage_last_year - current_net_wage


def calc_elterngeld_percentage(considered_wage, params):
    """ This function calculates the percentage share of net income, which is
    reinbursed in the time of recieving elterngeld.

    According to § 2 (2) BEEG the percentage increases below elg_st_1 and decreases
    above elg_st_2.
    """
    if considered_wage < params["elg_st_1"]:
        wag_diff = params["elg_st_1"] - considered_wage

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = params["elgfaktor"] + number_steps * params["elg_perc_correct"]

    elif considered_wage > params["elg_st_2"]:
        wag_diff = considered_wage - params["elg_st_2"]

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = params["elgfaktor"] - number_steps * params["elg_perc_correct"]

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


def calc_geschw_bonus(elt_geld_calc, params):
    """ Calculating the bonus for siblings.


    According to § 2a parents of siblings get a bonus.
    """
    bonus_calc = params["elg_geschw_bonus_share"] * elt_geld_calc
    bonus = max(
        min(bonus_calc, params["elg_geschw_bonus_max"]), params["elg_geschw_bonus_min"],
    )
    return bonus
