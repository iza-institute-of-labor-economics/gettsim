from gettsim.shared import add_rounding_spec


def mini_job_grenze(wohnort_ost: bool, soz_vers_beitr_params: dict) -> float:
    """Select the income threshold depending on place of living

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------

    """
    params = soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]
    out = params["ost"] if wohnort_ost else params["west"]
    return float(out)


def geringfügig_beschäftigt(bruttolohn_m: float, mini_job_grenze: float) -> bool:
    """Check if individual earns less than marginal employment threshold.

    Marginal employed pay no social insurance contributions.

    Legal reference: § 8 Abs. 1 Satz 1 and 2 SGB IV

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    mini_job_grenze
        See :func:`mini_job_grenze`.


    Returns
    -------
    Whether person earns less than marginal employment threshold.
    """
    return bruttolohn_m <= mini_job_grenze


def in_gleitzone(
    bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    soz_vers_beitr_params: dict,
) -> bool:
    """Check if individual's income is in midi-job range.

    Employed people with their wage in the range of gleitzone pay reduced social
    insurance contributions.

    Legal reference: § 20 Abs. 2 SGB IV

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Whether individual's income is in midi-job range.
    """
    out = (
        bruttolohn_m <= soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
    ) and (not geringfügig_beschäftigt)
    return out


@add_rounding_spec(params_key="soz_vers_beitr")
def midi_job_faktor_f(
    soz_vers_beitr_params: dict,
) -> float:
    """Faktor F which is needed for the calculation of Bemessungsentgelt
    (beitragspflichtige Einnahme) of midi jobs. It is calculated as the ratio of 30 %
    divided by the total social security contribution rate
    (Gesamtsozialversicherungsbeitragssatz).

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midi job.
    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_soz_vers_beitr = (
        soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
        + soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        + soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = (
        allg_soz_vers_beitr + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["an"]
    )
    ag_anteil = (
        allg_soz_vers_beitr + soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ag"]
    )

    # Sum over the shares which are specific for midi jobs.
    pausch_mini = (
        soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["st"]
    )

    # Now calculate final factor
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


def midi_job_bemessungsentgelt_m(
    midi_job_faktor_f: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
) -> float:
    """Income subject to social insurance contributions for midi job.

    Bemmessungsgeld (Gleitzonenentgelt) is the reference income for midi jobs subject
    to social insurance contribution.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    midi_job_faktor_f
        See basic input variable :ref:`midi_job_faktor_f <midi_job_faktor_f>`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midi job.
    """
    # Now use the factor to calculate the overall bemessungsentgelt
    mini_job_anteil = (
        midi_job_faktor_f
        * soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]
    )

    lohn_über_mini = (
        bruttolohn_m
        - soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]
    )
    gewichtete_midi_job_rate = (
        soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]
        )
    ) - (
        soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]
        )
        * midi_job_faktor_f
    )
    return mini_job_anteil + lohn_über_mini * gewichtete_midi_job_rate


def regulär_beschäftigt(bruttolohn_m: float, soz_vers_beitr_params: dict) -> bool:
    """Check if person is in regular employment.

    Employees earning more than the midi job threshold, are subject to all ordinary
    income and social insurance contribution regulations. In gettsim we call these
    regular employed.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Whether regular employed persons.
    """
    out = (
        bruttolohn_m >= soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
    )
    return out
