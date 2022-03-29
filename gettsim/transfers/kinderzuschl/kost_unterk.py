def kinderzuschl_kost_unterk_m(
    _kinderzuschl_wohnbedarf_eltern_anteil_tu: float,
    kinderzuschl_bruttokaltmiete_m: float,
    kinderzuschl_heizkosten_m: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    _kinderzuschl_wohnbedarf_eltern_anteil_tu
        See :func:`_kinderzuschl_wohnbedarf_eltern_anteil_tu`.
    kinderzuschl_bruttokaltmiete_m
        See :func:`kinderzuschl_bruttokaltmiete_m`.
    kinderzuschl_heizkosten_m
        See :func:`kinderzuschl_heizkosten_m`.

    Returns
    -------

    """
    out = _kinderzuschl_wohnbedarf_eltern_anteil_tu * (
        kinderzuschl_bruttokaltmiete_m + kinderzuschl_heizkosten_m
    )
    return out


def kinderzuschl_bruttokaltmiete_m(
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


def kinderzuschl_heizkosten_m(
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


def _kinderzuschl_wohnbedarf_eltern_anteil_tu(
    anz_kinder_tu: int,
    anz_erwachsene_tu: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate living needs broken down to the parents.
     Defined as parents' subsistence level on housing, divided by sum
     of subsistence level from parents and children.

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

    # Only 5 children are considered
    considered_children = min(anz_kinder_tu, 5)
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
