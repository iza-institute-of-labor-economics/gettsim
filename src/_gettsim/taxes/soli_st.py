from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.eink_st import _eink_st_tarif


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
        anz_erwachsene_tu * _soli_tarif(eink_st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_tu
    )

    return out


def lohn_st_soli_m(lohn_st_kinderfreibetrag: float, soli_st_params: dict) -> float:
    """Calculates the Solidarity Surcharge as a top-up on Lohnsteuer.

    Parameters
    ----------
    lohn_st_kinderfreibetrag
    soli_st_params

    Returns
    -------

    """

    return _soli_tarif(lohn_st_kinderfreibetrag, soli_st_params)


def lohn_st_eink_kifb(lohn_st_eink: float, kinderfreibetrag_lohn_st: float) -> float:
    """Calculates tax base for Soli Lohnsteuer by subtracting child allowance from
    regular lohnsteuer taxable income."""
    return max(lohn_st_eink - kinderfreibetrag_lohn_st, 0)


def kinderfreibetrag_lohn_st(
    steuerklasse: int,
    anz_kinder_mit_kindergeld_tu: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculates Child Allowance for Lohnsteuer-Soli.

    For the purpose of Soli on Lohnsteuer, the child allowance not only depends on the
    number of children, but also on the steuerklasse

    """

    kinderfreibetrag_basis = (
        eink_st_abzuege_params["kinderfreibetrag"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreibetrag"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    if steuerklasse == 1 | steuerklasse == 2 | steuerklasse == 3:
        out = kinderfreibetrag_basis * 2 * anz_kinder_mit_kindergeld_tu
    elif steuerklasse == 4:
        out = kinderfreibetrag_basis * anz_kinder_mit_kindergeld_tu
    else:
        out = 0
    return out


def lohn_st_kinderfreibetrag(
    lohn_st_eink_kifb: float, steuerklasse: int, eink_st_params: dict
) -> float:
    """Calculate Lohnsteuer just as lohn_st function, but with a different tax base,
    i.e. including child allowance."""
    lohnsteuer_basistarif = _eink_st_tarif(lohn_st_eink_kifb, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(
        lohn_st_eink_kifb / 2, eink_st_params
    )
    lohnsteuer_klasse5_6 = max(
        2
        * (
            _eink_st_tarif(lohn_st_eink_kifb * 1.25, eink_st_params)
            - _eink_st_tarif(lohn_st_eink_kifb * 0.75, eink_st_params)
        ),
        lohn_st_eink_kifb * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    if steuerklasse in (1, 2, 4):
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    return out


def _soli_tarif(st_per_individual: float, soli_st_params: dict) -> float:
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
