from _gettsim.shared import add_rounding_spec, dates_active


@dates_active(
    start="2005-01-01", end="2022-12-31", change_name="vorsorgeaufw_alter_y_tu"
)
def vorsorgeaufw_alter_y_tu_einfuehrung(
    ges_rentenv_beitr_m_tu: float,
    priv_rentenv_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Determine contributions to retirement savings deductible from taxable income.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    priv_rentenv_beitr_m_tu
        See :func:`priv_rentenv_beitr_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        eink_st_abzuege_params["einführungsfaktor_vorsorgeaufw_alter_ab_2005"]
        * (2 * ges_rentenv_beitr_m_tu + priv_rentenv_beitr_m_tu)
        - ges_rentenv_beitr_m_tu
    ) * 12
    max_value = anz_erwachsene_tu * eink_st_abzuege_params["vorsorge_altersaufw_max"]
    out = min(out, max_value)

    return out


@dates_active(start="2023-01-01")
def vorsorgeaufw_alter_y_tu(
    ges_rentenv_beitr_m_tu: float,
    priv_rentenv_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Determine contributions to retirement savings deductible from taxable income.

    Parameters
    ----------
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    priv_rentenv_beitr_m_tu
        See :func:`priv_rentenv_beitr_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (ges_rentenv_beitr_m_tu + priv_rentenv_beitr_m_tu) * 12
    max_value = anz_erwachsene_tu * eink_st_abzuege_params["vorsorge_altersaufw_max"]

    return min(out, max_value)


@dates_active(
    start="2005-01-01",
    end="2009-12-31",
    change_name="einführung_vorsorgeaufw_y_tu",
)
def einführung_vorsorgeaufw_y_tu_ab_2005_bis_2009(  # noqa: PLR0913
    vorsorgeaufw_alter_y_tu: float,
    ges_krankenv_beitr_m_tu: float,
    arbeitsl_v_beitr_m_tu: float,
    ges_pflegev_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen from 2005 to 2009, new mode.

    Parameters
    ----------
    vorsorgeaufw_alter_y_tu
        See :func:`vorsorgeaufw_alter_y_tu`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    arbeitsl_v_beitr_m_tu
        See :func:`arbeitsl_v_beitr_m_tu`.
    ges_pflegev_beitr_m_tu
        See :func:`ges_pflegev_beitr_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    sum_vorsorge = 12 * (
        ges_krankenv_beitr_m_tu + arbeitsl_v_beitr_m_tu + ges_pflegev_beitr_m_tu
    )
    max_value = anz_erwachsene_tu * eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]

    sum_vorsorge = min(sum_vorsorge, max_value)
    out = sum_vorsorge + vorsorgeaufw_alter_y_tu

    return out


@dates_active(start="2005-01-01", end="2019-12-31", change_name="vorsorgeaufw_y_tu")
@add_rounding_spec(params_key="eink_st_abzuege")
def vorsorgeaufw_y_tu_guenstiger(
    vorsorgeaufw_y_tu_bis_2004: float,
    einführung_vorsorgeaufw_y_tu: float,
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
    vorsorgeaufw_y_tu
        See :func:`vorsorgeaufw_y_tu`.
    vorsorgeaufw_y_tu_bis_2004
        See :func:`vorsorgeaufw_y_tu_bis_2004`.

    Returns
    -------

    """

    return max(vorsorgeaufw_y_tu_bis_2004, einführung_vorsorgeaufw_y_tu)


@dates_active(
    start="2010-01-01",
    end="2019-12-31",
    change_name="einführung_vorsorgeaufw_y_tu",
)
def einführung_vorsorgeaufw_y_tu_ab_2010_bis_2019(
    vorsorgeaufw_y_tu_ab_2020: float,
) -> float:
    return vorsorgeaufw_y_tu_ab_2020


@dates_active(start="2020-01-01", change_name="vorsorgeaufw_y_tu")
@add_rounding_spec(params_key="eink_st_abzuege")
def _vorsorgeaufw_y_tu_ab_2020(vorsorgeaufw_y_tu_ab_2020: float) -> float:
    return vorsorgeaufw_y_tu_ab_2020


def vorsorgeaufw_y_tu_ab_2020(  # noqa: PLR0913
    vorsorgeaufw_alter_y_tu: float,
    ges_pflegev_beitr_m_tu: float,
    ges_krankenv_beitr_m_tu: float,
    arbeitsl_v_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen since 2020.

    Vorsorgeaufwendungen after the regime implemented in 2010 is in full effect,
    see § 10 (3) EStG.

    Parameters
    ----------
    vorsorgeaufw_alter_y_tu
        See :func:`vorsorgeaufw_alter_y_tu`.
    ges_pflegev_beitr_m_tu
        See :func:`ges_pflegev_beitr_m_tu`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    arbeitsl_v_beitr_m_tu
        See :func:`arbeitsl_v_beitr_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    basiskrankenversicherung = 12 * (
        ges_pflegev_beitr_m_tu
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * ges_krankenv_beitr_m_tu
    )

    sonst_vors_max = (
        eink_st_abzuege_params["vorsorge_sonstige_aufw_max"] * anz_erwachsene_tu
    )
    sonst_vors_before_basiskrankenv = min(
        12 * (arbeitsl_v_beitr_m_tu + ges_pflegev_beitr_m_tu + ges_krankenv_beitr_m_tu),
        sonst_vors_max,
    )

    # Basiskrankenversicherung can always be deducted even if above sonst_vors_max
    sonst_vors = max(basiskrankenversicherung, sonst_vors_before_basiskrankenv)

    out = sonst_vors + vorsorgeaufw_alter_y_tu
    return out


@dates_active(
    start="2005-01-01", end="2019-12-31", change_name="vorsorgeaufw_y_tu_bis_2004"
)
def _vorsorgeaufw_y_tu_bis_2004(
    _vorsorgeaufw_vom_lohn_y_tu_bis_2004: float,
    ges_krankenv_beitr_m_tu: float,
    ges_rentenv_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    return vorsorgeaufw_y_tu_bis_2004(
        _vorsorgeaufw_vom_lohn_y_tu_bis_2004=_vorsorgeaufw_vom_lohn_y_tu_bis_2004,
        ges_krankenv_beitr_m_tu=ges_krankenv_beitr_m_tu,
        ges_rentenv_beitr_m_tu=ges_rentenv_beitr_m_tu,
        anz_erwachsene_tu=anz_erwachsene_tu,
        eink_st_abzuege_params=eink_st_abzuege_params,
    )


@dates_active(
    end="2004-12-31",
    change_name="vorsorgeaufw_y_tu",
)
@add_rounding_spec(params_key="eink_st_abzuege")
def vorsorgeaufw_y_tu_bis_2004(
    _vorsorgeaufw_vom_lohn_y_tu_bis_2004: float,
    ges_krankenv_beitr_m_tu: float,
    ges_rentenv_beitr_m_tu: float,
    anz_erwachsene_tu: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    _vorsorgeaufw_vom_lohn_y_tu_bis_2004
        See :func:`_vorsorgeaufw_vom_lohn_y_tu_bis_2004`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    multiplikator1 = max(
        (
            12 * (ges_rentenv_beitr_m_tu + ges_krankenv_beitr_m_tu)
            - _vorsorgeaufw_vom_lohn_y_tu_bis_2004
        ),
        0.0,
    )

    item_1 = (1 / anz_erwachsene_tu) * multiplikator1

    if item_1 > eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]:
        multiplikator2 = eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    else:
        multiplikator2 = item_1

    item_2 = (1 / anz_erwachsene_tu) * multiplikator2

    hoechstgrenze_item3 = (
        anz_erwachsene_tu * eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )

    if (item_1 - item_2) > hoechstgrenze_item3:
        item_3 = 0.5 * hoechstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = _vorsorgeaufw_vom_lohn_y_tu_bis_2004 + item_2 + item_3

    return out


@dates_active(end="2019-12-31")
def _vorsorgeaufw_vom_lohn_y_tu_bis_2004(
    bruttolohn_m_tu: float,
    gemeinsam_veranlagt_tu: bool,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate precautionary expenditures until 2019 for singles.

    Parameters
    ----------
    bruttolohn_m_tu
        See :func:`bruttolohn_m_tu`.
    gemeinsam_veranlagt_tu
        See :func:`gemeinsam_veranlagt_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    if gemeinsam_veranlagt_tu:
        out = 0.5 * (
            2 * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
            - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
            * 12
            * bruttolohn_m_tu
        )
    else:
        out = (
            eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
            - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
            * 12
            * bruttolohn_m_tu
        )

    return max(out, 0.0)
