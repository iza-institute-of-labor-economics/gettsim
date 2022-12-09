from _gettsim.shared import add_rounding_spec


def minijob_grenze(
    wohnort_ost: bool, minijob_grenze_west: float, minijob_grenze_ost: float
) -> float:
    """Select the income threshold depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------

    """
    out = minijob_grenze_ost if wohnort_ost else minijob_grenze_west
    return float(out)


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
        bruttolohn_m <= soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    ) and (not geringfügig_beschäftigt)
    return out


@add_rounding_spec(params_key="soz_vers_beitr")
def midijob_faktor_f_bis_09_2022(
    soz_vers_beitr_params: dict,
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
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
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
    allg_soz_vers_beitr = (
        soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
        + soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        + soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = allg_soz_vers_beitr + ges_krankenv_beitr_satz
    ag_anteil = allg_soz_vers_beitr + _ges_krankenv_beitr_satz_arbeitg

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["st"]
    )

    # Now calculate final factor
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@add_rounding_spec(params_key="soz_vers_beitr")
def midijob_faktor_f_ab_10_2022(
    soz_vers_beitr_params: dict,
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
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
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
    allg_soz_vers_beitr = (
        soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
        + soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        + soz_vers_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = allg_soz_vers_beitr + ges_krankenv_beitr_satz
    ag_anteil = allg_soz_vers_beitr + _ges_krankenv_beitr_satz_arbeitg

    # Sum over the shares which are specific for midijobs.
    # New formula only inludes the lump-sum contributions to health care
    # and pension insurance
    pausch_mini = (
        soz_vers_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        + soz_vers_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
    )

    # Now calculate final factor f
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


def midijob_bemessungsentgelt_m_bis_09_2022(
    midijob_faktor_f: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    minijob_grenze_west: float,
) -> float:
    """Income subject to social insurance contributions for midijob until September
    2022.

    Bemmessungsgeld (Gleitzonenentgelt) is the reference income for midijobs subject to
    social insurance contribution.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    midijob_faktor_f
        See :func:`midijob_faktor_f`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # Now use the factor to calculate the overall bemessungsentgelt
    minijob_anteil = midijob_faktor_f * minijob_grenze_west
    lohn_über_mini = bruttolohn_m - minijob_grenze_west
    gewichtete_midijob_rate = (
        soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
            - minijob_grenze_west
        )
    ) - (
        minijob_grenze_west
        / (
            soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
            - minijob_grenze_west
        )
        * midijob_faktor_f
    )

    return minijob_anteil + lohn_über_mini * gewichtete_midijob_rate


def midijob_bemessungsentgelt_m_ab_10_2022(
    midijob_faktor_f: float,
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
    minijob_grenze: float,
) -> float:
    """Total income subject to social insurance contributions for employers a and
    employees for midijob since October 2022. In the law, the considered income is
    referred to as "beitragspflichtige Einnahme".

    Beitragspflichtige Einnahme is the reference income for midijobs subject
    to employer and employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022


    Parameters
    ----------
    midijob_faktor_f
        See :func:`midijob_faktor_f`.
    minijob_grenze
        See :func:`minijob_grenze`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    midijob_grenze = soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]

    quotient1 = (midijob_grenze) / (midijob_grenze - minijob_grenze)
    quotient2 = (minijob_grenze) / (midijob_grenze - minijob_grenze)
    einkommen_diff = bruttolohn_m - minijob_grenze

    faktor1 = midijob_faktor_f * minijob_grenze
    faktor2 = (quotient1 - quotient2 * midijob_faktor_f) * einkommen_diff
    out = faktor1 + faktor2

    return out


def _midijob_beitragspf_einnahme_arbeitn_m(
    bruttolohn_m: float,
    soz_vers_beitr_params: dict,
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
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    minijob_grenze
        See :func:`minijob_grenze`.


    Returns
    -------
    Income subject to employee social insurance contributions for midijob.

    """
    midijob_grenze = soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]

    quotient = midijob_grenze / (midijob_grenze - minijob_grenze)
    einkommen_diff = bruttolohn_m - minijob_grenze

    out = quotient * einkommen_diff

    return out


@add_rounding_spec(params_key="soz_vers_beitr")
def minijob_grenze_west_vor_10_2022(soz_vers_beitr_params: dict) -> float:
    """Obtains marginal job thresholds for West Germany before October 2022.

    Parameters
    ----------
    soz_vers_beitr_params:
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["west"]


@add_rounding_spec(params_key="soz_vers_beitr")
def minijob_grenze_ost_vor_10_2022(soz_vers_beitr_params: dict) -> float:
    """Obtains marginal job thresholds for East Germany before October 2022.

    Parameters
    ----------
    soz_vers_beitr_params:
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["ost"]


@add_rounding_spec(params_key="soz_vers_beitr")
def minijob_grenze_ab_10_2022(soz_vers_beitr_params: dict) -> float:
    """Obtains marginal job threshold since 10/2022. Since then, it is calculated from
    the statutory minimum wage.

    Parameters
    ----------
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """

    return (
        soz_vers_beitr_params["mindestlohn"]
        * soz_vers_beitr_params["geringf_eink_faktor"]
        / soz_vers_beitr_params["geringf_eink_divisor"]
    )


def regulär_beschäftigt(bruttolohn_m: float, soz_vers_beitr_params: dict) -> bool:
    """Check if person is in regular employment.

    Employees earning more than the midijob threshold, are subject to all ordinary
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
        bruttolohn_m >= soz_vers_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    )
    return out
