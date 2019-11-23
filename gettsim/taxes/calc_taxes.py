import numpy as np
import pandas as pd


def tax_sched(tax_unit, e_st_data, e_st_abzuege_data, soli_st_data, abgelt_st_data):
    """Given various forms of income and other state variables, return
    the different taxes to be paid before making favourability checks etc..

    In particular

        * Income tax (Einkommensteuer)
        * Solidarity Surcharge (Solidaritätszuschlag)
        * Capital income tax (Abgeltungssteuer)

    """

    adult_married = (~tax_unit["child"]) & (tax_unit["zveranl"])

    for inc in e_st_abzuege_data["zve_list"]:
        # apply tax tariff, round to full Euro amounts
        tax_unit[f"tax_{inc}"] = e_st_data["tax_schedule"](
            tax_unit[f"zve_{inc}"], e_st_data
        ).astype(int)
        tax_unit[f"tax_{inc}_tu"] = tax_unit[f"tax_{inc}"]
        tax_unit.loc[adult_married, f"tax_{inc}_tu"] = tax_unit[f"tax_{inc}"][
            adult_married
        ].sum()

    # Abgeltungssteuer
    tax_unit["abgst"] = abgeltung(tax_unit, abgelt_st_data, e_st_abzuege_data)
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

    if e_st_abzuege_data["year"] >= 1991:
        # Soli also in monthly terms. only for adults
        tax_unit["soli_tu"] = (
            (
                soli_formula(tax_unit["tax_kfb_tu"], soli_st_data)
                + soli_st_data["solisatz"] * tax_unit["abgst_tu"]
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


def abgeltung(tax_unit, abgelt_st_data, e_st_abzuege_data):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    tax_unit_abgelt = pd.DataFrame(index=tax_unit.index.copy())
    tax_unit_abgelt["abgst"] = 0
    if abgelt_st_data["year"] >= 2009:
        tax_unit_abgelt.loc[~tax_unit["zveranl"], "abgst"] = abgelt_st_data[
            "abgst"
        ] * np.maximum(
            tax_unit["gross_e5"]
            - e_st_abzuege_data["spsparf"]
            - e_st_abzuege_data["spwerbz"],
            0,
        )
        tax_unit_abgelt.loc[tax_unit["zveranl"], "abgst"] = (
            0.5
            * abgelt_st_data["abgst"]
            * np.maximum(
                tax_unit["gross_e5_tu"]
                - 2 * (e_st_abzuege_data["spsparf"] + e_st_abzuege_data["spwerbz"]),
                0,
            )
        )
    return tax_unit_abgelt["abgst"].round(2)


@np.vectorize
def tarif(x, e_st_data):
    """ The German Income Tax Tariff
    modelled only after 2002 so far

    It's not calculated as in the tax code, but rather a gemoetric decomposition of the
    area beneath the marginal tax rate function.
    This facilitates the implementation of alternative tax schedules

    args:
        x (float): taxable income
        tb (dict): tax-benefit parameters specific to year and reform
    """

    if e_st_data["year"] < 2002:
        raise ValueError("Income Tax Pre 2002 not yet modelled!")
    else:
        t = 0.0
        if e_st_data["G"] < x <= e_st_data["M"]:
            t = (
                (
                    (e_st_data["t_m"] - e_st_data["t_e"])
                    / (2 * (e_st_data["M"] - e_st_data["G"]))
                )
                * (x - e_st_data["G"])
                + e_st_data["t_e"]
            ) * (x - e_st_data["G"])
        elif e_st_data["M"] < x <= e_st_data["S"]:
            t = (
                (
                    (e_st_data["t_s"] - e_st_data["t_m"])
                    / (2 * (e_st_data["S"] - e_st_data["M"]))
                )
                * (x - e_st_data["M"])
                + e_st_data["t_m"]
            ) * (x - e_st_data["M"]) + (e_st_data["M"] - e_st_data["G"]) * (
                (e_st_data["t_m"] + e_st_data["t_e"]) / 2
            )
        elif x > e_st_data["S"]:
            t = (
                e_st_data["t_s"] * x
                - e_st_data["t_s"] * e_st_data["S"]
                + ((e_st_data["t_s"] + e_st_data["t_m"]) / 2)
                * (e_st_data["S"] - e_st_data["M"])
                + ((e_st_data["t_m"] + e_st_data["t_e"]) / 2)
                * (e_st_data["M"] - e_st_data["G"])
            )
        if x > e_st_data["R"]:
            t = t + (e_st_data["t_r"] - e_st_data["t_s"]) * (x - e_st_data["R"])
        assert t >= 0
    return t


def soli_formula(solibasis, tb):
    """ The actual soli calculation

    args:
        solibasis: taxable income, *always with Kinderfreibetrag!*
        tb (dict): tax-benefit parameters

    """
    soli = np.minimum(
        tb["solisatz"] * solibasis,
        np.maximum(0.2 * (solibasis - tb["solifreigrenze"]), 0),
    )

    return soli.round(2)
