from gettsim.shared import add_rounding_spec


def mini_job_grenze(
    wohnort_ost: bool, geringfügigkeitsgrenze_west: int, geringfügigkeitsgrenze_ost: int
) -> float:
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
    out = geringfügigkeitsgrenze_ost if wohnort_ost else geringfügigkeitsgrenze_west
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
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
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
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

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
    an_anteil = allg_soz_vers_beitr + ges_krankenv_beitr_satz
    ag_anteil = allg_soz_vers_beitr + _ges_krankenv_beitr_satz_arbeitg

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
    geringfügigkeitsgrenze_west: int,
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
    mini_job_anteil = midi_job_faktor_f * geringfügigkeitsgrenze_west
    lohn_über_mini = bruttolohn_m - geringfügigkeitsgrenze_west
    gewichtete_midi_job_rate = (
        soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
            - geringfügigkeitsgrenze_west
        )
    ) - (
        geringfügigkeitsgrenze_west
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midi_job"]
            - geringfügigkeitsgrenze_west
        )
        * midi_job_faktor_f
    )

    return mini_job_anteil + lohn_über_mini * gewichtete_midi_job_rate


def geringfügigkeitsgrenze_west_vor_2022(soz_vers_beitr_params: dict) -> int:
    return soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["west"]


def geringfügigkeitsgrenze_ost_vor_2022(soz_vers_beitr_params: dict) -> int:
    return soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["mini_job"]["ost"]


def geringfügigkeitsgrenze_ab_2022(soz_vers_beitr_params: dict) -> int:
    """Since 10/2022, the mini job threshold is calculated
    from the statutory minimum wage"""

    return round(
        soz_vers_beitr_params["mindestlohn"]
        * soz_vers_beitr_params["geringf_eink_faktor"]
        / soz_vers_beitr_params["geringf_eink_divisor"]
    )


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
