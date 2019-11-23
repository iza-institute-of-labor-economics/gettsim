import numpy as np


def favorability_check(tax_unit, e_st_abzuege_data):
    """ 'Higher-Yield Test'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child
        allowance (_nokfb) AND receiving child benefit with the tax burden including
        the child allowance (_kfb), but without child benefit. The most beneficial (
        for the household) is chosen. If child allowance is claimed, kindergeld is
        set to zero. A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    tax_unit["kindergeld"] = tax_unit["kindergeld_basis"]
    tax_unit["kindergeld_tu"] = tax_unit["kindergeld_tu_basis"]
    # get the maximum income
    max_inc = get_max_inc(tax_unit, e_st_abzuege_data)
    # relevant incometax
    tax_unit.loc[:, "incometax_tu"] = 0
    # Income Tax in monthly terms! And write only to parents
    tax_unit.loc[~tax_unit["child"], "incometax_tu"] = (
        tax_unit["tax_" + max_inc + "_tu"] / 12
    )
    # set kindergeld to zero if necessary.
    if (not ("nokfb" in max_inc)) | (e_st_abzuege_data["year"] <= 1996):
        tax_unit.loc[:, "kindergeld"] = 0
        tax_unit.loc[:, "kindergeld_tu"] = 0
    if "abg" in max_inc:
        tax_unit.loc[:, "abgst"] = 0
        tax_unit.loc[:, "abgst_tu"] = 0
    # Aggregate Child benefit on the household level, as we could have several
    # tax_units in one household.
    tax_unit["kindergeld_hh"] = tax_unit["kindergeld"].sum()
    # Assign Income tax to individuals
    tax_unit["incometax"] = np.select(
        [tax_unit["zveranl"], ~tax_unit["zveranl"]],
        [tax_unit["incometax_tu"] / 2, tax_unit["incometax_tu"]],
    )

    return tax_unit


def get_max_inc(tax_unit, e_st_abzuege_data):
    """The maximal income is selected considering taxing methods differing in the
    policies on  Kinderfreibetrag or Abgeltungssteuer. """
    inc_list = []
    for i, inc in enumerate(e_st_abzuege_data["zve_list"]):
        inc_list += [tax_unit["tax_" + inc + "_tu"].max()]
        # for those tax bases without capital taxes in tariff,
        # add abgeltungssteuer
        if "abg" not in inc:
            inc_list[i] += tax_unit["abgst_tu"].iloc[0]
        # For those tax bases without kfb, subtract kindergeld.
        # Before 1996, both child allowance and child benefit could be claimed
        if ("nokfb" in inc) | (e_st_abzuege_data["year"] <= 1996):
            inc_list[i] -= (12 * tax_unit["kindergeld_tu_basis"]).iloc[0]

    # get the maximum income, i.e. the minimum payment burden
    return e_st_abzuege_data["zve_list"][np.argmin(inc_list)]
