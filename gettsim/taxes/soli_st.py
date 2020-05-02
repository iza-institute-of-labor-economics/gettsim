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

    tax_unit["soli_st_m_tu"] = 0
    import pdb

    pdb.set_trace()
    # Soli also in monthly terms. only for adults
    tax_unit.loc[~tax_unit["kind"], "soli_st_m_tu"] = (
        params["soli_formula"](tax_unit["_st_kind_freib_tu"], params)
        + params["soli_rate"] * tax_unit["abgelt_st_m_tu"]
    ) * (1 / 12)

    # Assign Soli to individuals
    tax_unit["soli_st_m"] = np.select(
        [tax_unit["gem_veranlagt"], ~tax_unit["gem_veranlagt"]],
        [tax_unit["soli_st_m_tu"] / 2, tax_unit["soli_st_m_tu"]],
    )
    return tax_unit


def get_uebergangs_threholds(soli_st_satz, soli_st_uebergang, freigrenze):
    """
    This function calculates the upper threshold for interval 1 for the piecewise
    function in soli_st.yaml.  Interval 1 is used to moderate the start of soli
    taxation. It uses the three parameters actually given in the law.
    """
    threshold = freigrenze / (1 - soli_st_satz / soli_st_uebergang)
    return threshold
