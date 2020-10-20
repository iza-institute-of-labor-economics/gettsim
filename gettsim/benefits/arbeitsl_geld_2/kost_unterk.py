from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def kost_unterk_m_hh(
    berechtigte_wohnfläche_hh: IntSeries, miete_pro_qm_hh: FloatSeries
) -> FloatSeries:
    """Justified costs of living.

    Parameters
    ----------
    berechtigte_wohnfläche_hh
        See :func:`berechtigte_wohnfläche_hh`.
    miete_pro_qm_hh
        See :func:`miete_pro_qm_hh`.

    Returns
    -------
    FloatSeries with total monthly cost of rent.
    """
    return berechtigte_wohnfläche_hh * miete_pro_qm_hh


def miete_pro_qm_hh(
    kaltmiete_m_hh: FloatSeries, heizkosten_m_hh: FloatSeries, wohnfläche_hh: IntSeries
) -> FloatSeries:
    """Check the monthly sum of rental costs per squaremeter.

    Parameters
    ----------
    kaltmiete_m_hh
        See basic input variable :ref:`kaltmiete_m_hh <kaltmiete_m_hh>`.
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    wohnfläche_hh
        See basic input variable :ref:`wohnfläche_hh <wohnfläche_hh>`.

    Returns
    -------
    IntSeries with the total amount of rental costs per squaremeter.
    """
    return ((kaltmiete_m_hh + heizkosten_m_hh) / wohnfläche_hh).clip(upper=10)


def berechtigte_wohnfläche_hh(
    wohnfläche_hh: IntSeries,
    bewohnt_eigentum_hh: BoolSeries,
    haushaltsgröße_hh: IntSeries,
) -> IntSeries:
    """Checks the maximum amount of squaremeters is payed by the state.

    Parameters
    ----------
    wohnfläche_hh
        See basic input variable :ref:`wohnfläche_hh <wohnfläche_hh>`.
    bewohnt_eigentum_hh
        See basic input variable :ref:`bewohnt_eigentum_hh <bewohnt_eigentum_hh>`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.

    Returns
    -------
    IntSeries with the number of squaremeters.
    """
    out = wohnfläche_hh * 0
    out.loc[bewohnt_eigentum_hh] = wohnfläche_hh.loc[bewohnt_eigentum_hh].clip(
        upper=(80 + (haushaltsgröße_hh.loc[bewohnt_eigentum_hh] - 2).clip(lower=0) * 20)
    )
    out.loc[~bewohnt_eigentum_hh] = wohnfläche_hh.loc[~bewohnt_eigentum_hh].clip(
        upper=(
            45 + (haushaltsgröße_hh.loc[~bewohnt_eigentum_hh] - 1).clip(lower=0) * 15
        )
    )
    return out
