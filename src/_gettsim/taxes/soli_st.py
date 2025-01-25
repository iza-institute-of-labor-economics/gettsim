from _gettsim.functions.policy_function import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function(end_date="2008-12-31", leaf_name="soli_st_y_sn")
def soli_st_y_sn_ohne_abgelt_st(
    eink_st_mit_kinderfreib_y_sn: float,
    anz_personen_sn: int,
    soli_st_params: dict,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level.

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
    eink_st_mit_kinderfreib_y_sn
        See :func:`eink_st_mit_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_mit_kinderfreib_y_sn / anz_personen_sn
    out = anz_personen_sn * _soli_st_tarif(eink_st_per_individual, soli_st_params)

    return out


@policy_function(start_date="2009-01-01", leaf_name="soli_st_y_sn")
def soli_st_y_sn_mit_abgelt_st(
    eink_st_mit_kinderfreib_y_sn: float,
    anz_personen_sn: int,
    abgelt_st_y_sn: float,
    soli_st_params: dict,
) -> float:
    """Calculate the Solidarity Surcharge on Steuernummer level.

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
    eink_st_mit_kinderfreib_y_sn
        See :func:`eink_st_mit_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    abgelt_st_y_sn
        See :func:`abgelt_st_y_sn`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_mit_kinderfreib_y_sn / anz_personen_sn
    out = (
        anz_personen_sn * _soli_st_tarif(eink_st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_y_sn
    )

    return out


def soli_st_lohnst_m(lohnst_mit_kinderfreib_m: float, soli_st_params: dict) -> float:
    """Calculates the monthly Solidarity Surcharge on Lohnsteuer
    (withholding tax on earnings).

    Parameters
    ----------
    lohnst_mit_kinderfreib_m
        See :func:`lohnst_mit_kinderfreib_m`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
        Solidarity Surcharge on Lohnsteuer
    -------

    """

    return _soli_st_tarif(12 * lohnst_mit_kinderfreib_m, soli_st_params) / 12


def _soli_st_tarif(st_per_individual: float, soli_st_params: dict) -> float:
    """The isolated function for Solidaritätszuschlag.

    Parameters
    ----------
    st_per_individual:
        the tax amount to be topped up
    soli_st_params :
        See params documentation :ref:`soli_st_params <solo_st_params>`
    Returns
        solidarity surcharge
    -------

    """

    out = piecewise_polynomial(
        st_per_individual,
        thresholds=soli_st_params["soli_st"]["thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return out
