from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def soli_st_tu(
    st_kind_freib_tu: FloatSeries,
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
    st_kind_freib_tu
        See :func:`st_kind_freib_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    abgelt_st_tu
        See :func:`abgelt_st_tu`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    st_per_individual = st_kind_freib_tu / anz_erwachsene_tu
    out = (
        anz_erwachsene_tu * soli_tarif(st_per_individual, soli_st_params)
        + soli_st_params["soli_st"]["rates"][0, -1] * abgelt_st_tu
    )

    return out


def lohn_steuer_soli(
    tu_id: IntSeries,
    lohn_steuer_zve: FloatSeries,
    kind: BoolSeries,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
    steuerklasse: IntSeries,
) -> FloatSeries:

    # Full child allowance
    kinderfreibetrag_basis = (
        eink_st_abzuege_params["kinderfreibetrag"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreibetrag"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    kinderfreibetrag = (
        kinderfreibetrag_basis * 2 * steuerklasse.isin([1, 2, 3])
        + (kinderfreibetrag_basis * steuerklasse == 4) * kind.groupby(tu_id).sum()
    )
    lohn_steuer_soli_zve = lohn_steuer_zve - kinderfreibetrag
    return soli_tarif(lohn_steuer_soli_zve, soli_st_params)


def soli_tarif(st_per_individual: FloatSeries, soli_st_params: dict) -> FloatSeries:
    """
    The isolated function for Solidaritätszuschlag

    Parameters
    ----------
    st_per_individual:
        taxable income
    soli_st_params :
        See params documentation :ref:`soli_st_params <solo_st_params>`
    Returns
        solidarity surcharge
    -------

    """

    return piecewise_polynomial(
        st_per_individual,
        thresholds=soli_st_params["soli_st"]["thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )
