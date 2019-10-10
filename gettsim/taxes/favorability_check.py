import numpy as np
import pandas as pd


def favorability_check(df, tb):
    """ 'Higher-Yield Test'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child
        allowance (_nokfb) AND receiving child benefit with the tax burden including
        the child allowance (_kfb), but without child benefit. The most beneficial (
        for the household) is chosen. If child allowance is claimed, kindergeld is
        set to zero. A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    fc = pd.DataFrame(index=df.index)
    fc["kindergeld"] = df["kindergeld_basis"]
    fc["kindergeld_tu"] = df["kindergeld_tu_basis"]

    nettaxes = calc_nettax(df, tb)
    # get the maximum income, i.e. the minimum payment burden
    min_inc = nettaxes.idxmin()
    # relevant incometax
    fc["incometax_tu"] = 0
    # Income Tax in monthly terms! And write only to parents
    fc.loc[~df["child"], "incometax_tu"] = df["tax_" + min_inc + "_tu"] / 12
    # set kindergeld to zero if necessary.
    if (not ("nokfb" in min_inc)) | (tb["yr"] <= 1996):
        fc.loc[:, "kindergeld"] = 0
        fc.loc[:, "kindergeld_tu"] = 0
    if "abg" in min_inc:
        fc.loc[:, "abgst"] = 0
        fc.loc[:, "abgst_tu"] = 0
    # Why do we calculate that? Can we not just set it as tu?
    # Aggregate Child benefit on the household.
    fc["kindergeld_hh"] = fc["kindergeld"].sum()
    # Assign Income tax to individuals
    fc["incometax"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [fc["incometax_tu"] / 2, fc["incometax_tu"]]
    )

    return fc[
        ["incometax_tu", "incometax", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
    ]


def calc_nettax(df, tb):
    """Nettax is defined on the maximum within the tax unit.
    Reason: This way, kids get assigned the tax payments of their parents,
    ensuring correct treatment afterwards"""
    nettaxes = pd.Series()
    for inc in tb["zve_list"]:
        nettaxes[inc] = df["tax_" + inc + "_tu"].max()
        # for those tax bases without capital taxes in tariff,
        # add abgeltungssteuer
        if "abg" not in inc:
            nettaxes[inc] += df["abgst_tu"].iloc[0]
        # For those tax bases without kfb, subtract kindergeld.
        # Before 1996, both child allowance and child benefit could be claimed
        if ("nokfb" in inc) | (tb["yr"] <= 1996):
            nettaxes[inc] -= (12 * df["kindergeld_tu_basis"]).iloc[0]

    return nettaxes
