import numpy as np

OUT_COLS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


def soc_ins_contrib(person, tb):
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
    westost = "o" if person["east"].iloc[0] else "w"
    tb_ost = {}
    for val in ["bezgr_", "mini_grenze", "kvmaxek", "rvmaxek"]:
        tb_ost[val] = tb[val + westost]

    # ssc["above_thresh_kv"] = inout["m_wage"] > tb_ost["kvmaxek"]
    #
    # ssc["above_thresh_rv"] = inout["m_wage"] > tb_ost["rvmaxek"]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = person["m_wage"] < tb_ost["mini_grenze"]

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = (tb["midi_grenze"] >= person["m_wage"]) & (
        person["m_wage"] >= tb_ost["mini_grenze"]
    )

    # Calculate accordingly the ssc
    if belowmini.iloc[0]:
        person.loc[:, OUT_COLS] = 0.0
    elif in_gleitzone.iloc[0]:
        # TODO: Before and in 2003 tb["midi_grenze"] is 0 and therefore we won't reach
        #  this.
        person = tb["calc_midi_contrib"](person, tb)
    else:
        person = ssc_regular_job(person, tb, tb_ost)

    # Self-employed may insure via the public health and care insurance.
    if (person["selfemployed"] & ~person["pkv"]).iloc[0]:
        person["gkvbeit"] = selfemployed_gkv_ssc(person, tb, tb_ost)
        person["pvbeit"] = selfemployed_pv_ssc(person, tb, tb_ost)

    # Add the health insurance contribution for pensions
    person["gkvbeit"] += gkv_ssc_pensions(person, tb, tb_ost)

    # Add the care insurance contribution for pensions
    person["pvbeit"] += pv_ssc_pensions(person, tb, tb_ost)

    # Sum of Social Insurance Contributions (for employees)
    person["svbeit"] = person[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum(axis=1)
    return person


def ssc_regular_job(person, tb, tb_ost):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    person["svwage_pens"] = np.minimum(person["m_wage"], tb_ost["rvmaxek"])
    person["svwage_health"] = np.minimum(person["m_wage"], tb_ost["kvmaxek"])
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    person["rvbeit"] = tb["grvbs"] * person["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    person["avbeit"] = tb["alvbs"] * person["svwage_pens"]
    # Health Insurance for Employees (GKV)
    person["gkvbeit"] = tb["gkvbs_an"] * person["svwage_health"]
    # Care Insurance / Pflegeversicherung
    person["pvbeit"] = tb["gpvbs"] * person["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    if (~person["haskids"] & (person["age"] > 22)).iloc[0]:
        person["pvbeit"] = (tb["gpvbs"] + tb["gpvbs_kind"]) * person["svwage_health"]
    return person


def selfemployed_gkv_ssc(person, tb, tb_ost):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (tb["gkvbs_an"] + tb["gkvbs_ag"]) * np.minimum(
        person["m_self"], 0.75 * tb_ost["bezgr_"]
    )


def selfemployed_pv_ssc(person, tb, tb_ost):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if (~person["haskids"] & (person["age"] > 22)).iloc[0]:
        return 2 * tb["gpvbs"] + tb["gpvbs_kind"] * np.minimum(
            person["m_self"], 0.75 * tb_ost["bezgr_"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(person["m_self"], 0.75 * tb_ost["bezgr_"])


def pv_ssc_pensions(person, tb, tb_ost):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if (~person["haskids"] & (person["age"] > 22)).iloc[0]:
        return (2 * tb["gpvbs"] + tb["gpvbs_kind"]) * np.minimum(
            person["m_pensions"], tb_ost["kvmaxek"]
        )
    else:
        return 2 * tb["gpvbs"] * np.minimum(person["m_pensions"], tb_ost["kvmaxek"])


def gkv_ssc_pensions(person, tb, tb_ost):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return tb["gkvbs_an"] * np.minimum(person["m_pensions"], tb_ost["kvmaxek"])


def calc_midi_contributions(person, tb):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""

    person["bemessungsentgelt"] = calc_midi_bemessungsentgelt(person, tb)

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    person["rvbeit"] = calc_midi_old_age_pensions_contr(person, tb)

    # Health
    person["gkvbeit"] = calc_midi_health_contr(person, tb)

    # Unemployment
    person["avbeit"] = calc_midi_unemployment_contr(person, tb)

    # Long-Term Care
    person["pvbeit"] = calc_midi_long_term_care_contr(person, tb)

    return person


def calc_midi_f(tb):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_an"]
    ag_anteil = tb["grvbs"] + tb["gpvbs"] + tb["alvbs"] + tb["gkvbs_ag"]
    dbsv = an_anteil + ag_anteil
    pauschmini = tb["mini_ag_gkv"] + tb["mini_ag_grv"] + tb["stpag"]
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(person, tb):
    f = calc_midi_f(tb)
    return f * tb["mini_grenzew"] + (
        (tb["midi_grenze"] / (tb["midi_grenze"] - tb["mini_grenzew"]))
        - (tb["mini_grenzew"] / (tb["midi_grenze"] - tb["mini_grenzew"]) * f)
    ) * (person["m_wage"] - tb["mini_grenzew"])


def calc_midi_old_age_pensions_contr(person, tb):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * tb["grvbs"] * person["bemessungsentgelt"]
    ag_rvbeit = tb["grvbs"] * person["m_wage"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(person, tb):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (tb["gkvbs_an"] + tb["gkvbs_ag"]) * person["bemessungsentgelt"]
    ag_gkvbeit = tb["gkvbs_ag"] * person["m_wage"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(person, tb):
    grbetr_alv = 2 * tb["alvbs"] * person["bemessungsentgelt"]
    ag_avbeit = tb["alvbs"] * person["m_wage"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(person, tb):
    grbetr_pv = 2 * tb["gpvbs"] * person["bemessungsentgelt"]
    ag_pvbeit = tb["gpvbs"] * person["m_wage"]
    if (~person["haskids"] & (person["age"] > 22)).iloc[0]:
        return grbetr_pv - ag_pvbeit + tb["gpvbs_kind"] * person["bemessungsentgelt"]
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(person, tb):
    """Dummy function returning nothing
    """
    person.loc[:, OUT_COLS] = 0.0
    return person
