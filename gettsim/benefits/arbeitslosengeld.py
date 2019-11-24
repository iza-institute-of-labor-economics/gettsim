import numpy as np

from gettsim.taxes.calc_taxes import soli_formula


def ui(person, tb):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """

    alg_entgelt = _alg_entgelt(person, tb)

    eligible = check_eligibility_alg(person)

    if eligible:
        if person["child_num_tu"].sum() == 0:
            person["m_alg1"] = alg_entgelt * tb["agsatz0"]
        else:
            person["m_alg1"] = alg_entgelt * tb["agsatz1"]
    else:
        person["m_alg1"] = 0.0
    return person


def _alg_entgelt(person, tb):
    """ Calculating the claim for the Arbeitslosengeld, depending on the current
    wage."""
    westost = "o" if person["east"] else "w"
    # Relevant wage is capped at the contribution thresholds
    alg_wage = np.minimum(tb["rvmaxek" + westost], person["m_wage_l1"])

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    alg_ssc = tb["alg1_abz"] * alg_wage
    # assume west germany for this particular calculation
    # df['east'] = False
    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    alg_tax = tb["tax_schedule"](12 * alg_wage - tb["werbung"], tb)

    alg_soli = soli_formula(alg_tax, tb)

    return np.maximum(0, alg_wage - alg_ssc - alg_tax / 12 - alg_soli / 12)


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
