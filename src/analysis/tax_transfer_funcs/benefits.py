import numpy as np
import pandas as pd

from src.analysis.tax_transfer_funcs.taxes import soli_formula
from src.model_code.imports import aggr


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


def regelberechnung_until_2010(regel_df, tb):
    return [
        tb["rs_hhvor"] * (1 + regel_df["mehrbed"])
        + (tb["rs_hhvor"] * tb["a2ch14"] * regel_df["child14_24_num"])
        + (tb["rs_hhvor"] * tb["a2ch7"] * regel_df["child7_13_num"])
        + (
            tb["rs_hhvor"]
            * tb["a2ch0"]
            * (regel_df["child0_2_num"] + regel_df["child3_6_num"])
        ),
        tb["rs_hhvor"] * tb["a2part"] * (1 + regel_df["mehrbed"])
        + (tb["rs_hhvor"] * tb["a2part"])
        + (tb["rs_hhvor"] * tb["a2ch18"] * np.maximum((regel_df["adult_num"] - 2), 0))
        + (tb["rs_hhvor"] * tb["a2ch14"] * regel_df["child14_24_num"])
        + (tb["rs_hhvor"] * tb["a2ch7"] * regel_df["child7_13_num"])
        + (
            tb["rs_hhvor"]
            * tb["a2ch0"]
            * (regel_df["child0_2_num"] + regel_df["child3_6_num"])
        ),
    ]


def regelberechnung_2011_and_beyond(regel_df, tb):
    return [
        tb["rs_hhvor"] * (1 + regel_df["mehrbed"])
        + (tb["rs_ch14"] * regel_df["child14_24_num"])
        + (tb["rs_ch7"] * regel_df["child7_13_num"])
        + (tb["rs_ch0"] * (regel_df["child0_2_num"] + regel_df["child3_6_num"])),
        tb["rs_2adults"] * (1 + regel_df["mehrbed"])
        + tb["rs_2adults"]
        + (tb["rs_madults"] * np.maximum((regel_df["adult_num"] - 2), 0))
        + (tb["rs_ch14"] * regel_df["child14_24_num"])
        + (tb["rs_ch7"] * regel_df["child7_13_num"])
        + (tb["rs_ch0"] * (regel_df["child0_2_num"] + regel_df["child3_6_num"])),
    ]


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


def kiz(df, tb):
    """ Kinderzuschlag / Additional Child Benefit
        The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they
        would be eligible to ALG2 due to the fact that their claim rises because of
        their children, they can claim Kiz.

        Also determines which benefit (if any) the household actually receives.
    """

    """ In contrast to ALG2, Kiz considers only the rental costs that are attributed
        to the parents.
        This is done by some fixed share which is updated on annual basis
        ('jährlicher Existenzminimumsbericht')
    """
    kiz = pd.DataFrame(index=df.index.copy())
    kiz["hid"] = df["hid"]
    kiz["tu_id"] = df["tu_id"]
    kiz["uhv_tu"] = aggr(df, "uhv", "all_tu")
    # First, calculate the need as for ALG2, but only for parents.
    kiz["kiz_ek_regel"] = calc_kiz_ek(df, tb)
    # Add rents. First, correct rent for the case of several tax units within the HH
    kiz["kiz_miete"] = df["miete"] * df["hh_korr"]
    kiz["kiz_heiz"] = df["heizkost"] * df["hh_korr"]
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf'.
    wb = get_wohnbedarf(max(tb["yr"], 2011))
    kiz["wb_eltern_share"] = 1.0
    for c in [1, 2]:
        for r in [1, 2, 3, 4]:
            kiz.loc[
                (df["child_num_tu"] == r) & (df["adult_num_tu"] == c), "wb_eltern_share"
            ] = (wb[r - 1][c - 1] / 100)
        kiz.loc[
            (df["child_num_tu"] >= 5) & (df["adult_num_tu"] == c), "wb_eltern_share"
        ] = (wb[4][c - 1] / 100)

    # apply this share to living costs
    # unlike ALG2, there is no check whether living costs are "appropriate".
    kiz["kiz_ek_kdu"] = kiz["wb_eltern_share"] * (kiz["kiz_miete"] + kiz["kiz_heiz"])
    kiz["kiz_ek_relev"] = kiz["kiz_ek_regel"] + kiz["kiz_ek_kdu"]

    # There is a maximum income threshold, depending on the need, plus the potential
    # kiz receipt
    # First, we need to count the number of children eligible to child benefit.
    kiz["child_num_kg"] = tb["childben_elig_rule"](df, tb).sum()

    kiz["kiz_ek_max"] = kiz["kiz_ek_relev"] + tb["a2kiz"] * kiz["child_num_kg"]
    # min income to be eligible for KIZ (different for singles and couples)
    kiz["kiz_ek_min"] = tb["a2kiz_minek_cou"] * (df["hhtyp"] == 4) + (
        tb["a2kiz_minek_sin"] * (df["alleinerz"])
    )

    #        Übersetzung §6a BKGG auf deutsch:
    #     1. Um KIZ zu bekommen, muss das Bruttoeinkommen minus Wohngeld
    #        und Kindergeld über 600 € (Alleinerziehende) bzw. 900 € (Paare) liegen.
    #     2. Das Nettoeinkommen minus Wohngeld muss unterhalb des Bedarfs
    #        plus Gesamtkinderzuschlag liegen.
    #     3. Dann wird geschaut, wie viel von dem Einkommen
    #        (Erwachsene UND Kinder !) noch auf KIZ angerechnet wird.
    #        Wenn das zu berücksichtigende Einkommen UNTER der
    #        Höchsteinkommensgrenze und UNTER der Bemessungsgrundlage liegt, wird
    #        der volle KIZ gezahlt
    #        Wenn es ÜBER der Bemessungsgrundlage liegt,
    #        wird die Differenz zur Hälfte abgezogen.
    kiz["kiz_ek_gross"] = df["alg2_grossek_hh"]
    kiz["kiz_ek_net"] = df["ar_alg2_ek_hh"]

    # Deductable income. 50% withdrawal rate.
    kiz["kiz_ek_anr"] = np.maximum(0, 0.5 * (df["ar_alg2_ek_hh"] - kiz["kiz_ek_relev"]))

    # Dummy variable whether household is in the relevant income range.
    kiz["kiz_incrange"] = (kiz["kiz_ek_gross"] >= kiz["kiz_ek_min"]) & (
        kiz["kiz_ek_net"] <= kiz["kiz_ek_max"]
    )
    # Finally, calculate the amount. Subtract deductable income with 50% and child
    # income fully!
    kiz["kiz"] = 0
    kiz.loc[kiz["kiz_incrange"], "kiz"] = np.maximum(
        0, tb["a2kiz"] * kiz["child_num_kg"] - kiz["kiz_ek_anr"] - kiz["uhv_tu"]
    )
    kiz["kiz_temp"] = kiz["kiz"].max()
    # Transfer some variables for eligibility check
    # kiz["ar_base_alg2_ek"] = df["ar_base_alg2_ek"]
    # kiz["n_pens"] = df["pensioner"].sum()
    return kiz[["kiz_temp", "kiz_incrange"]]


def calc_kiz_ek(df, tb):
    if tb["yr"] <= 2010:
        # not yet implemented
        kiz_regel = _calc_kiz_regel_until_2010(df, tb)
    else:
        kiz_regel = _calc_kiz_regel_since_2011(df, tb)

    return np.select(
        [df["adult_num_tu"] == 1, df["adult_num_tu"] == 2, df["adult_num_tu"] > 2],
        kiz_regel,
    )


def _calc_kiz_regel_until_2010(df, tb):
    """"""
    return [
        tb["rs_hhvor"] * (1 + df["mehrbed"]),
        tb["rs_hhvor"] * tb["a2part"] * (2 + df["mehrbed"]),
        tb["rs_hhvor"] * tb["a2ch18"] * df["adult_num_tu"],
    ]


def _calc_kiz_regel_since_2011(df, tb):
    return [
        tb["rs_hhvor"] * (1 + df["mehrbed"]),
        tb["rs_2adults"] + ((1 + df["mehrbed"]) * tb["rs_2adults"]),
        tb["rs_madults"] * df["adult_num_tu"],
    ]


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


def get_wohnbedarf(yr):
    """ Specifies the percent share of living costs that is attributed to the parents
        This is a share that is defined by the "Existenzminimumsbericht". The
        function is called by uhv().
    """
    # cols: number of adults
    # rows: number of kids
    wohnbedarf = {
        "2011": [
            [75.90, 83.11],
            [61.16, 71.10],
            [51.21, 62.12],
            [44.05, 55.15],
            [38.65, 49.59],
        ],
        "2012": [
            [76.34, 83.14],
            [61.74, 71.15],
            [51.82, 62.18],
            [44.65, 55.22],
            [39.23, 49.66],
        ],
        "2013": [
            [76.34, 83.14],
            [61.74, 71.15],
            [51.82, 62.18],
            [44.65, 55.22],
            [39.23, 49.66],
        ],
        "2014": [
            [76.69, 83.30],
            [62.20, 71.38],
            [52.31, 62.45],
            [45.13, 55.50],
            [39.69, 49.95],
        ],
        "2015": [
            [76.69, 83.30],
            [62.20, 71.38],
            [52.31, 62.45],
            [45.13, 55.50],
            [39.69, 49.95],
        ],
        "2016": [
            [77.25, 83.16],
            [62.93, 71.17],
            [53.09, 62.20],
            [45.92, 55.24],
            [40.45, 49.69],
        ],
        "2017": [
            [77.25, 83.16],
            [62.93, 71.17],
            [53.09, 62.20],
            [45.92, 55.24],
            [40.45, 49.69],
        ],
        "2018": [
            [77.24, 83.25],
            [62.92, 71.30],
            [53.08, 62.36],
            [45.90, 55.41],
            [40.43, 49.85],
        ],
        "2019": [
            [77.10, 83.60],
            [62.73, 71.93],
            [52.88, 62.96],
            [45.70, 56.04],
            [40.24, 50.49],
        ],
    }

    return wohnbedarf[str(yr)]
