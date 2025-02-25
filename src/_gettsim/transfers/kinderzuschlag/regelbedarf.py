"""Basic needs of children in the calculation of Kinderzuschlag."""

from _gettsim.functions.policy_function import policy_function


def kosten_unterkunft_m_bg(
    wohnbedarf_anteil_eltern_bg: float,
    arbeitslosengeld_2__bruttokaltmiete_m_bg: float,
    arbeitslosengeld_2__heizkosten_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    wohnbedarf_anteil_eltern_bg
        See :func:`wohnbedarf_anteil_eltern_bg`.
    arbeitslosengeld_2__bruttokaltmiete_m_bg
        See :func:`arbeitslosengeld_2__bruttokaltmiete_m_bg`.
    arbeitslosengeld_2__heizkosten_m_bg
        See :func:`arbeitslosengeld_2__heizkosten_m_bg`.

    Returns
    -------

    """
    warmmiete_m_bg = (
        arbeitslosengeld_2__bruttokaltmiete_m_bg + arbeitslosengeld_2__heizkosten_m_bg
    )

    out = wohnbedarf_anteil_eltern_bg * warmmiete_m_bg

    return out


def wohnbedarf_anteil_eltern_bg(
    anzahl_kinder_bg: int,
    anz_erwachsene_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate living needs broken down to the parents. Defined as parents'
    subsistence level on housing, divided by sum of subsistence level from parents and
    children.

    Reference: § 6a Abs. 5 S. 3 BKGG

    Parameters
    ----------
    anzahl_kinder_bg
        See :func:`anzahl_kinder_bg`.
    anz_erwachsene_bg
        See :func:`anz_erwachsene_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    ex_min = kinderzuschl_params["existenzminimum"]

    # Up to 10 children are considered
    considered_children = min(anzahl_kinder_bg, 10)
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


@policy_function(end_date="2010-12-31", name_in_dag="regelsatz_m_bg")
def regelsatz_m_bg_arbeitsl_geld_2_params_old(
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        See :func:`arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        )
    else:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"]
            * 2
        )

    return float(out)


@policy_function(start_date="2011-01-01")
def regelsatz_m_bg(
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        See :func:`arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * 2

    return float(out)


def bedarf_m_bg(regelsatz_m_bg: float, kosten_unterkunft_m_bg: float) -> float:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    regelsatz_m_bg
        See :func:`regelsatz_m_bg`.
    kosten_unterkunft_m_bg
        See :func:`kosten_unterkunft_m_bg`.

    Returns
    -------

    """
    return regelsatz_m_bg + kosten_unterkunft_m_bg
