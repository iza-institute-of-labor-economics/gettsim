from _gettsim.shared import add_rounding_spec, dates_active


@dates_active(
    end="2022-09-30",
)
def minijob_grenze_west(sozialv_beitr_params: dict) -> float:
    """Obtains marginal job thresholds for West Germany until September 2022.

    Parameters
    ----------
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["west"]


@dates_active(
    end="2022-09-30",
)
def minijob_grenze_ost(sozialv_beitr_params: dict) -> float:
    """Obtains marginal job thresholds for East Germany until September 2022.

    Parameters
    ----------
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["ost"]


@dates_active(end="2022-09-30", change_name="minijob_grenze")
@add_rounding_spec(params_key="sozialv_beitr")
def minijob_grenze_unterschied_ost_west(
    wohnort_ost: bool, minijob_grenze_west: float, minijob_grenze_ost: float
) -> float:
    """Select the income threshold depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------

    """
    out = minijob_grenze_ost if wohnort_ost else minijob_grenze_west
    return float(out)


@add_rounding_spec(params_key="sozialv_beitr")
@dates_active(start="2022-10-01")
def minijob_grenze(sozialv_beitr_params: dict) -> float:
    """Obtains marginal job threshold since 10/2022. Since then, it is calculated from
    the statutory minimum wage.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return (
        sozialv_beitr_params["mindestlohn"]
        * sozialv_beitr_params["geringf_eink_faktor"]
        / sozialv_beitr_params["geringf_eink_divisor"]
    )


def geringfügig_beschäftigt(bruttolohn_m: float, minijob_grenze: float) -> bool:
    """Check if individual earns less than marginal employment threshold.

    Marginal employed pay no social insurance contributions.

    Legal reference: § 8 Abs. 1 Satz 1 and 2 SGB IV

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    minijob_grenze
        See :func:`minijob_grenze`.


    Returns
    -------
    Whether person earns less than marginal employment threshold.

    """
    return bruttolohn_m <= minijob_grenze


def in_gleitzone(
    bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    sozialv_beitr_params: dict,
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
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether individual's income is in midi-job range.

    """
    out = (
        bruttolohn_m <= sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    ) and (not geringfügig_beschäftigt)
    return out


@dates_active(
    end="2022-09-30",
    change_name="midijob_faktor_f",
)
@add_rounding_spec(params_key="sozialv_beitr")
def midijob_faktor_f_mit_minijob_st(
    sozialv_beitr_params: dict,
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Faktor F which is needed for the calculation of Bemessungsentgelt
    (beitragspflichtige Einnahme) of midijobs before October 2022. It is calculated as
    the ratio of the sum of lump-sum contributions for marginal employment (30 %)
    divided by the total social security contribution rate
    (Gesamtsozialversicherungsbeitragssatz).

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        + sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = allg_sozialv_beitr + ges_krankenv_beitr_satz
    ag_anteil = allg_sozialv_beitr + _ges_krankenv_beitr_satz_arbeitg

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        + sozialv_beitr_params["ag_abgaben_geringf"]["st"]
    )

    # Now calculate final factor
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@dates_active(start="2022-10-01", change_name="midijob_faktor_f")
@add_rounding_spec(params_key="sozialv_beitr")
def midijob_faktor_f_ohne_minijob_st(
    sozialv_beitr_params: dict,
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Faktor F which is needed for the calculation of Bemessungsentgelt
    (beitragspflichtige Einnahme) of midijobs since October 2022. It is calculated as
    the ratio of the sum of lump-sum contributions for marginal employment (28 %)
    divided by the total social security contribution rate
    (Gesamtsozialversicherungsbeitragssatz). Since October 2022 the sum of lump-sum
    contributions for marginal employment does not include the 2% flat-rate tax.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # Calculate the Gesamtsozialversicherungsbeitragssatz by summing social
    # insurance contributions for employer and employee and
    # adding the mean Zusatzbeitrag
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        + sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = allg_sozialv_beitr + ges_krankenv_beitr_satz
    ag_anteil = allg_sozialv_beitr + _ges_krankenv_beitr_satz_arbeitg

    # Sum over the shares which are specific for midijobs.
    # New formula only inludes the lump-sum contributions to health care
    # and pension insurance
    pausch_mini = (
        sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
    )

    # Now calculate final factor f
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@dates_active(
    end="2022-09-30",
    change_name="midijob_bemessungsentgelt_m",
)
def midijob_bemessungsentgelt_m_bis_09_2022(
    bruttolohn_m: float,
    midijob_faktor_f: float,
    minijob_grenze: float,
    sozialv_beitr_params: dict,
) -> float:
    """Income subject to social insurance contributions for midijob until September
    2022.

    Bemessungsgeld (Gleitzonenentgelt) is the reference income for midijobs subject to
    social insurance contribution.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    midijob_faktor_f
        See :func:`midijob_faktor_f`.
    minijob_grenze
        See :func:`minijob_grenze`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # Now use the factor to calculate the overall bemessungsentgelt
    minijob_anteil = midijob_faktor_f * minijob_grenze
    lohn_über_mini = bruttolohn_m - minijob_grenze
    gewichtete_midijob_rate = (
        sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
        / (
            sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
            - minijob_grenze
        )
    ) - (
        minijob_grenze
        / (
            sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
            - minijob_grenze
        )
        * midijob_faktor_f
    )

    return minijob_anteil + lohn_über_mini * gewichtete_midijob_rate


@dates_active(start="2022-10-01", change_name="midijob_bemessungsentgelt_m")
def midijob_bemessungsentgelt_m_ab_10_2022(
    bruttolohn_m: float,
    midijob_faktor_f: float,
    minijob_grenze: float,
    sozialv_beitr_params: dict,
) -> float:
    """Total income subject to social insurance contributions for employers a and
    employees for midijob since October 2022. In the law, the considered income is
    referred to as "beitragspflichtige Einnahme".

    Beitragspflichtige Einnahme is the reference income for midijobs subject
    to employer and employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    midijob_faktor_f
        See :func:`midijob_faktor_f`.
    minijob_grenze
        See :func:`minijob_grenze`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    midijob_grenze = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]

    quotient1 = (midijob_grenze) / (midijob_grenze - minijob_grenze)
    quotient2 = (minijob_grenze) / (midijob_grenze - minijob_grenze)
    einkommen_diff = bruttolohn_m - minijob_grenze

    faktor1 = midijob_faktor_f * minijob_grenze
    faktor2 = (quotient1 - quotient2 * midijob_faktor_f) * einkommen_diff
    out = faktor1 + faktor2

    return out


def _midijob_beitragspfl_einnahme_arbeitn_m(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
    minijob_grenze: float,
) -> float:
    """Income subject to employee social insurance contributions for midijob since
    October 2022.

    Gesonderte Beitragspflichtige Einnahme is the reference income for midijobs subject
    to employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    minijob_grenze
        See :func:`minijob_grenze`.


    Returns
    -------
    Income subject to employee social insurance contributions for midijob.

    """
    midijob_grenze = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]

    quotient = midijob_grenze / (midijob_grenze - minijob_grenze)
    einkommen_diff = bruttolohn_m - minijob_grenze

    out = quotient * einkommen_diff

    return out


def regulär_beschäftigt(bruttolohn_m: float, sozialv_beitr_params: dict) -> bool:
    """Check if person is in regular employment.

    Employees earning more than the midijob threshold, are subject to all ordinary
    income and social insurance contribution regulations. In gettsim we call these
    regular employed.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether regular employed persons.

    """
    out = bruttolohn_m >= sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    return out
