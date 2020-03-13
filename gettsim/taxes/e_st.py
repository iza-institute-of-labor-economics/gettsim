import numpy as np

from gettsim.taxes.abgelt_st import abgelt_st
from gettsim.taxes.soli_st import soli_st


def e_st(tax_unit, e_st_params, e_st_abzuege_params, soli_st_params, abgelt_st_params):
    """Given various forms of income and other state variables, return
    the different taxes to be paid before making favourability checks etc..

    In particular

        * Income tax (Einkommensteuer)
        * Solidarity Surcharge (Solidaritätszuschlag)
        * Capital income tax (Abgeltungssteuer)

    """

    adult_married = (~tax_unit["kind"]) & (tax_unit["gem_veranlagt"])

    for inc in e_st_abzuege_params["eink_arten"]:
        # apply tax tariff, round to full Euro amounts
        tax_unit[f"_st_{inc}"] = e_st_params["st_tarif"](
            tax_unit[f"_zu_versteuerndes_eink_{inc}"], e_st_params
        ).astype(int)
        tax_unit[f"_st_{inc}_tu"] = tax_unit[f"_st_{inc}"]
        tax_unit.loc[adult_married, f"_st_{inc}_tu"] = tax_unit[f"_st_{inc}"][
            adult_married
        ].sum()

    # Abgeltungssteuer
    tax_unit = abgelt_st(tax_unit, abgelt_st_params, e_st_abzuege_params)
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
        tb (dict): tax-benefit parameters specific to year and reform
    """

    if params["jahr"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    else:
        eink_steuer = 0.0
        if params["G"] < x <= params["M"]:
            eink_steuer = (
                ((params["t_m"] - params["t_e"]) / (2 * (params["M"] - params["G"])))
                * (x - params["G"])
                + params["t_e"]
            ) * (x - params["G"])
        elif params["M"] < x <= params["S"]:
            eink_steuer = (
                ((params["t_s"] - params["t_m"]) / (2 * (params["S"] - params["M"])))
                * (x - params["M"])
                + params["t_m"]
            ) * (x - params["M"]) + (params["M"] - params["G"]) * (
                (params["t_m"] + params["t_e"]) / 2
            )
        elif x > params["S"]:
            eink_steuer = (
                params["t_s"] * x
                - params["t_s"] * params["S"]
                + ((params["t_s"] + params["t_m"]) / 2) * (params["S"] - params["M"])
                + ((params["t_m"] + params["t_e"]) / 2) * (params["M"] - params["G"])
            )
        if x > params["R"]:
            eink_steuer = eink_steuer + (params["t_r"] - params["t_s"]) * (
                x - params["R"]
            )
        assert eink_steuer >= 0
    return eink_steuer
