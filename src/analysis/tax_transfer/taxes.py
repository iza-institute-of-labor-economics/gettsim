import numpy as np
import pandas as pd
from src.model_code.imports import tarif_ubi
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

    adult_married = (~df["child"]) & (df["zveranl"])
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
        ts["tax_{}_tu".format(inc)] = ts["tax_{}".format(inc)][adult_married].sum()

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

    ts["abgst_tu"] = ts["abgst"][adult_married].sum()
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
