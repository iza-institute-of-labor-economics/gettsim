from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def vorsorgeaufw_alter_ab_2005(
    kind: BoolSeries,
    ges_rentenv_beitr_m: FloatSeries,
    priv_rentenv_beitr_m: FloatSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
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

    out = (
        eink_st_abzüge_params["einführungsfaktor_vorsorgeaufw_alter_ab_2005"]
        * (2 * ges_rentenv_beitr_m + priv_rentenv_beitr_m)
        - ges_rentenv_beitr_m
    ) * 12

    if kind:
        return 0
    elif out > eink_st_abzüge_params["vorsorge_altersaufw_max"]:
        return eink_st_abzüge_params["vorsorge_altersaufw_max"]
    else:
        return out


def _vorsorge_alternative_ab_2005_bis_2009(
    vorsorgeaufw_alter_ab_2005: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
    ges_pflegev_beitr_m: FloatSeries,
    kind: BoolSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    sum_vorsorge = 12 * (
        ges_krankenv_beitr_m + arbeitsl_v_beitr_m + ges_pflegev_beitr_m
    )
    if sum_vorsorge > eink_st_abzüge_params["vorsorge_sonstige_aufw_max"]:
        sum_vorsorge = eink_st_abzüge_params["vorsorge_sonstige_aufw_max"]
    else:
        sum_vorsorge = sum_vorsorge

    if not kind:
        return sum_vorsorge + vorsorgeaufw_alter_ab_2005
    else:
        return 0


def vorsorgeaufw_ab_2005_bis_2009(
    _vorsorge_alternative_ab_2005_bis_2009: FloatSeries,
    vorsorgeaufw_bis_2004: FloatSeries,
) -> FloatSeries:
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
    if vorsorgeaufw_bis_2004 < _vorsorge_alternative_ab_2005_bis_2009:
        return _vorsorge_alternative_ab_2005_bis_2009
    else:
        return vorsorgeaufw_bis_2004


def vorsorgeaufw_ab_2010_bis_2019(
    vorsorgeaufw_bis_2004: FloatSeries, vorsorgeaufw_ab_2020: FloatSeries
) -> FloatSeries:
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
    if vorsorgeaufw_bis_2004 < vorsorgeaufw_ab_2020:
        return vorsorgeaufw_ab_2020
    else:
        return vorsorgeaufw_bis_2004


def vorsorgeaufw_ab_2020(
    vorsorgeaufw_alter_ab_2005: FloatSeries,
    ges_pflegev_beitr_m: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
    kind: BoolSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    _vorsorgeaufw_vom_lohn_bis_2019_single: FloatSeries,
    _vorsorgeaufw_vom_lohn_bis_2019_tu: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    ges_rentenv_beitr_m: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    ges_rentenv_beitr_m_tu: FloatSeries,
    gemeinsam_veranlagt_tu: BoolSeries,
    kind: BoolSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    if (not gemeinsam_veranlagt_tu) & (not kind):
        out = _berechne_vorsorgeaufw_bis_2004(
            _vorsorgeaufw_vom_lohn_bis_2019_single,
            ges_krankenv_beitr_m,
            ges_rentenv_beitr_m,
            1,
            eink_st_abzüge_params,
        )
    elif (gemeinsam_veranlagt_tu) & (not kind):
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
    bruttolohn_m: FloatSeries, eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    bruttolohn_m_tu: FloatSeries, eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    lohn_vorsorge: FloatSeries,
    ges_krankenv_beitr: FloatSeries,
    ges_rentenv_beitr: FloatSeries,
    anzahl_erwachsene: IntSeries,
    eink_st_abzüge_params: dict,
) -> FloatSeries:
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
    item_1 = (1 / anzahl_erwachsene) * (
        12 * (ges_rentenv_beitr + ges_krankenv_beitr) - lohn_vorsorge
    ).clip(lower=0)
    item_2 = (1 / anzahl_erwachsene) * item_1.clip(
        upper=eink_st_abzüge_params["vorsorge_2004_grundhöchstbetrag"]
    )

    item_3 = 0.5 * (item_1 - item_2).clip(
        upper=anzahl_erwachsene
        * eink_st_abzüge_params["vorsorge_2004_grundhöchstbetrag"]
    )
    out = int(lohn_vorsorge + item_2 + item_3)
    return out
