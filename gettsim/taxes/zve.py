import numpy as np


def zve(tax_unit, tb):
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

    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    tax_unit.loc[:, "gross_e1"] = 12 * tax_unit["m_self"]
    # Earnings
    tax_unit = calc_gross_e4(tax_unit, tb)
    # Capital Income
    tax_unit.loc[:, "gross_e5"] = np.maximum((12 * tax_unit["m_kapinc"]), 0)
    # Income from rents
    tax_unit.loc[:, "gross_e6"] = 12 * tax_unit["m_vermiet"]
    # Others (Pensions)
    tax_unit = calc_gross_e7(tax_unit, tb)
    # Sum of incomes
    tax_unit.loc[:, "gross_gde"] = calc_gde(tax_unit, tb)

    # Gross (market) income <> sum of incomes...
    tax_unit.loc[:, "m_brutto"] = tax_unit[
        ["m_self", "m_wage", "m_kapinc", "m_vermiet", "m_pensions"]
    ].sum(axis=1)

    tax_unit.loc[:, "handc_pausch"] = calc_handicap_lump_sum(tax_unit, tb)

    # Aggregate several incomes on the taxpayer couple
    for inc in ["gross_e1", "gross_e4", "gross_e5", "gross_e6", "gross_e7"]:
        tax_unit.loc[adult_married, inc + "_tu"] = tax_unit.loc[
            adult_married, inc
        ].sum()

    # TAX DEDUCTIONS
    # 1. Allgemeine Sonderausgaben
    # Sonderausgaben
    tax_unit = deductible_child_care_costs(tax_unit, tb)
    # 2. VORSORGEAUFWENDUNGEN (technically a special case of "Sonderausgaben")
    #
    tax_unit.loc[:, "vorsorge"] = tb["vorsorge"](tax_unit, tb)

    # 3. Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    tax_unit = calc_altfreibetrag(tax_unit, tb)
    # 4.. Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    tax_unit = tb["calc_hhfreib"](tax_unit, tb)

    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    tax_unit.loc[~tax_unit["child"], "zve_nokfb"] = zve_nokfb(tax_unit, tb)
    # Tax base including capital income
    tax_unit = zve_abg_nokfb(tax_unit, tb)

    tax_unit = kinderfreibetrag(tax_unit, tb)

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


def kinderfreibetrag(tax_unit, tb):
    """Calculate zve with Child Allowance (Kinderfreibetrag)"""
    tax_unit["kifreib"] = 0.0
    #
    # Married couples may share deductions if one partner does not need it.
    # For non-married, just deduct half the amount for each child.
    # TODO: Check whether this is correct for non-married couples

    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    child_num_kg = tb["childben_elig_rule"](tax_unit, tb).sum()

    # Find out who has the lower zve among partners
    nokfb_lower = tax_unit["zve_nokfb"].min()

    diff_kifreib = nokfb_lower - (0.5 * tb["kifreib"] * child_num_kg)

    # If the couple is married and one earns not enough to split the kinderfeibetrag,
    # things get a bit more complicated
    if diff_kifreib < 0 & tax_unit[~tax_unit["child"]]["zveranl"].all():

        # The high earner gets half of the total kinderfreibetrag plus the amount the
        # lower earner can't claim.
        kifreib_higher = (0.5 * tb["kifreib"] * child_num_kg) + abs(diff_kifreib)
        # The second earner subtracts the remaining amount
        kifreib_lower = 0.5 * tb["kifreib"] * child_num_kg - abs(diff_kifreib)
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
        tax_unit.loc[~tax_unit["child"], "kifreib"] = 0.5 * tb["kifreib"] * child_num_kg
        return tax_unit


def zve_nokfb(tax_unit, tb):
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


def zve_abg_nokfb(tax_unit, tb):
    """Calculates the zve with capital income in the tax base."""
    if tax_unit[~tax_unit["child"]]["zveranl"].all():
        tax_unit.loc[~tax_unit["child"], "zve_abg_nokfb"] = np.maximum(
            0,
            tax_unit["gross_gde"]
            + np.maximum(
                0, tax_unit["gross_e5"] - 2 * tb["spsparf"] - 2 * tb["spwerbz"]
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
            + np.maximum(0, tax_unit["gross_e5"] - tb["spsparf"] - tb["spwerbz"])
            - tax_unit["vorsorge"]
            - tax_unit["sonder"]
            - tax_unit["handc_pausch"]
            - tax_unit["hhfreib"]
            - tax_unit["altfreib"],
        )
    return tax_unit


def calc_altfreibetrag(tax_unit, tb):
    """Calculates the deductions for elderly. Not tested yet!!!"""
    tax_unit["altfreib"] = 0.0
    tax_unit.loc[tax_unit["age"] > 64, "altfreib"] = np.minimum(
        tb["altentq"]
        * 12
        * (
            tax_unit["m_wage"]
            + np.maximum(0, tax_unit[["m_kapinc", "m_self", "m_vermiet"]].sum(axis=1))
        ),
        tb["altenth"],
    )
    return tax_unit


def calc_handicap_lump_sum(tax_unit, tb):
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
        tb["sbhp50"],
        tb["sbhp60"],
        tb["sbhp70"],
        tb["sbhp80"],
        tb["sbhp90"],
        tb["sbhp100"],
    ]
    return np.nan_to_num(np.select(hc_degrees, hc_pausch))


def calc_gde(tax_unit, tb):
    """Calculates sum of the taxable income. It depends on the year if capital
    income, counts into the sum."""
    gross_gde = tax_unit[["gross_e1", "gross_e4", "gross_e6", "gross_e7"]].sum(axis=1)

    # Add UBI to taxable income
    # if ref == "UBI":
    #    zve.loc[:, "gross_gde"] = zve["gross_gde"] + (tax_unit["ubi"] * 12)

    # Kapitaleinkommen im Tarif versteuern oder nicht?
    # If capital income tax with tariff, add it but account for exemptions
    if tb["yr"] < 2009:
        gross_gde += np.maximum(tax_unit["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0)
    return gross_gde


def calc_gross_e4(tax_unit, tb):
    """Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'"""

    tax_unit.loc[:, "gross_e4"] = 12 * tax_unit["m_wage"]
    # Every adult with some wage, gets a lump sum payment for Werbungskosten
    tax_unit.loc[(~tax_unit["child"]) & (tax_unit["m_wage"] > 0), "gross_e4"] -= tb[
        "werbung"
    ]

    # If they earn less the mini job limit, then their relevant gross income is 0
    if tax_unit.east.iloc[0]:
        mini = tb["mini_grenzeo"]
    else:
        mini = tb["mini_grenzew"]

    tax_unit.loc[tax_unit["m_wage"] <= mini, "gross_e4"] = 0
    return tax_unit


def deductible_child_care_costs(tax_unit, tb):
    """Calculating sonderausgaben for childcare. We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg."""
    # So far we only implement the current regulation, which is since 2012 is in place.
    if tb["yr"] < 2012:
        # For earlier years we only use the pausch value
        tax_unit.loc[~tax_unit["child"], "sonder"] = tb["sonder"]
        return tax_unit
    else:
        adult_num = len(tax_unit[~tax_unit["child"]])
        # The maximal amount to claim is 4000 per child. We only count the claim for
        # children under 14. By law the parents are also to allow to claim for disabled
        # children til the age of 25.
        eligible = tax_unit["age"] <= 14

        deductible_costs = (
            eligible
            * np.minimum(tb["childcare_max"], 12 * tax_unit["m_childcare"])
            * tb["childcare_share"]
            / adult_num
        )
        # If parents can't claim anything, they get a pausch value.
        tax_unit.loc[~tax_unit["child"], "sonder"] = max(
            np.sum(deductible_costs), tb["sonder"]
        )
        return tax_unit


def calc_gross_e7(tax_unit, tb):
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
        12 * (tax_unit["ertragsanteil"] * tax_unit["m_pensions"]) - tb["vorsorgpausch"],
        0,
    )
    return tax_unit


def vorsorge2010(tax_unit, tb):
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
        2 * tb["grvbs"] * np.select(westost, [tb["rvmaxekw"], tb["rvmaxeko"]]),
    )

    # calculate x% of relevant employer and employee contributions
    # then subtract employer contributions
    # also subtract health + care + unemployment insurance contributions
    altersvors2010 = ~tax_unit["child"] * vorsorge_year_faktor(tb["yr"]) * (
        12 * rvbeit_vors
    ) - (12 * 0.5 * rvbeit_vors)

    # These you get anyway ('Basisvorsorge').
    sonstigevors2010 = 12 * (tax_unit["pvbeit"] + 0.96 * tax_unit["gkvbeit"])
    # maybe add avbeit, but do not exceed 1900€.
    sonstigevors2010 = np.maximum(
        sonstigevors2010,
        np.minimum(sonstigevors2010 + 12 * tax_unit["avbeit"], tb["vors_sonst_max"]),
    )
    return altersvors2010.astype(int) + sonstigevors2010.astype(int)


def vorsorge2005(tax_unit, tb):
    """ Vorsorgeaufwendungen pre 2010
    Pension contributions are accounted for up to €20k.
    From this, a certain share can actually be deducted,
    starting with 60% in 2005.
    Other deductions are just added, up to a ceiling of 2400 p.a. for standard employees.

    Background: https://bit.ly/32oqCQq
    """
    tb["max_altersvors_2005"] = 20000
    tb["max_sonstige_vors_2005"] = 2400
    rvbeit_vors_max = np.minimum(tb["max_altersvors_2005"], 12 * tax_unit["rvbeit"] * 2)
    # intermediate step
    altersvors2005_int = ~tax_unit["child"] * (
        vorsorge_year_faktor(tb["yr"]) * (12 * 2 * tax_unit["rvbeit"])
        - (12 * tax_unit["rvbeit"])
    ).astype(int)
    altersvors2005 = np.minimum(rvbeit_vors_max, altersvors2005_int)

    sonstigevors2005 = ~tax_unit["child"] * np.minimum(
        tb["max_sonstige_vors_2005"],
        12 * (tax_unit["gkvbeit"] + tax_unit["avbeit"] + tax_unit["pvbeit"]),
    ).astype(int)
    return (altersvors2005 + sonstigevors2005).astype(int)


def vorsorge2004(tax_unit, tb):
    """ Vorsorgeaufwendungen up until 2004.
        - only pension and health contributions.
    """

    # Distinguish between married and singles
    # Single Taxpayer
    if not tax_unit["zveranl"].max():
        # Amount 1: Basic deduction, based on earnings. Usually zero.
        item_1 = np.maximum(
            tb["vorwegab"] - tb["kuerzquo"] * 12 * tax_unit["m_wage"], 0
        )
        # calcuate the remaining amount.
        vorsorg_rest = np.maximum(
            12 * (tax_unit["rvbeit"] + tax_unit["gkvbeit"]) - item_1, 0
        )
        # Deduct a 'Grundhöchstbetrag' (1334€ in 2004),
        # or the actual expenses if lower (which is unlikely)
        item_2 = np.minimum(tb["grundbet"], vorsorg_rest)
        # From what is left from vorsorg_rest, you may deduct 50%.
        # (up until 50% of 'Grundhöchstbetrag')
        item_3 = np.minimum(0.5 * (vorsorg_rest - item_2), 0.5 * tb["grundbet"])
    # For the married couple, the same stuff, but with tu totals.
    if tax_unit["zveranl"].max():
        item_1 = 0.5 * np.maximum(
            2 * tb["vorwegab"] - tb["kuerzquo"] * 12 * tax_unit["m_wage_tu"], 0
        )
        vorsorg_rest = 0.5 * np.maximum(
            12 * (tax_unit["rvbeit_tu"] + tax_unit["gkvbeit_tu"]) - item_1, 0
        )
        item_2 = 0.5 * np.minimum(tb["grundbet"], vorsorg_rest)
        item_3 = 0.5 * np.minimum((vorsorg_rest - item_2), 2 * tb["grundbet"])

    # Finally, add up all three amounts and assign in to the adults.
    vorsorge2004 = ~tax_unit["child"] * (item_1 + item_2 + item_3).astype(int)

    return vorsorge2004


def vorsorge04_05(tax_unit, tb):
    """ With the 2004 reform, no taxpayer was supposed to be affected negatively.
        Therefore, between 2005 and 2010, one needs to compute amounts
        (2004 and 2005 regime) and take the higher one.
        Sidenote: The 2010 ruling is *always* more beneficial than the 2005 one,
        so no need for a check there.
    """
    vors2004 = vorsorge2004(tax_unit, tb)
    vors2005 = vorsorge2005(tax_unit, tb)
    # Take the sum of both adults in the tax unit
    return np.maximum(vors2004.sum(), vors2005.sum())


def vorsorge_year_faktor(year):
    """ at several points in the calculation of *Vorsorgeaufwendungen*,
    there is year-dependent factor to be calculated.

    year: int

    returns the factor
    """
    return 0.6 + 0.02 * (min(year, 2025) - 2005)


def calc_hhfreib_until2014(tax_unit, tb):
    """Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'"""
    tax_unit["hhfreib"] = 0.0
    tax_unit.loc[tax_unit["alleinerz"], "hhfreib"] = tb["hhfreib"]
    return tax_unit


def calc_hhfreib_from2015(tax_unit, tb):
    """Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'"""
    tax_unit["hhfreib"] = 0.0
    tax_unit.loc[tax_unit["alleinerz"], "hhfreib"] = tb["hhfreib"] + (
        (tax_unit["child"].sum() - 1) * tb["hhfreib_ch"]
    )
    return tax_unit
