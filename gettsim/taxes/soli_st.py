import numpy as np

from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def soli_st_tu(
    eink_st_kinderfreib_tu: FloatSeries,
    anz_erwachsene_tu: IntSeries,
    abgelt_st_tu: FloatSeries,
    soli_st_params: dict,
) -> FloatSeries:
    """Calculate the Solidarity Surcharge.

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
    eink_st_kinderfreib_tu
        See :func:`eink_st_kinderfreib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    abgelt_st_tu
        See :func:`abgelt_st_tu`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    eink_st_per_individual = eink_st_kinderfreib_tu / anz_erwachsene_tu
    out = (
        anz_erwachsene_tu * soli_tarif(eink_st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_tu
    )

    return out


def lohn_st_soli(
    lohn_st_kinderfreibetrag: FloatSeries, soli_st_params: dict
) -> FloatSeries:
    """
    Calculates the Solidarity Surcharge as a top-up on Lohnsteuer

    Parameters
    ----------
    lohn_st_kinderfreibetrag
    soli_st_params

    Returns
    -------

    """

    return soli_tarif(lohn_st_kinderfreibetrag, soli_st_params)


def lohn_st_zve_kifb(
    lohn_st_zve: FloatSeries, kinderfreibetrag_lohn_st: FloatSeries
) -> FloatSeries:
    """ Calculates tax base for Soli Lohnsteuer
    by subtracting child allowance from regular lohnsteuer taxable income
    """
    return np.maximum(lohn_st_zve - kinderfreibetrag_lohn_st, 0)


def kinderfreibetrag_lohn_st(
    tu_id: IntSeries,
    steuerklasse: IntSeries,
    anz_kindergeld_kinder_tu: FloatSeries,
    eink_st_abzuege_params,
) -> FloatSeries:
    """ Calculates Child Allowance for Lohnsteuer-Soli

    For the purpose of Soli on Lohnsteuer,
    the child allowance not only depends on the number of children,
    but also on the steuerklasse
    """

    kinderfreibetrag_basis = (
        eink_st_abzuege_params["kinderfreibetrag"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreibetrag"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    out = (
        (kinderfreibetrag_basis * 2 * steuerklasse.isin([1, 2, 3]))
        + (kinderfreibetrag_basis * steuerklasse == 4)
    ) * tu_id.replace(anz_kindergeld_kinder_tu)
    return out


def lohn_st_kinderfreibetrag(
    lohn_st_zve_kifb: FloatSeries, steuerklasse: IntSeries, eink_st_params: dict
) -> FloatSeries:
    """ Calculate Lohnsteuer just as lohn_st function,
    but with a different tax base, i.e. including child allowance
    """
    lohnsteuer_basistarif = _eink_st_tarif(lohn_st_zve_kifb, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(lohn_st_zve_kifb / 2, eink_st_params)
    lohnsteuer_klasse5_6 = np.maximum(
        2
        * (
            _eink_st_tarif(lohn_st_zve_kifb * 1.25, eink_st_params)
            - _eink_st_tarif(lohn_st_zve_kifb * 0.75, eink_st_params)
        ),
        lohn_st_zve_kifb * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    out = (
        (lohnsteuer_splittingtarif * (steuerklasse == 3))
        + (lohnsteuer_basistarif * (steuerklasse.isin([1, 2, 4])))
        + (lohnsteuer_klasse5_6 * (steuerklasse.isin([5, 6])))
    )
    return out


def soli_tarif(lohn_st: FloatSeries, soli_st_params: dict) -> FloatSeries:
    """
    The isolated function for Solidaritätszuschlag

    Parameters
    ----------
    lohn_st:
        the tax amount to be topped up
    soli_st_params :
        See params documentation :ref:`soli_st_params <solo_st_params>`
    Returns
        solidarity surcharge
    -------

    """

    return piecewise_polynomial(
        lohn_st,
        thresholds=soli_st_params["soli_st"]["thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )
