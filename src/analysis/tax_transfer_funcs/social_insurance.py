import numpy as np
import pandas as pd
from termcolor import cprint


def soc_ins_contrib(df, tb):
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
    kinderlos = (~df["haskids"]) & (df["age"] > 22)
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
    ssc.loc[kinderlos, "pvbeit"] = (tb["gpvbs"] + tb["gpvbs_kind"]) * ssc[
        "svwage_health"
    ]

    # Gleitzone / Midi-Jobs
    # This checks whether wage is in the relevant range
    ssc["in_gleitzone"] = df["m_wage"].between(
        np.select(westost, [tb["mini_grenzew"], tb["mini_grenzeo"]]), tb["midi_grenze"]
    )

    midi = tb["calc_midi_contrib"](df, tb, kinderlos)

    for beit in ["rvbeit", "gkvbeit", "avbeit", "pvbeit"]:
        ssc.loc[ssc["in_gleitzone"], beit] = midi[beit]

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
        2 * tb["gpvbs"] + np.select([kinderlos, ~kinderlos], [tb["gpvbs_kind"], 0])
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
    ssc.loc[kinderlos, "pvrbeit"] = (2 * tb["gpvbs"] + tb["gpvbs_kind"]) * np.minimum(
        df["m_pensions"], np.select(westost, [tb["kvmaxekw"], tb["kvmaxeko"]])
    )

    ssc["gkvbeit"] = ssc["gkvbeit"] + ssc["gkvrbeit"]
    ssc["pvbeit"] = ssc["pvbeit"] + ssc["pvrbeit"]

    # Sum of Social Insurance Contributions (for employees)
    ssc["svbeit"] = ssc[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum(axis=1)

    return ssc[["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]]


def calc_midi_contributions(df, tb, kinderlos):
    # Calculates Contributions for wage in the 'Gleitzone'
    # For these jobs, the rate is not calculated on the wage,
    # but on the 'bemessungsentgelt'
    # Contributions are usually shared equally by employee (AN) and
    # employer (AG). We are actually not interested in employer's contributions,
    # but we need them here as an intermediate step

    # This function calculates the contributions for everybody.
    # Whether they apply (i.e. whether wage is within the gleitzone)
    # is checked outside.
    midi = pd.DataFrame(index=df.index.copy())
    midi["m_wage"] = df["m_wage"]

    midi["bemessungsentgelt"] = calc_midi_bemessungsentgelt(midi, tb)

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    midi["rvbeit"] = calc_midi_old_age_pensions_contr(midi, tb)

    # Health
    midi["gkvbeit"] = calc_midi_health_contr(midi, tb)

    # Unemployment
    midi["avbeit"] = calc_midi_unemployment_contr(midi, tb)

    # Long-Term Care
    midi["pvbeit"] = calc_midi_long_term_care_contr(midi, tb, kinderlos)

    return midi[["rvbeit", "gkvbeit", "avbeit", "pvbeit"]]


def calc_midi_f(midi, tb):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_an"]
    ag_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_ag"]
    dbsv = an_anteil + ag_anteil
    pauschmini = tb["mini_ag_gkv"] + tb["mini_ag_grv"] + tb["stpag"]
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(midi, tb):
    f = calc_midi_f(midi, tb)
    return f * tb["mini_grenzew"] + (
        (tb["midi_grenze"] / (tb["midi_grenze"] - tb["mini_grenzew"]))
        - (tb["mini_grenzew"] / (tb["midi_grenze"] - tb["mini_grenzew"]) * f)
    ) * (midi["m_wage"] - tb["mini_grenzew"])


def calc_midi_old_age_pensions_contr(midi, tb):
    """ Calculate old age pensions social insurance contribution for midi job."""
    gb_rv = 2 * tb["grvbs"] * midi["bemessungsentgelt"]
    ag_rvbeit = tb["grvbs"] * midi["m_wage"]
    return gb_rv - ag_rvbeit


def calc_midi_health_contr(midi, tb):
    """ Calculate social insurance health contributions for midi job."""
    gb_gkv = (tb["gkvbs_an"] + tb["gkvbs_ag"]) * midi["bemessungsentgelt"]
    ag_gkvbeit = tb["gkvbs_ag"] * midi["m_wage"]
    return gb_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(midi, tb):
    gb_alv = 2 * tb["alvbs"] * midi["bemessungsentgelt"]
    ag_avbeit = tb["alvbs"] * midi["m_wage"]
    return gb_alv - ag_avbeit


def calc_midi_long_term_care_contr(midi, tb, kinderlos):
    gb_pv = 2 * tb["gpvbs"] * midi["bemessungsentgelt"]
    ag_pvbeit = tb["gpvbs"] * midi["m_wage"]
    return (
        gb_pv - ag_pvbeit + (kinderlos * tb["gpvbs_kind"] * midi["bemessungsentgelt"])
    )


def no_midi(df, tb, kinderlos):
    """Dummy function returning nothing
    """
    return pd.DataFrame(
        [{beit: np.nan for beit in ["rvbeit", "gkvbeit", "avbeit", "pvbeit"]}]
    )
