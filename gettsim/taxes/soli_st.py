from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def soli_st_tu(_st_kind_freib_tu, _anz_erwachsene_tu, abgelt_st_tu, soli_st_params):
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
    st_per_individual = _st_kind_freib_tu / _anz_erwachsene_tu
    out = (
        _anz_erwachsene_tu
        * piecewise_polynomial(
            st_per_individual,
            thresholds=soli_st_params["soli_st"]["thresholds"],
            rates=soli_st_params["soli_st"]["rates"],
            intercepts_at_lower_thresholds=soli_st_params["soli_st"][
                "intercepts_at_lower_thresholds"
            ],
        )
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_tu
    )

    return out
