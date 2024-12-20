"""Tax allowances for single parents."""

from _gettsim.shared import policy_info


@policy_info(end_date="2014-12-31", name_in_dag="alleinerz_freib_y_sn")
def eink_st_alleinerz_freib_y_sn_pauschal(
    alleinerz_sn: bool, eink_st_abzuege_params: dict
) -> float:
    """Calculate tax deduction allowance for single parents until 2014.

    This used to be called 'Haushaltsfreibetrag'.

    Parameters
    ----------
    alleinerz_sn
        See :func:`alleinerz_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    if alleinerz_sn:
        out = eink_st_abzuege_params["alleinerz_freibetrag"]
    else:
        out = 0.0

    return out


@policy_info(start_date="2015-01-01", name_in_dag="alleinerz_freib_y_sn")
def eink_st_alleinerz_freib_y_sn_nach_kinderzahl(
    alleinerz_sn: bool,
    kindergeld_anz_ansprüche_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015.

    Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    alleinerz_sn
        See :func:`alleinerz_sn`.
    kindergeld_anz_ansprüche_sn
        See :func:`kindergeld_anz_ansprüche_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    alleinerz_freib_y_sn = (
        eink_st_abzuege_params["alleinerz_freibetrag"]
        + (kindergeld_anz_ansprüche_sn - 1)
        * eink_st_abzuege_params["alleinerz_freibetrag_zusatz"]
    )
    if alleinerz_sn:
        out = alleinerz_freib_y_sn
    else:
        out = 0.0

    return out
