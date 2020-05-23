import numpy as np


def benefit_priority(household, params):
    """There are three main transfers for working-age people:
        1. Basic social security / ALG2
        2. Housing Benefit / Wohngeld
        3. Additional Child Benefit / Kinderzuschlag

    There is a rule which benefits are superior to others
    If there is a positive ALG2 entitlement, but the need can be covered with
    Housing Benefit (and possibly add. child benefit),
    the HH *has* to claim the housing benefit and addit. child benefit.
    If the household need cannot be covered via Wohngeld, he has to apply for ALG2.
    There is no way you can receive ALG2 and Wohngeld/Kinderzuschlag at the same time!
    """
    # Before 2005 no basic social security (=ALG2) is implemented so far and thus
    # return a nan dataframe.
    if params["jahr"] < 2005:
        return household
    # But first, we check whether hh wealth is too high
    household = wealth_test(household, params)
    # use these values (possibly zero now) below
    household["sum_wohngeld_m_arbeitsl_geld_2_eink"] = (
        household["sum_basis_arbeitsl_geld_2_eink"] + household["wohngeld_basis_hh"]
    )
    household["sum_kinderzuschlag_arbeitsl_geld_2_eink"] = (
        household["sum_basis_arbeitsl_geld_2_eink"] + household["kinderzuschlag_temp"]
    )
    household["sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink"] = (
        household["sum_basis_arbeitsl_geld_2_eink"]
        + household["wohngeld_basis_hh"]
        + household["kinderzuschlag_temp"]
    )

    # calculate difference between transfers and the household need
    for v in ["basis", "wohngeld_m", "kinderzuschlag", "wohngeld_m_kinderzuschlag"]:
        household["fehlbedarf_" + v] = (
            household["regelbedarf_m"] - household["sum_" + v + "_arbeitsl_geld_2_eink"]
        )
        household["arbeitsl_geld_2_m_" + v] = np.maximum(
            household["fehlbedarf_" + v], 0
        )

    # check whether any of wg kiz or wg+kiz joint imply a fulfilled need.
    for v in ["wohngeld_m", "kinderzuschlag", "wohngeld_m_kinderzuschlag"]:
        household[v + "_vorrang"] = (household["arbeitsl_geld_2_m_" + v] == 0) & (
            household["arbeitsl_geld_2_m_basis"] > 0
        )

    # initialize final benefits
    household["arbeitsl_geld_2_m"] = household["arbeitsl_geld_2_m_basis"]
    household["kinderzuschlag_m"] = household["kinderzuschlag_temp"]
    household["wohngeld_m"] = household["wohngeld_basis_hh"]

    # If this is the case set alg2 to zero.
    household.loc[
        (household["wohngeld_m_vorrang"])
        | (household["kinderzuschlag_vorrang"])
        | (household["wohngeld_m_kinderzuschlag_vorrang"]),
        "arbeitsl_geld_2_m",
    ] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    household.loc[
        (~household["wohngeld_m_vorrang"])
        & (~household["wohngeld_m_kinderzuschlag_vorrang"])
        & (household["arbeitsl_geld_2_m_basis"] > 0),
        "wohngeld_m",
    ] = 0
    household.loc[
        (~household["kinderzuschlag_vorrang"])
        & (~household["wohngeld_m_kinderzuschlag_vorrang"])
        & (household["arbeitsl_geld_2_m_basis"] > 0),
        "kinderzuschlag_m",
    ] = 0

    # Pensioners do not receive Kiz or Wohngeld.
    # They actually do not receive ALGII, too. Instead,
    # they get 'Grundleistung im Alter', which pays the same amount.
    household["anz_rentner"] = household["rentner"].sum()

    for ben in ["kinderzuschlag_m", "wohngeld_m", "arbeitsl_geld_2_m"]:
        household.loc[household["anz_rentner"] > 0, ben] = 0

    return household


def wealth_test(household, params):
    """ Checks Benefit Claim against Household wealth.
        - household: a dataframe containing information on theoretical claim of
              - ALG2
              - Kiz
              - Wohngeld
          as well as age of each hh member

    For ALG2 and Kiz, there are wealth exemptions for every year.
    For Wohngeld, there is a lump-sum amount depending on the household size
    """
    household_size = household.shape[0]

    # If wealth exceeds the exemption, set benefits to zero
    # (since ALG2 is not yet calculated, just set the need to zero)
    household.loc[
        (household["vermögen_hh"] > household["freibetrag_vermögen"]), "regelbedarf_m"
    ] = 0
    household.loc[
        (household["vermögen_hh"] > household["freibetrag_vermögen"]),
        "kinderzuschlag_temp",
    ] = 0

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    household.loc[
        (household["vermögen_hh"] > (60_000 + (30_000 * (household_size - 1)))),
        "wohngeld_basis_hh",
    ] = 0

    return household
