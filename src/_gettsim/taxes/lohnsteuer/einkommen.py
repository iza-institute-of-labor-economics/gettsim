"""Income relevant for withholding tax on earnings (Lohnsteuer)."""

from _gettsim.functions.policy_function import policy_function


@policy_function(params_key_for_rounding="lohnst")
def einkommen_y(
    bruttolohn_y: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale_y: float,
) -> float:
    """Calculate tax base for Lohnsteuer (withholding tax on earnings).

    Parameters
    ----------
    bruttolohn_y:
      See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
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
        "alleinerz_freibetrag"
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
        bruttolohn_y
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
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2015_bis_2018(
    sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y: float,  # noqa: E501
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz: float,  # noqa: E501
    sozialv_beitr_params: dict,
    sozialversicherungsbeitraege__pflegeversicherung__beitragssatz: float,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y:
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz`.
    sozialversicherungsbeitraege__pflegeversicherung__beitragssatz:
        See :func:`sozialversicherungsbeitraege__pflegeversicherung__beitragssatz`.


    Returns
    -------
    Health care deductions for withholding taxes option b

    """  # noqa: E501

    out = (
        sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y
        * (
            sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
            + sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz  # noqa: E501
            + sozialversicherungsbeitraege__pflegeversicherung__beitragssatz
        )
    )

    return out


@policy_function(
    start_date="2019-01-01",
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2019(
    sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y: float,  # noqa: E501
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz: float,  # noqa: E501
    sozialversicherungsbeitraege__pflegeversicherung__beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y:
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz`.
    sozialversicherungsbeitraege__pflegeversicherung__beitragssatz:
        See :func:`sozialversicherungsbeitraege__pflegeversicherung__beitragssatz`.
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params`


    Returns
    -------
    Health care deductions for withholding taxes option b

    """  # noqa: E501

    out = (
        sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y
        * (
            sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
            + sozialversicherungsbeitraege__krankenversicherung__beitragssatz__zusatzbeitrag_satz  # noqa: E501
            / 2
            + sozialversicherungsbeitraege__pflegeversicherung__beitragssatz
        )
    )

    return out


@policy_function
def vorsorge_krankenv_option_a(
    sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y: float,  # noqa: E501
    steuerklasse: int,
    eink_st_abzuege_params: dict,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deuctions.
    This function calculates option a where at least 12% of earnings
    of earnings can be deducted, but only up to a certain threshold.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__betrag_regulär_beschäftigt_m:
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_regulär_beschäftigt_m`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.
    eink_st_abzuege_params:
        See params documentation :ref:`eink_st_abzuege_params`


    Returns
    -------
    Health care deductions for withholding taxes option a

    """  # noqa: E501

    vorsorge_krankenv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"]
        * sozialversicherungsbeitraege__krankenversicherung__einkommen_regulär_beschäftigt_y  # noqa: E501
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
    name_in_dag="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2010(  # noqa: PLR0913
    bruttolohn_y: float,
    wohnort_ost: bool,
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
    bruttolohn_y:
      See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    wohnort_ost:
      See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
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
    if wohnort_ost:
        bruttolohn_rente = min(
            bruttolohn_y,
            12 * sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["ost"],
        )
    else:
        bruttolohn_rente = min(
            bruttolohn_y,
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
    name_in_dag="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2005_bis_2009() -> float:
    return 0.0
