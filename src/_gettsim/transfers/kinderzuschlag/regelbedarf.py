"""Basic needs of children in the calculation of Kinderzuschlag."""

from _gettsim.shared import policy_info


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


@policy_info(end_date="2010-12-31", name_in_dag="kinderzuschl_eink_regel_m_bg")
def kinderzuschl_eink_regel_m_bg_arbeitsl_geld_2_params_old(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    else:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"]
            * 2
        )

    return float(out)


@policy_info(start_date="2011-01-01")
def kinderzuschl_eink_regel_m_bg(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_bg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * 2

    return float(out)


def kinderzuschl_eink_relev_m_bg(
    kinderzuschl_eink_regel_m_bg: float, kinderzuschl_kost_unterk_m_bg: float
) -> float:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    kinderzuschl_eink_regel_m_bg
        See :func:`kinderzuschl_eink_regel_m_bg`.
    kinderzuschl_kost_unterk_m_bg
        See :func:`kinderzuschl_kost_unterk_m_bg`.

    Returns
    -------

    """
    return kinderzuschl_eink_regel_m_bg + kinderzuschl_kost_unterk_m_bg
