"""Tax allowances for single parents."""

from _gettsim.function_types import policy_function


@policy_function(end_date="2014-12-31", leaf_name="alleinerziehend_betrag_y")
def alleinerziehend_betrag_y_pauschal(
    einkommensteuer__alleinerziehend_sn: bool, eink_st_abzuege_params: dict
) -> float:
    """Calculate tax deduction allowance for single parents until 2014.

    This used to be called 'Haushaltsfreibetrag'.

    Parameters
    ----------
    einkommensteuer__alleinerziehend_sn
        See :func:`einkommensteuer__alleinerziehend_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    if einkommensteuer__alleinerziehend_sn:
        out = eink_st_abzuege_params["alleinerziehendenfreibetrag"]
    else:
        out = 0.0

    return out


@policy_function(start_date="2015-01-01", leaf_name="alleinerziehend_betrag_y")
def alleinerziehend_betrag_y_nach_kinderzahl(
    einkommensteuer__alleinerziehend_sn: bool,
    kindergeld__anzahl_ansprüche_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for single parents since 2015.

    Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'

    Parameters
    ----------
    einkommensteuer__alleinerziehend_sn
        See :func:`einkommensteuer__alleinerziehend_sn`.
    kindergeld__anzahl_ansprüche_sn
        See :func:`kindergeld__anzahl_ansprüche_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    betrag_y = (
        eink_st_abzuege_params["alleinerziehendenfreibetrag"]
        + (kindergeld__anzahl_ansprüche_sn - 1)
        * eink_st_abzuege_params["alleinerziehendenfreibetrag_zusatz"]
    )
    if einkommensteuer__alleinerziehend_sn:
        out = betrag_y
    else:
        out = 0.0

    return out
