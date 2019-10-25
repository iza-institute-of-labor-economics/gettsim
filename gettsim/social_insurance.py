import numpy as np

OUT_COLS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


def soc_ins_contrib(df_row, tb):
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
    # initiate dataframe, indices must be identical

    # a couple of definitions

    # As there is only one household, we selcet west_ost dependent paramter in the
    # beginning and place them in a seperate dictionary tb_ost.
    westost = "o" if df_row["east"].all() else "w"
    tb_ost = {}
    for val in ["bezgr_", "mini_grenze", "kvmaxek", "rvmaxek"]:
        tb_ost[val] = tb[val + westost]

    # ssc["above_thresh_kv"] = inout["m_wage"] > tb_ost["kvmaxek"]
    #
    # ssc["above_thresh_rv"] = inout["m_wage"] > tb_ost["rvmaxek"]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = df_row["m_wage"] < tb_ost["mini_grenze"]

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = (tb["midi_grenze"] >= df_row["m_wage"]) & (
        df_row["m_wage"] >= tb_ost["mini_grenze"]
    )

    # Calculate accordingly the ssc
    if belowmini.all():
        df_row.loc[:, OUT_COLS] = 0.0
    elif in_gleitzone.all():
        # TODO: Before and in 2003 tb["midi_grenze"] is 0 and therefore we won't reach
        #  this.
        df_row = tb["calc_midi_contrib"](df_row, tb)
    else:
        df_row = ssc_regular_job(df_row, tb, tb_ost)

    # Self-employed may insure via the public health and care insurance.
    if (df_row["selfemployed"] & ~df_row["pkv"]).all():
        df_row["gkvbeit"] = selfemployed_gkv_ssc(df_row, tb, tb_ost)
        df_row["pvbeit"] = selfemployed_pv_ssc(df_row, tb, tb_ost)

    # Add the health insurance contribution for pensions
    df_row["gkvbeit"] += gkv_ssc_pensions(df_row, tb, tb_ost)

    # Add the care insurance contribution for pensions
    df_row["pvbeit"] += pv_ssc_pensions(df_row, tb, tb_ost)

    # Sum of Social Insurance Contributions (for employees)
    df_row["svbeit"] = df_row[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum(axis=1)
    return df_row


def ssc_regular_job(df_row, tb, tb_ost):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    df_row["svwage_pens"] = np.minimum(df_row["m_wage"], tb_ost["rvmaxek"])
    df_row["svwage_health"] = np.minimum(df_row["m_wage"], tb_ost["kvmaxek"])
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    df_row["rvbeit"] = tb["grvbs"] * df_row["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    df_row["avbeit"] = tb["alvbs"] * df_row["svwage_pens"]
    # Health Insurance for Employees (GKV)
    df_row["gkvbeit"] = tb["gkvbs_an"] * df_row["svwage_health"]
    # Care Insurance / Pflegeversicherung
    df_row["pvbeit"] = tb["gpvbs"] * df_row["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    if (~df_row["haskids"] & (df_row["age"] > 22)).all():
        df_row["pvbeit"] = (tb["gpvbs"] + tb["gpvbs_kind"]) * df_row["svwage_health"]
    return df_row


def selfemployed_gkv_ssc(df_row, tb, tb_ost):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (tb["gkvbs_an"] + tb["gkvbs_ag"]) * np.minimum(
        df_row["m_self"], 0.75 * tb_ost["bezgr_"]
    )


def selfemployed_pv_ssc(df_row, tb, tb_ost):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if (~df_row["haskids"] & (df_row["age"] > 22)).all():
        return 2 * tb["gpvbs"] + tb["gpvbs_kind"] * np.minimum(
            df_row["m_self"], 0.75 * tb_ost["bezgr_"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(df_row["m_self"], 0.75 * tb_ost["bezgr_"])


def pv_ssc_pensions(df_row, tb, tb_ost):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if (~df_row["haskids"] & (df_row["age"] > 22)).all():
        return (2 * tb["gpvbs"] + tb["gpvbs_kind"]) * np.minimum(
            df_row["m_pensions"], tb_ost["kvmaxek"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(df_row["m_pensions"], tb_ost["kvmaxek"])


def gkv_ssc_pensions(df_row, tb, tb_ost):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return tb["gkvbs_an"] * np.minimum(df_row["m_pensions"], tb_ost["kvmaxek"])


def calc_midi_contributions(df_row, tb):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""

    df_row["bemessungsentgelt"] = calc_midi_bemessungsentgelt(df_row, tb)

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    df_row["rvbeit"] = calc_midi_old_age_pensions_contr(df_row, tb)

    # Health
    df_row["gkvbeit"] = calc_midi_health_contr(df_row, tb)

    # Unemployment
    df_row["avbeit"] = calc_midi_unemployment_contr(df_row, tb)

    # Long-Term Care
    df_row["pvbeit"] = calc_midi_long_term_care_contr(df_row, tb)

    return df_row


def calc_midi_f(tb):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_an"]
    ag_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_ag"]
    dbsv = an_anteil + ag_anteil
    pauschmini = tb["mini_ag_gkv"] + tb["mini_ag_grv"] + tb["stpag"]
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(df_row, tb):
    f = calc_midi_f(tb)
    return f * tb["mini_grenzew"] + (
        (tb["midi_grenze"] / (tb["midi_grenze"] - tb["mini_grenzew"]))
        - (tb["mini_grenzew"] / (tb["midi_grenze"] - tb["mini_grenzew"]) * f)
    ) * (df_row["m_wage"] - tb["mini_grenzew"])


def calc_midi_old_age_pensions_contr(df_row, tb):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * tb["grvbs"] * df_row["bemessungsentgelt"]
    ag_rvbeit = tb["grvbs"] * df_row["m_wage"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(df_row, tb):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (tb["gkvbs_an"] + tb["gkvbs_ag"]) * df_row["bemessungsentgelt"]
    ag_gkvbeit = tb["gkvbs_ag"] * df_row["m_wage"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(df_row, tb):
    grbetr_alv = 2 * tb["alvbs"] * df_row["bemessungsentgelt"]
    ag_avbeit = tb["alvbs"] * df_row["m_wage"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(df_row, tb):
    grbetr_pv = 2 * tb["gpvbs"] * df_row["bemessungsentgelt"]
    ag_pvbeit = tb["gpvbs"] * df_row["m_wage"]
    if (~df_row["haskids"] & (df_row["age"] > 22)).all():
        return grbetr_pv - ag_pvbeit + tb["gpvbs_kind"] * df_row["bemessungsentgelt"]
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(df_row, tb):
    """Dummy function returning nothing
    """
    df_row.loc[:, OUT_COLS] = 0.0
    return df_row
