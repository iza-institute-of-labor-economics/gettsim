import numpy as np
import pandas as pd
from src.model_code.imports import aggr
from termcolor import cprint


def favorability_check(df, tb, yr):
    """ 'Higher-Yield Tepst'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child
        allowance (_nokfb) AND receiving child benefit with the tax burden including
        the child allowance (_kfb), but without child benefit. The most beneficial (
        for the household) is chocen. If child allowance is claimed, kindergeld is
        set to zero A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    fc = pd.DataFrame(index=df.index.copy())
    fc["tu_id"] = df["tu_id"]
    fc["hid"] = df["hid"]
    fc["pid"] = df["pid"]
    fc["kindergeld"] = df["kindergeld_basis"]
    fc["kindergeld_tu"] = df["kindergeld_tu_basis"]

    cprint("Günstigerprüfung...", "red", "on_white")
    if yr < 2009:
        inclist = ["nokfb", "kfb"]
    else:
        inclist = ["nokfb", "abg_nokfb", "kfb", "abg_kfb"]
    """
    df = df.sort_values(by=['hid', 'tu_id', 'pid'])
    df[['hid', 'tu_id', 'child', 'tax_nokfb_tu', 'tax_kfb_tu',
        'kindergeld_basis' ,'kindergeld_tu_basis']].to_excel('Z:/test/fav_check.xlsx')
    """
    for inc in inclist:
        # Nettax is defined on the maximum within the tax unit.
        # Reason: This way, kids get assigned the tax payments of their parents,
        # ensuring correct treatment afterwards
        fc["tax_" + inc + "_tu"] = df["tax_" + inc + "_tu"]
        fc = fc.join(
            fc.groupby(["tu_id"])["tax_" + inc + "_tu"].max(),
            on=["tu_id"],
            how="left",
            rsuffix="_max",
        )
        fc = fc.rename(columns={"tax_" + inc + "_tu_max": "nettax_" + inc})
        # for those tax bases without capital taxes in tariff,
        # add abgeltungssteuer
        if "abg" not in inc:
            fc["nettax_" + inc] = fc["nettax_" + inc] + df["abgst_tu"]
        # For those tax bases without kfb, subtract kindergeld.
        # Before 1996, both child allowance and child benefit could be claimed
        if ("nokfb" in inc) | (yr <= 1996):
            fc["nettax_" + inc] = fc["nettax_" + inc] - (12 * df["kindergeld_tu_basis"])
    # get the maximum income, i.e. the minimum payment burden
    fc["minpay"] = fc.filter(regex="nettax").min(axis=1)
    # relevant tax base. not really needed...
    # fc['tax_income'] = 0
    # relevant incometax associated with this tax base
    fc["incometax_tu"] = 0
    # secures that every tax unit gets 'treated'
    fc["abgehakt"] = False
    for inc in inclist:
        """
        fc.loc[(fc['minpay'] == fc['nettax_' + inc])
               & (~fc['abgehakt'])
               & (~df['child']),
               'tax_income'] = df['zve_'+inc]
        """
        # Income Tax in monthly terms! And write only to parents
        fc.loc[
            (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]) & (~df["child"]),
            "incometax_tu",
        ] = (df["tax_" + inc + "_tu"] / 12)
        # set kindergeld to zero if necessary.
        if (not ("nokfb" in inc)) | (yr <= 1996):
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "kindergeld"
            ] = 0
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]),
                "kindergeld_tu",
            ] = 0
        if "abg" in inc:
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "abgst"
            ] = 0
            fc.loc[
                (fc["minpay"] == fc["nettax_" + inc]) & (~fc["abgehakt"]), "abgst_tu"
            ] = 0
        fc.loc[(fc["minpay"] == fc["nettax_" + inc]), "abgehakt"] = True

    # Aggregate Child benefit on the household.
    fc["kindergeld_hh"] = fc["kindergeld"].sum()

    # Control output
    # df.to_excel(
    #     pd.ExcelWriter(data_path + "check_güsntiger.xlsx"),
    #     sheet_name="py_out",
    #     columns=[
    #         "tu_id",
    #         "child",
    #         "zveranl",
    #         "minpay",
    #         "incometax",
    #         "abgehakt",
    #         "nettax_abg_kfb_tu",
    #         "zve_abg_kfb_tu",
    #         "tax_abg_kfb_tu",
    #         "nettax_abg_kfb_tu",
    #         "zve_abg_kfb_tu",
    #         "tax_abg_kfb_tu",
    #         "nettax_abg_kfb_tu",
    #         "zve_abg_kfb_tu",
    #         "tax_abg_kfb_tu",
    #         "nettax_abg_kfb_tu",
    #         "zve_abg_kfb_tu",
    #         "tax_abg_kfb_tu",
    #     ],
    #     na_rep="NaN",
    #     freeze_panes=(0, 1),
    # )
    # pd.to_pickle(df, data_path + ref + "/taxben_check")
    # df.to_excel(
    #     pd.ExcelWriter(data_path + "check_tax_incomes.xlsx"),
    #     sheet_name="py_out",
    #     columns=[
    #         "hid",
    #         "pid",
    #         "age",
    #         "female",
    #         "child",
    #         "zve_nokfb",
    #         "zve_kfb",
    #         "tax_nokfb",
    #         "tax_kfb",
    #         "gross_e1",
    #         "gross_e4",
    #         "gross_e5",
    #         "gross_e6",
    #         "gross_e7",
    #         "gross_gde",
    #     ],
    #     na_rep="NaN",
    #     freeze_panes=(0, 1),
    # )
    return fc[
        ["hid", "pid", "incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
    ]


def uhv(df, tb, taxyear):
    """ Advanced Alimony Payment / Unterhaltsvorschuss (UHV)

    In Germany, Single Parents get alimony payments for themselves and for their child
    from the ex partner. If the ex partner is not able to pay the child alimony,
    the government pays the child alimony to the mother (or the father, if he has the
    kids)
    Since 2017, the receipt of this
    UHV has been extended substantially and needs to be taken into account, since it's
    dominant to other transfers, i.e. single parents 'have to' apply for it.

    returns:
        uhv (pd.Series): Alimony Payment on individual level
    """
    cprint("Unterhaltsvorschuss...", "red", "on_white")
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit
    uhv = pd.DataFrame(index=df.index.copy())
    uhv["tu_id"] = df["tu_id"]
    uhv["zveranl"] = df["zveranl"]

    uhv["uhv"] = 0

    # Amounts depend on age
    uhv.loc[df["age"].between(0, 5) & df["alleinerz"]] = tb["uhv5"]
    uhv.loc[df["age"].between(6, 11) & df["alleinerz"]] = tb["uhv11"]
    # Older kids get it only if the parent has income > 600€
    uhv["uhv_inc"] = df[
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

    uhv["uhv_inc_tu"] = uhv["uhv_inc"].sum()
    uhv.loc[
        (df["age"].between(12, 17)) & (df["alleinerz"]) & (uhv["uhv_inc_tu"] > 600),
        "uhv",
    ] = tb["uhv17"]
    # TODO: Check against actual transfers

    return uhv["uhv"]


def kiz(df, tb, yr, hyporun):
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
    cprint("Kinderzuschlag...", "red", "on_white")

    kiz = pd.DataFrame(index=df.index.copy())
    kiz["hid"] = df["hid"]
    kiz["tu_id"] = df["tu_id"]
    kiz["uhv_tu"] = aggr(df, "uhv", "all_tu")
    # First, calculate the need as for ALG2, but only for parents.
    if yr <= 2010:
        # not yet implemented
        kiz_regel = [
            tb["rs_hhvor"] * (1 + df["mehrbed"]),
            tb["rs_hhvor"] * tb["a2part"] * (2 + df["mehrbed"]),
            tb["rs_hhvor"] * tb["a2ch18"] * df["adult_num_tu"],
        ]
    else:
        kiz_regel = [
            tb["rs_hhvor"] * (1 + df["mehrbed"]),
            tb["rs_2adults"] + ((1 + df["mehrbed"]) * tb["rs_2adults"]),
            tb["rs_madults"] * df["adult_num_tu"],
        ]

    kiz["kiz_ek_regel"] = np.select(
        [df["adult_num_tu"] == 1, df["adult_num_tu"] == 2, df["adult_num_tu"] > 2],
        kiz_regel,
    )
    # Add rents. First, correct rent for the case of several tax units within the HH
    kiz["kiz_miete"] = df["miete"] * df["hh_korr"]
    kiz["kiz_heiz"] = df["heizkost"] * df["hh_korr"]
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf'.
    wb = get_wohnbedarf(max(yr, 2011))
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
    kiz["kiz_ek_kdu"] = kiz["wb_eltern_share"] * (kiz["kiz_miete"] + kiz["kiz_heiz"])

    kiz["kiz_ek_relev"] = kiz["kiz_ek_regel"] + kiz["kiz_ek_kdu"]

    # There is a maximum income threshold, depending on the need, plus the potential
    # kiz receipt
    kiz["kiz_ek_max"] = kiz["kiz_ek_relev"] + tb["a2kiz"] * df["child_num_tu"]
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

    # Deductable income. 50% withdrawal rate, rounded to 5€ values.
    if not hyporun:
        kiz["kiz_ek_anr"] = np.maximum(
            0, round((df["ar_alg2_ek_hh"] - kiz["kiz_ek_relev"]) / 10) * 5
        )
    if hyporun:
        kiz["kiz_ek_anr"] = np.maximum(
            0, 0.5 * (df["ar_alg2_ek_hh"] - kiz["kiz_ek_relev"])
        )

    # Dummy variable whether household is in the relevant income range.
    kiz["kiz_incrange"] = (kiz["kiz_ek_gross"] >= kiz["kiz_ek_min"]) & (
        kiz["kiz_ek_net"] <= kiz["kiz_ek_max"]
    )
    # Finally, calculate the amount. Subtract deductable income with 50% and child
    # income fully!
    kiz["kiz"] = 0
    kiz.loc[kiz["kiz_incrange"], "kiz"] = np.maximum(
        0, tb["a2kiz"] * df["child_num_tu"] - kiz["kiz_ek_anr"] - kiz["uhv_tu"]
    )

    # Extend the amount to the other hh members for complementarity with wohngeld and
    # alg2
    kiz = kiz.join(
        kiz.groupby(["hid"])["kiz"].max(), on=["hid"], how="left", rsuffix="_temp"
    )

    kiz["kiz"] = kiz["kiz_temp"]
    ###############################
    # Check eligibility for benefits
    ###############################
    # transfer some variables...
    kiz["ar_base_alg2_ek"] = df["ar_base_alg2_ek"]
    kiz["wohngeld_basis"] = df["wohngeld_basis_hh"]

    kiz["ar_wg_alg2_ek"] = kiz["ar_base_alg2_ek"] + kiz["wohngeld_basis"]
    kiz["ar_kiz_alg2_ek"] = kiz["ar_base_alg2_ek"] + kiz["kiz"]
    kiz["ar_wgkiz_alg2_ek"] = (
        kiz["ar_base_alg2_ek"] + kiz["wohngeld_basis"] + kiz["kiz"]
    )

    for v in ["base", "wg", "kiz", "wgkiz"]:
        kiz["fehlbedarf_" + v] = df["regelbedarf"] - kiz["ar_" + v + "_alg2_ek"]
        kiz["m_alg2_" + v] = np.maximum(kiz["fehlbedarf_" + v], 0)

    # There is a rule which benefits are superior to others
    # If there is a positive ALG2 claim, but the need can be covered with
    # Housing Benefit (and possibly add. child benefit),
    # the HH has to claim the housing benefit and addit. child benefit.
    # There is no way you can receive ALG2 and Wohngeld at the same time!
    for v in ["wg", "kiz", "wgkiz"]:
        kiz[v + "_vorrang"] = (kiz["m_alg2_" + v] == 0) & (kiz["m_alg2_base"] > 0)

    kiz["m_alg2"] = kiz["m_alg2_base"]
    # If this is the case set alg2 to zero.
    kiz.loc[
        (kiz["wg_vorrang"]) | (kiz["kiz_vorrang"]) | (kiz["wgkiz_vorrang"]), "m_alg2"
    ] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    kiz["wohngeld"] = kiz["wohngeld_basis"]
    kiz.loc[
        (~kiz["wg_vorrang"]) & (~kiz["wgkiz_vorrang"]) & (kiz["m_alg2_base"] > 0),
        "wohngeld",
    ] = 0
    kiz.loc[
        (~kiz["kiz_vorrang"]) & (~kiz["wgkiz_vorrang"]) & (kiz["m_alg2_base"] > 0),
        "kiz",
    ] = 0

    # Pensioners do not receive Kiz. They actually do not receive ALGII, too. Instead,
    # they get 'Grundleistung im Alter', which pays the same amount.
    df["n_pens"] = df.groupby("hid")["pensioner"].transform("sum")
    for ben in ["kiz", "wg", "m_alg2"]:
        kiz.loc[df["n_pens"] > 1, ben] = 0

    assert kiz["m_alg2"].notna().all()
    assert kiz["wohngeld"].notna().all()
    assert kiz["kiz"].notna().all()
    return kiz[["kiz", "wohngeld", "m_alg2"]]


def kindergeld(df, tb, yr, ref=""):
    """ Child Benefit (kindergeld)
    Basic Amount for each child, hours restriction applies

    Returns:
        pd.series:
            kindergeld_basis: Kindergeld on the individual level
            kindergeld_tu_basis: Kindergeld summed up within the tax unit
    """
    kg = pd.DataFrame(index=df.index.copy())
    kg["tu_id"] = df["tu_id"]
    kg["eligible"] = 1
    if yr > 2011:
        kg["eligible"] = kg["eligible"].where(
            (df["age"] <= tb["kgage"]) & (df["w_hours"] <= 20) & (df["ineducation"]), 0
        )
    else:
        kg["eligible"] = kg["eligible"].where(
            (df["age"] <= tb["kgage"])
            & (df["m_wage"] <= tb["kgfreib"] / 12)
            & (df["ineducation"]),
            0,
        )

    kg["child_count"] = kg.groupby(["tu_id"])["eligible"].cumsum()

    kg_amounts = {1: tb["kgeld1"], 2: tb["kgeld2"], 3: tb["kgeld3"], 4: tb["kgeld4"]}
    kg["kindergeld_basis"] = kg["child_count"].replace(kg_amounts)
    kg.loc[kg["child_count"] > 4, "kindergeld_basis"] = tb["kgeld4"]
    kg["kindergeld_tu_basis"] = kg.groupby("tu_id")["kindergeld_basis"].transform(sum)

    # kg.drop(['child_count', 'eligible', 'kindergeld'], axis=1, inplace=True)

    return kg[["kindergeld_basis", "kindergeld_tu_basis"]]


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
