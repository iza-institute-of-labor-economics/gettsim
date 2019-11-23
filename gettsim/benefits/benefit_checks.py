import numpy as np


def benefit_priority(household, params):
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
    household = wealth_test(household, params)
    # use these values (possibly zero now) below
    household["ar_wg_alg2_ek"] = (
        household["ar_base_alg2_ek"] + household["wohngeld_basis_hh"]
    )
    household["ar_kiz_alg2_ek"] = household["ar_base_alg2_ek"] + household["kiz_temp"]
    household["ar_wgkiz_alg2_ek"] = (
        household["ar_base_alg2_ek"]
        + household["wohngeld_basis_hh"]
        + household["kiz_temp"]
    )

    # calculate difference between transfers and the household need
    for v in ["base", "wg", "kiz", "wgkiz"]:
        household["fehlbedarf_" + v] = (
            household["regelbedarf"] - household["ar_" + v + "_alg2_ek"]
        )
        household["m_alg2_" + v] = np.maximum(household["fehlbedarf_" + v], 0)

    # check whether any of wg kiz or wg+kiz joint imply a fulfilled need.
    for v in ["wg", "kiz", "wgkiz"]:
        household[v + "_vorrang"] = (household["m_alg2_" + v] == 0) & (
            household["m_alg2_base"] > 0
        )

    # initialize final benefits
    household["m_alg2"] = household["m_alg2_base"]
    household["kiz"] = household["kiz_temp"]
    household["wohngeld"] = household["wohngeld_basis_hh"]

    # If this is the case set alg2 to zero.
    household.loc[
        (household["wg_vorrang"])
        | (household["kiz_vorrang"])
        | (household["wgkiz_vorrang"]),
        "m_alg2",
    ] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    household.loc[
        (~household["wg_vorrang"])
        & (~household["wgkiz_vorrang"])
        & (household["m_alg2_base"] > 0),
        "wohngeld",
    ] = 0
    household.loc[
        (~household["kiz_vorrang"])
        & (~household["wgkiz_vorrang"])
        & (household["m_alg2_base"] > 0),
        "kiz",
    ] = 0

    # Pensioners do not receive Kiz or Wohngeld.
    # They actually do not receive ALGII, too. Instead,
    # they get 'Grundleistung im Alter', which pays the same amount.
    household["n_pens"] = household["pensioner"].sum()

    for ben in ["kiz", "wohngeld", "m_alg2"]:
        household.loc[household["n_pens"] > 0, ben] = 0

    return household


def wealth_test(household, arbeitsl_geld_2_params):
    """ Checks Benefit Claim against Household wealth.
        - household: a dataframe containing information on theoretical claim of
              - ALG2
              - Kiz
              - Wohngeld
          as well as age of each hh member

    For ALG2 and Kiz, there are wealth exemptions for every year.
    For Wohngeld, there is a lump-sum amount depending on the household size
    """

    # there are exemptions depending on individual age for adults
    household["ind_freib"] = 0
    household.loc[(household["byear"] >= 1948) & (~household["child"]), "ind_freib"] = (
        arbeitsl_geld_2_params["a2ve1"] * household["age"]
    )
    household.loc[(household["byear"] < 1948), "ind_freib"] = (
        arbeitsl_geld_2_params["a2ve2"] * household["age"]
    )
    # sum over individuals
    household["ind_freib_hh"] = household["ind_freib"].sum()

    # there is an overall maximum exemption
    household["maxvermfb"] = 0
    household.loc[
        (household["byear"] < 1948) & (~household["child"]), "maxvermfb"
    ] = arbeitsl_geld_2_params["a2voe1"]
    household.loc[
        (household["byear"].between(1948, 1957)), "maxvermfb"
    ] = arbeitsl_geld_2_params["a2voe1"]
    household.loc[
        (household["byear"].between(1958, 1963)), "maxvermfb"
    ] = arbeitsl_geld_2_params["a2voe3"]
    household.loc[
        (household["byear"] >= 1964) & (~household["child"]), "maxvermfb"
    ] = arbeitsl_geld_2_params["a2voe4"]
    household["maxvermfb_hh"] = household["maxvermfb"].sum()

    household_size = household.shape[0]
    # add fixed amounts per child and adult
    household["vermfreibetr"] = np.minimum(
        household["maxvermfb_hh"],
        household["ind_freib_hh"]
        + household["child0_18_num"] * arbeitsl_geld_2_params["a2vkf"]
        + (household_size - household["child0_18_num"])
        * arbeitsl_geld_2_params["a2verst"],
    )

    # If wealth exceeds the exemption, set benefits to zero
    # (since ALG2 is not yet calculated, just set the need to zero)
    household.loc[
        (household["hh_wealth"] > household["vermfreibetr"]), "regelbedarf"
    ] = 0
    household.loc[(household["hh_wealth"] > household["vermfreibetr"]), "kiz_temp"] = 0

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    household.loc[
        (household["hh_wealth"] > (60_000 + (30_000 * (household_size - 1)))),
        "wohngeld_basis_hh",
    ] = 0

    return household
