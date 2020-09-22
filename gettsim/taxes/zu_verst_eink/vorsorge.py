def _vorsorge_alternative_ab_2005_bis_2009(
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
    out = _altervorsorge_aufwend * 0
    sum_vorsorge = (
        12 * (ges_krankenv_beitr_m + arbeitsl_v_beitr_m + pflegev_beitr_m)
    ).clip(upper=eink_st_abzuege_params["vorsorge_sonstige_aufw_max"])
    out.loc[~kind] = sum_vorsorge.loc[~kind] + _altervorsorge_aufwend.loc[~kind]
    return out


def vorsorge_ab_2005_bis_2009(
    _vorsorge_alternative_ab_2005_bis_2009, vorsorge_bis_2004
):
    """
    With the 2005 reform, no taxpayer was supposed to be affected negatively.
    Therefore, one needs to compute amounts under the 2004 and 2005 regimes
    and take the more favourable one.

    Parameters
    ----------
    _vorsorge_alternative_ab_2005_bis_2009
    vorsorge_bis_2004

    Returns
    -------

    """
    return vorsorge_bis_2004.clip(lower=_vorsorge_alternative_ab_2005_bis_2009)


def vorsorge_ab_2010_bis_2019(vorsorge_bis_2004, vorsorge_ab_2020):
    """
    After a supreme court ruling, the 2005 rule had to be changed in 2010.
    Therefore, one needs to compute amounts under the 2004 and 2010 regimes
    and take the more favourable one. (§10 (3a) EStG).

    Sidenote: The 2010 rules are by construction at least as beneficial as
    the 2005 regime, so there is no need for a separate check.


    Parameters
    ----------
    vorsorge_bis_2004
    vorsorge_ab_2020

    Returns
    -------

    """
    return vorsorge_bis_2004.clip(lower=vorsorge_ab_2020)


def vorsorge_ab_2020(
    _altervorsorge_aufwend,
    pflegev_beitr_m,
    ges_krankenv_beitr_m,
    arbeitsl_v_beitr_m,
    kind,
    eink_st_abzuege_params,
):
    """
    Vorsorgeaufwendungen after the regime implemented in 2010 is in full effect,
    see § 10 (3) EStG.

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
    out = _altervorsorge_aufwend * 0
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
    return out


def vorsorge_bis_2004(
    _lohn_vorsorge_bis_2019_single,
    _lohn_vorsorgeabzug_bis_2019_tu,
    ges_krankenv_beitr_m,
    rentenv_beitr_m,
    ges_krankenv_beitr_m_tu,
    rentenv_beitr_m_tu,
    tu_id,
    gemeinsam_veranlagte_tu,
    gemeinsam_veranlagt,
    kind,
    eink_st_abzuege_params,
):
    """

    Parameters
    ----------
    _lohn_vorsorge_bis_2019_single
    _lohn_vorsorgeabzug_bis_2019_tu
    ges_krankenv_beitr_m
    rentenv_beitr_m
    ges_krankenv_beitr_m_tu
    rentenv_beitr_m_tu
    tu_id
    gemeinsam_veranlagte_tu
    gemeinsam_veranlagt
    kind
    eink_st_abzuege_params

    Returns
    -------

    """

    out = ges_krankenv_beitr_m * 0
    out.loc[~gemeinsam_veranlagt & ~kind] = _berechne_vorsorge_bis_2004(
        _lohn_vorsorge_bis_2019_single.loc[~kind],
        ges_krankenv_beitr_m.loc[~gemeinsam_veranlagt & ~kind],
        rentenv_beitr_m.loc[~gemeinsam_veranlagt & ~kind],
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
    out.loc[gemeinsam_veranlagt & ~kind] = tu_id[gemeinsam_veranlagt].replace(
        vorsorge_tu
    )
    return out


def _lohn_vorsorge_bis_2019_single(
    bruttolohn_m, gemeinsam_veranlagt, eink_st_abzuege_params
):
    """

    Parameters
    ----------
    bruttolohn_m
    gemeinsam_veranlagt
    eink_st_abzuege_params

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


def _lohn_vorsorgeabzug_bis_2019_tu(
    bruttolohn_m_tu, gemeinsam_veranlagte_tu, eink_st_abzuege_params
):
    """

    Parameters
    ----------
    bruttolohn_m_tu
    gemeinsam_veranlagte_tu
    eink_st_abzuege_params

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
    lohn_vorsorge,
    krankenv_beitr,
    rentenv_beitr,
    anzahl_erwachsene,
    eink_st_abzuege_params,
):
    """

    Parameters
    ----------
    lohn_vorsorge
    krankenv_beitr
    rentenv_beitr
    anzahl_erwachsene
    eink_st_abzuege_params

    Returns
    -------

    """
    item_1 = (1 / anzahl_erwachsene) * (
        12 * (rentenv_beitr + krankenv_beitr) - lohn_vorsorge
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
