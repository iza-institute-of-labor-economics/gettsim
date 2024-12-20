"""Eligibility checks for housing benefits (Wohngeld)."""


def wohngeld_anspruchsbedingungen_erfüllt_wthh(
    wohngeld_mindesteinkommen_erreicht_wthh: bool,
    wohngeld_vermögensgrenze_unterschritten_wthh: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    Parameters
    ----------
    wohngeld_mindesteinkommen_erreicht_wthh
        See :func:`wohngeld_mindesteinkommen_erreicht_wthh`.
    wohngeld_vermögensgrenze_unterschritten_wthh
        See :func:`wohngeld_vermögensgrenze_unterschritten_wthh`.

    Returns
    -------

    """
    return (
        wohngeld_vermögensgrenze_unterschritten_wthh
        and wohngeld_mindesteinkommen_erreicht_wthh
    )


def wohngeld_anspruchsbedingungen_erfüllt_bg(
    wohngeld_mindesteinkommen_erreicht_bg: bool,
    wohngeld_vermögensgrenze_unterschritten_bg: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    wohngeld_mindesteinkommen_erreicht_bg
        See :func:`wohngeld_mindesteinkommen_erreicht_bg`.
    wohngeld_vermögensgrenze_unterschritten_bg
        See :func:`wohngeld_vermögensgrenze_unterschritten_bg`.

    Returns
    -------

    """
    return (
        wohngeld_mindesteinkommen_erreicht_bg
        and wohngeld_vermögensgrenze_unterschritten_bg
    )


def wohngeld_vermögensgrenze_unterschritten_wthh(
    vermögen_bedürft_wthh: float,
    anz_personen_wthh: int,
    wohngeld_params: dict,
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits.

    Parameters
    ----------
    vermögen_bedürft_wthh
        See :func:`vermögen_bedürft_wthh <vermögen_bedürft_wthh>`.
    anz_personen_wthh
        See :func:`anz_personen_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return _wohngeld_vermögensprüfung_formel(
        vermögen=vermögen_bedürft_wthh,
        anz_personen=anz_personen_wthh,
        params=wohngeld_params,
    )


def wohngeld_vermögensgrenze_unterschritten_bg(
    vermögen_bedürft_bg: float,
    anz_personen_bg: int,
    wohngeld_params: dict,
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits.

    Parameters
    ----------
    vermögen_bedürft_bg
        See :func:`vermögen_bedürft_bg <vermögen_bedürft_bg>`.
    anz_personen_bg
        See :func:`anz_personen_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return _wohngeld_vermögensprüfung_formel(
        vermögen=vermögen_bedürft_bg,
        anz_personen=anz_personen_bg,
        params=wohngeld_params,
    )


def wohngeld_mindesteinkommen_erreicht_wthh(
    arbeitsl_geld_2_regelbedarf_m_wthh: float,
    wohngeld_einkommen_für_mindesteinkommen_check_m_wthh: float,
) -> bool:
    """Minimum income requirement for housing benefits is met.

    Note: The Wohngeldstelle can make a discretionary judgment if the applicant does not
    meet the Mindesteinkommen:

    1. Savings may partly cover the Regelbedarf, making the applicant eligible again.
    2. The Wohngeldstelle may reduce the Regelsatz by 20% (but not KdU or private
        insurance contributions).

    The allowance for discretionary judgment is ignored here.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_wthh
        See :func:`arbeitsl_geld_2_regelbedarf_m_wthh`.
    wohngeld_einkommen_für_mindesteinkommen_check_m_wthh
        See :func:`wohngeld_einkommen_für_mindesteinkommen_check_m_wthh`.

    Returns
    -------

    """
    return (
        wohngeld_einkommen_für_mindesteinkommen_check_m_wthh
        >= arbeitsl_geld_2_regelbedarf_m_wthh
    )


def wohngeld_mindesteinkommen_erreicht_bg(
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    wohngeld_einkommen_für_mindesteinkommen_check_m_bg: float,
) -> bool:
    """Minimum income requirement for housing benefits is met.

    Note: The Wohngeldstelle can make a discretionary judgment if the applicant does not
    meet the Mindesteinkommen:

    1. Savings may partly cover the Regelbedarf, making the applicant eligible again.
    2. The Wohngeldstelle may reduce the Regelsatz by 20% (but not KdU or private
        insurance contributions).

    The allowance for discretionary judgment is ignored here.

    Parameters
    ----------
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    wohngeld_einkommen_für_mindesteinkommen_check_m_bg
        See :func:`wohngeld_einkommen_für_mindesteinkommen_check_m_bg`.

    Returns
    -------

    """
    return (
        wohngeld_einkommen_für_mindesteinkommen_check_m_bg
        >= arbeitsl_geld_2_regelbedarf_m_bg
    )


def wohngeld_einkommen_für_mindesteinkommen_check_m(
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    kindergeld_m: float,
    _kinderzuschl_nach_vermög_check_m: float,
) -> float:
    """Income for the Mindesteinkommen check.

    Minimum income is defined via VwV 15.01 ff § 15 WoGG.

    According to BMI Erlass of 11.03.2020, Unterhaltsvorschuss, Kinderzuschlag and
    Kindergeld count as income for this check.

    Parameters
    ----------
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m
        See :func:`arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m`.
    kind_unterh_erhalt_m
        See :func:`kind_unterh_erhalt_m`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    kindergeld_m
        See :func:`kindergeld_m`.
    _kinderzuschl_nach_vermög_check_m
        See :func:`_kinderzuschl_nach_vermög_check_m`.

    Returns
    -------

    """

    return (
        arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m
        + kind_unterh_erhalt_m
        + unterhaltsvors_m
        + kindergeld_m
        + _kinderzuschl_nach_vermög_check_m
    )


def _wohngeld_vermögensprüfung_formel(
    vermögen: float,
    anz_personen: int,
    params: dict,
) -> float:
    """Wealth check for housing benefit calculation.

    The payment depends on the wealth of the household and the number of household
    members.

    Note: This function is not a direct target in the DAG, but a helper function to
    store the code for Wohngeld calculation.

    Parameters
    ----------
    vermögen
        Relevant wealth of the Wohngeld recipients.
    anz_personen
        Number of people Wohngeld is being calculated for.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """

    if anz_personen == 1:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"]
    else:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"] + params[
            "vermögensfreibetrag_pers"
        ] * (anz_personen - 1)

    if vermögen <= vermögensfreibetrag:
        out = True
    else:
        out = False

    return out
