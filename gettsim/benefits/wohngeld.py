import numpy as np

from gettsim.auxiliary import aggr


def wg(df, tb):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual
        rent and differs on the municipality level ('Mietstufe' (1,...,6)).

        We usually don't have information on the last item.
        Therefore we assume 'Mietstufe' 3, corresponding to an average level,
        but other Mietstufen can be specified in `df`.
    """
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)

    hhsize = df.shape[0]
    # Caluclate income in separate function
    df["Y"] = calc_wg_income(df, tb, hhsize)
    # Caluclate rent in separate function
    df["M"] = calc_wg_rent(df, tb, hhsize)
    # Apply Wohngeld Formel.
    df["wohngeld_basis"] = apply_wg_formula(df, tb, hhsize)

    # Sum of wohngeld within household
    wg_head = df["wohngeld_basis"] * df["head_tu"]
    df.loc[:, "wohngeld_basis_hh"] = wg_head.sum()
    df = df.round({"wohngeld_basis_hh": 2})
    # df["hhsize_tu"].describe()
    # wg.to_excel(get_settings()['DATA_PATH'] + 'wg_check_hypo.xlsx')
    return df


def calc_wg_rent(df, tb, hhsize):
    """
    This function yields the relevant rent for calculating the wohngeld.
    """
    # There are also min and max values for this.
    # If 'Mietstufe' is not given, choose '3'.
    if "mietstufe" in df.columns:
        mietstufe = int(df["mietstufe"].iloc[0])
    else:
        mietstufe = 3

    assert mietstufe in range(1, 7)
    cnstyr = df["cnstyr"].iloc[0]
    # First max rent
    # Before 2009, they differed by construction year of the house
    max_rent = tb["calc_max_rent"](tb, hhsize, cnstyr, mietstufe)

    # Second min rent
    min_rent = calc_min_rent(tb, hhsize)

    # check for failed assignments
    assert not np.isnan(max_rent)
    assert not np.isnan(min_rent)

    # distribute max rent among the tax units
    max_rent_dist = max_rent * df["hh_korr"]

    wgmiete = np.minimum(max_rent_dist, df["miete"] * df["hh_korr"])
    # wg["wgheiz"] = df["heizkost"] * df["hh_korr"]
    return np.maximum(wgmiete, min_rent)


def calc_max_rent_since_2009(tb, hhsize, cnstyr, mietstufe):
    """
    Since 2009 a different formula for the maximal acknowledged rent applies.
    Now the date of the construction is irrelevant.

    cnstyr is not used, but needs to be handled for compatibility reasons
    """
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    if hhsize <= 5:
        max_rent = tb[f"wgmax{hhsize}p_m_st{mietstufe}"]
    else:
        max_rent = tb[f"wgmax5p_m_st{mietstufe}"] + tb[
            f"wgmaxplus5_m_st{mietstufe}"
        ] * (hhsize - 5)
    return max_rent


def calc_max_rent_until_2008(tb, hhsize, cnstyr, mietstufe):
    """ Before 2009, differentiate by construction year of the house and
    calculate the maximal acknowledged rent."""
    cnstyr_dict = {1: "a", 2: "m", 3: "n"}
    key = cnstyr_dict[cnstyr]
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    if hhsize <= 5:
        max_rent = tb[f"wgmax{hhsize}p_{key}_st{mietstufe}"]
    else:
        max_rent = tb[f"wgmax5p_{key}_st{mietstufe}"] + tb[
            f"wgmaxplus5_{key}_st{mietstufe}"
        ] * (hhsize - 5)
    return max_rent


def calc_min_rent(tb, hhsize):
    """ The minimal acknowledged rent depending on the household size."""
    if hhsize < 12:
        min_rent = tb["wgmin" + str(hhsize) + "p"]
    else:
        min_rent = tb["wgmin12p"]
    return min_rent


def calc_wg_income(df, tb, hhsize):
    """ This function calculates the relevant income for the calculation of the
    wohngeld."""
    # Start with income revelant for the housing beneift
    # tax-relevant share of pensions for tax unit
    df["pens_steuer"] = df["ertragsanteil"] * df["m_pensions"]
    df["pens_steuer_tu_k"] = aggr(df, "pens_steuer", "all_tu")
    # Different incomes on tu base
    for inc in [
        "m_alg1",
        "m_transfers",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "incometax",
        "rvbeit",
        "gkvbeit",
        "uhv",
    ]:
        df[f"{inc}_tu_k"] = aggr(df, inc, "all_tu")

    df["wg_abzuege"] = calc_wg_abzuege(df, tb)
    # Relevant income is market income + transfers...
    df["wg_grossY"] = calc_wg_gross_income(df)
    df["wg_otherinc"] = df[
        ["m_alg1_tu_k", "m_transfers_tu_k", "pens_steuer_tu_k", "uhv_tu_k"]
    ].sum(axis=1)

    # ... minus a couple of lump-sum deductions for handicaps,
    # children income or being single parent
    df["wg_incdeduct"] = calc_wg_income_deductions(df, tb)
    df["wg_incdeduct_tu_k"] = aggr(df, "wg_incdeduct", "all_tu")
    prelim_y = (1 - df["wg_abzuege"]) * np.maximum(
        0, (df["wg_grossY"] + df["wg_otherinc"] - df["wg_incdeduct_tu_k"])
    )
    # There's a minimum Y depending on the hh size
    return _set_min_y(prelim_y, tb, hhsize)


def calc_wg_abzuege(df, tb):
    # There share of income to be deducted is 0/10/20/30%, depending on whether
    # household is subject to income taxation and/or payroll taxes
    wg_abz = (
        (df["incometax_tu_k"] > 0) * 1
        + (df["rvbeit_tu_k"] > 0) * 1
        + (df["gkvbeit_tu_k"] > 0) * 1
    )

    wg_abz_amounts = {
        0: tb["wgpabz0"],
        1: tb["wgpabz1"],
        2: tb["wgpabz2"],
        3: tb["wgpabz3"],
    }

    return wg_abz.replace(wg_abz_amounts)


def calc_wg_gross_income(df):
    out = (
        np.maximum(df["gross_e1_tu_k"] / 12, 0)
        + np.maximum(df["gross_e4_tu_k"] / 12, 0)
        + np.maximum(df["gross_e5_tu_k"] / 12, 0)
        + np.maximum(df["gross_e6_tu_k"] / 12, 0)
    )
    return out


def calc_wg_income_deductions(df, tb):
    if tb["yr"] < 2016:
        wg_incdeduct = _calc_wg_income_deductions_until_2015(df, tb)
    else:
        wg_incdeduct = _calc_wg_income_deductions_since_2016(df, tb)
    return wg_incdeduct


def _calc_wg_income_deductions_until_2015(df, tb):
    """ calculate special deductions for handicapped, single parents
    and children who are working
    """
    workingchild = df["child"] & (df["m_wage"] > 0)
    wg_incdeduct = (
        (df["handcap_degree"] > 80) * tb["wgpfbm80"]
        + df["handcap_degree"].between(1, 80) * tb["wgpfbu80"]
        + (workingchild * np.minimum(tb["wgpfb24"], df["m_wage"]))
        + ((df["alleinerz"] & (~df["child"])) * df["child11_num_tu"] * tb["wgpfb12"])
    )
    return wg_incdeduct


def _calc_wg_income_deductions_since_2016(df, tb):
    """ calculate special deductions for handicapped, single parents
    and children who are working
    """
    workingchild = df["child"] & (df["m_wage"] > 0)
    wg_incdeduct = (
        (df["handcap_degree"] > 0) * tb["wgpfbm80"]
        + (workingchild * np.minimum(tb["wgpfb24"], df["m_wage"]))
        + (df["alleinerz"] * tb["wgpfb12"] * (~df["child"]))
    )
    return wg_incdeduct


def _set_min_y(prelim_y, tb, hhsize):
    if hhsize < 12:
        min_y = np.maximum(prelim_y, tb["wgminEK" + str(hhsize) + "p"])
    else:
        min_y = np.maximum(prelim_y, tb["wgminEK12p"])
    return min_y


def apply_wg_formula(df, tb, hhsize):
    # There are parameters a, b, c, depending on hh size
    a, b, c = calc_wg_formula_factors(tb, hhsize)
    return np.maximum(
        0, tb["wg_factor"] * (df["M"] - ((a + (b * df["M"]) + (c * df["Y"])) * df["Y"]))
    )


def calc_wg_formula_factors(tb, hhsize):
    a = tb["wg_a_" + str(hhsize) + "p"]
    b = tb["wg_b_" + str(hhsize) + "p"]
    c = tb["wg_c_" + str(hhsize) + "p"]
    return a, b, c
