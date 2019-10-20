import numpy as np
import pandas as pd


def zve(df, tb):
    """Calculate taxable income (zve = zu versteuerndes Einkommen). The calculation
    of the 6 branches of income is according to
    https://de.wikipedia.org/wiki/Einkommensteuer_(Deutschland)#Rechenschema

        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
    """
    adult_married = ~df["child"] & df["zveranl"]
    # married = [df['zveranl'], ~df['zveranl']]
    # create output dataframe and transter some important variables

    # Sonderausgaben
    df = deductible_child_care_costs(df, tb)

    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    df.loc[:, "gross_e1"] = 12 * df["m_self"]
    # Earnings
    df.loc[:, "gross_e4"] = calc_gross_e4(df, tb)
    # Capital Income
    df.loc[:, "gross_e5"] = np.maximum((12 * df["m_kapinc"]), 0)
    # Income from rents
    df.loc[:, "gross_e6"] = 12 * df["m_vermiet"]
    # Others (Pensions)
    df.loc[:, "gross_e7"], df["ertragsanteil"] = calc_gross_e7(df, tb)
    # Sum of incomes
    df.loc[:, "gross_gde"] = calc_gde(df, tb)

    # Gross (market) income <> sum of incomes...
    df.loc[:, "m_brutto"] = df[
        ["m_self", "m_wage", "m_kapinc", "m_vermiet", "m_pensions"]
    ].sum(axis=1)

    df.loc[:, "handc_pausch"] = calc_handicap_lump_sum(df, tb)

    # Aggregate several incomes on the taxpayer couple
    for inc in ["gross_e1", "gross_e4", "gross_e5", "gross_e6", "gross_e7"]:
        df.loc[adult_married, inc + "_tu"] = df[inc][adult_married].sum()

    # TAX DEDUCTIONS
    # 1. VORSORGEAUFWENDUNGEN
    # TODO: check various deductions against each other (when modelled)
    df.loc[:, "vorsorge"] = tb["vorsorge"](df, tb)
    # 2. Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    df = calc_altfreibetrag(df, tb)

    # Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    df = tb["calc_hhfreib"](df, tb)

    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    df.loc[~df["child"], "zve_nokfb"] = zve_nokfb(df, tb)
    # Tax base including capital income
    df = zve_abg_nokfb(df, tb)

    df = kinderfreibetrag(df, tb)

    # Finally, Subtract (corrected) Child allowance
    df.loc[~df["child"], "zve_kfb"] = np.maximum(df["zve_nokfb"] - df["kifreib"], 0)
    df.loc[~df["child"], "zve_abg_kfb"] = np.maximum(
        df["zve_abg_nokfb"] - df["kifreib"], 0
    )
    # Finally, modify married couples income according to Splitting rule,
    # i.e. each partner get assigned half of the total income
    for incdef in ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]:
        df.loc[:, "zve_" + incdef + "_tu"] = df["zve_" + incdef][adult_married].sum()
        df.loc[adult_married, "zve_" + incdef] = 0.5 * df["zve_" + incdef + "_tu"]

    return df


def kinderfreibetrag(df, tb):
    """Calculate zve with Child Allowance (Kinderfreibetrag)"""
    df["kifreib"] = 0.0
    #
    # Married couples may share deductions if one partner does not need it.
    # For non-married, just deduct half the amount for each child.
    # TODO: Check whether this is correct for non-married couples

    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    child_num_kg = tb["childben_elig_rule"](df, tb).sum()

    # Find out who has the lower zve among partners
    nokfb_lower = df["zve_nokfb"].min()

    diff_kifreib = nokfb_lower - (0.5 * tb["kifreib"] * child_num_kg)

    # If the couple is married and one earns not enough to split the kinderfeibetrag,
    # things get a bit more complicated
    if diff_kifreib < 0 & df[~df["child"]]["zveranl"].all():

        # The high earner gets half of the total kinderfreibetrag plus the amount the
        # lower earner can't claim.
        kifreib_higher = (0.5 * tb["kifreib"] * child_num_kg) + abs(diff_kifreib)
        # The second earner subtracts the remaining amount
        kifreib_lower = 0.5 * tb["kifreib"] * child_num_kg - abs(diff_kifreib)
        # Then we assign each earner the amount and return the series
        df.loc[
            ~df["child"] & df["zve_nokfb"] != nokfb_lower, "kifreib"
        ] = kifreib_higher
        df.loc[~df["child"] & df["zve_nokfb"] == nokfb_lower, "kifreib"] = kifreib_lower

        return df

    # For non married couples or couples where both earn enough this are a lot easier.
    # Just split the kinderfreibetrag 50/50.
    else:
        df.loc[~df["child"], "kifreib"] = 0.5 * tb["kifreib"] * child_num_kg
        return df


def zve_nokfb(df, tb):
    """Calculate zve with no 'kinderfreibetrag'."""
    return np.maximum(
        0,
        df["gross_gde"]
        - df["vorsorge"]
        - df["sonder"]
        - df["handc_pausch"]
        - df["hhfreib"]
        - df["altfreib"],
    )


def zve_abg_nokfb(df, tb):
    """Calculates the zve with capital income in the tax base."""
    if df[~df["child"]]["zveranl"].all():
        df.loc[~df["child"], "zve_abg_nokfb"] = np.maximum(
            0,
            df["gross_gde"]
            + np.maximum(0, df["gross_e5"] - 2 * tb["spsparf"] - 2 * tb["spwerbz"])
            - df["vorsorge"]
            - df["sonder"]
            - df["handc_pausch"]
            - df["hhfreib"]
            - df["altfreib"],
        )
    else:
        df.loc[~df["child"], "zve_abg_nokfb"] = np.maximum(
            0,
            df["gross_gde"]
            + np.maximum(0, df["gross_e5"] - tb["spsparf"] - tb["spwerbz"])
            - df["vorsorge"]
            - df["sonder"]
            - df["handc_pausch"]
            - df["hhfreib"]
            - df["altfreib"],
        )
    return df


def calc_altfreibetrag(df, tb):
    """Calculates the deductions for elderly. Not tested yet!!!"""
    df["altfreib"] = 0.0
    df.loc[df["age"] > 64, "altfreib"] = np.minimum(
        tb["altentq"]
        * 12
        * (
            df["m_wage"]
            + np.maximum(0, df[["m_kapinc", "m_self", "m_vermiet"]].sum(axis=1))
        ),
        tb["altenth"],
    )
    return df


def calc_handicap_lump_sum(df, tb):
    """Calculate the different deductions for different handicap degrees."""
    # Behinderten-Pauschbeträge
    hc_degrees = [
        df["handcap_degree"].between(45, 50),
        df["handcap_degree"].between(51, 60),
        df["handcap_degree"].between(61, 70),
        df["handcap_degree"].between(71, 80),
        df["handcap_degree"].between(81, 90),
        df["handcap_degree"].between(91, 100),
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


def calc_gde(df, tb):
    """Calculates sum of the taxable income. It depends on the year if capital
    income, counts into the sum."""
    gross_gde = df[["gross_e1", "gross_e4", "gross_e6", "gross_e7"]].sum(axis=1)

    # Add UBI to taxable income
    # if ref == "UBI":
    #    zve.loc[:, "gross_gde"] = zve["gross_gde"] + (df["ubi"] * 12)

    # Kapitaleinkommen im Tarif versteuern oder nicht?
    # If capital income tax with tariff, add it but account for exemptions
    if tb["yr"] < 2009:
        gross_gde += np.maximum(df["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0)
    return gross_gde


def calc_gross_e4(df, tb):
    """Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'"""
    # Every adult with some wage, gets a lump sum payment for Werbungskosten
    werbung = pd.Series(index=df.index, data=0)
    werbung[(~df["child"]) & (df["m_wage"] > 0)] = tb["werbung"]

    gross_e4 = (12 * df["m_wage"]).subtract(werbung)

    # If they earn less the mini job limit, then their relevant gross income is 0
    if df.east.iloc[0]:
        mini = tb["mini_grenzeo"]
    else:
        mini = tb["mini_grenzew"]

    gross_e4[df["m_wage"] <= mini] = 0
    return gross_e4


def deductible_child_care_costs(df, tb):
    """Calculating sonderausgaben for childcare. We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg."""
    # So far we only implement the current regulation, which is since 2012 is in place.
    if tb["yr"] < 2012:
        # For earlier years we only use the pausch value
        df.loc[~df["child"], "sonder"] = tb["sonder"]
        return df
    else:
        adult_num = len(df[~df["child"]])
        # The maximal amount to claim is 4000 per child. We only count the claim for
        # children under 14. By law the parents are also to allow to claim for disabled
        # children til the age of 25.
        eligible = df["age"] <= 14

        deductible_costs = (
            eligible
            * np.minimum(tb["childcare_max"], 12 * df["m_childcare"])
            * tb["childcare_share"]
            / adult_num
        )
        # If parents can't claim anything, they get a pausch value.

        df.loc[~df["child"], "sonder"] = max(np.sum(deductible_costs), tb["sonder"])
        return df


def calc_gross_e7(df, tb):
    """ Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions."""
    # The share of pensions subject to income taxation
    ertragsanteil = pd.Series(index=df.index, data=0)
    ertragsanteil[df["renteneintritt"] <= 2004] = 0.27
    ertragsanteil[df["renteneintritt"].between(2005, 2020)] = 0.5 + 0.02 * (
        df["renteneintritt"] - 2005
    )
    ertragsanteil[df["renteneintritt"].between(2021, 2040)] = 0.8 + 0.01 * (
        df["renteneintritt"] - 2020
    )
    ertragsanteil[df["renteneintritt"] >= 2041] = 1
    gross_e7 = np.maximum(
        12 * (ertragsanteil * df["m_pensions"]) - tb["vorsorgpausch"], 0
    )
    return gross_e7, ertragsanteil


def vorsorge2010(df, tb):
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
    westost = [~df["east"], df["east"]]
    rvbeit_vors = np.minimum(
        2 * df["rvbeit"],
        2 * tb["grvbs"] * np.select(westost, [tb["rvmaxekw"], tb["rvmaxeko"]]),
    )

    # calculate x% of relevant employer and employee contributions
    # then subtract employer contributions
    # also subtract health + care + unemployment insurance contributions
    altersvors2010 = ~df["child"] * (
        (0.6 + 0.02 * (np.minimum(tb["yr"], 2025) - 2005)) * (12 * rvbeit_vors)
        - (12 * 0.5 * rvbeit_vors)
    )
    # These you get anyway ('Basisvorsorge').
    sonstigevors2010 = 12 * (df["pvbeit"] + 0.96 * df["gkvbeit"])
    # maybe add avbeit, but do not exceed 1900€.
    sonstigevors2010 = np.maximum(
        sonstigevors2010,
        np.minimum(sonstigevors2010 + 12 * df["avbeit"], tb["vors_sonst_max"]),
    )

    vorsorge2010 = altersvors2010 + sonstigevors2010

    return vorsorge2010.astype(int)


def vorsorge_dummy(df, tb):
    return 0


def calc_hhfreib_until2014(df, tb):
    """Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'"""
    df["hhfreib"] = 0.0
    df.loc[df["alleinerz"], "hhfreib"] = tb["hhfreib"]
    return df


def calc_hhfreib_from2015(df, tb):
    """Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'"""
    df["hhfreib"] = 0.0
    df.loc[df["alleinerz"], "hhfreib"] = tb["hhfreib"] + (
        (df["child"].sum() - 1) * tb["hhfreib_ch"]
    )
    return df
