import numpy as np


def soli_st(tax_unit, params):
    """Solidarity Surcharge.

    Solidaritätszuschlaggesetz (SolZG) in 1991 and 1992.
    Solidaritätszuschlaggesetz 1995 (SolZG 1995) since 1995.

    The Solidarity Surcharge is an additional tax on top of the income tax which
    is the tax base. As opposed to the 'standard' income tax, child allowance is
    always deducted for tax base calculation.

    There is also Solidarity Surcharge on the Capital Income Tax, but always
    with Solidarity Surcharge tax rate and no tax exempt level. §3 (3) S.2
    SolzG 1995.
    """

    tax_unit["soli_tu"] = 0

    # Soli also in monthly terms. only for adults
    tax_unit.loc[~tax_unit["child"], "soli_tu"] = (
        params["soli_formula"](tax_unit["tax_kfb_tu"], params)
        + params["soli_rate"] * tax_unit["abgelt_st_tu"]
    ) * (1 / 12)

    # Assign Soli to individuals
    tax_unit["soli"] = np.select(
        [tax_unit["zveranl"], ~tax_unit["zveranl"]],
        [tax_unit["soli_tu"] / 2, tax_unit["soli_tu"]],
    )
    return tax_unit


def keine_soli_st(solibasis, params):
    """ There was no Solidaritätszuschlaggesetz before 1991 and in 1993/1994 """
    return 0


def soli_st_formel_1991_92(solibasis, params):
    """ Solidaritätszuschlaggesetz (SolZG) in 1991 and 1992 """

    soli = params["soli_rate"] * solibasis

    return soli.round(2)


def soli_st_formel_seit_1995(solibasis, params):
    """ Solidaritätszuschlaggesetz 1995 (SolZG 1995) since 1995 """

    soli = np.minimum(
        params["soli_rate"] * solibasis,
        np.maximum(
            params["soli_rate_max"] * (solibasis - params["soli_freigrenze"]), 0
        ),
    )

    return soli.round(2)
