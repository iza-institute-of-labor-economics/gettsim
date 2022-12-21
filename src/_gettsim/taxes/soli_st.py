from _gettsim.piecewise_functions import piecewise_polynomial


def soli_st_tu(
    eink_st_mit_kinderfreib_tu: float,
    anz_erwachsene_tu: int,
    abgelt_st_tu: float,
    soli_st_params: dict,
) -> float:
    """Calculate the Solidarity Surcharge on tax unit level.

    Solidaritätszuschlaggesetz (SolZG) in 1991 and 1992.
    Solidaritätszuschlaggesetz 1995 (SolZG 1995) since 1995.

    The Solidarity Surcharge is an additional tax on top of the income tax which
    is the tax base. As opposed to the 'standard' income tax, child allowance is
    always deducted for tax base calculation.

    There is also Solidarity Surcharge on the Capital Income Tax, but always
    with Solidarity Surcharge tax rate and no tax exempt level. §3 (3) S.2
    SolzG 1995.

    Parameters
    ----------
    eink_st_mit_kinderfreib_tu
        See :func:`eink_st_mit_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    abgelt_st_tu
        See :func:`abgelt_st_tu`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_mit_kinderfreib_tu / anz_erwachsene_tu
    out = (
        anz_erwachsene_tu
        * piecewise_polynomial(
            eink_st_per_individual,
            thresholds=soli_st_params["soli_st"]["thresholds"],
            rates=soli_st_params["soli_st"]["rates"],
            intercepts_at_lower_thresholds=soli_st_params["soli_st"][
                "intercepts_at_lower_thresholds"
            ],
        )
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_tu
    )

    return out
