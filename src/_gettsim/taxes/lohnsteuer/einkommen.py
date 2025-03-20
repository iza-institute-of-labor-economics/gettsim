"""Income relevant for withholding tax on earnings (Lohnsteuer)."""

from _gettsim.function_types import policy_function


@policy_function(params_key_for_rounding="lohnst")
def einkommen_y(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale_y: float,
) -> float:
    """Calculate tax base for Lohnsteuer (withholding tax on earnings).

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y:
      See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y>`.
    steuerklasse:
      See :func:`steuerklasse`
    eink_st_abzuege_params:
      See :func:`eink_st_abzuege_params`
    vorsorgepauschale_y
        See :func:`vorsorgepauschale_y`

    Returns
    -------

    """
    entlastung_freibetrag_alleinerz = (steuerklasse == 2) * eink_st_abzuege_params[
        "alleinerziehendenfreibetrag"
    ]

    if steuerklasse == 6:
        werbungskosten = 0
    else:
        werbungskosten = eink_st_abzuege_params["werbungskostenpauschale"]

    if steuerklasse == 6:
        sonderausgaben = 0
    else:
        sonderausgaben = eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]

    # Zu versteuerndes Einkommen / tax base for Lohnsteuer.
    out = max(
        einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y
        - werbungskosten
        - sonderausgaben
        - entlastung_freibetrag_alleinerz
        - vorsorgepauschale_y,
        0.0,
    )

    return out


@policy_function(
    start_date="2015-01-01",
    end_date="2018-12-31",
    leaf_name="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2015_bis_2018(
    sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y: float,
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz: float,
    sozialv_beitr_params: dict,
    sozialversicherung__pflege__beitrag__beitragssatz: float,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y:
        See :func:`sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y`.
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz
        See :func:`sozialversicherung__kranken__beitrag__zusatzbeitragssatz`.
    sozialversicherung__pflege__beitrag__beitragssatz:
        See :func:`sozialversicherung__pflege__beitrag__beitragssatz`.


    Returns
    -------
    Health care deductions for withholding taxes option b

    """

    out = sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y * (
        sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + sozialversicherung__kranken__beitrag__zusatzbeitragssatz
        + sozialversicherung__pflege__beitrag__beitragssatz
    )

    return out


@policy_function(
    start_date="2019-01-01",
    leaf_name="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2019(
    sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y: float,
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz: float,
    sozialversicherung__pflege__beitrag__beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y:
        See :func:`sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y`.
    sozialversicherung__kranken__beitrag__zusatzbeitragssatz
        See :func:`sozialversicherung__kranken__beitrag__zusatzbeitragssatz`.
    sozialversicherung__pflege__beitrag__beitragssatz:
        See :func:`sozialversicherung__pflege__beitrag__beitragssatz`.
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params`


    Returns
    -------
    Health care deductions for withholding taxes option b

    """

    out = sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y * (
        sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + sozialversicherung__kranken__beitrag__zusatzbeitragssatz / 2
        + sozialversicherung__pflege__beitrag__beitragssatz
    )

    return out


@policy_function()
def vorsorge_krankenv_option_a(
    sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deuctions.
    This function calculates option a where at least 12% of earnings
    of earnings can be deducted, but only up to a certain threshold.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__betrag_regulär_beschäftigt_m:
        See :func:`sozialversicherung__kranken__beitrag__betrag_regulär_beschäftigt_m`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.
    eink_st_abzuege_params:
        See params documentation :ref:`eink_st_abzuege_params`


    Returns
    -------
    Health care deductions for withholding taxes option a

    """

    vorsorge_krankenv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"]
        * sozialversicherung__kranken__beitrag__einkommen_regulär_beschäftigt_y
    )

    if steuerklasse == 3:
        vorsorge_krankenv_option_a_max = eink_st_abzuege_params[
            "vorsorgepauschale_kv_max"
        ]["steuerklasse_3"]
    else:
        vorsorge_krankenv_option_a_max = eink_st_abzuege_params[
            "vorsorgepauschale_kv_max"
        ]["steuerklasse_nicht3"]

    out = min(vorsorge_krankenv_option_a_max, vorsorge_krankenv_option_a_basis)

    return out


@policy_function(
    start_date="2010-01-01",
    leaf_name="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2010(  # noqa: PLR0913
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y: float,
    demographics__wohnort_ost: bool,
    sozialv_beitr_params: dict,
    vorsorge_krankenv_option_a: float,
    vorsorge_krankenv_option_b: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgepauschale for Lohnsteuer valid since 2010. Those are deducted
    from gross earnings. Idea is similar, but not identical, to Vorsorgeaufwendungen
    used when calculating Einkommensteuer.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y:
      See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y>`.
    demographics__wohnort_ost:
      See basic input variable :ref:`demographics__wohnort_ost <demographics__wohnort_ost>`.
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params`
    vorsorge_krankenv_option_a:
      See :func:`vorsorge_krankenv_option_a`
    vorsorge_krankenv_option_b:
      See :func:`vorsorge_krankenv_option_b`
    eink_st_abzuege_params:
      See params documentation :ref:`eink_st_abzuege_params`


    Returns
    -------
    Individual Vorsorgepauschale on annual basis

    """

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    if demographics__wohnort_ost:
        bruttolohn_rente = min(
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y,
            12 * sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["ost"],
        )
    else:
        bruttolohn_rente = min(
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y,
            12 * sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["west"],
        )

    vorsorg_rentenv = (
        bruttolohn_rente
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
        * eink_st_abzuege_params["vorsorgepauschale_rentenv_anteil"]
    )

    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate
    # the deuctions.
    # a) at least 12% of earnings of earnings can be deducted,
    #    but only up to a certain threshold
    #  b) Take the actual contributions (usually the better option),
    #   but apply the reduced rate

    vorsorg_krankenv = max(vorsorge_krankenv_option_a, vorsorge_krankenv_option_b)

    # add both RV and KV deductions. For KV, take the larger amount.
    out = vorsorg_rentenv + vorsorg_krankenv
    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    leaf_name="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2005_bis_2009() -> float:
    return 0.0
