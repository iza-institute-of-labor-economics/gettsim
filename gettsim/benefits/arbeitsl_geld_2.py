import datetime
from functools import partial

import numpy as np

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.piecewise_functions import piecewise_linear


def alg2(household, params):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """

    household = regelsatz_alg2(household, params)

    household["kost_unterk_m"] = kdu_alg2(household)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    household["regelbedarf_m"] = household["regelsatz_m"] + household["kost_unterk_m"]

    (
        household["arbeitsl_geld_2_eink"],
        household["arbeitsl_geld_2_brutto_eink"],
    ) = alg2_inc(household)

    household = params["calc_e_anr_frei"](household, params)

    # the final alg2 amount is the difference between the theoretical need and the
    # relevant income. this will be calculated later when several benefits have to be
    # compared.
    household["sum_arbeitsl_geld_2_eink"] = np.maximum(
        household["arbeitsl_geld_2_eink"] - household["eink_anrechn_frei"], 0
    )

    # Aggregate on HH
    for var in [
        "sum_arbeitsl_geld_2_eink",
        "arbeitsl_geld_2_brutto_eink",
        "unterhaltsvors_m",
    ]:
        household[f"{var}_hh"] = household[var].sum()

    household["sum_basis_arbeitsl_geld_2_eink"] = (
        household["sum_arbeitsl_geld_2_eink_hh"]
        + household["kindergeld_m_hh"]
        + household["unterhaltsvors_m_hh"]
    )

    return household


def regelsatz_alg2(household, params):
    """Creating the variables need for the calculation of the alg2 regelsatz. Then
    according to the year the appropriate function is called"""
    children_age_info = {}
    for age in [(0, 6), (0, 15), (14, 24), (7, 13), (3, 6), (0, 2)]:
        children_age_info["child{}_{}_num".format(age[0], age[1])] = (
            household["kind"] & household["alter"].between(age[0], age[1])
        ).sum()
    children_age_info["anz_kinder"] = household["kind"].sum()
    children_age_info["anz_erw"] = len(household) - children_age_info["anz_kinder"]

    household["mehrbed"] = mehrbedarf_alg2(household, children_age_info, params)

    household["regelsatz_m"] = params["calc_regelsatz"](
        household, children_age_info, params
    )

    return household


def regelberechnung_until_2010(household, children_age_info, params):
    if children_age_info["anz_erw"] == 1:
        return (
            params["rs_hhvor"] * (1 + household["mehrbed"])
            + (
                params["rs_hhvor"]
                * params["a2ch14"]
                * children_age_info["child14_24_num"]
            )
            + (
                params["rs_hhvor"]
                * params["a2ch7"]
                * children_age_info["child7_13_num"]
            )
            + (
                params["rs_hhvor"]
                * params["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["anz_erw"] > 1:
        return (
            (
                params["rs_hhvor"] * params["a2part"] * (1 + household["mehrbed"])
                + (params["rs_hhvor"] * params["a2part"])
                + (
                    params["rs_hhvor"]
                    * params["a2ch18"]
                    * np.maximum((children_age_info["anz_erw"] - 2), 0)
                )
            )
            + (
                params["rs_hhvor"]
                * params["a2ch14"]
                * children_age_info["child14_24_num"]
            )
            + (
                params["rs_hhvor"]
                * params["a2ch7"]
                * children_age_info["child7_13_num"]
            )
            + (
                params["rs_hhvor"]
                * params["a2ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def regelberechnung_2011_and_beyond(household, children_age_info, params):
    if children_age_info["anz_erw"] == 1:
        return (
            params["rs_hhvor"] * (1 + household["mehrbed"])
            + (params["rs_ch14"] * children_age_info["child14_24_num"])
            + (params["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                params["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )
    elif children_age_info["anz_erw"] > 1:
        return (
            params["rs_2adults"] * (1 + household["mehrbed"])
            + params["rs_2adults"]
            + (params["rs_madults"] * np.maximum((children_age_info["anz_erw"] - 2), 0))
            + (params["rs_ch14"] * children_age_info["child14_24_num"])
            + (params["rs_ch7"] * children_age_info["child7_13_num"])
            + (
                params["rs_ch0"]
                * (
                    children_age_info["child0_2_num"]
                    + children_age_info["child3_6_num"]
                )
            )
        )


def mehrbedarf_alg2(household, children_age_info, params):
    """ Additional need for single parents. Maximum 60% of the standard amount on top
    (a2zu2) if you have at least one kid below 6 or two or three below 15, you get
    36% on top alternatively, you get 12% per kid, depending on what's higher."""
    return household["alleinerziehend"] * np.minimum(
        params["a2zu2"] / 100,
        np.maximum(
            params["a2mbch1"] * children_age_info["anz_kinder"],
            (
                (children_age_info["child0_6_num"] >= 1)
                | (2 <= children_age_info["child0_15_num"] <= 3)
            )
            * params["a2mbch2"],
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
        (household["kaltmiete_m"] + household["heizkost_m"]) / household["wohnfläche"],
        10,
    )
    if household["bewohnt_eigentum"].iloc[0]:
        wohnfl_justified = np.minimum(
            household["wohnfläche"], 80 + np.maximum(0, (len(household) - 2) * 20)
        )
    else:
        wohnfl_justified = np.minimum(
            household["wohnfläche"], (45 + (len(household) - 1) * 15)
        )

    return rent_per_sqm * wohnfl_justified


def alg2_inc(household):
    """Relevant income of alg2."""
    # Income relevant to check against ALG2 claim
    alg2_grossek = grossinc_alg2(household)
    # ...deduct income tax and social security contributions
    alg2_ek = np.maximum(
        alg2_grossek
        - household["eink_st_m"]
        - household["soli_st_m"]
        - household["sozialv_beit_m"],
        0,
    ).fillna(0)

    return alg2_ek, alg2_grossek


def grossinc_alg2(household):
    """Calculating the gross income relevant for alg2."""
    return (
        household[
            [
                "bruttolohn_m",
                "sonstig_eink_m",
                "eink_selbstst_m",
                "vermiet_eink_m",
                "kapital_eink_m",
                "ges_rente_m",
                "arbeitsl_geld_m",
                "elterngeld_m",
            ]
        ]
        .sum(axis=1)
        .fillna(0)
    )


def e_anr_frei_2005_01(household, params):
    """Calculate income not subject to transfer withdrawal for the household.

    Legislation in force 2005-01-01 to 2005-09-30.

    Determine the gross income that is not deducted. Withdrawal rates depend
    on monthly earnings. § 30 SGB II."""

    cols = [
        "bruttolohn_m",
        "eink_anrechn_frei",
        "eink_st_m",
        "soli_st_m",
        "sozialv_beit_m",
    ]
    household.loc[:, cols] = household.groupby("p_id")[cols].apply(
        e_anr_frei_person_2005_01, params, params["a2eg3"]
    )

    return household


def e_anr_frei_person_2005_01(person, params, a2eg3):
    """Calculate income not subject to transfer withdrawal for each person.

    Legislation in force 2005-01-01 to 2005-09-30.

    """

    m_wage = person["bruttolohn_m"].iloc[0]

    # Nettoquote
    nq = alg2_2005_nq(person, params)

    # Income not deducted
    if m_wage <= params["a2eg1"]:
        person["eink_anrechn_frei"] = params["a2an1"] * nq * m_wage

    elif params["a2eg1"] < m_wage <= params["a2eg2"]:
        person["eink_anrechn_frei"] = params["a2an1"] * nq * params["a2eg1"] + params[
            "a2an2"
        ] * nq * (m_wage - params["a2eg1"])

    elif params["a2eg2"] < m_wage <= a2eg3:
        person["eink_anrechn_frei"] = (
            params["a2an1"] * nq * params["a2eg1"]
            + params["a2an2"] * nq * (params["a2eg2"] - params["a2eg1"])
            + params["a2an3"] * nq * (m_wage - params["a2eg2"])
        )

    else:
        person["eink_anrechn_frei"] = (
            params["a2an1"] * nq * params["a2eg1"]
            + params["a2an2"] * nq * (params["a2eg2"] - params["a2eg1"])
            + params["a2an3"] * nq * (a2eg3 - params["a2eg2"])
        )

    return person


def alg2_2005_nq(person, params):
    """Calculate Nettoquote

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3
    Abs. 2 Alg II-V.

    """

    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit. Nach § 11 Abs. 2 Nr. 1
    # bis 5.
    alg2_2005_bne = np.clip(
        person["bruttolohn_m"]
        - person["eink_st_m"]
        - person["soli_st_m"]
        - person["sozialv_beit_m"]
        - params["a2we"]
        - params["a2ve"],
        0,
        None,
    )

    # Nettoquote:
    alg2_2005_nq = alg2_2005_bne / person["bruttolohn_m"]

    return alg2_2005_nq


def e_anr_frei_2005_10(household, params):
    """Calculate income not subject to transfer withdrawal for the household.

    Legislation in force since 2005-10-01.

    Determine the gross income that is not deducted. Withdrawal rates depend
    on monthly earnings and on the number of children in the household. § 30 SGB
    II. Since 01.04.2011 § 11b.

    """

    # Calculate the number of children below the age of 18.
    num_childs_0_18 = (household["kind"] & (household["alter"] < 18)).sum()

    a2eg3 = params["a2eg3"] if num_childs_0_18 == 0 else params["a2eg3ki"]

    cols = ["bruttolohn_m", "eink_anrechn_frei"]
    household.loc[:, cols] = household.groupby("p_id")[cols].apply(
        e_anr_frei_person_2005_10, params, a2eg3
    )

    return household


def e_anr_frei_person_2005_10(person, params, a2eg3):
    """Calculate income not subject to transfer withdrawal for each person.

    Legislation in force since 2005-10-01.

    """

    m_wage = person["bruttolohn_m"].iloc[0]

    # Income not deducted
    if m_wage < params["a2eg1"]:
        person["eink_anrechn_frei"] = params["a2an1"] * m_wage

    elif params["a2eg1"] <= m_wage < params["a2eg2"]:
        person["eink_anrechn_frei"] = params["a2an1"] * params["a2eg1"] + params[
            "a2an2"
        ] * (m_wage - params["a2eg1"])

    elif params["a2eg2"] <= m_wage < a2eg3:
        person["eink_anrechn_frei"] = (
            params["a2an1"] * params["a2eg1"]
            + params["a2an2"] * (params["a2eg2"] - params["a2eg1"])
            + params["a2an3"] * (m_wage - params["a2eg2"])
        )

    else:
        person["eink_anrechn_frei"] = (
            params["a2an1"] * params["a2eg1"]
            + params["a2an2"] * (params["a2eg2"] - params["a2eg1"])
            + params["a2an3"] * (a2eg3 - params["a2eg2"])
        )

    return person


def regrouped_ein_anr_frei(household, params):
    """Calculate income not subject to transfer withdrawal for each person.

    """
    # If there live kids in the household, we select different parameters.
    if household["kind"].any():
        e_anr_frei_params = params["e_anr_frei_kinder"]
    else:
        e_anr_frei_params = params["e_anr_frei"]

    in_cols = [
        "bruttolohn_m",
        "eink_anrechn_frei",
        "eink_st_m",
        "soli_st_m",
        "sozialv_beit_m",
    ]
    # Everything was already initialized
    out_cols = []
    household = apply_tax_transfer_func(
        household,
        tax_func=eink_anr_frei_person,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"e_anr_frei_params": e_anr_frei_params, "params": params,},
    )

    return household


def eink_anr_frei_person(person, e_anr_frei_params, params):
    # In the first version of alg2, the rates were multiplied by the nettoquote.
    if params["datum"] < datetime.date(year=2005, month=10, day=1):
        e_anr_frei_params["rates"] *= alg2_2005_nq(person, params)

    person["eink_anrechn_frei"] = piecewise_linear(
        person["bruttolohn_m"], **e_anr_frei_params
    )
    return person
