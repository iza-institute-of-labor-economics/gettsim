"""Midijob."""

from _gettsim.function_types import policy_function


@policy_function()
def beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m(
    einkommensteuer__einnahmen__bruttolohn_m: float,
    minijob_grenze: float,
    sozialv_beitr_params: dict,
) -> float:
    """Income subject to employee social insurance contributions for midijob since
    October 2022.

    Gesonderte Beitragspflichtige Einnahme is the reference income for midijobs subject
    to employee social insurance contribution.

    Legal reference: Changes in § 20 SGB IV from 01.10.2022


    Parameters
    ----------
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
    minijob_grenze
        See :func:`minijob_grenze`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Income subject to employee social insurance contributions for midijob.

    """
    midijob_grenze = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]

    quotient = midijob_grenze / (midijob_grenze - minijob_grenze)
    einkommen_diff = einkommensteuer__einnahmen__bruttolohn_m - minijob_grenze

    out = quotient * einkommen_diff

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2004-12-31",
    leaf_name="midijob_faktor_f",
    params_key_for_rounding="sozialv_beitr",
)
def midijob_faktor_f_mit_minijob_steuerpauschale_bis_2004(
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang: float,
    sozialv_beitr_params: dict,
) -> float:
    """Midijob Faktor F until December 2004.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitslosenversicherung"]
    )

    allg_sozialv_beitr += sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_pflegev"]

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
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
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang: float,
    sozialv_beitr_params: dict,
) -> float:
    """Midijob Faktor F between 2005 and September 2025.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------.
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`

    Returns
    -------
    Income subject to social insurance contributions for midijob.

    """
    # First calculate the factor F from the formula in § 163 (10) SGB VI
    # Therefore sum the contributions which are the same for employee and employer
    allg_sozialv_beitr = (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_rentenv"]
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitslosenversicherung"]
    )

    allg_sozialv_beitr += sozialv_beitr_params["beitr_satz_jahresanfang"][
        "ges_pflegev"
    ]["standard"]

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
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
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang: float,
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang: float,
    sozialv_beitr_params: dict,
) -> float:
    """Midijob Faktor F since October 2022.

    Legal reference: § 163 Abs. 10 SGB VI


    Parameters
    ----------
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang`.
    sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
        See :func:`sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

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
        + sozialv_beitr_params["beitr_satz_jahresanfang"]["arbeitslosenversicherung"]
    )

    # Then calculate specific shares
    an_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitnehmer_jahresanfang
    )
    ag_anteil = (
        allg_sozialv_beitr
        + sozialversicherung__kranken__beitrag__beitragssatz_arbeitgeber_jahresanfang
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
    einkommensteuer__einnahmen__bruttolohn_m: float,
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
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
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
    lohn_über_mini = einkommensteuer__einnahmen__bruttolohn_m - minijob_grenze
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
    einkommensteuer__einnahmen__bruttolohn_m: float,
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
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
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
    einkommen_diff = einkommensteuer__einnahmen__bruttolohn_m - minijob_grenze

    faktor1 = midijob_faktor_f * minijob_grenze
    faktor2 = (quotient1 - quotient2 * midijob_faktor_f) * einkommen_diff
    out = faktor1 + faktor2

    return out


@policy_function(start_date="2003-04-01")
def in_gleitzone(
    einkommensteuer__einnahmen__bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    sozialv_beitr_params: dict,
) -> bool:
    """Individual's income is in midi-job range.

    Employed people with their wage in the range of gleitzone pay reduced social
    insurance contributions.

    Legal reference: § 20 Abs. 2 SGB IV

    Parameters
    ----------
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Whether individual's income is in midi-job range.

    """
    out = (
        einkommensteuer__einnahmen__bruttolohn_m
        <= sozialv_beitr_params["geringfügige_eink_grenzen_m"]["midijob"]
    ) and (not geringfügig_beschäftigt)
    return out
