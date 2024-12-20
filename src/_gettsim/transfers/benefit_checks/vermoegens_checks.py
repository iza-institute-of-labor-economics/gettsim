from _gettsim.shared import policy_info


def _kinderzuschl_nach_vermög_check_m_bg(
    _kinderzuschl_vor_vermög_check_m_bg: float,
    vermögen_bedürft_bg: float,
    kinderzuschl_vermög_freib_bg: float,
) -> float:
    """Set preliminary child benefit to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschl_vor_vermög_check_m_bg
        See :func:`_kinderzuschl_vor_vermög_check_m_bg`.
    vermögen_bedürft_bg
        See basic input variable :ref:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    kinderzuschl_vermög_freib_bg
        See :func:`kinderzuschl_vermög_freib_bg`.

    Returns
    -------

    """

    if vermögen_bedürft_bg > kinderzuschl_vermög_freib_bg:
        out = max(
            _kinderzuschl_vor_vermög_check_m_bg
            - (vermögen_bedürft_bg - kinderzuschl_vermög_freib_bg),
            0.0,
        )
    else:
        out = _kinderzuschl_vor_vermög_check_m_bg
    return out


@policy_info(end_date="2022-12-31", name_in_dag="kinderzuschl_vermög_freib_bg")
def kinderzuschl_vermög_freib_bg_bis_2022(
    arbeitsl_geld_2_vermög_freib_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag until 2022.

    Parameters
    ----------
    arbeitsl_geld_2_vermög_freib_bg
        See :func:`arbeitsl_geld_2_vermög_freib_bg`.

    Returns
    -------

    """

    return arbeitsl_geld_2_vermög_freib_bg


@policy_info(start_date="2023-01-01", name_in_dag="kinderzuschl_vermög_freib_bg")
def kinderzuschl_vermög_freib_bg_ab_2023(
    _arbeitsl_geld_2_vermög_freib_karenzz_bg: float,
) -> float:
    """Wealth exemptions for Kinderzuschlag since 2023.

    Parameters
    ----------
    _arbeitsl_geld_2_vermög_freib_karenzz_bg
        See :func:`_arbeitsl_geld_2_vermög_freib_karenzz_bg`.

    Returns
    -------

    """

    return _arbeitsl_geld_2_vermög_freib_karenzz_bg
