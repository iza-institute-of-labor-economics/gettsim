import numpy as np


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
    df = wealth_test(df, tb)
    # use these values (possibly zero now) below
    df["ar_wg_alg2_ek"] = df["ar_base_alg2_ek"] + df["wohngeld_basis_hh"]
    df["ar_kiz_alg2_ek"] = df["ar_base_alg2_ek"] + df["kiz_temp"]
    df["ar_wgkiz_alg2_ek"] = (
        df["ar_base_alg2_ek"] + df["wohngeld_basis_hh"] + df["kiz_temp"]
    )

    # calculate difference between transfers and the household need
    for v in ["base", "wg", "kiz", "wgkiz"]:
        df["fehlbedarf_" + v] = df["regelbedarf"] - df["ar_" + v + "_alg2_ek"]
        df["m_alg2_" + v] = np.maximum(df["fehlbedarf_" + v], 0)

    # check whether any of wg kiz or wg+kiz joint imply a fulfilled need.
    for v in ["wg", "kiz", "wgkiz"]:
        df[v + "_vorrang"] = (df["m_alg2_" + v] == 0) & (df["m_alg2_base"] > 0)

    # initialize final benefits
    df["m_alg2"] = df["m_alg2_base"]
    df["kiz"] = df["kiz_temp"]
    df["wohngeld"] = df["wohngeld_basis_hh"]

    # If this is the case set alg2 to zero.
    df.loc[
        (df["wg_vorrang"]) | (df["kiz_vorrang"]) | (df["wgkiz_vorrang"]), "m_alg2"
    ] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    df.loc[
        (~df["wg_vorrang"]) & (~df["wgkiz_vorrang"]) & (df["m_alg2_base"] > 0),
        "wohngeld",
    ] = 0
    df.loc[
        (~df["kiz_vorrang"]) & (~df["wgkiz_vorrang"]) & (df["m_alg2_base"] > 0), "kiz"
    ] = 0

    # Pensioners do not receive Kiz or Wohngeld.
    # They actually do not receive ALGII, too. Instead,
    # they get 'Grundleistung im Alter', which pays the same amount.
    df["n_pens"] = df["pensioner"].sum()

    for ben in ["kiz", "wohngeld", "m_alg2"]:
        df.loc[df["n_pens"] > 0, ben] = 0

    return df


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
    if "byear" not in df.columns.values:
        # Initiate birth year series
        df["byear"] = tb["yr"] - df["age"]

    # there are exemptions depending on individual age for adults
    df["ind_freib"] = 0
    df.loc[(df["byear"] >= 1948) & (~df["child"]), "ind_freib"] = (
        tb["a2ve1"] * df["age"]
    )
    df.loc[(df["byear"] < 1948), "ind_freib"] = tb["a2ve2"] * df["age"]
    # sum over individuals
    df["ind_freib_hh"] = df["ind_freib"].sum()

    # there is an overall maximum exemption
    df["maxvermfb"] = 0
    df.loc[(df["byear"] < 1948) & (~df["child"]), "maxvermfb"] = tb["a2voe1"]
    df.loc[(df["byear"].between(1948, 1957)), "maxvermfb"] = tb["a2voe1"]
    df.loc[(df["byear"].between(1958, 1963)), "maxvermfb"] = tb["a2voe3"]
    df.loc[(df["byear"] >= 1964) & (~df["child"]), "maxvermfb"] = tb["a2voe4"]
    df["maxvermfb_hh"] = df["maxvermfb"].sum()

    # add fixed amounts per child and adult
    df["vermfreibetr"] = np.minimum(
        df["maxvermfb_hh"],
        df["ind_freib_hh"]
        + df["child0_18_num"] * tb["a2vkf"]
        + (df["hhsize"] - df["child0_18_num"]) * tb["a2verst"],
    )

    # If wealth exceeds the exemption, set benefits to zero
    # (since ALG2 is not yet calculated, just set the need to zero)
    df.loc[(df["hh_wealth"] > df["vermfreibetr"]), "regelbedarf"] = 0
    df.loc[(df["hh_wealth"] > df["vermfreibetr"]), "kiz_temp"] = 0

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    df.loc[
        (df["hh_wealth"] > (60000 + (30000 * (df["hhsize"] - 1)))), "wohngeld_basis_hh"
    ] = 0

    return df
