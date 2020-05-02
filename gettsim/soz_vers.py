"""This module contains the calculation of the social insurance contribution."""


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

    # As there is only one household, we selcet the wohnort of the household in the
    # beginning.
    wohnort = "ost" if person["wohnort_ost"] else "west"

    # ssc["above_thresh_kv"] =
    # inout["m_wage"] > params["beitr_bemess_grenze"]["ges_krankv"][wohnort]
    #
    # ssc["above_thresh_rv"] =
    # inout["m_wage"] >params["beitr_bemess_grenze"]["rentenv"][wohnort]

    # This is probably the point where Entgeltpunkte should be updated as well.

    # Check if wage is below the mini job grenze.
    belowmini = (
        person["bruttolohn_m"]
        < params["geringfügige_eink_grenzen"]["mini_job"][wohnort]
    )

    # Check if wage is in Gleitzone / Midi-Jobs
    in_gleitzone = (
        params["geringfügige_eink_grenzen"]["midi_job"] >= person["bruttolohn_m"]
    ) & (
        person["bruttolohn_m"]
        >= params["geringfügige_eink_grenzen"]["mini_job"][wohnort]
    )

    # Calculate accordingly the ssc
    if belowmini:
        person[
            [
                "rentenv_beit_m",
                "arbeitsl_v_beit_m",
                "ges_krankv_beit_m",
                "pflegev_beit_m",
            ]
        ] = 0.0
    elif in_gleitzone:
        # TODO: Before and in 2003 params["midi_grenze"] is 0 and
        #  therefore we won't reach this.
        person = params["calc_midi_contrib"](person, params)
    else:
        person = ssc_regular_job(person, params, wohnort)

    # Self-employed may insure via the public health and care insurance.
    if person["selbstständig"] & ~person["prv_krankv_beit_m"]:
        person["ges_krankv_beit_m"] = selfemployed_gkv_ssc(person, params, wohnort)
        person["pflegev_beit_m"] = selfemployed_pv_ssc(person, params, wohnort)

    # Add the health insurance contribution for pensions
    person["ges_krankv_beit_m"] += gkv_ssc_pensions(person, params, wohnort)

    # Add the care insurance contribution for pensions
    person["pflegev_beit_m"] += pv_ssc_pensions(person, params, wohnort)

    # Sum of Social Insurance Contributions (for employees)
    person["sozialv_beit_m"] = person[
        ["rentenv_beit_m", "arbeitsl_v_beit_m", "ges_krankv_beit_m", "pflegev_beit_m"]
    ].sum()
    return person


def ssc_regular_job(person, params, wohnort):
    """Calculates the ssc for a regular job with wage above the midi limit."""
    # Check if the wage is higher than the Beitragsbemessungsgrenze. If so, only the
    # value of this is used.
    person["_lohn_rentenv"] = min(
        person["bruttolohn_m"], params["beitr_bemess_grenze"]["rentenv"][wohnort]
    )
    person["_lohn_krankv"] = min(
        person["bruttolohn_m"], params["beitr_bemess_grenze"]["ges_krankv"][wohnort]
    )
    # Then, calculate employee contributions.
    # Old-Age Pension Insurance / Rentenversicherung
    person["rentenv_beit_m"] = (
        params["soz_vers_beitr"]["rentenv"] * person["_lohn_rentenv"]
    )
    # Unemployment Insurance / Arbeitslosenversicherung
    person["arbeitsl_v_beit_m"] = (
        params["soz_vers_beitr"]["arbeitsl_v"] * person["_lohn_rentenv"]
    )
    # Health Insurance for Employees (GKV)
    person["ges_krankv_beit_m"] = (
        params["soz_vers_beitr"]["ges_krankv"]["an"] * person["_lohn_krankv"]
    )
    # Care Insurance / Pflegeversicherung
    person["pflegev_beit_m"] = (
        params["soz_vers_beitr"]["pflegev"]["standard"] * person["_lohn_krankv"]
    )
    # If you are above 23 and without kids, you have to pay a higher rate
    if ~person["hat_kinder"] & (person["alter"] > 22):
        person["pflegev_beit_m"] = (
            params["soz_vers_beitr"]["pflegev"]["standard"]
            + params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
        ) * person["_lohn_krankv"]
    return person


def selfemployed_gkv_ssc(person, params, wohnort):
    """Calculates health insurance contributions. Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'"""
    return (
        params["soz_vers_beitr"]["ges_krankv"]["an"]
        + params["soz_vers_beitr"]["ges_krankv"]["ag"]
    ) * min(person["eink_selbstst_m"], 0.75 * params["bezugsgröße"][wohnort])


def selfemployed_pv_ssc(person, params, wohnort):
    """Calculates care insurance contributions. Self-employed pay the full
        contribution (employer + employee), which is either assessed on their
        self-employement income or 3/4 of the 'Bezugsgröße'"""
    if ~person["hat_kinder"] & (person["alter"] > 22):
        return 2 * params["soz_vers_beitr"]["pflegev"]["standard"] + params[
            "soz_vers_beitr"
        ]["pflegev"]["zusatz_kinderlos"] * min(
            person["eink_selbstst_m"], 0.75 * params["bezugsgröße"][wohnort]
        )
    else:
        return (
            2
            * params["soz_vers_beitr"]["pflegev"]["standard"]
            * min(person["eink_selbstst_m"], 0.75 * params["bezugsgröße"][wohnort])
        )


def pv_ssc_pensions(person, params, wohnort):
    """Calculates the care insurance contributions for pensions. It is twice the
    standard rate"""
    if ~person["hat_kinder"] & (person["alter"] > 22):
        return (
            2 * params["soz_vers_beitr"]["pflegev"]["standard"]
            + params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
        ) * min(
            person["ges_rente_m"], params["beitr_bemess_grenze"]["ges_krankv"][wohnort]
        )
    else:
        return (
            2
            * params["soz_vers_beitr"]["pflegev"]["standard"]
            * min(
                person["ges_rente_m"],
                params["beitr_bemess_grenze"]["ges_krankv"][wohnort],
            )
        )


def gkv_ssc_pensions(person, params, wohnort):
    """Calculates the health insurance contributions for pensions. It is the normal
    rate"""
    return params["soz_vers_beitr"]["ges_krankv"]["an"] * min(
        person["ges_rente_m"], params["beitr_bemess_grenze"]["ges_krankv"][wohnort]
    )


def calc_midi_contributions(person, params):
    """Calculates the ssc for midi jobs. For these jobs, the rate is not calculated
    on the wage, but on the 'bemessungsentgelt'. Contributions are usually shared
    equally by employee (AN) and employer (AG). We are actually not interested in
    employer's contributions, but we need them here as an intermediate step"""

    person["_bemessungsentgelt"] = calc_midi_bemessungsentgelt(person, params)

    # Again, all branches of social insurance
    # First total amount, then employer, then employee

    # Old-Age Pensions
    person["rentenv_beit_m"] = calc_midi_old_age_pensions_contr(person, params)

    # Health
    person["ges_krankv_beit_m"] = calc_midi_health_contr(person, params)

    # Unemployment
    person["arbeitsl_v_beit_m"] = calc_midi_unemployment_contr(person, params)

    # Long-Term Care
    person["pflegev_beit_m"] = calc_midi_long_term_care_contr(person, params)

    return person


def calc_midi_f(params):
    """
    This calculates the factor F from the formula in § 163 (10) SGB VI.
    """

    an_anteil = (
        params["soz_vers_beitr"]["rentenv"]
        + params["soz_vers_beitr"]["pflegev"]["standard"]
        + params["soz_vers_beitr"]["arbeitsl_v"]
        + params["soz_vers_beitr"]["ges_krankv"]["an"]
    )
    ag_anteil = (
        params["soz_vers_beitr"]["rentenv"]
        + params["soz_vers_beitr"]["pflegev"]["standard"]
        + params["soz_vers_beitr"]["arbeitsl_v"]
        + params["soz_vers_beitr"]["ges_krankv"]["ag"]
    )
    dbsv = an_anteil + ag_anteil
    pauschmini = (
        params["ag_abgaben_geringf"]["ges_krankenv"]
        + params["ag_abgaben_geringf"]["rentenv"]
        + params["ag_abgaben_geringf"]["st"]
    )
    f = round(pauschmini / dbsv, 4)
    return f


def calc_midi_bemessungsentgelt(person, params):
    f = calc_midi_f(params)
    return f * params["geringfügige_eink_grenzen"]["mini_job"]["west"] + (
        (
            params["geringfügige_eink_grenzen"]["midi_job"]
            / (
                params["geringfügige_eink_grenzen"]["midi_job"]
                - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
            )
        )
        - (
            params["geringfügige_eink_grenzen"]["mini_job"]["west"]
            / (
                params["geringfügige_eink_grenzen"]["midi_job"]
                - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
            )
            * f
        )
    ) * (
        person["bruttolohn_m"] - params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )


def calc_midi_old_age_pensions_contr(person, params):
    """ Calculate old age pensions social insurance contribution for midi job."""
    grbetr_rv = 2 * params["soz_vers_beitr"]["rentenv"] * person["_bemessungsentgelt"]
    ag_rvbeit = params["soz_vers_beitr"]["rentenv"] * person["bruttolohn_m"]
    return grbetr_rv - ag_rvbeit


def calc_midi_health_contr(person, params):
    """ Calculate social insurance health contributions for midi job."""
    grbetr_gkv = (
        params["soz_vers_beitr"]["ges_krankv"]["an"]
        + params["soz_vers_beitr"]["ges_krankv"]["ag"]
    ) * person["_bemessungsentgelt"]
    ag_gkvbeit = params["soz_vers_beitr"]["ges_krankv"]["ag"] * person["bruttolohn_m"]
    return grbetr_gkv - ag_gkvbeit


def calc_midi_unemployment_contr(person, params):
    grbetr_alv = (
        2 * params["soz_vers_beitr"]["arbeitsl_v"] * person["_bemessungsentgelt"]
    )
    ag_avbeit = params["soz_vers_beitr"]["arbeitsl_v"] * person["bruttolohn_m"]
    return grbetr_alv - ag_avbeit


def calc_midi_long_term_care_contr(person, params):
    grbetr_pv = (
        2
        * params["soz_vers_beitr"]["pflegev"]["standard"]
        * person["_bemessungsentgelt"]
    )
    ag_pvbeit = params["soz_vers_beitr"]["pflegev"]["standard"] * person["bruttolohn_m"]
    if ~person["hat_kinder"] & (person["alter"] > 22):
        return (
            grbetr_pv
            - ag_pvbeit
            + params["soz_vers_beitr"]["pflegev"]["zusatz_kinderlos"]
            * person["_bemessungsentgelt"]
        )
    else:
        return grbetr_pv - ag_pvbeit


def no_midi(person, params):
    """Dummy function returning 0 for the single contributions
    """
    for col in [
        "rentenv_beit_m",
        "arbeitsl_v_beit_m",
        "ges_krankv_beit_m",
        "pflegev_beit_m",
    ]:
        person[col] = 0.0
    return person
