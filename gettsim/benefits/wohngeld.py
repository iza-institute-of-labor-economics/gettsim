import numpy as np


def wg(household, params):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual
        rent and differs on the municipality level ('Mietstufe' (1,...,6)).

        We usually don't have information on the last item.
        Therefore we assume 'Mietstufe' 3, corresponding to an average level,
        but other Mietstufen can be specified in `household`.
    """
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)

    household_size = household.shape[0]
    # Caluclate income in separate function
    household["Y"] = household["_wohngeld_eink"]
    # Caluclate rent in separate function
    household["M"] = calc_wg_rent(household, params, household_size)
    # Apply Wohngeld Formel.
    household["wohngeld_basis"] = apply_wg_formula(household, params, household_size)

    # Sum of wohngeld within household
    wg_head = household["wohngeld_basis"] * household["tu_vorstand"]
    household.loc[:, "wohngeld_basis_hh"] = wg_head.sum()
    household = household.round({"wohngeld_basis_hh": 2})
    return household


def calc_wg_rent(household, params, household_size):
    """
    This function yields the relevant rent for calculating the wohngeld.
    """
    # # There are also min and max values for this.
    # # If 'Mietstufe' is not given, choose '3'.
    # if "mietstufe" in household.columns:
    #     mietstufe = int(household["mietstufe"].iloc[0])
    # else:
    #     mietstufe = 3

    mietstufe = household["mietstufe"].iloc[0]
    cnstyr = household["immobilie_baujahr"].iloc[0]
    # First max rent
    # Before 2009, they differed by construction year of the house
    max_rent = params["calc_max_rent"](params, household_size, cnstyr, mietstufe)

    # Calculate share of tax unit wrt whole household
    tax_unit_share = household.groupby("tu_id")["tu_id"].transform("count") / len(
        household
    )
    # distribute max rent among the tax units
    max_rent_dist = max_rent * tax_unit_share
    wgmiete = np.minimum(max_rent_dist, household["kaltmiete_m"] * tax_unit_share)
    # wg["wgheiz"] = household["heizkost"] * tax_unit_share
    return np.maximum(wgmiete, household["_wohngeld_min_miete"])


def calc_max_rent_since_2009(params, household_size, cnstyr, mietstufe):
    """
    Since 2009 a different formula for the maximal acknowledged rent applies.
    Now the date of the construction is irrelevant.

    cnstyr is not used, but needs to be handled for compatibility reasons
    """
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    max_miete = params["max_miete"][min(household_size, 5)][mietstufe]
    if household_size > 5:
        max_miete += params["max_miete"]["5plus"][mietstufe] * (household_size - 5)
    return max_miete


def calc_max_rent_until_2008(params, household_size, constr_year, mietstufe):
    """ Before 2009, differentiate by construction year of the house and
    calculate the maximal acknowledged rent."""

    max_miete_dict = params["max_miete"]
    constr_year_dict = max_miete_dict[min(household_size, 5)]
    constr_year_category = min(
        year_limit
        for year_limit in constr_year_dict.keys()
        if constr_year <= year_limit
    )
    max_miete = constr_year_dict[constr_year_category][mietstufe]
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    if household_size > 5:
        max_miete += max_miete_dict["5plus"][constr_year_category][mietstufe] * (
            household_size - 5
        )
    return max_miete


def apply_wg_formula(household, params, household_size):
    # The formula is only valid for up to 12 household members
    koeffizenten = params["koeffizienten_berechnungsformel"][min(household_size, 12)]
    # There are parameters a, b, c, depending on hh size
    wg_amount = np.maximum(
        0,
        params["faktor_berechnungsformel"]
        * (
            household["M"]
            - (
                (
                    koeffizenten["a"]
                    + (koeffizenten["b"] * household["M"])
                    + (koeffizenten["c"] * household["Y"])
                )
                * household["Y"]
            )
        ),
    )
    # If more than 12 persons, there is a lump-sum on top.
    # You may however not get more than the corrected rent "M".
    if household_size > 12:
        wg_amount = np.minimum(
            household["M"],
            np.max(wg_amount, 0) + params["bonus_12_mehr"] * (household_size - 12),
        )

    return wg_amount
