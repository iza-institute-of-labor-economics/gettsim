from _gettsim.shared import policy_info
from _gettsim.taxes.eink_st import _eink_st_tarif


@policy_info(params_key_for_rounding="lohnst")
def lohnst_eink_y(
    bruttolohn_m: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale_y: float,
) -> float:
    """Calculate tax base for Lohnsteuer (withholding tax on earnings).

    Parameters
    ----------
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
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
        12 * bruttolohn_m
        - werbungskosten
        - sonderausgaben
        - entlastung_freibetrag_alleinerz
        - vorsorgepauschale_y,
        0.0,
    )

    return out


def _lohnsteuer_klasse5_6_basis_y(taxable_inc: float, eink_st_params: dict) -> float:
    """Calculate base for Lohnsteuer for Steuerklasse 5 and 6, by applying
    obtaining twice the difference between applying the factors 1.25 and 0.75
    to the lohnsteuer payment. There is a also a minimum amount, which is checked
    afterwards.

    §39 b Absatz 2 Satz 7 (part 1):

        Jahreslohnsteuer die sich aus dem Zweifachen des Unterschiedsbetrags zwischen
        dem Steuerbetrag für das Eineinviertelfache und dem Steuerbetrag für das
        Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a Absatz 1 ergibt;
        die Jahreslohnsteuer beträgt jedoch mindestens 14 Prozent des zu versteuernden
        Jahresbetrags.

    Parameters
    ----------

    taxable_inc:
        Taxable Income used in function (not necessarily the same as lohnst_eink_y)
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`

    Returns
    -------
    Base for Lohnsteuer for Steuerklasse 5 and 6

    """

    out = max(
        2
        * (
            _eink_st_tarif(taxable_inc * 1.25, eink_st_params)
            - _eink_st_tarif(taxable_inc * 0.75, eink_st_params)
        ),
        taxable_inc * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    return out


@policy_info(
    start_date="2019-01-01",
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2019(
    _ges_krankenv_bruttolohn_reg_beschäftigt_m: float,
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
    _ges_krankenv_bruttolohn_reg_beschäftigt_m:
        See basic input variable :ref:`_ges_krankenv_bruttolohn_reg_beschäftigt_m`
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

    out = (
        _ges_krankenv_bruttolohn_reg_beschäftigt_m
        * 12
        * (
            sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
            + ges_krankenv_zusatzbeitr_satz / 2
            + ges_pflegev_beitr_satz_arbeitnehmer
        )
    )

    return out


@policy_info(
    start_date="2015-01-01",
    end_date="2018-12-31",
    name_in_dag="vorsorge_krankenv_option_b",
)
def vorsorge_krankenv_option_b_ab_2015_bis_2018(
    _ges_krankenv_bruttolohn_reg_beschäftigt_m: float,
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
    _ges_krankenv_bruttolohn_reg_beschäftigt_m:
        See basic input variable :ref:`_ges_krankenv_bruttolohn_reg_beschäftigt_m`
    ges_krankenv_zusatzbeitr_satz
        See :func:ges_krankenv_zusatzbeitr_satz`.
    ges_pflegev_beitr_satz_arbeitnehmer:
        See :func:ges_pflegev_beitr_satz_arbeitnehmer`.


    Returns
    -------
    Health care deductions for withholding taxes option b

    """

    out = (
        _ges_krankenv_bruttolohn_reg_beschäftigt_m
        * 12
        * (
            sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
            + ges_krankenv_zusatzbeitr_satz
            + ges_pflegev_beitr_satz_arbeitnehmer
        )
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
    bruttolohn_m: float,
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
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
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
            12 * bruttolohn_m,
            12 * sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["ost"],
        )
    else:
        bruttolohn_rente = min(
            12 * bruttolohn_m,
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


def _lohnst_m(
    lohnst_eink_y: float, eink_st_params: dict, lohnst_params: dict, steuerklasse: int
) -> float:
    """
    Calculates Lohnsteuer (withholding tax on earnings), paid monthly by the employer on
    behalf of the employee. Apply the income tax tariff, but individually and with
    different exemptions, determined by the 'Steuerklasse'. Source: §39b EStG

    Calculation is differentiated by steuerklasse

    1,2,4: Standard tariff (§32a (1) EStG) 3: Splitting tariff (§32a (5) EStG) 5,6: Take
    twice the difference between applying the tariff on 5/4 and 3/4 of taxable income.
    Tax rate may not be lower than the starting statutory one.

    Parameters
    ----------
    lohnst_eink_y
        See :func:`lohnst_eink_y`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`
    lohnst_params
        See params documentation :ref:`lohnst_params <lohnst_params>`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.


    Returns
    -------
    Individual withholding tax on monthly basis

    """

    lohnsteuer_basistarif = _eink_st_tarif(lohnst_eink_y, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(lohnst_eink_y / 2, eink_st_params)
    lohnsteuer_5_6_basis = _lohnsteuer_klasse5_6_basis_y(lohnst_eink_y, eink_st_params)

    grenze_1 = lohnst_params["lohnst_einkommensgrenzen"][0]
    grenze_2 = lohnst_params["lohnst_einkommensgrenzen"][1]
    grenze_3 = lohnst_params["lohnst_einkommensgrenzen"][2]

    lohnsteuer_grenze_1 = _lohnsteuer_klasse5_6_basis_y(grenze_1, eink_st_params)
    max_lohnsteuer = (
        lohnsteuer_grenze_1
        + (lohnst_eink_y - grenze_1) * eink_st_params["eink_st_tarif"]["rates"][0][3]
    )
    lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis_y(grenze_2, eink_st_params)
    lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params["eink_st_tarif"][
        "rates"
    ][0][3]
    lohnsteuer_klasse5_6_tmp = lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3

    if lohnst_eink_y < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= lohnst_eink_y < grenze_2:
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer, _lohnsteuer_klasse5_6_basis_y(lohnst_eink_y, eink_st_params)
        )
    elif grenze_2 <= lohnst_eink_y < grenze_3:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_grenze_2
            + (lohnst_eink_y - grenze_2)
            * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
    else:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_klasse5_6_tmp
            + (lohnst_eink_y - grenze_3)
            * eink_st_params["eink_st_tarif"]["rates"][0][4]
        )

    if steuerklasse in {1, 2, 4}:
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    out = out / 12

    return max(out, 0.0)


def lohnst_m(
    lohnst_eink_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Calls _lohnst_m with individual income
    """
    return _lohnst_m(lohnst_eink_y, eink_st_params, lohnst_params, steuerklasse)


def lohnst_mit_kinderfreib_m(
    lohnst_eink_y: float,
    kinderfreib_für_soli_st_lohnst_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Same as lohnst_m, but with an alternative income definition that
    takes child allowance into account. Important only for calculation
    of soli on Lohnsteuer!
    """

    eink = max(lohnst_eink_y - kinderfreib_für_soli_st_lohnst_y, 0)

    return _lohnst_m(eink, eink_st_params, lohnst_params, steuerklasse)
