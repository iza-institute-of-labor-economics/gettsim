from _gettsim.shared import policy_info


@policy_info(
    end_date="2004-12-31",
    name_in_dag="betrag_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def betrag_y_sn_bis_2004(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    vorwegabzug_lohnsteuer_2004er_regime_y_sn
        See :func:`vorwegabzug_lohnsteuer_2004er_regime_y_sn`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn`.
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn,
        anz_personen_sn=anz_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_info(
    start_date="2005-01-01",
    end_date="2019-12-31",
    name_in_dag="betrag_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def betrag_mit_günstigerprüfung_y_sn(
    betrag_regime_bis_2004_y_sn: float,
    betrag_vor_günstigerprüfung_y_sn: float,
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
    betrag_y_sn
        See :func:`betrag_y_sn`.
    betrag_regime_bis_2004_y_sn
        See :func:`betrag_regime_bis_2004_y_sn`.

    Returns
    -------

    """

    return max(betrag_regime_bis_2004_y_sn, betrag_vor_günstigerprüfung_y_sn)


@policy_info(
    start_date="2020-01-01",
    name_in_dag="betrag_y_sn",
    params_key_for_rounding="eink_st_abzuege",
)
def betrag_ohne_günstigerprüfung_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherungsbeitraege__pflegeversicherung__betrag_m_sn: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m_sn: float,
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    return formel_2020er_regime(
        alter_aufwendungen=altersvorsorge_y_sn,
        pv_aufwendungen=sozialversicherungsbeitraege__pflegeversicherung__betrag_m_sn,
        kv_aufwendungen=sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m_sn,
        av_aufwendungen=sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m_sn,
        anz_personen_sn=anz_personen_sn,
        minderung_kv_beitrag=eink_st_abzuege_params["vorsorge_kranken_minderung"],
        maximalbetrag_sonstige_aufwendungen=eink_st_abzuege_params[
            "vorsorge_sonstige_aufw_max"
        ],
    )


@policy_info(
    start_date="2005-01-01",
    end_date="2009-12-31",
    name_in_dag="betrag_vor_günstigerprüfung_y_sn",
)
def betrag_vor_günstigerprüfung_bis_2009_y_sn(  # noqa: PLR0913
    altersvorsorge_y_sn: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn: float,
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_y_sn: float,
    sozialversicherungsbeitraege__pflegeversicherung__betrag_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2005 to 2009.

    Parameters
    ----------
    altersvorsorge_y_sn
        See :func:`altersvorsorge_y_sn`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn`.
    sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_y_sn`.
    sozialversicherungsbeitraege__pflegeversicherung__betrag_y_sn
        See :func:`sozialversicherungsbeitraege__pflegeversicherung__betrag_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    sum_vorsorge = (
        sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn
        + sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_y_sn
        + sozialversicherungsbeitraege__pflegeversicherung__betrag_y_sn
    )
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]

    sum_vorsorge = min(sum_vorsorge, max_value)
    out = sum_vorsorge + altersvorsorge_y_sn

    return out


@policy_info(
    start_date="2010-01-01",
    end_date="2019-12-31",
    name_in_dag="betrag_vor_günstigerprüfung_y_sn",
)
def betrag_vor_günstigerprüfung_ab_2010_bis_2019_y_sn(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorsorgeaufwendungen before favorability checks from 2010 to 2019.

    Parameters
    ----------
    vorwegabzug_lohnsteuer_2004er_regime_y_sn
        See :func:`vorwegabzug_lohnsteuer_2004er_regime_y_sn`.
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn`.
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn,
        anz_personen_sn=anz_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_info(
    start_date="2005-01-01",
    end_date="2022-12-31",
    name_in_dag="altersvorsorge_y_sn",
)
def altersvorsorge_phase_in_y_sn(
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m_sn: float,
    priv_rentenv_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m_sn
        See :func:`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m_sn`.
    priv_rentenv_beitr_m_sn
        See :func:`priv_rentenv_beitr_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        eink_st_abzuege_params["einführungsfaktor_vorsorgeaufwand_alter_ab_2005"]
        * (
            2
            * sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m_sn
            + priv_rentenv_beitr_m_sn
        )
        - sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m_sn
    ) * 12
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    out = min(out, max_value)

    return out


@policy_info(start_date="2023-01-01", name_in_dag="altersvorsorge_y_sn")
def altersvorsorge_volle_anrechnung_y_sn(
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn: float,
    priv_rentenv_beitr_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Contributions to retirement savings deductible from taxable income.

    Parameters
    ----------
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn
        See :func:`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn`.
    priv_rentenv_beitr_y_sn
        See :func:`priv_rentenv_beitr_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn
        + priv_rentenv_beitr_y_sn
    )
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_altersaufw_max"]

    return min(out, max_value)


@policy_info(
    start_date="2005-01-01",
    end_date="2019-12-31",
)
def betrag_regime_bis_2004_y_sn(
    vorwegabzug_lohnsteuer_2004er_regime_y_sn: float,
    sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn: float,
    sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    return formel_2004er_regime(
        vorwegabzug_lohnsteuer=vorwegabzug_lohnsteuer_2004er_regime_y_sn,
        krankenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_y_sn,
        rentenversicherung_beitrag_arbeitnehmer=sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_y_sn,
        anz_personen_sn=anz_personen_sn,
        grundhöchstbetrag=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )


@policy_info(end_date="2019-12-31")
def vorwegabzug_lohnsteuer_2004er_regime_y_sn(
    bruttolohn_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Vorwegabzug for Vorsorgeaufwendungen via Lohnsteuer.

    Parameters
    ----------
    bruttolohn_m_sn
        See :func:`bruttolohn_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (1 / anz_personen_sn) * (
        anz_personen_sn * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"] * bruttolohn_y_sn
    )

    return max(out, 0.0)


def formel_2020er_regime(  # noqa: PLR0913
    alter_aufwendungen: float,
    pv_aufwendungen: float,
    kv_aufwendungen: float,
    av_aufwendungen: float,
    anz_personen_sn: int,
    minderung_kv_beitrag: float,
    maximalbetrag_sonstige_aufwendungen: float,
) -> float:
    """Formula to calculate Vorsorgeaufwand using the 2020 regime."""
    basiskrankenversicherung = (
        pv_aufwendungen + (1 - minderung_kv_beitrag) * kv_aufwendungen
    )

    sonst_vors_max = maximalbetrag_sonstige_aufwendungen * anz_personen_sn
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
    anz_personen_sn: int,
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

    item_1 = (1 / anz_personen_sn) * multiplikator1

    if item_1 > grundhöchstbetrag:
        multiplikator2 = grundhöchstbetrag
    else:
        multiplikator2 = item_1

    item_2 = (1 / anz_personen_sn) * multiplikator2

    hoechstgrenze_item3 = anz_personen_sn * grundhöchstbetrag

    if (item_1 - item_2) > hoechstgrenze_item3:
        item_3 = 0.5 * hoechstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = vorwegabzug_lohnsteuer + item_2 + item_3

    return out
