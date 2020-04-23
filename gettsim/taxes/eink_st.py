import numpy as np

from gettsim.pre_processing.piecewise_functions import piecewise_polynominal
from gettsim.taxes.abgelt_st import abgelt_st
from gettsim.taxes.soli_st import soli_st


def eink_st(
    tax_unit, eink_st_params, eink_st_abzuege_params, soli_st_params, abgelt_st_params
):
    """Given various forms of income and other state variables, return
    the different taxes to be paid before making favourability checks etc..

    In particular

        * Income tax (Einkommensteuer)
        * Solidarity Surcharge (Solidaritätszuschlag)
        * Capital income tax (Abgeltungssteuer)

    """
    if eink_st_params["jahr"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")

    adult_married = (~tax_unit["kind"]) & (tax_unit["gem_veranlagt"])

    for inc in eink_st_abzuege_params["eink_arten"]:
        # apply tax tariff, round to full Euro amounts
        tax_unit[f"_st_{inc}"] = st_tarif(
            tax_unit[f"_zu_versteuerndes_eink_{inc}"], eink_st_params
        ).astype(int)
        tax_unit[f"_st_{inc}_tu"] = tax_unit[f"_st_{inc}"]
        tax_unit.loc[adult_married, f"_st_{inc}_tu"] = tax_unit[f"_st_{inc}"][
            adult_married
        ].sum()

    # Abgeltungssteuer
    tax_unit = abgelt_st(tax_unit, abgelt_st_params, eink_st_abzuege_params)
    tax_unit["abgelt_st_m_tu"] = tax_unit["abgelt_st_m"]
    tax_unit.loc[adult_married, "abgelt_st_m_tu"] = tax_unit["abgelt_st_m"][
        adult_married
    ].sum()

    tax_unit = soli_st(tax_unit, soli_st_params)

    return tax_unit


@np.vectorize
def st_tarif(x, params):
    """ The German Income Tax Tariff
    modelled only after 2002 so far

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (float): taxable income
        params (dict): tax-benefit parameters specific to year and reform
    """

    eink_st = piecewise_polynominal(
        x,
        lower_thresholds=params["eink_st_tarif"]["lower_thresholds"],
        upper_thresholds=params["eink_st_tarif"]["upper_thresholds"],
        rates=params["eink_st_tarif"]["rates"],
        intercepts_at_lower_thresholds=params["eink_st_tarif"][
            "intercepts_at_lower_thresholds"
        ],
    )
    return eink_st
