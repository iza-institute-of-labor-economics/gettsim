from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def mini_job_grenze(wohnort_ost: BoolSeries, soz_vers_beitr_params: dict):
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
    out = wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["ost"],
            False: soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"][
                "west"
            ],
        }
    )

    return out.astype(float)


def geringfügig_beschäftigt(
    bruttolohn_m: FloatSeries, mini_job_grenze: FloatSeries
) -> BoolSeries:
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
    BoolSeries indicating if person earns less than marginal employment threshold.
    """
    return bruttolohn_m <= mini_job_grenze


def in_gleitzone(
    bruttolohn_m: FloatSeries,
    geringfügig_beschäftigt: BoolSeries,
    soz_vers_beitr_params: dict,
) -> BoolSeries:
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
    BoolSeries indicating individual's income is in midi-job range.
    """
    return (
        bruttolohn_m <= soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
    ) & (~geringfügig_beschäftigt)


def midi_job_bemessungsentgelt(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Select income subject to social insurance contributions for midi job.

    Bemmessungsgeld (Gleitzonenentgelt) is the reference income for midi jobs subject
    to social insurance contribution.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------
    FloatSeries with the income subject to social insurance contributions for midi job.
    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_soz_vers_beitr = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
        + soz_vers_beitr_params["soz_vers_beitr"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = (
        allg_soz_vers_beitr
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
    )
    ag_anteil = (
        allg_soz_vers_beitr
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )

    # Sum over the shares which are specific for midi jobs.
    pausch_mini = (
        soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["st"]
    )
    # Now calculate final factor
    f = round(pausch_mini / (an_anteil + ag_anteil), 4)

    # Now use the factor to calculate the overall bemessungsentgelt
    mini_job_anteil = (
        f * soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )
    lohn_über_mini = (
        bruttolohn_m.loc[in_gleitzone]
        - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
    )
    gewichtete_midi_job_rate = (
        soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
    ) - (
        soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
            - soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]
        )
        * f
    )
    return mini_job_anteil + lohn_über_mini * gewichtete_midi_job_rate


def reg_beschäftigt(
    bruttolohn_m: FloatSeries, soz_vers_beitr_params: dict
) -> BoolSeries:
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
    BoolSeries indicating regular employed persons.
    """
    return (
        bruttolohn_m >= soz_vers_beitr_params["geringfügige_eink_grenzen"]["midi_job"]
    )
