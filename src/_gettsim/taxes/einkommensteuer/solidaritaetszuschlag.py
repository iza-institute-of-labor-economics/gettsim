"""Solidarity Surcharge (Solidaritätszuschlag)."""

from _gettsim.functions.policy_function import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function(end_date="2008-12-31", name_in_dag="betrag_y_sn")
def betrag_y_sn_ohne_abgelt_st(
    taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn: float,
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
    taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn
        See :func:`taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = (
        taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn / anz_personen_sn
    )
    out = anz_personen_sn * solidaritaetszuschlag_tarif(
        eink_st_per_individual, soli_st_params
    )

    return out


@policy_function(start_date="2009-01-01", name_in_dag="betrag_y_sn")
def betrag_y_sn_mit_abgelt_st(
    taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn: float,
    anz_personen_sn: int,
    abgeltungssteuer__betrag_y_sn: float,
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
    taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn
        See :func:`taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    abgeltungssteuer__betrag_y_sn
        See :func:`abgeltungssteuer__betrag_y_sn`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = (
        taxes__einkommensteuer__betrag_mit_kinderfreib_y_sn / anz_personen_sn
    )
    out = (
        anz_personen_sn
        * solidaritaetszuschlag_tarif(eink_st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgeltungssteuer__betrag_y_sn
    )

    return out


def solidaritaetszuschlag_tarif(
    st_per_individual: float, soli_st_params: dict
) -> float:
    """The isolated function for Solidaritätszuschlag.

    Parameters
    ----------
    st_per_individual:
        the tax amount to be topped up
    soli_st_params
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
