from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries
import numpy as np

def lohnsteuer(bruttolohn_m: FloatSeries,
            params: FloatSeries,
            steuerklassen: IntSeries,
            anz_kinder_tu: IntSeries,
            alleinerziehend_freib_tu: IntSeries):
    """
    Calculates Lohnsteuer = withholding tax on earnings,
    paid monthly by the employer on behalf of the employee.
    Apply the income tax tariff, but individually and with different
    exemptions, determined by the 'Steuerklasse'

    Parameters
    ----------
    bruttolohn_m: FloatSeries
        Monthly Earnings
    params: Float Series

    steuerklassen: IntSeries

    anz_kinder_tu: IntSeries

    Returns
    -------
    lohn_st

    """
    grundfreibetrag = params["eink_st_tarif"]["G"]
    # Full child allowance
    kinderfreibetrag = params["eink_st_abzuege"]["sächl_existenzmin"] + params["eink_st_abzuege"]["beitr_erz_ausb"]
    lohnsteuer_freibetrag = (grundfreibetrag * steuerklassen.isin([1, 2, 4])) + (2 * grundfreibetrag * (steuerklassen == 3))
    lohnsteuer_freibetrag += (alleinerziehend_freib_tu * (steuerklassen == 2))
    werbungskosten = (params["eink_st_abzuege"]["werbung"] + params["eink_st_abzuege"]["sonder"]) * (steuerklassen != 6)
    vorsorgepauschale = calc_vorsorgepauschale() * (steuerklassen != 6)

"""
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
"""
    return lohnsteuer


def calc_vorsorgepauschale():
    return 0.0
