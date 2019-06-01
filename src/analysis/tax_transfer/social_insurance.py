import numpy as np
import pandas as pd
from termcolor import cprint


def soc_ins_contrib(df, tb, yr, ref=""):
    """Calculates Social Insurance Contributions

    4 branches of social insurances:

        - health
        - old-age pensions
        - unemployment
        - care

    There is a fixed rate on earnings up to a threshold,
    after which no rates are charged.

    'Minijobs' below 450€ are free of contributions
    For 'Midijobs' between 450€ and 850€, the rate increases
    smoothly until the regular one is reached

    """

    cprint("Social Insurance Contributions...", "red", "on_white")

    # initiate dataframe, indices must be identical
    ssc = pd.DataFrame(index=df.index.copy())

    # a couple of definitions
    westost = [~df["east"], df["east"]]
    # 'Bezugsgröße'
    ssc["bezgr"] = np.select(westost, [tb["bezgr_o"], tb["bezgr_w"]])
    ssc["kinderlos"] = (~df["haskids"]) & (df["age"] > 22)
    ssc["belowmini"] = 1 == np.select(
        westost, [df["m_wage"] < tb["mini_grenzew"], df["m_wage"] < tb["mini_grenzeo"]]
    )
    ssc["above_thresh_kv"] = 1 == np.select(
        westost, [df["m_wage"] > tb["kvmaxekw"], df["m_wage"] > tb["kvmaxeko"]]
    )
    ssc["above_thresh_rv"] = 1 == np.select(
        westost, [df["m_wage"] > tb["rvmaxekw"], df["m_wage"] > tb["rvmaxeko"]]
    )

    # This is probably the point where Entgeltpunkte should be updated as well.

    # First, define corrected wage; need to differentiate between East and West Germany
    ssc["svwage_pens"] = np.minimum(
        df["m_wage"], np.select(westost, [tb["rvmaxekw"], tb["rvmaxeko"]])
    )

    ssc["svwage_health"] = np.minimum(
        df["m_wage"], np.select(westost, [tb["kvmaxekw"], tb["kvmaxeko"]])
    )
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    ssc["rvbeit"] = tb["grvbs"] * ssc["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    ssc["avbeit"] = tb["alvbs"] * ssc["svwage_pens"]
    # Health Insurance for Employees (GKV)
    ssc["gkvbeit"] = tb["gkvbs_an"] * ssc["svwage_health"]
    # Care Insurance / Pflegeversicherung
    ssc["pvbeit"] = tb["gpvbs"] * ssc["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    ssc.loc[ssc["kinderlos"], "pvbeit"] = (tb["gpvbs"] + tb["gpvbs_kind"]) * ssc[
        "svwage_health"
    ]

    # Gleitzone / Midi-Jobs
    if (yr >= 2003) & (tb["midi_grenze"] > 0):
        # For midijobs, the rate is not calculated on the wage,
        # but on the 'bemessungsentgelt'
        # Contributions are usually shared equally by employee (AN) and
        # employer (AG). We are actually not interested in employer's contributions,
        # but we need them here as an intermediate step
        an_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_an"]
        ag_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_ag"]
        dbsv = an_anteil + ag_anteil
        pauschmini = tb["mini_ag_gkv"] + tb["mini_ag_grv"] + tb["stpag"]
        f = round(pauschmini / dbsv, 4)

        ssc["bemessungsentgelt"] = f * tb["mini_grenzew"] + (
            (tb["midi_grenze"] / (tb["midi_grenze"] - tb["mini_grenzew"]))
            - (tb["mini_grenzew"] / (tb["midi_grenze"] - tb["mini_grenzew"]) * f)
        ) * (df["m_wage"] - tb["mini_grenzew"])

        # This checks whether wage is in the relevant range
        ssc["in_gleitzone"] = df["m_wage"].between(
            np.select(westost, [tb["mini_grenzew"], tb["mini_grenzeo"]]),
            tb["midi_grenze"],
        )
        # Again, all branches of social insurance
        # First total amount, then employer, then employee

        # Old-Age Pensions
        ssc["gb_rv"] = 2 * tb["grvbs"] * ssc["bemessungsentgelt"]
        ssc.loc[ssc["in_gleitzone"], "ag_rvbeit"] = tb["grvbs"] * df["m_wage"]
        ssc.loc[ssc["in_gleitzone"], "rvbeit"] = ssc["gb_rv"] - ssc["ag_rvbeit"]

        # Health
        ssc["gb_gkv"] = (tb["gkvbs_an"] + tb["gkvbs_ag"]) * ssc["bemessungsentgelt"]
        ssc.loc[ssc["in_gleitzone"], "ag_gkvbeit"] = tb["gkvbs_ag"] * df["m_wage"]
        ssc.loc[ssc["in_gleitzone"], "gkvbeit"] = ssc["gb_gkv"] - ssc["ag_gkvbeit"]

        # Unemployment
        ssc["gb_alv"] = 2 * tb["alvbs"] * ssc["bemessungsentgelt"]
        ssc.loc[ssc["in_gleitzone"], "ag_avbeit"] = tb["alvbs"] * df["m_wage"]
        ssc.loc[ssc["in_gleitzone"], "avbeit"] = ssc["gb_alv"] - ssc["ag_avbeit"]

        # Long-Term Care
        ssc["gb_pv"] = 2 * tb["gpvbs"] * ssc["bemessungsentgelt"]
        ssc.loc[ssc["in_gleitzone"], "ag_pvbeit"] = tb["gpvbs"] * df["m_wage"]
        ssc.loc[ssc["in_gleitzone"], "pvbeit"] = (
            ssc["gb_pv"]
            - ssc["ag_pvbeit"]
            + (ssc["kinderlos"] * tb["gpvbs_kind"] * ssc["bemessungsentgelt"])
        )

        # Drop intermediate variables
        ssc = ssc.drop(
            ["gb_rv", "gb_gkv", "gb_alv", "gb_pv", "bemessungsentgelt"], axis=1
        )
    # END 'GLEITZONE'

    # check whether we are below 450€...set to zero
    for beit in [
        "rvbeit",
        "gkvbeit",
        "avbeit",
        "pvbeit",
        "ag_rvbeit",
        "ag_gkvbeit",
        "ag_avbeit",
        "ag_pvbeit",
    ]:
        ssc.loc[ssc["belowmini"], beit] = 0
    # Exception: since 2013, marginally employed people may pay pension
    # insurance contributions.
    """
    if yr > 2012:
        ssc.loc[df["m_wage"].between(1, tb["mini_grenzew"]), "rvbeit"] = tb[
            "grvbs_mini"
        ] * np.maximum(175, df["m_wage"])
    """
    # Self-employed may insure via the public health insurance
    # In that case, they pay the full contribution (employer + employee),
    # which is either assessed on their self-employemtn income or 3/4
    # of the 'Bezugsgröße'
    ssc.loc[(df["selfemployed"]) & (~df["pkv"]), "gkvbeit"] = (
        tb["gkvbs_an"] + tb["gkvbs_ag"]
    ) * np.minimum(
        df["m_self"], 0.75 * np.select(westost, [tb["bezgr_w"], tb["bezgr_o"]])
    )
    # Same holds for care insurance
    ssc.loc[(df["selfemployed"]) & (~df["pkv"]), "pvbeit"] = (
        2 * tb["gpvbs"]
        + np.select([ssc["kinderlos"], ~ssc["kinderlos"]], [tb["gpvbs_kind"], 0])
    ) * np.minimum(
        df["m_self"], 0.75 * np.select(westost, [tb["bezgr_w"], tb["bezgr_o"]])
    )
    # Health insurance for pensioners; they pay the standard health insurance rate...
    ssc["gkvrbeit"] = tb["gkvbs_an"] * np.minimum(
        df["m_pensions"], np.select(westost, [tb["kvmaxekw"], tb["kvmaxeko"]])
    )
    # but twice the care insurance rate.
    ssc["pvrbeit"] = (
        2
        * tb["gpvbs"]
        * np.minimum(
            df["m_pensions"], np.select(westost, [tb["kvmaxekw"], tb["kvmaxeko"]])
        )
    )
    ssc.loc[ssc["kinderlos"], "pvrbeit"] = (
        2 * tb["gpvbs"] + tb["gpvbs_kind"]
    ) * np.minimum(
        df["m_pensions"], np.select(westost, [tb["kvmaxekw"], tb["kvmaxeko"]])
    )

    ssc["gkvbeit"] = ssc["gkvbeit"] + ssc["gkvrbeit"]
    ssc["pvbeit"] = ssc["pvbeit"] + ssc["pvrbeit"]

    # Sum of Social Insurance Contributions (for employees)
    ssc["svbeit"] = ssc[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum(axis=1)

    return ssc[["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]]


def vorsorge2010(df, tb, yr, hyporun):
    """
        'Vorsorgeaufwendungen': Deduct part of your social insurance contributions
        from your taxable income
        This regulation has been changed often in recent years. In order not to make
        anyone worse off, the old regulation was maintained. Nowadays the older
        regulations don't play a large role (i.e. the new one is more beneficial most of
         the times) but they'd need to be implemented if earlier years are modelled.
        Vorsorgeaufwendungen until 2004
        TODO
        Vorsorgeaufwendungen since 2010
        § 10 (3) EStG
        The share of deductable pension contributions increases each year by 2 pp.
        ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
        4% from health contributions are not deductable.
        only deduct pension contributions up to the ceiling. multiply by 2
        because it's both employee and employer contributions.
        """
    westost = [~df["east"], df["east"]]
    rvbeit_vors = np.minimum(
        2 * df["rvbeit"],
        2 * tb["grvbs"] * np.select(westost, [tb["rvmaxekw"], tb["rvmaxeko"]]),
    )

    # calculate x% of relevant employer and employee contributions
    # then subtract employer contributions
    # also subtract health + care + unemployment insurance contributions
    altersvors2010 = ~df["child"] * (
        (0.6 + 0.02 * (np.minimum(yr, 2025) - 2005)) * (12 * rvbeit_vors)
        - (12 * 0.5 * rvbeit_vors)
    )
    # These you get anyway ('Basisvorsorge').
    sonstigevors2010 = 12 * (df["pvbeit"] + 0.96 * df["gkvbeit"])
    # maybe add avbeit, but do not exceed 1900€.
    sonstigevors2010 = np.maximum(
        sonstigevors2010,
        np.minimum(sonstigevors2010 + 12 * df["avbeit"], tb["vors_sonst_max"]),
    )

    if hyporun:
        vorsorge2010 = altersvors2010 + sonstigevors2010
    else:
        vorsorge2010 = np.fix(altersvors2010) + np.fix(sonstigevors2010)

    return vorsorge2010