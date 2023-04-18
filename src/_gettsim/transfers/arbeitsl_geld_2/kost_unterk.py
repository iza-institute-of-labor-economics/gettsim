from _gettsim.shared import dates_active


@dates_active(end="2022-12-31", change_name="arbeitsl_geld_2_kost_unterk_m_hh")
def arbeitsl_geld_2_kost_unterk_m_hh_bis_2022(
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_hh: float,
) -> float:
    """Calculate costs of living eligible to claim until 2022.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Parameters
    ----------
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_hh`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_hh
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_hh`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    return (
        _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        * _arbeitsl_geld_2_warmmiete_pro_qm_m_hh
    )


@dates_active(start="2023-01-01", change_name="arbeitsl_geld_2_kost_unterk_m_hh")
def arbeitsl_geld_2_kost_unterk_m_hh_ab_2023(
    bruttokaltmiete_m_hh: float,
    heizkosten_m_hh: float,
    bürgerg_bezug_vorj: bool,
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh: float,
    _arbeitsl_geld_2_warmmiete_pro_qm_m_hh: float,
) -> float:
    """Calculate costs of living eligible to claim since 2023. During the first year,
    the waiting period (Karenzzeit), only the appropriateness of the heating costs is
    tested, while the living costs are fully considered in Bürgergeld.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    bürgerg_bezug_vorj
        See basic input variable :ref:`bürgerg_bezug_vorj <bürgerg_bezug_vorj>`.
    _arbeitsl_geld_2_berechtigte_wohnfläche_hh
        See :func:`_arbeitsl_geld_2_berechtigte_wohnfläche_hh`.
    _arbeitsl_geld_2_warmmiete_pro_qm_m_hh
        See :func:`_arbeitsl_geld_2_warmmiete_pro_qm_m_hh`.

    Returns
    -------
    float with total monthly cost of rent.

    """
    if bürgerg_bezug_vorj:
        out = (
            _arbeitsl_geld_2_berechtigte_wohnfläche_hh
            * _arbeitsl_geld_2_warmmiete_pro_qm_m_hh
        )
    else:
        # ToDo: only reasonable heating costs are taken into account
        # these are calculated taking into account the actual size of the apartment
        # not just the appropriate size
        out = bruttokaltmiete_m_hh + heizkosten_m_hh

    return out


def _arbeitsl_geld_2_warmmiete_pro_qm_m_hh(
    bruttokaltmiete_m_hh: float,
    heizkosten_m_hh: float,
    wohnfläche_hh: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate rent per square meter.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

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

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

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
    params = arbeitsl_geld_2_params["berechtigte_wohnfläche_eigentum"]
    if bewohnt_eigentum_hh:
        if haushaltsgröße_hh <= 4:
            maximum = params[haushaltsgröße_hh]
        else:
            maximum = params[4] + (haushaltsgröße_hh - 4) * params["je_weitere_person"]
    else:
        maximum = (
            arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"]["single"]
            + max(haushaltsgröße_hh - 1, 0)
            * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
                "je_weitere_person"
            ]
        )
    return min(wohnfläche_hh, maximum)

    # if bewohnt_eigentum_hh and haushaltsgröße_hh < 5:

    # if not bewohnt_eigentum_hh:
    #         * arbeitsl_geld_2_params["berechtigte_wohnfläche_miete"][
    #             "je_weitere_person"
