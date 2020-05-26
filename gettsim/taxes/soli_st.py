import numpy as np
import pandas as pd

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
        _st_kind_freib_tu.apply(
            piecewise_polynomial,
            lower_thresholds=soli_st_params["soli_st"]["lower_thresholds"],
            upper_thresholds=soli_st_params["soli_st"]["upper_thresholds"],
            rates=soli_st_params["soli_st"]["rates"],
            intercepts_at_lower_thresholds=soli_st_params["soli_st"][
                "intercepts_at_lower_thresholds"
            ],
        )
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_m_tu
    ) * (1 / 12)
    return out.rename("soli_st_m_tu")


def soli_st_m(soli_st_m_tu, gem_veranlagt, kind, tu_id):
    """
    Assign Soli to individuals. Kids get 0.

    Parameters
    ----------
    soli_st_m_tu
    gem_veranlagt
    kind
    tu_id

    Returns
    -------

    """
    out = np.select(
        [gem_veranlagt & ~kind, ~gem_veranlagt & ~kind, kind],
        [tu_id.replace(soli_st_m_tu) / 2, tu_id.replace(soli_st_m_tu), 0],
    )
    return pd.Series(data=out, index=tu_id.index, name="soli_st_m")
