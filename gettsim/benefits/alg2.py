import numpy as np


def alg2(household, tb):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """

    household = regelsatz_alg2(household, tb)

    household["alg2_kdu"] = kdu_alg2(household)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    household["regelbedarf"] = household["regelsatz"] + household["alg2_kdu"]

    household["alg2_ek"], household["alg2_grossek"] = alg2_inc(household)

    household = einkommensanrechnungsfrei(household, tb)

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


def regelsatz_alg2(household, tb):
    """Creating the variables need for the calculation of the alg2 regelsatz. Then
    according to the year the appropriate function is called"""
    children_age_info = {}
    for age in [(0, 6), (0, 15), (14, 24), (7, 13), (3, 6), (0, 2)]:
        children_age_info["child{}_{}_num".format(age[0], age[1])] = (
            household["child"] & household["age"].between(age[0], age[1])
        ).sum()
    children_age_info["child_num"] = household["child"].sum()
    children_age_info["adult_num"] = len(household) - children_age_info["child_num"]

    household["mehrbed"] = mehrbedarf_alg2(household, children_age_info, tb)
    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person

    if tb["yr"] <= 2010:
        calc_regelsatz = regelberechnung_until_2010
    else:
        calc_regelsatz = regelberechnung_2011_and_beyond

    household["regelsatz"] = calc_regelsatz(household, children_age_info, tb)
    return household


def regelberechnung_until_2010(household, children_age_info, tb):
    if children_age_info["adult_num"] == 1:
        return (
            tb["rs_hhvor"] * (1 + household["mehrbed"])
            + (tb["rs_hhvor"] * tb["a2ch14"] * children_age_info["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * children_age_info["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["adult_num"] > 1:
        return (
            (
                tb["rs_hhvor"] * tb["a2part"] * (1 + household["mehrbed"])
                + (tb["rs_hhvor"] * tb["a2part"])
                + (
                    tb["rs_hhvor"]
                    * tb["a2ch18"]
                    * np.maximum((children_age_info["adult_num"] - 2), 0)
                )
            )
            + (tb["rs_hhvor"] * tb["a2ch14"] * children_age_info["child14_24_num"])
            + (tb["rs_hhvor"] * tb["a2ch7"] * children_age_info["child7_13_num"])
            + (
                tb["rs_hhvor"]
                * tb["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def regelberechnung_2011_and_beyond(household, children_age_info, tb):
    if children_age_info["adult_num"] == 1:
        return (
            tb["rs_hhvor"] * (1 + household["mehrbed"])
            + (tb["rs_ch14"] * children_age_info["child14_24_num"])
            + (tb["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                tb["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["adult_num"] > 1:
        return (
            tb["rs_2adults"] * (1 + household["mehrbed"])
            + tb["rs_2adults"]
            + (tb["rs_madults"] * np.maximum((children_age_info["adult_num"] - 2), 0))
            + (tb["rs_ch14"] * children_age_info["child14_24_num"])
            + (tb["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                tb["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def mehrbedarf_alg2(household, children_age_info, tb):
    """ Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get
    36% on top alternatively, you get 12% per kid, depending on what's higher."""
    return household["alleinerz"] * np.minimum(
        tb["a2zu2"] / 100,
        np.maximum(
            tb["a2mbch1"] * children_age_info["child_num"],
            (
                (children_age_info["child0_6_num"] >= 1)
                | (2 <= children_age_info["child0_15_num"] <= 3)
            )
            * tb["a2mbch2"],
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


def alg2_2005_nq(household, tb):
    """ Nettoquote = Quotienten von bereinigtem Nettoeinkommen und
    Bruttoeinkommen. Vgl. § 3 Abs. 2 Alg II-V. """

    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit. Nach § 11 Abs. 2 Nr. 1 bis 5.
    alg2_2005_bne = np.maximum(
        household["m_wage"]
        - household["incometax"]
        - household["soli"]
        - household["svbeit"]
        - tb["a2we"]
        - tb["a2ve"],
        0,
    ).fillna(0)

    # Nettoquote:
    alg2_2005_nq = alg2_2005_bne / household["m_wage"]

    return alg2_2005_nq


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


def einkommensanrechnungsfrei(household, tb):
    """Determine the amount of income that is not deducted. Withdrawal rates
    depend on monthly earnings. § 30 SGB II. Since 01.04.2011 § 11b (4)."""

    # TODO: Rule 2005-01-01 to 2005-09-30
    if tb["yr"] == 2005:
        # Nettequote
        nq = alg2_2005_nq(household, tb)
        # Income in interval 1
        household.loc[(household["m_wage"].between(0, tb["a2eg1"])), "ekanrefrei"] = (
            tb["a2an1"] * nq * household["m_wage"]
        )
        # Income in interval 2
        household.loc[
            (household["m_wage"].between(tb["a2eg1"], tb["a2eg2"])), "ekanrefrei"
        ] = tb["a2an1"] * nq * tb["a2eg1"] + tb["a2an2"] * nq * (
            household["m_wage"] - tb["a2eg1"]
        )
        # Income in interval 3
        household.loc[
            (household["m_wage"].between(tb["a2eg2"], tb["a2eg3"])), "ekanrefrei"
        ] = (
            tb["a2an1"] * nq * tb["a2eg1"]
            + tb["a2an2"] * nq * (tb["a2eg2"] - tb["a2eg1"])
            + tb["a2an3"] * nq * (household["m_wage"] - tb["a2eg2"])
        )
        # Income beyond interval 3
        household.loc[(household["m_wage"] > tb["a2eg3"]), "ekanrefrei"] = (
            tb["a2an1"] * nq * tb["a2eg1"]
            + tb["a2an2"] * nq * (tb["a2eg2"] - tb["a2eg1"])
            + tb["a2an3"] * nq * (tb["a2eg3"] - tb["a2eg2"])
        )
    # TODO: Rule since 2005-10-01
    elif tb["yr"] >= 2006:
        # Number of children below the age of 18
        child0_18_num = (household["child"] & household["age"].between(0, 18)).sum()
        # Income in interval 1
        household.loc[(household["m_wage"].between(0, tb["a2eg1"])), "ekanrefrei"] = (
            tb["a2an1"] * household["m_wage"]
        )
        # Income in interval 2
        household.loc[
            (household["m_wage"].between(tb["a2eg1"], tb["a2eg2"])), "ekanrefrei"
        ] = tb["a2an1"] * tb["a2eg1"] + tb["a2an2"] * (
            household["m_wage"] - tb["a2eg1"]
        )
        if child0_18_num == 0:
            # Income in interval 3
            household.loc[
                (household["m_wage"].between(tb["a2eg2"], tb["a2eg3"])), "ekanrefrei"
            ] = (
                tb["a2an1"] * tb["a2eg1"]
                + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
                + tb["a2an3"] * (household["m_wage"] - tb["a2eg2"])
            )
            # Income beyond interval 3
            household.loc[(household["m_wage"] > tb["a2eg3"]), "ekanrefrei"] = (
                tb["a2an1"] * tb["a2eg1"]
                + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
                + tb["a2an3"] * (tb["a2eg3"] - tb["a2eg2"])
            )
        elif child0_18_num > 0:
            # Income in interval 3
            household.loc[
                (household["m_wage"].between(tb["a2eg2"], tb["a2eg3ki"]))
                & (child0_18_num > 0),
                "ekanrefrei",
            ] = (
                tb["a2an1"] * tb["a2eg1"]
                + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
                + tb["a2an3"] * (household["m_wage"] - tb["a2eg2"])
            )
            # Income beyond interval 3
            household.loc[(household["m_wage"] > tb["a2eg3ki"]), "ekanrefrei"] = (
                tb["a2an1"] * tb["a2eg1"]
                + tb["a2an2"] * (tb["a2eg2"] - tb["a2eg1"])
                + tb["a2an3"] * (tb["a2eg3ki"] - tb["a2eg2"])
            )

    # Children income is fully deducted, except for the first 100 €.
    household.loc[(household["child"]), "ekanrefrei"] = np.maximum(
        0, household["m_wage"] - 100
    )

    return household
