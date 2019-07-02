import numpy as np
import pandas as pd


# @jit(nopython=True)
def zve(df, tb):
    """Calculate taxable income (zve = zu versteuerndes Einkommen)
        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
    """
    pd.options.mode.chained_assignment = "raise"
    # Kapitaleinkommen im Tarif versteuern oder nicht?
    kapinc_in_tarif = tb["yr"] < 2009
    westost = [~df["east"], df["east"]]
    adult_married = ~df["child"] & df["zveranl"]
    # married = [df['zveranl'], ~df['zveranl']]
    # create output dataframe and transter some important variables
    zve = pd.DataFrame(index=df.index.copy())
    for v in ["hid", "tu_id", "zveranl"]:
        zve[v] = df[v]

    # Werbungskosten und Sonderausgaben

    zve["sonder"] = 0
    zve.loc[(~df["child"]), "sonder"] = tb["sonder"]
    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    zve["gross_e1"] = 12 * df["m_self"]
    # Earnings
    zve["gross_e4"] = calc_gross_e4(df, tb)
    # Minijob-Grenze beachten
    zve.loc[
        df["m_wage"] <= np.select(westost, [tb["mini_grenzew"], tb["mini_grenzeo"]]),
        "gross_e4",
    ] = 0

    # Capital Income
    zve["gross_e5"] = np.maximum((12 * df["m_kapinc"]), 0)
    # Income from rents
    zve["gross_e6"] = 12 * df["m_vermiet"]
    # Others (Pensions)
    zve["gross_e7"], zve["ertragsanteil"] = calc_gross_e7(df, tb)
    # Sum of incomes
    zve["gross_gde"] = zve[["gross_e1", "gross_e4", "gross_e6", "gross_e7"]].sum(axis=1)
    # Add UBI to taxable income
    # if ref == "UBI":
    #    zve.loc[:, "gross_gde"] = zve["gross_gde"] + (df["ubi"] * 12)

    # If capital income tax with tariff, add it but account for exemptions
    if kapinc_in_tarif:
        zve.loc[:, "gross_gde"] = zve["gross_gde"] + np.maximum(
            zve["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0
        )

    # Gross (market) income <> sum of incomes...
    zve.loc[:, "m_brutto"] = df[
        ["m_self", "m_wage", "m_kapinc", "m_vermiet", "m_pensions"]
    ].sum(axis=1)

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
    zve["handc_pausch"] = np.select(hc_degrees, hc_pausch)
    zve["handc_pausch"].fillna(0, inplace=True)

    # Aggregate several incomes on the taxpayer couple
    for inc in [
        "sonder",
        "handc_pausch",
        "gross_gde",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "gross_e7",
    ]:
        zve[inc + "_tu"] = 0
        zve.loc[adult_married, inc + "_tu"] = zve[inc][adult_married].sum()

    # TAX DEDUCTIONS
    # 1. VORSORGEAUFWENDUNGEN
    # TODO: check various deductions against each other (when modelled)
    zve["vorsorge"] = vorsorge2010(df, tb)
    # 2. Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    zve["altfreib"] = 0
    zve.loc[df["age"] > 64, "altfreib"] = np.minimum(
        tb["altentq"]
        * 12
        * (
            df["m_wage"]
            + np.maximum(0, df[["m_kapinc", "m_self", "m_vermiet"]].sum(axis=1))
        ),
        tb["altenth"],
    )
    zve["altfreib_tu"] = 0
    zve.loc[adult_married, "altfreib_tu"] = zve["altfreib"][adult_married].sum()
    # Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    # Since 2015, it increases with number of children.
    # Used to be called 'Haushaltsfreibetrag'
    zve["hhfreib"] = 0
    zve.loc[df["alleinerz"], "hhfreib"] = tb["calc_hhfreib"](df, tb)

    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    zve.loc[~df["child"], "zve_nokfb"] = np.maximum(
        0,
        zve["gross_gde"]
        - zve["vorsorge"]
        - zve["sonder"]
        - zve["handc_pausch"]
        - zve["hhfreib"]
        - zve["altfreib"],
    )
    # Tax base incl. capital income
    zve.loc[~df["zveranl"] & ~df["child"], "zve_abg_nokfb"] = np.maximum(
        0,
        zve["gross_gde"]
        + np.maximum(0, zve["gross_e5"] - tb["spsparf"] - tb["spwerbz"])
        - zve["vorsorge"]
        - zve["sonder"]
        - zve["handc_pausch"]
        - zve["hhfreib"]
        - zve["altfreib"],
    )
    # Married couples get twice the basic allowance
    zve.loc[df["zveranl"] & ~df["child"], "zve_abg_nokfb"] = np.maximum(
        0,
        zve["gross_gde"]
        + np.maximum(0, zve["gross_e5"] - 2 * tb["spsparf"] - 2 * tb["spwerbz"])
        - zve["vorsorge"]
        - zve["sonder"]
        - zve["handc_pausch"]
        - zve["hhfreib"]
        - zve["altfreib"],
    )

    # Child Allowance (Kinderfreibetrag)
    # Married couples may share deductions if one partner does not need it.
    # For non-married, just deduct half the amount for each child.
    # TODO: Check whether this is correct for non-married couples

    zve["kifreib"] = 0
    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    zve["child_num_kg"] = tb["childben_elig_rule"](df, tb).sum()

    zve.loc[~zve["zveranl"] & ~df["child"], "kifreib"] = (
        0.5 * tb["kifreib"] * zve["child_num_kg"]
    )
    # For married couples, things are more complicated
    # Find out who has higher and lower zve among partners
    zve = zve.join(
        zve[zve["zveranl"]].groupby("tu_id")["zve_nokfb"].max(),
        on=["tu_id"],
        how="left",
        rsuffix="_higher",
    )
    zve = zve.join(
        zve[zve["zveranl"]].groupby("tu_id")["zve_nokfb"].min(),
        on=["tu_id"],
        how="left",
        rsuffix="_lower",
    )
    # the difference of the lower value to the child allowance is what the first earner
    # can claim.
    zve["diff_kifreib"] = zve["zve_nokfb_lower"] - (
        0.5 * tb["kifreib"] * zve["child_num_kg"]
    )

    # For the first earner, subtract half the amount first.
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_higher"]) & zve["zveranl"], "kifreib"
    ] = (0.5 * tb["kifreib"] * zve["child_num_kg"])
    # Then subtract also the amount transferred from the second earner.
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_higher"])
        & zve["zveranl"]
        & (zve["diff_kifreib"] < 0),
        "kifreib",
    ] = zve["kifreib"] + abs(zve["diff_kifreib"])
    # The second earner subtracts the remaining amount
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_lower"])
        & zve["zveranl"]
        & (zve["diff_kifreib"] < 0),
        "kifreib",
    ] = 0.5 * tb["kifreib"] * zve["child_num_kg"] - abs(zve["diff_kifreib"])

    # If the second earner earns enough, deduct half the amount also for him/her
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_lower"])
        & zve["zveranl"]
        & (zve["diff_kifreib"] >= 0),
        "kifreib",
    ] = (0.5 * tb["kifreib"] * zve["child_num_kg"])

    # Finally, Subtract (corrected) Child allowance
    zve.loc[~df["child"], "zve_kfb"] = np.maximum(zve["zve_nokfb"] - zve["kifreib"], 0)
    zve.loc[~df["child"], "zve_abg_kfb"] = np.maximum(
        zve["zve_abg_nokfb"] - zve["kifreib"], 0
    )
    # Finally, modify married couples income according to Splitting rule,
    # i.e. each partner get assigned half of the total income
    for incdef in ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]:
        zve["zve_" + incdef + "_tu"] = zve["zve_" + incdef][adult_married].sum()
        zve.loc[adult_married, "zve_" + incdef] = 0.5 * zve["zve_" + incdef + "_tu"]

    #        print("Sum of gross income: {} bn €".format(
    #                    (zve['gross_gde'] * df['pweight']).sum()/1e9
    #                )
    #              )
    #        print("Sum of taxable income: {} bn €".format(
    #                    (zve['zve_nokfb'] * df['pweight']).sum()/1e9
    #                )
    #              )

    return zve[
        [
            "zve_nokfb",
            "zve_abg_nokfb",
            "zve_kfb",
            "zve_abg_kfb",
            "kifreib",
            "gross_e1",
            "gross_e4",
            "gross_e5",
            "gross_e6",
            "gross_e7",
            "gross_e1_tu",
            "gross_e4_tu",
            "gross_e5_tu",
            "gross_e6_tu",
            "gross_e7_tu",
            "ertragsanteil",
        ]
    ]


def calc_gross_e4(df, tb):
    """Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'werbungskosten'"""
    werbung = pd.Series(index=df.index, data=0)
    werbung[(~df["child"]) & (df["m_wage"] > 0)] = tb["werbung"]
    return np.maximum((12 * df["m_wage"]) - werbung, 0)


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

    return vorsorge2010


def calc_hhfreib_until2014(df, tb):
    return tb["hhfreib"]


def calc_hhfreib_from2015(df, tb):
    return tb["hhfreib"] + ((df["child_num_tu"] - 1) * tb["hhfreib_ch"])
