def kinderzuschl_kost_unterk_m_bg(
    _kinderzuschl_wohnbedarf_eltern_anteil_bg: float,
    bruttokaltmiete_m_bg: float,
    heizkosten_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    _kinderzuschl_wohnbedarf_eltern_anteil_bg
        See :func:`_kinderzuschl_wohnbedarf_eltern_anteil_bg`.
    bruttokaltmiete_m_bg
        See :func:`bruttokaltmiete_m_bg`.
    heizkosten_m_bg
        See :func:`heizkosten_m_bg`.

    Returns
    -------

    """
    warmmiete_m_bg = bruttokaltmiete_m_bg + heizkosten_m_bg

    out = _kinderzuschl_wohnbedarf_eltern_anteil_bg * warmmiete_m_bg

    return out


def _kinderzuschl_wohnbedarf_eltern_anteil_bg(
    _kinderzuschl_anz_kinder_anspruch_bg: int,
    anz_erwachsene_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate living needs broken down to the parents. Defined as parents'
    subsistence level on housing, divided by sum of subsistence level from parents and
    children.

    Reference: § 6a Abs. 5 S. 3 BKGG

    Parameters
    ----------
    _kinderzuschl_anz_kinder_anspruch_bg
        See :func:`_kinderzuschl_anz_kinder_anspruch_bg`.
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    ex_min = kinderzuschl_params["existenzminimum"]

    # Up to 10 children are considered
    considered_children = min(_kinderzuschl_anz_kinder_anspruch_bg, 10)
    single_oder_paar = "single" if anz_erwachsene_bg == 1 else "paare"

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
