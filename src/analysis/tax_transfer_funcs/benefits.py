import numpy as np
import pandas as pd


def benefit_priority(df, tb):
    """There are three main transfers for working-age people:
        1. Unemployment Benefit / ALG2
        2. Housing Benefit / Wohngeld
        3. Additional Child Benefit / Kinderzuschlag

    There is a rule which benefits are superior to others
    If there is a positive ALG2 entitlement, but the need can be covered with
    Housing Benefit (and possibly add. child benefit),
    the HH *has* to claim the housing benefit and addit. child benefit.
    If the household need cannot be covered via Wohngeld, he has to apply for ALG2.
    There is no way you can receive ALG2 and Wohngeld/Kinderzuschlag at the same time!
    """
    # But first, we check whether hh wealth is too high
    bp = wealth_test(
        df[
            [
                "pid",
                "hid",
                "tu_id",
                "regelbedarf",
                "ar_base_alg2_ek",
                "wohngeld_basis_hh",
                "kiz_temp",
                "child",
                "hh_wealth",
                "age",
                "hhsize",
                "adult_num",
                "child0_18_num",
            ]
        ],
        tb,
    )

    # use these values (possibly zero now) below
    bp["ar_base_alg2_ek"] = df["ar_base_alg2_ek"]
    bp["ar_wg_alg2_ek"] = bp["ar_base_alg2_ek"] + bp["wohngeld_basis_hh"]
    bp["ar_kiz_alg2_ek"] = bp["ar_base_alg2_ek"] + bp["kiz_temp"]
    bp["ar_wgkiz_alg2_ek"] = (
        bp["ar_base_alg2_ek"] + bp["wohngeld_basis_hh"] + bp["kiz_temp"]
    )

    # calculate difference between transfers and the household need
    for v in ["base", "wg", "kiz", "wgkiz"]:
        bp["fehlbedarf_" + v] = bp["regelbedarf"] - bp["ar_" + v + "_alg2_ek"]
        bp["m_alg2_" + v] = np.maximum(bp["fehlbedarf_" + v], 0)

    # check whether any of wg kiz or wg+kiz joint imply a fulfilled need.
    for v in ["wg", "kiz", "wgkiz"]:
        bp[v + "_vorrang"] = (bp["m_alg2_" + v] == 0) & (bp["m_alg2_base"] > 0)

    # initialize final benefits
    bp["m_alg2"] = bp["m_alg2_base"]
    bp["kiz"] = bp["kiz_temp"]
    bp["wohngeld"] = bp["wohngeld_basis_hh"]

    # If this is the case set alg2 to zero.
    bp.loc[
        (bp["wg_vorrang"]) | (bp["kiz_vorrang"]) | (bp["wgkiz_vorrang"]), "m_alg2"
    ] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    bp.loc[
        (~bp["wg_vorrang"]) & (~bp["wgkiz_vorrang"]) & (bp["m_alg2_base"] > 0),
        "wohngeld",
    ] = 0
    bp.loc[
        (~bp["kiz_vorrang"]) & (~bp["wgkiz_vorrang"]) & (bp["m_alg2_base"] > 0), "kiz"
    ] = 0

    # Pensioners do not receive Kiz or Wohngeld.
    # They actually do not receive ALGII, too. Instead,
    # they get 'Grundleistung im Alter', which pays the same amount.
    bp["n_pens"] = df["pensioner"].sum()

    for ben in ["kiz", "wohngeld", "m_alg2"]:
        bp.loc[bp["n_pens"] > 0, ben] = 0
        assert bp[ben].notna().all()

    return bp[["kiz", "wohngeld", "m_alg2"]]


def wealth_test(df, tb):
    """ Checks Benefit Claim against Household wealth.
        - df: a dataframe containing information on theoretical claim of
              - ALG2
              - Kiz
              - Wohngeld
          as well as age of each hh member

    For ALG2 and Kiz, there are wealth exemptions for every year.
    For Wohngeld, there is a lump-sum amount depending on the household size
    """

    wt = pd.DataFrame(index=df.index)
    for v in ["regelbedarf", "wohngeld_basis_hh", "kiz_temp"]:
        wt[v] = df[v]
    # Initiate birth year series
    wt["byear"] = tb["yr"] - df["age"]

    # there are exemptions depending on individual age for adults
    wt["ind_freib"] = 0
    wt.loc[(wt["byear"] >= 1948) & (~df["child"]), "ind_freib"] = (
        tb["a2ve1"] * df["age"]
    )
    wt.loc[(wt["byear"] < 1948), "ind_freib"] = tb["a2ve2"] * df["age"]
    # sum over individuals
    wt["ind_freib_hh"] = wt["ind_freib"].sum()

    # there is an overall maximum exemption
    wt["maxvermfb"] = 0
    wt.loc[(wt["byear"] < 1948) & (~df["child"]), "maxvermfb"] = tb["a2voe1"]
    wt.loc[(wt["byear"].between(1948, 1957)), "maxvermfb"] = tb["a2voe1"]
    wt.loc[(wt["byear"].between(1958, 1963)), "maxvermfb"] = tb["a2voe3"]
    wt.loc[(wt["byear"] >= 1964) & (~df["child"]), "maxvermfb"] = tb["a2voe4"]
    wt["maxvermfb_hh"] = wt["maxvermfb"].sum()

    # add fixed amounts per child and adult
    wt["vermfreibetr"] = np.minimum(
        wt["maxvermfb_hh"],
        wt["ind_freib_hh"]
        + df["child0_18_num"] * tb["a2vkf"]
        + (df["hhsize"] - df["child0_18_num"]) * tb["a2verst"],
    )

    # If wealth exceeds the exemption, set benefits to zero
    # (since ALG2 is not yet calculated, just set the need to zero)
    wt.loc[(df["hh_wealth"] > wt["vermfreibetr"]), "regelbedarf"] = 0
    wt.loc[(df["hh_wealth"] > wt["vermfreibetr"]), "kiz_temp"] = 0

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    wt.loc[
        (df["hh_wealth"] > (60000 + (30000 * (df["hhsize"] - 1)))), "wohngeld_basis_hh"
    ] = 0
    for v in ["regelbedarf", "wohngeld_basis_hh", "kiz_temp"]:
        assert wt[v].notna().all()

    return wt[["regelbedarf", "wohngeld_basis_hh", "kiz_temp"]]
