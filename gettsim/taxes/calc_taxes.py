import numpy as np
import pandas as pd


def tax_sched(
    tax_unit, e_st_params, e_st_abzuege_params, soli_st_params, abgelt_st_params
):
    """Given various forms of income and other state variables, return
    the different taxes to be paid before making favourability checks etc..

    In particular

        * Income tax (Einkommensteuer)
        * Solidarity Surcharge (Solidaritätszuschlag)
        * Capital income tax (Abgeltungssteuer)

    """

    adult_married = (~tax_unit["child"]) & (tax_unit["zveranl"])

    for inc in e_st_abzuege_params["zve_list"]:
        # apply tax tariff, round to full Euro amounts
        tax_unit[f"tax_{inc}"] = e_st_params["tax_schedule"](
            tax_unit[f"zve_{inc}"], e_st_params
        ).astype(int)
        tax_unit[f"tax_{inc}_tu"] = tax_unit[f"tax_{inc}"]
        tax_unit.loc[adult_married, f"tax_{inc}_tu"] = tax_unit[f"tax_{inc}"][
            adult_married
        ].sum()

    tax_unit["lohnsteuer"] = lohnsteuer(tax_unit, e_st_params)

    # Abgeltungssteuer
    tax_unit["abgst"] = abgeltung(tax_unit, abgelt_st_params, e_st_abzuege_params)
    tax_unit["abgst_tu"] = tax_unit["abgst"]
    tax_unit.loc[adult_married, "abgst_tu"] = tax_unit["abgst"][adult_married].sum()

    """Solidarity Surcharge. on top of the income tax.
    No Soli if income tax due is below € 920 (solifreigrenze)
    Then it increases with 0.2 marginal rate until 5.5% (solisatz)
    of the incometax is reached.
    As opposed to the 'standard' income tax,
    child allowance is always deducted for soli calculation
    There is also Soli on capital income tax, but always with 5.5%. (§3 (3) S.2 SolzG 1995)
    """

    if e_st_abzuege_params["year"] >= 1991:
        # Soli also in monthly terms. only for adults
        tax_unit["soli_tu"] = (
            (
                soli_formula(tax_unit["tax_kfb_tu"], soli_st_params)
                + soli_st_params["solisatz"] * tax_unit["abgst_tu"]
            )
            * ~tax_unit["child"]
            * (1 / 12)
        )
    else:
        tax_unit["soli_tu"] = 0

    # Assign Soli to individuals
    tax_unit["soli"] = np.select(
        [tax_unit["zveranl"], ~tax_unit["zveranl"]],
        [tax_unit["soli_tu"] / 2, tax_unit["soli_tu"]],
    )
    return tax_unit


def abgeltung(tax_unit, e_st_params, e_st_abzuege_params):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    tax_unit_abgelt = pd.DataFrame(index=tax_unit.index.copy())
    tax_unit_abgelt["abgst"] = 0
    if e_st_params["year"] >= 2009:
        tax_unit_abgelt.loc[~tax_unit["zveranl"], "abgst"] = e_st_params[
            "abgst"
        ] * np.maximum(
            tax_unit["gross_e5"]
            - e_st_abzuege_params["spsparf"]
            - e_st_abzuege_params["spwerbz"],
            0,
        )
        tax_unit_abgelt.loc[tax_unit["zveranl"], "abgst"] = (
            0.5
            * e_st_params["abgst"]
            * np.maximum(
                tax_unit["gross_e5_tu"]
                - 2 * (e_st_abzuege_params["spsparf"] + e_st_abzuege_params["spwerbz"]),
                0,
            )
        )
    return tax_unit_abgelt["abgst"].round(2)


@np.vectorize
def tarif(x, params):
    """ The German Income Tax Tariff
    modelled only after 2002 so far

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (float): taxable income
        tb (dict): tax-benefit parameters specific to year and reform
    """

    if params["year"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    else:
        t = 0.0
        if params["G"] < x <= params["M"]:
            t = (
                ((params["t_m"] - params["t_e"]) / (2 * (params["M"] - params["G"])))
                * (x - params["G"])
                + params["t_e"]
            ) * (x - params["G"])
        elif params["M"] < x <= params["S"]:
            t = (
                ((params["t_s"] - params["t_m"]) / (2 * (params["S"] - params["M"])))
                * (x - params["M"])
                + params["t_m"]
            ) * (x - params["M"]) + (params["M"] - params["G"]) * (
                (params["t_m"] + params["t_e"]) / 2
            )
        elif x > params["S"]:
            t = (
                params["t_s"] * x
                - params["t_s"] * params["S"]
                + ((params["t_s"] + params["t_m"]) / 2) * (params["S"] - params["M"])
                + ((params["t_m"] + params["t_e"]) / 2) * (params["M"] - params["G"])
            )
        if x > params["R"]:
            t = t + (params["t_r"] - params["t_s"]) * (x - params["R"])
        assert t >= 0
    return t


def soli_formula(solibasis, params):
    """ The actual soli calculation

    args:
        solibasis: taxable income, *always with Kinderfreibetrag!*
        tb (dict): tax-benefit parameters

    """
    soli = np.minimum(
        params["solisatz"] * solibasis,
        np.maximum(0.2 * (solibasis - params["solifreigrenze"]), 0),
    )

    return soli.round(2)


def lohnsteuer(tax_unit, e_st_params):
    """ Calculates Lohnsteuer = withholding tax on earnings, paid monthly by the employer.

        Apply the income tax tariff, but individually and with different exemptions,
        determined by the 'Steuerklasse'
    """
    # Steuerklasse 1 gets the basic exemption. Default value. Also holds for Steuerklasse 4
    tax_unit["lohnsteuer_abzüge"] = e_st_params["G"]
    # Steuerklasse 2 for single parents.
    tax_unit.loc[tax_unit["e_st_klasse"] == 2, "lohnsteuer_abzüge"] = (
        e_st_params["G"] + e_st_params["hhfreib"]
    )
    # Steuerklasse 3: married. get twice the basic exemption
    tax_unit.loc[tax_unit["e_st_klasse"] == 3, "lohnsteuer_abzüge"] = (
        2 * e_st_params["G"]
    )
    # Steuerklasse 5: married and if partner has klasse 3. No exemption
    tax_unit.loc[tax_unit["e_st_klasse"] == 5, "lohnsteuer_abzüge"] = 0

    tax_unit.loc[tax_unit["e_st_klasse"] != 6, "lohnsteuer_abzüge"] += (
        e_st_params["werbung"]
        + e_st_params["sonder"]
        + calc_vorsorgepauschale(tax_unit)
    )
    tax_unit["lohnsteuer_inc"] = tax_unit["m_wage"] * 12 - tax_unit["lohnsteuer_abzüge"]
    tax_unit["lohnsteuer"] = tax_unit["y_wage"].apply(tarif)

    return tax_unit["lohnsteuer"]


def calc_vorsorgepauschale(tax_unit):
    return 0.0
