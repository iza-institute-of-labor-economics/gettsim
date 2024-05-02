from _gettsim.shared import policy_info

aggregate_by_group_kindergeld = {
    "bewohnt_eigentum_bg": {
        "source_col": "bewohnt_eigentum",
        "aggr": "any",
    },
}


@policy_info(end_date="2022-12-31", name_in_dag="arbeitsl_geld_2_kost_unterk_m_bg")
def arbeitsl_geld_2_kost_unterk_m_bg_bis_2022(
    _arbeitsl_geld_2_berechtigte_wohnfläche_bg: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Parameters
    ----------
    _arbeitsl_geld_2_berechtigte_wohnfläche_bg
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_bg`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_bg
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_bg`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    return (
        _arbeitsl_geld_2_berechtigte_wohnfläche_bg
        * _arbeitsl_geld_2_warmmiete_pro_qm_m_bg
    )


@policy_info(start_date="2023-01-01", name_in_dag="arbeitsl_geld_2_kost_unterk_m_bg")
def arbeitsl_geld_2_kost_unterk_m_bg_ab_2023(
    bruttokaltmiete_m_bg: float,
    heizkosten_m_bg: float,
    bürgerg_bezug_vorj: bool,
    _arbeitsl_geld_2_berechtigte_wohnfläche_bg: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim since 2023. During the first year,
    the waiting period (Karenzzeit), only the appropriateness of the heating costs is
    tested, while the living costs are fully considered in Bürgergeld.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m_bg
        See basic input variable :ref:`bruttokaltmiete_m_bg <bruttokaltmiete_m_bg>`.
    heizkosten_m_bg
        See basic input variable :ref:`heizkosten_m_bg <heizkosten_m_bg>`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.
    _arbeitsl_geld_2_berechtigte_wohnfläche_bg
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_bg`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_bg
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_bg`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    if bürgerg_bezug_vorj:
        out = (
            _arbeitsl_geld_2_berechtigte_wohnfläche_bg
            * _arbeitsl_geld_2_warmmiete_pro_qm_m_bg
        )
    else:
        out = bruttokaltmiete_m_bg + heizkosten_m_bg

    return out


def _arbeitsl_geld_2_warmmiete_pro_qm_m_bg(
    bruttokaltmiete_m_bg: float,
    heizkosten_m_bg: float,
    wohnfläche_bg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate rent per square meter.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m_bg
        See basic input variable :ref:`bruttokaltmiete_m_bg <bruttokaltmiete_m_bg>`.
    heizkosten_m_bg
        See basic input variable :ref:`heizkosten_m_bg <heizkosten_m_bg>`.
    wohnfläche_bg
        See basic input variable :ref:`wohnfläche_bg <wohnfläche_bg>`.

    Returns
    -------
    Integer with the total amount of rental costs per squaremeter.

    """
    out = (bruttokaltmiete_m_bg + heizkosten_m_bg) / wohnfläche_bg

    # Consider maximum considered rent per square meter
    out = min(out, arbeitsl_geld_2_params["max_miete_pro_qm"]["max"])

    return out


def _arbeitsl_geld_2_berechtigte_wohnfläche_bg(
    wohnfläche_bg: float,
    bewohnt_eigentum_bg: bool,
    anz_personen_bg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate size of dwelling eligible to claim.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    wohnfläche_bg
        See basic input variable :ref:`wohnfläche_bg <wohnfläche_bg>`.
    bewohnt_eigentum_bg
        See basic input variable :ref:`bewohnt_eigentum_bg <bewohnt_eigentum_bg>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.

    Returns
    -------
    Integer with the number of squaremeters.

    """
    params = arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]
    max_anzahl_direkt = params["max_anzahl_direkt"]
    if bewohnt_eigentum_bg:
        if anz_personen_bg <= max_anzahl_direkt:
            maximum = params[anz_personen_bg]
        else:
            maximum = (
                params[max_anzahl_direkt]
                + (anz_personen_bg - max_anzahl_direkt) * params["je_weitere_person"]
            )
    else:
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + max(anz_personen_bg - 1, 0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    return min(wohnfläche_bg, maximum)
