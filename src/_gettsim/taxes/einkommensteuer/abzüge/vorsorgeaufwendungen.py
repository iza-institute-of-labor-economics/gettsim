from _gettsim.function_types import policy_function


@policy_function(
    end_date="2004-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_y_sn_bis_2004(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    vorsorgeaufwendungen_regime_bis_2004_y_sn
        See :func:`vorsorgeaufwendungen_regime_bis_2004_y_sn`.

    Returns
    -------

    """
    return vorsorgeaufwendungen_regime_bis_2004_y_sn


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_y_sn_ab_2005_bis_2009(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
    vorsorgeaufwendungen_globale_kappung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen from 2005 to 2009.

    Günstigerprüfung against the pre-2005 regime.

    Parameters
    ----------
    vorsorgeaufwendungen_regime_bis_2004_y_sn
        See :func:`vorsorgeaufwendungen_regime_bis_2004_y_sn`.
    vorsorgeaufwendungen_globale_kappung_y_sn
        See :func:`vorsorgeaufwendungen_globale_kappung_y_sn`.

    Returns
    -------

    """

    return max(
        vorsorgeaufwendungen_regime_bis_2004_y_sn,
        vorsorgeaufwendungen_globale_kappung_y_sn,
    )


@policy_function(
    start_date="2010-01-01",
    end_date="2019-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_y_sn_ab_2010_bis_2019(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen from 2010 to 2019.

    Günstigerprüfung against the pre-2005 regime.

    Parameters
    ----------
    vorsorgeaufwendungen_regime_bis_2004_y_sn
        See :func:`vorsorgeaufwendungen_regime_bis_2004_y_sn`.
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn
        See :func:`vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn`.

    Returns
    -------

    """

    return max(
        vorsorgeaufwendungen_regime_bis_2004_y_sn,
        vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn,
    )


@policy_function(
    start_date="2020-01-01",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_y_sn_ab_2020(
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen since 2020.

    Günstigerprüfung against the regime before 2005 revoked.

    Parameters
    ----------
    vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn
        See :func:`vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn`.

    Returns
    -------

    """
    return vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn


@policy_function(
    end_date="2019-12-31",
)
def vorsorgeaufwendungen_regime_bis_2004_y_sn(
    vorwegabzug_lohnsteuer_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen calculated using the pre-2005 regime.

    Parameters
    ----------
    vorwegabzug_lohnsteuer_y_sn
        See :func:`vorwegabzug_lohnsteuer_y_sn`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__rente__beitrag__betrag_versicherter_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    multiplikator1 = max(
        (
            (
                sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
                + sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
            )
            - vorwegabzug_lohnsteuer_y_sn
        ),
        0.0,
    )

    item_1 = (1 / einkommensteuer__anzahl_personen_sn) * multiplikator1

    höchstbetrag = eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]

    if item_1 > höchstbetrag:
        multiplikator2 = höchstbetrag
    else:
        multiplikator2 = item_1

    item_2 = (1 / einkommensteuer__anzahl_personen_sn) * multiplikator2

    höchstgrenze_item3 = einkommensteuer__anzahl_personen_sn * höchstbetrag

    if (item_1 - item_2) > höchstgrenze_item3:
        item_3 = 0.5 * höchstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = vorwegabzug_lohnsteuer_y_sn + item_2 + item_3

    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
)
def vorsorgeaufwendungen_globale_kappung_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2005 to 2009.

    All deductions for social insurance contributions are capped.

    Parameters
    ----------
    altersvorsorge_y_sn
        See :func:`altersvorsorge_y_sn`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    sum_vorsorge = (
        sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        + sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn
        + sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn
    )
    max_value = (
        einkommensteuer__anzahl_personen_sn
        * eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]
    )

    sum_vorsorge = min(sum_vorsorge, max_value)
    out = sum_vorsorge + altersvorsorge_y_sn

    return out


@policy_function(
    start_date="2010-01-01",
)
def vorsorgeaufwendungen_keine_kappung_krankenversicherung_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen.

    Expenses for health insurance contributions are not subject to any caps.

    Parameters
    ----------
    altersvorsorge_y_sn
        See :func:`altersvorsorge_y_sn`.
    sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    basiskrankenversicherung = (
        sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
    )

    sonst_vors_max = (
        eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]
        * einkommensteuer__anzahl_personen_sn
    )
    sonst_vors_before_basiskrankenv = min(
        (
            sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn
            + sozialversicherung__pflege__beitrag__betrag_versicherter_y_sn
            + sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        ),
        sonst_vors_max,
    )

    # Basiskrankenversicherung can always be deducted even if above sonst_vors_max
    sonst_vors = max(basiskrankenversicherung, sonst_vors_before_basiskrankenv)

    out = sonst_vors + altersvorsorge_y_sn
    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="altersvorsorge_y_sn",
)
def altersvorsorge_y_sn_phase_in(
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    beitrag_private_rentenversicherung_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__rente__beitrag__betrag_versicherter_y_sn`.
    beitrag_private_rentenversicherung_y_sn
        See :func:`beitrag_private_rentenversicherung_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        eink_st_abzuege_params["einführungsfaktor_vorsorgeaufwendungen_alter_ab_2005"]
        * (
            2 * sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
            + beitrag_private_rentenversicherung_y_sn
        )
        - sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
    )
    max_value = (
        einkommensteuer__anzahl_personen_sn
        * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    )
    out = min(out, max_value)

    return out


@policy_function(start_date="2023-01-01", leaf_name="altersvorsorge_y_sn")
def altersvorsorge_y_sn_volle_anrechnung(
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    beitrag_private_rentenversicherung_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    Parameters
    ----------
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__rente__beitrag__betrag_versicherter_y_sn`.
    beitrag_private_rentenversicherung_y_sn
        See :func:`beitrag_private_rentenversicherung_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        sozialversicherung__rente__beitrag__betrag_versicherter_y_sn
        + beitrag_private_rentenversicherung_y_sn
    )
    max_value = (
        einkommensteuer__anzahl_personen_sn
        * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    )

    return min(out, max_value)


@policy_function(end_date="2019-12-31")
def vorwegabzug_lohnsteuer_y_sn(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorwegabzug for Vorsorgeaufwendungen via Lohnsteuer.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y_sn
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y_sn`.
    einkommensteuer__anzahl_personen_sn
        See :func:`einkommensteuer__anzahl_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (1 / einkommensteuer__anzahl_personen_sn) * (
        einkommensteuer__anzahl_personen_sn
        * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_y_sn
    )

    return max(out, 0.0)
