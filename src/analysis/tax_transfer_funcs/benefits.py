import numpy as np
import pandas as pd

from src.analysis.tax_transfer_funcs.taxes import soli_formula


def ui(df_row, tb):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """

    ui = pd.DataFrame(index=df_row.index)

    # ui["m_alg1_soep"] = df["alg_soep"].fillna(0)

    ui["alg_entgelt"] = _alg_entgelt(df_row, tb)

    ui["eligible"] = check_eligibility_alg(df_row)

    ui["m_alg1"] = 0
    ui.loc[ui["eligible"], "m_alg1"] = ui["alg_entgelt"] * np.select(
        [df_row["child_num_tu"] == 0, df_row["child_num_tu"] > 0],
        [tb["agsatz0"], tb["agsatz1"]],
    )

    return ui["m_alg1"]


def _alg_entgelt(df_row, tb):
    """ Calculating the claim for the Arbeitslosengeldgeld, depending on the current
    wage."""
    if df_row["east"].iloc[0]:
        westost = "o"
    else:
        westost = "w"
    # Relevant wage is capped at the contribution thresholds
    alg_wage = np.minimum(tb["rvmaxek" + westost], df_row["m_wage_l1"])

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    alg_ssc = tb["alg1_abz"] * alg_wage
    # assume west germany for this particular calculation
    # df['east'] = False
    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    alg_tax = tb["tax_schedule"](12 * alg_wage - tb["werbung"], tb)

    alg_soli = soli_formula(alg_tax, tb)

    return np.maximum(0, alg_wage - alg_ssc - alg_tax / 12 - alg_soli / 12)


def check_eligibility_alg(df_row):
    """Checking eligibility, depending on the months worked beforehand, the age and
    other variables.."""
    # Months of unemployment beforehand.
    mts_ue = df_row["months_ue"] + df_row["months_ue_l1"] + df_row["months_ue_l2"]
    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # there are different replacement rates depending on presence of children
    return (
        mts_ue.between(1, 12)
        & (df_row["age"] < 65)
        & (df_row["m_pensions"] == 0)
        & (df_row["w_hours"] < 15)
    )


def uhv(df, tb):
    """
    Since 2017, the receipt of this
    UHV has been extended substantially and needs to be taken into account, since it's
    dominant to other transfers, i.e. single parents 'have to' apply for it.
    """
    if tb["yr"] >= 2017:
        return uhv_since_2017(df, tb)
    else:
        return 0


def uhv_since_2017(df, tb):
    """ Advanced Alimony Payment / Unterhaltsvorschuss (UHV)

        In Germany, Single Parents get alimony payments for themselves and for their
        child from the ex partner. If the ex partner is not able to pay the child
        alimony, the government pays the child alimony to the mother (or the father, if
        he has the kids)

        returns:
            uhv (pd.Series): Alimony Payment on individual level
        """
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit
    uhv = pd.DataFrame(index=df.index.copy())

    uhv["uhv"] = 0
    # Amounts depend on age
    uhv.loc[df["age"].between(0, 5) & df["alleinerz"], "uhv"] = tb["uhv5"]
    uhv.loc[df["age"].between(6, 11) & df["alleinerz"], "uhv"] = tb["uhv11"]
    # Older kids get it only if the parent has income > 600€
    uhv["uhv_inc_tu"] = (
        df[
            [
                "m_wage",
                "m_transfers",
                "m_self",
                "m_vermiet",
                "m_kapinc",
                "m_pensions",
                "m_alg1",
            ]
        ]
        .sum()
        .sum()
    )
    uhv.loc[
        (df["age"].between(12, 17)) & (df["alleinerz"]) & (uhv["uhv_inc_tu"] > 600),
        "uhv",
    ] = tb["uhv17"]
    # TODO: Check against actual transfers
    return uhv["uhv"]


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
