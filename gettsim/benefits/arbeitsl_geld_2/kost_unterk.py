def kost_unterk_m_hh(berechtigte_wohnfläche_hh, miete_pro_qm_hh):
    """Justified costs of living.

    Parameters
    ----------
    berechtigte_wohnfläche_hh
    miete_pro_qm_hh

    Returns
    -------

    """
    return berechtigte_wohnfläche_hh * miete_pro_qm_hh


def miete_pro_qm_hh(kaltmiete_m_hh, heizkosten_m_hh, wohnfläche_hh):
    """

    Parameters
    ----------
    kaltmiete_m_hh
    heizkosten_m_hh
    wohnfläche_hh

    Returns
    -------

    """
    return ((kaltmiete_m_hh + heizkosten_m_hh) / wohnfläche_hh).clip(upper=10)


def berechtigte_wohnfläche_hh(wohnfläche_hh, bewohnt_eigentum_hh, haushaltsgröße_hh):
    """

    Parameters
    ----------
    wohnfläche_hh
    bewohnt_eigentum_hh
    haushaltsgröße_hh

    Returns
    -------

    """
    out = wohnfläche_hh * 0
    out.loc[bewohnt_eigentum_hh] = wohnfläche_hh.loc[bewohnt_eigentum_hh].clip(
        upper=(80 + (haushaltsgröße_hh.loc[bewohnt_eigentum_hh] - 2).clip(lower=0) * 20)
    )
    out.loc[~bewohnt_eigentum_hh] = wohnfläche_hh.loc[~bewohnt_eigentum_hh].clip(
        upper=(
            45 + (haushaltsgröße_hh.loc[~bewohnt_eigentum_hh] - 1).clip(lower=0) * 15
        )
    )
    return out
