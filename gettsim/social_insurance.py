import numpy as np

OUT_COLS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


def soc_ins_contrib(person, soz_vers_beitr_params):
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
    # beginning and place them in a seperate dictionary soz_vers_beitr_params_ost.
    westost = "o" if person["east"] else "w"
    soz_vers_beitr_params_ost = {}
    for val in ["bezgr_", "mini_grenze", "kvmaxek", "rvmaxek"]:
        soz_vers_beitr_params_ost[val] = soz_vers_beitr_params[val + westost]

    # ssc["above_thresh_kv"] = inout["m_wage"] > soz_vers_beitr_params_ost["kvmaxek"]
    #
    # ssc["above_thresh_rv"] = inout["m_wage"] > soz_vers_beitr_params_ost["rvmaxek"]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = person["m_wage"] < soz_vers_beitr_params_ost["mini_grenze"]

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = (soz_vers_beitr_params["midi_grenze"] >= person["m_wage"]) & (
        person["m_wage"] >= soz_vers_beitr_params_ost["mini_grenze"]
    )

    # Calculate accordingly the ssc
    if belowmini:
        person[OUT_COLS] = 0.0
    elif in_gleitzone:
        # TODO: Before and in 2003 soz_vers_beitr_params["midi_grenze"] is 0 and
        #  therefore we won't reach this.
        person = soz_vers_beitr_params["calc_midi_contrib"](
            person, soz_vers_beitr_params
        )
    else:
        person = ssc_regular_job(
            person, soz_vers_beitr_params, soz_vers_beitr_params_ost
        )

    # Self-employed may insure via the public health and care insurance.
    if person["selfemployed"] & ~person["pkv"]:
        person["gkvbeit"] = selfemployed_gkv_ssc(
            person, soz_vers_beitr_params, soz_vers_beitr_params_ost
        )
        person["pvbeit"] = selfemployed_pv_ssc(
            person, soz_vers_beitr_params, soz_vers_beitr_params_ost
        )

    # Add the health insurance contribution for pensions
    person["gkvbeit"] += gkv_ssc_pensions(
        person, soz_vers_beitr_params, soz_vers_beitr_params_ost
    )

    # Add the care insurance contribution for pensions
    person["pvbeit"] += pv_ssc_pensions(
        person, soz_vers_beitr_params, soz_vers_beitr_params_ost
    )

    # Sum of Social Insurance Contributions (for employees)
    person["svbeit"] = person[["rvbeit", "avbeit", "gkvbeit", "pvbeit"]].sum()
    return person


def ssc_regular_job(person, soz_vers_beitr_params, soz_vers_beitr_params_ost):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    person["svwage_pens"] = np.minimum(
        person["m_wage"], soz_vers_beitr_params_ost["rvmaxek"]
    )
    person["svwage_health"] = np.minimum(
        person["m_wage"], soz_vers_beitr_params_ost["kvmaxek"]
    )
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    person["rvbeit"] = soz_vers_beitr_params["grvbs"] * person["svwage_pens"]
    # Unemployment Insurance / Arbeitslosenversicherung
    person["avbeit"] = soz_vers_beitr_params["alvbs"] * person["svwage_pens"]
    # Health Insurance for Employees (GKV)
    person["gkvbeit"] = soz_vers_beitr_params["gkvbs_an"] * person["svwage_health"]
    # Care Insurance / Pflegeversicherung
    person["pvbeit"] = soz_vers_beitr_params["gpvbs"] * person["svwage_health"]
    # If you are above 23 and without kids, you have to pay a higher rate
    if ~person["haskids"] & (person["age"] > 22):
        person["pvbeit"] = (
            soz_vers_beitr_params["gpvbs"] + soz_vers_beitr_params["gpvbs_kind"]
        ) * person["svwage_health"]
    return person


def selfemployed_gkv_ssc(person, soz_vers_beitr_params, soz_vers_beitr_params_ost):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (
        soz_vers_beitr_params["gkvbs_an"] + soz_vers_beitr_params["gkvbs_ag"]
    ) * np.minimum(person["m_self"], 0.75 * soz_vers_beitr_params_ost["bezgr_"])


def selfemployed_pv_ssc(person, soz_vers_beitr_params, soz_vers_beitr_params_ost):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if ~person["haskids"] & (person["age"] > 22):
        return 2 * soz_vers_beitr_params["gpvbs"] + soz_vers_beitr_params[
            "gpvbs_kind"
        ] * np.minimum(person["m_self"], 0.75 * soz_vers_beitr_params_ost["bezgr_"])
    else:
        return (
            2
            * soz_vers_beitr_params["gpvbs"]
            * np.minimum(person["m_self"], 0.75 * soz_vers_beitr_params_ost["bezgr_"])
        )


def pv_ssc_pensions(person, soz_vers_beitr_params, soz_vers_beitr_params_ost):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if ~person["haskids"] & (person["age"] > 22):
        return (
            2 * soz_vers_beitr_params["gpvbs"] + soz_vers_beitr_params["gpvbs_kind"]
        ) * np.minimum(person["m_pensions"], soz_vers_beitr_params_ost["kvmaxek"])
    else:
        return (
            2
            * soz_vers_beitr_params["gpvbs"]
            * np.minimum(person["m_pensions"], soz_vers_beitr_params_ost["kvmaxek"])
        )


def gkv_ssc_pensions(person, soz_vers_beitr_params, soz_vers_beitr_params_ost):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return soz_vers_beitr_params["gkvbs_an"] * np.minimum(
        person["m_pensions"], soz_vers_beitr_params_ost["kvmaxek"]
    )


def calc_midi_contributions(person, soz_vers_beitr_params):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""

    person["bemessungsentgelt"] = calc_midi_bemessungsentgelt(
        person, soz_vers_beitr_params
    )

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    person["rvbeit"] = calc_midi_old_age_pensions_contr(person, soz_vers_beitr_params)

    # Health
    person["gkvbeit"] = calc_midi_health_contr(person, soz_vers_beitr_params)

    # Unemployment
    person["avbeit"] = calc_midi_unemployment_contr(person, soz_vers_beitr_params)

    # Long-Term Care
    person["pvbeit"] = calc_midi_long_term_care_contr(person, soz_vers_beitr_params)

    return person


def calc_midi_f(soz_vers_beitr_params):
    """ I have no idea what this function calculates. What means f?"""
    an_anteil = (
        soz_vers_beitr_params["grvbs"]
        + soz_vers_beitr_params["gpvbs"]
        + soz_vers_beitr_params["alvbs"]
        + soz_vers_beitr_params["gkvbs_an"]
    )
    ag_anteil = (
        soz_vers_beitr_params["grvbs"]
        + soz_vers_beitr_params["gpvbs"]
        + soz_vers_beitr_params["alvbs"]
        + soz_vers_beitr_params["gkvbs_ag"]
    )
    dbsv = an_anteil + ag_anteil
    pauschmini = (
        soz_vers_beitr_params["mini_ag_gkv"]
        + soz_vers_beitr_params["mini_ag_grv"]
        + soz_vers_beitr_params["stpag"]
    )
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(person, soz_vers_beitr_params):
    f = calc_midi_f(soz_vers_beitr_params)
    return f * soz_vers_beitr_params["mini_grenzew"] + (
        (
            soz_vers_beitr_params["midi_grenze"]
            / (
                soz_vers_beitr_params["midi_grenze"]
                - soz_vers_beitr_params["mini_grenzew"]
            )
        )
        - (
            soz_vers_beitr_params["mini_grenzew"]
            / (
                soz_vers_beitr_params["midi_grenze"]
                - soz_vers_beitr_params["mini_grenzew"]
            )
            * f
        )
    ) * (person["m_wage"] - soz_vers_beitr_params["mini_grenzew"])


def calc_midi_old_age_pensions_contr(person, soz_vers_beitr_params):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * soz_vers_beitr_params["grvbs"] * person["bemessungsentgelt"]
    ag_rvbeit = soz_vers_beitr_params["grvbs"] * person["m_wage"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(person, soz_vers_beitr_params):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (
        soz_vers_beitr_params["gkvbs_an"] + soz_vers_beitr_params["gkvbs_ag"]
    ) * person["bemessungsentgelt"]
    ag_gkvbeit = soz_vers_beitr_params["gkvbs_ag"] * person["m_wage"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(person, soz_vers_beitr_params):
    grbetr_alv = 2 * soz_vers_beitr_params["alvbs"] * person["bemessungsentgelt"]
    ag_avbeit = soz_vers_beitr_params["alvbs"] * person["m_wage"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(person, soz_vers_beitr_params):
    grbetr_pv = 2 * soz_vers_beitr_params["gpvbs"] * person["bemessungsentgelt"]
    ag_pvbeit = soz_vers_beitr_params["gpvbs"] * person["m_wage"]
    if ~person["haskids"] & (person["age"] > 22):
        return (
            grbetr_pv
            - ag_pvbeit
            + soz_vers_beitr_params["gpvbs_kind"] * person["bemessungsentgelt"]
        )
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(person, soz_vers_beitr_params):
    """Dummy function returning nothing
    """
    person[OUT_COLS] = 0.0
    return person
