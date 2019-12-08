def elt_geld(person, params):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    if person["elt_zeit"]:
        considered_wage = person["m_wage_l1"] - person["m_wage"]

        payed_percentage = calc_elterngeld_percentage(considered_wage, params)

        elt_geld_calc = considered_wage * payed_percentage

        person["elt_geld"] = max(min(elt_geld_calc, params["elgmax"]), params["elgmin"])

    else:
        person["elt_geld"] = 0

    return person


def calc_elterngeld_percentage(considered_wage, params):
    if considered_wage < params["elg_st_1"]:
        wag_diff = params["elg_st_1"] - considered_wage

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = params["elgfaktor"] + number_steps * params["elg_perc_correct"]

    elif considered_wage > params["elg_st_2"]:
        wag_diff = considered_wage - params["elg_st_2"]

        number_steps = wag_diff / params["elg_perc_correct_step"]
        percentage = params["elgfaktor"] + number_steps * params["elg_perc_correct"]

    else:
        percentage = params["elgfaktor"]

    return percentage
