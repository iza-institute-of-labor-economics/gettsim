"""This module contains functions related to "Arbeitslosengeld"."""


def ui(
    person,
    params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """
    # Beitragsbemessungsgrenze differs in east and west germany
    westost = "o" if person["wohnort_ost"] else "w"

    alg_entgelt = proxy_net_wage_last_year(
        person,
        eink_st_params,
        soli_st_params,
        beit_bem_grenz=soz_vers_beitr_params[f"rvmaxek{westost}"],
        werbungs_pausch=eink_st_abzuege_params["werbung"],
        soz_vers_pausch=params["soz_vers_pausch"],
    )

    eligible = check_eligibility_alg(person, params)

    if eligible:
        if person["anz_kinder_tu"].sum() == 0:
            person["arbeitsl_geld_m"] = alg_entgelt * params["agsatz0"]
        else:
            person["arbeitsl_geld_m"] = alg_entgelt * params["agsatz1"]
    else:
        person["arbeitsl_geld_m"] = 0.0
    return person


def proxy_net_wage_last_year(
    person,
    eink_st_params,
    soli_st_params,
    beit_bem_grenz,
    werbungs_pausch,
    soz_vers_pausch,
):
    """ Calculating the claim for the Arbeitslosengeld, depending on the current
    wage."""

    # Relevant wage is capped at the contribution thresholds
    max_wage = min(beit_bem_grenz, person["bruttolohn_vorj_m"])

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = soz_vers_pausch * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = eink_st_params["st_tarif"](
        12 * max_wage - werbungs_pausch, eink_st_params
    )

    prox_soli = soli_st_params["soli_formula"](prox_tax, soli_st_params)

    return max(0, max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12)


def check_eligibility_alg(person, params):
    """Checking eligibility, depending on the months worked beforehand, the age and
    other variables.."""
    # Months of unemployment beforehand.
    mts_ue = (
        person["arbeitsl_lfdj_m"]
        + person["arbeitsl_vorj_m"]
        + person["arbeitsl_vor2j_m"]
    )
    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # there are different replacement rates depending on presence of children
    return (
        (1 <= mts_ue <= 12)
        & (person["alter"] < 65)
        & (person["ges_rente_m"] == 0)
        & (person["arbeitsstunden_w"] < params["ag_stundengrenze"])
    )
