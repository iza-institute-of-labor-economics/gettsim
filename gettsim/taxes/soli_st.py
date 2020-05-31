from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def soli_st_m_tu(_st_kind_freib_tu, abgelt_st_m_tu, soli_st_params):
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

    out = (
        piecewise_polynomial(
            _st_kind_freib_tu,
            thresholds=soli_st_params["soli_st"]["thresholds"],
            rates=soli_st_params["soli_st"]["rates"],
            intercepts_at_lower_thresholds=soli_st_params["soli_st"][
                "intercepts_at_lower_thresholds"
            ],
        )
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_m_tu
    ) * (1 / 12)
    return out


def soli_st_m(soli_st_m_tu, gemeinsam_veranlagt, kind, tu_id):
    """Assign Soli to individuals. Kids get 0.

    Parameters
    ----------
    soli_st_m_tu
    gemeinsam_veranlagt
    kind
    tu_id

    Returns
    -------

    """
    # First assign all individuals the tax unit value
    out = tu_id.replace(soli_st_m_tu)
    # Half it for married couples
    out.loc[gemeinsam_veranlagt] /= 2
    # Set it to zero for kids
    out.loc[kind] = 0
    return out
