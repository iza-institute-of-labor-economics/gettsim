import numpy as np


def alg2(household, arbeitsl_geld_2_data):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """

    household = regelsatz_alg2(household, arbeitsl_geld_2_data)

    household["alg2_kdu"] = kdu_alg2(household)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    household["regelbedarf"] = household["regelsatz"] + household["alg2_kdu"]

    household["alg2_ek"], household["alg2_grossek"] = alg2_inc(household)

    household = einkommensanrechnungsfrei(household, arbeitsl_geld_2_data)

    # the final alg2 amount is the difference between the theoretical need and the
    # relevant income. this will be calculated later when several benefits have to be
    # compared.
    household["ar_alg2_ek"] = np.maximum(
        household["alg2_ek"] - household["ekanrefrei"], 0
    )
    # Aggregate on HH
    for var in ["ar_alg2_ek", "alg2_grossek", "uhv"]:
        household[f"{var}_hh"] = household[var].sum()
    household["ar_base_alg2_ek"] = (
        household["ar_alg2_ek_hh"] + household["kindergeld_hh"] + household["uhv_hh"]
    )

    return household


def regelsatz_alg2(household, arbeitsl_geld_2_data):
    """Creating the variables need for the calculation of the alg2 regelsatz. Then
    according to the year the appropriate function is called"""
    children_age_info = {}
    for age in [(0, 6), (0, 15), (14, 24), (7, 13), (3, 6), (0, 2)]:
        children_age_info["child{}_{}_num".format(age[0], age[1])] = (
            household["child"] & household["age"].between(age[0], age[1])
        ).sum()
    children_age_info["child_num"] = household["child"].sum()
    children_age_info["adult_num"] = len(household) - children_age_info["child_num"]

    household["mehrbed"] = mehrbedarf_alg2(
        household, children_age_info, arbeitsl_geld_2_data
    )
    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # arbeitsl_geld_2_data['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person

    if arbeitsl_geld_2_data["yr"] <= 2010:
        calc_regelsatz = regelberechnung_until_2010
    else:
        calc_regelsatz = regelberechnung_2011_and_beyond

    household["regelsatz"] = calc_regelsatz(
        household, children_age_info, arbeitsl_geld_2_data
    )
    return household


def regelberechnung_until_2010(household, children_age_info, arbeitsl_geld_2_data):
    if children_age_info["adult_num"] == 1:
        return (
            arbeitsl_geld_2_data["rs_hhvor"] * (1 + household["mehrbed"])
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch14"]
                * children_age_info["child14_24_num"]
            )
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch7"]
                * children_age_info["child7_13_num"]
            )
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["adult_num"] > 1:
        return (
            (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2part"]
                * (1 + household["mehrbed"])
                + (arbeitsl_geld_2_data["rs_hhvor"] * arbeitsl_geld_2_data["a2part"])
                + (
                    arbeitsl_geld_2_data["rs_hhvor"]
                    * arbeitsl_geld_2_data["a2ch18"]
                    * np.maximum((children_age_info["adult_num"] - 2), 0)
                )
            )
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch14"]
                * children_age_info["child14_24_num"]
            )
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch7"]
                * children_age_info["child7_13_num"]
            )
            + (
                arbeitsl_geld_2_data["rs_hhvor"]
                * arbeitsl_geld_2_data["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def regelberechnung_2011_and_beyond(household, children_age_info, arbeitsl_geld_2_data):
    if children_age_info["adult_num"] == 1:
        return (
            arbeitsl_geld_2_data["rs_hhvor"] * (1 + household["mehrbed"])
            + (arbeitsl_geld_2_data["rs_ch14"] * children_age_info["child14_24_num"])
            + (arbeitsl_geld_2_data["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                arbeitsl_geld_2_data["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["adult_num"] > 1:
        return (
            arbeitsl_geld_2_data["rs_2adults"] * (1 + household["mehrbed"])
            + arbeitsl_geld_2_data["rs_2adults"]
            + (
                arbeitsl_geld_2_data["rs_madults"]
                * np.maximum((children_age_info["adult_num"] - 2), 0)
            )
            + (arbeitsl_geld_2_data["rs_ch14"] * children_age_info["child14_24_num"])
            + (arbeitsl_geld_2_data["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                arbeitsl_geld_2_data["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def mehrbedarf_alg2(household, children_age_info, arbeitsl_geld_2_data):
    """ Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get
    36% on top alternatively, you get 12% per kid, depending on what's higher."""
    return household["alleinerz"] * np.minimum(
        arbeitsl_geld_2_data["a2zu2"] / 100,
        np.maximum(
            arbeitsl_geld_2_data["a2mbch1"] * children_age_info["child_num"],
            (
                (children_age_info["child0_6_num"] >= 1)
                | (2 <= children_age_info["child0_15_num"] <= 3)
            )
            * arbeitsl_geld_2_data["a2mbch2"],
        ),
    )


def kdu_alg2(household):
    # kdu = Kosten der Unterkunft
    """Only 'appropriate' housing costs are paid. Two possible options:
    1. Just pay rents no matter what
    return household["miete"] + household["heizkost"]
    2. Add restrictions regarding flat size and rent per square meter (set it 10€,
    slightly above average)"""
    rent_per_sqm = np.minimum(
        (household["miete"] + household["heizkost"]) / household["wohnfl"], 10
    )
    if household["eigentum"].iloc[0]:
        wohnfl_justified = np.minimum(
            household["wohnfl"], 80 + np.maximum(0, (len(household) - 2) * 20)
        )
    else:
        wohnfl_justified = np.minimum(
            household["wohnfl"], (45 + (len(household) - 1) * 15)
        )

    return rent_per_sqm * wohnfl_justified


def alg2_inc(household):
    """Relevant income of alg2."""
    # Income relevant to check against ALG2 claim
    alg2_grossek = grossinc_alg2(household)
    # ...deduct income tax and social security contributions
    alg2_ek = np.maximum(
        alg2_grossek - household["incometax"] - household["soli"] - household["svbeit"],
        0,
    ).fillna(0)

    return alg2_ek, alg2_grossek


def grossinc_alg2(household):
    """Calculating the gross income relevant for alg2."""
    return (
        household[
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


def einkommensanrechnungsfrei(household, arbeitsl_geld_2_data):
    """Determine the amount of income that is not deducted. Varies withdrawal rates
    depending on monthly earnings."""
    # Calculate the amount of children below the age of 18.
    child0_18_num = (household["child"] & household["age"].between(0, 18)).sum()

    # 100€ is always 'free'
    household.loc[
        (household["m_wage"] <= arbeitsl_geld_2_data["a2grf"]), "ekanrefrei"
    ] = household["m_wage"]
    # until 1000€, you may keep 20% (withdrawal rate: 80%)
    household.loc[
        (
            household["m_wage"].between(
                arbeitsl_geld_2_data["a2grf"], arbeitsl_geld_2_data["a2eg1"]
            )
        ),
        "ekanrefrei",
    ] = arbeitsl_geld_2_data["a2grf"] + arbeitsl_geld_2_data["a2an1"] * (
        household["m_wage"] - arbeitsl_geld_2_data["a2grf"]
    )
    # from 1000 to 1200 €, you may keep only 10%
    household.loc[
        (
            household["m_wage"].between(
                arbeitsl_geld_2_data["a2eg1"], arbeitsl_geld_2_data["a2eg2"]
            )
        )
        & (child0_18_num == 0),
        "ekanrefrei",
    ] = (
        arbeitsl_geld_2_data["a2grf"]
        + arbeitsl_geld_2_data["a2an1"]
        * (arbeitsl_geld_2_data["a2eg1"] - arbeitsl_geld_2_data["a2grf"])
        + arbeitsl_geld_2_data["a2an2"]
        * (household["m_wage"] - arbeitsl_geld_2_data["a2eg1"])
    )
    # If you have kids, this range goes until 1500 €,
    household.loc[
        (
            household["m_wage"].between(
                arbeitsl_geld_2_data["a2eg1"], arbeitsl_geld_2_data["a2eg3"]
            )
        )
        & (child0_18_num > 0),
        "ekanrefrei",
    ] = (
        arbeitsl_geld_2_data["a2grf"]
        + arbeitsl_geld_2_data["a2an1"]
        * (arbeitsl_geld_2_data["a2eg1"] - arbeitsl_geld_2_data["a2grf"])
        + arbeitsl_geld_2_data["a2an2"]
        * (household["m_wage"] - arbeitsl_geld_2_data["a2eg1"])
    )
    # beyond 1200/1500€, you can't keep anything.
    household.loc[
        (household["m_wage"] > arbeitsl_geld_2_data["a2eg2"]) & (child0_18_num == 0),
        "ekanrefrei",
    ] = (
        arbeitsl_geld_2_data["a2grf"]
        + arbeitsl_geld_2_data["a2an1"]
        * (arbeitsl_geld_2_data["a2eg1"] - arbeitsl_geld_2_data["a2grf"])
        + arbeitsl_geld_2_data["a2an2"]
        * (arbeitsl_geld_2_data["a2eg2"] - arbeitsl_geld_2_data["a2eg1"])
    )
    household.loc[
        (household["m_wage"] > arbeitsl_geld_2_data["a2eg3"]) & (child0_18_num > 0),
        "ekanrefrei",
    ] = (
        arbeitsl_geld_2_data["a2grf"]
        + arbeitsl_geld_2_data["a2an1"]
        * (arbeitsl_geld_2_data["a2eg1"] - arbeitsl_geld_2_data["a2grf"])
        + arbeitsl_geld_2_data["a2an2"]
        * (arbeitsl_geld_2_data["a2eg3"] - arbeitsl_geld_2_data["a2eg1"])
    )
    # Children income is fully deducted, except for the first 100 €.
    household.loc[(household["child"]), "ekanrefrei"] = np.maximum(
        0, household["m_wage"] - 100
    )

    return household
