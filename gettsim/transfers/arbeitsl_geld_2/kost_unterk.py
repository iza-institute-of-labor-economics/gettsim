def arbeitsl_geld_2_kost_unterk_m_hh(
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_hh: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Parameters
    ----------
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_hh`.
    _arbeitsl_geld_2_warmmiete_pro_qm_hh
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_hh`.

    Returns
    -------
    float with total monthly cost of rent.
    """
    return (
        _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        * _arbeitsl_geld_2_warmmiete_pro_qm_hh
    )


def _arbeitsl_geld_2_warmmiete_pro_qm_hh(
    bruttokaltmiete_m_hh: float,
    heizkosten_m_hh: float,
    wohnfläche_hh: float,
    arbeitsl_geld_2_params: dict,
) -> float:
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
    Integer with the total amount of rental costs per squaremeter.
    """
    out = (bruttokaltmiete_m_hh + heizkosten_m_hh) / wohnfläche_hh

    # Consider maximum considered rent per square meter
    out = min(out, arbeitsl_geld_2_params["max_miete_pro_qm"]["max"])

    return out


def _arbeitsl_geld_2_berechtigte_wohnfläche_hh(
    wohnfläche_hh: float,
    bewohnt_eigentum_hh: bool,
    haushaltsgröße_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
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
    Integer with the number of squaremeters.
    """
    if bewohnt_eigentum_hh:
        weitere_mitglieder = max(haushaltsgröße_hh - 2, 0)
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]["basisgröße"]
            + weitere_mitglieder
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]["erweiterung"]
        )
    else:
        weitere_mitglieder = max(haushaltsgröße_hh - 1, 0)
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + weitere_mitglieder
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    return min(wohnfläche_hh, maximum)
