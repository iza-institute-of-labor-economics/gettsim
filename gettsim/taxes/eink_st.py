from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.soli_st import soli_st_tu


def _st_kein_kind_freib_tu(
    _zu_verst_eink_kein_kinderfreib_tu, _anz_erwachsene_tu, eink_st_params
):
    """ Taxes without child allowance.

    Parameters
    ----------
    _zu_verst_eink_kein_kinderfreib_tu
    _anz_erwachsene_tu
    eink_st_params

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_kein_kinderfreib_tu / _anz_erwachsene_tu

    return _anz_erwachsene_tu * _st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )


def _st_kind_freib_tu(
    _zu_verst_eink_kinderfreib_tu, _anz_erwachsene_tu, eink_st_params
):
    """Taxes with child allowance.

    Parameters
    ----------
    _zu_verst_eink_kinderfreib_tu
    _anz_erwachsene_tu
    eink_st_params

    Returns
    -------

    """
    zu_verst_eink_per_indiv = _zu_verst_eink_kinderfreib_tu / _anz_erwachsene_tu

    return _anz_erwachsene_tu * _st_tarif(
        zu_verst_eink_per_indiv, params=eink_st_params
    )


def _st_tarif(x, params):
    """ The German Income Tax Tariff.
     Modelled only after 2002 so far.

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (Series): taxable income
        params (dict): tax-benefit parameters specific to year and reform
    """
    eink_st = piecewise_polynomial(
        x=x,
        thresholds=params["eink_st_tarif"]["thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return eink_st


def lohnsteuer(tax_unit, params, e_st_abzuege_params, soli_st_params):
    """ Calculates Lohnsteuer = withholding tax on earnings,
        paid monthly by the employer on behalf of the employee.
        Apply the income tax tariff, but individually and with different
        exemptions, determined by the 'Steuerklasse'
    """
    # Steuerklasse 1 gets the basic exemption. Default value.
    # Also holds for Steuerklasse 4
    tax_unit["lohnsteuer_abzüge"] = params["G"]
    # Steuerklasse 2 for single parents.
    tax_unit.loc[tax_unit["lohn_st_klasse"] == 2, "lohnsteuer_abzüge"] = (
        params["G"] + e_st_abzuege_params["hhfreib"]
    )
    # Steuerklasse 3: married. get twice the basic exemption
    tax_unit.loc[tax_unit["lohn_st_klasse"] == 3, "lohnsteuer_abzüge"] = 2 * params["G"]
    # Steuerklasse 5: married and if partner has klasse 3. No exemption
    tax_unit.loc[tax_unit["lohn_st_klasse"] == 5, "lohnsteuer_abzüge"] = 0

    tax_unit.loc[tax_unit["lohn_st_klasse"] != 6, "lohnsteuer_abzüge"] += (
        e_st_abzuege_params["werbung"]
        + e_st_abzuege_params["sonder"]
        + calc_vorsorgepauschale()
    )

    # Kinderfreibetrag. Split it for Steuerklasse 4
    tax_unit["lohnsteuer_kinderfreibetrag"] = tax_unit["child_num_kg"] * (
        e_st_abzuege_params["kifreib_s_exm"] + e_st_abzuege_params["kifreib_bea"]
    )
    tax_unit.loc[tax_unit["e_st_klasse"] == 4, "lohnsteuer_kinderfreibetrag"] = (
        tax_unit["lohnsteuer_kinderfreibetrag"] / 2
    )

    tax_unit["lohnsteuer_inc"] = tax_unit["m_wage"] * 12 - tax_unit["lohnsteuer_abzüge"]
    tax_unit["lohnsteuer"] = _st_tarif(tax_unit["lohnsteuer_inc"], params).astype(int)
    # print(tax_unit["lohnsteuer"])
    # For Soli, subtract Kinderfreibetrag!
    tax_unit["lohnsteuer_soli"] = soli_st_tu(
        tax_unit["lohnsteuer_inc"] - tax_unit["lohnsteuer_kinderfreibetrag"],
        soli_st_params,
    )

    return tax_unit[["lohnsteuer", "lohnsteuer_soli"]]


def calc_vorsorgepauschale():
    return 0.0
