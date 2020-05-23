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
    considered_wage = person["elterngeld_eink_relev"]

    if considered_wage < 0:
        person["elterngeld_m"] = 0
    else:
        elterngeld_calc = person["elterngeld_eink_erlass"]

        prelim_elterngeld = max(
            min(elterngeld_calc, params["elterngeld_höchstbetrag"]),
            params["elterngeld_mindestbetrag"],
        )
        if person["berechtigt_für_geschw_bonus"]:
            prelim_elterngeld += person["geschw_bonus"]
        prelim_elterngeld += (
            person["anz_mehrlinge_bonus"] * params["elterngeld_mehrling_bonus"]
        )
        person["elterngeld_m"] = prelim_elterngeld

    return person
