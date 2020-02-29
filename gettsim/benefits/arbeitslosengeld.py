"""This module contains functions related to "Arbeitslosengeld"."""


def ui(
    person,
    params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    e_st_params,
    soli_st_params,
):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """
    # Beitragsbemessungsgrenze differs in east and west germany
    westost = "o" if person["east"] else "w"

    alg_entgelt = proxy_net_wage_last_year(
        person,
        e_st_params,
        soli_st_params,
        beit_bem_grenz=soz_vers_beitr_params[f"rvmaxek{westost}"],
        werbungs_pausch=e_st_abzuege_params["werbung"],
        soz_vers_pausch=params["soz_vers_pausch"],
    )

    eligible = check_eligibility_alg(person)

    if eligible:
        if person["child_num_tu"].sum() == 0:
            person["m_alg1"] = alg_entgelt * params["agsatz0"]
        else:
            person["m_alg1"] = alg_entgelt * params["agsatz1"]
    else:
        person["m_alg1"] = 0.0
    return person


def proxy_net_wage_last_year(
    person,
    e_st_params,
    soli_st_params,
    beit_bem_grenz,
    werbungs_pausch,
    soz_vers_pausch,
):
    """ Calculating the claim for the Arbeitslosengeld, depending on the current
    wage."""

    # Relevant wage is capped at the contribution thresholds
    max_wage = min(beit_bem_grenz, person["m_wage_l1"])

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = soz_vers_pausch * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = e_st_params["tax_schedule"](12 * max_wage - werbungs_pausch, e_st_params)

    prox_soli = soli_st_params["soli_formula"](prox_tax, soli_st_params)

    return max(0, max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12)


def check_eligibility_alg(person):
    """Checking eligibility, depending on the months worked beforehand, the age and
    other variables.."""
    # Months of unemployment beforehand.
    mts_ue = person["months_ue"] + person["months_ue_l1"] + person["months_ue_l2"]
    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # there are different replacement rates depending on presence of children
    return (
        (1 <= mts_ue <= 12)
        & (person["age"] < 65)
        & (person["m_pensions"] == 0)
        & (person["w_hours"] < 15)
    )
