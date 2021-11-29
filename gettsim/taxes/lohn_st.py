import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.social_insurance.krankenv import krankenv_beitr_regulär_beschäftigt
from gettsim.social_insurance.pflegev import pflegev_beitr_regulär_beschäftigt
from gettsim.social_insurance.rentenv import rentenv_beitr_regular_job
from gettsim.taxes.eink_st import st_tarif
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def lohn_steuer(
    bruttolohn_m: FloatSeries,
    vorsorgepauschale,
    alleinerziehend_freib_tu,
    params: dict,
    steuerklasse: IntSeries,
    jahr_renteneintr: IntSeries,
) -> FloatSeries:
    """
    Calculates Lohnsteuer = withholding tax on earnings,
    paid monthly by the employer on behalf of the employee.
    Apply the income tax tariff, but individually and with different
    exemptions, determined by the 'Steuerklasse'.
    Source: §39b EStG

    Parameters
    ----------
    bruttolohn_m: FloatSeries
        Monthly Earnings
    params: Float Series

    steuerklasse: IntSeries

    anz_kinder_tu: IntSeries

    Returns
    -------
    lohn_st

    """

    grundfreibetrag = params["eink_st"]["eink_st_tarif"]["thresholds"][1]
    # Full child allowance
    kinderfreibetrag_basis = (
        params["eink_st_abzuege"]["kinderfreibetrag"]["sächl_existenzmin"]
        + params["eink_st_abzuege"]["kinderfreibetrag"]["beitr_erz_ausb"]
    )
    # For certain tax brackets, twice the child allowance can be deducted
    kinderfreibetrag = kinderfreibetrag_basis * 2 * steuerklasse.isin([1, 2, 3]) + (
        kinderfreibetrag_basis * steuerklasse == 4
    )
    lohnsteuer_freibetrag = (grundfreibetrag * steuerklasse.isin([1, 2, 4])) + (
        2 * grundfreibetrag * (steuerklasse == 3)
    )
    lohnsteuer_freibetrag += alleinerziehend_freib_tu * (steuerklasse == 2)
    werbungskosten = (params["eink_st_abzuege"]["werbung"]) * (steuerklasse != 6)
    sonderausgaben = (params["eink_st_abzuege"]["sonder"]) * steuerklasse != 6
    # zu versteuerndes Einkommen for Lohnsteuer
    lohnsteuer_zve = (
        bruttolohn_m
        - werbungskosten
        - sonderausgaben
        - vorsorgepauschale(bruttolohn_m, steuerklasse, jahr_renteneintr, params)
    )

    lohnsteuer = lohnsteuer_zve.apply(st_tarif, params=params)

    """
        # Kinderfreibetrag. Split it for Steuerklasse 4
        tax_unit["lohnsteuer_kinderfreibetrag"] = tax_unit["child_num_kg"] * (
            e_st_abzuege_params["kifreib_s_exm"] + e_st_abzuege_params["kifreib_bea"]
        )
        tax_unit.loc[tax_unit["l_st_klasse"] == 4, "lohnsteuer_kinderfreibetrag"] = (
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


def vorsorgepauschale_ab_2010(
    bruttolohn_m: FloatSeries,
    steuerklasse: IntSeries,
    jahr: IntSeries,
    params: dict,
    kinderlos: BoolSeries,
) -> FloatSeries:
    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    vorsorg_rv = rentenv_beitr_regular_job(
        bruttolohn_m, params["soz_vers_beitr"]
    ) * vorsorg_rv_anteil(jahr, params["eink_st_abzuege"])
    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate.
    # a) at least 12% of earnings of earnings can be deducted, but only up to a certain threshold
    vorsorg_kv_option_a_basis = (
        params["eink_st_abzuege"]["vorsorgepauschale_mindestanteil"] * bruttolohn_m
    )

    vorsorg_kv_option_a_max = np.select(
        [steuerklasse == 3, steuerklasse != 3],
        [
            params["eink_st_abzuege"]["vorsorgepauschale_kv_max"]["stkl3"],
            params["eink_st_abzuege"]["vorsorgepauschale_kv_max"]["stkl_nicht3"],
        ],
    )
    vorsorg_kv_option_a = np.minimum(vorsorg_kv_option_a_max, vorsorg_kv_option_a_basis)
    # b) Take the actual contribtutions (usually the better option)
    vorsorg_kv_option_b = krankenv_beitr_regulär_beschäftigt(
        bruttolohn_m, params["soz_vers_beitr"]
    )
    vorsorg_kv_option_b += pflegev_beitr_regulär_beschäftigt(
        kinderlos, bruttolohn_m, params["soz_vers_beitr"]
    )
    # add both RV and KV deductions
    out = vorsorg_rv + np.maximum(vorsorg_kv_option_a, vorsorg_kv_option_b)

    return out


def vorsorgepauschale_2005_2010(bruttolohn, steuerklasse, params) -> FloatSeries:
    out = 0
    return out


def vorsorg_rv_anteil(jahr: IntSeries, params: dict) -> FloatSeries:
    """
    Calculates the share of pension contributions to be deducted for Lohnsteuer

    Parameters
    ----------
    jahr : IntSeries
    params : dict

    Returns
    -------
    out: float
    """

    out = piecewise_polynomial(
        x=jahr,
        thresholds=params["vorsorge_pauschale_rv_anteil"]["thresholds"],
        rates=params["vorsorge_pauschale_rv_anteil"]["rates"],
        intercepts_at_lower_thresholds=params["vorsorge_pauschale_rv_anteil"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return out
