"""Eligibility checks for housing benefits (Wohngeld)."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def grundsätzlich_anspruchsberechtigt_wthh(
    mindesteinkommen_erreicht_wthh: bool,
    vermögensgrenze_unterschritten_wthh: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used to calculate the actual Wohngeld of all Bedarfsgemeinschaften
    that passed the priority check against Arbeitslosengeld II / Bürgergeld.

    Parameters
    ----------
    mindesteinkommen_erreicht_wthh
        See :func:`mindesteinkommen_erreicht_wthh`.
    vermögensgrenze_unterschritten_wthh
        See :func:`vermögensgrenze_unterschritten_wthh`.

    Returns
    -------

    """
    return vermögensgrenze_unterschritten_wthh and mindesteinkommen_erreicht_wthh


@policy_function()
def grundsätzlich_anspruchsberechtigt_bg(
    mindesteinkommen_erreicht_bg: bool,
    vermögensgrenze_unterschritten_bg: bool,
) -> bool:
    """Check whether the household meets the conditions for Wohngeld.

    This target is used for the priority check calculation against Arbeitslosengeld II /
    Bürgergeld on the Bedarfsgemeinschaft level.

    Parameters
    ----------
    mindesteinkommen_erreicht_bg
        See :func:`mindesteinkommen_erreicht_bg`.
    vermögensgrenze_unterschritten_bg
        See :func:`vermögensgrenze_unterschritten_bg`.

    Returns
    -------

    """
    return mindesteinkommen_erreicht_bg and vermögensgrenze_unterschritten_bg


@policy_function()
def vermögensgrenze_unterschritten_wthh(
    demographics__vermögen_wthh: float,
    demographics__anzahl_personen_wthh: int,
    wohngeld_params: dict,
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits.

    Parameters
    ----------
    demographics__vermögen_wthh
        See :func:`demographics__vermögen_wthh <demographics__vermögen_wthh>`.
    demographics__anzahl_personen_wthh
        See :func:`demographics__anzahl_personen_wthh`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return vermögensprüfung_formel(
        vermögen=demographics__vermögen_wthh,
        anzahl_personen=demographics__anzahl_personen_wthh,
        params=wohngeld_params,
    )


@policy_function()
def vermögensgrenze_unterschritten_bg(
    demographics__vermögen_bg: float,
    demographics__anzahl_personen_bg: int,
    wohngeld_params: dict,
) -> bool:
    """Wealth is below the eligibility threshold for housing benefits.

    Parameters
    ----------
    demographics__vermögen_bg
        See :func:`demographics__vermögen_bg <demographics__vermögen_bg>`.
    demographics__anzahl_personen_bg
        See :func:`demographics__anzahl_personen_bg`.
    wohngeld_params
        See params documentation :ref:`wohngeld_params <wohngeld_params>`.

    Returns
    -------

    """

    return vermögensprüfung_formel(
        vermögen=demographics__vermögen_bg,
        anzahl_personen=demographics__anzahl_personen_bg,
        params=wohngeld_params,
    )


@policy_function()
def mindesteinkommen_erreicht_wthh(
    arbeitslosengeld_2__regelbedarf_m_wthh: float,
    einkommen_für_mindesteinkommen_check_m_wthh: float,
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
    arbeitslosengeld_2__regelbedarf_m_wthh
        See :func:`arbeitslosengeld_2__regelbedarf_m_wthh`.
    einkommen_für_mindesteinkommen_check_m_wthh
        See :func:`einkommen_für_mindesteinkommen_check_m_wthh`.

    Returns
    -------

    """
    return (
        einkommen_für_mindesteinkommen_check_m_wthh
        >= arbeitslosengeld_2__regelbedarf_m_wthh
    )


@policy_function()
def mindesteinkommen_erreicht_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    einkommen_für_mindesteinkommen_check_m_bg: float,
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
    arbeitslosengeld_2__regelbedarf_m_bg
        See :func:`arbeitslosengeld_2__regelbedarf_m_bg`.
    einkommen_für_mindesteinkommen_check_m_bg
        See :func:`einkommen_für_mindesteinkommen_check_m_bg`.

    Returns
    -------

    """
    return (
        einkommen_für_mindesteinkommen_check_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )


@policy_function()
def einkommen_für_mindesteinkommen_check_m(
    arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m: float,
    unterhalt__kind_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    kindergeld__betrag_m: float,
    kinderzuschlag__anspruchshöhe_m: float,
) -> float:
    """Income for the Mindesteinkommen check.

    Minimum income is defined via VwV 15.01 ff § 15 WoGG.

    According to BMI Erlass of 11.03.2020, Unterhaltsvorschuss, Kinderzuschlag and
    Kindergeld count as income for this check.

    Parameters
    ----------
    arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m
        See :func:`arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m`.
    unterhalt__kind_betrag_m
        See :func:`unterhalt__kind_betrag_m`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    kindergeld__betrag_m
        See :func:`kindergeld__betrag_m`.
    kinderzuschlag__anspruchshöhe_m
        See :func:`kinderzuschlag__anspruchshöhe_m`.

    Returns
    -------

    """

    return (
        arbeitslosengeld_2__nettoeinkommen_vor_abzug_freibetrag_m
        + unterhalt__kind_betrag_m
        + unterhaltsvorschuss__betrag_m
        + kindergeld__betrag_m
        + kinderzuschlag__anspruchshöhe_m
    )


def vermögensprüfung_formel(
    vermögen: float,
    anzahl_personen: int,
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
    anzahl_personen
        Number of people Wohngeld is being calculated for.
    params
        See params documentation :ref:`params <params>`.

    Returns
    -------

    """

    if anzahl_personen == 1:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"]
    else:
        vermögensfreibetrag = params["vermögensgrundfreibetrag"] + params[
            "vermögensfreibetrag_pers"
        ] * (anzahl_personen - 1)

    if vermögen <= vermögensfreibetrag:
        out = True
    else:
        out = False

    return out
