import numpy as np
import pandas as pd
from src.model_code.imports import aggr, tarif_ubi
from termcolor import cprint


def tax_sched(df, tb, yr, ref="", hyporun=False):
    """ Applies the income tax tariff for various definitions of taxable income
        also calculates tax on capital income (Abgeltungssteuer)
    """
    cprint("Income Tax...", "red", "on_white")
    # Before 2009, no separate taxation of capital income
    if (yr >= 2009) or (ref == "UBI"):
        inclist = ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]
    else:
        inclist = ["nokfb", "kfb"]

    cprint("Tax Schedule...", "red", "on_white")
    # create ts dataframe and copy three important variables
    ts = pd.DataFrame(index=df.index.copy())
    for v in ["hid", "tu_id", "zveranl"]:
        ts[v] = df[v]

    for inc in inclist:
        if ref == "UBI":
            ts["tax_" + inc] = np.vectorize(tarif_ubi)(df["zve_" + inc], tb)
        else:
            ts["tax_" + inc] = np.vectorize(tarif)(df["zve_" + inc], tb)

        if not hyporun:
            ts["tax_" + inc] = np.fix(ts["tax_" + inc])
        ts["tax_" + inc + "_tu"] = aggr(ts, "tax_" + inc, "adult_married")

    ################

    # Abgeltungssteuer
    ts["abgst"] = 0
    if yr >= 2009:
        ts.loc[~ts["zveranl"], "abgst"] = tb["abgst"] * np.maximum(
            df["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0
        )
        ts.loc[ts["zveranl"], "abgst"] = (
            0.5
            * tb["abgst"]
            * np.maximum(df["gross_e5_tu"] - 2 * (tb["spsparf"] + tb["spwerbz"]), 0)
        )

    ts["abgst_tu"] = aggr(ts, "abgst", "adult_married")
    # drop some vars to avoid duplicates in join. More elegant way would be to modifiy
    # joint command above.
    ts = ts.drop(columns=["zveranl", "hid", "tu_id"], axis=1)
    # Here, I don't specify exactly the return variables because they may differ
    # by year.
    return ts


def tarif(x, tb):
    """ The German Income Tax Tariff
    modelled only after 2002 so far

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (float): taxable income
        tb (dict): tax-benefit parameters specific to year and reform
    """
    y = int(tb["yr"])
    if y < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    else:
        t = 0.0
        if tb["G"] < x <= tb["M"]:
            t = (
                ((tb["t_m"] - tb["t_e"]) / (2 * (tb["M"] - tb["G"]))) * (x - tb["G"])
                + tb["t_e"]
            ) * (x - tb["G"])
        if tb["M"] < x <= tb["S"]:
            t = (
                ((tb["t_s"] - tb["t_m"]) / (2 * (tb["S"] - tb["M"]))) * (x - tb["M"])
                + tb["t_m"]
            ) * (x - tb["M"]) + (tb["M"] - tb["G"]) * ((tb["t_m"] + tb["t_e"]) / 2)
        if x > tb["S"]:
            t = (
                tb["t_s"] * x
                - tb["t_s"] * tb["S"]
                + ((tb["t_s"] + tb["t_m"]) / 2) * (tb["S"] - tb["M"])
                + ((tb["t_m"] + tb["t_e"]) / 2) * (tb["M"] - tb["G"])
            )
        if x > tb["R"]:
            t = t + (tb["t_r"] - tb["t_s"]) * (x - tb["R"])
        # round down to next integer
        # t = int(t)
        assert t >= 0
    return t


# @jit(nopython=True)
def zve(df, tb, yr, hyporun, ref=""):
    """Calculate taxable income (zve = zu versteuerndes Einkommen)
        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
    """
    cprint("Calculate Taxable Income...", "red", "on_white")
    # Kapitaleinkommen im Tarif versteuern oder nicht?
    kapinc_in_tarif = yr < 2009
    westost = [~df["east"], df["east"]]
    # married = [df['zveranl'], ~df['zveranl']]
    # create output dataframe and transter some important variables
    zve = pd.DataFrame(index=df.index.copy())
    for v in ["hid", "tu_id", "zveranl"]:
        zve[v] = df[v]

    # The share of pensions subject to income taxation
    zve["ertragsanteil"] = 0
    df.loc[df["renteneintritt"] <= 2004, "ertragsanteil"] = 0.27
    df.loc[df["renteneintritt"].between(2005, 2020), "ertragsanteil"] = 0.5 + 0.02 * (
        df["renteneintritt"] - 2005
    )
    df.loc[df["renteneintritt"].between(2021, 2040), "ertragsanteil"] = 0.8 + 0.01 * (
        df["renteneintritt"] - 2020
    )
    df.loc[df["renteneintritt"] >= 2041, "ertragsanteil"] = 1

    # Werbungskosten und Sonderausgaben
    zve["werbung"] = 0
    zve.loc[(~df["child"]) & (df["m_wage"] > 0), "werbung"] = tb["werbung"]
    zve["sonder"] = 0
    zve.loc[(~df["child"]), "sonder"] = tb["sonder"]
    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    zve["gross_e1"] = 12 * df["m_self"]
    # Earnings
    zve["gross_e4"] = np.maximum((12 * df["m_wage"]) - zve["werbung"], 0)
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
    zve["gross_e7"] = np.maximum(
        12 * (zve["ertragsanteil"] * df["m_pensions"]) - tb["vorsorgpausch"], 0
    )
    # Sum of incomes
    zve["gross_gde"] = zve[["gross_e1", "gross_e4", "gross_e6", "gross_e7"]].sum(axis=1)
    # Add UBI to taxable income
    if ref == "UBI":
        zve["gross_gde"] = zve["gross_gde"] + (df["ubi"] * 12)

    # If capital income tax with tariff, add it but account for exemptions
    if kapinc_in_tarif:
        zve["gross_gde"] = zve["gross_gde"] + np.maximum(
            zve["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0
        )

    # Gross (market) income <> sum of incomes...
    zve["m_brutto"] = df[
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
    # for inc in ["m_wage", "rvbeit", "gkvbeit", "avbeit", "pvbeit"]:
    #    zve[inc + "_tu_k"] = aggr(df, inc, "all_tu")
    #    zve[inc + "_tu"] = aggr(df, inc, "adult_married")
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
        sum_inc = zve[zve["zveranl"]][inc].sum()
        zve.loc[zve["zveranl"] & ~df["child"], inc + "_tu"] = 0.5 * sum_inc
        zve.loc[~zve["zveranl"] & df["child"], inc + "_tu"] = zve[inc]

    # TAX DEDUCTIONS
    # 1. VORSORGEAUFWENDUNGEN
    # TODO: check various deductions against each other (when modelled)
    zve["vorsorge"] = vorsorge2010(df, tb, yr, hyporun)
    # Summing up not necessary! they already got half
    # zve["vorsorge_tu"] = aggr(zve, "vorsorge", "all_tu")
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
    zve["altfreib_tu"] = aggr(zve, "altfreib", "adult_married")
    # Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    # Since 2015, it increases with number of children.
    # Used to be called 'Haushaltsfreibetrag'
    zve["hhfreib"] = 0
    if yr < 2015:
        zve.loc[df["alleinerz"], "hhfreib"] = tb["hhfreib"]
    if yr >= 2015:
        zve.loc[df["alleinerz"], "hhfreib"] = tb["hhfreib"] + (
            (df["child_num_tu"] - 1) * tb["hhfreib_ch"]
        )

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
    zve.loc[~zve["zveranl"] & ~df["child"], "kifreib"] = (
        0.5 * tb["kifreib"] * df["child_num_tu"]
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
        0.5 * tb["kifreib"] * df["child_num_tu"]
    )

    # For the first earner, subtract half the amount first.
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_higher"]) & zve["zveranl"], "kifreib"
    ] = (0.5 * tb["kifreib"] * df["child_num_tu"])
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
    ] = 0.5 * tb["kifreib"] * df["child_num_tu"] - abs(zve["diff_kifreib"])

    # If the second earner earns enough, deduct half the amount also for him/her
    zve.loc[
        (zve["zve_nokfb"] == zve["zve_nokfb_lower"])
        & zve["zveranl"]
        & (zve["diff_kifreib"] >= 0),
        "kifreib",
    ] = (0.5 * tb["kifreib"] * df["child_num_tu"])

    # Finally, Subtract (corrected) Child allowance
    zve.loc[~df["child"], "zve_kfb"] = np.maximum(zve["zve_nokfb"] - zve["kifreib"], 0)
    zve.loc[~df["child"], "zve_abg_kfb"] = np.maximum(
        zve["zve_abg_nokfb"] - zve["kifreib"], 0
    )
    # Finally, modify married couples income according to Splitting rule,
    # i.e. each partner get assigned half of the total income
    for incdef in ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]:
        sum_incdef = zve[zve["zveranl"]]["zve_" + incdef].sum()
        zve.loc[zve["zveranl"] & ~df["child"], "zve_" + incdef] = 0.5 * sum_incdef

    #    if not hyporun:
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


def vorsorge2010(df, tb, yr, hyporun):
    """
        'Vorsorgeaufwendungen': Deduct part of your social insurance contributions
        from your taxable income
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
        (0.6 + 0.02 * (np.minimum(yr, 2025) - 2005)) * (12 * rvbeit_vors)
        - (12 * 0.5 * rvbeit_vors)
    )
    # These you get anyway ('Basisvorsorge').
    sonstigevors2010 = 12 * (df["pvbeit"] + 0.96 * df["gkvbeit"])
    # maybe add avbeit, but do not exceed 1900€.
    sonstigevors2010 = np.maximum(
        sonstigevors2010,
        np.minimum(sonstigevors2010 + 12 * df["avbeit"], tb["vors_sonst_max"]),
    )

    if hyporun:
        vorsorge2010 = altersvors2010 + sonstigevors2010
    else:
        vorsorge2010 = np.fix(altersvors2010) + np.fix(sonstigevors2010)

    return vorsorge2010


def soli(df, tb, yr, ref=""):
    """ Solidarity Surcharge ('soli')
        on top of the income tax and capital income tax.
        No Soli if income tax due is below € 920 (solifreigrenze)
        Then it increases with 0.2 marginal rate until 5.5% (solisatz)
        of the incometax is reached.
        As opposed to the 'standard' income tax,
        child allowance is always deducted for soli calculation
    """

    soli = pd.DataFrame(index=df.index.copy())
    soli["tu_id"] = df["tu_id"]
    soli["hid"] = df["hid"]
    soli["pid"] = df["pid"]

    cprint("Solidarity Surcharge...", "red", "on_white")

    if yr >= 1991:
        if yr >= 2009:
            soli["solibasis"] = df["tax_kfb_tu"] + df["abgst_tu"]
        else:
            soli["solibasis"] = df["tax_abg_kfb_tu"]
        # Soli also in monthly terms. only for adults
        soli["soli_tu"] = soli_formula(soli["solibasis"], tb) * ~df["child"] * (1 / 12)

    # Assign income Tax + Soli to individuals
    soli["incometax"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [df["incometax_tu"] / 2, df["incometax_tu"]]
    )
    soli["soli"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [soli["soli_tu"] / 2, soli["soli_tu"]]
    )
    return soli[["incometax", "soli", "soli_tu"]]


def soli_formula(solibasis, tb):
    """ The actual soli calculation

    args:
        solibasis: taxable income, *always with Kinderfreibetrag!*
        tb (dict): tax-benefit parameters

    """
    soli = np.minimum(
        tb["solisatz"] * solibasis,
        np.maximum(0.2 * (solibasis - tb["solifreigrenze"]), 0),
    )

    return soli
