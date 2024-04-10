from _gettsim.shared import policy_info


@policy_info(
    start_date="2005-01-01", end_date="2022-12-31", change_name="vorsorgeaufw_alter_y_sn"
)
def vorsorgeaufw_alter_y_sn_einfuehrung(
    ges_rentenv_beitr_m_sn: float,
    priv_rentenv_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Determine contributions to retirement savings deductible from taxable income.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    ges_rentenv_beitr_m_sn
        See :func:`ges_rentenv_beitr_m_sn`.
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
        eink_st_abzuege_params["einführungsfaktor_vorsorgeaufw_alter_ab_2005"]
        * (2 * ges_rentenv_beitr_m_sn + priv_rentenv_beitr_m_sn)
        - ges_rentenv_beitr_m_sn
    ) * 12
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    out = min(out, max_value)

    return out


@policy_info(start_date="2023-01-01")
def vorsorgeaufw_alter_y_sn(
    ges_rentenv_beitr_m_sn: float,
    priv_rentenv_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Determine contributions to retirement savings deductible from taxable income.

    Parameters
    ----------
    ges_rentenv_beitr_m_sn
        See :func:`ges_rentenv_beitr_m_sn`.
    priv_rentenv_beitr_m_sn
        See :func:`priv_rentenv_beitr_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (ges_rentenv_beitr_m_sn + priv_rentenv_beitr_m_sn) * 12
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_altersaufw_max"]

    return min(out, max_value)


@policy_info(
    start_date="2005-01-01",
    end_date="2009-12-31",
    change_name="einführung_vorsorgeaufw_y_sn",
)
def einführung_vorsorgeaufw_y_sn_ab_2005_bis_2009(  # noqa: PLR0913
    vorsorgeaufw_alter_y_sn: float,
    ges_krankenv_beitr_m_sn: float,
    arbeitsl_v_beitr_m_sn: float,
    ges_pflegev_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen from 2005 to 2009, new mode.

    Parameters
    ----------
    vorsorgeaufw_alter_y_sn
        See :func:`vorsorgeaufw_alter_y_sn`.
    ges_krankenv_beitr_m_sn
        See :func:`ges_krankenv_beitr_m_sn`.
    arbeitsl_v_beitr_m_sn
        See :func:`arbeitsl_v_beitr_m_sn`.
    ges_pflegev_beitr_m_sn
        See :func:`ges_pflegev_beitr_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    sum_vorsorge = 12 * (
        ges_krankenv_beitr_m_sn + arbeitsl_v_beitr_m_sn + ges_pflegev_beitr_m_sn
    )
    max_value = anz_personen_sn * eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]

    sum_vorsorge = min(sum_vorsorge, max_value)
    out = sum_vorsorge + vorsorgeaufw_alter_y_sn

    return out


@policy_info(
    start_date="2005-01-01",
    end_date="2019-12-31",
    change_name="vorsorgeaufw_y_sn",
    rounding_key="eink_st_abzuege",
)
def vorsorgeaufw_y_sn_guenstiger(
    vorsorgeaufw_y_sn_bis_2004: float,
    einführung_vorsorgeaufw_y_sn: float,
) -> float:
    """Calculate Vorsorgeaufwendungen from 2005 to 2019.

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
    vorsorgeaufw_y_sn
        See :func:`vorsorgeaufw_y_sn`.
    vorsorgeaufw_y_sn_bis_2004
        See :func:`vorsorgeaufw_y_sn_bis_2004`.

    Returns
    -------

    """

    return max(vorsorgeaufw_y_sn_bis_2004, einführung_vorsorgeaufw_y_sn)


@policy_info(
    start_date="2010-01-01",
    end_date="2019-12-31",
    change_name="einführung_vorsorgeaufw_y_sn",
)
def einführung_vorsorgeaufw_y_sn_ab_2010_bis_2019(
    vorsorgeaufw_y_sn_ab_2020: float,
) -> float:
    return vorsorgeaufw_y_sn_ab_2020


@policy_info(
    start_date="2020-01-01", change_name="vorsorgeaufw_y_sn", rounding_key="eink_st_abzuege"
)
def _vorsorgeaufw_y_sn_ab_2020(vorsorgeaufw_y_sn_ab_2020: float) -> float:
    return vorsorgeaufw_y_sn_ab_2020


def vorsorgeaufw_y_sn_ab_2020(  # noqa: PLR0913
    vorsorgeaufw_alter_y_sn: float,
    ges_pflegev_beitr_m_sn: float,
    ges_krankenv_beitr_m_sn: float,
    arbeitsl_v_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen since 2020.

    Vorsorgeaufwendungen after the regime implemented in 2010 is in full effect,
    see § 10 (3) EStG.

    Parameters
    ----------
    vorsorgeaufw_alter_y_sn
        See :func:`vorsorgeaufw_alter_y_sn`.
    ges_pflegev_beitr_m_sn
        See :func:`ges_pflegev_beitr_m_sn`.
    ges_krankenv_beitr_m_sn
        See :func:`ges_krankenv_beitr_m_sn`.
    arbeitsl_v_beitr_m_sn
        See :func:`arbeitsl_v_beitr_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    basiskrankenversicherung = 12 * (
        ges_pflegev_beitr_m_sn
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * ges_krankenv_beitr_m_sn
    )

    sonst_vors_max = (
        eink_st_abzuege_params["vorsorge_sonstige_aufw_max"] * anz_personen_sn
    )
    sonst_vors_before_basiskrankenv = min(
        12 * (arbeitsl_v_beitr_m_sn + ges_pflegev_beitr_m_sn + ges_krankenv_beitr_m_sn),
        sonst_vors_max,
    )

    # Basiskrankenversicherung can always be deducted even if above sonst_vors_max
    sonst_vors = max(basiskrankenversicherung, sonst_vors_before_basiskrankenv)

    out = sonst_vors + vorsorgeaufw_alter_y_sn
    return out


@policy_info(
    start_date="2005-01-01", end_date="2019-12-31", change_name="vorsorgeaufw_y_sn_bis_2004"
)
def _vorsorgeaufw_y_sn_bis_2004(
    _vorsorgeaufw_vom_lohn_y_sn_bis_2004: float,
    ges_krankenv_beitr_m_sn: float,
    ges_rentenv_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    return vorsorgeaufw_y_sn_bis_2004(
        _vorsorgeaufw_vom_lohn_y_sn_bis_2004=_vorsorgeaufw_vom_lohn_y_sn_bis_2004,
        ges_krankenv_beitr_m_sn=ges_krankenv_beitr_m_sn,
        ges_rentenv_beitr_m_sn=ges_rentenv_beitr_m_sn,
        anz_personen_sn=anz_personen_sn,
        eink_st_abzuege_params=eink_st_abzuege_params,
    )


@policy_info(
    end_date="2004-12-31", change_name="vorsorgeaufw_y_sn", rounding_key="eink_st_abzuege"
)
def vorsorgeaufw_y_sn_bis_2004(
    _vorsorgeaufw_vom_lohn_y_sn_bis_2004: float,
    ges_krankenv_beitr_m_sn: float,
    ges_rentenv_beitr_m_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    _vorsorgeaufw_vom_lohn_y_sn_bis_2004
        See :func:`_vorsorgeaufw_vom_lohn_y_sn_bis_2004`.
    ges_krankenv_beitr_m_sn
        See :func:`ges_krankenv_beitr_m_sn`.
    ges_rentenv_beitr_m_sn
        See :func:`ges_rentenv_beitr_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    multiplikator1 = max(
        (
            12 * (ges_rentenv_beitr_m_sn + ges_krankenv_beitr_m_sn)
            - _vorsorgeaufw_vom_lohn_y_sn_bis_2004
        ),
        0.0,
    )

    item_1 = (1 / anz_personen_sn) * multiplikator1

    if item_1 > eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]:
        multiplikator2 = eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    else:
        multiplikator2 = item_1

    item_2 = (1 / anz_personen_sn) * multiplikator2

    hoechstgrenze_item3 = (
        anz_personen_sn * eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )

    if (item_1 - item_2) > hoechstgrenze_item3:
        item_3 = 0.5 * hoechstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = _vorsorgeaufw_vom_lohn_y_sn_bis_2004 + item_2 + item_3

    return out


@policy_info(end_date="2019-12-31")
def _vorsorgeaufw_vom_lohn_y_sn_bis_2004(
    bruttolohn_y_sn: float,
    anz_personen_sn: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate precautionary expenditures until 2019 for singles.

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
