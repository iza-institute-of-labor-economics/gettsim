import numpy as np
import pandas as pd

from gettsim.auxiliary import aggr


def alg2(df, tb):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """

    df = regelsatz_alg2(df, tb)

    df["alg2_kdu"] = kdu_alg2(df)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    df["regelbedarf"] = df["regelsatz"] + df["alg2_kdu"]

    df["alg2_ek"], df["alg2_grossek"] = alg2_inc(df)

    df["ekanrefrei"] = einkommensanrechnungsfrei(df, tb)

    # the final alg2 amount is the difference between the theoretical need and the
    # relevant income. this will be calculated later when several benefits have to be
    # compared.
    df["ar_alg2_ek"] = np.maximum(df["alg2_ek"] - df["ekanrefrei"], 0)
    # Aggregate on HH
    for var in ["ar_alg2_ek", "alg2_grossek", "uhv"]:
        df[var + "_hh"] = aggr(df, var, "all_hh")
    df["ar_base_alg2_ek"] = df["ar_alg2_ek_hh"] + df["kindergeld_hh"] + df["uhv_hh"]

    return df


def regelsatz_alg2(df, tb):
    """Creating the variables need for the calculation of the alg2 regelsatz. Then
    according to the year the appropriate function is called"""
    child_dict = {}
    for age in [(0, 6), (0, 15), (14, 24), (7, 13), (3, 6), (0, 2)]:
        child_dict["child{}_{}_num".format(age[0], age[1])] = (
            df["child"] & df["age"].between(age[0], age[1])
        ).sum()
    child_dict["child_num"] = df["child"].sum()
    child_dict["adult_num"] = len(df) - child_dict["child_num"]

    df["mehrbed"] = mehrbedarf_alg2(df, child_dict, tb)
    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person

    if tb["yr"] <= 2010:
        calc_regelsatz = regelberechnung_until_2010
    else:
        calc_regelsatz = regelberechnung_2011_and_beyond

    df["regelsatz"] = calc_regelsatz(df, child_dict, tb)
    return df


def regelberechnung_until_2010(df, child_dict, tb):
    if child_dict["adult_num"] == 1:
        return (
            tb["rs_hhvor"] * (1 + df["mehrbed"])
            + (tb["rs_hhvor"] * tb["a2ch14"] * child_dict["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * child_dict["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (child_dict["child0_2_num"] + child_dict["child3_6_num"])
            )
        )
    elif child_dict["adult_num"] > 1:
        return (
            (
                tb["rs_hhvor"] * tb["a2part"] * (1 + df["mehrbed"])
                + (tb["rs_hhvor"] * tb["a2part"])
                + (
                    tb["rs_hhvor"]
                    * tb["a2ch18"]
                    * np.maximum((child_dict["adult_num"] - 2), 0)
                )
            )
            + (tb["rs_hhvor"] * tb["a2ch14"] * child_dict["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * child_dict["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (child_dict["child0_2_num"] + child_dict["child3_6_num"])
            )
        )


def regelberechnung_2011_and_beyond(df, child_dict, tb):
    if child_dict["adult_num"] == 1:
        return (
            tb["rs_hhvor"] * (1 + df["mehrbed"])
            + (tb["rs_ch14"] * child_dict["child14_24_num"])
            + (tb["rs_ch7"] * child_dict["child7_13_num"])
            + (tb["rs_ch0"] * (child_dict["child0_2_num"] + child_dict["child3_6_num"]))
        )
    elif child_dict["adult_num"] > 1:
        return (
            tb["rs_2adults"] * (1 + df["mehrbed"])
            + tb["rs_2adults"]
            + (tb["rs_madults"] * np.maximum((child_dict["adult_num"] - 2), 0))
            + (tb["rs_ch14"] * child_dict["child14_24_num"])
            + (tb["rs_ch7"] * child_dict["child7_13_num"])
            + (tb["rs_ch0"] * (child_dict["child0_2_num"] + child_dict["child3_6_num"]))
        )


def mehrbedarf_alg2(df, rs, tb):
    """ Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get
    36% on top alternatively, you get 12% per kid, depending on what's higher."""
    return df["alleinerz"] * np.minimum(
        tb["a2zu2"] / 100,
        np.maximum(
            tb["a2mbch1"] * rs["child_num"],
            ((rs["child0_6_num"] >= 1) | (2 <= rs["child0_15_num"] <= 3))
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
