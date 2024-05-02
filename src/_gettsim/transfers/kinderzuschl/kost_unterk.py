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

    return (
        bruttokaltmiete_m_bg + heizkosten_m_bg
    ) * _kinderzuschl_wohnbedarf_eltern_anteil_bg


def bruttokaltmiete_m_bg(  # noqa: PLR0913
    anz_paare_hh: int,
    bruttokaltmiete_m_hh: float,
    anz_kinder_bis_17_bg: int,
    anz_kinder_bis_17_hh: int,
    anz_erwachsene_bg: int,
    anz_erwachsene_hh: int,
    kinderzuschl_params: dict,
) -> float:
    """Monthly rent attributed to the Bedarfsgemeinschaft.

    The rent is split among a household's Bedarfsgemeinschaften according to their needs
    specified in the Existenzminimumsbericht.

    Parameters
    ----------
    anz_paare_hh
        See :func:`anz_paare_hh`.
    bruttokaltmiete_m_hh
        See basic input variable :ref:`bruttokaltmiete_m_hh <bruttokaltmiete_m_hh>`.
    anz_kinder_bis_17_bg
        See :func:`anz_kinder_bis_17_bg`.
    anz_kinder_bis_17_hh
        See :func:`anz_kinder_bis_17_hh`.
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    bedarf_hh = (
        anz_paare_hh
        * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["paare"]
        + (anz_erwachsene_hh - anz_paare_hh * 2)
        * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["single"]
        + anz_kinder_bis_17_hh
        * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["kinder"]
    )

    if anz_erwachsene_bg == 1:
        bedarf_bg = (
            anz_erwachsene_bg
            * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["single"]
            + anz_kinder_bis_17_bg
            * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["kinder"]
        )
    else:
        bedarf_bg = (
            kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["paare"]
            + anz_kinder_bis_17_bg
            * kinderzuschl_params["existenzminimum"]["kosten_der_unterkunft"]["kinder"]
        )

    return bruttokaltmiete_m_hh * (bedarf_bg / bedarf_hh)


def heizkosten_m_bg(  # noqa: PLR0913
    anz_paare_hh: int,
    heizkosten_m_hh: float,
    anz_kinder_bis_17_bg: int,
    anz_kinder_bis_17_hh: int,
    anz_erwachsene_bg: int,
    anz_erwachsene_hh: int,
    kinderzuschl_params: dict,
) -> float:
    """Monthly heating expenses attributed to the Bedarfsgemeinschaft.

    Heating expenses is split among a household's Bedarfsgemeinschaften according to
    their needs specified in the Existenzminimumsbericht.

    Parameters
    ----------
    anz_paare_hh
        See :func:`anz_paare_hh`.
    heizkosten_m_hh
        See basic input variable :ref:`heizkosten_m_hh <heizkosten_m_hh>`.
    anz_kinder_bis_17_bg
        See :func:`anz_kinder_bis_17_bg`.
    anz_kinder_bis_17_hh
        See :func:`anz_kinder_bis_17_hh`.
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    bedarf_hh = (
        anz_paare_hh * kinderzuschl_params["existenzminimum"]["heizkosten"]["paare"]
        + (anz_erwachsene_hh - anz_paare_hh * 2)
        * kinderzuschl_params["existenzminimum"]["heizkosten"]["single"]
        + anz_kinder_bis_17_hh
        * kinderzuschl_params["existenzminimum"]["heizkosten"]["kinder"]
    )

    if anz_erwachsene_bg == 1:
        bedarf_bg = (
            anz_erwachsene_bg
            * kinderzuschl_params["existenzminimum"]["heizkosten"]["single"]
            + anz_kinder_bis_17_bg
            * kinderzuschl_params["existenzminimum"]["heizkosten"]["kinder"]
        )
    else:
        bedarf_bg = (
            kinderzuschl_params["existenzminimum"]["heizkosten"]["paare"]
            + anz_kinder_bis_17_bg
            * kinderzuschl_params["existenzminimum"]["heizkosten"]["kinder"]
        )

    return heizkosten_m_hh * (bedarf_bg / bedarf_hh)


def wohnfläche_bg(
    wohnfläche_hh: float,
    anz_personen_bg: int,
    anz_personen_hh: int,
) -> float:
    """Apartment size attributed to the Bedarfsgemeinschaft.

    Parameters
    ----------
    wohnfläche_hh
        See basic input variable :ref:`wohnfläche_hh <wohnfläche_hh>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    anz_personen_hh
        See :func:`anz_personen_hh`.

    Returns
    -------

    """
    return wohnfläche_hh * (anz_personen_bg / anz_personen_hh)


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
