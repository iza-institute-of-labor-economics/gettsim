"""Income relevant for withholding tax on earnings (Lohnsteuer)."""

from _gettsim.shared import policy_info
from _gettsim.taxes.einkommensteuer.solidaritaetszuschlag import _soli_st_tarif


@policy_info(params_key_for_rounding="lohnst")
def lohnst_eink_y(
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


def soli_st_lohnst_y(lohnst_mit_kinderfreib_y: float, soli_st_params: dict) -> float:
    """Calculates the monthly Solidarity Surcharge on Lohnsteuer
    (withholding tax on earnings).

    Parameters
    ----------
    lohnst_mit_kinderfreib_y
        See :func:`lohnst_mit_kinderfreib_y`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
        Solidarity Surcharge on Lohnsteuer
    -------

    """

    return _soli_st_tarif(lohnst_mit_kinderfreib_y, soli_st_params)


@policy_info(
    start_date="2015-01-01",
    end_date="2018-12-31",
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2015_bis_2018(
    _ges_krankenv_bruttolohn_reg_beschäftigt_y: float,
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_reg_beschäftigt_y:
        See :func:`_ges_krankenv_bruttolohn_reg_beschäftigt_y`.
    ges_krankenv_zusatzbeitr_satz
        See :func:ges_krankenv_zusatzbeitr_satz`.
    ges_pflegev_beitr_satz_arbeitnehmer:
        See :func:ges_pflegev_beitr_satz_arbeitnehmer`.


    Returns
    -------
    Health care deductions for withholding taxes option b

    """

    out = _ges_krankenv_bruttolohn_reg_beschäftigt_y * (
        sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + ges_krankenv_zusatzbeitr_satz
        + ges_pflegev_beitr_satz_arbeitnehmer
    )

    return out


@policy_info(
    start_date="2019-01-01",
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2019(
    _ges_krankenv_bruttolohn_reg_beschäftigt_y: float,
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deductions: "Option a" and "Option b".
    This function calculates option b where the actual contributions
    are used.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_reg_beschäftigt_y:
        See :func:`_ges_krankenv_bruttolohn_reg_beschäftigt_y`.
    ges_krankenv_zusatzbeitr_satz
        See :func:ges_krankenv_zusatzbeitr_satz`.
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params`
    ges_pflegev_beitr_satz_arbeitnehmer:
        See :func:ges_pflegev_beitr_satz_arbeitnehmer`.


    Returns
    -------
    Health care deductions for withholding taxes option b

    """

    out = _ges_krankenv_bruttolohn_reg_beschäftigt_y * (
        sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + ges_krankenv_zusatzbeitr_satz / 2
        + ges_pflegev_beitr_satz_arbeitnehmer
    )

    return out


def vorsorge_krankenv_option_a(
    _ges_krankenv_bruttolohn_reg_beschäftigt_y: float,
    eink_st_abzuege_params: dict,
    steuerklasse: int,
) -> float:
    """For health care deductions, there are two ways to calculate
    the deuctions.
    This function calculates option a where at least 12% of earnings
    of earnings can be deducted, but only up to a certain threshold.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_reg_beschäftigt_m:
        See basic input variable :ref:`_ges_krankenv_bruttolohn_reg_beschäftigt_m`
    eink_st_abzuege_params:
        See params documentation :ref:`eink_st_abzuege_params`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.


    Returns
    -------
    Health care deductions for withholding taxes option a

    """

    vorsorge_krankenv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"]
        * _ges_krankenv_bruttolohn_reg_beschäftigt_y
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


@policy_info(
    start_date="2010-01-01",
    name_in_dag="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2010(  # noqa: PLR0913
    bruttolohn_y: float,
    wohnort_ost: bool,
    eink_st_abzuege_params: dict,
    sozialv_beitr_params: dict,
    vorsorge_krankenv_option_a: float,
    vorsorge_krankenv_option_b: float,
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
    eink_st_abzuege_params:
      See params documentation :ref:`eink_st_abzuege_params`
    sozialv_beitr_params:
        See params documentation :ref:`sozialv_beitr_params`
    vorsorge_krankenv_option_a:
      See :func:`vorsorge_krankenv_option_a`
    vorsorge_krankenv_option_b:
      See :func:`vorsorge_krankenv_option_b`


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


@policy_info(
    start_date="2005-01-01",
    end_date="2009-12-31",
    name_in_dag="vorsorgepauschale_y",
    params_key_for_rounding="lohnst",
)
def vorsorgepauschale_y_ab_2005_bis_2009() -> float:
    out = 0.0
    return out


def kinderfreib_für_soli_st_lohnst_y(
    steuerklasse: int,
    _eink_st_kinderfreib_anz_ansprüche: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Child Allowance for Lohnsteuer-Soli.

    For the purpose of Soli on Lohnsteuer, the child allowance not only depends on the
    number of children, but also on the steuerklasse

    """

    kinderfreib_basis = (
        eink_st_abzuege_params["kinderfreib"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreib"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    if steuerklasse in {1, 2, 3}:
        out = kinderfreib_basis * 2 * _eink_st_kinderfreib_anz_ansprüche
    elif steuerklasse == 4:
        out = kinderfreib_basis * _eink_st_kinderfreib_anz_ansprüche
    else:
        out = 0
    return out
