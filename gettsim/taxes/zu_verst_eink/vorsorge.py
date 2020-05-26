import copy

import numpy as np

from gettsim._numpy import numpy_vectorize


def _vorsorge_alternative_2005_bis_2009(
    _altervorsorge_aufwend,
    ges_krankenv_beitr_m,
    arbeitsl_v_beitr_m,
    pflegev_beitr_m,
    kind,
    eink_st_abzuege_params,
):
    """
    Vorsorgeaufwendungen 2005 to 2010
    Pension contributions are accounted for up to €20k.
    From this, a certain share can actually be deducted,
    starting with 60% in 2005.
    Other deductions are simply added up, up to a ceiling of 1500 p.a. for standard
    employees.

    Parameters
    ----------
    _altervorsorge_aufwend
    ges_krankenv_beitr_m
    arbeitsl_v_beitr_m
    pflegev_beitr_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = copy.deepcopy(_altervorsorge_aufwend) * 0
    sum_vorsorge = (
        12 * (ges_krankenv_beitr_m + arbeitsl_v_beitr_m + pflegev_beitr_m)
    ).clip(upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"])
    out.loc[~kind] = (
        sum_vorsorge.loc[~kind] + _altervorsorge_aufwend.loc[~kind]
    ).astype(int)
    return out.rename("_vorsorge_alternative_2005_bis_2010")


def _vorsorge_2005_vs_pre_2005(_vorsorge_alternative_2005_bis_2009, _vorsorge_bis_2004):
    """
    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts
    (2004 and 2005 regime) and take the higher one.

    Parameters
    ----------
    _vorsorge_alternative_2005_bis_2009
    _vorsorge_bis_2004

    Returns
    -------

    """
    old_reform = _vorsorge_bis_2004 > _vorsorge_alternative_2005_bis_2009
    out = copy.deepcopy(_vorsorge_alternative_2005_bis_2009)
    out.loc[old_reform] = _vorsorge_bis_2004.loc[old_reform]
    return out.rename("vorsorge")


def _vorsorge_2010_vs_pre_2005(_vorsorge_bis_2004, _vorsorge_ab_2010):
    """
    After a supreme court ruling, the 2005 rule had to be changed in 2010.
    Therefore, one needs to compute amounts
    (2004 and 2010 regime) and take the higher one. (§10 (3a) EStG).
    Sidenote: The 2010 ruling is by construction
    *always* more or equally beneficial than the 2005 one,
    so no need for a separate check there.


    Parameters
    ----------
    _vorsorge_bis_2004
    _vorsorge_ab_2010

    Returns
    -------

    """
    # import pdb
    # pdb.set_trace()
    old_reform = _vorsorge_bis_2004 > _vorsorge_ab_2010
    out = copy.deepcopy(_vorsorge_ab_2010)
    out.loc[old_reform] = _vorsorge_bis_2004.loc[old_reform]
    return out.rename("vorsorge")


def _vorsorge_ab_2010(
    _altervorsorge_aufwend,
    pflegev_beitr_m,
    ges_krankenv_beitr_m,
    arbeitsl_v_beitr_m,
    kind,
    eink_st_abzuege_params,
):
    """
    Vorsorgeaufwendungen 2010 regime
    § 10 (3) EStG
    The share of deductable pension contributions increases each year by 2 pp.
    ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
    4% from health contributions are not deductable.
    only deduct pension contributions up to the ceiling. multiply by 2
    because it's both employee and employer contributions.

    Contributions to other security branches can also be deducted.

    This ruling differs to vorsorge2005() only in the treatment of other contributions.

    By 2020 this rule is by construction the more benefical and the checking against
    the the pre 2005 rule is not necessary any more. Thus this function is directly
    assigned to generate the vorsorge data.

    Parameters
    ----------
    _altervorsorge_aufwend
    pflegev_beitr_m
    ges_krankenv_beitr_m
    arbeitsl_v_beitr_m
    eink_st_abzuege_params

    Returns
    -------

    """
    out = copy.deepcopy(_altervorsorge_aufwend) * 0
    # 'Basisvorsorge': Health and old-age care contributions are deducted anyway.
    sonstige_vors = 12 * (
        pflegev_beitr_m.loc[~kind]
        + (1 - eink_st_abzuege_params["vorsorge_kranken_minderung"])
        * ges_krankenv_beitr_m.loc[~kind]
    )
    # maybe add unemployment insurance, but do not exceed 1900€.
    out.loc[~kind] = sonstige_vors.clip(
        lower=(sonstige_vors + 12 * arbeitsl_v_beitr_m.loc[~kind]).clip(
            upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"]
        )
    )
    out.loc[~kind] += _altervorsorge_aufwend.loc[~kind]
    return out.rename("vorsorge")


def _vorsorge_bis_2004(
    _lohn_vorsorge_bis_2019_single,
    _lohn_vorsorgeabzug_bis_2019_tu,
    ges_krankenv_beitr_m,
    rentenv_beitr_m,
    ges_krankenv_beitr_m_tu,
    rentenv_beitr_m_tu,
    tu_id,
    gemeinsam_veranlagte_tu,
    gem_veranlagt,
    kind,
    eink_st_abzuege_params,
):

    out = copy.deepcopy(ges_krankenv_beitr_m) * 0
    out.loc[~gem_veranlagt & ~kind] = _berechne_vorsorge_bis_2004(
        _lohn_vorsorge_bis_2019_single.loc[~kind],
        ges_krankenv_beitr_m.loc[~gem_veranlagt & ~kind],
        rentenv_beitr_m.loc[~gem_veranlagt & ~kind],
        1,
        eink_st_abzuege_params,
    )

    vorsorge_tu = _berechne_vorsorge_bis_2004(
        _lohn_vorsorgeabzug_bis_2019_tu,
        ges_krankenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        rentenv_beitr_m_tu.loc[gemeinsam_veranlagte_tu],
        2,
        eink_st_abzuege_params,
    )
    out.loc[gem_veranlagt & ~kind] = tu_id[gem_veranlagt].replace(vorsorge_tu)
    return out.rename("vorsorge")


def _lohn_vorsorge_bis_2019_single(
    bruttolohn_m, gemeinsam_veranlagt, eink_st_abzuege_params
):
    out = (
        eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m.loc[~gemeinsam_veranlagt]
    ).clip(lower=0)
    return out.rename("_lohn_vorsorge_bis_2019_single")


def _lohn_vorsorgeabzug_bis_2019_tu(
    bruttolohn_m_tu, gemeinsam_veranlagte_tu, eink_st_abzuege_params
):
    out = 0.5 * (
        2 * eink_st_abzuege_params["vorsorge2004_vorwegabzug"]
        - eink_st_abzuege_params["vorsorge2004_kürzung_vorwegabzug"]
        * 12
        * bruttolohn_m_tu.loc[gemeinsam_veranlagte_tu]
    ).clip(lower=0)
    return out.rename("_lohn_vorsorgeabzug_bis_2019_tu")


@numpy_vectorize(
    excluded=["anzahl_erwachsene", "eink_st_abzuege_params"], otypes=[float]
)
def _berechne_vorsorge_bis_2004(
    lohn_vorsorge,
    krankenv_beitr,
    rentenv_beitr,
    anzahl_erwachsene,
    eink_st_abzuege_params,
):
    item_1 = (1 / anzahl_erwachsene) * max(
        12 * (rentenv_beitr + krankenv_beitr) - lohn_vorsorge, 0
    )
    item_2 = (1 / anzahl_erwachsene) * min(
        item_1, eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"]
    )

    item_3 = 0.5 * np.minimum(
        (item_1 - item_2),
        anzahl_erwachsene * eink_st_abzuege_params["vorsorge_2004_grundhöchstbetrag"],
    )
    out = (lohn_vorsorge + item_2 + item_3).astype(int)
    return out
