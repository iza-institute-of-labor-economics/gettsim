from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def vorsorge_alter_aufwend(
    kind: BoolSeries,
    ges_rentenv_beitr_m: FloatSeries,
    priv_rentenv_beitr_m: FloatSeries,
    eink_st_abzuege_params: dict,
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
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    out = (
        (
            eink_st_abzuege_params["einführungsfaktor_vorsorge_alter_aufwend"]
            * (2 * ges_rentenv_beitr_m + priv_rentenv_beitr_m)
            - ges_rentenv_beitr_m
        )
        * 12
    ).clip(upper=eink_st_abzuege_params["vorsorge_altersaufw_max"])
    out.loc[kind] = 0
    return out


def _vorsorge_alternative_ab_2005_bis_2009(
    vorsorge_alter_aufwend: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
    ges_pflegev_beitr_m: FloatSeries,
    kind: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calculate Vorsorgeaufwendungen from 2005 to 2010.


    Pension contributions are accounted for up to €20k. From this, a certain share
    can actually be deducted, starting with 60% in 2005. Other deductions are simply
    added up, up to a ceiling of 1500 p.a. for standard employees.

    Parameters
    ----------
    vorsorge_alter_aufwend
        See :func:`vorsorge_alter_aufwend`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.
    ges_pflegev_beitr_m
        See :func:`ges_pflegev_beitr_m`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = vorsorge_alter_aufwend * 0
    sum_vorsorge = (
        12 * (ges_krankenv_beitr_m + arbeitsl_v_beitr_m + ges_pflegev_beitr_m)
    ).clip(upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"])
    out.loc[~kind] = sum_vorsorge.loc[~kind] + vorsorge_alter_aufwend.loc[~kind]
    return out


def vorsorge_ab_2005_bis_2009(
    _vorsorge_alternative_ab_2005_bis_2009: FloatSeries, vorsorge_bis_2004: FloatSeries
) -> FloatSeries:
    """Calculate Vorsorgeaufwendungen from 2005 to 2009.

    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts under the 2004 and 2005 regimes
    and take the more favourable one.

    Parameters
    ----------
    _vorsorge_alternative_ab_2005_bis_2009
        See :func:`_vorsorge_alternative_ab_2005_bis_2009`.
    vorsorge_bis_2004
        See :func:`vorsorge_bis_2004`.

    Returns
    -------

    """
    return vorsorge_bis_2004.clip(lower=_vorsorge_alternative_ab_2005_bis_2009)


def vorsorge_ab_2010_bis_2019(
    vorsorge_bis_2004: FloatSeries, vorsorge_ab_2020: FloatSeries
) -> FloatSeries:
    """Calculate Vorsorgeaufwendungen from 2010 to 2019.

    After a supreme court ruling, the 2005 rule had to be changed in 2010.
    Therefore, one needs to compute amounts under the 2004 and 2010 regimes
    and take the more favourable one. (§10 (3a) EStG).

    Sidenote: The 2010 rules are by construction at least as beneficial as
    the 2005 regime, so there is no need for a separate check.


    Parameters
    ----------
    vorsorge_bis_2004
        See :func:`vorsorge_bis_2004`.
    vorsorge_ab_2020
        See :func:`vorsorge_ab_2020`.

    Returns
    -------

    """
    return vorsorge_bis_2004.clip(lower=vorsorge_ab_2020)


def vorsorge_ab_2020(
    vorsorge_alter_aufwend: FloatSeries,
    ges_pflegev_beitr_m: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    arbeitsl_v_beitr_m: FloatSeries,
    kind: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calculate Vorsorgeaufwendungen since 2020.

    Vorsorgeaufwendungen after the regime implemented in 2010 is in full effect,
    see § 10 (3) EStG.

    Parameters
    ----------
    vorsorge_alter_aufwend
        See :func:`vorsorge_alter_aufwend`.
    ges_pflegev_beitr_m
        See :func:`ges_pflegev_beitr_m`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    arbeitsl_v_beitr_m
        See :func:`arbeitsl_v_beitr_m`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = vorsorge_alter_aufwend * 0
    # 'Basisvorsorge': Health and old-age care contributions are deducted anyway.
    sonstige_vors = 12 * (
        ges_pflegev_beitr_m.loc[~kind]
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * ges_krankenv_beitr_m.loc[~kind]
    )
    # maybe add unemployment insurance, but do not exceed 1900€.
    out.loc[~kind] = sonstige_vors.clip(
        lower=(sonstige_vors + 12 * arbeitsl_v_beitr_m.loc[~kind]).clip(
            upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]
        )
    )
    out.loc[~kind] += vorsorge_alter_aufwend.loc[~kind]
    return out


def vorsorge_bis_2004(
    lohn_vorsorge_bis_2019_single: FloatSeries,
    lohn_vorsorgeabzug_bis_2019_tu: FloatSeries,
    ges_krankenv_beitr_m: FloatSeries,
    ges_rentenv_beitr_m: FloatSeries,
    ges_krankenv_beitr_m_tu: FloatSeries,
    ges_rentenv_beitr_m_tu: FloatSeries,
    tu_id: IntSeries,
    gemeinsam_veranlagte_tu: BoolSeries,
    gemeinsam_veranlagt: BoolSeries,
    kind: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calculate Vorsorgeaufwendungen until 2004.

    Parameters
    ----------
    lohn_vorsorge_bis_2019_single
        See :func:`lohn_vorsorge_bis_2019_single`.
    lohn_vorsorgeabzug_bis_2019_tu
        See :func:`lohn_vorsorgeabzug_bis_2019_tu`.
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    ges_rentenv_beitr_m
        See :func:`ges_rentenv_beitr_m`.
    ges_krankenv_beitr_m_tu
        See :func:`ges_krankenv_beitr_m_tu`.
    ges_rentenv_beitr_m_tu
        See :func:`ges_rentenv_beitr_m_tu`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.
    gemeinsam_veranlagte_tu
        See :func:`gemeinsam_veranlagte_tu`.
    gemeinsam_veranlagt
        See :func:`gemeinsam_veranlagt`.
    kind
        See basic input variable :ref:`kind <kind>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """

    out = ges_krankenv_beitr_m * 0
    out.loc[~gemeinsam_veranlagt & ~kind] = _berechne_vorsorge_bis_2004(
        lohn_vorsorge_bis_2019_single.loc[~kind],
        ges_krankenv_beitr_m.loc[~gemeinsam_veranlagt & ~kind],
        ges_rentenv_beitr_m.loc[~gemeinsam_veranlagt & ~kind],
        1,
        eink_st_abzuege_params,
    )

    vorsorge_tu = _berechne_vorsorge_bis_2004(
        lohn_vorsorgeabzug_bis_2019_tu,
        ges_krankenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        ges_rentenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        2,
        eink_st_abzuege_params,
    )
    out.loc[gemeinsam_veranlagt & ~kind] = tu_id[gemeinsam_veranlagt].replace(
        vorsorge_tu
    )
    return out


def lohn_vorsorge_bis_2019_single(
    bruttolohn_m: FloatSeries,
    gemeinsam_veranlagt: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calcaulate vorsoge expenditures until 2019 for singles.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    gemeinsam_veranlagt
        See :func:`gemeinsam_veranlagt`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = (
        eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m.loc[~gemeinsam_veranlagt]
    ).clip(lower=0)
    return out


def lohn_vorsorgeabzug_bis_2019_tu(
    bruttolohn_m_tu: FloatSeries,
    gemeinsam_veranlagte_tu: BoolSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calcaulate vorsoge expenditures until 2019 per tax unit.

    Parameters
    ----------
    bruttolohn_m_tu
        See :func:`bruttolohn_m_tu`.
    gemeinsam_veranlagte_tu
        See :func:`gemeinsam_veranlagte_tu`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    out = 0.5 * (
        2 * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m_tu.loc[gemeinsam_veranlagte_tu]
    ).clip(lower=0)
    return out


def _berechne_vorsorge_bis_2004(
    lohn_vorsorge: FloatSeries,
    ges_krankenv_beitr: FloatSeries,
    ges_rentenv_beitr: FloatSeries,
    anzahl_erwachsene: IntSeries,
    eink_st_abzuege_params: dict,
) -> FloatSeries:
    """Calcaulate vorsoge expenditures until 2004.

    Parameters
    ----------
    lohn_vorsorge
    ges_krankenv_beitr
    ges_rentenv_beitr
    anzahl_erwachsene
    eink_st_abzuege_params

    Returns
    -------

    """
    item_1 = (1 / anzahl_erwachsene) * (
        12 * (ges_rentenv_beitr + ges_krankenv_beitr) - lohn_vorsorge
    ).clip(lower=0)
    item_2 = (1 / anzahl_erwachsene) * item_1.clip(
        upper=eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )

    item_3 = 0.5 * (item_1 - item_2).clip(
        upper=anzahl_erwachsene
        * eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )
    out = (lohn_vorsorge + item_2 + item_3).astype(int)
    return out
