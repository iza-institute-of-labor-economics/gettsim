"""Tax allowances for the disabled."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.functions.policy_function import policy_function


@policy_function
def pauschbetrag_behinderung_y(
    behinderungsgrad: int, eink_st_abzuege_params: dict
) -> float:
    """Assign tax deduction allowance for handicaped to different handicap degrees.

    Parameters
    ----------
    behinderungsgrad
        See basic input variable :ref:`behinderungsgrad <behinderungsgrad>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    # Get disability degree thresholds
    bins = sorted(eink_st_abzuege_params["behinderten_pauschbetrag"])

    # Select corresponding bin.
    selected_bin_index = (
        np.searchsorted(np.asarray([*bins, np.inf]), behinderungsgrad, side="right") - 1
    )
    selected_bin = bins[selected_bin_index]

    # Select appropriate pauschbetrag.
    out = eink_st_abzuege_params["behinderten_pauschbetrag"][selected_bin]

    return float(out)
