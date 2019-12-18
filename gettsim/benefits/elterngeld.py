from gettsim.benefits.arbeitslosengeld import proxy_net_wage_last_year
from gettsim.tax_transfer import _apply_tax_transfer_func


def elt_geld(
    household,
    params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    in_cols = list(household.columns.values)
    # Everything was already initialized
    out_cols = []
    household.loc[household["elt_zeit"], :] = _apply_tax_transfer_func(
        household[household["elt_zeit"]],
        tax_func=calc_elt_geld,
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

    household.loc[~household["elt_zeit"], ["elt_geld"]] = 0

    return household


def calc_elt_geld(
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
    considered_wage = calc_consideraded_wage(
        person,
        params,
        soz_vers_beitr_params,
        e_st_abzuege_params,
        e_st_params,
        soli_st_params,
    )
    if considered_wage < 0:
        person["elt_geld"] = 0
    else:
        payed_percentage = calc_elterngeld_percentage(considered_wage, params)

        elt_geld_calc = considered_wage * payed_percentage

        if person["geschw_bonus"]:
            elt_geld_calc += calc_geschw_bonus(elt_geld_calc, params)
        person["elt_geld"] = max(min(elt_geld_calc, params["elgmax"]), params["elgmin"])

    return person


def calc_consideraded_wage(
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
