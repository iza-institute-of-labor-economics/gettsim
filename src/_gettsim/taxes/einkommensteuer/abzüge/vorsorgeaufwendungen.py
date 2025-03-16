from _gettsim.function_types import policy_function


@policy_function(
    end_date="2004-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_y_sn_bis_2004(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    vorwegabzug_lohnsteuer_2004er_regime_y_sn
        See :func:`vorwegabzug_lohnsteuer_2004er_regime_y_sn`.
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
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherung__rente__beitrag__betrag_versicherter_y_sn,
        anzahl_personen_sn=einkommensteuer__anzahl_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2019-12-31",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_mit_günstigerprüfung_y_sn(
    vorsorgeaufwendungen_regime_bis_2004_y_sn: float,
    vorsorgeaufwendungen_vor_günstigerprüfung_y_sn: float,
) -> float:
    """Vorsorgeaufwendungen from 2005 to 2019.

    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts under the 2004 and 2005 regimes
    and take the more favourable one.

    After a supreme court ruling, the 2005 rule had to be changed in 2010.
    Therefore, one needs to compute amounts under the 2004 and 2010 regimes
    and take the more favourable one. (§10 (3a) EStG).

    Sidenote: The 2010 rules are by construction at least as beneficial as
    the 2005 regime, so there is no need for a separate check.

    Parameters
    ----------
    vorsorgeaufwendungen_y_sn
        See :func:`vorsorgeaufwendungen_y_sn`.
    vorsorgeaufwendungen_regime_bis_2004_y_sn
        See :func:`vorsorgeaufwendungen_regime_bis_2004_y_sn`.

    Returns
    -------

    """

    return max(
        vorsorgeaufwendungen_regime_bis_2004_y_sn,
        vorsorgeaufwendungen_vor_günstigerprüfung_y_sn,
    )


@policy_function(
    start_date="2020-01-01",
    leaf_name="vorsorgeaufwendungen_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def vorsorgeaufwendungen_ohne_günstigerprüfung_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherung__pflege__beitrag__betrag_versicherter_m_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_m_sn: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    return formel_2020er_regime(
        alter_aufwendungen=altersvorsorge_y_sn,
        pv_aufwendungen=sozialversicherung__pflege__beitrag__betrag_versicherter_m_sn,
        kv_aufwendungen=sozialversicherung__kranken__beitrag__betrag_versicherter_m_sn,
        av_aufwendungen=sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m_sn,
        anzahl_personen_sn=einkommensteuer__anzahl_personen_sn,
        minderung_kv_beitrag=eink_st_abzuege_params["vorsorge_kranken_minderung"],
        maximalbetrag_sonstige_aufwendungen=eink_st_abzuege_params[
            "vorsorge_sonstige_aufw_max"
        ],
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2009-12-31",
    leaf_name="vorsorgeaufwendungen_vor_günstigerprüfung_y_sn",
)
def vorsorgeaufwendungen_vor_günstigerprüfung_bis_2009_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__pflege__beitrag__betrag_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2005 to 2009.

    Parameters
    ----------
    altersvorsorge_y_sn
        See :func:`altersvorsorge_y_sn`.
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn
        See :func:`sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_y_sn`.
    sozialversicherung__pflege__beitrag__betrag_y_sn
        See :func:`sozialversicherung__pflege__beitrag__betrag_y_sn`.
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
        + sozialversicherung__pflege__beitrag__betrag_y_sn
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
    end_date="2019-12-31",
    leaf_name="vorsorgeaufwendungen_vor_günstigerprüfung_y_sn",
)
def vorsorgeaufwendungen_vor_günstigerprüfung_ab_2010_bis_2019_y_sn(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2010 to 2019.

    Parameters
    ----------
    vorwegabzug_lohnsteuer_2004er_regime_y_sn
        See :func:`vorwegabzug_lohnsteuer_2004er_regime_y_sn`.
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
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherung__rente__beitrag__betrag_versicherter_y_sn,
        anzahl_personen_sn=einkommensteuer__anzahl_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_function(
    start_date="2005-01-01",
    end_date="2022-12-31",
    leaf_name="altersvorsorge_y_sn",
)
def altersvorsorge_phase_in_y_sn(
    sozialversicherung__rente__beitrag__betrag_versicherter_m_sn: float,
    beitrag_private_rentenversicherung_m_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    sozialversicherung__rente__beitrag__betrag_versicherter_m_sn
        See :func:`sozialversicherung__rente__beitrag__betrag_versicherter_m_sn`.
    beitrag_private_rentenversicherung_m_sn
        See :func:`beitrag_private_rentenversicherung_m_sn`.
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
            2 * sozialversicherung__rente__beitrag__betrag_versicherter_m_sn
            + beitrag_private_rentenversicherung_m_sn
        )
        - sozialversicherung__rente__beitrag__betrag_versicherter_m_sn
    ) * 12
    max_value = (
        einkommensteuer__anzahl_personen_sn
        * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    )
    out = min(out, max_value)

    return out


@policy_function(start_date="2023-01-01", leaf_name="altersvorsorge_y_sn")
def altersvorsorge_volle_anrechnung_y_sn(
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


@policy_function(
    start_date="2005-01-01",
    end_date="2019-12-31",
)
def vorsorgeaufwendungen_regime_bis_2004_y_sn(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn: float,
    sozialversicherung__rente__beitrag__betrag_versicherter_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherung__kranken__beitrag__betrag_versicherter_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherung__rente__beitrag__betrag_versicherter_y_sn,
        anzahl_personen_sn=einkommensteuer__anzahl_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_function(end_date="2019-12-31")
def vorwegabzug_lohnsteuer_2004er_regime_y_sn(
    einnahmen__bruttolohn_y_sn: float,
    einkommensteuer__anzahl_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorwegabzug for Vorsorgeaufwendungen via Lohnsteuer.

    Parameters
    ----------
    einnahmen__bruttolohn_m_sn
        See :func:`einnahmen__bruttolohn_m_sn`.
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
        * einnahmen__bruttolohn_y_sn
    )

    return max(out, 0.0)


def formel_2020er_regime(  # noqa: PLR0913
    alter_aufwendungen: float,
    pv_aufwendungen: float,
    kv_aufwendungen: float,
    av_aufwendungen: float,
    anzahl_personen_sn: int,
    minderung_kv_beitrag: float,
    maximalbetrag_sonstige_aufwendungen: float,
) -> float:
    """Formula to calculate Vorsorgeaufwand using the 2020 regime."""
    basiskrankenversicherung = (
        pv_aufwendungen + (1 - minderung_kv_beitrag) * kv_aufwendungen
    )

    sonst_vors_max = maximalbetrag_sonstige_aufwendungen * anzahl_personen_sn
    sonst_vors_before_basiskrankenv = min(
        (av_aufwendungen + pv_aufwendungen + kv_aufwendungen),
        sonst_vors_max,
    )

    # Basiskrankenversicherung can always be deducted even if above sonst_vors_max
    sonst_vors = max(basiskrankenversicherung, sonst_vors_before_basiskrankenv)

    out = sonst_vors + alter_aufwendungen
    return out


def formel_2004er_regime(
    vorwegabzug_lohnsteuer: float,
    rentenversicherung_beitrag_arbeitnehmer: float,
    krankenversicherung_beitrag_arbeitnehmer: float,
    anzahl_personen_sn: int,
    grundhöchstbetrag: float,
) -> float:
    """Formula to calculate Vorsorgeaufwand using the pre-2005 regime."""
    multiplikator1 = max(
        (
            (
                rentenversicherung_beitrag_arbeitnehmer
                + krankenversicherung_beitrag_arbeitnehmer
            )
            - vorwegabzug_lohnsteuer
        ),
        0.0,
    )

    item_1 = (1 / anzahl_personen_sn) * multiplikator1

    if item_1 > grundhöchstbetrag:
        multiplikator2 = grundhöchstbetrag
    else:
        multiplikator2 = item_1

    item_2 = (1 / anzahl_personen_sn) * multiplikator2

    höchstgrenze_item3 = anzahl_personen_sn * grundhöchstbetrag

    if (item_1 - item_2) > höchstgrenze_item3:
        item_3 = 0.5 * höchstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = vorwegabzug_lohnsteuer + item_2 + item_3

    return out
