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
        net_wage_last_year = proxy_net_wage_last_year(
            person,
            arbeitsl_geld_params,
            soz_vers_beitr_params,
            e_st_abzuege_params,
            e_st_params,
            soli_st_params,
        )

        current_net_wage = calc_net_wage(person)

        considered_wage = net_wage_last_year - current_net_wage

        if considered_wage < 0:
            person["elt_geld"] = 0

        else:
            payed_percentage = calc_elterngeld_percentage(considered_wage, params)

            elt_geld_calc = considered_wage * payed_percentage

            person["elt_geld"] = max(
                min(elt_geld_calc, params["elgmax"]), params["elgmin"]
            )

    else:
        person["elt_geld"] = 0

    return person


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
