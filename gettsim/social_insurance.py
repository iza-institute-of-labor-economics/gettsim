OUT_COLS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


def soc_ins_contrib(person, params):
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
    # beginning and place them in a seperate dictionary params_ost.
    westost = "o" if person["east"] else "w"
    params_ost = {}
    for val in ["bezgr_", "mini_grenze", "kvmaxek", "rvmaxek"]:
        params_ost[val] = params[val + westost]

    # ssc["above_thresh_kv"] = inout["m_wage"] > params_ost["kvmaxek"]
    #
    # ssc["above_thresh_rv"] = inout["m_wage"] > params_ost["rvmaxek"]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = person["m_wage"] < params_ost["mini_grenze"]

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = (params["midi_grenze"] >= person["m_wage"]) & (
        person["m_wage"] >= params_ost["mini_grenze"]
    )

    # Calculate accordingly the ssc
    if belowmini:
        person[OUT_COLS] = 0.0
    elif in_gleitzone:
        # TODO: Before and in 2003 params["midi_grenze"] is 0 and
        #  therefore we won't reach this.
        person = params["calc_midi_contrib"](person, params)
    else:
        person = ssc_regular_job(person, params, params_ost)

    # Self-employed may insure via the public health and care insurance.
    if person["selfemployed"] & ~person["pkv"]:
        person["gkvbeit"] = selfemployed_gkv_ssc(person, params, params_ost)
        person["pvbeit"] = selfemployed_pv_ssc(person, params, params_ost)

    # Add the health insurance contribution for pensions
    person["gkvbeit"] += gkv_ssc_pensions(person, params, params_ost)

    # Add the care insurance contribution for pensions
    person["pvbeit"] += pv_ssc_pensions(person, params, params_ost)

    # Sum of Social Insurance Contributions (for employees)
    person["svbeit"] = person[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum()
    return person


def ssc_regular_job(person, params, params_ost):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    person["svwage_pens"] = min(person["m_wage"], params_ost["rvmaxek"])
    person["svwage_health"] = min(person["m_wage"], params_ost["kvmaxek"])
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    person["rvbeit"] = params["grvbs"] * person["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    person["avbeit"] = params["alvbs"] * person["svwage_pens"]
    # Health Insurance for Employees (GKV)
    person["gkvbeit"] = params["gkvbs_an"] * person["svwage_health"]
    # Care Insurance / Pflegeversicherung
    person["pvbeit"] = params["gpvbs"] * person["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    if ~person["haskids"] & (person["age"] > 22):
        person["pvbeit"] = (params["gpvbs"] + params["gpvbs_kind"]) * person[
            "svwage_health"
        ]
    return person


def selfemployed_gkv_ssc(person, params, params_ost):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (params["gkvbs_an"] + params["gkvbs_ag"]) * min(
        person["m_self"], 0.75 * params_ost["bezgr_"]
    )


def selfemployed_pv_ssc(person, params, params_ost):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if ~person["haskids"] & (person["age"] > 22):
        return 2 * params["gpvbs"] + params["gpvbs_kind"] * min(
            person["m_self"], 0.75 * params_ost["bezgr_"]
        )
    else:
        return 2 * params["gpvbs"] * min(person["m_self"], 0.75 * params_ost["bezgr_"])


def pv_ssc_pensions(person, params, params_ost):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if ~person["haskids"] & (person["age"] > 22):
        return (2 * params["gpvbs"] + params["gpvbs_kind"]) * min(
            person["m_pensions"], params_ost["kvmaxek"]
        )
    else:
        return 2 * params["gpvbs"] * min(person["m_pensions"], params_ost["kvmaxek"])


def gkv_ssc_pensions(person, params, params_ost):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return params["gkvbs_an"] * min(person["m_pensions"], params_ost["kvmaxek"])


def calc_midi_contributions(person, params):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""

    person["bemessungsentgelt"] = calc_midi_bemessungsentgelt(person, params)

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    person["rvbeit"] = calc_midi_old_age_pensions_contr(person, params)

    # Health
    person["gkvbeit"] = calc_midi_health_contr(person, params)

    # Unemployment
    person["avbeit"] = calc_midi_unemployment_contr(person, params)

    # Long-Term Care
    person["pvbeit"] = calc_midi_long_term_care_contr(person, params)

    return person


def calc_midi_f(params):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = params["grvbs"] + params["gpvbs"] + params["alvbs"] + params["gkvbs_an"]
    ag_anteil = params["grvbs"] + params["gpvbs"] + params["alvbs"] + params["gkvbs_ag"]
    dbsv = an_anteil + ag_anteil
    pauschmini = params["mini_ag_gkv"] + params["mini_ag_grv"] + params["stpag"]
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(person, params):
    f = calc_midi_f(params)
    return f * params["mini_grenzew"] + (
        (params["midi_grenze"] / (params["midi_grenze"] - params["mini_grenzew"]))
        - (
            params["mini_grenzew"]
            / (params["midi_grenze"] - params["mini_grenzew"])
            * f
        )
    ) * (person["m_wage"] - params["mini_grenzew"])


def calc_midi_old_age_pensions_contr(person, params):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * params["grvbs"] * person["bemessungsentgelt"]
    ag_rvbeit = params["grvbs"] * person["m_wage"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(person, params):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (params["gkvbs_an"] + params["gkvbs_ag"]) * person["bemessungsentgelt"]
    ag_gkvbeit = params["gkvbs_ag"] * person["m_wage"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(person, params):
    grbetr_alv = 2 * params["alvbs"] * person["bemessungsentgelt"]
    ag_avbeit = params["alvbs"] * person["m_wage"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(person, params):
    grbetr_pv = 2 * params["gpvbs"] * person["bemessungsentgelt"]
    ag_pvbeit = params["gpvbs"] * person["m_wage"]
    if ~person["haskids"] & (person["age"] > 22):
        return (
            grbetr_pv - ag_pvbeit + params["gpvbs_kind"] * person["bemessungsentgelt"]
        )
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(person, params):
    """Dummy function returning 0 for the single contributions
    """
    for col in OUT_COLS:
        person[col] = 0.0
    return person
