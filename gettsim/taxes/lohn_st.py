import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.social_insurance.krankenv import krankenv_beitr_regulär_beschäftigt
from gettsim.social_insurance.pflegev import pflegev_beitr_regulär_beschäftigt
from gettsim.social_insurance.rentenv import rentenv_beitr_regular_job
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def lohnsteuer(
    bruttolohn_m: FloatSeries,
    vorsorgepauschale: FloatSeries,
    params: FloatSeries,
    steuerklasse: IntSeries,
    anz_kinder_tu: IntSeries,
    kinderlos: BoolSeries,
    alleinerziehend_freib_tu: IntSeries,
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
    grundfreibetrag = params["eink_st_tarif"]["G"]
    # Full child allowance
    kinderfreibetrag_basis = (
        params["eink_st_abzuege"]["sächl_existenzmin"]
        + params["eink_st_abzuege"]["beitr_erz_ausb"]
    )
    kinderfreibetrag = kinderfreibetrag_basis * 2 * steuerklasse.isin([1, 2, 3]) + (
        kinderfreibetrag_basis * steuerklasse == 4
    )
    lohnsteuer_freibetrag = (grundfreibetrag * steuerklasse.isin([1, 2, 4])) + (
        2 * grundfreibetrag * (steuerklasse == 3)
    )
    lohnsteuer_freibetrag += alleinerziehend_freib_tu * (steuerklasse == 2)
    werbungskosten = (params["eink_st_abzuege"]["werbung"]) * (steuerklasse != 6)
    sonderausgaben = (params["eink_st_abzuege"]["sonder"]) * steuerklasse != 6

    lohnsteuer_zve = (
        bruttolohn_m
        - werbungskosten
        - sonderausgaben
        - vorsorgepauschale(bruttolohn_m, steuerklasse, jahr_renteneintr, params)
    )

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


def vorsorgepauschale_ab_2010(
    bruttolohn: FLoatSeries,
    steuerklasse: IntSeries,
    jahr: IntSeries,
    params: dict,
    kinderlos: BoolSeries,
) -> FloatSeries:

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    vorsorg_rv = rentenv_beitr_regular_job(
        bruttolohn, params["soz_vers_beitr"]
    ) * vorsorg_rv_anteil(jahr, params["eink_st_abzuege"])
    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG
    vorsorg_kv = krankenv_beitr_regulär_beschäftigt(
        bruttolohn, params["soz_vers_beitr"]
    )
    # 3. Pflegeversicherungsbeiträge, §28b (2) Nr. 3c EStG
    vorsorg_pv = pflegev_beitr_regulär_beschäftigt(
        kinderlos, bruttolohn, params["soz_vers_beitr"]
    )
    # Wende Maximalbetrag an aus params["eink_st_abzuege"]["vorsorgepauschale_kv_max"] in Abh der Steuerklasse

    return out


def vorsorgepauschale_2005_2010(bruttolohn, steuerklasse, params) -> FloatSeries:

    out = 0
    return out


def vorsorg_rv_anteil(jahr: int, params: dict):
    """

    Parameters
    ----------
    jahr :
    params :

    Returns
    -------
    out: Float
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
