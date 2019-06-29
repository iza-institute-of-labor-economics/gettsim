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

    # a couple of definitions

    # As there is only one household, we selcet west_ost dependent paramter in the
    # beginning and place them in a seperate dictionary tb_ost.
    if df["east"]:
        westost = "o"
    else:
        westost = "w"
    tb_ost = {}
    for val in ["bezgr_", "mini_grenze", "kvmaxek", "rvmaxek"]:
        tb_ost[val] = tb[val + westost]

    # ssc["above_thresh_kv"] = df["m_wage"] > tb_ost["kvmaxek"]
    #
    # ssc["above_thresh_rv"] = df["m_wage"] > tb_ost["rvmaxek"]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = df["m_wage"] < tb_ost["mini_grenze"]

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = tb["midi_grenze"] >= df["m_wage"] >= tb_ost["mini_grenze"]

    # Calculate accordingly the ssc
    if belowmini:
        ssc = ssc_mini_job()
    elif in_gleitzone:
        ssc = tb["calc_midi_contrib"](df, tb)
    else:
        ssc = ssc_regular_job(df, tb, tb_ost)

    # Exception: since 2013, marginally employed people may pay pension
    # insurance contributions.
    """
    if yr > 2012:
        ssc.loc[df["m_wage"].between(1, tb["mini_grenzew"]), "rvbeit"] = tb[
            "grvbs_mini"
        ] * np.maximum(175, df["m_wage"])
    """
    # Self-employed may insure via the public health and care insurance.
    if df["selfemployed"] & ~df["pkv"]:
        ssc["gkvbeit"] = selfemployed_gkv_ssc(df, tb, tb_ost)
        ssc["pvbeit"] = selfemployed_pv_ssc(df, tb, tb_ost)

    # Add the health insurance contribution for pensions
    ssc["gkvbeit"] += gkv_ssc_pensions(df, tb, tb_ost)

    # Add the care insurance contribution for pensions
    ssc["pvbeit"] += pv_ssc_pensions(df, tb, tb_ost)

    # Sum of Social Insurance Contributions (for employees)
    ssc["svbeit"] = ssc.loc[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum()

    return ssc.loc[["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]]


def ssc_mini_job():
    """Calculates the ssc for mini jobs."""
    mini = pd.Series()
    for beit in ["rvbeit", "gkvbeit", "avbeit", "pvbeit"]:
        mini[beit] = 0.0
    return mini


def ssc_regular_job(df, tb, tb_ost):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    regular = pd.Series()
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    regular["svwage_pens"] = np.minimum(df["m_wage"], tb_ost["rvmaxek"])
    regular["svwage_health"] = np.minimum(df["m_wage"], tb_ost["kvmaxek"])
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    regular["rvbeit"] = tb["grvbs"] * regular["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    regular["avbeit"] = tb["alvbs"] * regular["svwage_pens"]
    # Health Insurance for Employees (GKV)
    regular["gkvbeit"] = tb["gkvbs_an"] * regular["svwage_health"]
    # Care Insurance / Pflegeversicherung
    regular["pvbeit"] = tb["gpvbs"] * regular["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    if ~df["haskids"] & (df["age"] > 22):
        regular["pvbeit"] = (tb["gpvbs"] + tb["gpvbs_kind"]) * regular["svwage_health"]
    return regular


def selfemployed_gkv_ssc(df, tb, tb_ost):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (tb["gkvbs_an"] + tb["gkvbs_ag"]) * np.minimum(
        df["m_self"], 0.75 * tb_ost["bezgr_"]
    )


def selfemployed_pv_ssc(df, tb, tb_ost):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if ~df["haskids"] & (df["age"] > 22):
        return 2 * tb["gpvbs"] + tb["gpvbs_kind"] * np.minimum(
            df["m_self"], 0.75 * tb_ost["bezgr_"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(df["m_self"], 0.75 * tb_ost["bezgr_"])


def pv_ssc_pensions(df, tb, tb_ost):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if ~df["haskids"] & (df["age"] > 22):
        return (2 * tb["gpvbs"] + tb["gpvbs_kind"]) * np.minimum(
            df["m_pensions"], tb_ost["kvmaxek"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(df["m_pensions"], tb_ost["kvmaxek"])


def gkv_ssc_pensions(df, tb, tb_ost):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return tb["gkvbs_an"] * np.minimum(df["m_pensions"], tb_ost["kvmaxek"])


def calc_midi_contributions(df, tb):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""
    midi = pd.Series()
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
    midi["pvbeit"] = calc_midi_long_term_care_contr(df, midi, tb)

    return midi.loc[["rvbeit", "gkvbeit", "avbeit", "pvbeit"]]


def calc_midi_f(tb):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_an"]
    ag_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_ag"]
    dbsv = an_anteil + ag_anteil
    pauschmini = tb["mini_ag_gkv"] + tb["mini_ag_grv"] + tb["stpag"]
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(midi, tb):
    f = calc_midi_f(tb)
    return f * tb["mini_grenzew"] + (
        (tb["midi_grenze"] / (tb["midi_grenze"] - tb["mini_grenzew"]))
        - (tb["mini_grenzew"] / (tb["midi_grenze"] - tb["mini_grenzew"]) * f)
    ) * (midi["m_wage"] - tb["mini_grenzew"])


def calc_midi_old_age_pensions_contr(midi, tb):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * tb["grvbs"] * midi["bemessungsentgelt"]
    ag_rvbeit = tb["grvbs"] * midi["m_wage"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(midi, tb):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (tb["gkvbs_an"] + tb["gkvbs_ag"]) * midi["bemessungsentgelt"]
    ag_gkvbeit = tb["gkvbs_ag"] * midi["m_wage"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(midi, tb):
    grbetr_alv = 2 * tb["alvbs"] * midi["bemessungsentgelt"]
    ag_avbeit = tb["alvbs"] * midi["m_wage"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(df, midi, tb):
    grbetr_pv = 2 * tb["gpvbs"] * midi["bemessungsentgelt"]
    ag_pvbeit = tb["gpvbs"] * midi["m_wage"]
    if ~df["haskids"] & (df["age"] > 22):
        return grbetr_pv - ag_pvbeit + tb["gpvbs_kind"] * midi["bemessungsentgelt"]
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(df, tb):
    """Dummy function returning nothing
    """
    return pd.DataFrame(
        [{beit: np.nan for beit in ["rvbeit", "gkvbeit", "avbeit", "pvbeit"]}]
    )
