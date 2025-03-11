"""Income tresholds for taxes and deductions."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def geringfügig_beschäftigt(
    einkommen__bruttolohn_m: float, minijob_grenze: float
) -> bool:
    """Individual earns less than marginal employment threshold.

    Marginal employed pay no social insurance contributions.

    Legal reference: § 8 Abs. 1 Satz 1 and 2 SGB IV

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    minijob_grenze
        See :func:`minijob_grenze`.


    Returns
    -------
    Whether person earns less than marginal employment threshold.

    """
    return einkommen__bruttolohn_m <= minijob_grenze


@policy_function(end_date="2003-03-31", leaf_name="regulär_beschäftigt")
def regulär_beschäftigt_vor_midijob(
    einkommen__bruttolohn_m: float, minijob_grenze: float
) -> bool:
    """Regular employment check until March 2003.

    Employees earning more than the minijob threshold, are subject to all ordinary
    income and social insurance contribution regulations. In gettsim we call these
    regular employed.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether regular employed persons.

    """
    out = einkommen__bruttolohn_m >= minijob_grenze
    return out


@policy_function(start_date="2003-04-01", leaf_name="regulär_beschäftigt")
def regulär_beschäftigt_mit_midijob(
    einkommen__bruttolohn_m: float, sozialv_beitr_params: dict
) -> bool:
    """Regular employment check since April 2003.

    Employees earning more than the midijob threshold, are subject to all ordinary
    income and social insurance contribution regulations. In gettsim we call these
    regular employed.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether regular employed persons.

    """
    out = (
        einkommen__bruttolohn_m
        >= sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    )
    return out


@policy_function(
    end_date="1999-12-31",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_unterscheidung_ost_west(
    demographics__wohnort_ost: bool, sozialv_beitr_params: dict
) -> float:
    """Minijob income threshold depending on place of living (East or West Germany).

    Until 1999, the threshold is different for East and West Germany.

    Parameters
    ----------
    demographics__wohnort_ost
        See basic input variable :ref:`demographics__wohnort_ost <demographics__wohnort_ost>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------

    """
    west = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["west"]
    ost = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["ost"]
    out = ost if demographics__wohnort_ost else west
    return float(out)


@policy_function(
    start_date="2000-01-01",
    end_date="2022-09-30",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_einheitlich(sozialv_beitr_params: dict) -> float:
    """Minijob income threshold depending on place of living.

    From 2000 onwards, the threshold is the same for all of Germany. Until September
    2022, the threshold is exogenously set.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------

    """
    return float(sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"])


@policy_function(
    start_date="2022-10-01",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_from_minimum_wage(sozialv_beitr_params: dict) -> float:
    """Minijob income threshold since 10/2022. Since then, it is calculated endogenously
    from the statutory minimum wage.

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


@policy_function()
def beitragspflichtige_einnahmen_arbeitnehmer_m(
    einkommen__bruttolohn_m: float,
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
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
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
    einkommen_diff = einkommen__bruttolohn_m - minijob_grenze

    out = quotient * einkommen_diff

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2004-12-31",
    leaf_name="midijob_faktor_f",
    params_key_for_rounding="sozialv_beitr",
)
def midijob_faktor_f_mit_minijob_steuerpauschale_bis_2004(
    sozialv_beitr_params: dict,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang: float,
) -> float:
    """Midijob Faktor F until December 2004.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang`.

    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitsl_v"]
    )

    allg_sozialv_beitr += sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_pflegev"]

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
    )

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_krankenv"]
        + sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["st"]
    )

    # Now calculate final factor
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2022-09-30",
    leaf_name="midijob_faktor_f",
    params_key_for_rounding="sozialv_beitr",
)
def midijob_faktor_f_mit_minijob_steuerpauschale_ab_2005(
    sozialv_beitr_params: dict,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang: float,
) -> float:
    """Midijob Faktor F between 2005 and September 2025.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang`.

    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitsl_v"]
    )

    allg_sozialv_beitr += sozialv_beitr_params["beitr_satz_jahresanfang"][
        "ges_pflegev"
    ]["standard"]

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
    )

    # Sum over the shares which are specific for midijobs.
    pausch_mini = (
        sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_krankenv"]
        + sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["st"]
    )

    # Now calculate final factor
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@policy_function(
    start_date="2022-10-01",
    leaf_name="midijob_faktor_f",
    params_key_for_rounding="sozialv_beitr",
)
def midijob_faktor_f_ohne_minijob_steuerpauschale(
    sozialv_beitr_params: dict,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang: float,
) -> float:
    """Midijob Faktor F since October 2022.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang`.

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
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_pflegev"]["standard"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitsl_v"]
    )

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherungsbeiträge__krankenversicherung__beitragssatz_arbeitgeber_jahresanfang
    )

    # Sum over the shares which are specific for midijobs.
    # New formula only inludes the lump-sum contributions to health care
    # and pension insurance
    pausch_mini = (
        sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_krankenv"]
        + sozialv_beitr_params["ag_abgaben_geringf_jahresanfang"]["ges_rentenv"]
    )

    # Now calculate final factor f
    out = pausch_mini / (an_anteil + ag_anteil)

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="midijob_bemessungsentgelt_m",
)
def midijob_bemessungsentgelt_m_bis_09_2022(
    einkommen__bruttolohn_m: float,
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
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
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
    lohn_über_mini = einkommen__bruttolohn_m - minijob_grenze
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


@policy_function(start_date="2022-10-01", leaf_name="midijob_bemessungsentgelt_m")
def midijob_bemessungsentgelt_m_ab_10_2022(
    einkommen__bruttolohn_m: float,
    midijob_faktor_f: float,
    minijob_grenze: float,
    sozialv_beitr_params: dict,
) -> float:
    """Total income subject to social insurance contributions for midijobs since October
    2022.

    In the law, the considered income is referred to as "beitragspflichtige Einnahme".

    Beitragspflichtige Einnahme is the reference income for midijobs subject to employer
    and employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022


    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
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
    einkommen_diff = einkommen__bruttolohn_m - minijob_grenze

    faktor1 = midijob_faktor_f * minijob_grenze
    faktor2 = (quotient1 - quotient2 * midijob_faktor_f) * einkommen_diff
    out = faktor1 + faktor2

    return out


@policy_function(start_date="2003-04-01")
def in_gleitzone(
    einkommen__bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    sozialv_beitr_params: dict,
) -> bool:
    """Individual's income is in midi-job range.

    Employed people with their wage in the range of gleitzone pay reduced social
    insurance contributions.

    Legal reference: § 20 Abs. 2 SGB IV

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether individual's income is in midi-job range.

    """
    out = (
        einkommen__bruttolohn_m
        <= sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    ) and (not geringfügig_beschäftigt)
    return out
