def kinderzuschl_kost_unterk_m_tu(
    _kinderzuschl_wohnbedarf_eltern_anteil_tu: float,
    bruttokaltmiete_m_hh: float,
    heizkosten_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    _kinderzuschl_wohnbedarf_eltern_anteil_tu
        See :func:`_kinderzuschl_wohnbedarf_eltern_anteil_tu`.
    bruttokaltmiete_m_tu
        See :func:`bruttokaltmiete_m_tu`.
    heizkosten_m_tu
        See :func:`heizkosten_m_tu`.

    Returns
    -------

    """
    warmmiete_m_hh = bruttokaltmiete_m_hh + heizkosten_m_hh
    anteil_warmmiete_m_tu = warmmiete_m_hh * _anteil_personen_in_haushalt_tu

    out = _kinderzuschl_wohnbedarf_eltern_anteil_tu * anteil_warmmiete_m_tu

    return out


def bruttokaltmiete_m_tu(
    bruttokaltmiete_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
) -> float:
    """Share of household's monthly rent attributed to the tax unit.

    Parameters
    ----------
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.

    Returns
    -------

    """
    return bruttokaltmiete_m_hh * _anteil_personen_in_haushalt_tu


def heizkosten_m_tu(
    heizkosten_m_hh: float,
    _anteil_personen_in_haushalt_tu: float,
) -> float:
    """Share of household's heating expenses attributed to the tax unit.

    Parameters
    ----------
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    _anteil_personen_in_haushalt_tu
        See :func:`_anteil_personen_in_haushalt_tu`.

    Returns
    -------

    """
    return heizkosten_m_hh * _anteil_personen_in_haushalt_tu


def _anteil_personen_in_haushalt_tu(
    tax_unit_größe_tu: int, haushaltsgröße_hh: int
) -> float:
    """Calculate the share of tax units in household.

    Parameters
    ----------
    tax_unit_größe_tu
        See :func:`tax_unit_größe_tu`.
    haushaltsgröße_hh
        See :func:`haushaltsgröße_hh`.

    Returns
    -------

    """
    return tax_unit_größe_tu / haushaltsgröße_hh


def _kinderzuschl_wohnbedarf_eltern_anteil_tu(
    anz_kinder_tu: int,
    anz_erwachsene_tu: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate living needs broken down to the parents. Defined as parents'
    subsistence level on housing, divided by sum of subsistence level from parents and
    children.

    Reference: § 6a Abs. 5 S. 3 BKGG

    Parameters
    ----------
    anz_kinder_tu
        See :func:`anz_kinder_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    ex_min = kinderzuschl_params["existenzminimum"]

    # Up to 10 children are considered
    considered_children = min(anz_kinder_tu, 10)
    single_oder_paar = "single" if anz_erwachsene_tu == 1 else "paare"

    out = (
        ex_min["kosten_der_unterkunft"][single_oder_paar]
        + ex_min["heizkosten"][single_oder_paar]
    ) / (
        ex_min["kosten_der_unterkunft"][single_oder_paar]
        + ex_min["heizkosten"][single_oder_paar]
        + (
            considered_children
            * (
                ex_min["kosten_der_unterkunft"]["kinder"]
                + ex_min["heizkosten"]["kinder"]
            )
        )
    )

    return out
