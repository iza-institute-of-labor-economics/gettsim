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
    kind: BoolSeries,
    steuerklasse: IntSeries,
    pflegev_zusatz_kinderlos: BoolSeries,
    eink_st_params: dict,
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

    grundfreibetrag = eink_st_params["eink_st_tarif"]["thresholds"][1]
    # Full child allowance
    kinderfreibetrag_basis = (
        eink_st_params["kinderfreibetrag"]["sächl_existenzmin"]
        + eink_st_params["kinderfreibetrag"]["beitr_erz_ausb"]
    )
    k
    # For certain tax brackets, twice the child allowance can be deducted
    kinderfreibetrag = kinderfreibetrag_basis * 2 * steuerklasse.isin([1, 2, 3]) + (
        kinderfreibetrag_basis * steuerklasse == 4
    ) * anz_minderj_hh
    lohn_steuer_freibetrag = (grundfreibetrag * steuerklasse.isin([1, 2, 4])) + (
        2 * grundfreibetrag * (steuerklasse == 3)
    )
    lohn_steuer_freibetrag += alleinerziehend_freib_tu * (steuerklasse == 2)
    werbungskosten = (eink_st_params["werbung"]) * (steuerklasse != 6)
    sonderausgaben = (eink_st_params["sonder"]) * steuerklasse != 6

    vorsorgepauschale = vorsorgepauschale(
        bruttolohn_m,
        steuerklasse,
        soz_vers_beitr_params,
        eink_st_abzuege_params,
        pflegev_zusatz_kinderlos,
    )
    # zu versteuerndes Einkommen / tax base for Lohnsteuer
    lohn_steuer_zve = (bruttolohn_m -
                       werbungskosten - sonderausgaben - vorsorgepauschale
                       )
    # TODO: Wie werden die richtigen Freibeträge berücksichtigt?
    lohn_steuer = lohn_steuer_zve.apply(st_tarif, params=eink_st_params)

    return lohn_steuer


def vorsorgepauschale_ab_2010(
    bruttolohn_m: FloatSeries,
    steuerklasse: IntSeries,
    soz_vers_beitr_params: dict,
    eink_st_abzuege_params: dict,
    pflegev_zusatz_kinderlos: BoolSeries,
) -> FloatSeries:
    """
    Calculates Vorsorgepauschale for Lohnsteuer valid since 2010

    Parameters
    ----------
    bruttolohn_m
    steuerklasse
    soz_vers_beitr_params
    eink_st_abzuege_params
    pflegev_zusatz_kinderlos

    Returns
    -------

    """
    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    vorsorg_rv = rentenv_beitr_regular_job(
        bruttolohn_m, soz_vers_beitr_params
    ) * vorsorg_rv_anteil(soz_vers_beitr_params["datum"].year, eink_st_abzuege_params)
    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate.
    # a) at least 12% of earnings of earnings can be deducted, but only up to a certain threshold
    vorsorg_kv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"] * bruttolohn_m
    )

    vorsorg_kv_option_a_max = np.select(
        [steuerklasse == 3, steuerklasse != 3],
        [
            eink_st_abzuege_params["vorsorgepauschale_kv_max"]["stkl3"],
            eink_st_abzuege_params["vorsorgepauschale_kv_max"]["stkl_nicht3"],
        ],
    )
    vorsorg_kv_option_a = np.minimum(vorsorg_kv_option_a_max, vorsorg_kv_option_a_basis)
    # b) Take the actual contribtutions (usually the better option)
    vorsorg_kv_option_b = krankenv_beitr_regulär_beschäftigt(
        bruttolohn_m, soz_vers_beitr_params
    )
    vorsorg_kv_option_b += pflegev_beitr_regulär_beschäftigt(
        pflegev_zusatz_kinderlos, bruttolohn_m, soz_vers_beitr_params
    )
    # add both RV and KV deductions
    out = vorsorg_rv + np.maximum(vorsorg_kv_option_a, vorsorg_kv_option_b)

    return out


def vorsorgepauschale_2005_2010(bruttolohn, steuerklasse, params) -> FloatSeries:
    out = 0
    return out


def vorsorg_rv_anteil(jahr: int, eink_st_params: dict) -> FloatSeries:
    """
    Calculates the share of pension contributions to be deducted for Lohnsteuer
    increases by year

    Parameters
    ----------
    jahr:
        year of simulation date
    params:
        eink_st_params


    Returns
    -------
    out: float
    """

    out = piecewise_polynomial(
        x=eink_st_params["datum"].year,
        thresholds=eink_st_params["vorsorge_pauschale_rv_anteil"]["thresholds"],
        rates=eink_st_params["vorsorge_pauschale_rv_anteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_params["vorsorge_pauschale_rv_anteil"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return out
