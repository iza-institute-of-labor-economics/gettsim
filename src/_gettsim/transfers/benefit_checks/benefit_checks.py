aggregate_by_group_benefit_checks = {
    "wohngeld_vorrang_wthh": {
        "source_col": "wohngeld_vorrang_bg",
        "aggr": "any",
    },
    "wohngeld_kinderzuschl_vorrang_wthh": {
        "source_col": "wohngeld_kinderzuschl_vorrang_bg",
        "aggr": "any",
    },
    "_transfereinkommen_für_günstigerprüfung_fg": {
        "source_col": "_transfereinkommen_für_günstigerprüfung",
        "aggr": "sum",
    },
}

# basic input wohngeld_günstiger_als_sgb_ii (bool)?
# pro: we do the günstigerprüfung outside of gettim, the bg level günstigerprüfung may
# make a mistake
# con: ???


def vorrangprüfung_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    _arbeitsl_geld_2_nettoeink_ohne_transfers_m_bg: float,
    kindergeld_zur_bedarfsdeckung_m_bg: float,
    kind_unterh_erhalt_m_bg: float,
    unterhaltsvors_m_bg: float,
) -> float:
    """Vorrangprüfung for SGB II vs. WoG / KiZ benefits.

    Determines whether needs of the Bedarfsgemeinschaft are covered. If so, the
    Bedarfsgemeinschaft is not eligible for SGB II benefits.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    _arbeitsl_geld_2_nettoeink_ohne_transfers_m_bg
        See :func:`_arbeitsl_geld_2_nettoeink_ohne_transfers_m_bg`.
    kindergeld_zur_bedarfsdeckung_m_bg
        See :func:`kindergeld_zur_bedarfsdeckung_m_bg`.
    kind_unterh_erhalt_m_bg
        See :func:`kind_unterh_erhalt_m_bg`.
    unterhaltsvors_m_bg
        See :func:`unterhaltsvors_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_regelbedarf_m_bg
        < _arbeitsl_geld_2_nettoeink_ohne_transfers_m_bg
        + kindergeld_zur_bedarfsdeckung_m_bg
        + kind_unterh_erhalt_m_bg
        + unterhaltsvors_m_bg
    )


def _transfereinkommen_für_günstigerprüfung(
    arbeitsl_geld_2_m_bg: float,
    wohngeld_m_wthh: float,
    kinderzuschl_m_bg: float,
    anz_personen_bg: int,
    anz_personen_wthh: int,
) -> float:
    """Transfer income on individual level.

    Used as an input for the Günstigerprüfung.

    Parameters
    ----------
    arbeitsl_geld_2_m_bg
        See :func:`arbeitsl_geld_2_m_bg`.
    wohngeld_m_wthh
        See :func:`wohngeld_m_wthh`.
    kinderzuschl_m_bg
        See :func:`kinderzuschl_m_bg`.

    Returns
    -------

    """
    wohngeld_individual_level = wohngeld_m_wthh / anz_personen_wthh
    arbeitsl_geld_2_kinderzuschl_individual_level = (
        kinderzuschl_m_bg / anz_personen_bg + arbeitsl_geld_2_m_bg / anz_personen_bg
    )
    return arbeitsl_geld_2_kinderzuschl_individual_level + wohngeld_individual_level


def wohngeld_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    wohngeld_nach_vermög_check_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Housing benefit has priority if the sum of housing benefit and income covers the
    needs according to SGB II of the Bedarfsgemeinschaft.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    wohngeld_nach_vermög_check_m_bg
        See :func:`wohngeld_nach_vermög_check_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_regelbedarf_m_bg
        <= arbeitsl_geld_2_eink_m_bg + wohngeld_nach_vermög_check_m_bg
    )


def kinderzuschl_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    _kinderzuschl_nach_vermög_check_m_bg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    _kinderzuschl_nach_vermög_check_m_bg
        See :func:`_kinderzuschl_nach_vermög_check_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_regelbedarf_m_bg
        <= arbeitsl_geld_2_eink_m_bg + _kinderzuschl_nach_vermög_check_m_bg
    )


def wohngeld_kinderzuschl_vorrang_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    arbeitsl_geld_2_eink_m_bg: float,
    _kinderzuschl_nach_vermög_check_m_bg: float,
    wohngeld_nach_vermög_check_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    arbeitsl_geld_2_eink_m_bg
        See :func:`arbeitsl_geld_2_eink_m_bg`.
    _kinderzuschl_nach_vermög_check_m_bg
        See :func:`_kinderzuschl_nach_vermög_check_m_bg`.
    wohngeld_nach_vermög_check_m_bg
        See :func:`wohngeld_nach_vermög_check_m_bg`.

    Returns
    -------

    """

    return (
        arbeitsl_geld_2_regelbedarf_m_bg
        <= arbeitsl_geld_2_eink_m_bg
        + wohngeld_nach_vermög_check_m_bg
        + _kinderzuschl_nach_vermög_check_m_bg
    )
