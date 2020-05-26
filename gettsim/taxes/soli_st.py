import numpy as np

from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


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

    # Soli also in monthly terms. only for adults
    tax_unit.loc[~tax_unit["kind"], "soli_st_m_tu"] = (
        tax_unit["_st_kind_freib_tu"].apply(
            piecewise_polynomial,
            lower_thresholds=params["soli_st"]["lower_thresholds"],
            upper_thresholds=params["soli_st"]["upper_thresholds"],
            rates=params["soli_st"]["rates"],
            intercepts_at_lower_thresholds=params["soli_st"][
                "intercepts_at_lower_thresholds"
            ],
        )
        + params["soli_st"]["rates"][0, -1] * tax_unit["abgelt_st_m_tu"]
    ) * (1 / 12)

    # Assign Soli to individuals
    tax_unit["soli_st_m"] = np.select(
        [tax_unit["gem_veranlagt"], ~tax_unit["gem_veranlagt"]],
        [tax_unit["soli_st_m_tu"] / 2, tax_unit["soli_st_m_tu"]],
    )
    return tax_unit


def transition_threshold(soli_st_satz, soli_st_uebergang, freigrenze):
    """
    This function calculates the upper threshold for interval 1 for the piecewise
    function in soli_st.yaml.  Interval 1 is used to moderate the start of soli
    taxation. From this threshold om, the regular soli rate("soli_st_satz") is
    applied to the basis of soli calculation. Before the transition rate (
    "soli_st_uebergang") is applied to the difference of basis and "freigrenze". It
    uses the three parameters actually given in the law.
    """
    threshold = freigrenze / (1 - soli_st_satz / soli_st_uebergang)
    return threshold
