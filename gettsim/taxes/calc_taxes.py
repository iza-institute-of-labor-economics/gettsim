import numpy as np
import pandas as pd


def tax_sched(df, tb):
    """Given various forms of income and other state variables, return
    the different taxes to be paid before making favourability checks etc..

    In particular

        * Income tax (Einkommensteuer)
        * Solidarity Surcharge (Solidaritätszuschlag)
        * Capital income tax (Abgeltungssteuer)

    """

    adult_married = (~df["child"]) & (df["zveranl"])
    # create ts dataframe and copy three important variables
    for inc in tb["zve_list"]:
        df["tax_" + inc] = tb["tax_schedule"](df["zve_" + inc], tb)
        df[f"tax_{inc}_tu"] = df[f"tax_{inc}"]
        df.loc[adult_married, f"tax_{inc}_tu"] = df[f"tax_{inc}"][adult_married].sum()

    # Abgeltungssteuer
    df["abgst"] = abgeltung(df, tb)
    df["abgst_tu"] = 0
    df.loc[adult_married, "abgst_tu"] = df["abgst"][adult_married].sum()

    """Solidarity Surcharge. on top of the income tax and capital income tax.
    No Soli if income tax due is below € 920 (solifreigrenze)
    Then it increases with 0.2 marginal rate until 5.5% (solisatz)
    of the incometax is reached.
    As opposed to the 'standard' income tax,
    child allowance is always deducted for soli calculation
    """

    if tb["yr"] >= 1991:
        df["solibasis"] = df["tax_kfb_tu"] + df["abgst_tu"]
        # Soli also in monthly terms. only for adults
        df["soli_tu"] = soli_formula(df["solibasis"], tb) * ~df["child"] * (1 / 12)
    else:
        df["soli_tu"] = 0

    # Assign Soli to individuals
    df["soli"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [df["soli_tu"] / 2, df["soli_tu"]]
    )
    return df


def abgeltung(df, tb):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    df_abgelt = pd.DataFrame(index=df.index.copy())
    df_abgelt["abgst"] = 0
    if tb["yr"] >= 2009:
        df_abgelt.loc[~df["zveranl"], "abgst"] = tb["abgst"] * np.maximum(
            df["gross_e5"] - tb["spsparf"] - tb["spwerbz"], 0
        )
        df_abgelt.loc[df["zveranl"], "abgst"] = (
            0.5
            * tb["abgst"]
            * np.maximum(df["gross_e5_tu"] - 2 * (tb["spsparf"] + tb["spwerbz"]), 0)
        )
    return df_abgelt["abgst"]


@np.vectorize
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
    if tb["yr"] < 2002:
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
