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
    df["kindergeld"] = df["kindergeld_basis"]
    df["kindergeld_tu"] = df["kindergeld_tu_basis"]
    nettaxes = calc_nettax(df, tb)
    # get the maximum income, i.e. the minimum payment burden
    min_inc = nettaxes.idxmin()
    # relevant incometax
    df.loc[:, "incometax_tu"] = 0
    # Income Tax in monthly terms! And write only to parents
    df.loc[~df["child"], "incometax_tu"] = df["tax_" + min_inc + "_tu"] / 12
    # set kindergeld to zero if necessary.
    if (not ("nokfb" in min_inc)) | (tb["yr"] <= 1996):
        df.loc[:, "kindergeld"] = 0
        df.loc[:, "kindergeld_tu"] = 0
    if "abg" in min_inc:
        df.loc[:, "abgst"] = 0
        df.loc[:, "abgst_tu"] = 0
    # TODO: Why do we calculate that? Can we not just set it as tu?
    # Aggregate Child benefit on the household.
    df["kindergeld_hh"] = df["kindergeld"].sum()
    # Assign Income tax to individuals
    df["incometax"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [df["incometax_tu"] / 2, df["incometax_tu"]]
    )

    return df


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
