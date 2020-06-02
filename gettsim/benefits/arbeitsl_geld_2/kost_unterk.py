def kost_unterk_m(_berechtigte_wohnfläche, _miete_pro_sqm):
    """
    Only 'appropriate' housing costs are paid. Two possible options:
    1. Just pay rents no matter what
    return household["miete"] + household["heizkost"]
    2. Add restrictions regarding flat size and rent per square meter (set it 10€,
    slightly above average)

    Parameters
    ----------
    _berechtigte_wohnfläche
    _miete_pro_sqm

    Returns
    -------

    """
    return _berechtigte_wohnfläche * _miete_pro_sqm


def _miete_pro_sqm(kaltmiete_m, heizkost_m, wohnfläche):
    """

    Parameters
    ----------
    kaltmiete_m
    heizkost_m
    wohnfläche

    Returns
    -------

    """
    return ((kaltmiete_m + heizkost_m) / wohnfläche).clip(upper=10)


def _berechtigte_wohnfläche(wohnfläche, bewohnt_eigentum, haushaltsgröße):
    """

    Parameters
    ----------
    wohnfläche
    bewohnt_eigentum
    haushaltsgröße

    Returns
    -------

    """
    out = wohnfläche * 0
    out.loc[bewohnt_eigentum] = wohnfläche.loc[bewohnt_eigentum].clip(
        upper=(80 + (haushaltsgröße.loc[bewohnt_eigentum] - 2).clip(lower=0) * 20)
    )
    out.loc[~bewohnt_eigentum] = wohnfläche.loc[~bewohnt_eigentum].clip(
        upper=(45 + (haushaltsgröße.loc[~bewohnt_eigentum] - 1).clip(lower=0) * 15)
    )
    return out
