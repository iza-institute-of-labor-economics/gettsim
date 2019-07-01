import numpy as np
import pandas as pd
from src.model_code.imports import aggr
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

    # print(
    #     "ALG1 Payments: {} bn €.".format(
    #         ui["m_alg1"].multiply(df["pweight"]).sum() * 12 / 1e9
    #     )
    # )
    # print("ALG1 Recipients: {}.".format(df['pweight'][ui['m_alg1']>0].sum()))
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


def alg2(df, tb):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """
    alg2 = pd.DataFrame(index=df.index.copy())
    alg2["hid"] = df["hid"]
    # alg2["tu_id"] = df["tu_id"]
    alg2["uhv"] = df["uhv"]

    # alg2 = alg2.join(
    #     alg2.groupby(["tu_id"])["tu_id"].count(),
    #     on=["tu_id"],
    #     how="left",
    #     rsuffix="_sum",
    # )
    # # rename
    # alg2 = alg2.rename(columns={"tu_id_sum": "hhsize_tu"})
    # alg2["byear"] = tb["yr"] - df["age"]

    alg2["mehrbed"], alg2["regelsatz"] = regelsatz_alg2(df, tb)

    """
    print(pd.crosstab(alg2['mehrbed'], df['typ_bud']))
    print(pd.crosstab(alg2['regelsatz'],  df['typ_bud']))
    print(pd.crosstab(df['typ_bud'], df['child6_num']))
    """
    # alg2['regelsatz_tu_k'] = aggr(alg2, 'regelsatz', True)

    alg2["alg2_kdu"] = kdu_alg2(df)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    alg2["regelbedarf"] = alg2["regelsatz"] + alg2["alg2_kdu"]

    alg2["alg2_ek"], alg2["alg2_grossek"] = alg2_inc(df)

    alg2["ekanrefrei"] = einkommensanrechnungsfrei(df, tb)

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
            "regelbedarf",
            "regelsatz",
            "alg2_kdu",
            "uhv_hh",
        ]
    ]


def regelsatz_alg2(df, tb):
    """Creating the variables need for the calculation of the alg2 regelsatz. Then
    according to the year the appropriate function is called"""
    regel_df = pd.DataFrame(index=df.index)
    for age in [(0, 6), (0, 15), (14, 24), (7, 13), (3, 6), (0, 2)]:
        regel_df["child{}_{}_num".format(age[0], age[1])] = (
            df["child"] & df["age"].between(age[0], age[1])
        ).sum()
    regel_df["child_num"] = df["child"].sum()
    regel_df["adult_num"] = len(regel_df) - regel_df["child_num"]

    regel_df["mehrbed"] = mehrbedarf_alg2(df, regel_df, tb)
    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person

    regelsatz = np.select(
        [regel_df["adult_num"] == 1, regel_df["adult_num"] > 1],
        tb["calc_regelsatz"](regel_df, tb),
    )
    return regel_df["mehrbed"], regelsatz


def mehrbedarf_alg2(df, rs, tb):
    """ Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get
    36% on top alternatively, you get 12% per kid, depending on what's higher."""
    return df["alleinerz"] * np.minimum(
        tb["a2zu2"] / 100,
        np.maximum(
            tb["a2mbch1"] * rs["child_num"],
            ((rs["child0_6_num"] >= 1) | (rs["child0_15_num"].between(2, 3)))
            * tb["a2mbch2"],
        ),
    )


def kdu_alg2(df):
    # kdu = Kosten der Unterkunft
    """Only 'appropriate' housing costs are paid. Two possible options:
    1. Just pay rents no matter what
    return df["miete"] + df["heizkost"]
    2. Add restrictions regarding flat size and rent per square meter (set it 10€,
    slightly above average)"""
    rent_per_sqm = np.minimum((df["miete"] + df["heizkost"]) / df["wohnfl"], 10)
    if df["eigentum"].iloc[0]:
        wohnfl_justified = np.minimum(
            df["wohnfl"], 80 + np.maximum(0, (len(df) - 2) * 20)
        )
    else:
        wohnfl_justified = np.minimum(df["wohnfl"], (45 + (len(df) - 1) * 15))

    return rent_per_sqm * wohnfl_justified


def alg2_inc(df):
    """Relevant income of alg2."""
    # Income relevant to check against ALG2 claim
    alg2_grossek = grossinc_alg2(df)
    # ...deduct income tax and social security contributions
    alg2_ek = np.maximum(
        alg2_grossek - df["incometax"] - df["soli"] - df["svbeit"], 0
    ).fillna(0)

    return alg2_ek, alg2_grossek


def grossinc_alg2(df):
    """Calculating the gross income relevant for alg2."""
    return (
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
        .sum(axis=1)
        .fillna(0)
    )


def einkommensanrechnungsfrei(df, tb):
    """Determine the amount of income that is not deducted. Varies withdrawal rates
    depending on monthly earnings."""

    ekanrefrei = pd.Series(index=df.index)
    # Calculate the amount of children below the age of 18.
    child0_18_num = (df["child"] & df["age"].between(0, 18)).sum()

    # 100€ is always 'free'
    ekanrefrei[(df["m_wage"] <= tb["a2grf"])] = df["m_wage"]
    # until 1000€, you may keep 20% (withdrawal rate: 80%)
    ekanrefrei[(df["m_wage"].between(tb["a2grf"], tb["a2eg1"]))] = tb["a2grf"] + tb[
        "a2an1"
    ] * (df["m_wage"] - tb["a2grf"])
    # from 1000 to 1200 €, you may keep only 10%
    ekanrefrei[
        (df["m_wage"].between(tb["a2eg1"], tb["a2eg2"])) & (child0_18_num == 0)
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (df["m_wage"] - tb["a2eg1"])
    )
    # If you have kids, this range goes until 1500 €,
    ekanrefrei[
        (df["m_wage"].between(tb["a2eg1"], tb["a2eg3"])) & (child0_18_num > 0)
    ] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (df["m_wage"] - tb["a2eg1"])
    )
    # beyond 1200/1500€, you can't keep anything.
    ekanrefrei[(df["m_wage"] > tb["a2eg2"]) & (child0_18_num == 0)] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
    )
    ekanrefrei[(df["m_wage"] > tb["a2eg3"]) & (child0_18_num > 0)] = (
        tb["a2grf"]
        + tb["a2an1"] * (tb["a2eg1"] - tb["a2grf"])
        + tb["a2an2"] * (tb["a2eg3"] - tb["a2eg1"])
    )
    # Children income is fully deducted, except for the first 100 €.
    ekanrefrei[(df["child"])] = np.maximum(0, df["m_wage"] - 100)

    return ekanrefrei


def wg(df, tb):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual
        rent and differs on the municipality level ('Mietstufe' (1,...,6)).
        As we don't have information on the last item, we assume 'Mietstufe' 3,
        corresponding to an average level
    """
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)

    wg = pd.DataFrame(index=df.index.copy())
    wg["hid"] = df["hid"]
    wg["tu_id"] = df["tu_id"]
    hhsize = df.shape[0]
    # Caluclate income in seperate function
    wg["Y"] = calc_wg_income(df, tb, hhsize)
    # Caluclate rent in seperate function
    wg["M"] = calc_wg_rent(df, tb, hhsize)

    # Apply Wohngeld Formel.
    wg["wohngeld_basis"] = apply_wg_formula(wg, tb, hhsize)

    # Sum of wohngeld within household
    wg["wg_head"] = wg["wohngeld_basis"] * df["head_tu"]
    wg = wg.join(
        wg.groupby(["hid"])["wg_head"].sum(), on=["hid"], how="left", rsuffix="_hh"
    )
    wg = wg.rename(columns={"wg_head_hh": "wohngeld_basis_hh"})
    # df["hhsize_tu"].describe()
    # wg.to_excel(get_settings()['DATA_PATH'] + 'wg_check_hypo.xlsx')
    return wg[["wohngeld_basis", "wohngeld_basis_hh"]]


def calc_wg_rent(df, tb, hhsize):
    """
    This function yields the relevant rent for calculating the wohngeld.
    """
    # There are also min and max values for this.
    # First max rent
    if tb["yr"] >= 2009:
        max_rent = calc_max_rent_since_2009(tb, hhsize)
    else:
        # Before 2009, they differed by construction year of the house
        cnstyr = df["cnstyr"].iloc[0]
        max_rent = calc_max_rent_until_2008(tb, hhsize, cnstyr)
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


def calc_max_rent_since_2009(tb, hhsize):
    """
    Since 2009 a different formula for the maximal acknowledged rent applies. Now the
    date of the construction is irrelevant.
    """
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    if hhsize <= 5:
        max_rent = tb["wgmax" + str(hhsize) + "p_m"]
    else:
        max_rent = tb["wgmax5p_m"] + tb["wgmaxplus5_m"] * (hhsize - 5)
    return max_rent


def calc_max_rent_until_2008(tb, hhsize, cnstyr):
    """ Before 2009, differentiate by construction year of the house and calculate
    the maximal acknowledged rent."""
    cnstyr_dict = {1: "a", 2: "m", 3: "n"}
    key = cnstyr_dict[cnstyr]
    # fixed amounts for the households with size 1 to 5
    # afterwards, fix amount for every additional hh member
    if hhsize <= 5:
        max_rent = tb["wgmax" + str(hhsize) + "p_" + cnstyr_dict[cnstyr]]
    else:
        max_rent = tb["wgmax5p_" + key] + tb["wgmaxplus5_" + key] * (hhsize - 5)
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
    wg_income = pd.DataFrame(index=df.index)
    wg_income["tu_id"] = df["tu_id"]
    # Start with income revelant for the housing beneift
    # tax-relevant share of pensions for tax unit
    wg_income["pens_steuer"] = df["ertragsanteil"] * df["m_pensions"]
    wg_income["pens_steuer_tu_k"] = aggr(wg_income, "pens_steuer", "all_tu")
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
        wg_income["{}_tu_k".format(inc)] = aggr(df, inc, "all_tu")

    wg_income["wg_abzuege"] = calc_wg_abzuege(wg_income, tb)

    # Relevant income is market income + transfers...
    wg_income["wg_grossY"] = calc_wg_gross_income(wg_income)

    wg_income["wg_otherinc"] = wg_income[
        ["m_alg1_tu_k", "m_transfers_tu_k", "pens_steuer_tu_k", "uhv_tu_k"]
    ].sum(axis=1)

    # ... minus a couple of lump-sum deductions for handicaps,
    # children income or being single parent
    wg_income["wg_incdeduct"] = calc_wg_income_deductions(df, tb)
    wg_income["wg_incdeduct_tu_k"] = aggr(wg_income, "wg_incdeduct", "all_tu")
    prelim_y = (1 - wg_income["wg_abzuege"]) * np.maximum(
        0,
        (
            wg_income["wg_grossY"]
            + wg_income["wg_otherinc"]
            - wg_income["wg_incdeduct_tu_k"]
        ),
    )
    # There's a minimum Y depending on the hh size
    return _set_min_y(prelim_y, tb, hhsize)


def calc_wg_abzuege(wg_income, tb):
    # There share of income to be deducted is 0/10/20/30%, depending on whether
    # household is subject to income taxation and/or payroll taxes
    wg_abz = (
        (wg_income["incometax_tu_k"] > 0) * 1
        + (wg_income["rvbeit_tu_k"] > 0) * 1
        + (wg_income["gkvbeit_tu_k"] > 0) * 1
    )

    wg_abz_amounts = {
        0: tb["wgpabz0"],
        1: tb["wgpabz1"],
        2: tb["wgpabz2"],
        3: tb["wgpabz3"],
    }

    return wg_abz.replace(wg_abz_amounts)


def calc_wg_gross_income(wg_income):
    out = (
        np.maximum(wg_income["gross_e1_tu_k"] / 12, 0)
        + np.maximum(wg_income["gross_e4_tu_k"] / 12, 0)
        + np.maximum(wg_income["gross_e5_tu_k"] / 12, 0)
        + np.maximum(wg_income["gross_e6_tu_k"] / 12, 0)
    )
    return out


def calc_wg_income_deductions(df, tb):
    if tb["yr"] < 2016:
        wg_incdeduct = _calc_wg_income_deductions_until_2015(df, tb)
    else:
        wg_incdeduct = _calc_wg_income_deductions_since_2016(df, tb)
    return wg_incdeduct


def _calc_wg_income_deductions_until_2015(df, tb):
    workingchild = df["child"] & (df["m_wage"] > 0)
    wg_incdeduct = (
        (df["handcap_degree"] > 80) * tb["wgpfbm80"]
        + df["handcap_degree"].between(1, 80) * tb["wgpfbu80"]
        + (workingchild * np.minimum(tb["wgpfb24"], df["m_wage"]))
        + ((df["alleinerz"] & (~df["child"])) * df["child11_num_tu"] * tb["wgpfb12"])
    )
    return wg_incdeduct


def _calc_wg_income_deductions_since_2016(df, tb):
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


def apply_wg_formula(wg, tb, hhsize):
    # There are parameters a, b, c, depending on hh size
    a, b, c = calc_wg_formula_factors(tb, hhsize)
    return np.maximum(
        0, tb["wg_factor"] * (wg["M"] - ((a + (b * wg["M"]) + (c * wg["Y"])) * wg["Y"]))
    )


def calc_wg_formula_factors(tb, hhsize):
    a = tb["wg_a_" + str(hhsize) + "p"]
    b = tb["wg_b_" + str(hhsize) + "p"]
    c = tb["wg_c_" + str(hhsize) + "p"]
    return a, b, c


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

    print(bp[["kiz", "wohngeld", "m_alg2"]])
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
