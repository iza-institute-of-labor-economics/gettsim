import numpy as np

from gettsim.auxiliary import aggr


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
    df["uhv_tu"] = aggr(df, "uhv", "all_tu")
    # First, calculate the need as for ALG2, but only for parents.
    df["kiz_ek_regel"] = calc_kiz_ek(df, tb)
    # Add rents. First, correct rent for the case of several tax units within the HH
    df["kiz_miete"] = df["miete"] * df["hh_korr"]
    df["kiz_heiz"] = df["heizkost"] * df["hh_korr"]
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf'.
    wb = get_wohnbedarf(max(tb["yr"], 2011))
    df["wb_eltern_share"] = 1.0
    for c in [1, 2]:
        for r in [1, 2, 3, 4]:
            df.loc[
                (df["child_num_tu"] == r) & (df["adult_num_tu"] == c), "wb_eltern_share"
            ] = (wb[r - 1][c - 1] / 100)
        df.loc[
            (df["child_num_tu"] >= 5) & (df["adult_num_tu"] == c), "wb_eltern_share"
        ] = (wb[4][c - 1] / 100)

    # apply this share to living costs
    # unlike ALG2, there is no check whether living costs are "appropriate".
    df["kiz_ek_kdu"] = df["wb_eltern_share"] * (df["kiz_miete"] + df["kiz_heiz"])
    df["kiz_ek_relev"] = df["kiz_ek_regel"] + df["kiz_ek_kdu"]

    # There is a maximum income threshold, depending on the need, plus the potential
    # kiz receipt
    # First, we need to count the number of children eligible to child benefit.
    df["child_num_kg"] = tb["childben_elig_rule"](df, tb).sum()

    df["kiz_ek_max"] = df["kiz_ek_relev"] + tb["a2kiz"] * df["child_num_kg"]
    # min income to be eligible for KIZ (different for singles and couples)
    df["kiz_ek_min"] = tb["a2kiz_minek_cou"] * (df["hhtyp"] == 4) + (
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
    df["kiz_ek_gross"] = df["alg2_grossek_hh"]
    df["kiz_ek_net"] = df["ar_alg2_ek_hh"]

    # Deductable income. 50% withdrawal rate.
    df["kiz_ek_anr"] = np.maximum(0, 0.5 * (df["ar_alg2_ek_hh"] - df["kiz_ek_relev"]))

    # Dummy variable whether household is in the relevant income range.
    df["kiz_incrange"] = (df["kiz_ek_gross"] >= df["kiz_ek_min"]) & (
        df["kiz_ek_net"] <= df["kiz_ek_max"]
    )
    # Finally, calculate the amount. Subtract deductable income with 50% and child
    # income fully!
    df["kiz"] = 0
    df.loc[df["kiz_incrange"], "kiz"] = np.maximum(
        0, tb["a2kiz"] * df["child_num_kg"] - df["kiz_ek_anr"] - df["uhv_tu"]
    )
    df["kiz_temp"] = df["kiz"].max()
    # Transfer some variables for eligibility check
    # kiz["ar_base_alg2_ek"] = df["ar_base_alg2_ek"]
    # kiz["n_pens"] = df["pensioner"].sum()
    return df


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
