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
    household["Y"] = calc_wg_income(household, params, household_size)
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

    # Second min rent
    min_rent = calc_min_rent(params, household_size)

    # Calculate share of tax unit wrt whole household
    tax_unit_share = household.groupby("tu_id")["tu_id"].transform("count") / len(
        household
    )
    # distribute max rent among the tax units
    max_rent_dist = max_rent * tax_unit_share
    wgmiete = np.minimum(max_rent_dist, household["kaltmiete_m"] * tax_unit_share)
    # wg["wgheiz"] = household["heizkost"] * tax_unit_share
    return np.maximum(wgmiete, min_rent)


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


def calc_min_rent(params, household_size):
    """ The minimal acknowledged rent depending on the household size."""
    min_rent = params["min_miete"][min(household_size, 12)]
    return min_rent


def calc_wg_income(household, params, household_size):
    """ This function calculates the relevant income for the calculation of the
    wohngeld."""
    # Start with income revelant for the housing beneift
    # tax-relevant share of pensions for tax unit
    household["_st_rente"] = household["_ertragsanteil"] * household["ges_rente_m"]
    household["_st_rente_tu_k"] = household.groupby("tu_id")["_st_rente"].transform(
        "sum"
    )
    # Different incomes on tu base
    for inc in [
        "arbeitsl_geld_m",
        "sonstig_eink_m",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "eink_st_m",
        "rentenv_beit_m",
        "ges_krankv_beit_m",
        "unterhaltsvors_m",
        "elterngeld_m",
    ]:
        # TODO Why is there a k in the end? It does not differ from the usual tu sum!
        household[f"{inc}_tu_k"] = household.groupby("tu_id")[inc].transform("sum")

    household["_wohngeld_abzüge"] = calc_wg_abzuege(household, params)
    # Relevant income is market income + transfers...
    household["_wohngeld_brutto_eink"] = calc_wg_gross_income(household)
    household["_wohngeld_sonstiges_eink"] = household[
        [
            "arbeitsl_geld_m_tu_k",
            "sonstig_eink_m_tu_k",
            "_st_rente_tu_k",
            "unterhaltsvors_m_tu_k",
            "elterngeld_m_tu_k",
        ]
    ].sum(axis=1)

    # ... minus a couple of lump-sum deductions for handicaps,
    # children income or being single parent
    household["_wohngeld_eink_abzüge"] = calc_wg_income_deductions(household, params)
    household["_wohngeld_eink_abzüge_tu_k"] = household.groupby("tu_id")[
        "_wohngeld_eink_abzüge"
    ].transform("sum")
    prelim_y = (1 - household["_wohngeld_abzüge"]) * np.maximum(
        0,
        (
            household["_wohngeld_brutto_eink"]
            + household["_wohngeld_sonstiges_eink"]
            - household["_wohngeld_eink_abzüge_tu_k"]
        ),
    )
    # There's a minimum Y depending on the hh size
    return _set_min_y(prelim_y, params, household_size)


def calc_wg_abzuege(household, params):
    # There share of income to be deducted is 0/10/20/30%, depending on whether
    # household is subject to income taxation and/or payroll taxes
    wg_abz = (
        (household["eink_st_m_tu_k"] > 0) * 1
        + (household["rentenv_beit_m_tu_k"] > 0) * 1
        + (household["ges_krankv_beit_m_tu_k"] > 0) * 1
    )

    return wg_abz.replace(params["abzug_stufen"])


def calc_wg_gross_income(household):
    out = (
        np.maximum(household["brutto_eink_1_tu_k"] / 12, 0)
        + np.maximum(household["brutto_eink_4_tu_k"] / 12, 0)
        + np.maximum(household["brutto_eink_5_tu_k"] / 12, 0)
        + np.maximum(household["brutto_eink_6_tu_k"] / 12, 0)
    )
    return out


def calc_wg_income_deductions(household, params):
    if params["jahr"] <= 2015:
        wg_incdeduct = _calc_wg_income_deductions_until_2015(household, params)
    else:
        wg_incdeduct = _calc_wg_income_deductions_since_2016(household, params)
    return wg_incdeduct


def _calc_wg_income_deductions_until_2015(household, params):
    """ calculate special deductions for handicapped, single parents
    and children who are working
    """
    household["_kind_unter_11"] = household["alter"].lt(11)
    household["_anzahl_kinder_unter_11"] = (
        household.groupby("tu_id")["_kind_unter_11"].transform("sum").astype(int)
    )
    workingchild = (household["bruttolohn_m"] > 0) & household["kindergeld_anspruch"]

    wg_incdeduct = (
        (household["behinderungsgrad"] > 80) * params["freib_behinderung"]["ab80"]
        + household["behinderungsgrad"].between(1, 80)
        * params["freib_behinderung"]["u80"]
        + (
            workingchild
            * np.minimum(params["freib_kinder"][24], household["bruttolohn_m"])
        )
        + (
            (household["alleinerziehend"] & (~household["kind"]))
            * household["_anzahl_kinder_unter_11"]
            * params["freib_kinder"][12]
        )
    )
    return wg_incdeduct


def _calc_wg_income_deductions_since_2016(household, params):
    """ calculate special deductions for handicapped, single parents
    and children who are working
    """
    workingchild = (household["bruttolohn_m"] > 0) & household["kindergeld_anspruch"]

    wg_incdeduct = (
        (household["behinderungsgrad"] > 0) * params["freib_behinderung"]
        + (
            workingchild
            * np.minimum(params["freib_kinder"][24], household["bruttolohn_m"])
        )
        + (
            household["alleinerziehend"]
            * params["freib_kinder"][12]
            * (~household["kind"])
        )
    )
    return wg_incdeduct


def _set_min_y(prelim_y, params, household_size):
    # Households larger then 12 get assigned the value of a 12 person household
    min_y = np.maximum(prelim_y, params["min_eink"][min(household_size, 12)])
    return min_y


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
