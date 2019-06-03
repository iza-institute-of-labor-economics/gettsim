import numpy as np
import pandas as pd
from src.model_code.imports import aggr, tarif_ubi
from termcolor import cprint
from src.analysis.tax_transfer.taxes import soli_formula, tarif


def ui(df, tb, taxyear, ref=""):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """

    ui = pd.DataFrame(index=df.index.copy())
    westost = [~df["east"], df["east"]]

    ui["m_alg1"] = 0
    # ui["m_alg1_soep"] = df["alg_soep"].fillna(0)

    # Months of unemployment beforehand.
    ui["mts_ue"] = df["months_ue"] + df["months_ue_l1"] + df["months_ue_l2"]
    # Relevant wage is capped at the contribution thresholds
    ui["alg_wage"] = np.select(
        westost,
        [
            np.minimum(tb["rvmaxekw"], df["m_wage_l1"]),
            np.minimum(tb["rvmaxeko"], df["m_wage_l1"]),
        ],
    )

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    ui["alg_ssc"] = tb["alg1_abz"] * ui["alg_wage"]
    # assume west germany for this particular calculation
    # df['east'] = False
    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    if ref == "":
        ui["alg_tax"] = np.vectorize(tarif)(12 * ui["alg_wage"] - tb["werbung"], tb)
    if ref == "UBI":
        ui["alg_tax"] = np.vectorize(tarif_ubi)(12 * ui["alg_wage"] - tb["werbung"], tb)

    ui["alg_soli"] = soli_formula(ui["alg_tax"], tb)

    ui["alg_entgelt"] = np.maximum(
        0, ui["alg_wage"] - ui["alg_ssc"] - ui["alg_tax"] / 12 - ui["alg_soli"] / 12
    )

    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # there are different replacement rates depending on presence of children
    ui["eligible"] = (
        (ui["mts_ue"].between(1, 12))
        & (df["age"] < 65)
        & (df["m_pensions"] == 0)
        & (df["w_hours"] < 15)
    )
    ui.loc[ui["eligible"], "m_alg1"] = ui["alg_entgelt"] * np.select(
        [df["child_num_tu"] == 0, df["child_num_tu"] > 0],
        [tb["agsatz0"], tb["agsatz1"]],
    )

    # print(
    #     "ALG1 Payments: {} bn €.".format(
    #         ui["m_alg1"].multiply(df["pweight"]).sum() * 12 / 1e9
    #     )
    # )
    # print("ALG1 Recipients: {}.".format(df['pweight'][ui['m_alg1']>0].sum()))
    return ui["m_alg1"]


def alg2(df, tb, yr):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """
    cprint("ALG 2...", "red", "on_white")

    alg2 = pd.DataFrame(index=df.index.copy())
    alg2["hid"] = df["hid"]
    alg2["tu_id"] = df["tu_id"]
    alg2["uhv"] = df["uhv"]

    # Calculate a couple of helper variables
    ch_ages = [(0, 6), (0, 15), (0, 18), (14, 24), (7, 13), (3, 6), (0, 2)]

    # Create columns which hold the numer of kids in the age range
    for c in ch_ages:
        alg2["child{}_{}_num".format(c[0], c[1])] = (
            df["child"] & df["age"].between(c[0], c[1])
        ).sum()

    alg2["hhsize"] = len(alg2)
    alg2 = alg2.join(
        alg2.groupby(["tu_id"])["tu_id"].count(),
        on=["tu_id"],
        how="left",
        rsuffix="_sum",
    )
    # rename
    alg2 = alg2.rename(columns={"tu_id_sum": "hhsize_tu"})
    alg2["child_num"] = df["child"].sum()
    alg2["adult_num"] = alg2["hhsize"] - alg2["child_num"]
    alg2["byear"] = yr - df["age"]

    # Additional need for single parents
    # Maximum 60% of the standard amount on top (a2zu2)
    # if you have at least one kid below 6 or two or three below 15, you get 36% on top
    # alternatively, you get 12% per kid, depending on what's higher.
    alg2["mehrbed"] = df["alleinerz"] * np.minimum(
        tb["a2zu2"] / 100,
        np.maximum(
            tb["a2mbch1"] * alg2["child_num"],
            ((alg2["child0_6_num"] >= 1) | (alg2["child0_15_num"].between(2, 3)))
            * tb["a2mbch2"],
        ),
    )

    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person
    if yr <= 2010:
        # Before 2010, other members' amounts were calculated by a share of the head's
        # need
        regelberechnung = [
            tb["rs_hhvor"] * (1 + alg2["mehrbed"])
            + (tb["rs_hhvor"] * tb["a2ch14"] * alg2["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * alg2["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (alg2["child0_2_num"] + alg2["child3_6_num"])
            ),
            tb["rs_hhvor"] * tb["a2part"] * (1 + alg2["mehrbed"])
            + (tb["rs_hhvor"] * tb["a2part"])
            + (tb["rs_hhvor"] * tb["a2ch18"] * np.maximum((alg2["adult_num"] - 2), 0))
            + (tb["rs_hhvor"] * tb["a2ch14"] * alg2["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * alg2["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (alg2["child0_2_num"] + alg2["child3_6_num"])
            ),
        ]

    else:
        # After 2010,
        regelberechnung = [
            tb["rs_hhvor"] * (1 + alg2["mehrbed"])
            + (tb["rs_ch14"] * alg2["child14_24_num"])
            + (tb["rs_ch7"] * alg2["child7_13_num"])
            + (tb["rs_ch0"] * (alg2["child0_2_num"] + alg2["child3_6_num"])),
            tb["rs_2adults"] * (1 + alg2["mehrbed"])
            + tb["rs_2adults"]
            + (tb["rs_madults"] * np.maximum((alg2["adult_num"] - 2), 0))
            + (tb["rs_ch14"] * alg2["child14_24_num"])
            + (tb["rs_ch7"] * alg2["child7_13_num"])
            + (tb["rs_ch0"] * (alg2["child0_2_num"] + alg2["child3_6_num"])),
        ]

    alg2["regelsatz"] = np.select(
        [alg2["adult_num"] == 1, alg2["adult_num"] > 1], regelberechnung
    )
    """
    print(pd.crosstab(alg2['mehrbed'], df['typ_bud']))
    print(pd.crosstab(alg2['regelsatz'],  df['typ_bud']))
    print(pd.crosstab(df['typ_bud'], df['child6_num']))
    """
    # alg2['regelsatz_tu_k'] = aggr(alg2, 'regelsatz', True)
    # Only 'appropriate' housing costs are paid. Two possible options:
    # 1. Just pay rents no matter what
    # alg2["alg2_kdu"] = df["miete"] + df["heizkost"]
    # 2. Add restrictions regarding flat size and rent per square meter (set it 10€,
    # slightly above average)
    alg2["rent_per_sqm"] = np.minimum((df["miete"] + df["heizkost"]) / df["wohnfl"], 10)
    alg2.loc[df["eigentum"], "wohnfl_just"] = np.minimum(
        df["wohnfl"], 80 + np.maximum(0, (alg2["hhsize"] - 2) * 20)
    )
    alg2.loc[~df["eigentum"], "wohnfl_just"] = np.minimum(
        df["wohnfl"], (45 + (alg2["hhsize"] - 1) * 15)
    )
    alg2["alg2_kdu"] = alg2["rent_per_sqm"] * alg2["wohnfl_just"]
    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    alg2["regelbedarf"] = alg2["regelsatz"] + alg2["alg2_kdu"]

    # Account for household wealth.
    # usually no wealth in the data, infer from capital income...works OK for low
    # wealth HH
    alg2["assets"] = df["divdy"] / tb["r_assets"]

    # df['vermfreib'] = tb['a2vki']
    # there are exemptions depending on individual age for adults
    alg2["ind_freib"] = 0
    alg2.loc[(alg2["byear"] >= 1948) & (~df["child"]), "ind_freib"] = (
        tb["a2ve1"] * df["age"]
    )
    alg2.loc[(alg2["byear"] < 1948), "ind_freib"] = tb["a2ve2"] * df["age"]
    # sum over individuals
    alg2 = alg2.join(
        alg2.groupby(["hid"])["ind_freib"].sum(), on=["hid"], how="left", rsuffix="_hh"
    )

    # there is an overall maximum exemption
    alg2["maxvermfb"] = 0
    alg2.loc[(alg2["byear"] < 1948) & (~df["child"]), "maxvermfb"] = tb["a2voe1"]
    alg2.loc[(alg2["byear"].between(1948, 1957)), "maxvermfb"] = tb["a2voe1"]
    alg2.loc[(alg2["byear"].between(1958, 1963)), "maxvermfb"] = tb["a2voe3"]
    alg2.loc[(alg2["byear"] >= 1964) & (~df["child"]), "maxvermfb"] = tb["a2voe4"]
    alg2 = alg2.join(
        alg2.groupby(["hid"])["maxvermfb"].sum(), on=["hid"], how="left", rsuffix="_hh"
    )
    # add fixed amounts per child and adult
    alg2["vermfreibetr"] = np.minimum(
        alg2["maxvermfb_hh"],
        alg2["ind_freib_hh"]
        + alg2["child0_18_num"] * tb["a2vkf"]
        + alg2["adult_num"] * tb["a2verst"],
    )

    # If wealth exceeds the exemption, the need is set to zero
    alg2.loc[(alg2["assets"] > alg2["vermfreibetr"]), "regelbedarf"] = 0

    # Income relevant to check against ALG2 claim
    alg2["alg2_grossek"] = df[
        [
            "m_wage",
            "m_transfers",
            "m_self",
            "m_vermiet",
            "m_kapinc",
            "m_pensions",
            "m_alg1",
        ]
    ].sum(axis=1)
    alg2["alg2_grossek"] = alg2["alg2_grossek"].fillna(0)
    # ...deduct income tax and social security contributions
    alg2["alg2_ek"] = np.maximum(
        alg2["alg2_grossek"] - df["incometax"] - df["soli"] - df["svbeit"], 0
    )
    alg2["alg2_ek"] = alg2["alg2_ek"].fillna(0)

    # Determine the amount of income that is not deducted
    # Varios withdrawal rates depending on monthly earnings.
    alg2["ekanrefrei"] = 0
    # 100€ is always 'free'
    alg2.loc[(df["m_wage"] <= tb["a2grf"]), "ekanrefrei"] = df["m_wage"]
    # until 1000€, you may keep 20% (withdrawal rate: 80%)
    alg2.loc[(df["m_wage"].between(tb["a2grf"], tb["a2eg1"])), "ekanrefrei"] = tb[
        "a2grf"
    ] + tb["a2an1"] * (df["m_wage"] - tb["a2grf"])
    # from 1000 to 1200 €, you may keep only 10%
    alg2.loc[
        (df["m_wage"].between(tb["a2eg1"], tb["a2eg2"])) & (alg2["child0_18_num"] == 0),
        "ekanrefrei",
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (df["m_wage"] - tb["a2eg1"])
    )
    # If you have kids, this range goes until 1500 €,
    alg2.loc[
        (df["m_wage"].between(tb["a2eg1"], tb["a2eg3"])) & (alg2["child0_18_num"] > 0),
        "ekanrefrei",
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (df["m_wage"] - tb["a2eg1"])
    )
    # beyond 1200/1500€, you can't keep anything.
    alg2.loc[
        (df["m_wage"] > tb["a2eg2"]) & (alg2["child0_18_num"] == 0), "ekanrefrei"
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
    )
    alg2.loc[
        (df["m_wage"] > tb["a2eg3"]) & (alg2["child0_18_num"] > 0), "ekanrefrei"
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (tb["a2eg3"] - tb["a2eg1"])
    )
    # Children income is fully deducted, except for the first 100 €.
    alg2.loc[(df["child"]), "ekanrefrei"] = np.maximum(0, df["m_wage"] - 100)
    # the final alg2 amount is the difference between the theoretical need and the
    # relevant income. this will be calculated later when several benefits have to be
    # compared.
    alg2["ar_alg2_ek"] = np.maximum(alg2["alg2_ek"] - alg2["ekanrefrei"], 0)
    # Aggregate on HH
    for var in ["ar_alg2_ek", "alg2_grossek", "uhv"]:
        alg2[var + "_hh"] = aggr(alg2, var, "all_hh")
    alg2["ar_base_alg2_ek"] = (
        alg2["ar_alg2_ek_hh"] + df["kindergeld_hh"] + alg2["uhv_hh"]
    )

    return alg2[
        [
            "ar_base_alg2_ek",
            "ar_alg2_ek_hh",
            "alg2_grossek_hh",
            "mehrbed",
            "assets",
            "vermfreibetr",
            "regelbedarf",
            "regelsatz",
            "alg2_kdu",
            "uhv_hh",
        ]
    ]


def wg(df, tb, yr, hyporun):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual
        rent and differs on the municipality level ('Mietstufe' (1,...,6)).
        As we don't have information on the last item, we assume 'Mietstufe' 3,
        corresponding to an average level
    """
    cprint("Wohngeld...", "red", "on_white")

    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit

    wg = pd.DataFrame(index=df.index.copy())
    wg["hid"] = df["hid"]
    wg["tu_id"] = df["tu_id"]
    # Start with income revelant for the housing beneift
    # tax-relevant share of pensions
    wg["pens_steuer"] = df["ertragsanteil"] * df["m_pensions"]
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
        wg["{}_tu_k".format(inc)] = aggr(df, inc, "all_tu")

    wg["pens_steuer_tu_k"] = aggr(wg, "pens_steuer", "all_tu")

    # There share of income to be deducted is 0/10/20/30%, depending on whether
    # household is subject to income taxation and/or payroll taxes
    wg["wg_abz"] = (
        (wg["incometax_tu_k"] > 0) * 1
        + (wg["rvbeit_tu_k"] > 0) * 1
        + (wg["gkvbeit_tu_k"] > 0) * 1
    )

    wg_abz_amounts = {
        0: tb["wgpabz0"],
        1: tb["wgpabz1"],
        2: tb["wgpabz2"],
        3: tb["wgpabz3"],
    }

    wg["wg_abzuege"] = wg["wg_abz"].replace(wg_abz_amounts)

    # Relevant income is market income + transfers...
    wg["wg_grossY"] = (
        np.maximum(wg["gross_e1_tu_k"] / 12, 0)
        + np.maximum(wg["gross_e4_tu_k"] / 12, 0)
        + np.maximum(wg["gross_e5_tu_k"] / 12, 0)
        + np.maximum(wg["gross_e6_tu_k"] / 12, 0)
    )

    wg["wg_otherinc"] = wg[
        ["m_alg1_tu_k", "m_transfers_tu_k", "pens_steuer_tu_k", "uhv_tu_k"]
    ].sum(axis=1)

    # ... minus a couple of lump-sum deductions for handicaps,
    # children income or being single parent
    wg["workingchild"] = df["child"] & (df["m_wage"] > 0)
    if yr < 2016:
        wg["wg_incdeduct"] = (
            (df["handcap_degree"] > 80) * tb["wgpfbm80"]
            + df["handcap_degree"].between(1, 80) * tb["wgpfbu80"]
            + (wg["workingchild"] * np.minimum(tb["wgpfb24"], df["m_wage"]))
            + (df["alleinerz"] * (~df["child"]) * df["child11_num_tu"] * tb["wgpfb12"])
        )
    else:
        wg["wg_incdeduct"] = (
            (df["handcap_degree"] > 0) * tb["wgpfbm80"]
            + (wg["workingchild"] * np.minimum(tb["wgpfb24"], df["m_wage"]))
            + (df["alleinerz"] * tb["wgpfb12"] * (~df["child"]))
        )

    wg["wg_incdeduct_tu_k"] = aggr(wg, "wg_incdeduct", "all_tu")

    wg["wgY"] = (1 - wg["wg_abzuege"]) * np.maximum(
        0, (wg["wg_grossY"] + wg["wg_otherinc"] - wg["wg_incdeduct_tu_k"])
    )

    # Parameter Y in steps of 5 Euros
    if not hyporun:
        wg["Y"] = np.maximum(0, pd.Series(wg["wgY"] + 4).round(-1) - 5)
    if hyporun:
        wg["Y"] = wg["wgY"]

    # There's a minimum Y depending on the hh size
    for i in range(1, 12):
        wg.loc[df["hhsize"] == i, "Y"] = np.maximum(
            wg["Y"], tb["wgminEK" + str(i) + "p"]
        )
    wg.loc[df["hhsize"] >= 12, "Y"] = np.maximum(wg["Y"], tb["wgminEK12p"])

    # Obtain relevant rent 'M'
    # There are also min and max values for this. Before 2009, they differed by
    # construction year of the house
    wg["max_rent"] = 0
    wg["min_rent"] = 0
    cnstyr = {"a": 1, "m": 2, "n": 3}
    for i in range(1, 13):
        # first, maximum rent.
        # fixed amounts for the households with size 1 to 5
        # afterwards, fix amount for every additional hh member
        if yr >= 2009:
            if i <= 5:
                wg.loc[(df["hhsize"] == i), "max_rent"] = tb["wgmax" + str(i) + "p_m"]

            wg.loc[(df["hhsize"] > 5), "max_rent"] = tb["wgmax5p_m"] + tb[
                "wgmaxplus5_m"
            ] * (df["hhsize"] - 5)
        if yr < 2009:
            for c in cnstyr:
                if i <= 5:
                    wg.loc[
                        (df["hhsize"] == i) & (df["cnstyr"] == cnstyr[c]), "max_rent"
                    ] = tb["wgmax" + str(i) + "p_" + c]

                wg.loc[
                    (df["hhsize"] > 5) & (df["cnstyr"] == cnstyr[c]), "max_rent"
                ] = tb["wgmax5p_" + c] + tb["wgmaxplus5_" + c] * (df["hhsize"] - 5)

        # min rent never depended on construction year
        wg.loc[(df["hhsize"] == i), "min_rent"] = tb["wgmin" + str(i) + "p"]

    wg.loc[(df["hhsize"] >= 12), "min_rent"] = tb["wgmin12p"]
    # check for failed assignments
    assert ~wg["max_rent"].isna().all()
    assert ~wg["min_rent"].isna().all()

    # distribute max rent among the tax units
    wg["max_rent"] = wg["max_rent"] * df["hh_korr"]

    wg["wgmiete"] = np.minimum(wg["max_rent"], df["miete"] * df["hh_korr"])
    # wg["wgheiz"] = df["heizkost"] * df["hh_korr"]
    wg["M"] = np.maximum(wg["wgmiete"], wg["min_rent"])
    if not hyporun:
        wg["M"] = np.maximum(pd.Series(wg["M"] + 4).round(-1) - 5, 0)

    # Finally, apply Wohngeld Formel. There are parameters a, b, c, depending on hh size
    # To ease notation, I write them first into separate variables from the
    # tb dictionary
    wgeld = {}
    # Call it wohngeld_basis for now, might be set back to zero later on.
    wg["wohngeld_basis"] = 0
    for x in range(1, 13):
        for z in ["a", "b", "c"]:
            wgeld[z] = tb["wg_" + z + "_" + str(x) + "p"]

        a = wgeld["a"]
        b = wgeld["b"]
        c = wgeld["c"]

        wg.loc[np.minimum(df["hhsize_tu"], 12) == x, "wohngeld_basis"] = np.maximum(
            0,
            tb["wg_factor"]
            * (wg["M"] - ((a + (b * wg["M"]) + (c * wg["Y"])) * wg["Y"])),
        )

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    wg["assets"] = df["divdy"] / tb["r_assets"]
    wg.loc[(wg["assets"] > (60000 + (30000 * (df["hhsize"] - 1)))), "wohngeld"] = 0

    # Sum of wohngeld within household
    wg["wg_head"] = wg["wohngeld_basis"] * df["head_tu"]
    wg = wg.join(
        wg.groupby(["hid"])["wg_head"].sum(), on=["hid"], how="left", rsuffix="_hh"
    )
    wg = wg.rename(columns={"wg_head_hh": "wohngeld_basis_hh"})
    df["hhsize_tu"].describe()
    # wg.to_excel(get_settings()['DATA_PATH'] + 'wg_check_hypo.xlsx')
    return wg[["wohngeld_basis", "wohngeld_basis_hh", "gkvbeit_tu_k", "rvbeit_tu_k"]]
