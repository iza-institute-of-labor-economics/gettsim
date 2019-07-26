import numpy as np
import pandas as pd


def favorability_check(df, tb):
    """ 'Higher-Yield Tepst'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child
        allowance (_nokfb) AND receiving child benefit with the tax burden including
        the child allowance (_kfb), but without child benefit. The most beneficial (
        for the household) is chocen. If child allowance is claimed, kindergeld is
        set to zero A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    fc = pd.DataFrame(index=df.index.copy())
    fc["tu_id"] = df["tu_id"]
    fc["hid"] = df["hid"]
    fc["pid"] = df["pid"]
    fc["kindergeld"] = df["kindergeld_basis"]
    fc["kindergeld_tu"] = df["kindergeld_tu_basis"]

    for inc in tb["zve_list"]:
        # Nettax is defined on the maximum within the tax unit.
        # Reason: This way, kids get assigned the tax payments of their parents,
        # ensuring correct treatment afterwards
        fc["tax_" + inc + "_tu"] = df["tax_" + inc + "_tu"]
        fc = fc.join(
            fc.groupby(["tu_id"])["tax_" + inc + "_tu"].max(),
            on=["tu_id"],
            how="left",
            rsuffix="_max",
        )
        fc = fc.rename(columns={"tax_" + inc + "_tu_max": "nettax_" + inc})
        # for those tax bases without capital taxes in tariff,
        # add abgeltungssteuer
        if "abg" not in inc:
            fc["nettax_" + inc] = fc["nettax_" + inc] + df["abgst_tu"]
        # For those tax bases without kfb, subtract kindergeld.
        # Before 1996, both child allowance and child benefit could be claimed
        if ("nokfb" in inc) | (tb["yr"] <= 1996):
            fc["nettax_" + inc] = fc["nettax_" + inc] - (12 * df["kindergeld_tu_basis"])
    # get the maximum income, i.e. the minimum payment burden
    fc["minpay"] = fc.filter(regex="nettax").min(axis=1)
    # relevant tax base. not really needed...
    # fc['tax_income'] = 0
    # relevant incometax
    fc["incometax_tu"] = 0
    # secures that every tax unit gets 'treated'
    fc["abgehakt"] = False
    for inc in tb["zve_list"]:
        """
        fc.loc[(fc['minpay'] == fc['nettax_' + inc])
               & (~fc['abgehakt'])
               & (~df['child']),
               'tax_income'] = df['zve_'+inc]
        """
        # Income Tax in monthly terms! And write only to parents
        fc.loc[
            (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]) & (~df["child"]),
            "incometax_tu",
        ] = (df["tax_" + inc + "_tu"] / 12)
        # set kindergeld to zero if necessary.
        if (not ("nokfb" in inc)) | (tb["yr"] <= 1996):
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "kindergeld"
            ] = 0
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]),
                "kindergeld_tu",
            ] = 0
        if "abg" in inc:
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "abgst"
            ] = 0
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "abgst_tu"
            ] = 0
        fc.loc[(fc["minpay"] == fc["nettax_" + inc]), "abgehakt"] = True

    # Aggregate Child benefit on the household.
    fc["kindergeld_hh"] = fc["kindergeld"].sum()
    # Assign Income tax to individuals
    fc["incometax"] = np.select(
        [df["zveranl"], ~df["zveranl"]], [fc["incometax_tu"] / 2, fc["incometax_tu"]]
    )

    return fc[
        [
            "hid",
            "pid",
            "incometax_tu",
            "incometax",
            "kindergeld",
            "kindergeld_hh",
            "kindergeld_tu",
        ]
    ]
