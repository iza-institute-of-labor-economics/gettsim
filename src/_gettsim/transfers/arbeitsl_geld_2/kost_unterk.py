from _gettsim.shared import dates_active


@dates_active(end="2022-12-31", change_name="arbeitsl_geld_2_kost_unterk_m_vg")
def arbeitsl_geld_2_kost_unterk_m_vg_bis_2022(
    _arbeitsl_geld_2_berechtigte_wohnfläche_vg: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_vg: float,
) -> float:
    """Calculate costs of living eligible to claim until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Parameters
    ----------
    _arbeitsl_geld_2_berechtigte_wohnfläche_vg
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_vg`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_vg
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_vg`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    return (
        _arbeitsl_geld_2_berechtigte_wohnfläche_vg
        * _arbeitsl_geld_2_warmmiete_pro_qm_m_vg
    )


@dates_active(start="2023-01-01", change_name="arbeitsl_geld_2_kost_unterk_m_vg")
def arbeitsl_geld_2_kost_unterk_m_vg_ab_2023(
    bruttokaltmiete_m_vg: float,
    heizkosten_m_vg: float,
    bürgerg_bezug_vorj: bool,
    _arbeitsl_geld_2_berechtigte_wohnfläche_vg: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_vg: float,
) -> float:
    """Calculate costs of living eligible to claim since 2023. During the first year,
    the waiting period (Karenzzeit), only the appropriateness of the heating costs is
    tested, while the living costs are fully considered in Bürgergeld.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m_vg
        See basic input variable :ref:`bruttokaltmiete_m_vg <bruttokaltmiete_m_vg>`.
    heizkosten_m_vg
        See basic input variable :ref:`heizkosten_m_vg <heizkosten_m_vg>`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.
    _arbeitsl_geld_2_berechtigte_wohnfläche_vg
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_vg`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_vg
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_vg`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    if bürgerg_bezug_vorj:
        out = (
            _arbeitsl_geld_2_berechtigte_wohnfläche_vg
            * _arbeitsl_geld_2_warmmiete_pro_qm_m_vg
        )
    else:
        out = bruttokaltmiete_m_vg + heizkosten_m_vg

    return out


def _arbeitsl_geld_2_warmmiete_pro_qm_m_vg(
    bruttokaltmiete_m_vg: float,
    heizkosten_m_vg: float,
    wohnfläche_vg: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate rent per square meter.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m_vg
        See basic input variable :ref:`bruttokaltmiete_m_vg <bruttokaltmiete_m_vg>`.
    heizkosten_m_vg
        See basic input variable :ref:`heizkosten_m_vg <heizkosten_m_vg>`.
    wohnfläche_vg
        See basic input variable :ref:`wohnfläche_vg <wohnfläche_vg>`.

    Returns
    -------
    Integer with the total amount of rental costs per squaremeter.

    """
    out = (bruttokaltmiete_m_vg + heizkosten_m_vg) / wohnfläche_vg

    # Consider maximum considered rent per square meter
    out = min(out, arbeitsl_geld_2_params["max_miete_pro_qm"]["max"])

    return out


def _arbeitsl_geld_2_berechtigte_wohnfläche_vg(
    wohnfläche_vg: float,
    bewohnt_eigentum_vg: bool,
    haushaltsgröße_vg: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate size of dwelling eligible to claim.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    wohnfläche_vg
        See basic input variable :ref:`wohnfläche_vg <wohnfläche_vg>`.
    bewohnt_eigentum_vg
        See basic input variable :ref:`bewohnt_eigentum_vg <bewohnt_eigentum_vg>`.
    haushaltsgröße_vg
        See :func:`haushaltsgröße_vg`.

    Returns
    -------
    Integer with the number of squaremeters.

    """
    params = arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]
    if bewohnt_eigentum_vg:
        if haushaltsgröße_vg <= 4:
            maximum = params[haushaltsgröße_vg]
        else:
            maximum = params[4] + (haushaltsgröße_vg - 4) * params["je_weitere_person"]
    else:
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + max(haushaltsgröße_vg - 1, 0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    return min(wohnfläche_vg, maximum)

    # if bewohnt_eigentum_vg and haushaltsgröße_vg < 5:

    # if not bewohnt_eigentum_vg:
    #         * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
    #             "je_weitere_person"
