import numpy as np


def zve(tax_unit, e_st_abzuege_params, soz_vers_beitr_params, kindergeld_params):
    """Calculate taxable income (zve = zu versteuerndes Einkommen). The calculation
    of the 6 branches of income is according to
    https://de.wikipedia.org/wiki/Einkommensteuer_(Deutschland)#Rechenschema

        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
    """
    adult_married = ~tax_unit["child"] & tax_unit["zveranl"]
    # married = [tax_unit['zveranl'], ~tax_unit['zveranl']]
    # create output dataframe and transter some important variables

    # Sonderausgaben
    tax_unit = deductible_child_care_costs(tax_unit, e_st_abzuege_params)

    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    tax_unit.loc[:, "gross_e1"] = 12 * tax_unit["m_self"]
    # Earnings
    tax_unit = calc_gross_e4(tax_unit, e_st_abzuege_params, soz_vers_beitr_params)
    # Capital Income
    tax_unit.loc[:, "gross_e5"] = np.maximum((12 * tax_unit["m_kapinc"]), 0)
    # Income from rents
    tax_unit.loc[:, "gross_e6"] = 12 * tax_unit["m_vermiet"]
    # Others (Pensions)
    tax_unit = calc_gross_e7(tax_unit, e_st_abzuege_params)
    # Sum of incomes
    tax_unit.loc[:, "gross_gde"] = calc_gde(tax_unit, e_st_abzuege_params)

    # Gross (market) income <> sum of incomes...
    tax_unit.loc[:, "m_brutto"] = tax_unit[
        ["m_self", "m_wage", "m_kapinc", "m_vermiet", "m_pensions"]
    ].sum(axis=1)

    tax_unit.loc[:, "handc_pausch"] = calc_handicap_lump_sum(
        tax_unit, e_st_abzuege_params
    )

    # Aggregate several incomes on the taxpayer couple
    for inc in ["gross_e1", "gross_e4", "gross_e5", "gross_e6", "gross_e7"]:
        tax_unit.loc[adult_married, inc + "_tu"] = tax_unit.loc[
            adult_married, inc
        ].sum()

    # TAX DEDUCTIONS
    # 1. VORSORGEAUFWENDUNGEN
    # TODO: check various deductions against each other (when modelled)
    tax_unit.loc[:, "vorsorge"] = e_st_abzuege_params["vorsorge"](
        tax_unit, e_st_abzuege_params, soz_vers_beitr_params
    )
    # 2. Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    tax_unit = calc_altfreibetrag(tax_unit, e_st_abzuege_params)

    # Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    tax_unit = e_st_abzuege_params["calc_hhfreib"](tax_unit, e_st_abzuege_params)

    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    tax_unit.loc[~tax_unit["child"], "zve_nokfb"] = zve_nokfb(
        tax_unit, e_st_abzuege_params
    )
    # Tax base including capital income
    tax_unit = zve_abg_nokfb(tax_unit, e_st_abzuege_params)

    tax_unit = kinderfreibetrag(tax_unit, e_st_abzuege_params, kindergeld_params)

    # Finally, Subtract (corrected) Child allowance
    tax_unit.loc[~tax_unit["child"], "zve_kfb"] = np.maximum(
        tax_unit["zve_nokfb"] - tax_unit["kifreib"], 0
    )
    tax_unit.loc[~tax_unit["child"], "zve_abg_kfb"] = np.maximum(
        tax_unit["zve_abg_nokfb"] - tax_unit["kifreib"], 0
    )
    # Finally, modify married couples income according to Splitting rule,
    # i.e. each partner get assigned half of the total income
    for incdef in ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]:
        tax_unit.loc[:, "zve_" + incdef + "_tu"] = tax_unit.loc[
            adult_married, "zve_" + incdef
        ].sum()
        tax_unit.loc[adult_married, "zve_" + incdef] = (
            0.5 * tax_unit["zve_" + incdef + "_tu"]
        )

    return tax_unit


def kinderfreibetrag(tax_unit, params, kindergeld_params):
    """Calculate zve with Child Allowance (Kinderfreibetrag)"""
    tax_unit["kifreib"] = 0.0
    #
    # Married couples may share deductions if one partner does not need it.
    # For non-married, just deduct half the amount for each child.
    # TODO: Check whether this is correct for non-married couples

    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    child_num_kg = kindergeld_params["childben_elig_rule"](
        tax_unit, kindergeld_params
    ).sum()

    # Find out who has the lower zve among partners
    nokfb_lower = tax_unit["zve_nokfb"].min()

    diff_kifreib = nokfb_lower - (0.5 * params["kifreib"] * child_num_kg)

    # If the couple is married and one earns not enough to split the kinderfeibetrag,
    # things get a bit more complicated
    if diff_kifreib < 0 & tax_unit[~tax_unit["child"]]["zveranl"].all():

        # The high earner gets half of the total kinderfreibetrag plus the amount the
        # lower earner can't claim.
        kifreib_higher = (0.5 * params["kifreib"] * child_num_kg) + abs(diff_kifreib)
        # The second earner subtracts the remaining amount
        kifreib_lower = 0.5 * params["kifreib"] * child_num_kg - abs(diff_kifreib)
        # Then we assign each earner the amount and return the series
        tax_unit.loc[
            ~tax_unit["child"] & tax_unit["zve_nokfb"] != nokfb_lower, "kifreib"
        ] = kifreib_higher
        tax_unit.loc[
            ~tax_unit["child"] & tax_unit["zve_nokfb"] == nokfb_lower, "kifreib"
        ] = kifreib_lower

        return tax_unit

    # For non married couples or couples where both earn enough this are a lot easier.
    # Just split the kinderfreibetrag 50/50.
    else:
        tax_unit.loc[~tax_unit["child"], "kifreib"] = (
            0.5 * params["kifreib"] * child_num_kg
        )
        return tax_unit


def zve_nokfb(tax_unit, params):
    """Calculate zve with no 'kinderfreibetrag'."""
    return np.maximum(
        0,
        tax_unit["gross_gde"]
        - tax_unit["vorsorge"]
        - tax_unit["sonder"]
        - tax_unit["handc_pausch"]
        - tax_unit["hhfreib"]
        - tax_unit["altfreib"],
    )


def zve_abg_nokfb(tax_unit, params):
    """Calculates the zve with capital income in the tax base."""
    if tax_unit[~tax_unit["child"]]["zveranl"].all():
        tax_unit.loc[~tax_unit["child"], "zve_abg_nokfb"] = np.maximum(
            0,
            tax_unit["gross_gde"]
            + np.maximum(
                0, tax_unit["gross_e5"] - 2 * params["spsparf"] - 2 * params["spwerbz"],
            )
            - tax_unit["vorsorge"]
            - tax_unit["sonder"]
            - tax_unit["handc_pausch"]
            - tax_unit["hhfreib"]
            - tax_unit["altfreib"],
        )
    else:
        tax_unit.loc[~tax_unit["child"], "zve_abg_nokfb"] = np.maximum(
            0,
            tax_unit["gross_gde"]
            + np.maximum(
                0, tax_unit["gross_e5"] - params["spsparf"] - params["spwerbz"],
            )
            - tax_unit["vorsorge"]
            - tax_unit["sonder"]
            - tax_unit["handc_pausch"]
            - tax_unit["hhfreib"]
            - tax_unit["altfreib"],
        )
    return tax_unit


def calc_altfreibetrag(tax_unit, params):
    """Calculates the deductions for elderly. Not tested yet!!!"""
    tax_unit["altfreib"] = 0.0
    tax_unit.loc[tax_unit["age"] > 64, "altfreib"] = np.minimum(
        params["altentq"]
        * 12
        * (
            tax_unit["m_wage"]
            + np.maximum(0, tax_unit[["m_kapinc", "m_self", "m_vermiet"]].sum(axis=1))
        ),
        params["altenth"],
    )
    return tax_unit


def calc_handicap_lump_sum(tax_unit, params):
    """Calculate the different deductions for different handicap degrees."""
    # Behinderten-Pauschbeträge
    hc_degrees = [
        tax_unit["handcap_degree"].between(45, 50),
        tax_unit["handcap_degree"].between(51, 60),
        tax_unit["handcap_degree"].between(61, 70),
        tax_unit["handcap_degree"].between(71, 80),
        tax_unit["handcap_degree"].between(81, 90),
        tax_unit["handcap_degree"].between(91, 100),
    ]
    hc_pausch = [
        params["sbhp50"],
        params["sbhp60"],
        params["sbhp70"],
        params["sbhp80"],
        params["sbhp90"],
        params["sbhp100"],
    ]
    return np.nan_to_num(np.select(hc_degrees, hc_pausch))


def calc_gde(tax_unit, params):
    """Calculates sum of the taxable income. It depends on the year if capital
    income, counts into the sum."""
    gross_gde = tax_unit[["gross_e1", "gross_e4", "gross_e6", "gross_e7"]].sum(axis=1)

    # Add UBI to taxable income
    # if ref == "UBI":
    #    zve.loc[:, "gross_gde"] = zve["gross_gde"] + (tax_unit["ubi"] * 12)

    # Kapitaleinkommen im Tarif versteuern oder nicht?
    # If capital income tax with tariff, add it but account for exemptions
    if params["year"] < 2009:
        gross_gde += np.maximum(
            tax_unit["gross_e5"] - params["spsparf"] - params["spwerbz"], 0,
        )
    return gross_gde


def calc_gross_e4(tax_unit, params, soz_vers_beitr_params):
    """Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'"""

    tax_unit.loc[:, "gross_e4"] = 12 * tax_unit["m_wage"]
    # Every adult with some wage, gets a lump sum payment for Werbungskosten
    tax_unit.loc[(~tax_unit["child"]) & (tax_unit["m_wage"] > 0), "gross_e4"] -= params[
        "werbung"
    ]

    # If they earn less the mini job limit, then their relevant gross income is 0
    if tax_unit.east.iloc[0]:
        mini = soz_vers_beitr_params["mini_grenzeo"]
    else:
        mini = soz_vers_beitr_params["mini_grenzew"]

    tax_unit.loc[tax_unit["m_wage"] <= mini, "gross_e4"] = 0
    return tax_unit


def deductible_child_care_costs(tax_unit, params):
    """Calculating sonderausgaben for childcare. We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg."""
    # So far we only implement the current regulation, which is since 2012 is in place.
    if params["year"] < 2012:
        # For earlier years we only use the pausch value
        tax_unit.loc[~tax_unit["child"], "sonder"] = params["sonder"]
        return tax_unit
    else:
        adult_num = len(tax_unit[~tax_unit["child"]])
        # The maximal amount to claim is 4000 per child. We only count the claim for
        # children under 14. By law the parents are also to allow to claim for disabled
        # children til the age of 25.
        eligible = tax_unit["age"] <= 14

        deductible_costs = (
            eligible
            * np.minimum(params["childcare_max"], 12 * tax_unit["m_childcare"])
            * params["childcare_share"]
            / adult_num
        )
        # If parents can't claim anything, they get a pausch value.
        tax_unit.loc[~tax_unit["child"], "sonder"] = max(
            np.sum(deductible_costs), params["sonder"]
        )
        return tax_unit


def calc_gross_e7(tax_unit, params):
    """ Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions."""
    # The share of pensions subject to income taxation
    tax_unit.loc[tax_unit["renteneintritt"] <= 2004, "ertragsanteil"] = 0.27
    tax_unit.loc[
        tax_unit["renteneintritt"].between(2005, 2020), "ertragsanteil"
    ] = 0.5 + 0.02 * (tax_unit["renteneintritt"] - 2005)
    tax_unit.loc[
        tax_unit["renteneintritt"].between(2021, 2040), "ertragsanteil"
    ] = 0.8 + 0.01 * (tax_unit["renteneintritt"] - 2020)
    tax_unit.loc[tax_unit["renteneintritt"] >= 2041, "ertragsanteil"] = 1
    tax_unit.loc[:, "gross_e7"] = np.maximum(
        12 * (tax_unit["ertragsanteil"] * tax_unit["m_pensions"])
        - params["vorsorgpausch"],
        0,
    )
    return tax_unit


def vorsorge2010(tax_unit, params, soz_vers_beitr_params):
    """'Vorsorgeaufwendungen': Deduct part of your social insurance contributions
        from your taxable income.
        This regulation has been changed often in recent years. In order not to make
        anyone worse off, the old regulation was maintained. Nowadays the older
        regulations don't play a large role (i.e. the new one is more beneficial most of
         the times) but they'd need to be implemented if earlier years are modelled.
        Vorsorgeaufwendungen until 2004
        TODO
        Vorsorgeaufwendungen since 2010
        § 10 (3) EStG
        The share of deductable pension contributions increases each year by 2 pp.
        ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
        4% from health contributions are not deductable.
        only deduct pension contributions up to the ceiling. multiply by 2
        because it's both employee and employer contributions.
        """
    westost = [~tax_unit["east"], tax_unit["east"]]
    rvbeit_vors = np.minimum(
        2 * tax_unit["rvbeit"],
        2
        * soz_vers_beitr_params["grvbs"]
        * np.select(
            westost,
            [soz_vers_beitr_params["rvmaxekw"], soz_vers_beitr_params["rvmaxeko"]],
        ),
    )

    # calculate x% of relevant employer and employee contributions
    # then subtract employer contributions
    # also subtract health + care + unemployment insurance contributions
    altersvors2010 = ~tax_unit["child"] * (
        (0.6 + 0.02 * (np.minimum(params["year"], 2025) - 2005)) * (12 * rvbeit_vors)
        - (12 * 0.5 * rvbeit_vors)
    )
    # These you get anyway ('Basisvorsorge').
    sonstigevors2010 = 12 * (tax_unit["pvbeit"] + 0.96 * tax_unit["gkvbeit"])
    # maybe add avbeit, but do not exceed 1900€.
    sonstigevors2010 = np.maximum(
        sonstigevors2010,
        np.minimum(
            sonstigevors2010 + 12 * tax_unit["avbeit"], params["vors_sonst_max"],
        ),
    )

    vorsorge2010 = altersvors2010 + sonstigevors2010

    return vorsorge2010.astype(int)


def vorsorge_dummy(tax_unit, params, soz_vers_beitr_params):
    return 0


def calc_hhfreib_until2014(tax_unit, params):
    """Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'"""
    tax_unit["hhfreib"] = 0.0
    tax_unit.loc[tax_unit["alleinerz"], "hhfreib"] = params["hhfreib"]
    return tax_unit


def calc_hhfreib_from2015(tax_unit, params):
    """Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'"""
    tax_unit["hhfreib"] = 0.0
    tax_unit.loc[tax_unit["alleinerz"], "hhfreib"] = params["hhfreib"] + (
        (tax_unit["child"].sum() - 1) * params["hhfreib_ch"]
    )
    return tax_unit
