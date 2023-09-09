from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


@dates_active(end="2008-12-31", change_name="soli_st_y_tu")
def soli_st_y_tu_ohne_abgelt_st(
    eink_st_mit_kinderfreib_y_tu: float,
    anz_erwachsene_tu: int,
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
    eink_st_mit_kinderfreib_y_tu
        See :func:`eink_st_mit_kinderfreib_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_mit_kinderfreib_y_tu / anz_erwachsene_tu
    out = anz_erwachsene_tu * _soli_st_tarif(eink_st_per_individual, soli_st_params)

    return out


@dates_active(start="2009-01-01", change_name="soli_st_y_tu")
def soli_st_y_tu_mit_abgelt_st(
    eink_st_mit_kinderfreib_y_tu: float,
    anz_personen_tu: int,
    abgelt_st_y_tu: float,
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
    eink_st_mit_kinderfreib_y_tu
        See :func:`eink_st_mit_kinderfreib_y_tu`.
    anz_personen_tu
        See :func:`anz_personen_tu`.
    abgelt_st_y_tu
        See :func:`abgelt_st_y_tu`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_mit_kinderfreib_y_tu / anz_personen_tu
    out = (
        anz_personen_tu * _soli_st_tarif(eink_st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_y_tu
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
