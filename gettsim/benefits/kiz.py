import numpy as np


def kiz(household, tb):
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
    household["uhv_tu"] = household.groupby("tu_id")["uhv"].transform("sum")
    # First, calculate the need as for ALG2, but only for parents.
    household["kiz_ek_regel"] = calc_kiz_ek(household, tb)
    # Add rents. First, correct rent for the case of several tax units within the HH
    household["kiz_miete"] = household["miete"] * household["hh_korr"]
    household["kiz_heiz"] = household["heizkost"] * household["hh_korr"]
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf'.
    wb = get_wohnbedarf(max(tb["yr"], 2011))
    household["wb_eltern_share"] = 1.0
    for c in [1, 2]:
        for r in [1, 2, 3, 4]:
            household.loc[
                (household["child_num_tu"] == r) & (household["adult_num_tu"] == c),
                "wb_eltern_share",
            ] = (wb[r - 1][c - 1] / 100)
        household.loc[
            (household["child_num_tu"] >= 5) & (household["adult_num_tu"] == c),
            "wb_eltern_share",
        ] = (wb[4][c - 1] / 100)

    # apply this share to living costs
    # unlike ALG2, there is no check whether living costs are "appropriate".
    household["kiz_ek_kdu"] = household["wb_eltern_share"] * (
        household["kiz_miete"] + household["kiz_heiz"]
    )
    household["kiz_ek_relev"] = household["kiz_ek_regel"] + household["kiz_ek_kdu"]

    # There is a maximum income threshold, depending on the need, plus the potential
    # kiz receipt
    # First, we need to count the number of children eligible to child benefit.
    household["child_num_kg"] = tb["childben_elig_rule"](household, tb).sum()

    household["kiz_ek_max"] = (
        household["kiz_ek_relev"] + tb["a2kiz"] * household["child_num_kg"]
    )
    # min income to be eligible for KIZ (different for singles and couples)
    household["kiz_ek_min"] = tb["a2kiz_minek_cou"] * (household["hhtyp"] == 4) + (
        tb["a2kiz_minek_sin"] * (household["alleinerz"])
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
    household["kiz_ek_gross"] = household["alg2_grossek_hh"]
    household["kiz_ek_net"] = household["ar_alg2_ek_hh"]

    # Deductable income from parent(s). 50% withdrawal rate until 07/19, then 45%
    household["kiz_ek_anr"] = np.maximum(
        0,
        tb["a2kiz_withdrawal_rate"]
        * (household["ar_alg2_ek_hh"] - household["kiz_ek_relev"]),
    )

    # Child income
    household["childinc_tu"] = (household["child"] * household["m_wage"]).sum()
    household = tb["calc_kiz_amount"](household, tb)
    household["kiz_temp"] = household["kiz"].max()
    # Transfer some variables for eligibility check
    # kiz["ar_base_alg2_ek"] = household["ar_base_alg2_ek"]
    # kiz["n_pens"] = household["pensioner"].sum()
    return household


def calc_kiz_amount_2005(household, tb):
    """ Kinderzuschlag from 2005 until 07/2019"
    """
    # Dummy variable whether household is in the relevant income range.
    household["kiz_incrange"] = (
        household["kiz_ek_gross"] >= household["kiz_ek_min"]
    ) & (household["kiz_ek_net"] <= household["kiz_ek_max"])
    # Finally, calculate the amount. Adult income is partly deducted.
    # Child income is fully deducted until 07/2019
    household["kiz"] = 0
    household.loc[household["kiz_incrange"], "kiz"] = np.maximum(
        0,
        tb["a2kiz"] * household["child_num_kg"]
        - household["kiz_ek_anr"]
        - household["childinc_tu"]
        - household["uhv_tu"],
    )

    return household


def calc_kiz_amount_2020(household, tb):
    """ Kinderzuschlag since 07/2019
        - no maximum income threshold.
        - child income is only partly deducted, just as parents income
    """
    household["kiz"] = 0
    household.loc[
        household["kiz_ek_gross"] >= household["kiz_ek_min"], "kiz"
    ] = np.maximum(
        0,
        tb["a2kiz"] * household["child_num_kg"]
        - household["kiz_ek_anr"]
        - tb["a2kiz_withdrawal_rate"] * household["childinc_tu"]
        - household["uhv_tu"],
    )

    return household


def calc_kiz_ek(household, tb):
    if tb["yr"] <= 2010:
        # not yet implemented
        kiz_regel = _calc_kiz_regel_until_2010(household, tb)
    else:
        kiz_regel = _calc_kiz_regel_since_2011(household, tb)

    return np.select(
        [
            household["adult_num_tu"] == 1,
            household["adult_num_tu"] == 2,
            household["adult_num_tu"] > 2,
        ],
        kiz_regel,
    )


def _calc_kiz_regel_until_2010(household, tb):
    """"""
    return [
        tb["rs_hhvor"] * (1 + household["mehrbed"]),
        tb["rs_hhvor"] * tb["a2part"] * (2 + household["mehrbed"]),
        tb["rs_hhvor"] * tb["a2ch18"] * household["adult_num_tu"],
    ]


def _calc_kiz_regel_since_2011(household, tb):
    return [
        tb["rs_hhvor"] * (1 + household["mehrbed"]),
        tb["rs_2adults"] + ((1 + household["mehrbed"]) * tb["rs_2adults"]),
        tb["rs_madults"] * household["adult_num_tu"],
    ]


def get_wohnbedarf(yr):
    """ Specifies the percent share of living costs that is attributed to the parents
        This is a share that is defined by the "Existenzminimumsbericht".

        The actual tables are found in the official "Merkblatt Kinderzuschlag".
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
        "2020": [[77, 84], [63, 72], [53, 63], [46, 56], [40, 50]],
    }

    return wohnbedarf[str(yr)]
