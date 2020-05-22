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
    household["M"] = household[
        "_wohngeld_max_miete"
    ]  # calc_wg_rent(household, params, household_size)

    # Apply Wohngeld Formel.
    household["wohngeld_basis"] = apply_wg_formula(household, params, household_size)

    # Sum of wohngeld within household
    wg_head = household["wohngeld_basis"] * household["tu_vorstand"]
    household.loc[:, "wohngeld_basis_hh"] = wg_head.sum()
    household = household.round({"wohngeld_basis_hh": 2})
    return household


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
