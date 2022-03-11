from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def arbeitsl_geld_2_kost_unterk_m_hh(
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh: IntSeries,
    _arbeitsl_geld_2_warmmiete_pro_qm_hh: FloatSeries,
) -> FloatSeries:
    """Calculate costs of living eligible to claim.

    Parameters
    ----------
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_hh`.
    _arbeitsl_geld_2_warmmiete_pro_qm_hh
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_hh`.

    Returns
    -------
    FloatSeries with total monthly cost of rent.
    """
    return (
        _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        * _arbeitsl_geld_2_warmmiete_pro_qm_hh
    )


def _arbeitsl_geld_2_warmmiete_pro_qm_hh(
    bruttokaltmiete_m_hh: FloatSeries,
    heizkosten_m_hh: FloatSeries,
    wohnfläche_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate rent per square meter.

    Parameters
    ----------
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    wohnfläche_hh
        See basic input variable :ref:`wohnfläche_hh <wohnfläche_hh>`.

    Returns
    -------
    IntSeries with the total amount of rental costs per squaremeter.
    """
    return ((bruttokaltmiete_m_hh + heizkosten_m_hh) / wohnfläche_hh).clip(
        upper=arbeitsl_geld_2_params["max_miete_pro_qm"]["max"]
    )


def _arbeitsl_geld_2_berechtigte_wohnfläche_hh(
    wohnfläche_hh: IntSeries,
    bewohnt_eigentum_hh: BoolSeries,
    haushaltsgröße_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> IntSeries:
    """Calculate size of dwelling eligible to claim.

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
        upper=(
            arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]["basisgröße"]
            + (haushaltsgröße_hh.loc[bewohnt_eigentum_hh] - 2).clip(lower=0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]["erweiterung"]
        )
    )
    out.loc[~bewohnt_eigentum_hh] = wohnfläche_hh.loc[~bewohnt_eigentum_hh].clip(
        upper=(
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + (haushaltsgröße_hh.loc[~bewohnt_eigentum_hh] - 1).clip(lower=0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    )
    return out
