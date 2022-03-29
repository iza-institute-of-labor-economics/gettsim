def vorsorgeaufw_alter_ab_2005(
    kind: bool,
    ges_rentenv_beitr_m: float,
    priv_rentenv_beitr_m: float,
    eink_st_abzüge_params: dict,
) -> float:
    """Determine contributions to retirement savings deductible from taxable income.

    This function becomes relevant in 2005, do not use it for prior
    year.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.

    Parameters
    ----------
    kind
        See basic input variable :ref:`kind <kind>`.
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.
    priv_rentenv_beitr_m
        See basic input variable :ref:`priv_rentenv_beitr_m <priv_rentenv_beitr_m>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """

    if kind:
        out = 0.0
    else:
        out = (
            eink_st_abzüge_params["einführungsfaktor_vorsorgeaufw_alter_ab_2005"]
            * (2 * ges_rentenv_beitr_m + priv_rentenv_beitr_m)
            - ges_rentenv_beitr_m
        ) * 12
        out = min(out, eink_st_abzüge_params["vorsorge_altersaufw_max"])

    return out


def _vorsorge_alternative_ab_2005_bis_2009(
    vorsorgeaufw_alter_ab_2005: float,
    ges_krankenv_beitr_m: float,
    arbeitsl_v_beitr_m: float,
    ges_pflegev_beitr_m: float,
    kind: bool,
    eink_st_abzüge_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen from 2005 to 2010.


    Pension contributions are accounted for up to €20k. From this, a certain share
    can actually be deducted, starting with 60% in 2005. Other deductions are simply
    added up, up to a ceiling of 1500 p.a. for standard employees.

    Parameters
    ----------
    vorsorgeaufw_alter_ab_2005
        See :func:`vorsorgeaufw_alter_ab_2005`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.
    ges_pflegev_beitr_m
        See :func:`ges_pflegev_beitr_m`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """

    if kind:
        out = 0.0
    else:
        sum_vorsorge = 12 * (
            ges_krankenv_beitr_m + arbeitsl_v_beitr_m + ges_pflegev_beitr_m
        )
        sum_vorsorge = min(
            sum_vorsorge, eink_st_abzüge_params["vorsorge_sonstige_aufw_max"]
        )
        out = sum_vorsorge + vorsorgeaufw_alter_ab_2005

    return out


def vorsorgeaufw_ab_2005_bis_2009(
    _vorsorge_alternative_ab_2005_bis_2009: float,
    vorsorgeaufw_bis_2004: float,
) -> float:
    """Calculate Vorsorgeaufwendungen from 2005 to 2009.

    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts under the 2004 and 2005 regimes
    and take the more favourable one.

    Parameters
    ----------
    _vorsorge_alternative_ab_2005_bis_2009
        See :func:`_vorsorge_alternative_ab_2005_bis_2009`.
    vorsorgeaufw_bis_2004
        See :func:`vorsorgeaufw_bis_2004`.

    Returns
    -------

    """
    out = max(vorsorgeaufw_bis_2004, _vorsorge_alternative_ab_2005_bis_2009)

    return out


def vorsorgeaufw_ab_2010_bis_2019(
    vorsorgeaufw_bis_2004: float, vorsorgeaufw_ab_2020: float
) -> float:
    """Calculate Vorsorgeaufwendungen from 2010 to 2019.

    After a supreme court ruling, the 2005 rule had to be changed in 2010.
    Therefore, one needs to compute amounts under the 2004 and 2010 regimes
    and take the more favourable one. (§10 (3a) EStG).

    Sidenote: The 2010 rules are by construction at least as beneficial as
    the 2005 regime, so there is no need for a separate check.


    Parameters
    ----------
    vorsorgeaufw_bis_2004
        See :func:`vorsorgeaufw_bis_2004`.
    vorsorgeaufw_ab_2020
        See :func:`vorsorgeaufw_ab_2020`.

    Returns
    -------

    """
    out = max(vorsorgeaufw_bis_2004, vorsorgeaufw_ab_2020)

    return out


def vorsorgeaufw_ab_2020(
    vorsorgeaufw_alter_ab_2005: float,
    ges_pflegev_beitr_m: float,
    ges_krankenv_beitr_m: float,
    arbeitsl_v_beitr_m: float,
    kind: bool,
    eink_st_abzüge_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen since 2020.

    Vorsorgeaufwendungen after the regime implemented in 2010 is in full effect,
    see § 10 (3) EStG.

    Parameters
    ----------
    vorsorgeaufw_alter_ab_2005
        See :func:`vorsorgeaufw_alter_ab_2005`.
    ges_pflegev_beitr_m
        See :func:`ges_pflegev_beitr_m`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    # maybe add unemployment insurance, but do not exceed 1900€.
    if kind:
        out = 0.0
    else:
        sonstige_vors = 12 * (
            ges_pflegev_beitr_m
            + (1 - eink_st_abzüge_params["vorsorge_kranken_minderung"])
            * ges_krankenv_beitr_m
        )
        limit_below = sonstige_vors + 12 * arbeitsl_v_beitr_m
        limit_above = eink_st_abzüge_params["vorsorge_sonstige_aufw_max"]

        out = min(max(sonstige_vors, limit_below), limit_above)
        out += vorsorgeaufw_alter_ab_2005
    return out


def vorsorgeaufw_bis_2004(
    _vorsorgeaufw_vom_lohn_bis_2019_single: float,
    _vorsorgeaufw_vom_lohn_bis_2019_tu: float,
    ges_krankenv_beitr_m: float,
    ges_rentenv_beitr_m: float,
    ges_krankenv_beitr_m_tu: float,
    ges_rentenv_beitr_m_tu: float,
    gemeinsam_veranlagt_tu: bool,
    kind: bool,
    eink_st_abzüge_params: dict,
) -> float:
    """Calculate Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    _vorsorgeaufw_vom_lohn_bis_2019_single
        See :func:`_vorsorgeaufw_vom_lohn_bis_2019_single`.
    _vorsorgeaufw_vom_lohn_bis_2019_tu
        See :func:`_vorsorgeaufw_vom_lohn_bis_2019_tu`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    gemeinsam_veranlagt_tu
        See :func:`gemeinsam_veranlagt_tu`.
    kind
        See basic input variable :ref:`kind <kind>`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    if (not gemeinsam_veranlagt_tu) and (not kind):
        out = _berechne_vorsorgeaufw_bis_2004(
            _vorsorgeaufw_vom_lohn_bis_2019_single,
            ges_krankenv_beitr_m,
            ges_rentenv_beitr_m,
            1,
            eink_st_abzüge_params,
        )
    elif (gemeinsam_veranlagt_tu) and (not kind):
        out = _berechne_vorsorgeaufw_bis_2004(
            _vorsorgeaufw_vom_lohn_bis_2019_tu,
            ges_krankenv_beitr_m_tu,
            ges_rentenv_beitr_m_tu,
            2,
            eink_st_abzüge_params,
        )
    else:
        out = 0.0

    return out


def _vorsorgeaufw_vom_lohn_bis_2019_single(
    bruttolohn_m: float,
    eink_st_abzüge_params: dict,
) -> float:
    """Calcaulate vorsoge expenditures until 2019 for singles.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    gemeinsam_veranlagt_tu
        See :func:`gemeinsam_veranlagt_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = (
        eink_st_abzüge_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzüge_params["vorsorge2004_kürzung_vorwegabzug"] * 12 * bruttolohn_m
    )
    return max(out, 0.0)


def _vorsorgeaufw_vom_lohn_bis_2019_tu(
    bruttolohn_m_tu: float,
    eink_st_abzüge_params: dict,
) -> float:
    """Calcaulate vorsoge expenditures until 2019 per tax unit.

    Parameters
    ----------
    bruttolohn_m_tu
        See :func:`bruttolohn_m_tu`.
    eink_st_abzüge_params
        See params documentation :ref:`eink_st_abzüge_params <eink_st_abzüge_params>`.

    Returns
    -------

    """
    out = 0.5 * (
        2 * eink_st_abzüge_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzüge_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m_tu
    )

    return max(out, 0.0)


def _berechne_vorsorgeaufw_bis_2004(
    lohn_vorsorge: float,
    ges_krankenv_beitr: float,
    ges_rentenv_beitr: float,
    anzahl_erwachsene: int,
    eink_st_abzüge_params: dict,
) -> float:
    """Calcaulate vorsoge expenditures until 2004.

    Parameters
    ----------
    lohn_vorsorge
    ges_krankenv_beitr
    ges_rentenv_beitr
    anzahl_erwachsene
    eink_st_abzüge_params

    Returns
    -------

    """
    multiplikator1 = max(
        (12 * (ges_rentenv_beitr + ges_krankenv_beitr) - lohn_vorsorge), 0.0
    )

    item_1 = (1 / anzahl_erwachsene) * multiplikator1

    if item_1 > eink_st_abzüge_params["vorsorge_2004_grundhöchstbetrag"]:
        multiplikator2 = eink_st_abzüge_params["vorsorge_2004_grundhöchstbetrag"]
    else:
        multiplikator2 = item_1

    item_2 = (1 / anzahl_erwachsene) * multiplikator2

    hoechstgrenze_item3 = (
        anzahl_erwachsene * eink_st_abzüge_params["vorsorge_2004_grundhöchstbetrag"]
    )

    if (item_1 - item_2) > hoechstgrenze_item3:
        item_3 = 0.5 * hoechstgrenze_item3
    else:
        item_3 = 0.5 * (item_1 - item_2)

    out = lohn_vorsorge + item_2 + item_3
    return out
