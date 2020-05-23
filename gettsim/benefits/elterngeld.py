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
    a child that is up to one year old (Elterngeld)

    """
    # Everything was already initialized
    out_cols = []
    household.loc[household["elternzeit_anspruch"], :] = apply_tax_transfer_func(
        household[household["elternzeit_anspruch"]],
        tax_func=calc_elterngeld,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=household.columns.tolist(),
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
        paid_percentage = calc_elterngeld_percentage(considered_wage, params)

        elterngeld_calc = considered_wage * paid_percentage

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
    net_wage_last_year = person["proxy_eink_vorj_elterngeld"]

    current_net_wage = calc_net_wage(person)

    return net_wage_last_year - current_net_wage


def calc_elterngeld_percentage(considered_wage, params):
    """ This function calculates the percentage share of net income, which is
    reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until elterngeld_prozent_minimum.

    """
    if considered_wage < params["elterngeld_nettoeinkommen_stufen"][1]:
        wag_diff = params["elterngeld_nettoeinkommen_stufen"][1] - considered_wage

        number_steps = wag_diff / params["elterngeld_eink_schritt_korrektur"]

        percentage = (
            params["elterngeld_faktor"]
            + number_steps * params["elterngeld_prozent_korrektur"]
        )

    elif considered_wage > params["elterngeld_nettoeinkommen_stufen"][2]:
        wag_diff = considered_wage - params["elterngeld_nettoeinkommen_stufen"][2]

        number_steps = wag_diff / params["elterngeld_eink_schritt_korrektur"]
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
    bonus = max(bonus_calc, params["elterngeld_geschwister_bonus_minimum"])
    return bonus
