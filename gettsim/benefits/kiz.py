import numpy as np


def kiz(household, params, arbeitsl_geld_2_params, kindergeld_params):
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
    household["kiz_ek_regel"] = calc_kiz_ek(household, params, arbeitsl_geld_2_params)

    # Calculate share of tax unit wrt whole household
    # Add rents. First, correct rent for the case of several tax units within the HH
    tax_unit_share = household.groupby("tu_id")["tu_id"].transform("count") / len(
        household
    )
    household["kiz_miete"] = household["miete"] * tax_unit_share
    household["kiz_heiz"] = household["heizkost"] * tax_unit_share
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf'.
    wb = get_wohnbedarf(max(params["year"], 2011))
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
    household["child_num_kg"] = kindergeld_params["childben_elig_rule"](
        household, kindergeld_params
    ).sum()

    household["kiz_ek_max"] = (
        household["kiz_ek_relev"] + params["a2kiz"] * household["child_num_kg"]
    )
    # min income to be eligible for KIZ (different for singles and couples)
    household["kiz_ek_min"] = calc_min_income_kiz(household, params)

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
    # TODO: Find a common name!
    household["kiz_ek_gross"] = household["alg2_grossek_hh"]
    household["kiz_ek_net"] = household["ar_alg2_ek_hh"]

    # Deductable income. 50% withdrawal rate.
    household["kiz_ek_anr"] = np.maximum(
        0, 0.5 * (household["ar_alg2_ek_hh"] - household["kiz_ek_relev"])
    )

    # Dummy variable whether household is in the relevant income range.
    household["kiz_incrange"] = (
        household["kiz_ek_gross"] >= household["kiz_ek_min"]
    ) & (household["kiz_ek_net"] <= household["kiz_ek_max"])
    # Finally, calculate the amount. Subtract deductable income with 50% and child
    # income fully!
    household["kiz"] = 0
    household.loc[household["kiz_incrange"], "kiz"] = np.maximum(
        0,
        params["a2kiz"] * household["child_num_kg"]
        - household["kiz_ek_anr"]
        - household["uhv_tu"],
    )
    household["kiz_temp"] = household["kiz"].max()
    # Transfer some variables for eligibility check
    # kiz["ar_base_alg2_ek"] = household["ar_base_alg2_ek"]
    # kiz["n_pens"] = household["pensioner"].sum()
    return household


def calc_min_income_kiz(household, params):
    # Are there kids in the household
    if household["child"].any() > 0:
        # Is it a single parent household
        if household["alleinerz"].all():
            return params["a2kiz_minek_sin"]
        else:
            return params["a2kiz_minek_cou"]
    else:
        return 0


def calc_kiz_ek(household, params, arbeitsl_geld_2_params):
    if params["year"] <= 2010:
        calc_kiz_regel = _calc_kiz_regel_until_2010
    else:
        calc_kiz_regel = _calc_kiz_regel_since_2011

    kiz_regel = calc_kiz_regel(household, arbeitsl_geld_2_params)

    return np.select(
        [
            household["adult_num_tu"] == 1,
            household["adult_num_tu"] == 2,
            household["adult_num_tu"] > 2,
        ],
        kiz_regel,
    )


def _calc_kiz_regel_until_2010(household, params):
    """"""
    return [
        params["rs_hhvor"] * (1 + household["mehrbed"]),
        params["rs_hhvor"] * params["a2part"] * (2 + household["mehrbed"]),
        params["rs_hhvor"] * params["a2ch18"] * household["adult_num_tu"],
    ]


def _calc_kiz_regel_since_2011(household, params):
    return [
        params["rs_hhvor"] * (1 + household["mehrbed"]),
        params["rs_2adults"] + ((1 + household["mehrbed"]) * params["rs_2adults"]),
        params["rs_madults"] * household["adult_num_tu"],
    ]


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
