def _kindergeld_m_basis(
    tu_id, _kindergeld_anspruch, kindergeld_params,
):
    """Calculate the preliminary kindergeld.

    Parameters
    ----------
    tu_id
    _kindergeld_anspruch
    kindergeld_params

    Returns
    -------

    """
    # Kindergeld_Anspruch is the cumulative sum of eligible children.
    kulmulative_anspruch = _kindergeld_anspruch.groupby(tu_id).transform("cumsum")
    out = kulmulative_anspruch.clip(upper=4).replace(kindergeld_params["kindergeld"])
    return out


def _kindergeld_m_tu_basis(_kindergeld_m_basis, tu_id):
    """Aggregate the preliminary kindergeld on tax unit level.

    Parameters
    ----------
    _kindergeld_m_basis
    tu_id

    Returns
    -------

    """
    return _kindergeld_m_basis.groupby(tu_id).sum()


def _kindergeld_anspruch_nach_stunden(
    alter, in_ausbildung, arbeitsstunden_w, kindergeld_params
):
    """
    Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
    in_ausbildung
    arbeitsstunden_w
    kindergeld_params

    Returns
    -------

    """
    out = alter <= 18
    out.loc[
        (alter.between(19, kindergeld_params["kindergeld_hoechstalter"]))
        & in_ausbildung
        & (arbeitsstunden_w <= kindergeld_params["kindergeld_stundengrenze"])
    ] = True

    return out


def _kindergeld_anspruch_nach_lohn(
    alter, in_ausbildung, bruttolohn_m, kindergeld_params
):
    """
    Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
    kindergeld_params
    in_ausbildung
    bruttolohn_m

    Returns
    -------

    """
    out = alter <= 18
    out.loc[
        (alter.between(19, kindergeld_params["kindergeld_hoechstalter"]))
        & in_ausbildung
        & (bruttolohn_m <= kindergeld_params["kindergeld_einkommensgrenze"] / 12)
    ] = True

    return out
