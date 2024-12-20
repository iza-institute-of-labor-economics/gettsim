"""Tax allowances."""


def freibeträge_y_sn(
    eink_st_sonderausgaben_y_sn: float,
    vorsorgeaufw_y_sn: float,
    freibeträge_ind_y_sn: float,
) -> float:
    """Calculate total allowances on Steuernummer level.

    Parameters
    ----------

    eink_st_sonderausgaben_y_sn
        See :func:`eink_st_sonderausgaben_y_sn`.
    vorsorgeaufw_y_sn
        See :func:`vorsorgeaufw_y_sn`.
    freibeträge_ind_y_sn
        See :func:`freibeträge_ind_y_sn`.

    Returns
    -------

    """
    out = eink_st_sonderausgaben_y_sn + vorsorgeaufw_y_sn + freibeträge_ind_y_sn

    return out


def freibeträge_ind_y(
    _eink_st_behinderungsgrad_pauschbetrag_y: float,
    eink_st_altersfreib_y: float,
    alleinerz_freib_y_sn: float,
) -> float:
    """Sum up all tax-deductible allowances applicable at the individual level.

    #ToDo: Check whether these columns are really calculated at the individual level.
    Parameters
    ----------

    _eink_st_behinderungsgrad_pauschbetrag_y
        See :func:`_eink_st_behinderungsgrad_pauschbetrag_y`.
    eink_st_altersfreib_y
        See :func:`eink_st_altersfreib_y`.
    alleinerz_freib_y_sn
        See :func:`alleinerz_freib_y_sn`.

    Returns
    -------

    """
    out = (
        _eink_st_behinderungsgrad_pauschbetrag_y
        + eink_st_altersfreib_y
        + alleinerz_freib_y_sn
    )
    return out
